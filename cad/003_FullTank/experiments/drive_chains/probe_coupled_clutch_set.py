"""Bound the M772 profile change before choosing a coupled reconstruction."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_clutch_delayed_set_parts import delayed_set

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
out=p.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
s=Saved(H/'coupled_driver_station_study/trial02');a=Saved((ROOT/s.report['details']['retained_development_native']).parent)
name='DriverClutchOperatingLever';key=s.rows[name]['definition'];old=a.definition(key)
world={n:s.world(n) for n in s.rows if n!=name};records=[]
for amount in [20.,25.,30.,35.,40.,45.,50.,55.,60.]:
    q,meta=delayed_set(old,amount);q.Placement=pose(s.rows[name]['frame']);pairs=[]
    for n,t in world.items():
        if not q.BoundBox.intersect(t.BoundBox):continue
        common=q.common(t);volume=sum(abs(v.Volume) for v in common.Solids)
        pairs.append(dict(other=n,volume_mm3=volume,passed=volume<1e-5 and (common.isNull() or common.isValid())))
    findings=[v for v in pairs if not v['passed']]
    distances={n:q.distToShape(world[n])[0] for n in ['DriverPortSupportPlate','DriverSeatPortFrontStayLowerBolt','DriverSeatPortFrontStayLowerNut','DriverSeatPortFrontStay']}
    records.append(dict(maximum_setback_mm=amount,plan_change_bound_px=amount*.33117731724752747,pairs=pairs,findings=findings,distances_mm=distances))
    print(amount,'findings',len(findings),'min support distance',min(distances.values()),flush=True)
write(out/'report.json',dict(worker_sha256=sha(Path(__file__)),parts_sha256=sha(H/'driver_clutch_delayed_set_parts.py'),
    candidate_native_sha256=sha(s.native),accepted_native_sha256=sha(a.native),records=records,
    source_camera_refitted=False,geometry_integrated=False,
    scope='Complete alternative M772 blade versus all393 other prototype parts. Smaller middle-blade displacement is preferred if stock and clearances survive. Full retained tank context and parameter variation require separate checks.'))
