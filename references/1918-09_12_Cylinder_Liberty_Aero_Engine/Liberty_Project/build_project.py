"""Finish the Liberty manual from its exact v08 baseline, inside Scribus 1.6.x.
Only unprinted closing cover surfaces are added. Scanner-only sources 163–167
are documented separately. The released current master is never an input.
"""
from pathlib import Path
import os, json, traceback, runpy
import scribus as s
ROOT = Path(__file__).resolve().parent
R = json.loads((ROOT / 'data/release.json').read_text())

def main():
    for name in ['build_error.txt', 'data/build_success.json']:
        p = ROOT / name
        if p.exists():
            p.unlink()
    fonts = {'C059 Roman', 'C059 Bold', 'C059 Italic', 'Nimbus Sans Bold'}
    missing = fonts - set(s.getFontNames())
    if missing:
        raise RuntimeError('Install bundled OpenType fonts: ' + str(missing))
    runpy.run_path(str(ROOT / 'scripts/prepare_batch09_seed.py'))
    s.openDoc(str(ROOT / '_batch09_seed.sla'))
    assert s.pageCount() == 162
    s.setInfo('Ministry of Munitions; digital reconstruction',
              'The Liberty 12-Cylinder Aero Engine Handbook (1918) — ' + R['release_id'],
              'Complete first reconstruction pass, batches 01–09. 162 manual pages '
              'from source scans 0001–0162, through printed page 151 and closing '
              'cover surfaces. Five scanner-only sources 0163–0167 are excluded '
              'from the manual and retained in the project. Provisional trim and typography.')
    frames = json.loads((ROOT / 'data/baseline_v08_native_frames.json').read_text())
    for n in [161, 162]:
        s.gotoPage(n)
        assert tuple(s.getPageNSize(n)) == (396., 691.)
        assert len(s.getPageItems()) == 0, 'Closing surface must remain unprinted'
    before = [f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name']) != 1]
    assert not before, before
    path = ROOT / R['sla']
    s.saveDocAs(str(path))
    s.closeDoc()
    s.openDoc(str(path))
    after = [f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name']) != 1 or s.getAllText(f['name']) != f['text']]
    assert not after, after
    s.saveDocAs(str(path))
    pdf = s.PDFfile()
    pdf.file = str(ROOT / R['pdf'])
    pdf.pages = list(range(1, 163))
    pdf.version = 15
    pdf.compress = True
    pdf.compressmtd = 2
    pdf.quality = 0
    pdf.downsample = 0
    pdf.resolution = 600
    pdf.outdst = 0
    pdf.bookmarks = True
    pdf.save()
    del pdf
    report = dict(scribus_version=s.scribus_version, pages=s.pageCount(),
                  editable_text_frames=len(frames), new_text_frames=0, new_fraction_rules=0,
                  overflow_before=before, overflow_after=after,
                  frames_below_85_percent=[f for f in frames if f['scale'] < 85],
                  closing_pages_blank=[161, 162], excluded_scanner_sources=[163, 164, 165, 166, 167])
    (ROOT / 'data/native_validation.json').write_text(json.dumps(report, indent=2))
    s.closeDoc()
    (ROOT / 'data/build_success.json').write_text(json.dumps(R, indent=2))

try:
    main()
except BaseException:
    (ROOT / 'build_error.txt').write_text(traceback.format_exc())
    raise
finally:
    if os.environ.get('LIBERTY_BATCH') == '1':
        os._exit(0)
