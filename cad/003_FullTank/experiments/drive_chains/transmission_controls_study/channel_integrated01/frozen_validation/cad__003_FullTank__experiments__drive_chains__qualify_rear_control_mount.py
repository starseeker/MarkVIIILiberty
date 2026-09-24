"""Freeze the evidence for the bounded M4130 mounting increment, retaining open historical questions."""
import copy
from pathlib import Path
import shutil
import subprocess
import sys
H = Path(__file__).resolve().parent
ROOT = H.parents[3]
STAGE = H.parents[1]
sys.path.insert(0, str(STAGE))
from lib.evidence import read, write, sha

packet = H / 'transmission_controls_study'
out = packet / 'channel_integrated01'
assert not (out / 'qualification.json').exists()
r = read(out / 'report.json')
assert sha(out / r['native_file']) == r['native_sha256']
checks = ['independent_checks.json', 'definition_preservation_checks.json', 'reproduction_checks.json']
for file in checks:
    q = read(out / file)
    assert q['passed'] and q['native_sha256'] == r['native_sha256']
assert read(out / 'visual_review.json')['disposition'] == 'reviewed_local_approximation'
trials = [packet / 'channel_mount02', packet / 'channel_mount_variation02']
for trial in trials:
    report = read(trial / 'report.json')
    assert sha(trial / report['native_file']) == report['native_sha256']
    for file in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']:
        q = read(trial / file)
        assert q['passed'] and q['native_sha256'] == report['native_sha256']
    assert len(read(trial / 'independent_checks.json')['checks']) == 75
    assert len(read(trial / 'independent_checks.json')['material_pairs']) == 57
    assert len(read(trial / 'exchange_checks.json')['checks']) == 37
nominal, variant = [read(t / 'report.json')['controls'] for t in trials]
expected = copy.deepcopy(nominal)
expected['cleat']['stock'] += .5
assert variant == expected
assert read(trials[0] / 'reproduction_checks.json')['passed']
subprocess.run([sys.executable, str(H / 'verify_transmission_control_checkpoint.py'),
                '--candidate', str((ROOT / r['source_native']).parent)], check=True)
subprocess.run([sys.executable, str(H / 'verify_rear_control_channel_study.py')], check=True)

scripts = [H / name for name in [
    'rear_control_channel_mount_parts.py', 'trial_rear_control_channel_mount.py',
    'check_rear_control_channel_mount.py', 'check_rear_control_channel_mount_context.py',
    'exchange_rear_control_channel_mount.py', 'render_rear_control_channel_mount.py',
    'check_rear_control_mount_reproduction.py', 'build_rear_control_channel_mount.py',
    'check_rear_control_channel_installation.py', 'check_rear_control_mount_preservation.py',
    'seed_rear_control_mount_preservation.py', 'render_rear_control_channel_installation.py',
    'check_powertrain_frame_reproduction.py', 'pump_integration_worker.py',
    'qualify_rear_control_mount.py', 'verify_rear_control_mount_checkpoint.py']]
scripts += [STAGE / 'lib' / name for name in ['evidence.py', 'cad_build.py', 'camera_review.py',
                                            'mass_properties.py', 'step_matching.py', 'visual_review.py', 'source_camera.py']]
frozen = out / 'frozen_validation'
frozen.mkdir()
for path in scripts:
    shutil.copy2(path, frozen / str(path.relative_to(ROOT)).replace('/', '__'))
dependencies = {}
def add(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    dependencies[str(path.relative_to(ROOT))] = sha(path)
for path in scripts:
    add(path)
for directory in [out, *trials, packet / 'channel_mount01', packet / 'channel_mount_variation01']:
    for path in directory.rglob('*'):
        if not path.is_file() or any(name in path.parts for name in ['adaptive_mass_runtime', 'preservation_runtime', '__pycache__']):
            continue
        add(path)
    report = read(directory / 'report.json')
    for path, digest in report['input_hashes'].items():
        assert sha(ROOT / path) == digest
        add(path)
for path in ['channel_mount_controls01.json', 'channel_mount_controls02.json',
             'channel_mount_controls_variation01.json', 'channel_mount_controls_variation02.json',
             'channel_mount_source_review01.json', 'channel_local_registration01.json',
             'channel_sources01/sources.json', 'channel_sources01/source_review.json',
             'channel_study_receipt01.json', 'channel_projection01/assessment.json']:
    add(packet / path)
for path, digest in read(packet / 'channel_mount_source_review01.json')['source_images'].items():
    assert sha(ROOT / path) == digest
    add(path)
standard = H / 'transmission_brake_front_study/trial01/standard_context_manifest.json'
add(standard)
for path, digest in read(standard)['native_files'].items():
    assert sha(ROOT / path) == digest
    add(path)
progression = read(out / 'progression_receipt.json')
assert progression['total_count'] == 225
for path, digest in (progression['prior'] | progression['new']).items():
    assert sha(ROOT / path) == digest
    add(path)
preservation = read(out / 'definition_preservation_checks.json')
assert preservation['definition_count'] == 545
for row in read(out / 'preservation_reuse.json')['records']:
    assert sha(ROOT / row['reused_from']) == row['receipt_sha256']
    add(row['reused_from'])
write(out / 'qualification.json', dict(
    local_static_checks_passed=True, native_sha256=r['native_sha256'],
    source_native_sha256=r['source_native_sha256'], parent_control_checkpoint=str((ROOT / r['source_native']).parent.relative_to(ROOT)),
    checks={file: sha(out / file) for file in checks}, dependencies=dependencies,
    counts=dict(occurrences=3202, definitions=551, assemblies=343, new_occurrences=29,
                nominal_checks=75, variation_checks=75, local_pairs_each=57,
                context_pairs_each=3, step_comparisons_each=37, integrated_checks=50,
                prototype_reproduction_checks=7, integrated_reproduction_checks=6,
                unchanged_parent_definitions=545, exact_parent_definitions=preservation['exact_count'],
                strict_parent_definitions=preservation['strict_count'],
                reused_strict_comparisons=len(read(out / 'preservation_reuse.json')['records']),
                progression_images=225),
    scope='M4128 channel and four M4130 cleats, four floor bolt/lockwasher/nut sets, twelve rivets, and four receiving floor holes. Prototype native/interface/context/STEP checks transfer through strict seven-definition and30-installed-shape comparisons; all inherited physical frames and545 unchanged definitions preserved.',
    source_camera_refitted=False,
    open_issues=read(trials[0] / 'visual_review.json')['limits'] + [
        'M4129 attachment has no identified rivet application; determine its mounting topology before adding hardware.',
        'The left clutch-support lower envelope is only about0.57mm above the channel. Upper brackets need actual-surface clearance checks.',
        'Fixed local SNL6 registration retains21.867px control-bore discrepancy. M581 lever identity and complete rod route remain unresolved.'],
    historical_geometry_qualified=False, installation_qualified=False,
    standard_assembly_modified=False, channel_complete=False, packet_complete=False))
print('Frozen mounting evidence:', len(dependencies), 'dependencies; complete tank goal remains active.')
