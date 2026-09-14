"""Build weak local, same-parity priors from accepted table and frame traces.
Run measure_book_trends.py first. Never modifies source images or artwork.
"""
from pathlib import Path
import json,numpy as np
from rectify_borders import evaluate
P=Path(__file__).resolve().parent;C=P/'calibration'
rows=json.loads((C/'book_page_trends.json').read_text());frames=[]
for n,cfg in json.loads((C/'border_transforms.json').read_text()).items():
 w,h=cfg['source_image_size'];A=[];b=[]
 for name in ['top','bottom']:
  curve=cfg['edges'][name];x=np.linspace(*curve['domain'],100);y=evaluate(curve,x);u=x/w-.5;v=y/h-.5
  f=np.column_stack([u,u*u,u*u*u,u*v,u*u*v,u*u*u*v]);A.extend(f-f.mean(0));b.extend(-(v-v.mean()))
 coef=np.linalg.lstsq(np.vstack([A,np.diag([.001,.002,.006,.001,.002,.006])]),np.r_[b,np.zeros(6)],rcond=None)[0]
 frames.append(dict(page=int(n),kind='framed plate',model=dict(coeff=coef.tolist(),accepted=True)))
prior={}
for n in range(277,307):
 near=[r for r in rows+frames if r['model']['accepted'] and r['page']%2==n%2 and abs(r['page']-n)<=24 and r['page']!=n]
 prior[str(n)]=dict(source_pages=[r['page'] for r in near],coeff=np.median([r['model']['coeff'][3:] for r in near],axis=0).tolist(),weight=.1)
(C/'book_priors.json').write_text(json.dumps(prior,indent=2));(C/'book_frame_trends.json').write_text(json.dumps(frames,indent=2))
print('Built local priors for',len(prior),'numbered figure pages.')
