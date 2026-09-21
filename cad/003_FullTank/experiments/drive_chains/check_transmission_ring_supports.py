"""Check actual revised bolt seats, access paths and native/STEP change detection."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_ring_support_build')
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
    from transmission_core_parts import cylinder
    report=read(out/'report.json');native=out/'TransmissionRingSupportCandidate.FCStd'
    assert report['passed'] and report['rendering_complete'] and sha(native)==report['native_sha256']
    for name,digest in report['input_hashes'].items():assert sha(ROOT/name)==digest,name
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    trials=[];source_checks=[]
    def frame(name):
        i=byid[name];return i['shape'].Placement.multiply(i['target'].Shape.Placement.inverse())
    def record(row):
        trials.append(row);print(row,flush=True);write(out/'interface_progress.json',dict(complete=False,trials=trials))
    for hand in ['Port','Starboard']:
        prefix=hand+'PlanetSupports_';carrier=hand+'TransmissionCore_planet_disk';ring=prefix+'pin_ring'
        cf=frame(carrier)
        receivers=[byid[n]['shape'] for n in [carrier,ring]+[hand+'PlanetTrain_'+k for k in ['sun','ring','planet0','planet1','planet2']]]
        for n in range(3):
            name=lambda k:prefix+k+str(n)
            f=frame(name('bolt'));axis=f.Rotation.multVec(App.Vector(0,1,0));radial=f.Rotation.multVec(App.Vector(1,0,0))
            local=cf.inverse().multVec(f.Base);radius=(local.x*local.x+local.z*local.z)**.5
            bolt=byid[name('bolt')]['target'].Shape
            measured_d=2*max(face.Surface.Radius for face in bolt.Faces if isinstance(face.Surface,Part.Cylinder))
            source_checks.append(dict(hand=hand,index=n,native_radius_mm=radius,conditional_source_radius_mm=148.77142857142854,
                native_bolt_diameter_mm=measured_d,printed_nominal_mm=22.225,
                passed=abs(radius-148.77142857142854)<1e-6 and abs(measured_d-22.225)<1e-6))
            for key,other,shift in [('bolt',ring,axis*.5),('bolt_nut',carrier,axis*-.5),('bolt',ring,radial*1.6)]:
                moved=byid[name(key)]['shape'].copy();moved.translate(shift);volume=moved.common(byid[other]['shape']).Volume
                record(dict(kind='receiver_stop_negative',hand=hand,index=n,key=key,receiver=other,shift_world_mm=list(shift),overlap_mm3=volume,passed=volume>1e-3))
            nut=byid[name('bolt_nut')]['shape'].copy();nut.rotate(f.Base,axis,30)
            volume=nut.common(byid[name('bolt_cotter')]['shape']).Volume
            record(dict(kind='cotter_clock_negative',hand=hand,index=n,rotation_deg=30,overlap_mm3=volume,passed=volume>1))
            # Hardware is removed before extraction. Check the bolt itself
            # through its actual axial access path against retained castings/gears.
            for travel in [.5,15,40,75]:
                moved=byid[name('bolt')]['shape'].copy();moved.translate(axis*-travel)
                hits=[moved.common(s).Volume for s in receivers]
                record(dict(kind='bolt_extraction_clearance',hand=hand,index=n,travel_mm=travel,max_overlap_mm3=max(hits),
                    scope='Bolt only; nut and cotter removed. Geometric access, not tooling or full assembly-motion qualification.',passed=max(hits)<1e-5))
        moved=byid[ring]['shape'].copy();moved.translate(cf.Rotation.multVec(App.Vector(0,.75,0)))
        hits=[moved.common(byid[prefix+'bronze'+str(n)]['shape']).Volume for n in range(3)]
        record(dict(kind='retained_bush_thrust_negative',hand=hand,overlaps_mm3=hits,passed=all(v>1 for v in hits)))
    step=Part.Shape();step.read(str(out/'TransmissionRingSupportParts.step'))
    representatives={'carrier':'PortTransmissionCore_planet_disk','pin_ring':'PortPlanetSupports_pin_ring',
        **{k:'PortPlanetSupports_'+k+'0' for k in ['bolt','bolt_nut','bolt_cotter']}}
    exchange=[]
    for key,name in representatives.items():
        a=byid[name]['shape'];b=min(step.Solids,key=lambda s:(a.Solids[0].CenterOfMass-s.CenterOfMass).Length)
        assert not a.cut(b).Faces and not b.cut(a).Faces
        b=b.copy();b.translate(App.Vector(.01,0,0));missing=a.cut(b);added=b.cut(a)
        exchange.append(dict(key=key,missing_mm3=missing.Volume,added_mm3=added.Volume,
            passed=bool(missing.Faces) and bool(added.Faces) and missing.Volume>1e-5 and added.Volume>1e-5))
    result=dict(passed=all(r['passed'] for r in trials+source_checks+exchange),trials=trials,source_station_checks=source_checks,
        exchange_displacement_negative_checks=exchange,candidate_native_sha256=sha(native),candidate_report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),
        full_parameter_envelope_qualified=False,thread_clamp_qualified=False,motion_qualified=False,historical_fit_qualified=False)
    assert sha(native)==report['native_sha256'];write(out/'interface_checks.json',result)
    print('PASS' if result['passed'] else 'FAIL',flush=True);sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
