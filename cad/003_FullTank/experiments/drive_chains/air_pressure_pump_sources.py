"""Freeze a focused source dossier without changing the survey or CAD models."""
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = Path(__file__).with_suffix('.json')
SURVEY = ROOT / 'cad/001_Survey/mark_viii_parts.sqlite'
SNL = 'references/1928-03-30_SNL_G13/SNL_G13_Project'
HB = 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank'

# Explicitly selected source rows; repeated evidence does not add occurrences.
RANGES = {
    '12': [(22, 22)], '15': [(25, 25)], '18': [(11, 11)],
    '30': [(4, 4)], '36': [(12, 13)], '43': [(10, 10)],
    '74': [(3, 3)], '77': [(1, 4)], '79': [(25, 25)],
    '112': [(11, 17)], '115': [(10, 10)], '124': [(12, 13)],
    '146': [(11, 11)], '155': [(24, 24)], '158': [(1, 1)],
    '159': [(3, 21)], '209': [(20, 23)], '219': [(17, 17)],
    '231': [(20, 26)], '240': [(19, 23)], '251': [(16, 19)],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before = sha(SURVEY)
    with sqlite3.connect(f'file:{SURVEY}?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        records = []
        for page, ranges in RANGES.items():
            for low, high in ranges:
                rows = db.execute(
                    'SELECT * FROM source_records WHERE source_id=? AND '
                    'printed_page=? AND row_no BETWEEN ? AND ? ORDER BY row_no',
                    ('SNL', page, low, high)).fetchall()
                assert len(rows) == high - low + 1, (page, low, high)
                for row in rows:
                    data = dict(row)
                    data['raw'] = json.loads(data.pop('raw_json'))
                    data['part_ids'] = [r[0] for r in db.execute(
                        'SELECT part_id FROM part_evidence WHERE record_id=? '
                        'ORDER BY part_id', (row['record_id'],))]
                    records.append(data)
        part_ids = sorted({pid for r in records for pid in r['part_ids']})
        identities = [dict(db.execute('SELECT * FROM parts WHERE part_id=?',
                                    (pid,)).fetchone()) for pid in part_ids]
        edges = [dict(r) for r in db.execute(
            'SELECT * FROM assembly_edges WHERE parent_part_id IN (?,?) '
            'ORDER BY record_id', ('P_dd55a02fabc8964b', 'P_4cb854d17d3862c4'))]
        assert sum(e['quantity_per_parent'] for e in edges
                   if e['parent_part_id'] == 'P_dd55a02fabc8964b') == 54
        assert sum(e['quantity_per_parent'] for e in edges
                   if e['parent_part_id'] == 'P_4cb854d17d3862c4') == 2
        notes = [dict(r) for r in db.execute(
            'SELECT * FROM notes WHERE note_id IN (?,?,?) ORDER BY note_id',
            ('SNL_NOTE:%', 'SNL_NOTE:X', 'SNL_NOTE:&'))]
        variants = [dict(r) for pid in part_ids for r in db.execute(
            'SELECT * FROM part_variants WHERE part_id=? ORDER BY variant_id', (pid,))]

    assets = [f'{SNL}/sources/p{p:03d}.jpg' for p in [18, 159, 209]]
    assets += [f'{SNL}/assets/p279-geometry.png']
    assets += [f'{HB}/Handbook_Project/assets/plate{p}.png' for p in [15, 22, 115]]
    assets += [f'{HB}/original_scans/MarkVIII016.jpg']
    body_path = ROOT / HB / 'Handbook_Project/data'
    prose = []
    for path in sorted(body_path.glob('body_batch*.json')):
        for page, rows in json.loads(path.read_text()).items():
            if page in ['24', '30', '31', '32']:
                prose.append(dict(printed_page=page, source=str(path.relative_to(ROOT)),
                                  sha256=sha(path), lines=[r['text'] for r in rows]))
    assert sha(SURVEY) == before
    result = dict(
        status='source_preparation_no_geometry', survey_sha256=before,
        assembly_id='P_dd55a02fabc8964b', records=records, identities=identities,
        assembly_edges=edges, catalogue_notes=notes, recorded_variants=variants,
        source_assets={p: sha(ROOT / p) for p in assets}, handbook_prose=prose,
        source_quantity_expansion=dict(
            direct_pump_units=54, shaft_container_replaced_by_two_pieces=1,
            four_bolt_sets_replaced_by_twelve_pieces=8, physical_pieces=63,
            scope='Catalogue pump plus base fasteners; excludes transmission '
                  'brackets, stud sets, belt and lines. Installed port/plug '
                  'allocation must be reconciled when routing lines.'),
        original_pages_visually_inspected=['SNL18', 'SNL159', 'SNL209', 'HB30/31'],
        figures_visually_inspected=['SNL Plate5', 'HB Plate15', 'HB Plate22', 'HB Plate115'],
        remaining_work='Author calibration/assumption controls and build the '
                       'pump and transmission installation; no geometric coverage claimed.')
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(f'Saved {len(records)} source rows and {len(identities)} identities; '
          '63-piece catalogue expansion; frozen survey unchanged.')


if __name__ == '__main__':
    main()
