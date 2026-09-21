"""Challenge the saved small gear meshes, sleeve journals and riveted joints."""
import argparse
import math
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_small_build');p.add_argument('--worker',action='store_true')
args=p.parse_args();stage=args.stage.resolve();out=args.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not args.worker:
    with (out/'interface_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],
            env=runtime.environment(out/'interface_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    from lib.cad_build import leaves
    report=read(out/'report.json');native=out/'TransmissionSmallCandidate.FCStd'
    assert report['passed'] and report['rendering_complete'] and sha(native)==report['native_sha256']
    for name,digest in report['input_hashes'].items():assert sha(ROOT/name)==digest,name
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    origin=App.Vector(*report['shaft_axis_world_mm']);trials=[];measured=[]
    def record(row):
        trials.append(row);write(out/'interface_progress.json',dict(complete=False,trials=trials))
        print(row['kind'],row['hand'],row['passed'],flush=True)
    def frame(name):
        i=byid[name];return i['shape'].Placement.multiply(i['target'].Shape.Placement.inverse())
    for hand,sign in [('Port',1),('Starboard',-1)]:
        pre=hand+'SmallPlanetTrain_';axis=App.Vector(0,sign,0)
        for n in range(3):
            name=pre+'planet'+str(n);f=frame(name)
            native_radius=math.hypot(f.Base.x-origin.x,f.Base.z-origin.z)
            measured.append(dict(kind='planet_radius',id=name,radius_mm=native_radius,expected_mm=137.16,passed=abs(native_radius-137.16)<1e-6))
            moved=byid[name]['shape'].copy();moved.rotate(f.Base,axis,7.5)
            hits={k:moved.common(byid[pre+k]['shape']).Volume for k in ['sun','ring']}
            record(dict(kind='planet_clock_negative',hand=hand,index=n,rotation_deg=7.5,overlaps_mm3=hits,passed=all(v>1 for v in hits.values())))
        for angle in [-2,-1,1,2]:
            sun=byid[pre+'sun']['shape'].copy();sun.rotate(origin,axis,angle)
            ring=byid[pre+'ring']['shape'].copy();ring.rotate(origin,axis,-angle*30/78)
            pairs=[]
            for n in range(3):
                name=pre+'planet'+str(n);planet=byid[name]['shape'].copy();planet.rotate(frame(name).Base,axis,-angle*30/24)
                for key,other in [('sun',sun),('ring',ring)]:
                    v=planet.common(other).Volume;gap=planet.distToShape(other)[0]
                    pairs.append(dict(index=n,other=key,overlap_mm3=v,gap_mm=gap,passed=v<1e-5 and .001<gap<.5))
            record(dict(kind='compatible_gear_only_phase',hand=hand,sun_rotation_deg=angle,pairs=pairs,passed=all(r['passed'] for r in pairs)))
        for n in [0,7]:
            name=pre+'rivet'+str(n)
            for travel,key in [(.5,'ring'),(-.5,'disk')]:
                moved=byid[name]['shape'].copy();moved.translate(axis*travel);v=moved.common(byid[pre+key]['shape']).Volume
                record(dict(kind='rivet_head_stop_negative',hand=hand,index=n,local_shift_y_mm=travel,receiver=key,overlap_mm3=v,passed=v>1))
        disk=byid[pre+'disk']['shape'].copy();disk.rotate(origin,axis,1)
        hits=[disk.common(byid[pre+'rivet'+str(n)]['shape']).Volume for n in range(16)]
        record(dict(kind='disk_rivet_clock_negative',hand=hand,overlaps_mm3=hits,passed=all(v>1 for v in hits)))
        bush=byid[pre+'sun_bush']['shape'].copy();bush.translate(App.Vector(.5,0,0))
        for other in [pre+'sun','CenterTransmissionCore_cross_shaft']:
            v=bush.common(byid[other]['shape']).Volume
            record(dict(kind='bush_radial_negative',hand=hand,receiver=other,overlap_mm3=v,passed=v>1))
        sun=byid[pre+'sun']['shape'].copy();sun.rotate(origin,axis,2)
        v=sun.common(byid[hand+'TransmissionCore_high_drum']['shape']).Volume
        record(dict(kind='drum_spline_clock_negative',hand=hand,overlap_mm3=v,passed=v>1))
        rivet=byid[pre+'rivet0']['target'].Shape
        radii=[f.Surface.Radius for f in rivet.Faces if isinstance(f.Surface,Part.Cylinder)]
        r=max(radii);equivalent=rivet.Volume/(math.pi*r*r)-8
        measured.append(dict(kind='rivet_nominal_blank',hand=hand,native_shank_diameter_mm=2*r,equivalent_blank_length_mm=equivalent,
            interpretation='The inferred original button head equals the modeled8mm upset allowance volume; remaining formed volume reconstructs the printed blank length.',
            passed=abs(2*r-12.7)<1e-6 and abs(equivalent-47.625)<1e-5))
    step=Part.Shape();step.read(str(out/'TransmissionSmallParts.step'));exchange=[]
    for name in ['PortSmallPlanetTrain_'+k for k in ['sun','sun_bush','planet0','ring','disk','rivet0']]+['CenterTransmissionCore_cross_shaft']:
        a=byid[name]['shape'];b=min(step.Solids,key=lambda s:(a.Solids[0].CenterOfMass-s.CenterOfMass).Length)
        assert not a.cut(b).Faces and not b.cut(a).Faces
        b=b.copy();b.translate(App.Vector(.01,0,0));missing=a.cut(b);extra=b.cut(a)
        exchange.append(dict(id=name,missing_mm3=missing.Volume,added_mm3=extra.Volume,
            passed=bool(missing.Faces) and bool(extra.Faces) and missing.Volume>1e-5 and extra.Volume>1e-5))
    result=dict(passed=all(r['passed'] for r in trials+measured+exchange),trials=trials,native_dimension_checks=measured,
        exchange_displacement_negative_checks=exchange,native_sha256=sha(native),report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),
        motion_qualified=False,historical_fit_qualified=False,full_parameter_envelope_qualified=False,
        scope='Local negative joint checks and four compatible isolated gear phases per side. No full revolution, carrier motion, load, wear or historical-fit qualification.')
    assert sha(native)==report['native_sha256'];write(out/'interface_checks.json',result)
    print('PASS' if result['passed'] else 'FAIL',flush=True);sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
