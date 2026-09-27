"""Recover omitted seat stays and source-sized mounting interfaces."""
import argparse
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys
from PIL import Image

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
SNL = ROOT / 'references/1928-03-30_SNL_G13/SNL_G13_Project'
SEAT = H / 'driver_seat_study'
sys.path.insert(0, str(SNL))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    dependencies = {}

    def bind(path):
        dependencies[str(path.relative_to(ROOT))] = sha(path)

    bind(Path(__file__))
    all_hits = []
    for path in sorted((SNL / 'data').glob('*.py')):
        if path.name != 'opening_tables.py' and not path.name.startswith('tables_'):
            continue
        bind(path)
        for page, rows in importlib.import_module('data.' + path.stem).TABLES.items():
            for i, row in enumerate(rows, 1):
                text = json.dumps(row, ensure_ascii=False).lower()
                if any(v in text for v in ['driver’s seat', 'seat support', 'sh289', 'sh291']):
                    all_hits.append(dict(source_id=f'SNL:{page:03d}:{i:03d}', **row))
    write(out / 'catalogue_discovery.json', all_hits)
    ids = ['SNL:031:005', 'SNL:033:009', 'SNL:222:007', 'SNL:222:008']
    selected = [next(v for v in all_hits if v['source_id'] == key) for key in ids]
    write(out / 'reviewed_rows.json', selected)
    crops = {31: (810, 328, 1810, 414), 33: (815, 440, 1810, 500),
             222: (910, 475, 1980, 540)}
    image_records = {}
    for page, bounds in crops.items():
        source = SNL / 'sources' / f'p{page:03d}.jpg'
        bind(source)
        image = Image.open(source).rotate(-90, expand=True)
        target = out / f'p{page:03d}_support_rows.png'
        image.crop(bounds).save(target)
        image_records[target.name] = dict(source=str(source.relative_to(ROOT)),
            source_sha256=sha(source), rotation_degrees=-90, crop_after_rotation=list(bounds),
            sha256=sha(target), metric_calibration=False)
    for path in [SEAT / 'study_receipt.json', SEAT / 'trial06/report.json',
                 SEAT / 'trial06/checks03/independent_checks.json',
                 SEAT / 'evidence01/section_datums.json', SEAT / 'evidence_receipt.json',
                 ROOT / 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate06.png']:
        bind(path)
    picks = read(SEAT / 'evidence01/section_datums.json')['construction_picks']
    endpoints = {}
    for side in ['front', 'rear']:
        upper = picks[side + '_underseat_attachment']
        lower = picks[side + '_lower_support_joint']
        endpoints[side] = dict(upper=upper, lower=lower,
            projected_center_distance_mm=math.dist(upper['conditional_world_xz_mm'], lower['conditional_world_xz_mm']),
            basis='Inherited conditional section picks; lower feature identity is unproven. Transverse offset and stock remain unmeasured.')
    old_bore = 16.3
    printed_bolt = 19.05
    write(out / 'interface_constraints.json', dict(
        upper_attachment=dict(source_id='SNL:033:009', quantity=4, diameter_mm=printed_bolt,
            stock_length_mm=60.325, plain_nut=True, lock_washer=True,
            proposed_receiver_diameter_mm=19.3, radial_clearance_mm=.125,
            receiver_fit_status='Construction allowance, not a printed bore dimension.',
            length_datum='Under head assumed; full printed length must remain.'),
        lower_attachment=dict(source_id='SNL:031:005', quantity=4, diameter_mm=12.7,
            stock_length_mm=34.925, plain_nut=True, lock_washer=True,
            allocation='One bolt per stay; two front and two rear stays from p222.',
            receiver_diameter_estimate_mm=13., length_datum='Under head assumed.'),
        support_angles=dict(source_ids=['SNL:005:006', 'SNL:031:008'], quantity=2,
            bolt_quantity=8, bolt_diameter_mm=12.7, bolt_stock_length_mm=41.275,
            plain_nut_quantity=8, lock_washer_quantity=8),
        current_bearing_conflict=dict(native_sha256=read(SEAT / 'trial06/report.json')['native_sha256'],
            definition='Def_DriverSeat_Bearing_SH289E', old_estimated_diameter_mm=old_bore,
            printed_bolt_diameter_mm=printed_bolt, diametral_interference_mm=printed_bolt-old_bore,
            disposition='Rebuild four receiver occurrences through a revised shared definition before installing the full upper bolts. Do not reduce printed bolt stock.'),
        conditional_stay_endpoints=endpoints,
        identity_conflict=dict(bolt_row_literal_marks=['SH289A', 'SH289B'],
            stay_rows_literal_marks=['SH289B', 'SH289D'],
            lower_bolt_row_literal_marks=['SH289B', 'SH289D'],
            original_scans_agree_with_transcription=True,
            provisional_selection='Two front SH289B and two rear SH289D from the explicit stay list, also corroborated by their lower bolts. Transfer the upper-bolt functional seat-to-stay application while retaining its contradictory A/B labels.',
            source_error_or_variant_resolved=False),
        projected_topology='Four upper bearing bolts and four lower stay bolts. Source picks suggest unequal front/rear slopes; no parallelogram motion or adjustment travel is qualified.',
        prior_packet_omission='The initial seat packet selected assembly/bearing rows but omitted the separate alphabetical STAY rows and associated generic BOLT applications. Its estimated receiver diameter did not use the printed upper bolt size.',
        expected_new_support_occurrences=54,
        expected_new_support_occurrence_breakdown=dict(stays=4, stay_bolts_nuts_locks=24, angles=2, angle_bolts_nuts_locks=24),
        protected_interfaces='Preserve full printed stock, real floor mounting and established shaft bores; revised support profiles must be checked against every neighboring physical part.',
        geometry_modified=False, source_camera_refitted=False))
    write(out / 'report.json', dict(
        geometry_modified=False, historical_installation_qualified=False,
        reviewed_source_ids=ids, catalogue_discovery_count=len(all_hits),
        discovery_is_not_full_source_review=True, images=image_records,
        input_hashes=dependencies,
        next_action='Revise the bearing bore for four full19.05x60.325mm seat bolts; build twoSH289B/twoSH289D stays and their four12.7x34.925mm lower bolts. Complete the twoM788 angles and eight12.7x41.275mm mounts; revise M786/M787 support extensions while preserving floor/shaft interfaces. Keep A/B versus B/D identity conflict explicit.'))
    print('Recorded four reviewed rows and', len(all_hits), 'catalogue discovery rows; no geometry changed.')


if __name__ == '__main__':
    main()
