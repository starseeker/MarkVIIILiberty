"""Independent saved-solid checks for the lower bearing/stop mounting trial.

Checks source-length thread envelopes and protected material, not thread strength
or historical authenticity. Nominal cylindrical threads remain a representation.
"""
import argparse
from pathlib import Path
import sys
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;sys.path[:0]=[str(H),str(H.parents[1])]
from lib.evidence import read,write,sha
V=App.Vector
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
parent=read(H/'transmission_brake_front_study/trial01/isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};cache={};checks=[];details={}
def shape(manifest,key):
    row=manifest['definitions'][key];path=Path(row['brep_path']);assert sha(path)==row['brep_sha256']
    if row['brep_sha256'] not in cache:
        s=Part.Shape();s.read(str(path));cache[row['brep_sha256']]=s
    return cache[row['brep_sha256']].copy()
def world(name):
    row=rows[name];s=shape(m,row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def material(s):
    return dict(faces=len(s.Faces),solids=len(s.Solids),volume_mm3=sum(abs(x.Volume) for x in s.Solids),
                valid=s.isNull() or s.isValid())
def empty(s):
    d=material(s);return d,d['valid'] and d['faces']==0 and d['solids']==0
def same(name,a,b):
    da,pa=empty(a.cut(b));db,pb=empty(b.cut(a))
    checks.append(dict(name=name,missing=da,added=db,passed=pa and pb))
def planar_contact(a,b):
    area=0.
    for f in a.Faces:
        if not isinstance(f.Surface,Part.Plane):continue
        for g in b.Faces:
            if not isinstance(g.Surface,Part.Plane):continue
            if abs(abs(f.normalAt(0,0).dot(g.normalAt(0,0)))-1)>1e-7 or f.distToShape(g)[0]>1e-6:continue
            area+=f.common(g).Area
    return area

for role in ['cap','bracket']:
    key='Def_FixedBearing_inner_'+role;old=shape(parent,key);new=shape(m,key)
    checks.append(dict(name=role+'_solid',passed=new.isValid() and len(new.Solids)==1 and new.isClosed()
        and new.getTolerance(1)<=1e-4,max_tolerance_mm=new.getTolerance(1)))
    # Preserve complete old upper, remote lower/frame and rear regions. The
    # allowed local replacement boundary is explicit, not an expanded tolerance.
    for name,witness in [('upper',box(-400,400,-200,200,-65,500)),
        ('frame_bottom',box(-400,400,-200,200,-500,-200)),('rear',box(-400,-160,-200,200,-500,500))]:
        same(role+'_'+name,old.common(witness),new.common(witness))
    socket=Part.makeCylinder(69.65,95.74285714285714,V(0,-47.87142857142857,0),V(0,1,0))
    d,passed=empty(new.common(socket));checks.append(dict(name=role+'_socket_void',material=d,passed=passed))
    ring=Part.makeCylinder(70.65,93.74285714285714,V(0,-46.87142857142857,0),V(0,1,0)).cut(socket)
    same(role+'_complete_socket_support',old.common(ring),new.common(ring))
    for sign in [-1,1]:
        y=sign*30.87142857142857
        point=V(20 if role=='cap' else -50,y,-84)
        checks.append(dict(name=role+'_old_lower_bore_filled_'+str(sign),point_mm=list(point),
                           passed=new.isInside(point,1e-7,True)))

counts={key:sum(row['definition']==key for row in rows.values()) for key in ['Def_TransmissionCap_MX9','Def_TransmissionCap_MX10','Def_TransmissionCap_MX36']}
checks.append(dict(name='source_stud_counts',actual=counts,passed=list(counts.values())==[8,4,4]))
for hand in ['Port','Starboard']:
    base=rows[hand+'FixedBearing_inner_bracket']['frame'];bracket=world(hand+'FixedBearing_inner_bracket')
    cap=world(hand+'FixedBearing_inner_cap');stop=world(hand+'BrakeStopBracket')
    mount_index=1 if hand=='Port' else 3
    for i in range(1,5):
        name=hand+'FixedBearing_inner_Stud'+str(i).zfill(2);row=rows[name+'_Stud']
        lower=i in [1,3];mark='MX36' if lower else 'MX10';length=139.7 if lower else 123.825
        s=shape(m,row['definition']);b=s.BoundBox
        checks.append(dict(name=name+'_source_length_allocation',length_mm=b.XLength,mark=row['definition'],
            passed=row['definition']=='Def_TransmissionCap_'+mark and abs(b.XLength-length)<1e-6))
        pose=App.Placement(App.Matrix(*row['frame']))
        # The complete printed 1.5-inch coarse-thread interval must be enclosed
        # by a continuous receiver annulus outside the nominal pilot clearance.
        outer=Part.makeCylinder(12,38.1,V(),V(1,0,0));inner=Part.makeCylinder(10.025,40.1,V(-1,0,0),V(1,0,0))
        witness=outer.cut(inner);witness.Placement=pose
        miss,passed=empty(witness.cut(bracket))
        checks.append(dict(name=name+'_coarse_thread_enclosure',missing=miss,passed=passed))
        nut=world(name+'_Nut');support=stop if i==mount_index else cap
        area=planar_contact(nut,support)
        checks.append(dict(name=name+'_nut_bearing',area_mm2=area,passed=area>100))
        # Three non-collinear frame points retain the nut/cotter relationship
        # already qualified on this unchanged hardware definition.
        source_rows={v['name']:v for v in parent['occurrences']}
        old_nut=App.Placement(App.Matrix(*source_rows[name+'_Nut']['frame']))
        old_cotter=App.Placement(App.Matrix(*source_rows[name+'_Cotter']['frame']))
        new_nut=App.Placement(App.Matrix(*rows[name+'_Nut']['frame']))
        new_cotter=App.Placement(App.Matrix(*rows[name+'_Cotter']['frame']))
        delta=max(abs(x-y) for x,y in zip(old_nut.inverse().multiply(old_cotter).toMatrix().A,new_nut.inverse().multiply(new_cotter).toMatrix().A))
        checks.append(dict(name=name+'_nut_cotter_relative_frame',error=delta,passed=delta<1e-7))
        if i==mount_index:
            moved=witness.copy();moved.translate(V(10,0,0));d,contained=empty(moved.cut(bracket))
            checks.append(dict(name=hand+'_short_engagement_negative',missing=d,passed=not contained))
    area=planar_contact(stop,cap)
    checks.append(dict(name=hand+'_stop_cap_bearing',area_mm2=area,passed=area>500))
    lifted=stop.copy();lifted.translate(V(.1,0,0));area=planar_contact(lifted,cap)
    checks.append(dict(name=hand+'_lifted_stop_negative',area_mm2=area,passed=area<1e-6))

result=dict(native_sha256=m['native_sha256'],checker_sha256=sha(Path(__file__)),checks=checks,
    passed=all(c['passed'] for c in checks),scope='Lower bearing material, nominal thread enclosure and static bearing-contact checks; no thread strength, removal path or historical qualification.',
    historical_geometry_qualified=False,installation_qualified=False)
write(out/'mount_checks.json',result)
print('Mount checks',sum(c['passed'] for c in checks),'/',len(checks))
for c in checks:
    if not c['passed']:print(c)
if not result['passed']:raise SystemExit(1)
