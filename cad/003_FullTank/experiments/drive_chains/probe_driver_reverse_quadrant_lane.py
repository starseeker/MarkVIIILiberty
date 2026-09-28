"""Locate the remaining static transverse corridor without clipping either neighbor."""
from control_rebuild_io_v2 import *
from driver_reverse_quadrant_parts import quadrant
s=Saved(H/'driver_foot_reverse_study/reverse_quadrant02');parent=Saved((ROOT/s.report['parent_native']).parent);d=s.report['details'];out=H/'driver_foot_reverse_study/reverse_quadrant_lane_probe01';out.mkdir(exist_ok=False)
lever=s.world('DriverReverseOperatingLever');seat=parent.world('DriverSeatStarboardRearStayLowerBolt');main=App.Vector(*d['main_world_mm']);holes=[App.Vector(*p) for p in d['mount_local_xz_mm']];rows=[]
for stock in [6.35,7.35]:
 for lane in [-256.,-257.,-258.,-259.,-260.,-261.,-262.]:
  c=dict(d['controls'],quadrant_stock_mm=stock);q=quadrant(c,holes);q.Placement=App.Placement(main+App.Vector(0,lane-stock/2,0),App.Rotation());pairs={}
  for label,t in [('Lever',lever),('SeatBolt',seat)]:
   common=q.common(t);pairs[label]=dict(intersection_mm3=sum(abs(v.Volume) for v in common.Solids),minimum_distance_mm=q.distToShape(t)[0])
  rows.append(dict(stock_mm=stock,inner_face_y_mm=lane,pairs=pairs))
write(out/'report.json',dict(native_sha256=sha(s.native),parent_sha256=sha(parent.native),worker_sha256=sha(Path(__file__)),geometry_worker_sha256=sha(H/'driver_reverse_quadrant_parts.py'),rows=rows,scope='Static transverse clearance sensitivity only. Complete profiles preserved; historical axial stack and moving latch remain unresolved. Full union audit remains required.'))
print(rows,flush=True)
