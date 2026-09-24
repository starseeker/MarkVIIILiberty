"""Place the complete proposed rear joints against the saved development model."""
from pathlib import Path
import json,sys
import numpy as np
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty');H=ROOT/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(H))
read=lambda p:json.loads(p.read_text());m=read(H/'transmission_brake_link_study/trial03/isolated/manifest.json');r=read(ROOT/'.work/transmission-brake-anchors/probe04/report.json');d=r['dimensions'];c=read(H/'transmission_brake_anchor_study/controls.json')['controls']
rows={v['name']:v for v in m['occurrences']};cache={};new_cache={}
def existing(name):
 row=rows[name];key=row['definition']
 if key not in cache:
  s=Part.Shape();s.read(m['definitions'][key]['brep_path']);cache[key]=s
 s=cache[key].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def fresh(role,pose):
 if role not in new_cache:
  s=Part.Shape();s.read(str(ROOT/'.work/transmission-brake-anchors/probe04'/(role+'.brep')));assert s.Placement.isIdentity();new_cache[role]=s
 s=new_cache[role].copy();s.Placement=pose;return s
new={};revised={};poses={};keys={};flip=App.Rotation(App.Vector(1,0,0),180)
def add(name,key,pose):new[name]=fresh(key,pose);poses[name]=list(pose.toMatrix().A);keys[name]=key
for hand in ['Port','Starboard']:
 for role,label in [('low','LowSpeed'),('track','Track')]:
  prefix=hand+label+'Brake';dr=d['brakes'][role];bd=d['band_details']['brakes'][role]
  for half in ['Upper','Lower']:
   hp=prefix+half;pose=App.Placement(App.Matrix(*rows[hp+'Band']['frame']))
   revised[hp+'Band']=fresh(role+'_band',pose)
   for i,angle in enumerate(bd['segment_angles_rad'],1):
    sp=pose.multiply(App.Placement(App.Vector(),App.Rotation(App.Vector(0,1,0),-np.degrees(angle))))
    ln=hp+'Segment'+str(i)+'Lining';s=existing(ln);s.Placement=sp;revised[ln]=s
    for j,hole in enumerate(bd['holes'],1):
     n=hp+'Segment'+str(i)+'Rivet'+str(j);rp=sp.multiply(App.Placement(App.Matrix(*hole['frame'])))
     if i==3 and j in [8,9]:s=fresh('long_copper_rivet',rp)
     else:s=existing(n);s.Placement=rp
     revised[n]=s
   add(hp+'AnchorBracket',role+'_bracket',pose)
   for joint in dr['steel_joints']:add(hp+'AnchorSteelRivet'+str(joint['index']),'steel_rivet',pose.multiply(App.Placement(App.Matrix(*joint['frame']))))
   retained=(half==('Lower' if hand=='Port' else 'Upper')) if role=='low' else (half==('Upper' if hand=='Port' else 'Lower'))
   if retained:
    anchor=dr['anchor_radius_mm'];add(hp+'RetainerSpring','spring',pose.multiply(App.Placement(App.Vector(-anchor,dr['spring_y_mm'],0),App.Rotation())))
    sx,sz=dr['retainer_stud_xz_mm'];sign=dr['outward_sign'];y=dr['lug_y_mm']-sign*c['lug_stock']/2
    add(hp+'RetainerRivet',role+'_retainer_rivet',pose.multiply(App.Placement(App.Vector(sx,y,sz),flip if sign<0 else App.Rotation())))
    if role=='low':
     y=dr['lug_y_mm']-c['lug_stock']/2-c['spring_spacer_stock']
     add(hp+'RetainerSpacer','spacer',pose.multiply(App.Placement(App.Vector(sx,y,sz),App.Rotation())))
  up=App.Placement(App.Matrix(*rows[prefix+'UpperBand']['frame']))
  add(prefix+'AnchorPin',role+'_pin',up.multiply(App.Placement(App.Vector(-dr['anchor_radius_mm'],0,0),flip if hand=='Starboard' else App.Rotation())))
all_shapes={n:existing(n) for n in rows if n not in revised};all_shapes.update(revised);all_shapes.update(new)
def bounds(s):
 b=s.copy().cleaned().BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
names=sorted(all_shapes);boxes=np.array([bounds(all_shapes[n]) for n in names]);seen=set();records=[]
# First examine every new joint component against the entire assembly. The
# eventual saved-artifact checker must also include all rephased band components.
for name,one in new.items():
 bb=np.array(bounds(one));possible=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
 for i in possible:
  other=names[i];pair=tuple(sorted([name,other]))
  if name==other or pair in seen:continue
  seen.add(pair);v=one.common(all_shapes[other]).Volume;records.append(dict(first=name,second=other,volume_mm3=v,passed=abs(v)<1e-5))
 Path('progress.json').write_text(json.dumps(records,indent=2)+'\n');print(name,len(records),'pairs',flush=True)
failed=[r for r in records if not r['passed']]
Path('report.json').write_text(json.dumps(dict(passed=not failed,checks=records,failed=failed,new_frames=poses,new_roles=keys,new_count=len(new),revised_count=len(revised)),indent=2)+'\n')
for n,s in new.items():s.exportBrep(str(Path(n+'.brep')))
print('Finished',len(new),'new /',len(revised),'revised;',len(records),'pairs; failures',failed,flush=True)
