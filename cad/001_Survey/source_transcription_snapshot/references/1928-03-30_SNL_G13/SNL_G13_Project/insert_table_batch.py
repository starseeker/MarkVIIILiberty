"""Run inside Scribus to insert a new consecutive batch into the saved master.

Set SNL_FIRST and SNL_LAST to the printed folios, and update project_sequence.py
and build_project.py first. Refuses a duplicate or out-of-date insertion.
The ordinary build_project.py remains the complete, independent rebuild route.
"""
import os,json,traceback,tempfile
from pathlib import Path
import scribus as s
import build_project as b
ROOT=Path(__file__).resolve().parent

def main():
 first=int(os.environ['SNL_FIRST']);last=int(os.environ['SNL_LAST'])
 numbers=list(range(first,last+1));names={str(n) for n in numbers}
 prior_labels=[label for label in b.LABELS if label not in names]
 assert all(n in b.TABLES for n in numbers)
 prior=json.loads((ROOT/'validation.json').read_text())
 assert not any(r['frame'].startswith(tuple(f'p{n}-' for n in numbers)) for r in prior)
 (ROOT/'build-status.txt').unlink(missing_ok=True)
 (ROOT/'build-error.txt').unlink(missing_ok=True)
 s.openDoc(str(ROOT/'SNL_G13_Pilot.sla'))
 assert s.pageCount()==len(prior_labels)
 s.setRedraw(False)
 for n in numbers:
  position=b.LABELS.index(str(n))+1
  s.newPage(position)
  s.gotoPage(position)
  assert not s.getPageItems()
  b.table(n)
  print(f'Inserted printed page {n} at document page {position}',flush=True)
 assert s.pageCount()==len(b.LABELS)
 expected=[(r['frame'],r['expected_lines']) for r in prior]+b.f.frames
 assert len({name for name,_ in expected})==len(expected)
 validation=[]
 for i,(name,count) in enumerate(expected,1):
  if i%5000==0:print(f'Checking text frame {i} of {len(expected)}',flush=True)
  s.layoutText(name)
  validation.append(dict(frame=name,overflow=bool(s.textOverflows(name)),expected_lines=count,actual_lines=s.getTextLines(name)))
 errors=[r for r in validation if r['overflow'] or r['expected_lines']!=r['actual_lines']]
 (ROOT/'validation.json').write_text(json.dumps(validation,indent=2))
 s.setInfo('Ordnance Department; digital reconstruction',
  'S. N. L. No. G-13 — supplied-page pilot',
  f'{len(b.LABELS)} supplied pages/leaves ordered by original folio, including Plate 2 foldout. Main pages 6 x 9 inches; provisional foldout 18 x 9. See page_inventory.json and calibration records.')
 s.gotoPage(1)
 s.saveDocAs(str(ROOT/'SNL_G13_Pilot.sla'))
 print('Saved native document; exporting complete PDF',flush=True)
 with tempfile.TemporaryDirectory(prefix='snl-g13-export-') as temp:
  target=Path(temp)/'pilot.pdf'
  pdf=s.PDFfile();pdf.file=str(target);pdf.pages=list(range(1,s.pageCount()+1))
  pdf.version=15;pdf.fonts=[];pdf.subsetList=[b.f.ROMAN,b.f.BOLD,b.f.ITALIC]
  pdf.compress=1;pdf.quality=0;pdf.resolution=300;pdf.save()
  data=target.read_bytes()
  assert data.rstrip().endswith(b'%%EOF'),'Incomplete PDF export'
  (ROOT/'SNL_G13_Pilot.pdf').write_bytes(data)
  (ROOT/'pdf-export-status.txt').write_text(f'PASS: complete PDF exported, {len(data)} bytes.\n')
 if errors:raise RuntimeError('Text layout errors: '+repr(errors))
 (ROOT/'build-status.txt').write_text(f'PASS: {s.pageCount()} pages; {len(validation)} native text frames; no overflow; expected line counts.\n')

if __name__=='__main__':
 try:main()
 except Exception:(ROOT/'build-error.txt').write_text(traceback.format_exc())
 finally:
  if os.environ.get('SNL_BATCH')=='1':os._exit(0)
