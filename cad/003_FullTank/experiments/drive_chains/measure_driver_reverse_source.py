"""Record the retained fixed-plan hand-end discrepancy from the saved solid."""
from control_rebuild_io_v2 import *
import math
s=Saved(H/'driver_foot_reverse_study/reverse_short03');out=s.folder/'source_measurement01';out.mkdir(exist_ok=False)
q=s.world('DriverReverseOperatingLever');pivot=App.Vector(*s.report['details']['pivot_world_mm'])
fs=[f.Surface for f in q.Faces if isinstance(f.Surface,Part.Sphere) and abs(f.Surface.Radius-10.5)<1e-7];assert len(fs)==1
center=fs[0].Center;axis=center-pivot;axis.normalize();tip=center+axis*10.5
regfile=H/'transmission_controls_study/driver_redo01/mount_registration01.json';reg=read(regfile);main=App.Vector(*s.report['details']['main_world_mm'])
pixel=[reg['image_center_px'][i]+reg['pixels_per_mm']*((tip.x-main.x)*reg['world_plus_x_image_unit'][i]+tip.y*reg['world_plus_y_image_unit'][i]) for i in range(2)]
pick=[132.,192.]
write(out/'report.json',dict(native_sha256=sha(s.native),worker_sha256=sha(Path(__file__)),registration_file=str(regfile.relative_to(ROOT)),registration_sha256=sha(regfile),source_image=reg['source_image'],source_image_sha256=sha(ROOT/reg['source_image']),saved_grip_radial_extreme_world_mm=list(tip),projected_endpoint_px=pixel,reviewed_apparent_source_grip_endpoint_px=pick,pick_uncertainty_px=5.,residual_px=math.dist(pixel,pick),source_camera_refitted=False,geometry_historically_qualified=False,scope='Apparent upper reverse-hand endpoint on SNL6; construction registration reused. Significant endpoint/profile discrepancy retained. Mixed/schematic source and provisional endpoint identity prevent interpreting residual as an exact dimensional error.'))
print('Fixed plan apparent hand-end discrepancy',math.dist(pixel,pick),'px',flush=True)
