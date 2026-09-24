"""Freeze completed local track-joint evidence without claiming historical completion."""
from pathlib import Path
import shutil
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

C = H/'transmission_controls_study'
out = C/'track_joints_integrated01'
assert not (out/'qualification.json').exists()
r = read(out/'report.json')
checks = {}
for name in ['independent_checks.json', 'definition_preservation_checks.json', 'reproduction_checks.json']:
    q = read(out/name)
    assert q['passed'] and q['native_sha256'] == r['native_sha256']
    checks[name] = sha(out/name)
for folder in [C/'track_joints02', C/'track_joints_variation02']:
    report = read(folder/'report.json')
    for name in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']:
        q = read(folder/name)
        assert q['passed'] and q['native_sha256'] == report['native_sha256']
assert read(C/'track_joints02/reproduction_checks.json')['passed']
assert read(out/'visual_review.json')['disposition'] == 'reviewed_local_approximation'
modules = [H/(name+'.py') for name in [
    'trial_rear_track_joints', 'check_rear_track_joints', 'check_rear_track_joint_context',
    'exchange_rear_track_joints', 'render_rear_track_joints', 'probe_rear_short_joint_constraints',
    'build_rear_track_joints', 'check_rear_track_joint_installation',
    'check_rear_track_joint_preservation', 'seed_rear_track_joint_preservation',
    'render_rear_track_joint_installation', 'verify_rear_track_joint_checkpoint',
    'qualify_rear_track_joints', 'check_rear_control_mount_reproduction',
    'check_powertrain_frame_reproduction', 'pump_integration_worker']]
frozen = out/'frozen_validation'
frozen.mkdir()
for file in modules:
    shutil.copy2(file, frozen/str(file.relative_to(ROOT)).replace('/', '__'))
dependencies = {}


def add(path, expected=None):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT/path
    digest = sha(path)
    assert expected is None or digest == expected, str(path)
    dependencies[str(path.relative_to(ROOT))] = digest


for folder in [C/'short_joint_sources01', C/'track_joints01', C/'track_joints02',
               C/'track_joints_variation02', out]:
    for file in sorted(folder.rglob('*')):
        if file.is_file() and not any(p.endswith('_runtime') or p == '__pycache__' for p in file.parts):
            add(file)
for file in modules + [C/name for name in [
        'track_joint_controls01.json', 'track_joint_controls02.json',
        'track_joint_variation_controls02.json', 'track_joint_source_review01.json',
        'track_joint_source_review02.json', 'channel_local_registration01.json']]:
    add(file)
for folder in [C/'track_joints01', C/'track_joints02', C/'track_joints_variation02', out]:
    report = read(folder/'report.json')
    for file, digest in report['input_hashes'].items():
        add(file, digest)
    for d in read(folder/'isolated/manifest.json')['definitions'].values():
        add(d['brep_path'], d['brep_sha256'])
for file, digest in read(C/'short_joint_sources01/sources.json')['source_hashes'].items():
    add(file, digest)
progression = read(out/'progression_receipt.json')
for file, digest in (progression['prior'] | progression['new']).items():
    add(file, digest)
write(out/'qualification.json', dict(
    local_static_checks_passed=True, native_sha256=r['native_sha256'],
    source_native_sha256=r['source_native_sha256'],
    parent_checkpoint=str((ROOT/r['source_native']).parent.relative_to(ROOT)),
    counts=dict(physical_occurrences=3262, definitions=567, assembly_groups=359),
    scope='Four M569C/M568C/cotter/plain-nut end joints installed:16 added parts, three new shared definitions and one reused nut. Tested prototype material transferred to the full hierarchy, all inherited geometry and frames preserved. Rods, low-speed shared-pin reconciliation, springs and standard integration remain open.',
    geometry_integrated=True,
    source_registration_sha256=sha(C/'channel_local_registration01.json'),
    source_camera_refitted=False, historical_geometry_qualified=False,
    installation_qualified=False, standard_assembly_modified=False,
    complete_rods_or_springs_qualified=False, channel_complete=False, packet_complete=False,
    open_issues=[
        'M569C profile/throat/socket and M568C diameter/head are estimates; listed pin length datum is assumed under head.',
        'Horizontal socket axes are provisional. Both SH946D occurrences require common rod geometry, angular closure and engagement; previous core corridors did not qualify full fork/rod interfaces.',
        'SNL136 assigns M568A to M569A and M569B. Current15.875mm high-speed pin conflicts with13.0mm low-speed receiver bores; reconcile estimates before adding low-speed joints.',
        'M567 washers, M564 springs, M575 and long rear rods, center/front controls, service and remaining interiors are unfinished.',
        'Fixed SNL6 registration retains inherited lever silhouette, spring height/inclination and21.867px high-speed control-bore disagreement. No historical photographic camera fit is claimed.'
    ], checks=checks, dependencies=dependencies))
print('Frozen', len(dependencies), 'dependencies; local static checkpoint only.', flush=True)
