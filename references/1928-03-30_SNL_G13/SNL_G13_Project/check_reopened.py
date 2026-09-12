"""Run inside Scribus to verify the saved native document."""
import os,json,traceback
from pathlib import Path
import scribus as s
from project_sequence import LABELS
ROOT=Path(__file__).resolve().parent
try:
 (ROOT/'reopen-error.txt').unlink(missing_ok=True)
 s.openDoc(str(ROOT/'SNL_G13_Pilot.sla'))
 rows=[]
 for row in json.loads((ROOT/'validation.json').read_text()):
  name=row['frame'];s.layoutText(name)
  rows.append(dict(frame=name,overflow=bool(s.textOverflows(name)),
   lines=s.getTextLines(name),expected_lines=row['expected_lines']))
 result=dict(page_count=s.pageCount(),frames=rows)
 (ROOT/'reopen-validation.json').write_text(json.dumps(result,indent=2))
 assert s.pageCount()==len(LABELS)
 assert not any(r['overflow'] or r['lines']!=r['expected_lines'] for r in rows)
except Exception:
 (ROOT/'reopen-error.txt').write_text(traceback.format_exc())
finally:
 if os.environ.get('SNL_BATCH')=='1':os._exit(0)
