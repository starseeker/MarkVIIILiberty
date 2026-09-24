"""Independent checks of saved forward fittings, lining hardware and retained interfaces."""
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
rows,prior=[{v['name']:v for v in t['occurrences']} for t in [m,old]];c=r['controls'];bc=r['band_controls'];V=App.Vector;checks=[];cache={}
def ck(name,passed,**details):
 checks.append(dict(name=name,passed=bool(passed),**details));write(out/'front_check_progress.json',dict(completed=len(checks),last=name,failed=[v['name'] for v in checks if not v['passed']]))
def definition(key,previous=False):
 k=(key,previous)
 if k not in cache:
  d=(old if previous else m)['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[k]=s
 return cache[k].copy()
def world(name):
 row=rows[name];s=definition(row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def cylinders(s,radius):return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6]
def coverage(fs,gs):
 result=[]
 for f in fs:
  matching=[g for g in gs if abs(f.Surface.Radius-g.Surface.Radius)<1e-6 and f.Surface.Axis.cross(g.Surface.Axis).Length<1e-7 and (f.Surface.Center-g.Surface.Center).cross(g.Surface.Axis).Length<1e-6]
  if not matching:result.append(False);continue
  missing=f.cut(Part.makeCompound(matching));result.append(not missing.Faces and abs(missing.Area)<1e-5)
 return bool(result) and all(result)
def contact(one,two,kind):
 area=0.
 for f in one.Faces:
  if not isinstance(f.Surface,kind):continue
  for g in two.Faces:
   if not isinstance(g.Surface,kind):continue
   a,b=f.Surface,g.Surface
   if kind is Part.Plane:
    if f.normalAt(0,0).cross(g.normalAt(0,0)).Length>1e-7 or abs((f.CenterOfMass-g.CenterOfMass).dot(f.normalAt(0,0)))>1e-6:continue
   else:
    if a.Axis.cross(b.Axis).Length>1e-7 or (a.Center-b.Center).cross(a.Axis).Length>1e-6:continue
    if kind is Part.Cylinder and abs(a.Radius-b.Radius)>1e-6:continue
    if kind is Part.Cone and abs(abs(a.SemiAngle)-abs(b.SemiAngle))>1e-7:continue
   if f.distToShape(g)[0]<1e-6:area+=f.common(g).Area
 return area
new=set(rows)-set(prior)
expected={hand+'HighSpeedBrake'+role+suffix for hand in ['Port','Starboard'] for role in ['Long','Short'] for suffix in ['FrontEnd']+['FrontSteelRivet'+str(i) for i in range(1,4)]+['LiningFastener'+str(i) for i in range(1,13 if role=='Long' else 7)]}
ck('52 added physical components and eight definitions',new==expected and len(rows)==3091 and len(m['definitions'])==519)
ck('All inherited occurrence frames and owners preserved',all(v['definition']==rows[n]['definition'] and v['owners']==rows[n]['owners'] and max(abs(x-y) for x,y in zip(v['frame'],rows[n]['frame']))<1e-7 for n,v in prior.items()))
ck('All new composed frames match declared joints',all(rows[n]['definition']==v['definition'] and rows[n]['owners']==v['owners'] and max(abs(x-y) for x,y in zip(v['frame'],rows[n]['frame']))<1e-7 for n,v in r['expected_new_occurrences'].items()))
ck('Exactly three inherited definitions intentionally revised',set(r['changed_definitions'])=={'Def_HighBrake_long_band','Def_HighBrake_short_band','Def_HighBrake_anchor_end'})
ck('Eight new groups; all old assembly frames and expected children retained',len(m['assemblies'])==314 and all(
 max(abs(x-y) for x,y in zip(g['world'],m['assemblies'][n]['world']))<1e-7 and max(abs(x-y) for x,y in zip(g['local'],m['assemblies'][n]['local']))<1e-7 and
 set(m['assemblies'][n]['children'])==set(g['children']) | (set(r['new_definitions']) if n=='Definitions' else {n.replace('Assembly','FrontJoint'),n.replace('Assembly','LiningFasteners')} if n.endswith(('HighSpeedBrakeLongAssembly','HighSpeedBrakeShortAssembly')) else set()) for n,g in old['assemblies'].items()))
for key in r['new_definitions']+r['changed_definitions']:
 s=definition(key);ck(key+' valid closed identity solid',s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.Placement.isIdentity() and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
for role in ['long','short']:
 key='Def_HighBrake_'+role+'_lining';ck(role+' printed lining BRep and metadata unchanged',m['definitions'][key]['brep_sha256']==old['definitions'][key]['brep_sha256'] and m['definitions'][key]['properties']==old['definitions'][key]['properties'])
for role,diameter,stock in [('steel_rivet',7.9375,28.575),('lining_normal_075',6.35,19.05),('lining_normal_1',6.35,25.4),('lining_front_1',6.35,25.4),('lining_anchor_125',6.35,31.75)]:
 s=definition('Def_HighBrakeFront_'+role);faces=cylinders(s,diameter/2);ck(role+' source shank diameter',len(faces)==1)
 b=faces[0].optimalBoundingBox(False,False);cap=s.common(Part.makeBox(60,60,60,V(-30,-30,b.ZMax)));length=b.ZLength+cap.Volume/(math.pi*(diameter/2)**2)
 ck(role+' source stock retained in shank and formed tail',abs(length-stock)<1e-4,inferred_stock_mm=length)
brass=definition('Def_HighBrakeFront_lining_brass');b=brass.optimalBoundingBox(False,False)
ck('Source quarter-inch by three-quarter-inch brass screw',len(cylinders(brass,3.175))==1 and abs(b.ZLength-19.05)<1e-6)
slot=Part.makeBox(2,1,1,V(-1,-.5,0));ck('Brass driving slot open',abs(brass.common(slot).Volume)<1e-5)
outer=bc['inner_radius']+bc['lining_stock']+bc['steel_stock'];joint_contacts=[]
for hand in ['Port','Starboard']:
 prefix=hand+'HighSpeedBrake';anchor=world(prefix+'AnchorEnd')
 for role in ['Long','Short']:
  pfx=prefix+role;ear=world(pfx+'FrontEnd');band=world(pfx+'Band');lining=world(pfx+'Lining')
  ck(pfx+' complete curved fitting bearing',coverage(cylinders(ear,outer),cylinders(band,outer)))
  shifted=ear.copy();shifted.translate(V(.05,0,0));ck(pfx+' shifted fitting loses complete bearing',not coverage(cylinders(shifted,outer),cylinders(band,outer)))
  fs=cylinders(ear,c['pin_bore_radius']);ck(pfx+' two coaxial pin bores',len(fs)==2 and all(f.Surface.Axis.cross(V(0,1,0)).Length<1e-7 for f in fs))
  center=fs[0].Surface.Center;center.y=r['interfaces'][prefix]['center_world_mm'][1]
  body=Part.makeCylinder(c['receiver_eye_radius'],c['receiver_width'],center+V(0,-c['receiver_width']/2,0),V(0,1,0))
  ck(pfx+' complete reserved receiver envelope clear',abs(ear.common(body).Volume)<1e-5)
  rim=Part.makeCylinder(c['pin_bore_radius']+1,c['lug_stock']-.4,center+V(0,c['fork_gap']/2+.2,0),V(0,1,0)).cut(Part.makeCylinder(c['pin_bore_radius']+.2,c['lug_stock']+1,center+V(0,c['fork_gap']/2,0),V(0,1,0)))
  ck(pfx+' receiving wall remains around pivot bore',not rim.cut(ear).Faces)
  for n in range(1,4):
   name=pfx+'FrontSteelRivet'+str(n);s=world(name);head=contact(s,band,Part.Cone)+contact(s,ear,Part.Cone);tail=contact(s,ear,Part.Plane)
   ck(name+' head and formed tail seats',head>1 and tail>1,head_area_mm2=head,tail_area_mm2=tail);joint_contacts.append(dict(name=name,head_mm2=head,tail_mm2=tail))
  counts={}
  for n in range(1,13 if role=='Long' else 7):
   name=pfx+'LiningFastener'+str(n);row=rows[name];key=row['definition'].replace('Def_HighBrakeFront_','');counts[key]=counts.get(key,0)+1;s=world(name)
   head=contact(s,lining,Part.Cone)
   receiver=ear if key in ['lining_front_1','lining_brass'] else anchor if key=='lining_anchor_125' else band
   if key=='lining_brass':
    pose=App.Placement(App.Matrix(*row['frame']));wall=Part.makeCylinder(bc['steel_hole_radius']+1.25,2,V(0,0,15)).cut(Part.makeCylinder(bc['steel_hole_radius']+.5,4,V(0,0,14)));wall.Placement=pose
    tail=1 if not wall.cut(receiver).Faces else 0
   else:tail=contact(s,receiver,Part.Plane)
   ck(name+' lining head and receiving seat',head>1 and tail>.1,head_area_mm2=head,tail_contact_or_wall=tail);joint_contacts.append(dict(name=name,head_mm2=head,tail_contact_or_wall=tail))
  wanted={'lining_front_1':2,'lining_normal_1':9,'lining_normal_075':1} if role=='Long' else {'lining_anchor_125':1,'lining_normal_1':3,'lining_front_1':1,'lining_brass':1}
  ck(pfx+' complete catalogue fastener allocation',counts==wanted,counts=counts)
# Check all changed/new material against every development occurrence.
all_shapes={n:world(n) for n in rows};names=sorted(all_shapes);boxes=np.array([[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax] for s in [all_shapes[n] for n in names]])
pairs=set();collisions=[];invalid=[]
for name in r['affected_occurrences']:
 s=all_shapes[name];b=s.BoundBox;lo=np.array([b.XMin,b.YMin,b.ZMin]);hi=np.array([b.XMax,b.YMax,b.ZMax])
 for i in np.where(np.all(boxes[:,:3]<=hi+1e-7,axis=1)&np.all(boxes[:,3:]>=lo-1e-7,axis=1))[0]:
  if name!=names[i]:pairs.add(tuple(sorted([name,names[i]])))
for i,(one,two) in enumerate(sorted(pairs)):
 common=all_shapes[one].common(all_shapes[two]);v=sum(abs(s.Volume) for s in common.Solids)
 if not common.isValid():invalid.append([one,two])
 if v>1e-5:collisions.append(dict(first=one,second=two,volume_mm3=v))
 if i%20==0:write(out/'front_interference_progress.json',dict(completed=i,total=len(pairs),collisions=collisions,invalid=invalid))
ck('No changed or new material interference',not collisions and not invalid,pairs=len(pairs),collisions=collisions,invalid=invalid)
result=dict(passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],checker_sha256=sha(Path(__file__)),checks=checks,development_pairs=len(pairs),joint_contacts=joint_contacts,scope='Forward fitting stock, fastener counts, bearing interfaces, hierarchy and development material. Preservation, STEP, complete lining support, rebuild and variation remain separate gates.',packet_complete=False,installation_qualified=False,standard_assembly_modified=False)
write(out/'independent_checks.json',result);print('Checks',len(checks),'pairs',len(pairs),'passed',result['passed'],flush=True)
for v in checks:
 if not v['passed']:print(v,flush=True)
assert result['passed']
