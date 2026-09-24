"""Add short connecting-rod and spring-support evidence without changing earlier packets."""
import argparse
from pathlib import Path
import sqlite3
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
db = ROOT / 'cad/001_Survey/mark_viii_parts.sqlite'
connection = sqlite3.connect('file:' + str(db) + '?mode=ro', uri=True)
connection.row_factory = sqlite3.Row
marks = ['M4129', 'M4135', 'M4136', 'M563', 'M564', 'M567', 'M572', 'M577',
         'M573', 'M578', 'M575', 'SH946D', 'SH946E', 'M569A', 'M569B', 'M569C',
         'M570', 'M568A', 'M568C']
identifiers = {mark: [dict(v) for v in connection.execute(
    'select * from part_identifiers where identifier=?', (mark,))] for mark in marks}
part_ids = sorted({v['part_id'] for rows in identifiers.values() for v in rows})
records = {}
for pid in part_ids:
    for row in connection.execute(
        'select s.* from source_records s join part_evidence e on e.record_id=s.record_id '
        'where e.part_id=?', (pid,)):
        records[row['record_id']] = dict(row)
for page, lower, upper in [(194, 19, 25), (195, 13, 20), (169, 11, 11), (170, 5, 5)]:
    for row in connection.execute('select * from source_records where source_id=? '
                                  'and printed_page=? and row_no between ? and ?',
                                  ('SNL', str(page), lower, upper)):
        records[row['record_id']] = dict(row)
for row in records.values():
    row['part_ids'] = [v[0] for v in connection.execute(
        'select distinct part_id from part_evidence where record_id=?', (row['record_id'],))]
connection.close()
packet = H / 'transmission_controls_study'
current = packet / 'fulcrum_integrated01'
probe = read(current / 'operating_interfaces.json')
corrections = []
for row in probe['proposed_routes']:
    track = row['source_rod_mark'] == 'M578'
    assert track or row['source_rod_mark'] == 'M573'
    corrections.append(dict(
        fulcrum_eye=row['fulcrum_eye'], rear_brake_eye=row['rear_brake_eye'],
        superseded_rod_mark=row['source_rod_mark'], selected_snl_mark='SH946D' if track else 'SH946E',
        corresponding_handbook_tube='M577' if track else 'M572',
        end_fork_mark='M569C' if track else 'M569A', end_forks_per_rod=2,
        straight_eye_center_distance_mm=row['straight_eye_center_distance_mm'],
        pin_axis_angle_degrees=row['pin_axis_angle_degrees'],
        limitation='Functional correspondence inferred from source descriptions and the plan. '
                   'No dimensionally exact interchangeability or clear rod route established.'))
images = [ROOT / f'references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p{n:03}.jpg'
          for n in [86, 87, 169, 170, 194, 195]]
images += [ROOT / 'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p280-geometry.png',
           ROOT / 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate104.png']
files = set(images) | {ROOT / row['source_path'] for row in records.values()}
files |= {db, current / 'operating_interfaces.json', current / 'qualification.json',
          packet / 'sources.json', packet / 'channel_sources01/sources.json', Path(__file__)}
out.mkdir(parents=True)
write(out / 'sources.json', dict(
    scope='Rear spring supports and short brake connections; additive correction of route identities.',
    source_records=list(records.values()), part_identifier_rows=identifiers,
    source_hashes={str(path.relative_to(ROOT)): sha(path) for path in sorted(files)},
    previous_interface_probe_sha256=sha(current / 'operating_interfaces.json'),
    current_native_sha256=probe['native_sha256'], corrected_route_identities=corrections,
    observations=[
        'SNL194 distinguishes M578 rear foot-brake rod from SH946D rear foot-brake connecting rod; each connecting-rod assembly includes two3/4inch plain nuts.',
        'SNL195 distinguishes M573 rear low-speed rod from SH946E low-speed connecting rod; each connecting-rod assembly includes two3/4inch plain nuts.',
        'SNL86 applies two M569C forks to each SH946D. SNL87 applies two M569A forks, length1inch, to each SH946E. The prior M573/M578 assignment to the short measured endpoint chords was incorrect.',
        'HB188 names M577 foot-brake connecting tube and M572 low-speed connecting tube; SNL6 still labels these short connections with the earlier marks. Select SH946D/SH946E for the current SNL-based build, retaining the correspondence as an inference.',
        'M573/M578 remain the long rear rods linking the center controls to the other horizontal-lever arms. Their two M569C forks must not be double-counted as the short connection hardware.',
        'Two M4135 high-speed spring supports have two half-inch by3/4inch rivets each; two M4136 shared foot/low-speed supports have two half-inch by1-7/8inch rivets each.',
        'HB104 qualitatively shows the shared foot/low-speed spring support spanning adjacent connections. Its full root shape and relationship to M4129 remain obscured.',
    ], open_issues=[
        'M4129 may share attachments with another channel member, but no source yet establishes that topology. Do not invent a separate rivet application.',
        'M4135 section, hole/foot dimensions and station remain approximations tied to current high-brake rod interfaces.',
        'The two M4136 roots and long mounting rivets need a source-consistent grip stack and clearance before integration.',
        'Spring free/installed lengths, profiles, end forms and M567 washer use need explicit assembly reconciliation.',
        'The prior fixed-camera discrepancy and all camera assumptions remain unchanged.',
    ], geometry_modified=False, historical_geometry_qualified=False))
print('Saved', len(records), 'rows and four corrected short-connection identities.')
