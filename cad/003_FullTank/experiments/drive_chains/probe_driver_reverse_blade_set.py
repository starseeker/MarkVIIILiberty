"""Compare full blade-set hypotheses; preserve all endpoints and source reaches."""
from control_rebuild_io_v2 import *
from driver_reverse_lever_parts import lever
s=Saved(H/'driver_foot_reverse_study/reverse_short01');parent=Saved((ROOT/s.report['parent_native']).parent);d=s.report['details']
out=H/'driver_foot_reverse_study/reverse_set_probe01';out.mkdir(exist_ok=False)
pivot=App.Vector(*d['pivot_world_mm']);bell=App.Vector(*d['front_pin_world_mm'])-pivot
records=[]
for stock in [12.7,13.7]:
    for delay in [60.,40.,20.,0.]:
        c=dict(d['controls'],blade_stock_mm=stock,delayed_set_mm=delay);q,rot,info=lever(c,bell);q.Placement=App.Placement(pivot,rot)
        low=parent.world('StarboardDriverLowSelector');com=q.common(low)
        records.append(dict(stock_mm=stock,delay_mm=delay,intersection_mm3=sum(abs(v.Volume) for v in com.Solids),minimum_distance_mm=q.distToShape(low)[0]))
write(out/'report.json',dict(native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),worker_sha256=sha(Path(__file__)),geometry_worker_sha256=sha(H/'driver_reverse_lever_parts.py'),records=records,scope='Sensitivity of estimated transverse blade set. Printed reach, full section stock, grip ends, journal, bell and short-rod closure unchanged. Clearance is not historical evidence.'))
print(records,flush=True)
