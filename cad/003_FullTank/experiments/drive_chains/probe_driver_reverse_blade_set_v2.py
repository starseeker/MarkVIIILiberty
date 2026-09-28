"""Full-section blade sensitivity against all known local interference candidates."""
from control_rebuild_io_v2 import *
from driver_reverse_lever_parts_v2 import lever
s=Saved(H/'driver_foot_reverse_study/reverse_short02');parent=Saved((ROOT/s.report['parent_native']).parent);d=s.report['details']
out=H/'driver_foot_reverse_study/reverse_set_probe02';out.mkdir(exist_ok=False)
pivot=App.Vector(*d['pivot_world_mm']);bell=App.Vector(*d['front_pin_world_mm'])-pivot
reports=[read(H/'driver_foot_reverse_study'/case/'context_audit/report.json') for case in ['reverse_short01','reverse_short02']]
names=set()
for report in reports:
    for pair in report['pairs']:
        if pair['first']=='DriverReverseOperatingLever':names.add(pair['second'])
        elif pair['second']=='DriverReverseOperatingLever':names.add(pair['first'])
assert all(n in s.rows or n in parent.rows for n in names),sorted(names-set(s.rows)-set(parent.rows))
neighbors={n:(s if n in s.rows else parent).world(n) for n in names};records=[]
for stock in [12.7,11.7]:
    for delay in [10.,20.,30.]:
        c=dict(d['controls'],blade_stock_mm=stock,delayed_set_mm=delay);q,rot,info=lever(c,bell);q.Placement=App.Placement(pivot,rot)
        pairs=[]
        for name,t in neighbors.items():
            com=q.common(t);v=sum(abs(v.Volume) for v in com.Solids)
            pairs.append(dict(other=name,intersection_mm3=v,minimum_distance_mm=q.distToShape(t)[0]))
        records.append(dict(stock_mm=stock,delay_mm=delay,findings=[v for v in pairs if v['intersection_mm3']>1e-5],pairs=pairs))
        print(stock,delay,records[-1]['findings'],flush=True)
write(out/'report.json',dict(native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),worker_sha256=sha(Path(__file__)),geometry_worker_sha256=sha(H/'driver_reverse_lever_parts_v2.py'),records=records,scope='All known local neighbors from rejected context audits. Full separate context audit remains required; clearance does not prove historical shape.'))
