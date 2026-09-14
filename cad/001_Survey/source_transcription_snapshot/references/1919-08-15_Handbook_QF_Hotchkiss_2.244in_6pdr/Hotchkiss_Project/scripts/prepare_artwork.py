"""Conservative deterministic artwork preparation. No tracing or invented marks."""
from pathlib import Path
from PIL import Image,ImageOps
from scipy.ndimage import maximum_filter,gaussian_filter
import numpy as np,json,hashlib,io
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets';meta=[]
def src(name):return Image.open(next((ROOT/'sources').glob(name+'.*')))
def save(im,name,source,operation):
 buf=io.BytesIO();im.save(buf,format='PNG',dpi=(400,400));(A/(name+'.png')).write_bytes(buf.getvalue());Image.open(A/(name+'.png')).load();meta.append(dict(asset=name+'.png',source=source,pixels=list(im.size),operation=operation,sha256=hashlib.sha256((A/(name+'.png')).read_bytes()).hexdigest()))
def paper(im,white=246,black=22):
 g=np.asarray(im.convert('L'),dtype=np.float32);bg=gaussian_filter(maximum_filter(g,size=35),12)
 n=np.minimum(g/np.maximum(bg,1)*255,255);a=np.clip((n-black)*255/(white-black),0,255)
 return Image.fromarray(a.astype('uint8'))
# Preserve the title seal as scan-derived art.
seal=paper(src('primary_01').crop((870,2100,1320,2560)));seal=Image.fromarray(np.clip(np.asarray(seal,dtype=float)*255/215,0,255).astype('uint8'));save(seal,'printer_seal','primary_01.png','crop [870,2100,1320,2560]; local paper normalization; additional white point 215')
# Rotate the photographs without resampling; crop only their printed image areas.
for leaf,label,box in [(3,'photo_A',(264,214,3095,1790)),(4,'photo_B',(198,218,3159,1856)),(5,'photo_C',(416,216,2946,1835))]:
 im=src(f'primary_{leaf:02}').transpose(Image.Transpose.ROTATE_90).crop(box).convert('L')
 save(im,label,f'primary_{leaf:02}.png',f'90 degrees counterclockwise, exact pixel crop {box}; grayscale, no tonal clipping')
# Primary plates already have white grounds. Keep every original pixel after orientation.
for leaf,lab in [(21,'I'),(22,'III'),(23,'IV'),(24,'VI'),(25,'VII'),(26,'VIII'),(27,'IX'),(28,'X')]:
 im=src(f'primary_{leaf:02}').convert('L')
 if lab=='I':im=im.transpose(Image.Transpose.ROTATE_270)
 save(im,'plate_'+lab,f'primary_{leaf:02}.png','90 degrees clockwise, otherwise grayscale only' if lab=='I' else 'grayscale only; no thresholding or geometric warp')
# Secondary-only plates remain continuous tone, including uncertain faint lines.
for leaf,lab in [(24,'II'),(27,'V')]:
 im=src(f'secondary_{leaf:02}')
 save(paper(im),'plate_'+lab,f'secondary_{leaf:02}.jpeg','local maximum-filter background (35 px), Gaussian sigma 12 px; monotonic remapping black 22 / white 246; no binarization or geometry correction')
save(src('primary_20').crop((1046,3206,1123,3276)).convert('L'),'end_ornament','primary_20.png','exact crop [1046,3206,1123,3276] of printer ornament')
(ROOT/'data/artwork.json').write_text(json.dumps(meta,indent=2))
print('prepared',len(meta),'assets')
