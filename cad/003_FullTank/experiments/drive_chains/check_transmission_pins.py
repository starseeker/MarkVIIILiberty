"""Inspect native pin support axes, stops, cotter locks and printed hardware sizes."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_pin_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.candidate.resolve();sys.path.insert(0,str(stage))
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
    report=read(out/'report.json');native=out/'TransmissionPinCandidate.FCStd'
    assert report['passed'] and report['rendering_complete'] and sha(native)==report['native_sha256']
    for name,digest in report['input_hashes'].items():assert sha(ROOT/name)==digest,name
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    c={k:v['value'] for k,v in read(ROOT/'transmission_pin_controls.json')['controls'].items()}
    trials=[];alignment=[]
    def frame(name):
        i=byid[name];return i['shape'].Placement.multiply(i['target'].Shape.Placement.inverse())
    def record(row):
        trials.append(row);print(row,flush=True)
        write(out/'interface_progress.json',dict(complete=False,trials=trials,native_sha256=sha(native)))
    for hand in ['Port','Starboard']:
        prefix=hand+'PlanetSupports_';carrier=hand+'TransmissionCore_planet_disk'
        for n in range(3):
            name=lambda key:prefix+key+str(n)
            f=frame(name('pin'));axis=f.Rotation.multVec(App.Vector(0,1,0));radial=f.Rotation.multVec(App.Vector(1,0,0))
            g=frame(hand+'PlanetTrain_planet'+str(n));delta=g.Base-f.Base
            radial_offset=delta.cross(axis).Length;angle_error=1-abs(axis.dot(g.Rotation.multVec(App.Vector(0,1,0))))
            alignment.append(dict(hand=hand,index=n,radial_axis_offset_mm=radial_offset,axis_dot_error=angle_error,
                                  passed=radial_offset<1e-6 and abs(angle_error)<1e-8))
            for key,other,shift in [('pin',prefix+'pin_ring',axis*.5),('nut',carrier,axis*-.5),
                                    ('bronze',prefix+'pin_ring',axis*-.75),('plug',name('pin'),radial*.5),
                                    ('bolt_nut',carrier,axis*-.5)]:
                moved=byid[name(key)]['shape'].copy();moved.translate(shift)
                volume=moved.common(byid[other]['shape']).Volume
                record(dict(kind='support_stop_negative',hand=hand,index=n,part=key,receiver=other,
                            shift_world_mm=list(shift),overlap_mm3=volume,passed=volume>1e-3))
            gear=byid[hand+'PlanetTrain_planet'+str(n)]['shape'].copy();gear.translate(axis*.5)
            volume=gear.common(byid[name('steel')]['shape']).Volume
            record(dict(kind='gear_thrust_stop_negative',hand=hand,index=n,shift_mm=.5,overlap_mm3=volume,passed=volume>1))
            for key,other in [('nut','cotter'),('bolt_nut','bolt_cotter')]:
                nut=byid[name(key)]['shape'].copy();nf=frame(name(key));nut.rotate(nf.Base,axis,30)
                volume=nut.common(byid[name(other)]['shape']).Volume
                record(dict(kind='cotter_lock_negative',hand=hand,index=n,nut=key,rotation_deg=30,overlap_mm3=volume,passed=volume>1))
        # Closing either annular side onto the journal flange must encounter material.
        ring=byid[prefix+'pin_ring']['shape'].copy();axis=frame(prefix+'pin0').Rotation.multVec(App.Vector(0,1,0))
        ring.translate(axis*.75)
        hits=[ring.common(byid[prefix+'bronze'+str(n)]['shape']).Volume for n in range(3)]
        record(dict(kind='pin_ring_thrust_negative',hand=hand,shift_mm=.75,overlaps_mm3=hits,passed=all(v>1 for v in hits)))
    dimensions=[]
    # Read actual analytic geometry for the printed nominal sizes.
    for key,diameter in [('bolt',22.225),('plug',12.7)]:
        shape=byid['PortPlanetSupports_'+key+'0']['target'].Shape
        if key=='bolt':
            radii=[f.Surface.Radius for f in shape.Faces if isinstance(f.Surface,Part.Cylinder)]
            measured=2*max(radii)
        else:
            radii=[e.Curve.Radius for e in shape.Edges if isinstance(e.Curve,Part.Circle)]
            measured=2*max(radii)
        dimensions.append(dict(key=key,native_diameter_mm=measured,printed_nominal_mm=diameter,passed=abs(measured-diameter)<1e-6))
    for key,diameter in [('cotter',4.7625),('bolt_cotter',3.175)]:
        shape=byid['PortPlanetSupports_'+key+'0']['target'].Shape
        axis_y=report['dimensions']['pin_fastening' if key=='cotter' else 'bolt_fastening']['cotter_axis_y_mm']
        slab=Part.makeBox(.02,20,20,App.Vector(-.01,axis_y-10,-10))
        section=shape.common(slab);assert not section.isNull()
        b=section.copy().cleaned().BoundBox
        measured=b.ZMax-b.ZMin
        dimensions.append(dict(key=key,native_straight_shank_envelope_mm=measured,printed_nominal_mm=diameter,passed=abs(measured-diameter)<1e-5))
    # Check that the material comparison rejects an actual displacement. Use
    # one occurrence per new definition, plus the revised carrier, rather than
    # depending on mass-property integration to detect a geometry change.
    imported=Part.Shape();imported.read(str(out/'TransmissionPinParts.step'))
    exchange_negatives=[]
    representatives={key:next(n for n,k in report['keys_by_id'].items() if k==key)
                     for key in set(report['keys_by_id'].values())}
    representatives['carrier']='PortTransmissionCore_planet_disk'
    for key,name in sorted(representatives.items()):
        a=byid[name]['shape'];b=min(imported.Solids,key=lambda s:(a.Solids[0].CenterOfMass-s.CenterOfMass).Length).copy()
        b.translate(App.Vector(.01,0,0));missing=a.cut(b);added=b.cut(a)
        exchange_negatives.append(dict(key=key,id=name,shift_world_mm=[.01,0,0],missing_mm3=missing.Volume,added_mm3=added.Volume,
            passed=bool(missing.Faces) and bool(added.Faces) and missing.Volume>1e-5 and added.Volume>1e-5))
    result=dict(passed=all(r['passed'] for r in trials+alignment+dimensions+exchange_negatives),trials=trials,axis_checks=alignment,printed_dimension_checks=dimensions,
        exchange_displacement_negative_checks=exchange_negatives,
        candidate_native_sha256=sha(native),candidate_report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),
        full_parameter_envelope_qualified=False,thread_clamp_qualified=False,motion_qualified=False,
        scope='Both-hand native support/thrust stops, nut-cotter clocking failures, actual pin/gear axis alignment and selected printed nominal hardware diameters. No clamping, strength, full motion or historical running fit qualification.')
    assert sha(native)==report['native_sha256'];write(out/'interface_checks.json',result)
    for row in alignment+dimensions:print(row,flush=True)
    print('PASS' if result['passed'] else 'FAIL',flush=True);sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
