"""Check saved planetary retention and gear mesh, including deliberate failures."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_planet_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not args.worker:
    with (out/'interface_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],
                               env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    from lib.cad_build import leaves
    report=read(out/'report.json');native=out/'TransmissionPlanetCandidate.FCStd'
    assert report['passed'] and report['rendering_complete'] and sha(native)==report['native_sha256']
    for name,digest in report['input_hashes'].items():assert sha(ROOT/name)==digest,name
    c={k:v['value'] for k,v in read(ROOT/'transmission_planet_controls.json')['controls'].items()}
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    origin=App.Vector(*report['shaft_axis_world_mm']);trials=[]
    print('Reopened',len(byid),'occurrences; checking native retention and gear mesh.',flush=True)
    def record(row):
        trials.append(row)
        write(out/'interface_progress.json',dict(complete=False,trials=trials,native_sha256=sha(native)))
        print(row['kind'],row['hand'],row.get('part',row.get('id',row.get('sun_angle_deg'))),row['passed'],flush=True)
    def shift(name,dy):
        shape=byid[name]['shape'].copy();shape.translate(App.Vector(0,dy,0));return shape
    for hand,sign in [('Port',1),('Starboard',-1)]:
        prefix=hand+'PlanetTrain_'
        # Axial stops must exist in the saved native solids, not just in control values.
        for role,receiver,dy in [('retainer','CenterTransmissionCore_cross_shaft',-.5),
                                 ('retainer','CenterTransmissionCore_cross_shaft',.5),
                                 ('sun',prefix+'retainer',.5),
                                 ('washer',hand+'TransmissionCore_planet_disk',-.5),
                                 ('washer',hand+'TransmissionBearing_InnerBush',.5),
                                 ('ring',prefix+'gasket0',-.5),('ring',prefix+'gasket1',.5)]:
            moved=shift(prefix+role,sign*dy);volume=moved.common(byid[receiver]['shape']).Volume
            record(dict(kind='axial_stop_negative',hand=hand,part=role,receiver=receiver,
                               local_shift_y_mm=dy,overlap_mm3=volume,passed=volume>1))
        axis=App.Vector(0,sign,0)
        for n in range(c['planets_per_side']):
            name=prefix+'planet'+str(n);item=byid[name]
            frame=item['shape'].Placement.multiply(item['target'].Shape.Placement.inverse())
            planet=item['shape'].copy();planet.rotate(frame.Base,axis,180/c['teeth_planet'])
            overlaps={key:planet.common(byid[prefix+key]['shape']).Volume for key in ['sun','ring']}
            record(dict(kind='planet_phase_negative',hand=hand,id=name,rotation_deg=180/c['teeth_planet'],
                               overlaps_mm3=overlaps,passed=all(v>1 for v in overlaps.values())))
        # Isolated gear-only phase perturbations: no shaft, carrier or pose is moved/saved.
        # Fixed carrier: Ns*dSun + Nr*dRing = 0, and Ns*dSun + Np*dPlanet = 0.
        for sun_angle in [-2,-1,1,2]:
            sun=byid[prefix+'sun']['shape'].copy();sun.rotate(origin,axis,sun_angle)
            ring=byid[prefix+'ring']['shape'].copy();ring.rotate(origin,axis,-sun_angle*c['teeth_sun']/c['teeth_ring'])
            pairs=[]
            for n in range(c['planets_per_side']):
                name=prefix+'planet'+str(n);item=byid[name]
                frame=item['shape'].Placement.multiply(item['target'].Shape.Placement.inverse())
                planet=item['shape'].copy();planet.rotate(frame.Base,axis,-sun_angle*c['teeth_sun']/c['teeth_planet'])
                for key,other in [('sun',sun),('ring',ring)]:
                    overlap=planet.common(other).Volume;gap=planet.distToShape(other)[0]
                    pairs.append(dict(planet=n,other=key,overlap_mm3=overlap,gap_mm=gap,
                                      passed=overlap<1e-5 and .001<gap<.5))
            record(dict(kind='gear_only_phase_trial',hand=hand,sun_angle_deg=sun_angle,
                               pairs=pairs,passed=all(p['passed'] for p in pairs)))
    assert sha(native)==report['native_sha256']
    result=dict(passed=all(r['passed'] for r in trials),trials=trials,candidate_native_sha256=sha(native),
                candidate_report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),
                full_parameter_envelope_qualified=False,motion_qualified=False,
                scope='Both-hand native axial-stop failures, deliberately wrong planet phases, and four nearby compatible isolated gear phases. No torque, wear, full-revolution motion or historical fit qualification.')
    write(out/'interface_checks.json',result)
    for row in trials:print(row,flush=True)
    print('PASS' if result['passed'] else 'FAIL',flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
