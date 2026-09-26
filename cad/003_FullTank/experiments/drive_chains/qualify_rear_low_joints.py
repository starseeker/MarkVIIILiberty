"""Freeze completed local low-speed joint evidence without claiming historical completion."""
from pathlib import Path
import shutil
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

C = H/'transmission_controls_study'
out = C/'low_joints_integrated01'
assert not (out/'qualification.json').exists()
r = read(out/'report.json')
checks = {}
for name in ['independent_checks.json', 'definition_preservation_checks.json', 'reproduction_checks.json']:
    q = read(out/name)
    assert q['passed'] and q['native_sha256'] == r['native_sha256']
    checks[name] = sha(out/name)
for folder in [C/'low_joints01', C/'low_joints_variation01']:
    report = read(folder/'report.json')
    for name in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']:
        q = read(folder/name)
        assert q['passed'] and q['native_sha256'] == report['native_sha256']
assert read(C/'low_joints01/reproduction_checks.json')['passed']
assert read(out/'visual_review.json')['disposition'] == 'reviewed_local_approximation'
modules = [H/(name+'.py') for name in [
    'trial_rear_low_joints', 'check_rear_low_joints', 'check_rear_low_joint_context',
    'exchange_rear_low_joints', 'render_rear_low_joints',
    'build_rear_low_joints', 'check_rear_low_joint_installation',
    'check_rear_low_joint_preservation', 'seed_rear_low_joint_preservation',
    'render_rear_low_joint_installation', 'verify_rear_low_joint_checkpoint',
    'qualify_rear_low_joints', 'check_rear_control_mount_reproduction',
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


for folder in [C/'low_joints01', C/'low_joints_variation01', out]:
    for file in sorted(folder.rglob('*')):
        if file.is_file() and not any(p.endswith('_runtime') or p == '__pycache__' for p in file.parts):
            add(file)
for file in modules + [C/name for name in [
        'low_joint_controls01.json', 'low_joint_variation_controls01.json',
        'low_joint_source_review01.json', 'channel_local_registration01.json']]:
    add(file)
for folder in [C/'low_joints01', C/'low_joints_variation01', out]:
    report = read(folder/'report.json')
    for file, digest in report['input_hashes'].items():
        add(file, digest)
    for d in read(folder/'isolated/manifest.json')['definitions'].values():
        add(d['brep_path'], d['brep_sha256'])
progression = read(out/'progression_receipt.json')
for file, digest in (progression['prior'] | progression['new']).items():
    add(file, digest)
write(out/'qualification.json', dict(
    local_static_checks_passed=True, native_sha256=r['native_sha256'],
    source_native_sha256=r['source_native_sha256'],
    parent_checkpoint=str((ROOT/r['source_native']).parent.relative_to(ROOT)),
    counts=dict(physical_occurrences=3280, definitions=569, assembly_groups=365),
    scope='Four M569A/M568A/cotter/plain-nut end joints installed: 16 added parts, one new shared definition (Def_LowJoint_fork) and three reused definitions (Def_ControlJoint_pin, Def_ControlJoint_cotter, Def_USStdControlNut). Tested prototype material transferred to the full hierarchy, all inherited geometry and frames preserved. Rods, springs and standard integration remain open.',
    geometry_integrated=True,
    source_registration_sha256=sha(C/'channel_local_registration01.json'),
    source_camera_refitted=False, historical_geometry_qualified=False,
    installation_qualified=False, standard_assembly_modified=False,
    complete_rods_or_springs_qualified=False, channel_complete=False, packet_complete=False,
    open_issues=[
        'M569A fork length 1 inch literal source dimension interpreted under throat_to_rod_seat datum (49.2125mm pin-center-to-face, 25.4mm socket). Alternative pin-center-to-face datum remains rejected as failing thread engagement.',
        'Low-speed rod alignment: front forks point along +X with transverse pins along Y; rear forks mount on vertical pins clocked along the horizontal rod chord. Two SH946E physical rods connecting front and rear joints remain pending in low_rods increment.',
        'M567 washers, M564 springs, M575 and long rear rods, center/front controls, service and remaining interiors are unfinished.',
        'Fixed SNL6 registration retains inherited lever silhouette, spring height/inclination and photographic discrepancies. No historical photographic camera fit is claimed.'
    ], checks=checks, dependencies=dependencies))
print('Frozen', len(dependencies), 'dependencies; local static checkpoint only.', flush=True)
