"""Package the complete checkpoint with an internal file checksum manifest."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
release=json.loads((ROOT/'data/release.json').read_text())
baseline=json.loads((ROOT/'data/baseline_v08_release.json').read_text())
# Keep the current master and the exact immediate baseline master needed by verification.
# The new comparison proof is delivered separately to keep this archive manageable.
# Older rendered PDFs already exist in earlier releases and duplicate these pages.
# Every native SLA, source scan, artwork asset, font and provenance record is retained.
keep_pdfs={release['pdf'],baseline['pdf']}
omitted=[p for p in sorted(ROOT.glob('*.pdf')) if p.name not in keep_pdfs]
files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and p not in omitted and '__pycache__' not in p.parts and p.name not in ['release_manifest.json','build_error.txt'] and not p.name.endswith(('.autosave','.bak'))]
records=[dict(path=str(p.relative_to(ROOT)),size_bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
manifest=ROOT/'data/release_manifest.json';manifest.write_text(json.dumps(dict(release=release,files=records,omitted_obsolete_pdf_exports=[p.name for p in omitted if p.name!=release['comparison']],separately_delivered_pdf_exports=[release['comparison']],omission_reason='Older exports remain in earlier releases; the current comparison PDF is a separate download. All editable files, the current master PDF and the immediate baseline master PDF are included. Older comparison proofs remain in their released separate downloads.'),indent=2));files.append(manifest)
out=ROOT.parent/'deliverables';out.mkdir(exist_ok=True);zipname=out/release['package']
with zipfile.ZipFile(zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,'Liberty_Project/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(zipname) as z:
 error=z.testzip()
 if error:raise RuntimeError('ZIP validation failure: '+error)
print(json.dumps(dict(package=str(zipname),files=len(files),bytes=zipname.stat().st_size,sha256=hashlib.sha256(zipname.read_bytes()).hexdigest())))
