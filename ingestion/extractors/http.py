"""Bounded HTTPS transport with retries, Retry-After and request pacing."""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import logging
import random
import time
import urllib.error
import urllib.request

LOG = logging.getLogger(__name__)
RETRYABLE = {408, 429, 500, 502, 503, 504}


def retry_after_seconds(value, now=None):
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            return max(0.0, (parsedate_to_datetime(value) - (now or datetime.now(timezone.utc))).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None


class HttpClient:
    def __init__(self, timeout=45, attempts=4, min_interval=1, max_bytes=15_000_000,
                 opener=None, sleep=time.sleep, monotonic=time.monotonic, max_retry_wait=60):
        if timeout <= 0 or attempts < 1 or min_interval < 0 or max_bytes < 1:
            raise ValueError('Invalid HTTP budget')
        self.timeout, self.attempts, self.min_interval, self.max_bytes = timeout, attempts, min_interval, max_bytes
        self.opener = opener or urllib.request.urlopen
        self.sleep, self.monotonic, self.max_retry_wait = sleep, monotonic, max_retry_wait
        self.last_call = None

    def get(self, url):
        if not url.startswith('https://'):
            raise ValueError('Only public HTTPS endpoints are allowed')
        for attempt in range(1, self.attempts + 1):
            if self.last_call is not None:
                self.sleep(max(0, self.min_interval - (self.monotonic() - self.last_call)))
            self.last_call = self.monotonic()
            request = urllib.request.Request(url, headers={
                'User-Agent': 'GlobalCriticalMaterialsIntelligence/0.2 (public research; bounded source requests)',
                'Accept': 'application/json', 'Accept-Encoding': 'identity'})
            try:
                with self.opener(request, timeout=self.timeout) as response:
                    raw = response.read(self.max_bytes + 1)
                    if len(raw) > self.max_bytes:
                        raise ValueError('Response exceeds byte budget; split the request')
                    if response.status != 200:
                        raise ValueError(f'Expected synchronous HTTP 200, received {response.status}; request requires review')
                    if not response.url.startswith('https://'):
                        raise ValueError('Redirect downgraded HTTPS')
                    headers = {key.lower(): value for key, value in response.headers.items()
                               if key.lower() in {'content-type', 'content-length', 'etag', 'last-modified', 'date'}}
                    if 'json' not in headers.get('content-type', '').lower():
                        raise ValueError('Expected JSON, received a different content type')
                    return raw, headers, response.url
            except urllib.error.HTTPError as exc:
                if exc.code not in RETRYABLE or attempt == self.attempts:
                    raise
                wait = retry_after_seconds(exc.headers.get('Retry-After'))
                wait = wait if wait is not None else 2 ** (attempt - 1) + random.random()
                if wait > self.max_retry_wait:
                    raise RuntimeError(f'Retry-After {wait:.0f}s exceeds run wait budget; retry later') from exc
                LOG.warning('Retryable HTTP %s; attempt %s/%s', exc.code, attempt, self.attempts)
                self.sleep(wait)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                if attempt == self.attempts:
                    raise
                LOG.warning('Transport retry %s/%s: %s', attempt, self.attempts, type(exc).__name__)
                self.sleep(min(self.max_retry_wait, 2 ** (attempt - 1) + random.random()))
        raise RuntimeError('HTTP attempts exhausted')


class CurlHttpClient(HttpClient):
    """Optional system trust-store transport; same retry/size/HTTPS contract.

    Useful on macOS where the Python CA bundle can differ from the system store.
    TLS verification is never disabled. No shell or user-provided command is run.
    """
    def __init__(self, **kwargs):
        if 'opener' in kwargs:
            raise ValueError('system-curl manages its own opener')
        super().__init__(opener=self._open, **kwargs)

    def _open(self, request, timeout):
        import io
        import pathlib
        import shutil
        import subprocess
        import tempfile
        from email.parser import Parser
        executable=shutil.which('curl')
        if not executable:
            raise RuntimeError('Install curl or use the urllib transport')
        with tempfile.TemporaryDirectory(prefix='gcm-http-') as temp:
            body=pathlib.Path(temp)/'body';headers=pathlib.Path(temp)/'headers'
            args=[executable,'--silent','--show-error','--location','--proto','=https',
                  '--proto-redir','=https','--max-time',str(timeout),'--connect-timeout','15',
                  '--max-filesize',str(self.max_bytes),'--user-agent',request.get_header('User-agent'),
                  '--header','Accept: application/json','--header','Accept-Encoding: identity',
                  '--dump-header',str(headers),'--output',str(body),
                  '--write-out','%{http_code}\n%{url_effective}',request.full_url]
            completed=subprocess.run(args,capture_output=True,text=True,timeout=timeout+5)
            if completed.returncode:
                raise urllib.error.URLError('curl transport failed: '+completed.stderr.strip()[:300])
            status,final_url=completed.stdout.strip().split('\n',1)
            # Redirect chains produce multiple HTTP header blocks; use the last one.
            blocks=headers.read_text().replace('\r\n','\n').strip().split('\n\n')
            parsed=Parser().parsestr(blocks[-1].split('\n',1)[1])
            with body.open('rb') as f:raw=f.read(self.max_bytes+1)
            if int(status)>=400:
                raise urllib.error.HTTPError(final_url,int(status),'HTTP source error',parsed,None)
        class Response(io.BytesIO):
            pass
        result=Response(raw);result.status=int(status);result.url=final_url;result.headers=parsed
        return result
