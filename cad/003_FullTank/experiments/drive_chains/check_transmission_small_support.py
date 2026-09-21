"""Independent native dimension, retention and STEP displacement checks."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_small_support_build');p.add_argument('--worker',action='store_true')
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
    report=read(out/'report.json');native=out/'TransmissionSmallSupportCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    trials=[];dimensions=[];reused=[]
    def collide(moving,receiver,delta,description):
        s=byid[moving]['shape'].copy();s.translate(App.Vector(*delta));v=s.common(byid[receiver]['shape']).Volume
        trials.append(dict(moving=moving,receiver=receiver,delta_world_mm=delta,description=description,
            displaced_overlap_mm3=v,passed=v>1e-5))
    for hand,sign in [('Port',1),('Starboard',-1)]:
        pre=hand+'SmallPlanetSupports_';case=hand+'TransmissionCore_plain_case';ring=pre+'pin_ring'
        for n in range(3):
            ids={k:pre+k+str(n) for k in ['pin','nut','steel','bronze','cotter','plug','bolt','bolt_nut','bolt_cotter']}
            for key,receiver,dy,desc in [('pin',ring,-.5,'Pin head cannot pass its ring seat'),
                ('nut',case,.5,'Pin nut cannot pass its case seat'),('steel',case,-.5,'Steel thrust flange cannot pass case seat'),
                ('bronze',hand+'SmallPlanetTrain_planet'+str(n),-1.5,'Bronze flange cannot pass planet face'),
                ('bolt',case,.5,'Ring bolt head cannot pass case seat'),('bolt_nut',ring,-.5,'Ring bolt nut cannot pass recessed ring seat'),
                ('cotter',ids['pin'],1,'Cotter cannot slide axially through pin bore wall'),
                ('bolt_cotter',ids['bolt'],1,'Cotter cannot slide axially through ring bolt bore wall')]:
                collide(ids[key],receiver,[0,sign*dy,0],desc)
            for key,radius in [('pin',12),('bolt',15.875/2),('bronze',24),('steel',19)]:
                s=byid[ids[key]]['shape']
                faces=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(abs(f.Surface.Axis.y)-1)<1e-7 and abs(f.Surface.Radius-radius)<1e-6]
                dimensions.append(dict(id=ids[key],required_native_radius_mm=radius,matching_axial_cylindrical_faces=len(faces),passed=bool(faces)))
            old=byid[hand+'PlanetSupports_plug'+str(n)]['target'];new=byid[ids['plug']]['target']
            reused.append(dict(id=ids['plug'],old_definition=old.Name,new_definition=new.Name,passed=old.Name==new.Name))
    # Reimport the delivered STEP and deliberately move representative solids.
    # A broad volume/bounds comparison must not mask a misplaced occurrence.
    exchange=out/'TransmissionSmallSupportParts.step';assert sha(exchange)==report['exchange_sha256']
    imported=Part.Shape();imported.read(str(exchange));negative=[]
    for key in ['pin','steel','bronze','pin_ring','bolt','bolt_nut','plug','cotter']:
        name='PortSmallPlanetSupports_'+key+('' if key=='pin_ring' else '0')
        a=byid[name]['shape'].Solids[0];b=min(imported.Solids,key=lambda s:(s.CenterOfMass-a.CenterOfMass).Length).copy()
        b.translate(App.Vector(.001,0,0));fuzzy=min(.0001,max(1e-7,a.getTolerance(1)+b.getTolerance(1)));missing=a.cut(b,fuzzy);extra=b.cut(a,fuzzy)
        negative.append(dict(id=name,deliberate_offset_mm=.001,comparison_fuzzy_tolerance_mm=fuzzy,missing_mm3=missing.Volume,extra_mm3=extra.Volume,
            passed=bool(missing.Faces) and bool(extra.Faces) and missing.Volume+extra.Volume>1e-5))
    spline_checks=[];rivet_checks=[]
    for hand,sign in [('Port',1),('Starboard',-1)]:
        disk=byid[hand+'SmallPlanetTrain_disk']['shape']
        curves=[e.Curve for e in disk.Edges if isinstance(e.Curve,Part.BSplineCurve)]
        spline_checks.append(dict(id=hand+'SmallPlanetTrain_disk',cubic_native_edges=sum(b.Degree==3 for b in curves),passed=any(b.Degree==3 for b in curves)))
        rivet=byid[hand+'SmallPlanetTrain_rivet0']['shape'].Solids[0]
        projected=362-(sign*rivet.CenterOfMass.y-882.65)/.7257142857142856
        rivet_checks.append(dict(id=hand+'SmallPlanetTrain_rivet0',projected_source_x_px=projected,source_target_x_px=1065,passed=abs(projected-1065)<1e-4))
    passed=all(r['passed'] for r in trials+dimensions+reused+negative+spline_checks+rivet_checks)
    result=dict(passed=passed,native_sha256=sha(native),report_sha256=sha(out/'report.json'),exchange_sha256=sha(exchange),
        checker_sha256=sha(Path(__file__)),local_retention_trials=trials,native_dimension_checks=dimensions,
        reused_definition_checks=reused,step_displacement_negatives=negative,native_spline_checks=spline_checks,source_rivet_station_checks=rivet_checks,
        scope='Local static retention and native dimensions only. No full extraction sequence, thread load, historical fit or moving-gear qualification.')
    write(out/'interface_checks.json',result)
    print('PASS' if passed else 'FAIL',len(trials),'retention trials',len(dimensions),'dimensions',len(reused),'reuse checks',len(negative),'STEP negatives',flush=True)
    for r in trials+dimensions+reused+negative+spline_checks+rivet_checks:
        if not r['passed']:print('FAILED',r,flush=True)
    sys.exit(0 if passed else 1)
finally:runtime.close()
