#!/usr/bin/env python3
"""Pilot comparisons, every-plate review, and a clean master gallery.

PDF placements preserve vector paths where the review recommends SVG. Raster
comparisons use the full PNG data, without JPEG recompression or upsampling.
"""
from pathlib import Path
import io,json,textwrap
import fitz
from PIL import Image
from reportlab import rl_config
rl_config.useA85=False  # Use direct lossless Flate streams.
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import proof_fonts

ROOT=Path(__file__).resolve().parent;R=ROOT/'restoration'
M=json.loads((R/'manifest.json').read_text());W,H=1000,720
overlays=[];bookmarks=[];count=0;buf=io.BytesIO()
c=canvas.Canvas(buf,pagesize=(W,H),initialFontName='ProofSans')
c.setTitle('SNL G-13 — figure restoration comparisons and all-plate review')

def text(x,y,s,size=11,bold=False,color='#243440'):
    c.setFillColor(color);c.setFont('ProofSans-Bold' if bold else 'ProofSans',size);c.drawString(x,y,s)
def para(s,x,y,width=143,size=10):
    for line in textwrap.wrap(s,width):text(x,y,line,size);y-=size+4
    return y
def head(title,sub):
    bookmarks.append([1,title,count+1]);text(28,683,title,20,True);para(sub,28,659,146,10)
def foot():
    global count
    text(28,20,'SNL G-13 | Source-derived restoration | Geometry and plate order retained',9,color='#62717a')
    text(950,20,str(count+1),9);c.showPage();count+=1
def raster(path,box,crop=None):
    im=Image.open(path)  # Preserve grayscale PDF storage without expanding to RGB.
    if crop:im=im.crop(crop)
    x,y,w,h=box;scale=min(w/im.width,h/im.height);ww,hh=im.width*scale,im.height*scale
    c.drawImage(ImageReader(im),x+(w-ww)/2,y+(h-hh)/2,ww,hh)
def vector(n,box,crop=None):
    x,y,w,h=box
    overlays.append((count,n,fitz.Rect(x,H-y-h,x+w,H-y),crop))
def preferred(n,box):
    if M[n]['preferred']!='raster':vector(n,box)
    else:raster(ROOT/M[n]['clean'],box)

head('Cleaner figures, with vectors where they help','31 artwork assets cover all 34 plates. Five recommended vector masters, two hybrid masters, and 24 grayscale raster masters.')
para('The pilot compared a hatched engineering section (Plate 29), shaded parts (Plate 16), and a photograph with a wiring diagram (Plates 10–11). Their successful treatments were extended to the complete figure set.',28,621,146,11)
text(28,566,'Paper color removed; subtle drawing information treated separately',13,True)
for x,title,path in [(28,'Previously corrected source',ROOT/'assets/p301-geometry.png'),(516,'Cleaned figure — Plate 29',R/'clean/p301-clean.png')]:
    text(x,536,title,11,True);raster(path,(x,283,456,235))
para('Line drawings use local paper normalization. Protected shaded regions retain continuous gray tones. Selected SVGs use eight gray levels of traced outlines, which avoid the heavy hatching produced by a single binary trace.',28,253,145,11)
para('The SVGs preserve photographed lettering as paths; they are not semantic CAD drawings or editable type. Hybrid SVGs explicitly contain raster image regions. The clean PNG masters remain at the rectified input pixel dimensions.',28,187,145,11)
para('Review limits: faint show-through remains near weak original lines. Plate 12 now uses the approved aggressive background mask; it and Plate 2 remain raster. No generative fill or invented engineering detail was used.',28,122,145,11)
text(28,60,'Pages 2–7: pilot comparisons and details. Pages 8–38: every artwork asset in reading order.',11,True)
foot()

for n,title in [('301','Plate 29 | section and hatching'),('288','Plate 16 | shaded parts'),('283','Plates 10–11 | photograph and wiring')]:
    head(title,'Compare the rectified source, cleaned grayscale pixels, and the source-derived SVG. SVG panels retain their vector content in this PDF.')
    for x,lab in [(28,'Rectified source'),(352,'Clean grayscale'),(676,'Layered vector' if n=='301' else 'Hybrid SVG')]:text(x,623,lab,12,True)
    raster(ROOT/'assets'/f'p{n}-geometry.png',(28,100,296,504))
    raster(R/'clean'/f'p{n}-clean.png',(352,100,296,504))
    vector(n,(676,100,296,504))
    para(M[n]['note'],28,80,148,10);foot()

for n,crop,title,notes in [
 ('301',(12,282,550,660),'Plate 29 | enlarged hatch and label check','The 8 at the left canvas edge, fine diagonal hatch lines, dashed internal lines and leader ends were inspected. Gray vector layers retain differences in ink weight.'),
 ('288',(432,474,928,960),'Plate 16 | enlarged shading and lettering','The shaded components stay raster. Their arrows and original part-number lettering are traced as outlines; tiny metal edges are not redrawn from inference.'),
 ('283',(489,1190,944,1660),'Plate 11 | enlarged crossings and connections','Component stippling and shading stay raster; clear wiring and surrounding lettering use vector outlines. These are illustration paths, not a newly inferred electrical schematic.')]:
    head(title,'Same source-coordinate crop in all three panels. Enlargement exposes sampling limits; it does not recover missing original detail.')
    for x,lab in [(28,'Rectified source'),(352,'Clean grayscale'),(676,'Layered vector' if n=='301' else 'Hybrid SVG')]:text(x,623,lab,12,True)
    raster(ROOT/'assets'/f'p{n}-geometry.png',(28,122,296,477),crop)
    raster(R/'clean'/f'p{n}-clean.png',(352,122,296,477),crop)
    vector(n,(676,122,296,477),crop)
    para(notes,28,94,146,11);foot()

for n,r in M.items():
    plates=', '.join(map(str,r['plates']));head(f"Folio {n.replace('_foldout',' foldout')} | Plate{'s' if len(r['plates'])>1 else ''} {plates}",r['note'])
    text(28,610,'Previously corrected source',12,True)
    text(516,610,'Restored master — '+r['preferred'],12,True)
    raster(ROOT/r['source'],(28,85,456,506));preferred(n,(516,85,456,506))
    text(28,59,f"Canvas: {r['pixel_size'][0]} × {r['pixel_size'][1]} source pixels. No new geometric transformation.",10)
    if n in ['284','277_foldout']:text(516,59,'Vector trial retained separately; raster preferred.',10)
    foot()

c.save();d=fitz.open(stream=buf.getvalue(),filetype='pdf');cache={}
for page,n,box,crop in overlays:
    if n not in cache:cache[n]=fitz.open(R/'vector'/f'p{n}-restored.pdf')
    clip=fitz.Rect(*(v*.75 for v in crop)) if crop else None
    d[page].show_pdf_page(box,cache[n],0,clip=clip)
d.set_toc(bookmarks)
(ROOT/'Figure_Restoration_Comparisons.pdf').write_bytes(d.tobytes(garbage=4,deflate=True))
assert len(d)==38
for i,p in enumerate(d):
    for b in p.get_text('blocks'):assert 0<=b[0]<=b[2]<=W and 0<=b[1]<=b[3]<=H,(i,b)
    p.get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(R/'review'/f'comparison-{i+1:02}.png')
print('Comparison PDF:',len(d),'pages; all rendered and text bounds checked.',flush=True)

# Master gallery has no proof headings; only the historical image content.
gallery=fitz.open();toc=[]
for n,r in M.items():
    src=R/('vector' if r['preferred']!='raster' else 'clean')/f"p{n}-{'restored' if r['preferred']!='raster' else 'clean'}.pdf"
    master=fitz.open(src);gallery.insert_pdf(master)
    toc.append([1,'Plate '+', '.join(map(str,r['plates']))+' — folio '+n,len(gallery)])
gallery.set_toc(toc);gallery.set_metadata({'title':'SNL G-13 — restored figure masters','author':'Ordnance Department; digital restoration'})
(ROOT/'Restored_Figures.pdf').write_bytes(gallery.tobytes(garbage=4,deflate=True))
print('Master gallery:',len(gallery),'pages / 34 plates.',flush=True)
