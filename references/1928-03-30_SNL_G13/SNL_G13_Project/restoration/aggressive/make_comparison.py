#!/usr/bin/env python3
"""Deliver the reviewed aggressive candidate and an explicit removal comparison."""
from pathlib import Path
import hashlib,io,json,textwrap,zipfile,tempfile
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import fitz
from reportlab import rl_config
rl_config.useA85=False
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from trial_cleanup import region_mask,save
P=Path(__file__).resolve().parent;cfg=json.loads((P/'config.json').read_text());a=np.asarray(Image.open(P/'Plate12_Current.png'))
# Refresh all explicitly protected text/detail regions after the removal review.
mask=P/'Plate12_KeepMask.png'
if not mask.exists():mask=P/'Plate12_Trial_25_KeepMask.png'
keep=np.asarray(Image.open(mask))>0
protected=region_mask(a.shape,cfg['text_rectangles'],cfg['detail_polygons']);keep |= protected
b=np.where(keep,a,255).astype(np.uint8);removed=(255-a)*(~keep)
save(Image.fromarray(b),P/'Plate12_Aggressive.png');save(Image.fromarray(np.uint8(keep)*255),P/'Plate12_KeepMask.png')
heat=np.stack([np.full(a.shape,255),255-removed,255-removed],axis=-1).astype(np.uint8);save(Image.fromarray(heat),P/'Plate12_RemovedMarks.png')
assert np.array_equal(b[keep],a[keep]);assert np.all(b[~keep]==255)
checks=[]
for label,box,kind in [('Upper blank field',[166,158,285,275],'background'),('Middle blank field',[181,478,276,578],'background'),('Dark mottling above left circle',[185,640,258,690],'background'),('Dark mottling above lower label',[149,827,251,850],'background'),('Shaft-lever wording',[510,288,787,325],'protected text'),('Lower dimension 14',[349,960,380,984],'protected text'),('STUD callout',[705,429,773,454],'protected text'),('Thin left circle',[121,700,198,780],'line plus background')]:
 x0,y0,x1,y1=box;aa=a[y0:y1,x0:x1];bb=b[y0:y1,x0:x1];ink=float((255-aa).sum());left=float((255-bb).sum())
 r={'region':label,'box':box,'kind':kind,'nonwhite_pixels_removed':int(((aa<255)&(bb==255)).sum()),'mean_ink_reduction_percent':100*(1-left/ink) if ink else 0,'identical_to_current':bool(np.array_equal(aa,bb))};checks.append(r)
 if kind=='protected text':assert r['identical_to_current']
result={'status':'PASS','source_sha256':hashlib.sha256((P/'Plate12_Current.png').read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((P/'Plate12_Aggressive.png').read_bytes()).hexdigest(),'pixel_size':list(Image.open(P/'Plate12_Current.png').size),'geometric_transform':False,'retained_pixels_unchanged':True,'changed_pixels_only_set_to_white':True,'protected_text_and_detail_pixels_unchanged':bool(np.array_equal(a[protected],b[protected])),'deleted_nonwhite_pixels':int(((a<255)&(~keep)).sum()),'total_mean_ink_reduction_percent':100*float(removed.sum())/float((255-a).sum()),'selected_regions':checks,'review':'Full candidate and removed-pixel map inspected; protected dimension 14, STUD lettering, left circular outline and context-line boundary after draft review. This is an editorial cleanup trial, not proof that every removed mark was unwanted.','book_master_replaced':False}
(P/'validation.json').write_text(json.dumps(result,indent=2))
W,H=1000,720;buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(W,H),initialFontName='Helvetica');c.setTitle('Plate 12 - aggressive cleanup comparison');n=0;toc=[]
def text(x,y,t,size=11,bold=False):c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.setFillColorRGB(.12,.18,.22);c.drawString(x,y,t)
def para(t,y,width=143,size=11):
 for line in textwrap.wrap(t,width):text(28,y,line,size);y-=size+4
 return y
def head(title,sub):
 toc.append([1,title,n+1]);text(28,681,title,20,True);para(sub,654,146,10)
def pic(file,box,crop=None):
 im=Image.open(P/file)
 if crop:im=im.crop(crop)
 x,y,w,h=box;s=min(w/im.width,h/im.height);ww,hh=im.width*s,im.height*s
 c.drawImage(ImageReader(im),x+(w-ww)/2,y+(h-hh)/2,ww,hh)
def end():
 global n
 n+=1;text(28,20,'SNL G-13 | Plate 12 | Aggressive editorial cleanup trial',9);text(950,20,str(n),9);c.showPage()
def pair(box1,box2,crop=None):
 pic('Plate12_Current.png',box1,crop);pic('Plate12_Aggressive.png',box2,crop)
head('What the more aggressive assumption changes','The current mirrored-reference master is at left. The candidate at right treats unassociated mottling as background noise.')
text(28,613,'Current conservative master',12,True);text(516,613,'Aggressive cleanup candidate',12,True)
pair((28,133,456,456),(516,133,456,456))
para('Open areas become much cleaner and the control-rod drawing is easier to separate visually from its background. Original text and sustained linework are protected. The kept pixels retain their existing grayscale values; nothing is retyped, sharpened or geometrically redrawn.',106,145,11);end()
head('Upper left - pale ghost and scattered marks','Identical enlarged crops. Blank regions are explicitly cleared while the body edge, rods, leaders and lettering retain source pixels.')
text(28,613,'Current',12,True);text(516,613,'Aggressive',12,True)
pair((28,132,456,454),(516,132,456,454),(40,111,509,403))
para('The background no longer competes with the fine drawing. This is a stronger editorial assumption than the preceding reverse-page model: isolated weak marks outside recognizable structures can disappear.',105,145,11);end()
head('Lower left - the conspicuous mottling','The larger mottled clusters between clear lines have been removed. Some remnants stay where they touch the circular outline, leaders or lettering.')
text(28,613,'Current',12,True);text(516,613,'Aggressive',12,True)
pair((28,130,456,456),(516,130,456,456),(82,620,316,903))
para('The first tight mask clipped part of the circular outline. The removal map exposed it, and the reviewed candidate protects that original curve. It does not replace the curve with an ideal circle.',105,145,11);end()
head('Lettering and thin-line checks','The current and candidate use the same grayscale source values in protected areas. Frame positions and the 1251 x 1054 pixel canvas are unchanged.')
text(28,613,'Current',12,True);text(516,613,'Aggressive',12,True)
pair((28,342,456,238),(516,342,456,238),(465,282,866,491))
pair((28,126,456,184),(516,126,456,184),(273,891,436,984))
para('Small standalone labels need explicit protection: the bottom dimension 14 and the STUD callout were retained after checking what the draft removed. Protected text, fractions and dense mechanical details are pixel-identical to the current master.',95,145,11);end()
head('Exactly what was removed','Red shows deleted source marks. This provides an auditable comparison, including any questionable isolated marks that the assumption classifies as noise.')
pic('Plate12_RemovedMarks.png',(28,98,582,517))
text(645,588,'Candidate scope',14,True)
for yy,t in [(555,'Separate comparison copy.'),(527,'Current book master retained.'),(499,'No geometric resampling.'),(471,'No replacement lettering or lines.'),(443,'Kept pixels are unchanged.'),(415,'Deleted pixels become white.')]:text(645,yy,t,11)
y=365
for t in textwrap.wrap('Remaining uncertainty: isolated dots, weak ticks and marks that do not form recognizable text or a clear line may be lost. Some noise adjacent to retained strokes remains.',45):text(645,y,t,11);y-=16
text(645,234,'Review suggestion',13,True)
y=208
for t in textwrap.wrap('Use the whole plate to judge readability, then the enlarged crops and red map to decide whether this editorial tradeoff is acceptable.',45):text(645,y,t,11);y-=16
end();c.save();d=fitz.open(stream=buf.getvalue(),filetype='pdf');d.set_toc(toc);assert len(d)==5
(P/'Plate12_Aggressive_Comparison.pdf').write_bytes(d.tobytes(deflate=True,garbage=4))
for i,p in enumerate(d):
 for t in p.get_text('blocks'):assert 0<=t[0]<=t[2]<=W and 0<=t[1]<=t[3]<=H,(i,t)
 p.get_pixmap(matrix=fitz.Matrix(1.15,1.15)).save(P/f'proof-{i+1:02}.png')
print(json.dumps(result,indent=2));print('Five comparison pages rendered with text bounds checked.')
