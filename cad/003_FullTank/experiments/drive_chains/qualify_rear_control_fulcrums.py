"""Freeze bounded fulcrum evidence; preserve source uncertainty and earlier hypotheses."""
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
out = packet / 'fulcrum_integrated01'
assert not (out / 'qualification.json').exists()
r = read(out / 'report.json')
assert sha(out / r['native_file']) == r['native_sha256']
checks = ['independent_checks.json', 'definition_preservation_checks.json',
          'reproduction_checks.json', 'operating_interfaces.json']
checkers = ['check_rear_control_fulcrum_installation.py',
            'check_rear_control_fulcrum_preservation.py',
            'check_powertrain_frame_reproduction.py',
            'probe_rear_control_fulcrum_interfaces.py']
for file, checker in zip(checks, checkers):
    receipt = read(out / file)
    assert receipt['passed'] and receipt['native_sha256'] == r['native_sha256']
    assert receipt.get('checker_sha256', receipt.get('probe_sha256')) == sha(H / checker)
assert len(read(out / checks[0])['checks']) == 46
assert len(read(out / 'reproduction_checks.json')['checks']) == 6
interfaces = read(out / 'operating_interfaces.json')
assert len(interfaces['new_rod_eyes']) == 8
assert len(interfaces['verified_rear_brake_eyes']) == 4
assert read(out / 'visual_review.json')['disposition'] == 'reviewed_local_approximation'

trials = [packet / 'fulcrum02', packet / 'fulcrum_variation02']
for trial in trials:
    report = read(trial / 'report.json')
    assert sha(trial / report['native_file']) == report['native_sha256']
    for file, checker in [
        ('independent_checks.json', 'check_rear_control_fulcrums.py'),
        ('context_checks.json', 'check_rear_control_fulcrum_context.py'),
        ('exchange_checks.json', 'exchange_rear_control_fulcrums.py'),
    ]:
        receipt = read(trial / file)
        assert receipt['passed'] and receipt['native_sha256'] == report['native_sha256']
        assert receipt['checker_sha256'] == sha(H / checker)
    assert len(read(trial / 'independent_checks.json')['checks']) == 82
    assert len(read(trial / 'independent_checks.json')['material_pairs']) == 46
    assert len(read(trial / 'context_checks.json')['pairs']) == 4
    exchange = read(trial / 'exchange_checks.json')
    assert len(exchange['checks']) == 33
    for path, digest in exchange['step_hashes'].items():
        assert sha(trial / path) == digest
nominal, variant = [read(t / 'report.json')['controls'] for t in trials]
expected = copy.deepcopy(nominal)
expected['bracket']['foot_stock'] += .5
assert variant == expected
reproduction = read(trials[0] / 'reproduction_checks.json')
assert reproduction['passed'] and len(reproduction['checks']) == 7
assert reproduction['native_sha256'] == read(trials[0] / 'report.json')['native_sha256']
assert reproduction['checker_sha256'] == sha(H / 'check_rear_control_mount_reproduction.py')

parent = (ROOT / r['source_native']).parent
subprocess.run([sys.executable, str(H / 'verify_rear_control_mount_checkpoint.py'),
                '--candidate', str(parent)], check=True)
registration_hash = sha(packet / 'channel_local_registration01.json')
registration_path = str((packet / 'channel_local_registration01.json').relative_to(ROOT))
assert read(parent / 'qualification.json')['dependencies'][registration_path] == registration_hash
for directory in [parent, trials[0], out]:
    render = read(directory / 'render_receipt.json')
    if directory != parent:
        assert render['source_registration_sha256'] == registration_hash
    assert not render['source_camera_refitted']
    for path, digest in render['images'].items():
        assert sha(directory / path) == digest
camera = read(out / 'camera_reuse_review.json')
assert camera['registration_sha256'] == registration_hash
assert not camera['source_camera_refitted']

scripts = [H / name for name in [
    'rear_control_fulcrum_parts.py', 'trial_rear_control_fulcrums.py',
    'check_rear_control_fulcrums.py', 'check_rear_control_fulcrum_context.py',
    'exchange_rear_control_fulcrums.py', 'render_rear_control_fulcrums.py',
    'build_rear_control_fulcrums.py', 'check_rear_control_fulcrum_installation.py',
    'check_rear_control_fulcrum_preservation.py', 'seed_rear_control_fulcrum_preservation.py',
    'render_rear_control_fulcrum_installation.py', 'probe_rear_control_fulcrum_interfaces.py',
    'check_rear_control_mount_reproduction.py', 'check_powertrain_frame_reproduction.py',
    'pump_integration_worker.py', 'qualify_rear_control_fulcrums.py',
    'verify_rear_control_fulcrum_checkpoint.py']]
scripts += [STAGE / 'lib' / name for name in ['evidence.py', 'cad_build.py', 'camera_review.py',
                                            'mass_properties.py', 'step_matching.py',
                                            'visual_review.py', 'source_camera.py']]
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
early = [packet / 'fulcrum01', packet / 'fulcrum_variation01']
for directory in [out, *trials, *early]:
    for path in directory.rglob('*'):
        if not path.is_file() or any(name in path.parts for name in
                                    ['adaptive_mass_runtime', 'preservation_runtime', '__pycache__']):
            continue
        add(path)
    report = read(directory / 'report.json')
    assert sha(directory / report['native_file']) == report['native_sha256']
    for path, digest in report['input_hashes'].items():
        live = ROOT / path
        # Early hypotheses deliberately retain their original builders. Their
        # receipts bind frozen inputs, not the later revised live code.
        if directory in early and sha(live) != digest:
            snapshot = directory / ('input_' + live.name)
            assert sha(snapshot) == digest, (directory, path)
            add(snapshot)
        else:
            assert sha(live) == digest, (directory, path)
            add(live)
for path in ['fulcrum_controls01.json', 'fulcrum_controls02.json',
             'fulcrum_controls_variation01.json', 'fulcrum_controls_variation02.json',
             'fulcrum_source_review01.json', 'fulcrum_source_review02.json',
             'channel_local_registration01.json', 'sources.json',
             'channel_sources01/sources.json', 'channel_sources01/source_review.json',
             'channel_projection01/assessment.json', 'context01/report.json']:
    add(packet / path)
for path, digest in read(packet / 'fulcrum_source_review02.json')['additional_source'].items():
    assert sha(ROOT / path) == digest
    add(path)
for path, digest in read(out / 'catalogue_scan_review.json')['source_images'].items():
    assert sha(ROOT / path) == digest
    add(path)
standard = H / 'transmission_brake_front_study/trial01/standard_context_manifest.json'
add(standard)
for path, digest in read(standard)['native_files'].items():
    assert sha(ROOT / path) == digest
    add(path)
progression = read(out / 'progression_receipt.json')
assert progression['total_count'] == 229
assert len(progression['prior']) == 225 and len(progression['new']) == 4
for path, digest in (progression['prior'] | progression['new']).items():
    assert sha(ROOT / path) == digest
    add(path)
preservation = read(out / 'definition_preservation_checks.json')
assert preservation['definition_count'] == 550
assert preservation['exact_count'] == 529 and preservation['strict_count'] == 21
reuse = read(out / 'preservation_reuse.json')['records']
assert len(reuse) == 16
for row in reuse:
    assert sha(ROOT / row['reused_from']) == row['receipt_sha256']
    add(row['reused_from'])
manifest = read(out / 'isolated/manifest.json')
assert len(manifest['occurrences']) == 3226
assert len(manifest['definitions']) == 558 and len(manifest['assemblies']) == 347
write(out / 'qualification.json', dict(
    local_static_checks_passed=True, native_sha256=r['native_sha256'],
    source_native_sha256=r['source_native_sha256'],
    parent_checkpoint=str(parent.relative_to(ROOT)),
    checks={file: sha(out / file) for file in checks}, dependencies=dependencies,
    counts=dict(occurrences=3226, definitions=558, assemblies=347, new_occurrences=24,
                nominal_checks=82, variation_checks=82, local_pairs_each=46,
                context_pairs_each=4, step_comparisons_each=33, integrated_checks=46,
                prototype_reproduction_checks=7, integrated_reproduction_checks=6,
                unchanged_parent_definitions=550, exact_parent_definitions=529,
                strict_parent_definitions=21, reused_strict_comparisons=16,
                measured_control_eyes=12, progression_images=229),
    scope='Four M4131 bracket/journals, four horizontal levers (two M4132, one M4133, '
          'one M4134), four M4137 washers, four cotters and eight rivets, with eight '
          'new receiving channel holes. Prototype native/interface/context/STEP checks '
          'transfer through strict eight-definition and25-installed-shape comparisons; '
          'all inherited physical frames and550 unchanged definitions preserved. '
          'No repeated full integrated STEP export is claimed.',
    source_camera_refitted=False,
    open_issues=read(out / 'visual_review.json')['limits'],
    historical_geometry_qualified=False, installation_qualified=False,
    standard_assembly_modified=False, channel_complete=False, packet_complete=False))
print('Frozen fulcrum evidence:', len(dependencies),
      'dependencies; complete tank goal remains active.')
