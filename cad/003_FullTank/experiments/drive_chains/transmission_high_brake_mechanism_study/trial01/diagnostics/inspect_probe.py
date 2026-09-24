"""Installed diagnostic using saved probe BReps and the qualified parent archive."""
import argparse,base64,itertools,json,sys
from pathlib import Path
from types import SimpleNamespace
import FreeCAD as A
import Part
import fitz
R=Path('/home/cyapp/MarkVIIILiberty');H=R/'cad/003_FullTank/experiments/drive_chains';sys.path[:0]=[str(H),str(H.parents[1])]
from lib.evidence import read,write,sha
from lib.visual_review import shaded
from lib.cad_build import COLORS
p=argparse.ArgumentParser();p.add_argument('--probe',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output;out.mkdir()
c=read(H/'transmission_high_brake_mechanism_study/controls.json')['controls'];d=read(a.probe/'details.json')
parent=H/'transmission_high_brake_front_study/trial01';r=read(parent/'report.json');m=read(parent/'isolated/manifest.json')
assert sha(parent/r['native_file'])==r['native_sha256']==m['native_sha256']
defs={};new={};items={};V=A.Vector
def load(key,path):
 if key not in defs:
  s=Part.Shape();s.read(str(path));defs[key]=s
 return defs[key]
def add(name,key,shape,pose,role):
 s=shape.copy();s.Placement=pose
 return dict(id=name,shape=s,target=SimpleNamespace(Shape=shape),definition=key,system=role,representation='assembly')
COLORS.update(Mechanism=(.57,.64,.70),Spring=(.70,.55,.34),Band=(.40,.56,.59),Lining=(.64,.43,.27),Frame=(.63,.52,.39))
for hand in ['Port','Starboard']:
 prefix=hand+'HighSpeedBrake';base=A.Placement(A.Matrix(*m['assemblies'][prefix]['world']));sf=A.Placement(A.Matrix(*d['screw_frame']))
 frames={role:A.Placement() for role in ['lever_left','lever_right']}
 frames.update({'rivet'+str(i):A.Placement(V(x,0,z),A.Rotation()) for i,(x,z) in enumerate(c['lever_rivet_centers_xz'],1)})
 for role,z in [('screw',0),('washer_b',d['washer_b_distance_mm']),('spring',d['spring_base_distance_mm']),('washer_a',d['washer_a_distance_mm']),('nut',d['lever_upper_seat_distance_mm'])]:
  frames[role]=sf.multiply(A.Placement(V(0,0,z),A.Rotation()))
 orient=A.Rotation() if hand=='Port' else A.Rotation(V(1,0,0),180)
 for joint in ['upper','lower']:
  pivot=A.Placement(V(*d[joint+'_pin_mm']),orient)
  frames[joint+'_pin']=pivot
  frames[joint+'_cotter']=pivot.multiply(A.Placement(V(0,d['cotter_station_y_mm'],0),A.Rotation()))
 for role,pose in frames.items():
  key='rivet' if role.startswith('rivet') else role.split('_')[-1] if role.endswith(('_pin','_cotter')) else role
  shape=load('new_'+key,a.probe/(key+'.brep'));name=prefix+'_'+role
  new[name]=add(name,'new_'+key,shape,base.multiply(pose),'Spring' if role=='spring' else 'Mechanism')
checks=[]
def measure(n1,i1,n2,i2):
 s1,s2=i1['shape'],i2['shape'];b1,b2=s1.BoundBox,s2.BoundBox
 if b1.XMax<b2.XMin-.01 or b2.XMax<b1.XMin-.01 or b1.YMax<b2.YMin-.01 or b2.YMax<b1.YMin-.01 or b1.ZMax<b2.ZMin-.01 or b2.ZMax<b1.ZMin-.01:return
 common=s1.common(s2);volume=abs(common.Volume) if common.Solids else 0.
 row=dict(first=n1,second=n2,common_volume_mm3=volume,common_valid=common.isValid(),distance_mm=s1.distToShape(s2)[0]);checks.append(row)
 if volume>1e-5:print('INTERFERENCE',row,flush=True)
for (n1,i1),(n2,i2) in itertools.combinations(new.items(),2):measure(n1,i1,n2,i2)
print('New/new pairs',len(checks),flush=True)
for row in m['occurrences']:
 definition=m['definitions'][row['definition']]
 if row['definition'] not in defs:assert sha(definition['brep_path'])==definition['brep_sha256']
 s=load(row['definition'],definition['brep_path']);name=row['name'];owners=row['owners']
 role='Lining' if name.endswith('Lining') else 'Frame' if 'TransmissionMountingFrame' in owners else 'Band'
 item=add(name,row['definition'],s,A.Placement(A.Matrix(*row['frame'])),role)
 for nn,ni in new.items():measure(nn,ni,name,item)
 if any(v in owners for v in ['TransmissionHighSpeedBrakes','TransmissionBrakeBands','TransmissionBrakeStops','TransmissionMountingFrame']) or name.endswith('TransmissionCore_high_drum'):items[name]=item
write(out/'interactions.json',dict(parent_native_sha256=r['native_sha256'],checks=checks,interferences=[v for v in checks if v['common_volume_mm3']>1e-5],new_count=len(new),acceptance=False))
print('All nearby pairs',len(checks),flush=True)
items.update(new)
shaded([v for v in items.values() if v['system']!='Frame'],out/'isometric.svg',(1,-.8,.55),'High-speed operating mechanism | first installed diagnostic',context=[v for v in items.values() if v['system']=='Frame'])
focus=[v for k,v in new.items() if k.startswith('Port')]+[v for k,v in items.items() if k.startswith('PortHighSpeedBrake') and k.endswith('FrontEnd')]
shaded(focus,out/'detail.svg',(1,-1,.3),'M355 paired lever, M356 pins and M357/M358/M369 adjustment | estimated profiles')
reg=read(H/'transmission_high_brake_mechanism_study/source_registration.json');source=R/reg['source_image'];assert sha(source)==reg['source_sha256']
cx,cy=reg['center_px'];scale=reg['pixels_per_mm'];center=r['interfaces']['PortHighSpeedBrake']['center_world_mm']
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1445" height="1810">','<rect width="100%" height="100%" fill="white"/>',f'<image x="40" y="70" width="1365" height="1641" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>','<text x="30" y="34" font-family="sans-serif" font-size="23">HB133 | operating mechanism in retained planar registration</text>']
for name,item in items.items():
 if not name.startswith('PortHighSpeedBrake') or 'Rivet' in name or 'Fastener' in name:continue
 color='#b12c1f' if name in new else '#008070'
 for edge in item['shape'].Edges:
  pts=[(40+cx-(v.x-center[0])*scale,70+cy-(v.z-center[2])*scale) for v in edge.discretize(Deflection=.35)]
  svg.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="1.3" opacity=".75"/>')
svg+=['<text x="30" y="1745" font-family="sans-serif" font-size="18">Red: new mechanism; green: retained bands/fittings. Source profiles remain conditional estimates.</text>','<text x="30" y="1780" font-family="sans-serif" font-size="18">Fixed planar diagnostic, not calibrated photographic perspective. No geometry acceptance implied.</text></svg>']
(out/'source.svg').write_text('\n'.join(svg))
with fitz.open(stream=(out/'source.svg').read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(out/'source.png'))
print('Rendered installed diagnostic',flush=True)
