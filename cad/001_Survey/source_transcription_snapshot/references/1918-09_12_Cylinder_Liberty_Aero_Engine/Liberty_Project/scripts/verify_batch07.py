"""Final rendering, baseline preservation and source-pixel verification."""
from pathlib import Path
import json,hashlib,subprocess,io
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageDraw
from lxml import etree
import numpy as np
import fitz
R=Path(__file__).resolve().parents[1];Q=R.parent/'qa/batch07';Q.mkdir(exist_ok=True)
release=json.loads((R/'data/release.json').read_text());old=json.loads((R/'data/baseline_v06_release.json').read_text())
pdf=R/release['pdf'];doc=fitz.open(pdf);baseline=fitz.open(R/old['pdf'])
# Exact same rasterizer, resolution and colorspace for both final PDFs.
preservation=[]
for n in range(120):
 a=baseline[n].get_pixmap(matrix=fitz.Matrix(2,2));b=doc[n].get_pixmap(matrix=fitz.Matrix(2,2))
 preservation.append(dict(page=n+1,render_dpi=144,pixels_identical=a.samples==b.samples,sha256=hashlib.sha256(b.samples).hexdigest()))
assert all(p['pixels_identical'] for p in preservation)
oldmanifest=json.loads((R/'data/baseline_v06_release_manifest.json').read_text())['files'];protected=[]
for f in oldmanifest:
 name=f['path']
 if name.startswith(('assets/','fonts/','sources/')) or name in [old['sla'],old['pdf'],old['comparison']]:
  ok=hashlib.sha256((R/name).read_bytes()).hexdigest()==f['sha256'];protected.append(dict(path=name,unchanged=ok));assert ok,name
# Native earlier objects and styles are compared structurally.
a=etree.parse(str(R/old['sla']));b=etree.parse(str(R/release['sla']))
oldobjects=a.findall('.//PAGEOBJECT');newobjects=b.findall('.//PAGEOBJECT');matches=[]
for i,x in enumerate(oldobjects):
 # Scribus assigns fresh ItemID values on native save; compare all content/geometry attributes.
 x.attrib.pop('ItemID',None);newobjects[i].attrib.pop('ItemID',None)
 same=etree.tostring(x,method='c14n')==etree.tostring(newobjects[i],method='c14n');matches.append(same)
oldstyles=a.findall('.//STYLE')+a.findall('.//CHARSTYLE');newstyles=b.findall('.//STYLE')+b.findall('.//CHARSTYLE')
ns={(e.get('NAME') or e.get('CNAME')):etree.tostring(e,method='c14n') for e in newstyles};styles=[dict(name=(e.get('NAME') or e.get('CNAME')),unchanged=etree.tostring(e,method='c14n')==ns.get((e.get('NAME') or e.get('CNAME')))) for e in oldstyles]
report=dict(pdf_pages=preservation,protected_files=protected,ignored_volatile_native_attribute='ItemID',native_objects_compared=len(matches),native_objects_identical=sum(matches),native_styles=styles)
(R/'data/baseline_v06_preservation.json').write_text(json.dumps(report,indent=2))
assert all(matches) and all(v['unchanged'] for v in styles),'Native baseline changed'
# Source inventory and lossless original crops.
inv=json.loads((R/'data/source_inventory.json').read_text())['sources'];sources=[]
for f in inv:
 if f['leaf']>140:continue
 p=R/'sources'/f['filename'];ok=hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'];sources.append(dict(leaf=f['leaf'],hash_matches=ok));assert ok
art=[]
for a in json.loads((R/'data/artwork.json').read_text()):
 p=R/'assets'/a['asset'];im=Image.open(p);im.load();original=Image.open(R/'assets'/(Path(a['asset']).stem+'_original.png'));original.load()
 src=Image.open(R/'sources'/f'liberty12cylinde00grea_{a["leaf"]:04}.jp2').convert('RGB').crop(a['crop'])
 assert original.tobytes()==src.tobytes();assert list(im.size)==a['pixels'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
 record=dict(figure=a['figure'],fully_decoded=True,original_pixel_match=True,cleaned_sha256=a['sha256'],pixels=list(im.size),mode=im.mode)
 if a['kind']=='color':
  arr=np.asarray(im,dtype=np.int16);red=(arr[:,:,0]>arr[:,:,1]+30)&(arr[:,:,0]>arr[:,:,2]+30);record['red_pixels']=int(red.sum());assert red.sum()>200
 art.append(record)
(R/'data/artwork_validation.json').write_text(json.dumps(dict(sources=sources,artwork=art),indent=2))
# Detect all illustration bounds, including raster labels.
bounds=[]
for n,p in enumerate(doc,1):
 for im in p.get_image_info():
  x0,y0,x1,y1=im['bbox']
  if min(x0,y0)<-.1 or x1>p.rect.width+.1 or y1>p.rect.height+.1:bounds.append(dict(page=n,bbox=im['bbox']))
assert not bounds,bounds
fonts=subprocess.run(['pdffonts',str(pdf)],capture_output=True,text=True,check=True).stdout
(R/'data/pdf_fonts.txt').write_text(fonts)
for line in fonts.splitlines()[2:]:assert 'yes' in line.split()[4:7],line
# Poppler outputs go through stdout and complete decoding to avoid partial writes.
def render(n):
 result=subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-r','120','-png',str(pdf)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
 im=Image.open(io.BytesIO(result.stdout));im.load();dest=Q/f'poppler_{n:02}.png';dest.write_bytes(result.stdout)
 return dict(page=n,dpi=120,pixels=list(im.size),sha256=hashlib.sha256(result.stdout).hexdigest())
with ThreadPoolExecutor(max_workers=4) as ex:renders=list(ex.map(render,range(121,141)))
(R/'data/render_validation.json').write_text(json.dumps(dict(pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),image_bounds_errors=bounds,poppler=renders),indent=2))
for k in range(5):
 sheet=Image.new('RGB',(1600,750),'#e9e9e9');draw=ImageDraw.Draw(sheet)
 for j,n in enumerate(range(121+k*4,125+k*4)):
  im=Image.open(Q/f'poppler_{n:02}.png').convert('RGB');im.thumbnail((390,700));x=j*400+5;sheet.paste(im,(x,28));draw.text((x,9),f'Scan {n:04}',fill='black')
 out=io.BytesIO();sheet.save(out,format='PNG');(Q/f'final_sheet_{k+1}.png').write_bytes(out.getvalue())
print(json.dumps(dict(pages=len(doc),baseline_pixels_identical=True,native_objects=len(matches),native_styles=len(styles),protected_files=len(protected),source_hashes=len(sources),original_crop_matches=len(art),color_figures=sum(a['mode']=='RGB' for a in art),poppler_pages=len(renders))))
