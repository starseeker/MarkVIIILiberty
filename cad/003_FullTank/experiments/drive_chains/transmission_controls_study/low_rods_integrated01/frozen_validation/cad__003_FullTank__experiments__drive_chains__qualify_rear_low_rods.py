"""Freeze the checked low-speed straight-rod revision and its explicitly limited source claims."""
from pathlib import Path
import shutil
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha

C = H / 'transmission_controls_study'
out = C / 'low_rods_integrated01'
assert not (out / 'qualification.json').exists()
r = read(out / 'report.json')
checks = {}
for name in ['independent_checks.json', 'definition_preservation_checks.json', 'reproduction_checks.json']:
    q = read(out / name)
    assert q['passed'] and q['native_sha256'] == r['native_sha256']
    checks[name] = sha(out / name)

for folder in [C / 'low_rods01', C / 'low_rods_variation01']:
    report = read(folder / 'report.json')
    for name in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']:
        q = read(folder / name)
        assert q['passed'] and q['native_sha256'] == report['native_sha256']

assert read(C / 'low_rods01/reproduction_checks.json')['passed']
assert read(out / 'visual_review.json')['disposition'] == 'reviewed_local_approximation'

modules = [H / (name + '.py') for name in [
    'trial_rear_low_rods', 'check_rear_low_rods', 'check_rear_low_rod_context',
    'exchange_rear_low_rods', 'render_rear_low_rods', 'build_rear_low_rods',
    'check_rear_low_rod_installation', 'check_rear_low_rod_preservation',
    'render_rear_low_rod_installation', 'verify_rear_low_rod_checkpoint',
    'qualify_rear_low_rods', 'check_rear_control_mount_reproduction',
    'check_powertrain_frame_reproduction', 'pump_integration_worker']]
modules += [H.parents[1] / 'lib' / (name + '.py') for name in [
    'evidence', 'cad_build', 'camera_review', 'source_camera', 'visual_review',
    'mass_properties', 'step_matching']]

frozen = out / 'frozen_validation'
frozen.mkdir()
for file in modules:
    shutil.copy2(file, frozen / str(file.relative_to(ROOT)).replace('/', '__'))

dependencies = {}


def add(path, expected=None):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    digest = sha(path)
    assert expected is None or digest == expected, str(path)
    dependencies[str(path.relative_to(ROOT))] = digest


for folder in [C / 'low_rod_sources01', C / 'low_rods01', C / 'low_rods_variation01', out]:
    for file in sorted(folder.rglob('*')):
        if file.is_file() and not any(p.endswith('_runtime') or p == '__pycache__' for p in file.parts):
            add(file)

for file in modules + [C / name for name in [
        'low_rod_controls01.json', 'low_rod_variation_controls01.json',
        'low_rod_source_review01.json', 'channel_local_registration01.json']]:
    add(file)

for folder in [C / 'low_rods01', C / 'low_rods_variation01', out]:
    report = read(folder / 'report.json')
    for file, digest in report['input_hashes'].items():
        add(file, digest)
    for d in read(folder / 'isolated/manifest.json')['definitions'].values():
        add(d['brep_path'], d['brep_sha256'])

for file, digest in read(C / 'low_rod_sources01/sources.json')['source_hashes'].items():
    add(file, digest)

progression = read(out / 'progression_receipt.json')
for file, digest in (progression['prior'] | progression['new']).items():
    add(file, digest)

write(out / 'qualification.json', dict(
    local_static_checks_passed=True, native_sha256=r['native_sha256'],
    source_native_sha256=r['source_native_sha256'],
    parent_checkpoint=str((ROOT / r['source_native']).parent.relative_to(ROOT)),
    counts=dict(physical_occurrences=3282, definitions=570, assembly_groups=365),
    scope='Two SH946E straight rods installed with one shared definition (Def_RearLowRod). Reconciled horizontal fulcrum levers M4134 (Starboard) and M4133 (Port) brake arm profiles symmetrically to [39.6875, ±85.395714] mm for straight-rod closure; all other lever geometry, front brake levers, upper bearing interfaces, and all unrelated geometry preserved. Static thread engagement (>= 19.05 mm), context, and 567 inherited definitions preserved. Complete controls, springs, and standard integration remain open.',
    geometry_integrated=True, low_short_rods_static_qualified=True,
    source_registration_sha256=sha(C / 'channel_local_registration01.json'),
    source_camera_refitted=False, historical_geometry_qualified=False,
    installation_qualified=False, standard_assembly_modified=False,
    complete_rods_or_springs_qualified=False, channel_complete=False, packet_complete=False,
    open_issues=[
        'SH946E solid 19.05 mm section and 130.761619 mm length are inferred. HB M-572 tube wording does not establish the selected 1928 rod internal section. Threads remain nominal envelopes.',
        'M4134/M4133 fulcrum lever brake arms reconciled to xb = 39.6875 mm (1-9/16 in), symmetrically adjusting prior provisional picks by ±7.9375 mm (5/16 in). Full routes, mechanical advantage, and motion remain unqualified.',
        'Low-speed brake receiver eyes use the updated operating_interfaces.json. Do not reuse superseded coordinate values from earlier checkpoints.',
        'M567 washers, M564 springs, M575 and long rear rods, center/front controls, remaining interiors, and standard integration are unfinished.',
        'Fixed SNL6 camera retains inherited lever/profile and spring-height discrepancies; no new edge is promoted to fitting evidence and HB photographs remain uncalibrated.'
    ], checks=checks, dependencies=dependencies))
print('Frozen', len(dependencies), 'dependencies; low-speed straight-rod static checkpoint only.', flush=True)
