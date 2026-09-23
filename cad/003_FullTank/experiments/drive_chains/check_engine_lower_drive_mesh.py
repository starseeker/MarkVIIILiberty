"""Mesh/free-play checks on the actual saved integral lower driver."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'engine_lower_drive_installation');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'mesh_check.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'mesh_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves
    V=App.Vector;r=read(out/'report.json');native=out/r.get('native_file','DrivetrainWithLowerDriveStudy.FCStd')
    assert sha(native)==r['native_sha256'];doc=App.openDocument(str(native));items={i['id']:i for i in leaves(doc.Root)}
    inverse=doc.TankLibertyEngine.getGlobalPlacement().inverse();o=V(r['main_apex'],0,0)
    def local(name):
        s=items[name]['shape'].copy();s.Placement=inverse.multiply(s.Placement);return s
    main,pinion=local('EngineGear_DrivingBevel'),local('EngineLowerDrive_IntegralDriver')
    samples=[]
    for i in range(9):
        theta=i*360/33/8;one,two=main.copy(),pinion.copy()
        one.rotate(o,V(1,0,0),theta);two.rotate(o,V(0,0,1),-1.5*theta)
        overlap=abs(one.common(two).Volume);gap=one.distToShape(two)[0]
        samples.append(dict(main_deg=theta,pinion_deg=-1.5*theta,overlap_mm3=overlap,gap_mm=gap,passed=overlap<1e-5 and gap>1e-6))
        write(out/'mesh_progress.json',dict(rotation_samples=samples));print('Mesh sample',i,samples[-1]['passed'],flush=True)
    wrong=pinion.copy();wrong.rotate(o,V(0,0,1),180/22)
    wrong_overlap=abs(main.common(wrong).Volume)
    brackets=[]
    for sign in [-1,1]:
        def distance(angle):
            s=pinion.copy();s.rotate(o,V(0,0,1),sign*angle);return main.distToShape(s)[0]
        assert distance(0)>1e-6 and distance(1)<=1e-6,'Contact not bracketed'
        lo,hi=0.,1.
        for _ in range(13):
            mid=(lo+hi)/2
            if distance(mid)<=1e-6:hi=mid
            else:lo=mid
        brackets.append(dict(direction=sign,free_deg=lo,contact_deg=hi,width_deg=hi-lo))
        print('Contact bracket',brackets[-1],flush=True)
    tooth=r['datums']['teeth']['upper'];pitch=tooth['pitch_radius_mm'];face=tooth['face_width_mm'];cone=tooth['cone_distance_mm']
    bounds={station:[math.radians(sum(b[k] for b in brackets))*pitch*factor for k in ['free_deg','contact_deg']]
        for station,factor in [('outer',1),('midface',1-face/(2*cone)),('inner',1-face/cone)]}
    passed=all(s['passed'] for s in samples) and wrong_overlap>100 and all(.127<=lo<=hi<=.254 for lo,hi in bounds.values())
    result=dict(passed=passed,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),rotation_samples=samples,
        negative_control_overlap_mm3=wrong_overlap,contact_brackets=brackets,circumferential_backlash_bounds_mm=bounds,
        contact_distance_threshold_mm=1e-6,source_cold_range_mm=[.127,.254],source_measurement_station_unspecified=True,
        scope='Actual saved128-station integral driver against saved33-tooth main bevel; geometric checks, not load/manufacturing qualification.')
    write(out/'mesh_checks.json',result);print('Actual saved mesh/free-play',passed,flush=True)
    assert passed
finally:
    runtime.close()
