"""Content-addressed snapshots, append-only manifests and a transactional local index."""
from pathlib import Path
import sqlite3
import uuid
from .common import atomic_write, digest, dumps, loads, stable_id, utc_now


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / 'catalog.sqlite3', timeout=30)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS snapshots (
            request_id TEXT NOT NULL, payload_sha TEXT NOT NULL,
            object_path TEXT NOT NULL, first_seen TEXT NOT NULL,
            PRIMARY KEY(request_id,payload_sha))''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS latest (
            request_id TEXT PRIMARY KEY, manifest_path TEXT NOT NULL)''')
        self.db.commit()

    def close(self):
        self.db.close()

    def request_id(self, spec):
        return stable_id({'source': spec['source'], 'url': spec['url']})

    def latest(self, request_id):
        row = self.db.execute('SELECT manifest_path FROM latest WHERE request_id=?', (request_id,)).fetchone()
        if not row:
            raise FileNotFoundError(f'No accepted cached capture for request {request_id}')
        manifest = loads((self.root / row[0]).read_bytes())
        raw = (self.root / manifest['object_path']).read_bytes()
        if digest(raw) != manifest['payload_sha256']:
            raise ValueError('Cached snapshot checksum mismatch')
        return raw, manifest

    def capture(self, spec, raw, headers, final_url, mode='live', replay_of=None):
        request_id, sha = self.request_id(spec), digest(raw)
        object_path = Path('objects') / sha[:2] / (sha + '.json')
        full = self.root / object_path
        if full.exists():
            if digest(full.read_bytes()) != sha:
                raise ValueError('Existing immutable object is corrupted')
        else:
            atomic_write(full, raw)
        stamp = utc_now()
        self.db.execute('INSERT OR IGNORE INTO snapshots VALUES (?,?,?,?)',
                        (request_id, sha, str(object_path), stamp))
        self.db.commit()
        first = self.db.execute('SELECT first_seen FROM snapshots WHERE request_id=? AND payload_sha=?',
                                (request_id, sha)).fetchone()[0]
        manifest = {'source': spec['source'], 'request_id': request_id, 'request': spec,
                    'payload_sha256': sha, 'snapshot_id': stable_id([request_id, sha]),
                    'object_path': str(object_path), 'bytes': len(raw), 'headers': headers,
                    'requested_url': spec['url'], 'final_url': final_url,
                    'checked_at_utc': stamp, 'first_retrieved_at_utc': first, 'mode': mode,
                    'replay_of': replay_of, 'http_status': 200 if mode == 'live' else None,
                    'validation_status': 'pending', 'licensing': spec['licensing']}
        return manifest

    def finish(self, manifest, status, validation, error=None):
        manifest = dict(manifest, validation_status=status, validation=validation, error=error)
        relative = Path('manifests') / manifest['request_id'] / (uuid.uuid4().hex + '.json')
        atomic_write(self.root / relative, (dumps(manifest) + '\n').encode())
        if status in {'accepted', 'accepted_empty'}:
            with self.db:
                self.db.execute('INSERT OR REPLACE INTO latest VALUES (?,?)',
                                (manifest['request_id'], str(relative)))
        return relative, manifest

    def failure(self, spec, error):
        request_id = self.request_id(spec)
        relative = Path('manifests') / request_id / (uuid.uuid4().hex + '.json')
        manifest = {'request': spec, 'request_id': request_id, 'source': spec['source'],
                    'checked_at_utc': utc_now(), 'validation_status': 'transport_failed',
                    'error_type': type(error).__name__, 'error': str(error), 'object_path': None}
        atomic_write(self.root / relative, (dumps(manifest) + '\n').encode())
        return relative, manifest

    def bronze(self, manifest, observations):
        relative = Path('bronze') / manifest['request_id'] / (manifest['payload_sha256'] + '.jsonl')
        records = []
        for locator, record in observations:
            records.append({'record_id': stable_id([manifest['snapshot_id'], locator]),
                            'source': manifest['source'], 'request_id': manifest['request_id'],
                            'snapshot_id': manifest['snapshot_id'], 'source_locator': locator,
                            'payload_sha256': manifest['payload_sha256'],
                            'source_object_path': manifest['object_path'],
                            'ingested_at_utc': manifest['first_retrieved_at_utc'],
                            'source_record': record})
        raw = ''.join(dumps(record) + '\n' for record in records).encode()
        full = self.root / relative
        if full.exists() and full.read_bytes() != raw:
            raise ValueError('Idempotence violation: existing Bronze output differs')
        if not full.exists():
            atomic_write(full, raw)
        return str(relative), len(records)
