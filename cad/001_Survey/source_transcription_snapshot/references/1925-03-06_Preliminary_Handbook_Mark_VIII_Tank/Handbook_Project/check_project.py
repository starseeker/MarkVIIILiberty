"""Execute inside Scribus to reopen and validate this checkpoint."""
import scribus as s,json,os,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
try:
 s.openDoc(str(ROOT/'Handbook_Master.sla'))
 expected=json.loads((ROOT/'data/native_validation.json').read_text())['frames']
 errors=[]
 for row in expected:
  n=row['name'];s.layoutText(n)
  if s.textOverflows(n) or s.getTextLines(n)!=1:errors.append({'frame':n,'problem':'layout'})
  if s.getAllText(n)!=row['text']:errors.append({'frame':n,'problem':'text mismatch'})
 fontrows=[r for r in s.getXFontNames() if r[0].startswith('C059')]
 result={'pages':s.pageCount(),'checked_text_frames':len(expected),'errors':errors,'font_records':fontrows}
 (ROOT/'data/reopen_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 if errors:raise RuntimeError('Saved master failed validation')
 def export_pdf():
  s.gotoPage(1);s.setRedraw(False)
  pdf=s.PDFfile();pdf.file=str(ROOT/'Handbook_Master_001-251_v13.pdf');pdf.pages=list(range(1,252));pdf.version=15
  pdf.fonts=[];pdf.subsetList=['C059 Roman','C059 Bold','C059 Italic'];pdf.compress=1;pdf.quality=0;pdf.resolution=300;pdf.downsample=0
  pdf.save()
 export_pdf()
 if not (ROOT/'Handbook_Master_001-251_v13.pdf').read_bytes().rstrip().endswith(b'%%EOF'):raise RuntimeError('PDF export incomplete')
 s.setRedraw(True)

 print(result,flush=True)
except Exception:
 (ROOT/'check-error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
finally:
 if os.environ.get('HANDBOOK_BATCH')=='1':os._exit(0)
