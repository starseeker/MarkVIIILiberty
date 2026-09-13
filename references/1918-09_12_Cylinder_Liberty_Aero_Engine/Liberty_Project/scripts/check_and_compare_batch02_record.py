"""Validate native exports, add PDF folio labels/bookmarks, and build comparison.
Uses PyMuPDF and Pillow; the exported manual pages remain Scribus-produced.
"""
from pathlib import Path
import json,hashlib,io,re,unicodedata
from collections import Counter
import fitz
from PIL import Image
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
R=json.loads((ROOT/'data/release.json').read_text());pdfpath=ROOT/R['pdf']
src=fitz.open(pdfpath)
labels=[dict(startpage=0,prefix='Cover',style=''),dict(startpage=1,prefix='Inside cover',style=''),dict(startpage=2,prefix='Title',style=''),dict(startpage=3,prefix='Frontispiece',style=''),dict(startpage=4,prefix='',style='D',firstpagenum=3)]
src.set_page_labels(labels)
src.set_toc([[1,'Cover',1],[1,'Title',3],[1,'The Liberty Engine — frontispiece',4],[1,'Table of contents',5],[1,'Introductory note — p5',7],[1,'Index of illustrations — pp6–8',8],[1,'Leading particulars — pp8–10',10],[1,'General description — p11',13],[2,'Cylinders — p12',14],[2,'Pistons — p13',15],[2,'Connecting rods — p15',17],[2,'Crankshaft — p17',19],[2,'Base chamber — p18',20],[2,'Valves — p23',25],[2,'Camshafts and valve gear — p25',27],[2,'Distribution gear — p26',28],[2,'Cooling system — p28',30],[2,'Starter — p30',32],[1,'Lubrication — p31',33],[2,'Oil pumps — p31',33],[2,'Main and big end bearings — p36',38],[2,'Gudgeon pins — p37',39],[2,'Camshaft lubrication — p37',39]])
tmp=ROOT/'_labelled.pdf';src.save(tmp,garbage=4,deflate=True);src.close();tmp.replace(pdfpath);src=fitz.open(pdfpath)
assert len(src)==40
frames=json.loads((ROOT/'data/native_frames.json').read_text());by={n:[] for n in range(1,41)}
for f in frames:by[f['page']].append(f)
def norm(t):return re.sub(r'\s+','',unicodedata.normalize('NFKC',t))
mismatches=[];bounds=[]
for n,page in enumerate(src,1):
 expected=Counter(norm(''.join(f['text'] for f in by[n])));actual=Counter(norm(page.get_text()))
 if expected!=actual:mismatches.append(dict(page=n,missing=dict(expected-actual),extra=dict(actual-expected)))
 for b in page.get_text('dict')['blocks']:
  if b['type']==0:
   for l in b['lines']:
    for s in l['spans']:
     x0,y0,x1,y1=s['bbox']
     if x0<-.1 or y0<-.1 or x1>page.rect.width+.1 or y1>page.rect.height+.1:bounds.append(dict(page=n,text=s['text'],bbox=s['bbox']))
tree=etree.parse(str(ROOT/R['sla']));links=[]
for x in tree.findall('.//PAGEOBJECT'):
 if x.get('PFILE'):
  path=Path(x.get('PFILE'));path=path if path.is_absolute() else ROOT/path
  links.append(dict(path=x.get('PFILE'),exists=path.is_file(),relative=not Path(x.get('PFILE')).is_absolute()))
report=dict(pages=len(src),pdf_sha256=hashlib.sha256(pdfpath.read_bytes()).hexdigest(),text_character_mismatches=mismatches,text_outside_pages=bounds,image_links=links,page_labels=src.get_page_labels(),page_dimensions_points=[list(p.rect)[2:] for p in src])
(ROOT/'data/pdf_validation.json').write_text(json.dumps(report,indent=2))
if mismatches or bounds or any(not x['exists'] for x in links):raise RuntimeError('PDF validation failed; inspect data/pdf_validation.json')
# A 20-sheet proof, source on left and the native reconstruction on right.
out=fitz.open();mapping=[]
for i in range(20,40):
 p=src[i]
 sheet=out.new_page(width=880,height=759)
 label=['Cover','Inside cover (blank)','Title','Frontispiece'][i] if i<4 else 'Printed page '+str(i-1)
 sheet.insert_text((26,25),f'LIBERTY ENGINE HANDBOOK | {R["release_id"]} | scan {i+1:04} | {label}',fontsize=9,fontname='helv')
 sheet.insert_text((26,46),'SOURCE SCAN',fontsize=8,fontname='hebo');sheet.insert_text((457,46),'SCRIBUS RECONSTRUCTION',fontsize=8,fontname='hebo')
 im=Image.open(ROOT/'sources'/f'liberty12cylinde00grea_{i+1:04}.jp2').convert('RGB');im.thumbnail((1450,2500));b=io.BytesIO();im.save(b,format='JPEG',quality=92)
 sheet.insert_image(fitz.Rect(26,57,422,748),stream=b.getvalue(),keep_proportion=True)
 sheet.show_pdf_page(fitz.Rect(457,57,853,748),src,i)
 mapping.append(dict(comparison_page=i-19,source_leaf=i+1,master_page=i+1,label=label))
out.save(ROOT/R['comparison'],garbage=4,deflate=True);out.close()
(ROOT/'data/comparison_map.json').write_text(json.dumps(mapping,indent=2))
review=ROOT.parent/'qa';review.mkdir(exist_ok=True)
for n in range(21,41):
 pix=src[n-1].get_pixmap(matrix=fitz.Matrix(2,2));b=pix.tobytes('png');Image.open(io.BytesIO(b)).load();(review/'batch02'/f'final_{n:02}.png').write_bytes(b)
print('40 pages verified; exact per-page native/PDF character inventory matches; no text outside pages. Comparison written.')
