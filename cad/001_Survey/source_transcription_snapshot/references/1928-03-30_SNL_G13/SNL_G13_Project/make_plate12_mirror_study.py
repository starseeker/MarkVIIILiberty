#!/usr/bin/env python3
"""Visual and numerical checks for the first paired reverse-page experiment."""
from pathlib import Path
import io,json,textwrap
import fitz,numpy as np
from PIL import Image
from reportlab import rl_config
rl_config.useA85=False  # Use direct lossless Flate streams.
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import proof_fonts
P=Path(__file__).resolve().parent;R=P/'restoration';D=R/'paired';W,H=1000,720
old=D/'p284-local-only.png';new=R/'aggressive/Plate12_Current.png';source=P/'assets/p284-geometry.png'
a=np.asarray(Image.open(old));b=np.asarray(Image.open(new));checks=[]
for label,rect,kind in [
 ('Upper blank area',(166,158,285,275),'background'),
 ('Middle blank area',(181,478,276,578),'background'),
 ('Lower-left mottling',(155,666,260,727),'possible localized reverse-ink bleed'),
 ('Upper control rod',(304,80,342,352),'foreground'),
 ('Shaft-lever lettering',(499,297,768,321),'foreground'),
 ('Fine body edge',(474,171,494,348),'foreground')]:
 x0,y0,x1,y1=rect;aa=a[y0:y1,x0:x1];bb=b[y0:y1,x0:x1];dark=aa<120
 r={'region':label,'box':rect,'kind':kind,'mean_ink_before':float((255-aa).mean()),'mean_ink_after':float((255-bb).mean()),'dark_pixels_before':int(dark.sum()),'dark_to_white_pixels':int(((aa<120)&(bb>245)).sum()),'dark_pixel_mean_absolute_change_0_255':float(np.abs(aa.astype(float)-bb)[dark].mean()) if dark.any() else None}
 r['mean_ink_reduction_percent']=100*(1-r['mean_ink_after']/r['mean_ink_before']);checks.append(r)
assert all(r['dark_to_white_pixels']==0 for r in checks if r['kind']=='foreground')
result={'status':'PASS','geometry_changed':False,'pixel_size':list(Image.open(new).size),'reverse_page':283,'global_registration_correlation':json.loads((D/'p284-model.json').read_text())['global_fit_correlation'],'checks':checks,'limitations':'Selected regions, not a complete proof of faint-line fidelity. Correlation is in-sample registration evidence, not held-out accuracy. Residual mottling remains.'}
(D/'p284-validation.json').write_text(json.dumps(result,indent=2))
buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=(W,H),initialFontName='ProofSans');c.setTitle('Plate 12 — mirrored reverse-page cleanup comparison');n=0

def text(x,y,s,size=11,bold=False):
 c.setFont('ProofSans-Bold' if bold else 'ProofSans',size);c.setFillColorRGB(.12,.18,.22);c.drawString(x,y,s)
def para(s,y,width=145,size=11):
 for line in textwrap.wrap(s,width):text(28,y,line,size);y-=size+4
 return y
def head(title,sub):text(28,680,title,20,True);para(sub,653,147,10)
def raster(path,box,crop=None):
 im=Image.open(path)  # Preserve grayscale PDF storage without expanding to RGB.
 if crop:im=im.crop(crop)
 x,y,w,h=box;scale=min(w/im.width,h/im.height);ww,hh=im.width*scale,im.height*scale;c.drawImage(ImageReader(im),x+(w-ww)/2,y+(h-hh)/2,ww,hh)
def end():
 global n
 n+=1;text(28,20,'SNL G-13 | Plate 12 | Source-derived paired-image experiment',9);text(950,20,str(n),9);c.showPage()
head('The mirrored reverse page does help','Page 284 contains Plate 12. Its visible ghost matches Plates 10 and 11 on the reverse of the leaf, page 283.')
text(76,614,'Original page 284',12,True);text(579,614,'Page 283, mirrored and registered',12,True)
raster(P/'sources/p284.jpg',(50,98,400,502));raster(D/'p283-mirrored-registered.png',(550,98,400,502))
para('Both pages were photographed while curved. The reference therefore needs a projective alignment plus a smooth local adjustment; mirroring alone is insufficient. Only the reverse reference moves. Plate 12 retains its accepted geometry.',81,145,11);end()
head('Same cleanup, with and without the reverse reference','The threshold and contrast settings are identical. The added step estimates reverse-ink attenuation before the local paper normalization.')
for x,label,path in [(28,'Rectified source',source),(352,'Earlier local cleanup',old),(676,'With mirrored reverse reference',new)]:
 text(x,608,label,11,True);raster(path,(x,130,296,451))
para('The faint tank and wiring patterns diminish further. The reference is blurred to approximate transmission through paper, and its strength is fitted locally. The result remains a lossless grayscale master; no drawing geometry or lettering is reconstructed.',102,145,11);end()
for title,crop,note in [
 ('Ghost wiring near fine original lines',(35,100,490,398),'Compare the pale curved ghost inside the upper left body area. Original straight body edges, the control rod and lettering remain in their original pixel positions.'),
 ('Control rods, leaders and small lettering',(278,303,830,608),'This enlargement checks genuine foreground intersections and weak context outlines. The correction divides by the estimated reverse-ink attenuation; it does not erase all ink wherever the reverse page is dark.')]:
 head(title,'Enlarged identical source-coordinate crop; earlier local cleanup at left, paired correction at right.')
 text(28,610,'Earlier local cleanup',12,True);text(516,610,'With mirrored reverse reference',12,True)
 raster(old,(28,163,456,417),crop);raster(new,(516,163,456,417),crop);para(note,123,145,11);end()
head('Darker mottling may also be reverse printing','Several clusters lie over inked battery and wiring regions. Localized ink penetration is plausible; the photographs cannot establish the physical cause.')
for x,label,path in [(28,'Earlier local cleanup',old),(352,'Registered reverse printing',D/'p283-reference-in-plate12-canvas.png'),(676,'Current paired correction',new)]:
 text(x,610,label,11,True);raster(path,(x,342,296,250),(60,627,341,863))
para('Selected blank patches lose about 24–32% of their remaining mean ink after the earlier cleanup. The darker mottled patch changes by only about 4%. These are sample measurements, not a claim that all bleed-through is removed.',302,145,11)
para('In three checked foreground regions, no previously dark pixel (gray below 120) became near-white (above 245). Mean changes at those dark pixels are about 1–2 gray levels out of 255. This supports the conservative setting but cannot prove every faint line is preserved.',235,145,11)
para('The smooth transfer field handles the broad ghost but may underestimate intense local ink penetration. Removing all mottling would need stronger local evidence at original-line crossings. Plate 12 remains raster-preferred; sources and the previous cleanup are retained.',153,145,11)
para('Registration evidence: the final whole-page fit correlation is 0.59, followed by 66 locally matched windows and a smoothed transfer field. This is fitting evidence, not a held-out validation score.',86,145,10);end()
c.save();pdf=fitz.open(stream=buf.getvalue(),filetype='pdf');assert len(pdf)==5
pdf.set_toc([[1,'Mirrored source match',1],[1,'Whole-plate comparison',2],[1,'Ghost detail',3],[1,'Foreground detail',4],[1,'Residual mottling and checks',5]])
(P/'Plate12_Mirror_Study.pdf').write_bytes(pdf.tobytes(garbage=4,deflate=True))
for i,p in enumerate(pdf):
 for t in p.get_text('blocks'):assert 0<=t[0]<=t[2]<=W and 0<=t[1]<=t[3]<=H,(i,t)
 p.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(D/f'study-{i+1:02}.png')
print('Saved and rendered five-page paired comparison.');print(json.dumps(checks,indent=2))
