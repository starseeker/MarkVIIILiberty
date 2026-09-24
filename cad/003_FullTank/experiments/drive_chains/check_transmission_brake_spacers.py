"""Independent checks of saved spacer stock, seats, ownership and neighbors."""
import argparse,math
from pathlib import Path
import sys
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');source=ROOT/r['source_native'];old=read(source.parent/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256'] and sha(source)==old['native_sha256']==r['source_native_sha256']
rows={v['name']:v for v in m['occurrences']};prior={v['name']:v for v in old['occurrences']};c=r['controls'];cache={};world={};checks=[]
def ck(name,passed,**details):checks.append(dict(name=name,passed=bool(passed),**details))
def frame(values):return App.Placement(App.Matrix(*values))
for key,d in m['definitions'].items():
 f=Path(d['brep_path']);assert sha(f)==d['brep_sha256'];s=Part.Shape();s.read(str(f));cache[key]=s
for name,row in rows.items():
 s=cache[row['definition']].copy();s.Placement=frame(row['frame']);world[name]=s
new_names={hand+role+'BrakeAdjustingSpringSpacer' for hand in ['Port','Starboard'] for role in ['LowSpeed','Track']}
ck('Four catalogued spacers, one definition, unchanged assembly count',len(rows)==len(prior)+4 and set(rows)-set(prior)==new_names and len(m['definitions'])==len(old['definitions'])+1 and len(m['assemblies'])==len(old['assemblies']))
frame_errors={n:max(abs(x-y) for x,y in zip(row['frame'],prior[n]['frame'])) for n,row in rows.items() if n in prior}
ck('Every inherited occurrence retains definition, composed frame and ownership',all(row['definition']==prior[n]['definition'] and row['owners']==prior[n]['owners'] and frame_errors[n]<1e-7 for n,row in rows.items() if n in prior),max_frame_error=max(frame_errors.values()))
for name,g in old['assemblies'].items():
 now=m['assemblies'][name];extra=[n for n in new_names if rows[n]['owners'][-1]==name]
 if name=='Definitions':extra.append('Def_BrakeSpringSpacer')
 ck('Assembly '+name,all(abs(x-y)<1e-7 for x,y in zip(g['world'],now['world'])) and sorted(now['children'])==sorted(g['children']+extra))
for key in ['Def_BrakeSpringSpacer','Def_BrakeFront_spring']:
 s=cache[key];ck(key+' valid closed solid in identity frame',s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.Placement.isIdentity() and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
spacer=cache['Def_BrakeSpringSpacer'];box=spacer.optimalBoundingBox(False,False);outer=c['spacer_outer_diameter']/2;inner=c['spacer_bore_radius'];length=c['spacer_length']
radii=sorted({round(f.Surface.Radius,9) for f in spacer.Faces if isinstance(f.Surface,Part.Cylinder)})
ck('Actual cylindrical stock and clear bore',radii==sorted([round(inner,9),round(outer,9)]) and abs(box.ZMin)<1e-5 and abs(box.ZMax-length)<1e-5 and abs(spacer.Volume-math.pi*(outer**2-inner**2)*length)<1e-5,radii_mm=radii,axial_bounds_mm=[box.ZMin,box.ZMax])
void=Part.makeCylinder(inner-.01,length+2,App.Vector(0,0,-1));envelope=Part.makeCylinder(outer,length)
ck('Through bore is empty and all spacer material stays within stock',abs(spacer.common(void).Volume)<1e-5 and abs(spacer.cut(envelope).Volume)<1e-5)
blocked=spacer.fuse(Part.makeCylinder(inner,1,App.Vector(0,0,length/2)))
ck('Blocked-bore negative is rejected',blocked.common(void).Volume>1)
old_spring=Part.Shape();os=old['definitions']['Def_BrakeFront_spring'];assert sha(Path(os['brep_path']))==os['brep_sha256'];old_spring.read(os['brep_path'])
old_box=old_spring.optimalBoundingBox(False,False);spring=cache['Def_BrakeFront_spring'];sb=spring.optimalBoundingBox(False,False)
height=old_box.ZMax-old_box.ZMin-length
ck('Saved spring shortens by spacer stock while retaining shoulder origin',abs(sb.ZMin-old_box.ZMin)<1e-5 and abs(sb.ZLength-height)<1e-5,old_height_mm=old_box.ZLength,new_height_mm=sb.ZLength)
# Whole-cylinder material envelope plus positive void around the central screw.
shaft_radius=r['spring_controls']['screw_radius'];core=Part.makeCylinder(shaft_radius+.05,sb.ZLength+2,App.Vector(0,0,-1))
ck('Spring retains central screw clearance',abs(spring.common(core).Volume)<1e-5)
def planar_contact(one,two):
 area=0.
 for f in one.Faces:
  if not isinstance(f.Surface,Part.Plane):continue
  for g in two.Faces:
   if not isinstance(g.Surface,Part.Plane):continue
   if abs(abs(f.normalAt(0,0).dot(g.normalAt(0,0)))-1)>1e-7:continue
   if f.distToShape(g)[0]>1e-6:continue
   area+=f.common(g).Area
 return area
contacts=[]
for name in sorted(new_names):
 prefix=name[:-len('AdjustingSpringSpacer')];oldrow=prior[prefix+'AdjustingSpring'];expected=frame(oldrow['frame']).multiply(App.Placement(App.Vector(0,0,height),App.Rotation()))
 row=rows[name];error=max(abs(x-y) for x,y in zip(row['frame'],expected.toMatrix().A))
 ck(name+' independent spacer station and owner',error<1e-5 and row['definition']=='Def_BrakeSpringSpacer' and row['owners']==oldrow['owners'],frame_error_mm=error)
 screw=world[prefix+'AdjustingScrew'];coil=world[prefix+'AdjustingSpring'];sp=world[name];swivel=world[prefix+'Swivel'];nut=world[prefix+'AdjustingNut']
 areas={k:planar_contact(x,y) for k,x,y in [('shoulder_spring',screw,coil),('spring_spacer',coil,sp),('spacer_swivel',sp,swivel),('swivel_nut',swivel,nut)]}
 ck(name+' actual planar bearing areas',all(x>1 for x in areas.values()),areas_mm2=areas)
 axis=frame(oldrow['frame']).Rotation.multVec(App.Vector(0,0,1));moved=sp.copy();moved.translate(axis*.1)
 ck(name+' displaced-spacer negative loses coil seat',planar_contact(coil,moved)<1e-5)
 ck(name+' screw bore radial clearance',sp.distToShape(screw)[0]>0.1,clearance_mm=sp.distToShape(screw)[0])
 contacts.append(dict(occurrence=name,areas_mm2=areas))
affected=new_names|{n[:-len('Spacer')] for n in new_names};pairs=set();collisions=[];invalid=[]
def overlaps(a,b):return all(min(getattr(a,k+'Max'),getattr(b,k+'Max'))-max(getattr(a,k+'Min'),getattr(b,k+'Min'))>1e-6 for k in ['X','Y','Z'])
for name in affected:
 for other,shape in world.items():
  if name!=other and overlaps(world[name].BoundBox,shape.BoundBox):pairs.add(tuple(sorted([name,other])))
for i,(left,right) in enumerate(sorted(pairs),1):
 common=world[left].common(world[right]);volume=sum(abs(s.Volume) for s in common.Solids)
 if not common.isNull() and not common.isValid():invalid.append([left,right])
 if volume>1e-5:collisions.append(dict(left=left,right=right,volume_mm3=volume))
 if i%10==0:write(out/'spacer_check_progress.json',dict(done=i,total=len(pairs),collisions=collisions))
ck('No new development-context material overlaps or invalid intersections',not collisions and not invalid,pair_count=len(pairs),collisions=collisions,invalid=invalid)
result=dict(passed=all(x['passed'] for x in checks),native_sha256=r['native_sha256'],checker_sha256=sha(Path(__file__)),checks=checks,contacts=contacts,changed_occurrences=sorted(affected),development_pairs=len(pairs),
 scope='Local spacer/spring stock, through bore, saved seats, ownership, inherited frames and development neighbors. Not historical identity/placement, full service, STEP or complete tank qualification.',historical_geometry_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',result);print('Checks',len(checks),'pairs',len(pairs),'passed',result['passed'],flush=True)
for item in checks:
 if not item['passed']:print(item,flush=True)
assert result['passed']
