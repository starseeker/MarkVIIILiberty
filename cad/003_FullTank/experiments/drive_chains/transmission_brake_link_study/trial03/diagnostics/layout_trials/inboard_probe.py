"""Test a side-mounted link interpretation without altering accepted artifacts."""
from pathlib import Path
import json,sys
import numpy as np
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty');H=ROOT/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(H))
from transmission_brake_link_parts import parts
m=json.loads((H/'transmission_brake_band_study/trial01/isolated/manifest.json').read_text());r=json.loads((H/'transmission_brake_link_study/trial01/report.json').read_text());band=json.loads((H/'transmission_brake_band_study/controls.json').read_text())['controls']
rows={v['name']:v for v in m['occurrences']};cache={}
def shape(name):
 row=rows[name];key=row['definition']
 if key not in cache:
  s=Part.Shape();s.read(m['definitions'][key]['brep_path']);cache[key]=s
 s=cache[key].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));return s
c=r['controls'];d=dict(r['dimensions']);plate=shape('TransmissionFrame_MiddleDiaphragm');lowerx=plate.BoundBox.XMax+c['lower_head_radius']+2.0
upper=r['interfaces']['PortTrack']['upper_mm'];d['lower_eye_relative_mm']=[lowerx-upper[0],0,r['interfaces']['PortTrack']['lower_mm'][2]-upper[2]];d['lower_anchor_radius_mm']=1831.4946420457636-lowerx;d['pin_center_distance_mm']=App.Vector(*d['lower_eye_relative_mm']).Length
shapes,detail=parts(c,d);new={};shifts={}
for prefix in ['PortLowSpeed','PortTrack','StarboardLowSpeed','StarboardTrack']:
 role='low' if 'LowSpeed' in prefix else 'track';sign=-1 if prefix.startswith('Port') else 1
 offset=band[role]['width']/2+band['steel_side_overhang']+c['lower_stock']/2+1.5
 shifts[prefix]=sign*offset
 pose=App.Placement(App.Matrix(*rows[prefix+'Bracket']['frame']));pose.Base.y+=sign*offset
 for suffix in ['Bracket']+(['TrackStop'] if False else []):
  n=prefix+suffix;s=shape(n);s.translate(App.Vector(0,sign*offset,0));new[n]=s
 if 'Track' in prefix:
  n=prefix+'Stop';s=shape(n);s.translate(App.Vector(0,sign*offset,0));new[n]=s
 for role in ['link','pin']:
  s=shapes[role].copy();s.Placement=pose;new[prefix+role]=s
 for i,y in enumerate([-d['cotter_y_mm'],d['cotter_y_mm']],1):
  s=shapes['cotter'].copy();s.Placement=pose.multiply(App.Placement(App.Vector(0,y,0),App.Rotation())).multiply(s.Placement);new[prefix+'cotter'+str(i)]=s
others={n:shape(n) for n in rows if n not in new};others.update(new)
def bounds(s):
 b=s.copy().cleaned().BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
names=sorted(others);boxes=np.array([bounds(others[n]) for n in names]);checked=set();pairs=[]
for name,s in new.items():
 b=np.array(bounds(s));possible=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
 for i in possible:
  n=names[i];pair=tuple(sorted([name,n]))
  if n==name or pair in checked:continue
  checked.add(pair);v=s.common(others[n]).Volume;pairs.append(dict(first=name,second=n,volume_mm3=v,passed=abs(v)<1e-5))
 print(name,len(pairs),'pairs',flush=True)
failed=[v for v in pairs if not v['passed']]
result=dict(dimensions=d,shifts_y_mm=shifts,checks=pairs,failed=failed,passed=not failed)
Path('report.json').write_text(json.dumps(result,indent=2)+'\n')
for n,s in new.items():s.exportBrep(str(Path(n+'.brep')))
print(json.dumps({k:result[k] for k in ['dimensions','shifts_y_mm','failed','passed']},indent=2))
