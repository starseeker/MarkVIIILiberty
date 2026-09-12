#!/usr/bin/env python3
"""Measure output printed borders against the fitted rectangular targets.

A check of line alignment and mapping orientation, not independent metrology of
interior objects. Run after prepare_assets.py; requires NumPy, SciPy and Pillow.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
ROOT=Path(__file__).resolve().parent

def main():
 rows={}
 for page,cfg in json.loads((ROOT/'calibration/border_transforms.json').read_text()).items():
  a=np.asarray(Image.open(ROOT/'assets'/f'p{page}-geometry.png').convert('L'),dtype=float)
  ink=gaussian_filter(a,6)-gaussian_filter(a,.65)
  width,height=cfg['output_border_size'];left,top,_,_=cfg['output_padding'];edges={}
  for name,horizontal,target,start,length in [('top',True,top,left,width),('bottom',True,top+height,left,width),('left',False,left,top,height),('right',False,left+width,top,height)]:
   along=start+np.linspace(.05,.95,400)*length
   offsets=np.arange(-4,4.01,.25)
   cross=np.broadcast_to(target+offsets,(len(along),len(offsets)))
   axis=np.broadcast_to(along[:,None],cross.shape)
   response=map_coordinates(ink,[cross,axis] if horizontal else [axis,cross],order=1)
   deviation=abs(offsets[np.argmax(response,axis=1)])
   edges[name]=dict(median_absolute_deviation_from_target_pixels=float(np.median(deviation)),p95_absolute_deviation_pixels=float(np.quantile(deviation,.95)))
  assert cfg['min_jacobian']>0
  rows[page]=dict(source_max_bow_pixels=max(e['stats']['curve_bow_pixels'] for e in cfg['edges'].values()),output_edge_checks=edges,min_jacobian=cfg['min_jacobian'],max_jacobian=cfg['max_jacobian'])
 result=dict(note='Output line checks measure fit to selected border constraints, not independent interior metrology.',pages=rows)
 (ROOT/'calibration/line_validation.json').write_text(json.dumps(result,indent=2))
 print({p:round(max(e['p95_absolute_deviation_pixels'] for e in r['output_edge_checks'].values()),2) for p,r in rows.items()})
if __name__=='__main__':main()
