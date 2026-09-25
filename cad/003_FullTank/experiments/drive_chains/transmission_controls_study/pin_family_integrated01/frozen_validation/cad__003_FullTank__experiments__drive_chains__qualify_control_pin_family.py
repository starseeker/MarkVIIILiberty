"""Freeze the limited static pin-family correction and retained rejected fork datum."""
from pathlib import Path
import shutil
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

C = H/'transmission_controls_study'
out = C/'pin_family_integrated01'
assert not (out/'qualification.json').exists()
r = read(out/'report.json')
checks = {}
for name in ['independent_checks.json', 'definition_preservation_checks.json', 'reproduction_checks.json']:
    q = read(out/name)
    assert q['passed'] and q['native_sha256'] == r['native_sha256']
    checks[name] = sha(out/name)
for folder in [C/'pin_family01', C/'pin_family_variation01']:
    for name in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']:
        q = read(folder/name)
        assert q['passed'] and q['native_sha256'] == read(folder/'report.json')['native_sha256']
assert read(C/'pin_family01/reproduction_checks.json')['passed']
assert read(out/'visual_review.json')['disposition'] == 'reviewed_local_approximation'
modules = [H/(name+'.py') for name in [
    'control_pin_family_parts', 'trial_control_pin_family', 'check_control_pin_family',
    'check_control_pin_family_context', 'exchange_control_pin_family', 'render_control_pin_family',
    'build_control_pin_family', 'check_control_pin_family_installation',
    'check_control_pin_family_preservation', 'seed_control_pin_family_preservation',
    'qualify_control_pin_family', 'verify_control_pin_family_checkpoint',
    'check_rear_control_mount_reproduction', 'check_powertrain_frame_reproduction', 'pump_integration_worker']]
modules += [H.parents[1]/'lib'/(name+'.py') for name in [
    'evidence', 'cad_build', 'camera_review', 'source_camera', 'visual_review',
    'mass_properties', 'kronrod_mass', 'step_matching']]
modules += [H.parents[1]/'lib'/name for name in ['occt_mass_properties.cpp', 'occt_kronrod_mass.cpp']]
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


for folder in [C/'pin_family01', C/'pin_family_variation01', out]:
    for file in sorted(folder.rglob('*')):
        if file.is_file() and not any(p.endswith('_runtime') or p == '__pycache__' for p in file.parts):
            add(file)
    report = read(folder/'report.json')
    for file, digest in report['input_hashes'].items():
        add(file, digest)
    for d in read(folder/'isolated/manifest.json')['definitions'].values():
        add(d['brep_path'], d['brep_sha256'])
for file in modules + [C/name for name in ['pin_family_controls01.json',
        'pin_family_variation_controls01.json', 'pin_family_source_review01.json',
        'channel_local_registration01.json']]:
    add(file)
for name in ['pin_family_controls01.json', 'pin_family_variation_controls01.json']:
    for file, digest in read(C/name)['evidence_hashes'].items():
        add(file, digest)
progression = read(out/'progression_receipt.json')
for file, digest in (progression['prior'] | progression['new']).items():
    add(file, digest)
write(out/'qualification.json', dict(
    local_static_checks_passed=True, native_sha256=r['native_sha256'],
    source_native_sha256=r['source_native_sha256'],
    parent_checkpoint=str((ROOT/r['source_native']).parent.relative_to(ROOT)),
    counts=dict(physical_occurrences=3264, definitions=568, assembly_groups=359),
    scope='One common estimated M568A12.7mm shank and13mm high-speed fork/paired-lever bores. Four definitions revised only at the declared annuli; head, cross-hole, cotter, complete outside material, all frames and564 unrelated definitions preserved. Four actual low-speed eyes accept the same pin. Low-speed fork datum and complete controls remain open.',
    geometry_integrated=True, source_registration_sha256=sha(C/'channel_local_registration01.json'),
    source_camera_refitted=False, historical_geometry_qualified=False,
    installation_qualified=False, standard_assembly_modified=False,
    low_speed_connections_complete=False, channel_complete=False, packet_complete=False,
    open_issues=[
        '12.7mm common shank and13mm bores remain estimates. Specific SNL136 physical-pin length1 5/8in selected over conflicting SNL71 assembly1 7/8in; under-head datum inferred.',
        'M569A printed1in length has no stated datum. A pin-centre-to-face interpretation with the current receiver-clearing profile leaves3.175mm full socket,4.175mm maximum cylindrical patch extent, below the chosen19.05mm engagement criterion. Rejected diagnostic retained; no low-speed forks or SH946E rods installed.',
        'Low fork grip, profile, rod alignment and source-length interpretation require joint reconciliation. Do not make unexplained same-mark pin variants or silently change the printed fork length.',
        'M567 washers, M564 springs, M575/long rods, center/front controls and remaining interiors are unfinished. Other M568A applications remain unmodeled.',
        'Fixed SNL6 camera retains prior high-speed lever/profile/station and spring-height discrepancies; photographs remain uncalibrated. Neither source view proves pin diameter.'
    ], checks=checks, dependencies=dependencies))
print('Frozen', len(dependencies), 'dependencies; pin-family static checkpoint only.', flush=True)
