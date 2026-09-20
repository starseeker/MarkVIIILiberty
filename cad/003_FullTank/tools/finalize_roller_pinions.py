"""Archive milestone 011 after its qualified transfer and recorded visual review.

This does not execute the original parameter trials or perform visual inspection.
It checks the preserved evidence and the separately authored inspection receipt.
Existing snapshots and archives may only be reused when byte-identical.
"""
import hashlib
from pathlib import Path
import shutil
import sys
import zipfile

from promote_roller_pinions import STAGE, REPO, WORK, OUT, read, write, sha, check_files

sys.path.insert(0, str(STAGE))
from lib.evidence import fingerprint, verify_sources
from lib.model import load
from lib.worker import delivery


def main():
    prepared = read(WORK / 'prepare.json')
    transfer_path = OUT / 'reports/qualification_transfer.json'
    transfer = read(transfer_path)
    assert transfer['complete'] and transfer['passed']
    assert sha(WORK / 'prepare.json') == transfer['prepare_receipt_sha256']
    assert sha(Path(__file__).with_name('promote_roller_pinions.py')) == transfer['verification_script_sha256']
    assert fingerprint() == transfer['authored_fingerprint']
    check_files(STAGE, prepared['authored_files'])
    check_files(OUT, transfer['native_hashes'])
    check_files(STAGE.parent, prepared['prior_snapshot_hashes'])
    assert sha(OUT / 'reports/build.json') == transfer['current_build_report_sha256']
    assert sha(OUT / transfer['original_build_report']) == transfer['original_build_report_sha256']
    assert sha(OUT / transfer['original_validation_report']) == transfer['original_validation_sha256']
    assert sha(OUT / 'reports/validation.json') == transfer['original_validation_sha256']
    checkpoint = read(OUT / 'reports/resumable_validation.json')
    assert sha(OUT / 'reports/resumable_validation.json') == sha(OUT / 'reports/qualified_origin/resumable_validation.json')
    assert checkpoint['complete'] and checkpoint['completed_stages'] == 29
    assert checkpoint['binding']['build_report_sha256'] == transfer['original_build_report_sha256']
    assert checkpoint['binding']['fingerprint'] == transfer['authored_fingerprint']
    assert checkpoint['binding']['native_hashes'] == transfer['native_hashes']
    tests = read(OUT / 'reports/record_renderer_tests.json')
    assert tests['passed'] and tests['authored_fingerprint'] == fingerprint()
    check_files(STAGE, tests['test_files'])
    assert sha(OUT / 'reports/record_renderer_tests.log') == tests['log_sha256']
    assert 'Ran 37 tests' in (OUT / 'reports/record_renderer_tests.log').read_text()
    origin_review = read(OUT / 'reports/qualified_origin/integrated_visual_review.json')
    check_files(OUT, origin_review['reviewed_sha256'])
    check_files(OUT, origin_review['source_reviewed_sha256'])
    sources = verify_sources(load()['model']['source_locks'])
    assert sources == transfer['source_lock']
    assert sha(REPO / prepared['previous_release']['archive']) == prepared['previous_release']['archive_sha256']
    origin = transfer['origin_archive']
    assert sha(REPO / origin['archive']) == origin['archive_sha256']
    with zipfile.ZipFile(REPO / origin['archive']) as archive:
        import json
        entries = json.loads(archive.read('origin_archive_manifest.json'))
        assert len(entries) == origin['verified_files']
        for name, expected in entries.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected, name

    review_path = STAGE / 'releases/011-roller-pinions-visual-review.json'
    review = read(review_path)
    assert review['stage'] == '011' and review['status'] == 'inspected'
    assert review['qualification_transfer_sha256'] == sha(transfer_path)
    assert review['authored_fingerprint'] == fingerprint()
    assert review['native_hashes'] == transfer['native_hashes']
    assert review['original_visual_review_sha256'] == sha(OUT / 'reports/qualified_origin/integrated_visual_review.json')
    check_files(OUT, review['reviewed_sha256'])
    assert review['transparent_renderer_report_sha256'] == sha(OUT / 'reports/transparent_isometric.json')
    transparent = read(OUT / 'reports/transparent_isometric.json')
    assert transparent['passed'] and not transparent['native_geometry_changed']
    assert transparent['authored_fingerprint'] == fingerprint()
    assert transparent['native_hashes'] == transfer['native_hashes']
    assert transparent['renderer_sha256'] == sha(Path(__file__).with_name('transparent_isometric.py'))
    check_files(OUT, transparent['output_sha256'])
    shutil.copyfile(review_path, OUT / 'reports/milestone011_visual_review.json')
    shutil.copyfile(transfer_path, STAGE / 'releases/011-roller-pinions-transfer.json')

    snapshots = {
        'intermediate_snapshot_iso_011.png': 'previews/isometric.png',
        'intermediate_snapshot_iso_transparent_011.png': 'previews/isometric_transparent.png',
        'intermediate_snapshot_detail_pinions_011.png': 'comparisons/pinion_drive_oblique.png',
        'intermediate_snapshot_detail_pinion_mounts_011.png': 'comparisons/pinion_mount_detail.png',
    }
    for name, source in snapshots.items():
        assert source in review['reviewed_sha256']
        target = STAGE.parent / name
        if target.exists():
            assert sha(target) == sha(OUT / source), 'Refusing to replace snapshot: ' + name
        else:
            shutil.copyfile(OUT / source, target)
    snapshot_hashes = {name: sha(STAGE.parent / name) for name in snapshots}
    check_files(STAGE.parent, prepared['prior_snapshot_hashes'])

    delivery(load(), OUT)
    with (OUT / 'README.md').open('a') as stream:
        stream.write('\nMilestone 011 adds 196 partial roller-pinion components. The standard assembly now has '
                     '5,326 physical components and 15 layout occurrences.\n\n'
                     'Qualification: 29 stages, 17 parameter trials and 37 record/renderer tests passed '
                     'at the preserved private origin. Byte-identical authored geometry and native files '
                     'were transferred here, then FreeCAD reopened all 20 documents and checked 5,341 '
                     'placements and 252 definitions from this directory. The parameter trials were '
                     'not repeated at this path.\n\n'
                     'See reports/qualification_transfer.json for the explicit binding. The original '
                     'build, validation and review records remain in reports/qualified_origin. Older '
                     'pending/private wording in those records describes their original time and scope. '
                     'The current four-image review is reports/milestone011_visual_review.json.\n\n'
                     '[Transparent-hull isometric](previews/isometric_transparent.png): armor uses '
                     '18% opacity; running gear and interior components stay opaque. Colored interior '
                     'layout envelopes are still provisional. Native geometry is unchanged.\n')
    manifest_path = OUT / 'delivery_manifest.json'
    manifest = read(manifest_path)
    manifest['files']['README.md'] = {'sha256': sha(OUT / 'README.md'), 'bytes': (OUT / 'README.md').stat().st_size}
    write(manifest_path, manifest)
    for name, expected in manifest['files'].items():
        assert sha(OUT / name) == expected['sha256'], name
        assert (OUT / name).stat().st_size == expected['bytes'], name

    archive_path = REPO / '.work/deliveries/011-roller-pinions.zip'
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    names = sorted([*manifest['files'], 'delivery_manifest.json'])
    if not archive_path.exists():
        temporary = archive_path.with_suffix('.zip.tmp')
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name in names:
                archive.write(OUT / name, name)
        temporary.replace(archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        assert sorted(archive.namelist()) == names
        for name in names:
            assert hashlib.sha256(archive.read(name)).hexdigest() == sha(OUT / name), name
    check_files(OUT, transfer['native_hashes'])
    assert fingerprint() == transfer['authored_fingerprint']
    record = dict(stage='011', model_revision=load()['model']['revision'], passed=True,
                  archive=str(archive_path.relative_to(REPO)), archive_sha256=sha(archive_path),
                  archive_bytes=archive_path.stat().st_size, manifest_sha256=sha(manifest_path),
                  verified_manifest_files=len(manifest['files']), native_documents=20,
                  physical_components=5326, definitions=252, physical_source_identities=216,
                  record_renderer_tests=37, validation_stages=29, parameter_trials=17,
                  qualification_method=transfer['method'], parameter_trials_rerun_at_main=False,
                  qualification_transfer_sha256=sha(transfer_path), visual_review_sha256=sha(review_path),
                  source_files_verified=sources['verified_files'], prior_snapshots_verified=18,
                  generated_archive_is_git_ignored=True, archive_contents_checked=True,
                  complete_tank_verified=False, historical_fit_qualified=False,
                  snapshot_hashes=snapshot_hashes, finalizer_sha256=sha(Path(__file__)))
    record['transparent_hull_opacity'] = transparent['armor_opacity']
    record['transparent_renderer_report_sha256'] = sha(OUT / 'reports/transparent_isometric.json')
    write(STAGE / 'releases/011-roller-pinions.json', record)
    write(WORK / 'delivery_audit.json', record)
    print('PASS: milestone 011; {} delivery files, 20 native documents, 18 prior snapshots unchanged.'.format(len(manifest['files'])))


if __name__ == '__main__':
    main()
