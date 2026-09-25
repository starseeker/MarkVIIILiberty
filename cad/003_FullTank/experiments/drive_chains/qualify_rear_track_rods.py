"""Freeze the checked straight-rod revision and its explicitly limited source claims."""
from pathlib import Path
import shutil
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

C = H/'transmission_controls_study'
out = C/'track_rods_integrated01'
assert not (out/'qualification.json').exists()
r = read(out/'report.json')
checks = {}
for name in ['independent_checks.json', 'definition_preservation_checks.json', 'reproduction_checks.json']:
    q = read(out/name)
    assert q['passed'] and q['native_sha256'] == r['native_sha256']
    checks[name] = sha(out/name)
for folder in [C/'track_rods02', C/'track_rods_variation02']:
    report = read(folder/'report.json')
    for name in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']:
        q = read(folder/name)
        assert q['passed'] and q['native_sha256'] == report['native_sha256']
assert read(C/'track_rods02/reproduction_checks.json')['passed']
assert read(out/'visual_review.json')['disposition'] == 'reviewed_local_approximation'
modules = [H/(name+'.py') for name in [
    'rear_track_rod_parts', 'trial_rear_track_rods', 'trial_rear_track_rods_aligned',
    'check_rear_track_rods', 'check_rear_track_rods_aligned', 'check_rear_track_rod_context',
    'exchange_rear_track_rods', 'render_rear_track_rods', 'build_rear_track_rods',
    'check_rear_track_rod_installation', 'check_rear_track_rod_preservation',
    'seed_rear_track_rod_preservation', 'verify_rear_track_rod_checkpoint',
    'qualify_rear_track_rods', 'check_rear_control_mount_reproduction',
    'check_powertrain_frame_reproduction', 'pump_integration_worker']]
modules += [H.parents[1]/'lib'/(name+'.py') for name in [
    'evidence', 'cad_build', 'camera_review', 'source_camera', 'visual_review',
    'mass_properties', 'step_matching']]
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


for folder in [C/'track_rod_sources01', C/'track_rods01', C/'track_rods02',
               C/'track_rods_variation02', out]:
    for file in sorted(folder.rglob('*')):
        if file.is_file() and not any(p.endswith('_runtime') or p == '__pycache__' for p in file.parts):
            add(file)
for file in modules + [C/name for name in [
        'track_rod_controls01.json', 'track_rod_controls02.json',
        'track_rod_variation_controls01.json', 'track_rod_variation_controls02.json',
        'track_rod_source_review01.json', 'track_rod_source_review02.json',
        'channel_local_registration01.json']]:
    add(file)
for folder in [C/'track_rods01', C/'track_rods02', C/'track_rods_variation02', out]:
    report = read(folder/'report.json')
    for file, digest in report['input_hashes'].items():
        add(file, digest)
    for d in read(folder/'isolated/manifest.json')['definitions'].values():
        add(d['brep_path'], d['brep_sha256'])
for file, digest in read(C/'track_rod_sources01/sources.json')['source_hashes'].items():
    add(file, digest)
progression = read(out/'progression_receipt.json')
for file, digest in (progression['prior'] | progression['new']).items():
    add(file, digest)
write(out/'qualification.json', dict(
    local_static_checks_passed=True, native_sha256=r['native_sha256'],
    source_native_sha256=r['source_native_sha256'],
    parent_checkpoint=str((ROOT/r['source_native']).parent.relative_to(ROOT)),
    counts=dict(physical_occurrences=3264, definitions=568, assembly_groups=359),
    scope='Two SH946D straight rods installed with one shared definition. Estimated M330 distal arms and M4132 short arms/clocking revised for closure; upper bearing interfaces, full M4132 front-arm material and all unrelated geometry preserved. Eight receiving-eye coordinates remeasured and bound to the new native. Static thread engagement and context checked; complete controls and standard integration remain open.',
    geometry_integrated=True, track_short_rods_static_qualified=True,
    source_registration_sha256=sha(C/'channel_local_registration01.json'),
    source_camera_refitted=False, historical_geometry_qualified=False,
    installation_qualified=False, standard_assembly_modified=False,
    complete_rods_or_springs_qualified=False, channel_complete=False, packet_complete=False,
    open_issues=[
        'SH946D solid19.05mm section and296.0460545mm length are inferred. HB M577 tube wording does not establish the selected1928 rod internal section. Threads remain nominal envelopes.',
        'M330 lower-arm eye Z and M4132 short-arm radius are revised estimates. Small standard lever-angle changes propagate to the front long-rod eyes; full routes, mechanical advantage and motion remain unqualified.',
        'All four M330 distal eyes and both M4132 pairs of rod eyes use the new operating_interfaces.json. Do not reuse their superseded coordinate values from earlier checkpoints.',
        'M568A high-speed15.875mm pin versus13mm low-speed eyes remains unresolved; SH946E joints/rods are not added.',
        'M567 washers, M564 springs, M575 and long rear rods, center/front controls, remaining interiors and standard integration are unfinished.',
        'Fixed SNL6 camera retains inherited lever/profile and spring-height discrepancies; no new edge is promoted to fitting evidence and HB photographs remain uncalibrated.'
    ], checks=checks, dependencies=dependencies))
print('Frozen', len(dependencies), 'dependencies; straight-rod static checkpoint only.', flush=True)
