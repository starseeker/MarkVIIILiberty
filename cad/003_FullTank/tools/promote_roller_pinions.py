"""Promote the exact qualified pinion artifacts, then verify their main-path links.

The original 29-stage validation stays byte-identical. A separate transfer
receipt binds it to the one changed build-report path and fresh native checks.
Run prepare, then verify; final release/image review is a separate operation.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]
WORK = REPO / '.work/pinion-promotion'
OUT = STAGE / 'build'
PREFLIGHT = STAGE / 'experiments/roller_pinions/integrated_preflight'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def check_files(base, entries):
    for name, expected in entries.items():
        if sha(base / name) != expected:
            raise ValueError('Missing or changed artifact: ' + str(base / name))


def prepare():
    if (WORK / 'prepare.json').exists():
        raise ValueError('Promotion already prepared; inspect its receipt before resuming')
    record = read(PREFLIGHT / 'qualified_origin_archive.json')
    archive = REPO / record['archive']
    assert sha(archive) == record['archive_sha256']
    previous_release = read(STAGE / 'releases/010-drive-mounts.json')
    assert sha(REPO / previous_release['archive']) == previous_release['archive_sha256']
    old_build = read(OUT / 'reports/build.json')
    check_files(STAGE, old_build['fingerprint'])
    check_files(OUT, old_build['native_hashes'])
    assert read(STAGE / 'data/model.json')['revision'] == 'standard_partial_drive_mounts'
    prior_images = read(REPO / '.work/pinion-prior-snapshots.json')
    check_files(STAGE.parent, prior_images)
    assert len(prior_images) == 18
    incoming = WORK / 'incoming_build'
    backup = WORK / 'previous_authored'
    previous_build = WORK / 'previous_build_010'
    assert not incoming.exists() and not previous_build.exists() and not backup.exists()
    receipt = dict(complete=False, started_epoch=time.time(), script_sha256=sha(Path(__file__)),
                   origin_archive=record, previous_release=previous_release,
                   prior_snapshot_hashes=prior_images, previous_build=str(previous_build),
                   main_build_path=str(OUT))
    write(WORK / 'prepare_status.json', receipt)
    with zipfile.ZipFile(archive) as z:
        entries = json.loads(z.read('origin_archive_manifest.json'))
        assert len(entries) == record['verified_files']
        for name, expected in entries.items():
            path = Path(name)
            assert not path.is_absolute() and '..' not in path.parts
            assert hashlib.sha256(z.read(name)).hexdigest() == expected
        original = json.loads(z.read('build/reports/build.json'))
        qualification = json.loads(z.read('runs/qualification_status.json'))
        validation = json.loads(z.read('build/reports/validation.json'))
        checkpoint = json.loads(z.read('build/reports/resumable_validation.json'))
        tests = json.loads(z.read('runs/record_renderer_tests.json'))
        assert qualification['complete'] and qualification['passed'] and qualification['exit_code'] == 0
        assert qualification['authored_fingerprint'] == original['fingerprint']
        assert validation['implemented_checks_passed'] and checkpoint['completed_stages'] == 29
        assert checkpoint['binding']['build_report_sha256'] == entries['build/reports/build.json']
        assert checkpoint['binding']['fingerprint'] == original['fingerprint']
        assert checkpoint['binding']['native_hashes'] == original['native_hashes']
        assert tests['passed'] and tests['authored_fingerprint'] == original['fingerprint']
        assert hashlib.sha256(z.read('runs/record_renderer_tests.log')).hexdigest() == tests['log_sha256']
        assert b'Ran 37 tests' in z.read('runs/record_renderer_tests.log')
        for name, expected in tests['test_files'].items():
            assert entries['authored/' + name] == expected
        certificate = read(PREFLIGHT / 'qualification_receipt.json')
        assert certificate['passed'] and certificate['authored_fingerprint'] == original['fingerprint']
        assert certificate['native_hashes'] == original['native_hashes']
        for name, expected in certificate['qualification_evidence'].items():
            assert sha(REPO / name) == expected
        authored = {name.removeprefix('authored/'): expected for name, expected in entries.items()
                    if name.startswith('authored/')}
        assert all('authored/' + name in entries for name in original['fingerprint'])
        for name, expected in original['fingerprint'].items():
            assert authored[name] == expected
        assert not set(old_build['fingerprint']) - set(original['fingerprint'])
        for name in entries:
            if name.startswith('build/'):
                target = incoming / name.removeprefix('build/')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(name))
        origin_folder = incoming / 'reports/qualified_origin'
        origin_folder.mkdir()
        # Preserve exact receipts and their binding targets, without rewriting them.
        for name in ['build.json', 'validation.json', 'resumable_validation.json']:
            shutil.copy2(incoming / 'reports' / name, origin_folder / name)
        for name in entries:
            if name.startswith('runs/'):
                target = origin_folder / Path(name).name
                target.write_bytes(z.read(name))
        shutil.copy2(PREFLIGHT / 'qualification_receipt.json', origin_folder / 'qualification_receipt.json')
        shutil.copy2(PREFLIGHT / 'qualified_origin_archive.json', origin_folder / 'archive_record.json')
        rebased = copy.deepcopy(original)
        rebased['build']['top_document'] = str(OUT / 'native/MarkVIII.FCStd')
        write(incoming / 'reports/build.json', rebased)
        changed = copy.deepcopy(rebased)
        changed['build']['top_document'] = original['build']['top_document']
        assert changed == original
        # Keep the source tests with the delivery as well as in the origin records.
        for name in ['record_renderer_tests.json', 'record_renderer_tests.log']:
            shutil.copy2(origin_folder / name, incoming / 'reports' / name)
        previous_authored = {}
        for name in authored:
            target = STAGE / name
            previous_authored[name] = sha(target) if target.exists() else None
            if target.exists():
                saved = backup / name
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, saved)
        receipt.update(authored_files=authored, previous_authored_files=previous_authored,
                       origin_build_report_sha256=entries['build/reports/build.json'],
                       origin_validation_sha256=entries['build/reports/validation.json'],
                       rebased_build_report_sha256=sha(incoming / 'reports/build.json'),
                       origin_native_hashes=original['native_hashes'],
                       qualification_receipt_sha256=sha(PREFLIGHT / 'qualification_receipt.json'))
        write(WORK / 'prepare_status.json', receipt)
        swapped = False
        try:
            for name in authored:
                target = STAGE / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read('authored/' + name))
            check_files(STAGE, authored)
            OUT.rename(previous_build)
            swapped = True
            incoming.rename(OUT)
            check_files(OUT, original['native_hashes'])
            check_files(STAGE.parent, prior_images)
        except Exception:
            if swapped:
                if OUT.exists():
                    OUT.rename(WORK / 'failed_incoming_build')
                previous_build.rename(OUT)
            for name, expected in previous_authored.items():
                if expected is None:
                    (STAGE / name).unlink(missing_ok=True)
                else:
                    shutil.copy2(backup / name, STAGE / name)
            receipt.update(complete=True, passed=False, rolled_back=True)
            write(WORK / 'prepare_status.json', receipt)
            raise
    receipt.update(complete=True, passed=True)
    write(WORK / 'prepare.json', receipt)
    write(WORK / 'prepare_status.json', receipt)
    print('Promoted exact qualified sources and 20 native files; main-path CAD verification pending.', flush=True)


def verify(worker):
    sys.path.insert(0, str(STAGE))
    from lib import runtime
    if not worker:
        with (WORK / 'verify.log').open('w') as log:
            return subprocess.run([sys.executable, __file__, 'verify', '--worker'],
                                  env=runtime.environment(WORK), stdout=log, stderr=subprocess.STDOUT).returncode
    try:
        App, Gui = runtime.start_gui()
        import Part
        import numpy
        import scipy
        import fitz
        from lib.evidence import fingerprint, verify_sources
        from lib.model import load
        from lib.cad_build import leaves, frame, shape_signature
        from lib.worker import check_build, same_shape, placement_errors, coverage
        prepared = read(WORK / 'prepare.json')
        assert prepared['passed'] and prepared['script_sha256'] == sha(Path(__file__))
        check_files(STAGE, prepared['authored_files'])
        current = check_build(OUT)
        original = read(OUT / 'reports/qualified_origin/build.json')
        validation = read(OUT / 'reports/qualified_origin/validation.json')
        assert sha(OUT / 'reports/qualified_origin/build.json') == prepared['origin_build_report_sha256']
        assert sha(OUT / 'reports/validation.json') == prepared['origin_validation_sha256']
        assert sha(OUT / 'reports/build.json') == prepared['rebased_build_report_sha256']
        expected_runtime = validation['checkpoint_audit']['binding']['runtime']
        current_runtime = dict(FreeCAD=App.Version(), OpenCASCADE=Part.OCC_VERSION,
                               Python=sys.version, numpy=numpy.__version__, scipy=scipy.__version__, fitz=fitz.VersionBind)
        assert current_runtime == expected_runtime
        data = load()
        sources = verify_sources(data['model']['source_locks'])
        assert sources['verified_files'] == 754
        doc = App.openDocument(str(OUT / 'native/MarkVIII.FCStd'))
        doc.recompute()
        items = leaves(doc.Root)
        ids = [i['id'] for i in items]
        nodes = {n['id']: n for n in data['occurrences']}
        expected = {n['id'] for n in data['occurrences'] if n['definition']}
        assert len(ids) == len(set(ids)) == 5341 and set(ids) == expected == set(original['geometry'])
        definitions = set()
        translation = rotation = 0.0
        for item in items:
            target = item['target']
            assert (OUT / 'native').resolve() in Path(target.Document.FileName).resolve().parents
            if item['definition'] not in definitions:
                assert target.Shape.isValid()
                definitions.add(item['definition'])
            expected_pose = frame(nodes[item['id']]['frame'], data).multiply(target.Shape.Placement)
            t, r = placement_errors(item['shape'].Placement, expected_pose)
            translation, rotation = max(translation, t), max(rotation, r)
            assert t <= 1e-6 and r <= 1e-8, item['id']
            assert same_shape(original['geometry'][item['id']], shape_signature(item['shape'])), item['id']
        assert len(definitions) == 252
        documents = {}
        for opened in App.listDocuments().values():
            path = Path(opened.FileName).resolve()
            assert (OUT / 'native').resolve() in path.parents
            documents[str(path.relative_to(OUT))] = sha(path)
        assert documents == original['native_hashes']
        actual_coverage = coverage(data, items)
        assert actual_coverage == read(OUT / 'reports/coverage.json')
        assert actual_coverage['component_occurrences'] == 5326
        review = read(OUT / 'reports/qualified_origin/integrated_visual_review.json')
        assert review['authored_fingerprint'] == fingerprint() == original['fingerprint']
        for key in ['reviewed_sha256', 'source_reviewed_sha256']:
            check_files(OUT, review[key])
        check_files(STAGE.parent, prepared['prior_snapshot_hashes'])
        check_build(OUT)
        receipt = dict(complete=True, passed=True,
                       method='Byte-identical qualified source/native transfer with fresh main-path native checks',
                       original_build_report='reports/qualified_origin/build.json',
                       original_build_report_sha256=prepared['origin_build_report_sha256'],
                       original_validation_report='reports/qualified_origin/validation.json',
                       original_validation_sha256=prepared['origin_validation_sha256'],
                       current_build_report_sha256=sha(OUT / 'reports/build.json'),
                       build_report_change='Only build.top_document was rebound to the main native directory.',
                       origin_archive=prepared['origin_archive'],
                       authored_fingerprint=fingerprint(), native_hashes=documents,
                       main_top_document=str(OUT / 'native/MarkVIII.FCStd'),
                       loaded_documents=len(documents), unique_occurrences=len(items),
                       valid_definitions=len(definitions), source_coverage=actual_coverage,
                       all_native_dependencies_inside_main=True, all_original_geometry_signatures_match=True,
                       max_translation_error_mm=translation, max_rotation_basis_error=rotation,
                       source_lock=sources, runtime=current_runtime,
                       original_validation_stages=29, original_parameter_trials=17,
                       original_record_renderer_tests=37, reviewed_rasters_verified=9,
                       prior_snapshots_unchanged=True, prepare_receipt_sha256=sha(WORK / 'prepare.json'),
                       verification_script_sha256=sha(Path(__file__)),
                       complete_tank_verified=False, historical_fit_qualified=False)
        write(OUT / 'reports/qualification_transfer.json', receipt)
        write(WORK / 'verification.json', receipt)
        print('PASS: 20 main-path native documents, 252 definitions, 5341 placements and original geometry signatures.', flush=True)
        return 0
    finally:
        runtime.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'verify'])
    parser.add_argument('--worker', action='store_true')
    arguments = parser.parse_args()
    if arguments.command == 'prepare':
        prepare()
    else:
        sys.exit(verify(arguments.worker))
