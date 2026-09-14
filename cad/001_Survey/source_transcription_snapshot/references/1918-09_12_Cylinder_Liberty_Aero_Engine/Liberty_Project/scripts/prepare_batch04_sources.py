"""OCR review material for pinned scans 0061–0080; leaves approved text alone."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageDraw
import json,subprocess,csv,io
ROOT=Path(__file__).resolve().parents[1];QA=ROOT.parent/'qa/batch04';QA.mkdir(parents=True,exist_ok=True)
def one(n):
 im=Image.open(ROOT/'sources'/f'liberty12cylinde00grea_{n:04}.jp2').convert('RGB');b=io.BytesIO();im.save(b,format='PNG');raw=b.getvalue();Image.open(io.BytesIO(raw)).load()
 (QA/f'{n:04}.png').write_bytes(raw)
 thumb=im.copy();thumb.thumbnail((1100,1900));b=io.BytesIO();thumb.save(b,format='JPEG',quality=94);(QA/f'{n:04}_view.jpg').write_bytes(b.getvalue())
 r=subprocess.run(['tesseract','stdin','stdout','--psm','3','tsv'],input=raw,capture_output=True,check=True)
 text=r.stdout.decode();(QA/f'{n:04}.tsv').write_text(text)
 groups={}
 for row in csv.DictReader(io.StringIO(text),delimiter='\t',quoting=csv.QUOTE_NONE):
  if row['level']=='5' and row['text'].strip():groups.setdefault((row['block_num'],row['par_num'],row['line_num']),[]).append(row)
 ls=[]
 for rs in groups.values():
  box=[min(int(r['left']) for r in rs),min(int(r['top']) for r in rs),max(int(r['left'])+int(r['width']) for r in rs),max(int(r['top'])+int(r['height']) for r in rs)]
  ls.append(dict(index=len(ls),box=box,text=' '.join(r['text'] for r in rs)))
 return dict(leaf=n,lines=ls)
with ThreadPoolExecutor(max_workers=4) as ex:pages=list(ex.map(one,range(61,81)))
(ROOT/'data/batch04_ocr_draft.json').write_text(json.dumps(pages,indent=2))
(QA/'lines.txt').write_text('\n\n'.join('SCAN '+str(p['leaf'])+'\n'+'\n'.join(f"{l['index']:02} {l['box']} {l['text']}" for l in p['lines']) for p in pages))
for k in range(5):
 c=Image.new('RGB',(1600,735),'#ddd');d=ImageDraw.Draw(c)
 for j in range(4):
  n=61+k*4+j;im=Image.open(QA/f'{n:04}_view.jpg');im.thumbnail((390,700));c.paste(im,(j*400+(400-im.width)//2,25));d.text((j*400+8,5),f'Scan {n:04} / printed {n-2}',fill='black')
 b=io.BytesIO();c.save(b,format='PNG');(QA/f'contact_{k+1}.png').write_bytes(b.getvalue())
print('20 sources prepared for review.')
