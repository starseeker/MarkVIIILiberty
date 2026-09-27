"""Bounded source-angle diagnostic against the actual retained nose panel.

These are construction hypotheses for an unprinted hand/bell angle, not motion
poses. Each regenerated lever retains the same true bell pin and printed reaches.
Final selected geometry still requires independent saved-artifact validation.
"""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_control_linkage_parts_v3 import clutch_lever
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);d=s.report['details'];c=d['controls'];stdpath=H/'transmission_brake_front_study/trial01/standard_context_manifest.json';m=read(stdpath);row=next(v for v in m['occurrences'] if v['name']=='hull_front_slope');entry=m['definitions'][row['definition']];assert sha(entry['brep_path'])==entry['brep_sha256'];nose=Part.Shape();nose.read(entry['brep_path']);nose.Placement=pose(row['frame']);records=[]
reg=read(ROOT/d['foundation']['controls']['registration']);scale=reg['pixels_per_mm'];xp=reg['world_plus_x_image_unit'];yp=reg['world_plus_y_image_unit'];center=reg['image_center_px'];pivot=App.Vector(*d['clutch_pivot_world_mm'])
for angle in [124.,125.,126.,127.,128.]:
    cfg=dict(c,lever_included_angle_degrees=angle);q,bell=clutch_lever(cfg);theta=d['clutch_hand_angle_degrees']+angle-c['lever_included_angle_degrees'];frame=App.Placement(pivot,App.Rotation(App.Vector(0,1,0),90-theta));cap=next(f.Surface for f in q.Faces if isinstance(f.Surface,Part.Sphere));point=frame.multVec(cap.Center*(1+cap.Radius/cap.Center.Length));q.Placement=frame;tip=[center[i]+scale*((point.x-pivot.x)*xp[i]+point.y*yp[i]) for i in [0,1]]
    records.append(dict(projected_arm_angle_degrees=angle,hand_elevation_degrees=theta,hand_tip_source_px=tip,hand_tip_residual_px=math.dist(tip,[122,462]),nose_distance_mm=q.distToShape(nose)[0],nose_common_mm3=sum(v.Volume for v in q.common(nose).Solids),bell_pin_deviation_mm=(frame.multVec(bell)-App.Vector(*d['clutch_bell_pin_world_mm'])).Length,valid=q.isValid()))
result=dict(candidate_native_sha256=sha(s.native),controls=c,worker_sha256=sha(Path(__file__)),parts_worker_sha256=sha(H/'driver_control_linkage_parts_v3.py'),standard_manifest_sha256=sha(stdpath),nose_brep_sha256=entry['brep_sha256'],records=records,scope='Diagnostic regenerated lever hypotheses only; no camera refit or historical pose validation.')
write(a.output,result);print(records,flush=True)
