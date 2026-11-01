"""Shared strict serialization and stable identities; no source value imputation."""
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def reject_constant(value):
    raise ValueError(f'Non-standard JSON constant: {value}')


def loads(raw):
    return json.loads(raw, parse_constant=reject_constant)


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(',', ':'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def stable_id(value):
    return digest(dumps(value).encode('utf-8'))


def number(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def atomic_write(path, raw):
    """Publish a complete local file; a killed writer cannot expose a partial snapshot."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix='.pending-', dir=str(path.parent))
    try:
        with os.fdopen(handle, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class ContractError(ValueError):
    """Source response does not satisfy its inspected request contract."""
