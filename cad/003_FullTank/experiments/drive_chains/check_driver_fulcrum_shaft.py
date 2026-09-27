"""Independently check saved M782 stock and its provisional source-sized retainers."""
import argparse,math,itertools
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);r=s.report;d=r['details'];c=d['controls'];parent=Saved((ROOT/r['parent_native']).parent);out=s.folder/'checks03';out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest);assert all(sha(ROOT/f)==v for f,v in r['input_hashes'].items());checks=[]
def ck(n,ok,**kw):checks.append(dict(name=n,passed=bool(ok),**kw))
def vol(q):return sum(abs(v.Volume) for v in q.Solids)
def cylinders(q,point,axis,radius):return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-point).cross(axis).Length<1e-6]
center=V(*c['center']);shaft=s.world('DriverFulcrumShaft');bb=shaft.BoundBox
ck('Five physical components and two new definitions',len(r['new_occurrences'])==5 and len(r['new_definitions'])==2 and not r['changed_definitions'])
for k in s.manifest['definitions']:
 q=s.definition(k);ck(k+' valid closed single solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
old=parent.definition('Def_TransmissionPin_nut');new=s.definition('Def_TransmissionPin_nut');ck('M313 complete inherited material unchanged',vol(old.cut(new))<1e-5 and vol(new.cut(old))<1e-5)
ck('Printed total length24-3/4in and central diameter1.497in',abs(bb.YLength-24.75*25.4)<1e-6 and abs(bb.XLength-1.497*25.4)<1e-6 and abs(bb.ZLength-1.497*25.4)<1e-6)
fs=cylinders(shaft,center,Y,1.497*25.4/2);ck('Actual full central cylindrical journal',len(fs)==1 and abs(fs[0].Area-2*math.pi*(1.497*25.4/2)*(2*d['shoulder_station_mm']))<1e-5)
for side,sign in [('Port',1),('Starboard',-1)]:
 nut=s.world('DriverFulcrum'+side+'Nut');keeper=s.world('DriverFulcrum'+side+'Keeper');pincenter=center+Y*(sign*d['keeper_station_mm']);seat=center+Y*(sign*d['nut_seat_station_mm']);shoulder=center+Y*(sign*d['shoulder_station_mm'])
 ck(side+' complete threaded stock through nut',vol(Part.makeCylinder(14,14,seat,Y*sign).cut(shaft))<1e-5)
 ck(side+' coaxial nut bore remains open',bool(cylinders(nut,center,Y,14.15)) and vol(nut.common(Part.makeCylinder(14.15,14,seat,Y*sign)))<1e-5)
 ck(side+' full future bearing stock without invented bracket',vol(Part.makeCylinder(14,c['receiver_grip'],shoulder,Y*sign).cut(shaft))<1e-5)
 ck(side+' actual transverse keeper bore',bool(cylinders(shaft,pincenter,X,2.5)) and vol(shaft.common(Part.makeCylinder(2.5,30,pincenter-X*15,X)))<1e-5)
 ck(side+' keeper outside nut and within shaft end',d['keeper_station_mm']-(d['nut_seat_station_mm']+14)>2.38 and d['shaft_half_length_mm']-d['keeper_station_mm']>2.5)
 ck(side+' shaft end hardware has no material intersections',all(vol(one.common(two))<1e-5 for one,two in [(nut,shaft),(keeper,shaft),(keeper,nut)]))
 moved=keeper.copy();moved.translate(Y*5);ck(side+' displaced keeper rejected by stock intersection',vol(moved.common(shaft))>1)
# Check actual straight/arc/tail stock along both legs. The source under-head
# length is an independent fixed38.1mm; no substitution of the63.5mm planet pin.
k=s.definition('Def_DriverFulcrumKeeper_Redo');pc=c['keeper'];half=pc['cotter_center_spacing']/2;wire=(4.7625-pc['cotter_center_spacing'])/2;head=-14-pc['cotter_head_gap'];bend=14+pc['cotter_exit_gap'];rad=pc['cotter_bend_radius'];angle=math.radians(pc['cotter_bend_angle']);straight=bend-head;tail=38.1-straight-rad*angle
ck('Source3/16 x1-1/2in retained with positive bent tails',abs(pc['cotter_diameter']-4.7625)<1e-9 and abs(pc['cotter_length']-38.1)<1e-9 and tail>0)
missing=[]
for sign in [-1,1]:
 for i in range(1,15):
  y=head+straight*i/15;missing.append(vol(Part.makeCylinder(wire-.01,.02,V(0,y-.01,sign*half),Y).cut(k)))
 for i in range(1,15):
  t=angle*i/15;point=V(0,bend+rad*math.sin(t),sign*(half+rad*(1-math.cos(t))));tangent=V(0,math.cos(t),sign*math.sin(t));missing.append(vol(Part.makeCylinder(wire-.01,.02,point-tangent*.01,tangent).cut(k)))
 point=V(0,bend+rad*math.sin(angle),sign*(half+rad*(1-math.cos(angle))));tangent=V(0,math.cos(angle),sign*math.sin(angle))
 for i in range(1,15):
  q=point+tangent*(tail*i/15);missing.append(vol(Part.makeCylinder(wire-.01,.02,q-tangent*.01,tangent).cut(k)))
ck('Complete source-length leg stock in saved keeper',max(missing)<1e-5,maximum_missing_mm3=max(missing))
for n,row in s.rows.items():ck(n+' actual saved frame',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][n]['frame']))<1e-7)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Bare shaft and retainers only. Future receiver grip is an empty interface, not an installed support. No mounting or historical shaft-end qualification.')
write(out/'independent_checks.json',result);print(len(checks),'checks',result['passed'],flush=True)
for v in checks:
 if not v['passed']:print(v,flush=True)
assert result['passed']
