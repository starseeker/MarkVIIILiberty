"""Measure saved rod-eye bores and retain the differing pin axes needed by subsequent rods."""
import argparse
import math
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
V=App.Vector
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};c=r['controls'];cache={};measurements=[];selected=[]
def world(name):
    row=rows[name];d=m['definitions'][row['definition']];key=d['brep_sha256']
    if key not in cache:
        assert sha(d['brep_path'])==key;s=Part.Shape();s.read(d['brep_path']);assert s.Placement.isIdentity();cache[key]=s
    s=cache[key].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));selected.append(name);return s
for name,station in c['stations'].items():
    occurrence=name+'HorizontalLever';s=world(occurrence);pose=App.Placement(App.Matrix(*rows[occurrence]['frame']))
    faces=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-c['lever']['end_bore_diameter']/2)<1e-7 and abs(abs(f.Surface.Axis.z)-1)<1e-7]
    assert len(faces)==2
    for end,xy in c['lever_profiles'][station['lever_profile']].items():
        nominal=pose.multVec(V(*xy,c['lever'].get('arm_bottom',0)+c['lever']['stock']/2))
        f=min(faces,key=lambda f:math.hypot(f.Surface.Center.x-nominal.x,f.Surface.Center.y-nominal.y))
        q=[f.Surface.Center.x,f.Surface.Center.y,(f.BoundBox.ZMin+f.BoundBox.ZMax)/2]
        assert math.dist(q,list(nominal))<1e-6
        measurements.append(dict(id=name+end.title()+'RodEye',occurrence=occurrence,end=end,center_world_mm=q,
                            pin_axis_world=[0,0,1],bore_diameter_mm=2*f.Surface.Radius,
                            bearing_width_mm=f.BoundBox.ZLength,definition_sha256=m['definitions'][rows[occurrence]['definition']]['brep_sha256']))
oldpath=H/'transmission_controls_study/context01/report.json';old=read(oldpath);rear=[]
for item in old['interfaces']:
    if 'HighSpeed' in item['id']:continue
    assert len(item['bearing_intervals'])==1
    name=item['bearing_intervals'][0]['occurrence'];s=world(name);q=item['center_world_mm']
    faces=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-item['bore_diameter_mm']/2)<1e-7 and abs(abs(f.Surface.Axis.y)-1)<1e-7 and math.hypot(f.Surface.Center.x-q[0],f.Surface.Center.z-q[2])<1e-6]
    assert len(faces)==1
    f=faces[0];actual=[f.Surface.Center.x,(f.BoundBox.YMin+f.BoundBox.YMax)/2,f.Surface.Center.z]
    assert math.dist(actual,q)<1e-6
    rear.append(dict(id=item['id'],occurrence=name,center_world_mm=actual,pin_axis_world=[0,1,0],bore_diameter_mm=2*f.Surface.Radius,bearing_width_mm=f.BoundBox.YLength))
routes=[]
for name in c['stations']:
    one=next(v for v in measurements if v['id']==name+'BrakeRodEye')
    target=name.replace('Low','LowSpeed')+'BrakeControl';two=next(v for v in rear if v['id']==target)
    delta=[a-b for a,b in zip(two['center_world_mm'],one['center_world_mm'])]
    routes.append(dict(fulcrum_eye=one['id'],rear_brake_eye=two['id'],source_rod_mark='M578' if 'Track' in name else 'M573',
                       displacement_to_brake_mm=delta,straight_eye_center_distance_mm=math.dist(one['center_world_mm'],two['center_world_mm']),
                       pin_axis_angle_degrees=90,scope='Endpoint chord only. Fork lengths, threaded adjustment, bends, spring/bracket connections and swept rod clearance still required.'))
validate_native_bindings(dict(native_file=str(native),render_occurrences=sorted(set(selected)),landmarks=[]),m)
result=dict(passed=True,native_sha256=sha(native),manifest_sha256=sha(out/'isolated/manifest.json'),probe_sha256=sha(Path(__file__)),
            previous_rear_interface_probe_sha256=sha(oldpath),new_rod_eyes=measurements,verified_rear_brake_eyes=rear,proposed_routes=routes,
            scope='Actual saved cylindrical faces and composed frames. The rod identity assignment follows SNL rear-rod entries; this does not establish an unobstructed route or historical dimensions.',geometry_modified=False)
write(out/'operating_interfaces.json',result)
print('Measured eight new vertical rod eyes and reverified four transverse brake eyes.',flush=True)
for v in routes:print(v['fulcrum_eye'],round(v['straight_eye_center_distance_mm'],3),'mm chord;90degree end-pin axes',flush=True)
