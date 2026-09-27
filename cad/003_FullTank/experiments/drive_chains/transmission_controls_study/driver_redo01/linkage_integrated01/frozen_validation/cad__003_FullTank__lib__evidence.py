"""Read-only survey access and reproducible authored-input fingerprints."""
import hashlib
import json
from pathlib import Path
import sqlite3

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]
SURVEY = REPO / "cad/001_Survey"
FOUNDATION = REPO / "cad/002_Foundation"


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def database():
    connection = sqlite3.connect((SURVEY / "mark_viii_parts.sqlite").as_uri() + "?mode=ro&immutable=1", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def rows(connection, query, args=()):
    return [dict(row) for row in connection.execute(query, args)]


def verify_sources(extra=()):
    """Verify the inherited reviewed lock; never refresh hashes on a mismatch."""
    lock = read(FOUNDATION / "data/sources.json")["required"]
    for entry in extra:
        existing = lock.get(entry["path"])
        if existing and existing != entry["sha256"]:
            raise ValueError("Conflicting source locks: " + entry["path"])
        lock[entry["path"]] = entry["sha256"]
    for relative, expected in lock.items():
        path = REPO / relative
        if not path.is_file() or sha(path) != expected:
            raise ValueError("Missing or changed source; review required: " + relative)
    return {"verified_files": len(lock), "survey_sha256": sha(SURVEY / "mark_viii_parts.sqlite")}


def fingerprint():
    paths = list((STAGE / "data").rglob("*.json")) + list((STAGE / "lib").glob("*.py")) + list((STAGE / "lib").glob("*.c")) + [STAGE / "manage.py"]
    return {str(p.relative_to(STAGE)): sha(p) for p in sorted(paths)}


def check_refs(refs, connection, issue_ids, calibration_ids):
    if not refs:
        raise ValueError("Missing evidence references")
    for ref in refs:
        kind, _, value = ref.partition(":")
        if kind == "record":
            valid = connection.execute("SELECT 1 FROM source_records WHERE record_id=?", (value,)).fetchone()
        elif kind == "page":
            source, page = value.split(":", 1)
            valid = connection.execute("SELECT 1 FROM source_pages WHERE source_id=? AND printed_page=?", (source, page)).fetchone()
        elif kind == "issue":
            valid = value in issue_ids
        elif kind == "calibration":
            valid = value in calibration_ids
        else:
            valid = False
        if not valid:
            raise ValueError("Unknown evidence reference: " + ref)
