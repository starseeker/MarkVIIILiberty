from pathlib import Path
import fitz,json,re
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];QA=ROOT.parent/'qa';QA.mkdir(parents=True,exist_ok=True)
p=ROOT/'Hotchkiss_Master_v01.pdf';d=fitz.open(p)
# Stream recompression only: no page rasterization, downsampling, or geometry change.
d.set_toc([[1,r['label'],r['pdf_page']] for r in json.loads((ROOT/'data/page_inventory.json').read_text())])
target=p.with_suffix('.compressed.pdf');d.save(target,garbage=4,deflate=True,deflate_images=True,deflate_fonts=True);d.close();target.replace(p)
d=fitz.open(p);v=json.loads((ROOT/'data/native_validation.json').read_text());print('pages',len(d),'frames',v['editable_text_frames'],'rules',v['editable_rules'],'overflow',v['overflow_after']);print('scaling',v['horizontal_scaling']);ts=[]
for i,pg in enumerate(d):
 pix=pg.get_pixmap(matrix=fitz.Matrix(.5,.5));im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((270,340));t=Image.new('RGB',(290,370),'#ededed');t.paste(im,((290-im.width)//2,25));ImageDraw.Draw(t).text((8,5),f'Export page {i+1}',fill='black');ts.append(t)
 if i+1 in [1,4,8,9,12,13,17,19,20,21,22,24,27,29]:pg.get_pixmap(matrix=fitz.Matrix(2,2)).save(QA/f'proof_{i+1:02}.png')
 print(i+1,list(pg.rect),len(pg.get_text()),'images',len(pg.get_images()))
for start in range(0,len(ts),12):
 c=ts[start:start+12];out=Image.new('RGB',(1160,370*((len(c)+3)//4)),'white')
 for j,t in enumerate(c):out.paste(t,(j%4*290,j//4*370))
 out.save(QA/f'proof_contact_{start+1:02}.jpg')
(ROOT/'data/pdf_validation.json').write_text(json.dumps(dict(pages=len(d),page_sizes=[list(p.rect)[2:] for p in d],bytes=p.stat().st_size,text_characters=sum(len(p.get_text()) for p in d),text_pages=[i+1 for i,p in enumerate(d) if p.get_text().strip()],rendered_all_pages=True),indent=2))
