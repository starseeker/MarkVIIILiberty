"""Independent saved-native checks for high-speed brake operating components."""
import argparse,math,sys
from pathlib import Path
import numpy as np
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');source=ROOT/r['source_native'];old=read(source.parent/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256'] and sha(source)==r['source_native_sha256']==old['native_sha256']
rows,prior=[{v['name']:v for v in t['occurrences']} for t in [m,old]];c=r['controls'];V=App.Vector;checks=[];cache={}
def ck(name,passed,**details):
 checks.append(dict(name=name,passed=bool(passed),**details));write(out/'mechanism_check_progress.json',dict(completed=len(checks),last=name,failed=[v['name'] for v in checks if not v['passed']]))
def definition(key):
 if key not in cache:
  d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[key]=s
 return cache[key].copy()
def world(name):
 row=rows[name];s=definition(row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def component(role):return definition('Def_HighBrakeMechanism_'+role)
def cylinders(s,radius):return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6]
def planes(s,point,normal):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(normal).Length<1e-7 and abs((f.CenterOfMass-point).dot(normal))<1e-6]
def covered(fs,gs):
 if not fs or not gs:return False
 support=Part.makeCompound(gs)
 return all(not f.cut(support).Faces and abs(f.cut(support).Area)<1e-5 for f in fs)
def contact(fs,gs):return sum(f.common(g).Area for f in fs for g in gs)
suffixes=['LeverLeft','LeverRight']+['LeverRivet'+str(i) for i in range(1,5)]+['AdjustingScrew','AdjustingNut','AdjustingSpring','UpperSpringWasher','LowerSpringWasher']+[j+'FreeEnd'+k for j in ['Upper','Lower'] for k in ['Pin','Cotter']]
expected={hand+'HighSpeedBrake'+suffix for hand in ['Port','Starboard'] for suffix in suffixes}
ck('30 added physical components and ten definitions',set(rows)-set(prior)==expected and len(rows)==3121 and len(m['definitions'])==529)
ck('Inherited occurrence definitions frames and owners retained',all(v['definition']==rows[n]['definition'] and v['owners']==rows[n]['owners'] and max(abs(x-y) for x,y in zip(v['frame'],rows[n]['frame']))<1e-7 for n,v in prior.items()))
ck('New composed frames match declared joints',all(rows[n]['definition']==v['definition'] and rows[n]['owners']==v['owners'] and max(abs(x-y) for x,y in zip(v['frame'],rows[n]['frame']))<1e-7 for n,v in r['expected_new_occurrences'].items()))
ck('No inherited definitions intentionally revised',not r['changed_definitions'])
ck('Eight new groups and retained old assembly frames/children',len(m['assemblies'])==322 and all(max(abs(x-y) for x,y in zip(g['world'],m['assemblies'][n]['world']))<1e-7 and max(abs(x-y) for x,y in zip(g['local'],m['assemblies'][n]['local']))<1e-7 and set(m['assemblies'][n]['children'])==set(g['children'])|set(r['added_children'].get(n,[])) for n,g in old['assemblies'].items()))
for key in r['new_definitions']:
 s=definition(key);ck(key+' valid closed identity solid',s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.Placement.isIdentity() and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
for role,diameter in [('washer_a',17.4625),('washer_b',20.6375)]:
 fs=cylinders(component(role),diameter/2);ck(role+' printed bore diameter and through stock',len(fs)==1 and abs(fs[0].optimalBoundingBox(False,False).ZLength-c['washer_stock'])<1e-6)
rv=component('rivet');fs=cylinders(rv,4.7625);bb=fs[0].optimalBoundingBox(False,False);tail=rv.common(Part.makeBox(60,60,60,V(-30,bb.YMax,-30)));stock=bb.YLength+tail.Volume/(math.pi*4.7625**2)
ck('Printed 3/8 by 1-3/8 rivet stock conserved under selected length datum',len(fs)==1 and abs(stock-34.925)<1e-4,derived_stock_mm=stock)
for role,ylo,yhi in [('left',-c['lever_width']/2,0),('right',0,c['lever_width']/2)]:
 s=component('lever_'+role);b=s.optimalBoundingBox(False,False)
 ck(role+' distinct half-width member with genuine curved B-spline boundary',abs(b.YMin-ylo)<1e-6 and abs(b.YMax-yhi)<1e-6 and any(isinstance(e.Curve,Part.BSplineCurve) for e in s.Edges))
for hand in ['Port','Starboard']:
 prefix=hand+'HighSpeedBrake';center=V(*r['interfaces'][prefix]['center_world_mm']);axis=V(0,1,0);levers=[world(prefix+'Lever'+k) for k in ['Left','Right']]
 joined=Part.makeCompound(levers);seam=center
 ck(prefix+' paired members contact across their common plane',contact(planes(levers[0],seam,axis),planes(levers[1],seam,axis))>1000)
 for i in range(1,5):
  s=world(prefix+'LeverRivet'+str(i));areas=[]
  for sign,lever in [(-1,levers[0]),(1,levers[1])]:
   point=center+V(0,sign*c['lever_width']/2,0);areas.append(contact(planes(s,point,axis),planes(lever,point,axis)))
  ck(prefix+' joining rivet '+str(i)+' has head and tail bearing',min(areas)>10,areas_mm2=areas)
 for joint,band,receiver in [('Upper','Long',joined),('Lower','Short',world(prefix+'AdjustingScrew'))]:
  pin=world(prefix+joint+'FreeEndPin');cotter=world(prefix+joint+'FreeEndCotter');end=world(prefix+band+'FrontEnd')
  pivot=center+V(r['front_controls']['pin_x'],0,r['front_controls']['upper_pin_z' if joint=='Upper' else 'lower_pin_z'])
  bore=r['front_controls']['pin_bore_radius'];receivers=cylinders(receiver,bore)
  # The lever also has a separate, same-diameter control-rod eye below the drum.
  # Select the upper lever eye spatially, then test its actual axis independently.
  if joint=='Upper':receivers=[f for f in receivers if f.Surface.Center.z>center.z]
  faces=cylinders(end,bore)+receivers;shanks=cylinders(pin,c['pin_diameter']/2)
  ck(prefix+joint+' pin and receiving bores share actual axis',len(receivers)==(2 if joint=='Upper' else 1) and len(faces)>=3 and all(f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-pivot).cross(axis).Length<1e-6 for f in faces) and bool(shanks) and all((f.Surface.Center-pivot).cross(axis).Length<1e-6 for f in shanks))
  moved=pin.copy();direction=1 if hand=='Port' else -1;moved.translate(V(0,direction*5,0))
  ck(prefix+joint+' head arrests axial passage',moved.common(end).Volume>1)
  moved=cotter.copy();moved.translate(V(0,-direction*5,0))
  ck(prefix+joint+' cotter arrests opposite withdrawal',moved.common(end).Volume>1)
 sf=App.Placement(App.Matrix(*rows[prefix+'AdjustingScrew']['frame']));normal=sf.Rotation.multVec(V(0,0,1));point=lambda z:sf.multVec(V(0,0,z))
 spring=world(prefix+'AdjustingSpring');lower=world(prefix+'LowerSpringWasher');upper=world(prefix+'UpperSpringWasher');screw=world(prefix+'AdjustingScrew');nut=world(prefix+'AdjustingNut')
 start=c['screw_shoulder_distance']+c['washer_stock'];finish=start+c['spring_installed_height']
 for label,z,washer in [('lower',start,lower),('upper',finish,upper)]:
  fs=planes(spring,point(z),normal);gs=planes(washer,point(z),normal)
  ck(prefix+label+' complete ground spring end supported by washer',covered(fs,gs))
  shifted=washer.copy();shifted.translate(normal*.1)
  ck(prefix+label+' displaced washer fails support',not covered(fs,planes(shifted,point(z),normal)))
 for label,one,two,z in [('screw shoulder',screw,lower,c['screw_shoulder_distance']),('lower lever seat',upper,joined,finish+c['washer_stock']),('upper lever seat',nut,joined,c['lever_upper_seat_distance'])]:
  area=contact(planes(one,point(z),normal),planes(two,point(z),normal));ck(prefix+label+' positive planar load-path contact',area>50,area_mm2=area)
 shaft=cylinders(screw,c['screw_radius']);bores=cylinders(joined,c['lever_screw_bore_radius'])
 ck(prefix+' adjusting screw and split lever passage coaxial',bool(shaft) and bool(bores) and all(f.Surface.Axis.cross(normal).Length<1e-7 and (f.Surface.Center-point(0)).cross(normal).Length<1e-6 for f in shaft+bores))
 tip=c['screw_length'];nut_top=c['lever_upper_seat_distance']+c['nut_neck_length']+c['nut_wing_stock']+c['nut_hex_stock']
 ck(prefix+' adjusting screw extends beyond nut and through both washers',tip>nut_top and min(f.optimalBoundingBox(False,False).ZLength for f in cylinders(component('screw'),c['screw_radius']))>c['spring_installed_height'],nominal_tip_protrusion_mm=tip-nut_top)
all_shapes={n:world(n) for n in rows};names=sorted(all_shapes);boxes=np.array([[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax] for s in [all_shapes[n] for n in names]])
pairs=set();collisions=[];invalid=[]
for name in expected:
 s=all_shapes[name];b=s.BoundBox;lo=np.array([b.XMin,b.YMin,b.ZMin]);hi=np.array([b.XMax,b.YMax,b.ZMax])
 for i in np.where(np.all(boxes[:,:3]<=hi+1e-7,axis=1)&np.all(boxes[:,3:]>=lo-1e-7,axis=1))[0]:
  if name!=names[i]:pairs.add(tuple(sorted([name,names[i]])))
for i,(one,two) in enumerate(sorted(pairs)):
 common=all_shapes[one].common(all_shapes[two]);v=sum(abs(s.Volume) for s in common.Solids)
 if not common.isValid():invalid.append([one,two])
 if v>1e-5:collisions.append(dict(first=one,second=two,volume_mm3=v))
 if i%20==0:write(out/'mechanism_interference_progress.json',dict(completed=i,total=len(pairs),collisions=collisions,invalid=invalid))
ck('No new material interference with development assembly',not collisions and not invalid,pairs=len(pairs),collisions=collisions,invalid=invalid)
result=dict(passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],checker_sha256=sha(Path(__file__)),checks=checks,development_pairs=len(pairs),scope='Saved hierarchy, counts, printed washer bores/rivet stock, static pin retention, actual bearing contacts, complete ground spring end support and neighboring material. Preservation, STEP, standard context, source review, rebuild and variation remain separate gates.',packet_complete=False,installation_qualified=False,standard_assembly_modified=False)
write(out/'independent_checks.json',result);print('Checks',len(checks),'pairs',len(pairs),'passed',result['passed'],flush=True)
for v in checks:
 if not v['passed']:print(v,flush=True)
assert result['passed']
