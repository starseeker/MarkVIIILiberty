"""Check exactly what changed from the qualified coupled station."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import H, Saved, sha, write, read

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
s = Saved(p.parse_args().candidate)
b = Saved(H/'coupled_driver_station_study/trial02')
expected = {'Def_DriverContext_hull_floor_1','Def_DriverPortSupportPlate_MountStudy',
            'Def_DriverStarboardSupportPlate_MountStudy','Def_SeatSupport_PortAngle_M788',
            'Def_SeatSupport_StarboardAngle_M788'}
assert set(s.rows)==set(b.rows) and set(s.manifest['definitions'])==set(b.manifest['definitions'])
changed = {k for k,v in s.manifest['definitions'].items()
           if v['brep_sha256']!=b.manifest['definitions'][k]['brep_sha256']}
checks = [dict(name='Exactly five changed definitions; all120 others byte-identical',passed=changed==expected)]
frames = []
for n,row in s.rows.items():
    assert row['definition']==b.rows[n]['definition'] and row['owners']==b.rows[n]['owners']
    if max(abs(x-y) for x,y in zip(row['frame'],b.rows[n]['frame']))>1e-7:
        frames.append(n)
permitted = {stem+str(i)+suffix for side in ['Port','Starboard'] for i in [3,4]
             for suffix in ['Bolt','Lock','Nut'] for stem in ['Driver'+side+'SupportMount','DriverSeat'+side+'AngleFloor']}
checks.append(dict(name='Only24 complete front mounting pieces move',passed=set(frames)==permitted))
for side in ['Port','Starboard']:
    q = s.world('Driver'+side+'SupportPlate')
    expected_x = 7696.363641618496+s.report['details']['support_front_offset_mm']
    checks.append(dict(name=side+' actual fore-edge follows declared variation',
                       passed=abs(q.BoundBox.XMax-expected_x)<1e-6,
                       actual_x_mm=q.BoundBox.XMax,expected_x_mm=expected_x))
    bend = read(H/'bow_reconstruction_study/trial02/report.json')['joint_datums']['inner']['floor_bend'][0]
    for index in [3,4]:
        bolt = s.world('DriverSeat'+side+'AngleFloor'+str(index)+'Bolt')
        checks.append(dict(name=side+str(index)+' whole floor-bolt head remains aft of bend',
                           passed=bolt.BoundBox.XMax < bend-10.,
                           forward_bound_mm=bolt.BoundBox.XMax,bend_x_mm=bend))
result = dict(passed=all(c['passed'] for c in checks),checks=checks,
              native_sha256=sha(s.native),baseline_native_sha256=sha(b.native),
              baseline_receipt_sha256=sha(H/'coupled_driver_station_study/study_receipt.json'),
              checker_sha256=sha(Path(__file__)),changed_definitions=sorted(changed),changed_frames=sorted(frames),
              scope='Actual saved change set, unchanged rod/shaft/seat geometry and frames, fore-edge variation and complete bolt clearance from bend.')
write(s.folder/'delta_checks.json',result)
print('Support outline delta checks:',len(checks),'passed:',result['passed'],flush=True)
assert result['passed']
