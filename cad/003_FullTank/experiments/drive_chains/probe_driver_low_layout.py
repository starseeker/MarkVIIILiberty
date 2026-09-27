"""Small closed-stock layout probe before rebuilding complete driver mechanisms."""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_control_linkage_parts_v3 import clutch_lever
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();f=C/'driver_redo01';s=Saved(f/'linkage_integrated01');base=read(f/'linkage_controls06.json');d=s.report['details'];V=App.Vector;Y=V(0,1,0);reg=read(f/'mount_registration01.json');spacing=reg['shaft_separation_mm'];low=pose(s.rows['PortLowIntermediateRocker']['frame']).multVec(V(0,0,66.675));m=read(H/'transmission_brake_front_study/trial01/standard_context_manifest.json');row=next(v for v in m['occurrences'] if v['name']=='hull_front_slope');entry=m['definitions'][row['definition']];assert sha(entry['brep_path'])==entry['brep_sha256'];nose=Part.Shape();nose.read(entry['brep_path']);nose.Placement=pose(row['frame']);records=[]
for mainz in [1240.,1270.,1300.,1330.,1360.]:
    rz=mainz+20;lowz=rz-295;lowx=low.x+math.sqrt((49.5*25.4+50.8)**2-(lowz-low.z)**2);rear=V(lowx-20,0,rz);main=rear+V(spacing,0,-20);pivot=main+Y*235;front=rear+V(45,235,-218)
    for included in [134.,136.,138.,140.]:
        c=dict(base,lever_included_angle_degrees=included);q,bell=clutch_lever(c)
        def frame(t):return App.Placement(pivot,App.Rotation(Y,90-t))
        def error(t):return (frame(t).multVec(bell)-front).Length-371.475
        lo,hi=20.,80.;assert error(lo)<0<error(hi)
        for _ in range(45):
            mid=(lo+hi)/2
            if error(mid)<0:lo=mid
            else:hi=mid
        theta=(lo+hi)/2;pose_=frame(theta);cap=next(v.Surface for v in q.Faces if isinstance(v.Surface,Part.Sphere));point=pose_.multVec(cap.Center*(1+cap.Radius/cap.Center.Length));q.Placement=pose_;tip=[reg['image_center_px'][i]+reg['pixels_per_mm']*((point.x-main.x)*reg['world_plus_x_image_unit'][i]+point.y*reg['world_plus_y_image_unit'][i]) for i in [0,1]]
        records.append(dict(main_z_mm=mainz,rear_world_mm=list(rear),main_world_mm=list(main),real_low_receiver_world_mm=[lowx,180.,lowz],projected_arm_angle_degrees=included,clutch_hand_elevation_degrees=theta,hand_tip_residual_px=math.dist(tip,[122,462]),hand_nose_gap_mm=q.distToShape(nose)[0],hand_nose_common_mm3=sum(v.Volume for v in q.common(nose).Solids),short_pin_residual_mm=error(theta)))
write(a.output,dict(parent_native_sha256=sha(s.native),worker_sha256=sha(Path(__file__)),parts_sha256=sha(H/'driver_control_linkage_parts_v3.py'),source_landmarks_sha256=sha(f/'low_source_landmarks01.json'),low_intermediate_pin_world_mm=list(low),M574_source_stock_mm=1257.3,M784_short_offset_mm=[45,0,-218],M784_long_offset_mm=[61,0,-295],M763_receiver_offset_mm=[20,0,-295],records=records,scope='Diagnostic uses independently reviewed joint identities and source-length stock closure. No pose, historical station or full saved assembly qualification.'))
for v in records:print(v,flush=True)
