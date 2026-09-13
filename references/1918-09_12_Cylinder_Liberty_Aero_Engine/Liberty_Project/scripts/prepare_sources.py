"""Inventory staged JP2 sources and OCR the current 20-page batch for review."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,subprocess,csv,io,shutil
from PIL import Image
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parent
SRC=WORK/'MarkVIIILiberty/references/1918-09_12_Cylinder_Liberty_Aero_Engine/original_scans'
scan=etree.parse(str(WORK/'source_metadata/scandata.xml'))
meta={int(p.get('leafNum')):p for p in scan.findall('.//pageData/page')}
inventory=[]
for f in sorted(SRC.glob('*.jp2')):
 n=int(f.stem[-4:]);p=meta[n];im=Image.open(f)
 inventory.append(dict(leaf=n,filename=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size_bytes=f.stat().st_size,pixels=list(im.size),archive_type=p.findtext('pageType'),printed_folio=p.findtext('pageNumber'),archive_include=p.findtext('addToAccessFormats'),batch=1 if n<=20 else None))
(ROOT/'data/source_inventory.json').write_text(json.dumps(dict(repository='https://github.com/starseeker/MarkVIIILiberty',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=WORK/'MarkVIIILiberty',text=True).strip(),source_directory='references/1918-09_12_Cylinder_Liberty_Aero_Engine/original_scans',sources=inventory),indent=2))
def one(n):
 f=SRC/f'liberty12cylinde00grea_{n:04}.jp2';im=Image.open(f).convert('RGB');im.save(WORK/f'qa/pages/{n:04}.png')
 thumb=im.copy();thumb.thumbnail((1100,1900));thumb.save(WORK/f'qa/pages/{n:04}_view.jpg',quality=94)
 shutil.copy2(f,ROOT/'sources'/f.name)
 result=subprocess.run(['tesseract',str(WORK/f'qa/pages/{n:04}.png'),'stdout','--psm','3','tsv'],capture_output=True,text=True,check=True)
 (WORK/f'qa/ocr/{n:04}.tsv').write_text(result.stdout)
 rows=list(csv.DictReader(io.StringIO(result.stdout),delimiter='\t',quoting=csv.QUOTE_NONE));groups={}
 for r in rows:
  if r['level']=='5' and r['text'].strip():groups.setdefault((r['block_num'],r['par_num'],r['line_num']),[]).append(r)
 lines=[]
 for k,rs in groups.items():
  b=[min(int(r['left']) for r in rs),min(int(r['top']) for r in rs),max(int(r['left'])+int(r['width']) for r in rs),max(int(r['top'])+int(r['height']) for r in rs)]
  lines.append(dict(index=len(lines),text=' '.join(r['text'] for r in rs),box=b,confidence=round(sum(float(r['conf']) for r in rs)/len(rs),1)))
 return dict(leaf=n,lines=lines)
with ThreadPoolExecutor(max_workers=4) as ex:
 pages=list(ex.map(one,range(1,21)))
(ROOT/'data/ocr_draft.json').write_text(json.dumps(pages,indent=2))
(WORK/'qa/ocr/lines.txt').write_text('\n\n'.join('SCAN '+str(p['leaf'])+'\n'+'\n'.join(f"{l['index']:02} {l['box']} {l['text']}" for l in p['lines']) for p in pages))
print('Inventoried',len(inventory),'sources; OCR complete for',len(pages),'pages')
