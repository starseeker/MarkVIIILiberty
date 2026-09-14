"""Produce the revision comparison, measured book trend, and complete plate audit."""
from pathlib import Path
import io,json,textwrap
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
import proof_fonts
from reportlab.lib.utils import ImageReader
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import fitz
P=Path(__file__).resolve().parent;C=P/'calibration'
audit=json.loads((C/'plate_review.json').read_text());models=json.loads((C/'text_model_validation.json').read_text());old=json.loads((C/'previous_geometry_validation.json').read_text())
W,H=1000,720
c=canvas.Canvas(str(P/'Figure_Refinement_Study.pdf'),pagesize=(W,H),initialFontName='ProofSans');c.setTitle('SNL G-13 — lettering and book-curvature refinement, all-plate review');page=0

def text(x,y,s,size=11,bold=False,color='#172938'):
 c.setFillColor(color);c.setFont('ProofSans-Bold' if bold else 'ProofSans',size);c.drawString(x,y,s)
def para(s,x,y,width=134,size=11):
 for line in textwrap.wrap(s,width):text(x,y,line,size);y-=size+4
 return y

def heading(title,sub):
 text(30,680,title,21,True);para(sub,30,658,148,10)
def finish():
 global page
 page+=1;text(30,20,'SNL G-13 | Geometry refinement | Original image pixels; no reconstructed linework',9,color='#536370');text(957,20,str(page),9);c.showPage()
def picture(im,box):
 if not isinstance(im,Image.Image):im=Image.open(im).convert('RGB')
 x,y,w,h=box;im.thumbnail((2200,2200));scale=min(w/im.width,h/im.height);ww,hh=im.width*scale,im.height*scale
 b=io.BytesIO();im.save(b,format='JPEG',quality=95,subsampling=0);b.seek(0)
 c.drawImage(ImageReader(b),x+(w-ww)/2,y+(h-hh)/2,width=ww,height=hh)
def pair(n,y=111,h=497,detail=False):
 for x,sub,file in [(30,'Previous delivered correction',C/f'p{n}-before-text-refinement.png'),(515,'Refined correction',P/f'assets/p{n}-geometry.png')]:
  text(x,627,sub,12,True);im=Image.open(file).convert('RGB')
  if detail:im=im.crop((0,int(im.height*.42),im.width,im.height))
  picture(im,(x,y,455,h))

def metrics(n,y=85):
 r=models[str(n)];v=old[str(n)]['heldout_rms_pixels'];text(30,y,f"Reserved observations: {r['heldout_count']} groups | Previous RMS {v:.2f} px | Refined RMS {r['heldout_corrected_rms_pixels']:.2f} px",12,True)
 para('RMS measures departure from the intended horizontal/vertical direction in source-pixel coordinates. These observations were excluded from fitting; they do not establish absolute dimensions.',30,y-20,151,10)

# Diagnostic derived from all accepted table models. It is not physical paper stretch.
rows=json.loads((C/'book_page_trends.json').read_text());fig,ax=plt.subplots(figsize=(12.8,3.1),dpi=150)
for parity,color,label in [(0,'#147a8a','Even folios'),(1,'#b35e2d','Odd folios')]:
 rr=[r for r in rows if r['model']['accepted'] and r['page']%2==parity];xs=np.array([r['page'] for r in rr]);ys=np.array([100*(r['model']['left_right_vertical_correction_ratio']-1) for r in rr]);ax.scatter(xs,ys,s=7,alpha=.36,color=color)
 med=[np.median(ys[abs(xs-x)<=12]) for x in xs];ax.plot(xs,med,color=color,label=label,lw=2)
ax.axhline(0,color='#888888',lw=.8);ax.set_xlim(1,277);ax.set_xlabel('Printed table folio');ax.set_ylabel('Left/right correction ratio\nminus 1 (%)');ax.grid(alpha=.18);ax.legend(frameon=False,ncol=2,loc='upper right');fig.tight_layout();fig.savefig(C/'book_curvature_trend.png');plt.close(fig)
heading('Lettering and book curvature improve six pages','All 30 numbered figure pages reviewed, covering 33 book-page plates. The flat-scanned Plate 2 foldout remains unchanged.')
para('Accepted refinements cover Plates 3-4, 10-11, 24, 27, 29 and 31. Letter baselines, selected reference lines and a restrained model of curvature are fitted together. The strongest gains are on Plates 10-11 and 29.',30,627,148,11)
text(30,565,'Reserved observations: comparison with the previous delivered corrections',12,True)
columns=[30,152,353,510,671,835]
for x,s in zip(columns,['Folio','Plate(s)','Groups','Previous RMS','Refined RMS','Assessment']):text(x,540,s,10,True)
for k,n in enumerate(models):
 r=models[n];pp=next(row['plates'] for row in audit['rows'] if row['page']==n);vals=[n,', '.join(map(str,pp)),str(r['heldout_count']),f"{old[n]['heldout_rms_pixels']:.2f} px",f"{r['heldout_corrected_rms_pixels']:.2f} px",'Modest' if n in ['278','296','299'] else 'Clear gain']
 for x,s in zip(columns,vals):text(x,519-k*21,s,11)
text(30,373,'The full book supports a changing parity pattern, not one fixed odd/even warp',12,True)
picture(C/'book_curvature_trend.png',(28,133,940,230))
para('275 table pages were surveyed automatically; 261 models passed the residual gate. Curvature trends differ by parity and change through the volume. Each accepted figure fit uses its own evidence; nearby same-parity pages provide only a weak guide where the model supports it.',30,112,151,10)
para('The plotted ratio is a diagnostic of the fitted correction field, not measured paper stretch. Original drawing dimensions and camera calibration remain unknown.',30,61,151,10)
finish()
heading('Plates 10 and 11 | printed page 283','Distributed lettering and selected photo/diagram reference lines constrain both directions. Both plates remain together on their original page.')
pair(283);metrics(283);finish()
heading('Plate 11 | enlarged wiring-diagram comparison','Bottom portion of the same page, enlarged to make the lettering and local change of tilt easier to inspect.')
pair(283,y=132,h=476,detail=True);para('The fit uses horizontal and vertical lettering across the diagram. Blue observations in the companion geometry proof were reserved for validation. Original wiring, labels and line quality remain raster pixels from the source.',30,105,147,11);finish()
heading('Plate 29 | printed page 301','The shaft and two end-plate references reveal different distortion through the page. A single affine correction could not align both ends.')
pair(301,y=131,h=477);metrics(301,102);finish()
heading('Plate 31 | printed page 303','Base edge, upright and headings constrain a smooth field. The caption and hub-edge checks were held out.')
pair(303);metrics(303);finish()
heading('Smaller accepted refinements','These changes have narrower supporting evidence. The comparison preserves the original viewpoint and avoids forcing circular parts to circles.')
for row,n in enumerate([278,296,299]):
 y=442-row*184;text(30,y+170,f"Printed page {n} | Plates {', '.join(map(str,next(r['plates'] for r in audit['rows'] if r['page']==str(n))))}",11,True)
 for x,title,path in [(30,'Previous',C/f'p{n}-before-text-refinement.png'),(510,'Refined',P/f'assets/p{n}-geometry.png')]:
  text(x,y+151,title,9);picture(path,(x,y,455,144))
finish()
for start,end in [(0,16),(16,31)]:
 heading('Plate-by-plate review'+(' | continued' if start else ''),'Every numbered figure page was inspected. Retained does not mean distortion-free: unresolved cases are recorded below.')
 text(30,622,'Folio / plates',10,True);text(166,622,'Decision and evidence',10,True)
 for k,row in enumerate(audit['rows'][start:end]):
  y=599-k*34;n=row['page'];label='Foldout / 2' if n=='277_foldout' else n+' / '+','.join(map(str,row['plates']))
  text(30,y,label,10,True)
  decision='REFINED' if row['decision']=='refined' else 'FLAT SCAN RETAINED' if n=='277_foldout' else 'RETAINED'
  text(166,y,decision,9,True,color='#147a8a' if decision=='REFINED' else '#536370')
  # Two lines use the full right-column width without touching the next row.
  para(row['reason'],277,y,115,8.5)
 finish()
c.save()
d=fitz.open(P/'Figure_Refinement_Study.pdf');assert len(d)==8
for i,p in enumerate(d):
 p.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(P/'proofs'/f'refinement-study-{i+1:02}.png')
 for b in p.get_text('blocks'):assert b[0]>=0 and b[1]>=0 and b[2]<=W and b[3]<=H,(i,b)
print('PASS:',len(d),'refinement study pages rendered; text bounds checked.')
