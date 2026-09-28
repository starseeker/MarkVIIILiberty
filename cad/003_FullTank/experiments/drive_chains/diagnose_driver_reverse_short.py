"""Preserve actual journal and conflicting selector material before revision."""
from control_rebuild_io_v2 import *
import math
s=Saved(H/'driver_foot_reverse_study/reverse_short01');parent=Saved((ROOT/s.report['parent_native']).parent)
out=s.folder/'diagnostics01';out.mkdir(exist_ok=False)
q=s.world('DriverReverseOperatingLever');p=App.Vector(*s.report['details']['pivot_world_mm']);axis=App.Vector(0,1,0)
fs=[f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-19.1619)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-p).cross(axis).Length<1e-6]
stock=Part.makeCylinder(19.0119,24,p-axis*12,axis);shaft=s.world('DriverMainShaft')
common=q.common(parent.world('StarboardDriverLowSelector'));b=common.BoundBox
common.exportBrep(str(out/'selector_intersection.brep'))
result=dict(native_sha256=sha(s.native),parent_sha256=sha(parent.native),worker_sha256=sha(Path(__file__)),journal_faces=[dict(area_mm2=f.Area,axial_vertex_extents=[min((v.Point-p).y for v in f.Vertexes),max((v.Point-p).y for v in f.Vertexes)],edges=len(f.Edges)) for f in fs],full_uncut_bore_area_mm2=2*math.pi*19.1619*24,missing_shaft_mm3=stock.cut(shaft).Volume,shaft_intersection_mm3=q.common(shaft).Volume,selector_intersection_mm3=common.Volume,intersection_bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],scope='Oilway interrupts journal cylindrical face; inspect complete span and actual open bore rather than uncut-cylinder area. Preserve genuine selector collision separately.')
write(out/'report.json',result);print(result,flush=True)
