"""Bind the reviewed collar joint for continued main-clutch construction."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
STAGE = HERE.parents[1]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, default=HERE / 'clutch_collar_build')
    out = parser.parse_args().candidate.resolve()
    report = read(out / 'report.json')
    native = out / 'TransmissionWithClutchCollar.FCStd'
    native_hash = sha(native)
    assert native_hash == report['native_sha256']
    assert report['native_occurrences'] == 1540
    assert report['new_physical_occurrences'] == len(report['new_ids']) == 10
    assert len(report['changed_ids']) == 10
    assert len(set(report['affected_ids'])) == 20
    assert set(report['affected_ids']) == set(report['new_ids'] + report['changed_ids'])
    assert report['unchanged_parent_occurrences'] == 1520
    assert report['material_passed'] and report['standard_context_checked']
    assert not report['overlaps'] and not report['standard_assembly_modified']

    parent = HERE / 'front_clutch_build'
    parent_receipt = read(parent / 'qualification.json')
    assert parent_receipt['passed'] and parent_receipt['accepted_for_main_clutch_development']
    assert sha(parent / 'TransmissionWithFrontClutch.FCStd') == report['parent_native_sha256']
    assert parent_receipt['native_sha256'] == report['parent_native_sha256']
    for rel, digest in report['input_hashes'].items():
        assert sha(REPO / rel) == digest, rel
        assert sha(out / 'inputs' / Path(rel).name) == digest, rel
    dossier = read(HERE / 'clutch_collar_sources.json')
    assert sha(REPO / 'cad/001_Survey/mark_viii_parts.sqlite') == dossier['survey_sha256']
    for rel, digest in dossier['source_assets'].items():
        assert sha(REPO / rel) == digest, rel
    assert len(report['standard_native_hashes']) == 20
    for rel, digest in report['standard_native_hashes'].items():
        assert sha(STAGE / 'build' / rel) == digest, rel

    artifacts = {
        'ClutchCollarInstallation.step': 'step_sha256',
        'ClutchCollarDefinitions.step': 'definition_step_sha256',
        'locking_wire_spine.brep': 'locking_wire_spine_sha256',
        'external_spring_spine.brep': 'external_spring_spine_sha256',
    }
    for name, key in artifacts.items():
        assert sha(out / name) == report[key], name
    assert report['step_ids'] == report['affected_ids']
    names = [
        'material_checks.json', 'independent_checks.json', 'exchange_checks.json',
        'assembly_exchange_checks.json', 'variants/report.json', 'visual_review.json',
    ]
    receipts = {name: read(out / name) for name in names}
    for name, receipt in receipts.items():
        assert receipt['passed'] and receipt['native_sha256'] == native_hash, name
        if 'checks' in receipt:
            assert all(row['passed'] for row in receipt['checks']), name
    material = receipts['material_checks.json']
    assert material['standard_context_checked']
    assert len(material['pairs']) == report['material_pairs'] == 65
    assert all(abs(row['intersection_mm3']) < 1e-5 for row in material['pairs'])
    assert len(receipts['independent_checks.json']['checks']) == 104
    assert len(receipts['exchange_checks.json']['checks']) == 8
    assert len(read(out / 'definition_order.json')) == 8
    assert len(receipts['assembly_exchange_checks.json']['checks']) == 20
    for name in ['independent_checks.json', 'exchange_checks.json', 'assembly_exchange_checks.json']:
        assert receipts[name]['checker_sha256'] == sha(HERE / 'check_clutch_collar.py'), name
    assert receipts['exchange_checks.json']['step_sha256'] == report['definition_step_sha256']
    assert receipts['assembly_exchange_checks.json']['step_sha256'] == report['step_sha256']

    variants = receipts['variants/report.json']
    assert variants['checker_sha256'] == sha(HERE / 'check_clutch_collar_variants.py')
    assert variants['parts_sha256'] == sha(HERE / 'clutch_collar_parts.py')
    assert variants['standard_native_hashes'] == report['standard_native_hashes']
    assert len(variants['scenarios']) == 2
    for name, summary in zip(['shorter', 'longer'], variants['scenarios']):
        path = f'variants/{name}.json'
        detail = read(out / path)
        assert summary == {k: v for k, v in detail.items() if k != 'pairs'}, path
        assert detail['passed'] and not detail['overlaps']
        assert len(detail['pairs']) == detail['material_pairs'] == 65
        assert all(abs(row['intersection_mm3']) < 1e-5 for row in detail['pairs'])
        assert len(detail['contacts']) == 16 and all(row['passed'] for row in detail['contacts'])
        assert abs(detail['wire_length'] - 660.4) < 1e-6
        names.append(path)

    source = read(out / 'source_review/render_receipt.json')
    assert source['native_sha256'] == native_hash
    assert source['renderer_sha256'] == sha(HERE / 'render_clutch_collar_review.py')
    for rel, digest in source['input_hashes'].items():
        assert sha(REPO / rel) == digest, rel
    for name, digest in source['output_hashes'].items():
        assert sha(out / 'source_review' / name) == digest, name
    visual = receipts['visual_review.json']
    expected_images = {'previews/' + name for name in report['render_hashes']}
    expected_images.add('source_review/comparison.png')
    assert len(expected_images) == 7 and set(visual['image_hashes']) == expected_images
    assert visual['source_render_receipt_sha256'] == sha(out / 'source_review/render_receipt.json')
    for name, digest in visual['image_hashes'].items():
        assert sha(out / name) == digest, name
    for name, digest in report['render_hashes'].items():
        assert sha(out / 'previews' / name) == digest, name

    with zipfile.ZipFile(native) as archive:
        xml = ET.fromstring(archive.read('Document.xml'))
    external = [dict(link.attrib) for link in xml.iter('XLink') if link.get('file', '')]
    assert not external, external
    tree = subprocess.check_output(['git', 'ls-tree', '-r', '-z', 'HEAD', '--', 'cad'], cwd=REPO)
    preserved = []
    for entry in tree.split(b'\0'):
        if not entry:
            continue
        meta, raw_path = entry.split(b'\t', 1)
        path = raw_path.decode()
        oid = meta.decode().split()[2]
        if path.startswith('cad/intermediate_') and path.endswith('.png'):
            data = (REPO / path).read_bytes()
            actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            assert actual == oid, path
            preserved.append(dict(path=path, sha256=sha(REPO / path), git_blob=oid))
    assert len(preserved) >= 72
    names += ['report.json', 'definition_order.json', 'source_review/render_receipt.json', 'source_review/index.html']
    result = dict(
        passed=True, status='checked_approximate_collar_joint_and_end_bearing',
        native_sha256=native_hash, parent_native_sha256=report['parent_native_sha256'],
        parent_qualification_sha256=sha(parent / 'qualification.json'),
        native_occurrences=1540, new_physical_occurrences=10, changed_parent_occurrences=10,
        unchanged_parent_occurrences=1520, accepted_for_main_clutch_development=True,
        complete_clutch=False, complete_installation=False, integrated_in_standard_tank=False,
        historical_fit_qualified=False, load_qualified=False, complete_tank=False,
        native_external_file_references=external, standard_native_hashes=report['standard_native_hashes'],
        source_dossier_sha256=sha(HERE / 'clutch_collar_sources.json'), input_hashes=report['input_hashes'],
        receipt_hashes={name: sha(out / name) for name in names},
        artifact_hashes={name: sha(out / name) for name in artifacts},
        preserved_progression_images=preserved, qualifier_sha256=sha(Path(__file__)),
        remaining=[
            'Main clutch bearing, positive sleeve, four keys, cone-support collar, thrust/ball stack and retention',
            'Cones, facing/rivets, six spring plungers, drum/flywheel/crankshaft interfaces and clutch-stop band',
            'Unproven HB-to-SNL dimensions and variant mapping; inferred axial stations, bearing fits and wire gauge/routing',
            'Pump air circuit, B6205/MX1 supports, lubrication, brakes, long controls and standard integration',
        ],
    )
    (out / 'qualification.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: 1540-leaf collar checkpoint ready for main clutch construction; full tank incomplete.')


if __name__ == '__main__':
    main()
