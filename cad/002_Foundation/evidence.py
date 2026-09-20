"""Read-only evidence access, restricted arithmetic, and authored-record validation."""
import ast
import hashlib
import json
import math
import operator
from pathlib import Path
import sqlite3

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SURVEY = REPO / 'cad/001_Survey'
CONFIG = 'ROCK_ISLAND_FIRST_100'
STATUSES = {'direct_dimension', 'documented_arrangement', 'scaled_from_plate',
            'assembly_inference', 'observed_variant', 'illustrative_provisional'}


def read(path):
    return json.loads(Path(path).read_text())


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def database():
    c = sqlite3.connect((SURVEY / 'mark_viii_parts.sqlite').as_uri() + '?mode=ro&immutable=1', uri=True)
    c.row_factory = sqlite3.Row
    return c


def arithmetic(expression, values):
    """Only constants, parameter names and arithmetic; never execute input as Python."""
    if isinstance(expression, (int, float)):
        value = float(expression)
    else:
        ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
               ast.Div: operator.truediv}

        def visit(node):
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.Name):
                if node.id not in values:
                    raise ValueError(f'Unknown parameter: {node.id}')
                return values[node.id]
            if isinstance(node, ast.BinOp) and type(node.op) in ops:
                return ops[type(node.op)](visit(node.left), visit(node.right))
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
                return (-1 if isinstance(node.op, ast.USub) else 1) * visit(node.operand)
            raise ValueError(f'Unsupported arithmetic: {expression!r}')
        value = float(visit(ast.parse(expression, mode='eval').body))
    if not math.isfinite(value):
        raise ValueError(f'Non-finite value: {expression}')
    return value


def load_data(directory):
    data = {name: read(directory / (name + '.json'))
            for name in ['parameters', 'model', 'calibrations', 'issues', 'sources']}
    values = {}
    if data['model']['configuration'] != CONFIG or data['model']['units'] != 'mm':
        raise ValueError('The pilot requires ROCK_ISLAND_FIRST_100 configuration and millimeter units.')
    for key, item in data['parameters'].items():
        if item['unit'] != 'mm':
            raise ValueError(f'CAD parameter must be in millimeters: {key}')
        if item['status'] not in STATUSES or item['configuration'] != CONFIG:
            raise ValueError(f'Unsupported status or configuration: {key}')
        if not item.get('evidence') or not item.get('interpretation'):
            raise ValueError(f'Parameter lacks evidence/interpretation: {key}')
        if item.get('blocked'):
            raise ValueError(f'Unresolved parameter conflict: {key}')
        value = arithmetic(item.get('expression', item.get('value')), values)
        lo, hi = item['bounds_mm']
        if not math.isfinite(lo) or not math.isfinite(hi):
            raise ValueError(f'Non-finite reconstruction bounds: {key}')
        if not lo <= value <= hi:
            raise ValueError(f'Parameter {key}={value} outside documented bounds [{lo}, {hi}]')
        values[key] = value
    data['values'] = values
    with database() as c:
        for key, item in data['parameters'].items():
            for ref in item['evidence']:
                if ref.startswith('record:'):
                    if not c.execute('select 1 from source_records where record_id=?', (ref[7:],)).fetchone():
                        raise ValueError(f'{key}: missing source record {ref}')
                elif ref.startswith('page:'):
                    sid, page = ref[5:].split(':', 1)
                    if not c.execute('select 1 from source_pages where source_id=? and printed_page=?', (sid, page)).fetchone():
                        raise ValueError(f'{key}: missing source page {ref}')
                elif ref.startswith('calibration:'):
                    if ref[12:] not in data['calibrations']:
                        raise ValueError(f'{key}: missing calibration {ref}')
                elif ref.startswith('issue:'):
                    if ref[6:] not in data['issues']:
                        raise ValueError(f'{key}: missing issue {ref}')
                else:
                    raise ValueError(f'{key}: unsupported evidence reference {ref}')
        for key, part in data['model']['parts'].items():
            pid = part.get('survey_id')
            if pid and not c.execute('select 1 from parts where part_id=?', (pid,)).fetchone():
                raise ValueError(f'{key}: unknown survey part {pid}')
            for p in part['parameters']:
                if p not in values:
                    raise ValueError(f'{key}: missing parameter {p}')
    ids = {'Root'}
    for occ in data['model']['occurrences']:
        if occ['id'] in ids or occ['parent'] not in ids:
            raise ValueError(f'Duplicate occurrence or missing/cyclic parent: {occ["id"]}')
        ids.add(occ['id'])
        if occ.get('part') and occ['part'] not in data['model']['parts']:
            raise ValueError(f'Missing part definition: {occ["part"]}')
        if not occ.get('evidence') or occ['configuration'] != CONFIG:
            raise ValueError(f'Missing occurrence provenance: {occ["id"]}')
        for v in occ['translation'] + occ['rotation']:
            arithmetic(v, values)
    return data


def source_check(data):
    failures = []
    for rel, expected in data['sources']['required'].items():
        path = REPO / rel
        if not path.is_file():
            failures.append('Missing source: ' + rel)
        elif sha(path) != expected:
            failures.append('Source hash changed (review before updating lock): ' + rel)
    if failures:
        raise ValueError('\n'.join(failures))
    return {'required_files_verified': len(data['sources']['required']),
            'supplements_present': {p: (REPO / p).is_file() for p in data['sources']['supplementary']}}


def fingerprint(directory):
    return {p.name: sha(p) for p in sorted(Path(directory).glob('*.json'))}
