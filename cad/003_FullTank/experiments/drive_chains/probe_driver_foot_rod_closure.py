"""Measure what a direct M769 socket would require of the remaining shared rods.

This is a constraint diagnosis, not authorization to invent or lengthen SH946F.
The two insertion depths and suggested plan picks are explicit hypotheses.
"""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import *
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);parent=Saved((ROOT/s.report['parent_native']).parent)
out=a.output.resolve();out.mkdir(exist_ok=False);V=App.Vector;Y=V(0,1,0)
rod=parent.definition('Def_DriverClutchFrontRod_M576')
rod_axis=max([f for f in rod.Faces if isinstance(f.Surface,Part.Cylinder)],key=lambda f:f.Area).Surface.Axis
end_coordinates=[v.Point.dot(rod_axis) for v in rod.Vertexes]
rodlength=max(end_coordinates)-min(end_coordinates)
assert abs(rodlength-parent.report['details']['M576_common_stock_mm'])<1e-7
regfile=H/'transmission_controls_study/driver_redo01/mount_registration01.json';reg=read(regfile)
main=V(*parent.report['details']['main_world_mm']);rows=[]
for side in ['Port','Starboard']:
    q=s.world(side+'DriverFootLink')
    sockets=[f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-9.575)<1e-7]
    assert len(sockets)==1;surface=sockets[0].Surface;axis=surface.Axis
    if axis.x>0:axis=-axis
    # The open socket mouth is the circular boundary furthest along its rearward axis.
    circles=[e.Curve for e in sockets[0].Edges if isinstance(e.Curve,Part.Circle)]
    assert len(circles)==2
    rear=max([x.Center for x in circles],key=lambda x:x.dot(axis))
    receiver=parent.world(side+'FootIntermediateRocker')
    centers=[f.Surface.Center for f in receiver.Faces if isinstance(f.Surface,Part.Cylinder) and
        abs(f.Surface.Radius-6.5)<1e-7 and f.Surface.Axis.cross(Y).Length<1e-7]
    assert centers
    pin=min(centers,key=lambda x:x.z);pin=V(pin.x,pose(parent.rows[side+'FootIntermediateRocker']['frame']).Base.y,pin.z)
    delta=pin-rear;direction=V(delta);direction.normalize()
    cross=delta.cross(axis).Length;angle=math.degrees(axis.getAngle(direction))
    insertion=19.05
    needed_face=delta.Length+2*insertion-rodlength
    def plan(point):
        d=point-main
        return [reg['image_center_px'][i]+reg['pixels_per_mm']*(d.x*reg['world_plus_x_image_unit'][i]+point.y*reg['world_plus_y_image_unit'][i]) for i in range(2)]
    rows.append(dict(side=side,socket_mouth_world_mm=list(rear),actual_socket_axis=list(axis),
        retained_lower_pin_axis_point_mm=list(pin),mouth_to_pin_mm=delta.Length,
        retained_pin_distance_from_socket_axis_mm=cross,needed_socket_rotation_deg=angle,
        proposed_straight_rod_direction=list(direction),socket_plan_px=plan(rear),
        nominal_socket_and_fork_insertion_mm=insertion,required_single_fork_pin_to_face_mm=needed_face,
        interpretation='If the link contains a direct rod socket, and both insertions are19.05mm, a straight unchanged M576 requires this fork pin-to-face reach. SH946F geometry is not established by this calculation.'))
result=dict(candidate_native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),worker_sha256=sha(Path(__file__)),
    registration_sha256=sha(regfile),rod_definition='Def_DriverClutchFrontRod_M576',rod_stock_length_mm=rodlength,
    retained_occurrences=[n for n,r in parent.rows.items() if r['definition']=='Def_DriverClutchFrontRod_M576'],cases=rows,
    source_camera_refitted=False,geometry_modified=False,stock_shortened=False,connections_closed=False,
    conclusion='Current inferred socket axes do not aim at retained intermediate eyes. Both socket topology and special-fork form must be reviewed before rod construction; solve all five shared M576 applications together if stock changes.')
write(out/'report.json',result)
print('Shared M576 stock',rodlength,'mm; diagnostic socket/receiver constraints',rows,flush=True)
