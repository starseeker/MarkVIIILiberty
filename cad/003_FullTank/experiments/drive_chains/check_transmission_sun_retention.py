"""Independent native ring dimensions, capture directions and export negatives."""
import argparse
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_sun_retention_build');p.add_argument('--worker',action='store_true')
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
    report=read(out/'report.json');native=out/'TransmissionSunRetentionCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    trials=[];dimensions=[];source_stations=[];reuse=[]
    def shifted(moving,receiver,dy,hand):
        s=byid[moving]['shape'].copy();s.translate(App.Vector(0,dy,0));v=s.common(byid[receiver]['shape']).Volume
        trials.append(dict(moving=moving,receiver=receiver,hand=hand,delta_world_y_mm=dy,overlap_mm3=v,passed=v>1e-5))
    for hand,sign in [('Port',1),('Starboard',-1)]:
        ring=hand+'SunRetention_ring';sun=hand+'SmallPlanetTrain_sun';drum=hand+'TransmissionCore_high_drum'
        for moving,receiver,delta in [(ring,sun,-.5),(ring,sun,.5),(drum,ring,-.5),(drum,sun,.5)]:
            shifted(moving,receiver,sign*delta,hand)
        for name,radii in [(ring,[46.2,57]),(sun,[46,50.8,57.8,36.65]),(drum,[50.95,57.2,58,190.5])]:
            for radius in radii:
                faces=[f for f in byid[name]['shape'].Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and abs(abs(f.Surface.Axis.y)-1)<1e-7]
                dimensions.append(dict(id=name,radius_mm=radius,native_faces=len(faces),passed=bool(faces)))
        shape=byid[ring]['shape'];center=sign*(shape.BoundBox.YMin+shape.BoundBox.YMax)/2
        source_x=362-(center-882.65)/.7257142857142856
        source_stations.append(dict(id=ring,source_x_px=source_x,passed=abs(source_x-1285)<1e-7))
        target=byid[ring]['target'];old=byid[hand+'TransmissionBearing_OuterRing']['target']
        reuse.append(dict(id=ring,definition=target.Name,passed=target.Name==old.Name))
    exchange=out/'TransmissionSunRetentionParts.step';assert sha(exchange)==report['exchange_sha256']
    imported=Part.Shape();imported.read(str(exchange));negative=[]
    for name in ['PortSunRetention_ring','PortSmallPlanetTrain_sun','PortTransmissionCore_high_drum']:
        a=byid[name]['shape'].Solids[0];b=min(imported.Solids,key=lambda s:(s.CenterOfMass-a.CenterOfMass).Length).copy()
        b.translate(App.Vector(.001,0,0));fuzzy=min(.0001,max(1e-7,a.getTolerance(1)+b.getTolerance(1)))
        missing=a.cut(b,fuzzy);extra=b.cut(a,fuzzy)
        negative.append(dict(id=name,offset_mm=.001,comparison_fuzzy_tolerance_mm=fuzzy,missing_mm3=missing.Volume,extra_mm3=extra.Volume,
            passed=bool(missing.Faces) and bool(extra.Faces) and missing.Volume+extra.Volume>1e-5))
    passed=all(r['passed'] for r in trials+dimensions+source_stations+reuse+negative)
    result=dict(passed=passed,native_sha256=sha(native),report_sha256=sha(out/'report.json'),exchange_sha256=sha(exchange),
        checker_sha256=sha(Path(__file__)),retention_trials=trials,native_dimension_checks=dimensions,source_station_checks=source_stations,
        reused_definition_checks=reuse,step_displacement_negatives=negative,
        scope='Nominal static ring/drum retention. No elastic ring installation, bearing fit or service-load qualification.')
    write(out/'interface_checks.json',result)
    for r in trials+dimensions+source_stations+reuse+negative:
        if not r['passed']:print('FAILED',r,flush=True)
    print('PASS' if passed else 'FAIL',len(trials),'capture trials',len(dimensions),'radii',len(negative),'STEP negatives',flush=True)
    sys.exit(0 if passed else 1)
finally:runtime.close()
