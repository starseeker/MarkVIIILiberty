#!/usr/bin/env python3
"""Editable, source-pixel cleanup trial; never redraws or retypes linework."""
from pathlib import Path
import io,json,hashlib
import numpy as np
from scipy import ndimage as nd
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent

def save(im,path):
 b=io.BytesIO();im.save(b,format='PNG',optimize=True);path.write_bytes(b.getvalue())
def region_mask(shape,rects,polys):
 im=Image.new('L',(shape[1],shape[0]));d=ImageDraw.Draw(im)
 for r in rects:d.rectangle(r,fill=255)
 for pts in polys:d.polygon(pts,fill=255)
 return np.asarray(im)>0

def main():
 cfg=json.loads((P/'config.json').read_text());src=P/'Plate12_Current.png';im=Image.open(src).convert('L');a=np.asarray(im)
 assert hashlib.sha256(src.read_bytes()).hexdigest()==cfg['source_sha256']
 protected=region_mask(a.shape,cfg['text_rectangles'],cfg['detail_polygons'])
 # Use faint grayscale evidence, then tolerate a one-pixel bend/alias before
 # searching for sustained directional strokes. No global darkening or threshold
 # is applied to the retained pixels themselves.
 candidate=nd.binary_dilation(a<cfg['candidate_gray_cutoff'],iterations=1)
 for length in cfg['support_lengths']:
  coherent=np.zeros(a.shape,bool)
  for deg in range(0,180,3):
   rad=np.deg2rad(deg);c=length//2+2;sz=2*c+1
   k=Image.new('1',(sz,sz));d=ImageDraw.Draw(k)
   d.line((round(c-np.cos(rad)*length/2),round(c-np.sin(rad)*length/2),round(c+np.cos(rad)*length/2),round(c+np.sin(rad)*length/2)),fill=1,width=1)
   coherent |= nd.binary_opening(candidate,structure=np.asarray(k))
  support=nd.binary_dilation(coherent,iterations=cfg['line_margin_pixels'])|protected
  # Small isolated image islands are not evidence of independent drawing parts.
  # Label/detail regions are protected regardless of connected-component size.
  islands,n=nd.label(support);sizes=np.bincount(islands.ravel());support=(sizes[islands]>=cfg['minimum_support_area'])&support|protected
  zones=region_mask(a.shape,cfg.get('background_rectangles',[]),[])
  path_image=Image.new('L',im.size);draw=ImageDraw.Draw(path_image)
  for path in cfg.get('foreground_paths_in_background',[]):
   draw.line([tuple(point) for point in path],fill=255,width=cfg['manual_corridor_width'],joint='curve')
  for box in cfg.get('foreground_ellipses_in_background',[]):
   draw.ellipse(box,outline=255,width=cfg['manual_corridor_width'])
  # The manually reviewed zones reject streak-like blotches that an orientation
  # detector would mistake for drawing strokes. Corridors retain source pixels;
  # these paths are masks, never newly drawn output linework.
  support[zones]=(protected | (np.asarray(path_image)>0))[zones]
  out=np.where(support,a,255).astype(np.uint8)
  stem=f'Plate12_Trial_{length}'
  save(Image.fromarray(out),P/(stem+'.png'));save(Image.fromarray(np.uint8(support)*255),P/(stem+'_KeepMask.png'))
  removal=(255-a)*(~support)
  heat=np.stack([np.full(a.shape,255),255-removal,255-removal],axis=-1).astype(np.uint8)
  save(Image.fromarray(heat),P/(stem+'_Removed.png'))
  print(length,'retained area',round(float(support.mean()),3),'removed ink fraction',round(float(removal.sum()/np.maximum(1,(255-a).sum())),3),flush=True)
if __name__=='__main__':main()
