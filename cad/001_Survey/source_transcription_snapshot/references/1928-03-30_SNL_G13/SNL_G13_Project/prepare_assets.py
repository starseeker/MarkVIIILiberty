#!/usr/bin/env python3
"""Deterministic, conservative image geometry and project inventory.

Uses original pixels. No inpainting, generative reconstruction or sharpening.
Coordinates refer to the source after the per-page rotation specified below.
Framed plates and p293 use traced-line nonlinear correction. Six further pages
use restrained text/line models; other pages retain affine correction or a crop.
"""
from pathlib import Path
import json, hashlib, math, io, sys
import numpy as np
from PIL import Image
from project_sequence import ORDER, LABELS, FOLDOUT_SIZE_POINTS
import rectify_borders, rectify_axes, rectify_text_model

ROOT=Path(__file__).resolve().parent
FIGURES={
277:dict(plates=[1],rotate=90,crop=[125,105,1780,955],horizontal=[1000,-23.8],vertical=None,
 reference='Caption baseline only; no geometry inferred from the vehicle photograph.'),
280:dict(plates=[6],rotate=90,crop=[295,70,1955,1100],horizontal=[1000,-27.1],vertical=None,
 reference='Caption baseline; deliberately angled and broken control rods are not straightened.'),
281:dict(plates=[7],rotate=90,crop=[135,45,1760,1030],horizontal=[1000,-5.9],vertical=None,
 reference='Caption baseline only; isometric armor edges are not assumed horizontal or vertical.'),
283:dict(plates=[10,11],rotate=0,crop=[45,265,1085,1930],horizontal=[1000,7.9],vertical=None,
 reference='Caption baseline; both plates retained together in a single image asset.'),
293:dict(plates=[21],rotate=90,crop=[255,75,1660,1108],horizontal=[1266,20],vertical=[14,854],
 reference='Main shaft centerline and a section face provide tentative orthogonal directions.'),
294:dict(plates=[22],rotate=90,crop=[250,20,1960,1138],horizontal=[1000,-17],vertical=[7,600],
 reference='Long shaft edge and a section face provide tentative orthogonal directions.'),
278:dict(plates=[3,4],rotate=0,crop=[35,85,1120,1750],horizontal=[1000,0],vertical=None,
 reference='Two plates kept together. Crop only; no shared orthogonal frame is available.'),
279:dict(plates=[5],rotate=90,crop=[385,10,1470,1110],horizontal=[1000,0],vertical=None,
 caption_region=[765,1060,1110,1097],reference='Caption baseline; assembled pump views preserve their internal perspective.'),
282:dict(plates=[8,9],rotate=0,crop=[30,180,1110,1655],horizontal=[1000,0],vertical=None,
 reference='Two plates kept together. Crop only; illustrated perspective edges are not forced to page axes.'),
284:dict(plates=[12],rotate=90,crop=[485,65,1710,1088],horizontal=[1000,0],vertical=None,
 caption_region=[930,1035,1300,1078],reference='Caption baseline; rod angles are retained pending stronger independent reference lines.'),
292:dict(plates=[20],rotate=90,crop=[575,280,1640,930],horizontal=[1000,0],vertical=None,
 caption_region=[755,878,1485,912],reference='Caption baseline; the two views retain their relative arrangement.'),
295:dict(plates=[23],rotate=90,crop=[415,65,1495,970],horizontal=[1000,0],vertical=None,
 caption_region=[785,915,1130,953],reference='Caption baseline; section-axis refinement remains pending.'),
296:{'plates': [24], 'rotate': 90, 'crop': [559, 61, 1713, 1090], 'horizontal': [1000, 0], 'vertical': None, 'reference': 'Caption baseline only; radiator-system leaders and deliberately angled plumbing remain as photographed.', 'caption_region': [944, 1047, 1350, 1080]},
298:{'plates': [26], 'rotate': 0, 'crop': [298, 547, 850, 1251], 'horizontal': [1000, 0], 'vertical': None, 'reference': 'Caption baseline only; original photographic perspective and rounded track-link shape retained.', 'caption_region': [443, 1206, 736, 1235]},
299:{'plates': [27], 'rotate': 0, 'crop': [69, 583, 1014, 1714], 'horizontal': [1000, 0], 'vertical': None, 'reference': 'Caption baseline only; the angled view of the track wheel is retained.', 'caption_region': [388, 1661, 742, 1704]},
300:{'plates': [28], 'rotate': 0, 'crop': [36, 614, 1090, 1237], 'horizontal': [1000, 0], 'vertical': None, 'reference': 'Caption baseline only; both assembled views retained in their original arrangement.', 'caption_region': [373, 1193, 790, 1224]},
301:{'plates': [29], 'rotate': 90, 'crop': [110, 100, 1809, 964], 'horizontal': [790, 0], 'vertical': [-12, 525], 'reference': 'Main shaft centerline and upper end-plate face used as tentative perpendicular axes; lower end-plate curvature remains unresolved.', 'identifier_exclusion': [1772, 751, 1836, 1058]},
302:{'plates': [30], 'rotate': 0, 'crop': [45, 256, 1086, 1540], 'horizontal': [1000, 0], 'vertical': None, 'reference': 'Caption baseline only; no circularity or internal scale constraint imposed on the brake band.', 'caption_region': [362, 1490, 774, 1524]},
303:{'plates': [31], 'rotate': 0, 'crop': [43, 647, 1084, 1552], 'horizontal': [590, -34], 'vertical': [15, 520], 'reference': 'Long lower base edge and right upright edge used as perpendicular reference axes; residual curvature remains unresolved.'},
304:{'plates': [32], 'rotate': 0, 'crop': [34, 448, 1092, 1371], 'horizontal': [1000, 0], 'vertical': None, 'reference': 'Caption baseline only; illustrated brake-band geometry retained.', 'caption_region': [365, 1327, 768, 1358]},
'277_foldout':dict(plates=[2],rotate=0,crop=[45,65,1945,815],horizontal=[1000,0],vertical=None,
 reference='Foldout preserved at source aspect ratio. Modern archive overlay below the original print is retained separately as provenance.'),

}

def save_png(image,path,**kwargs):
 buffer=io.BytesIO()
 image.save(buffer,format='PNG',**kwargs)
 path.write_bytes(buffer.getvalue())

def caption_slope(source,box):
 from scipy.ndimage import label,find_objects
 a=np.array(source.convert('L').crop(box));labs,_=label(a<115);pts=[]
 for sl in find_objects(labs):
  if sl is None:continue
  ys,xs=sl;w=xs.stop-xs.start;h=ys.stop-ys.start
  if 2<=w<=22 and 5<=h<=28:pts.append([(xs.start+xs.stop)/2,ys.stop])
 if len(pts)<10:return 0,dict(status='insufficient caption components; rotation not applied')
 pts=np.array(pts);slopes=np.linspace(-.06,.06,1201)
 costs=[]
 for m in slopes:
  v=pts[:,1]-m*pts[:,0];costs.append(np.quantile(abs(v-np.median(v)),.6))
 idx=int(np.argmin(costs));slope=float(slopes[idx])
 if abs(slope)>.055:return 0,dict(status='slope outside conservative range; rotation not applied')
 return slope,dict(region=box,components=len(pts),slope=slope,baseline_residual_60_percent_pixels=float(costs[idx]))

def prepare_figure(page,cfg):
 source=Image.open(ROOT/'sources'/f'p{page}.jpg').convert('RGB')
 if cfg['rotate']: source=source.transpose(Image.Transpose.ROTATE_270)
 cfg=cfg.copy()
 if cfg.get('caption_region'):
  m,measure=caption_slope(source,cfg['caption_region'])
  cfg['horizontal']=[1000,m*1000];cfg['caption_measurement']=measure
 if cfg.get('identifier_exclusion'):
  from PIL import ImageDraw
  box=cfg['identifier_exclusion'];ImageDraw.Draw(source).rectangle(box,fill=source.getpixel((box[0]-15,box[1])))
 x0,y0,x1,y1=cfg['crop']
 crop=source.crop((x0,y0,x1,y1))
 # Exclude only the upright running identifier, outside the plate artwork.
 # Its native text equivalent is placed separately in Scribus.
 if page in [277,281]:
  from PIL import ImageDraw
  ImageDraw.Draw(crop).rectangle((1740-x0,760-y0,crop.width,crop.height),fill=source.getpixel((1720,1030)))
 if page==283:
  from PIL import ImageDraw
  ImageDraw.Draw(crop).rectangle((780-x0,0,crop.width,315-y0),fill=source.getpixel((750,270)))
 u=np.array(cfg['horizontal'],float);u/=np.linalg.norm(u)
 if cfg['vertical']:
  v=np.array(cfg['vertical'],float);v/=np.linalg.norm(v)
 else: v=np.array([-u[1],u[0]])
 basis=np.column_stack([u,v]); forward=np.linalg.inv(basis)
 corners=np.array([[0,0],[crop.width,0],[0,crop.height],[crop.width,crop.height]])
 mapped=corners@forward.T
 lower=np.floor(mapped.min(axis=0));upper=np.ceil(mapped.max(axis=0))
 size=tuple(int(v) for v in upper-lower)
 offset=basis@lower
 coeff=tuple([basis[0,0],basis[0,1],offset[0],basis[1,0],basis[1,1],offset[1]])
 corrected=crop.transform(size,Image.Transform.AFFINE,coeff,
   resample=Image.Resampling.BICUBIC,fillcolor=(248,246,239))
 save_png(corrected,ROOT/'assets'/f'p{page}-geometry.png',dpi=(300,300))
 save_png(crop,ROOT/'proofs'/f'p{page}-before.png')
 if page in [301,303]:
  from PIL import ImageDraw
  original=Image.open(ROOT/'sources'/f'p{page}.jpg').convert('RGB');scale=original.width/800
  pairs=[[(430,587),(432,1367)],[(121,564),(645,576)]] if page==301 else [[(152,1047),(743,1013)],[(713,494),(728,1014)]]
  draw=ImageDraw.Draw(original)
  for points in pairs:draw.line([(x*scale,y*scale) for x,y in points],fill=(220,40,45),width=3)
  if cfg['rotate']:original=original.transpose(Image.Transpose.ROTATE_270)
  save_png(original.crop(cfg['crop']),ROOT/'proofs'/f'p{page}-constraints.png')
  cfg['reference_segments_in_800px_portrait_preview']=pairs

 result={**cfg,'source_image_size':source.size,'output_size':size,
    'inverse_affine_coefficients':coeff,'rotation_degrees':math.degrees(math.atan2(u[1],u[0])),
    'method':('crop + tentative affine axis correction' if cfg['vertical'] else
      'crop only' if cfg['horizontal'][1]==0 else 'crop + caption-based affine deskew'),
    'status':'pilot; nonlinear curvature not corrected; not a metric engineering reference',
    'estimated_control_point_precision_pixels':3,
    'identifier_exclusion_rectangle_in_rotated_source': [1740,760,x1,y1] if page in [277,281] else [780,265,1085,315] if page==283 else None}
 return result

def main():
 for folder in ['assets','proofs','calibration']:(ROOT/folder).mkdir(exist_ok=True)
 out={}
 for page,cfg in FIGURES.items():
  out[str(page)]=prepare_figure(page,cfg)
 out.update(rectify_borders.main())
 out.update(rectify_axes.main())
 out.update(rectify_text_model.main())
 out={str(page):out[str(page)] for page in ORDER if str(page) in out}
 (ROOT/'calibration'/'figure_transforms.json').write_text(json.dumps(out,indent=2))
 write_inventory(out)

def write_inventory(out):
 sources={p.name:p for p in (ROOT/'sources').glob('*.jpg')}
 order=LABELS
 records=[]
 for label in ['I','II']+[str(p) for p in range(1,312)]:
  name={'I':'cover001.jpg','II':'cover002.jpg'}.get(label,f'p{int(label):03}.jpg' if label.isdigit() else '')
  exists=name in sources
  pnum=int(label) if label.isdigit() else None
  category='front matter' if not pnum else 'title leaf' if pnum==1 else 'parts table' if 2<=pnum<=276 else 'plate page' if 277<=pnum<=306 else 'notes'
  rec=dict(printed_label=label,arabic_number=pnum,source_filename=name if exists else None,
   supplied=exists,pilot_page=order.index(label)+1 if label in order else None,
   page_type=category,plates=out.get(str(pnum),{}).get('plates',[]),
   status=('reconstructed; needs independent proofreading' if category!='plate page' else 'original artwork; individually reviewed correction') if label in order else 'received; not processed' if exists else 'not supplied')
  if exists:
   rec['sha256']=hashlib.sha256(sources[name].read_bytes()).hexdigest()
   rec['image_size']=Image.open(sources[name]).size
  records.append(rec)
 records.append(dict(printed_label='Face p. 277',arabic_number=None,source_filename='p277_foldout.jpg',supplied=True,pilot_page=order.index('Face p. 277')+1,page_type='foldout',plates=[2],status='source artwork; provisional wide page',sha256=hashlib.sha256(sources['p277_foldout.jpg'].read_bytes()).hexdigest(),image_size=Image.open(sources['p277_foldout.jpg']).size,page_size_points=FOLDOUT_SIZE_POINTS))
 inventory=dict(nominal_page_size_inches=[6,9],reported_last_arabic_page=311,
   counting_note='Track Arabic folios 1–311 separately from Roman front matter and inserts. Supplied p001 visibly confirms Arabic 1 as the title leaf. All Arabic folios are supplied; physical binding and any unnumbered blank leaves remain unverified.',
   supplied_source_count=len(sources),pilot_printed_order=order,pages=records,
   extra_insertions=[dict(printed_label='Face p. 277',plate=2,position='facing p277; exact binding position unconfirmed',status='received; included after p277 in plate reading sequence; physical binding/imposition unconfirmed')],
   camera_observations=[
    'Front sample p2/p6 show stronger curved table rules than p3/p7.',
    'Back odd pages 307/309/311: card above; even 308/310: card below, inverted.',
    'This capture alternation does not demonstrate a single global odd/even warp, or establish a flip.',
    'All 30 numbered figure pages reviewed. Ten framed pages and the p293 paired-axis correction retained; six pages use new restrained text/line models. See calibration/plate_review.json.',
    'All 275 table pages surveyed automatically; 261 accepted models support a changing local parity trend, not one global transform.',
    'The user confirms that Plate 2 was scanned flat. Its corrected asset and placement are unchanged.'
   ])
 (ROOT/'page_inventory.json').write_text(json.dumps(inventory,indent=2))
 # Plain TSV is an inventory interchange file; no spreadsheet dependencies.
 fields=['printed_label','pilot_page','supplied','page_type','source_filename','status']
 (ROOT/'page_inventory.tsv').write_text('\t'.join(fields)+'\n'+'\n'.join('\t'.join(str(r.get(f) or '') for f in fields) for r in records)+'\n')

if __name__=='__main__':
 if '--inventory-only' in sys.argv:
  write_inventory(json.loads((ROOT/'calibration/figure_transforms.json').read_text()))
 else:main()
