"""Shared, dependency-free work-packet records and conservative routing."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNS = ROOT / 'benchmarks/cad_work_packets/results'
WORK = ROOT / '.work/cad-packets/runs'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def identifier(value):
    if not re.fullmatch(r'[a-z][a-z0-9_-]{0,79}', value):
        raise ValueError('Use a short lowercase run/packet ID, with no path components')
    return value


def contained(base, relative):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('Expected a relative descendant path: ' + str(relative))
    result = (base / p).resolve()
    if not result.is_relative_to(base.resolve()):
        raise ValueError('Path escapes its root: ' + str(relative))
    return result


def regular(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError('Expected an ordinary, unlinked file: ' + str(path))
    return path


def route(packet, diagnosis=False):
    if diagnosis:
        return dict(effort='xhigh', reason='Independent diagnosis of a failed candidate')
    reviews = packet.get('reviewed', {})
    eligible = (packet.get('category') in {'reviewed_implementation', 'qualified_family'}
                and all(reviews.get(k) is True for k in ('dimensions', 'sources', 'interfaces'))
                and not packet.get('risks'))
    return dict(effort='medium' if eligible else 'xhigh',
                reason='Reviewed, bounded implementation; experimental medium route' if eligible
                else 'Uncertainty, interface changes, missing reviews, or an unrecognized category')


def load_packet(path):
    path = Path(path).resolve()
    p = read(path)
    identifier(p['id'])
    if p.get('version') != 1 or p.get('mode') != 'shadow':
        raise ValueError('Only version 1 shadow packets are supported')
    if not isinstance(p.get('instructions'), str) or not p['instructions'].strip():
        raise ValueError('Instructions are required')
    seen = set()
    for row in p['inputs']:
        src = regular(contained(ROOT, row['source']))
        dst = contained(Path('/inputs'), row['destination'])
        if dst in seen or sha(src) != row['sha256']:
            raise ValueError('Duplicate or stale packet input: ' + row['source'])
        seen.add(dst)
    for name in p['outputs']:
        if not str(name).startswith('deliverables/'):
            raise ValueError('Outputs must be under deliverables/')
        contained(Path('/candidate'), name)
    validator = regular(contained(ROOT, p['validator']))
    if not validator.is_relative_to(HERE / 'validators'):
        raise ValueError('Validator must be a reviewed controller validator')
    qualification = regular(contained(ROOT, p['validator_qualification']))
    q = read(qualification)
    if q.get('passed') is not True or q.get('validator_sha256') != sha(validator):
        raise ValueError('Validator qualification is missing or stale')
    return p


def production_hashes():
    # Preserve all production native CAD, including currently uncommitted files.
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / 'cad').rglob('*.FCStd'))}


def code_hashes():
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(HERE.rglob('*.py'))}
