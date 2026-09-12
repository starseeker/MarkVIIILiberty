#!/usr/bin/env python3
"""Run inside Scribus; patch three named cells, preserve styles, check and export.

The data modules and audit/ambiguity_audit.json are the source of decisions.
This is idempotent and does not rebuild pages or change artwork.
"""
from pathlib import Path
import json,os,re,traceback
import scribus as s
ROOT=Path(__file__).resolve().parent
try:
 error=ROOT/'audit/context_native_error.txt';error.unlink(missing_ok=True)
 loaded={f[0]:Path(f[-1]) for f in s.getXFontNames()}
 for face,filename in [('C059 Roman','C059-Roman.otf'),('C059 Bold','C059-Bold.otf'),('C059 Italic','C059-Italic.otf')]:
  assert face in loaded and loaded[face].read_bytes()==(ROOT/'fonts'/filename).read_bytes(), 'Select the bundled OpenType font for '+face+' before exporting; a same-name Type 1 font has different metrics.'
 changes=[f['change'] for f in json.loads((ROOT/'audit/ambiguity_audit.json').read_text())['findings'] if f['change']]
 path=ROOT/'SNL_G13_Pilot.sla'; text=path.read_text()
 for c in changes:
  pattern=r'<PAGEOBJECT\b[^>]*\bANNAME="'+re.escape(c['frame'])+r'"[\s\S]*?</PAGEOBJECT>'
  hits=list(re.finditer(pattern,text));assert len(hits)==1,c
  a,b=hits[0].span();block=hits[0].group()
  if c['old'] in block:
   assert block.count(c['old'])==1,c
   block=block.replace(c['old'],c['new'])
   text=text[:a]+block+text[b:]
  else:assert c['new'] in block,c
 path.write_text(text)
 print('Opening native document',flush=True)
 s.openDoc(str(path)); s.setRedraw(False)
 assert s.pageCount()==314
 validation=[]
 oldvalidation=json.loads((ROOT/'validation.json').read_text())
 for i,r in enumerate(oldvalidation):
  if i%5000==0:print('Checking frame',i,'of',len(oldvalidation),flush=True)
  name=r['frame'];s.layoutText(name)
  validation.append(dict(frame=name,overflow=bool(s.textOverflows(name)),
   expected_lines=r['expected_lines'],actual_lines=s.getTextLines(name),characters=s.getTextLength(name)))
 errors=[r for r in validation if r['overflow'] or r['expected_lines']!=r['actual_lines']]
 (ROOT/'audit/context_layout_errors.json').write_text(json.dumps(errors,indent=2))
 assert not errors,repr(errors[:10])
 for c in changes:
  assert c['new'] in s.getAllText(c['frame']),c
 # The three edits were saved before reopening. Keep that serialization so
 # Scribus does not rewrite unrelated IDs or floating-point image scales.
 s.gotoPage(1)
 print('Verified native document; exporting PDF',flush=True)
 (ROOT/'validation.json').write_text(json.dumps(validation,indent=2))
 pdf=s.PDFfile();pdf.file=str(ROOT/'SNL_G13_Pilot.pdf');pdf.pages=list(range(1,315))
 pdf.version=15;pdf.fonts=[];pdf.subsetList=['C059 Roman','C059 Bold','C059 Italic']
 pdf.compress=1;pdf.quality=0;pdf.resolution=300;pdf.save()
 (ROOT/'audit/context_native_validation.json').write_text(json.dumps(dict(
  page_count=s.pageCount(),text_frames=len(validation),overflow_count=0,line_count_errors=0,
  corrected_frames=[c['frame'] for c in changes],exported=True),indent=2))
except Exception:
 (ROOT/'audit/context_native_error.txt').write_text(traceback.format_exc())
finally:
 if os.environ.get('SNL_BATCH')=='1':os._exit(0)
