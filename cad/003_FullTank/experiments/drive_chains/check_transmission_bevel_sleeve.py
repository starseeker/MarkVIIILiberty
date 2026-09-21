"""Check saved bearing passages, receiver capture and exchange sensitivity."""
import argparse
import math
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_bevel_sleeve_build');p.add_argument('--worker',action='store_true')
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
    report=read(out/'report.json');native=out/'TransmissionBevelSleeveCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    origin=App.Vector(*report['shaft_axis_world_mm']);shaft=byid['CenterTransmissionCore_cross_shaft']['shape']
    dims=[];passages=[];sweeps=[];negative=[];capture=[];reuse=[];stations=[];profiles=[]
    def cyl(radius,low,high):
        return Part.makeCylinder(radius,high-low,origin+App.Vector(0,low,0),App.Vector(0,1,0))
    for hand,sign in [('Port',1),('Starboard',-1)]:
        pre=hand+'BevelWheelSupports_'
        for suffix,radii in [('sleeve',[40.65,53.8,167]),('inner_bush',[35.65,40.5]),('outer_bush',[53.9,59,65]),('retainer',[54,65])]:
            name=pre+suffix
            for radius in radii:
                faces=[f for f in byid[name]['shape'].Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and abs(abs(f.Surface.Axis.y)-1)<1e-7]
                dims.append(dict(id=name,radius_mm=radius,faces=len(faces),passed=bool(faces)))
        for name in [pre+'inner_bush',hand+'SmallPlanetTrain_sun_bush']:
            bush=byid[name]['shape'];bb=bush.BoundBox
            # Actual native parts at six stations, moving only from their side.
            for delta in [0,40,90,160,350,650]:
                s=bush.copy();s.translate(App.Vector(0,sign*delta,0));v=s.common(shaft).Volume
                passages.append(dict(id=name,delta_y_mm=sign*delta,overlap_mm3=v,passed=v<1e-5))
            radii=sorted(set(round(f.Surface.Radius,6) for f in bush.Faces if isinstance(f.Surface,Part.Cylinder) and abs(abs(f.Surface.Axis.y)-1)<1e-7))
            assert radii==[35.65,40.5],(name,radii)
            low=min(bb.YMin,bb.YMin+sign*650);high=max(bb.YMax,bb.YMax+sign*650)
            swept=cyl(radii[-1],low,high).cut(cyl(radii[0],low-1,high+1))
            v=swept.common(shaft).Volume
            sweeps.append(dict(id=name,swept_limits_y_mm=[low,high],overlap_mm3=v,passed=v<1e-5,
                method='Conservative annular swept envelope, native bore/OD; ignores radial screw hole.'))
            wrong=cyl(radii[-1],low,high).cut(cyl(28.95,low-1,high+1));v=wrong.common(shaft).Volume
            negative.append(dict(id=name,alteration='Rejected root-radius bore28.95 in same swept envelope',overlap_mm3=v,passed=v>1e-5))
        for moving,receiver in [(pre+'inner_bush',pre+'screw'),(pre+'outer_bush',pre+'dowel')]:
            s=byid[moving]['shape'].copy();s.rotate(origin,App.Vector(0,1,0),10);v=s.common(byid[receiver]['shape']).Volume
            capture.append(dict(moving=moving,receiver=receiver,rotation_deg=10,overlap_mm3=v,passed=v>1e-5))
        # Retention remains meaningful after enlarging M267's bore.
        for moving,receiver,delta in [(hand+'SunRetention_ring',hand+'SmallPlanetTrain_sun',-.5),
            (hand+'SunRetention_ring',hand+'SmallPlanetTrain_sun',.5),
            (hand+'TransmissionCore_high_drum',hand+'SunRetention_ring',-.5),
            (hand+'TransmissionCore_high_drum',hand+'SmallPlanetTrain_sun',.5)]:
            s=byid[moving]['shape'].copy();s.translate(App.Vector(0,sign*delta,0));v=s.common(byid[receiver]['shape']).Volume
            capture.append(dict(moving=moving,receiver=receiver,delta_y_mm=sign*delta,overlap_mm3=v,passed=v>1e-5))
        for suffix in ['sun','sun_bush']:
            name=hand+'SmallPlanetTrain_'+suffix;radius=40.65 if suffix=='sun' else 35.65
            count=sum(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 for f in byid[name]['shape'].Faces)
            dims.append(dict(id=name,radius_mm=radius,faces=count,passed=count>0))
        reuse.append(dict(id=pre+'dowel',passed=byid[pre+'dowel']['target'].Name==byid[hand+'TransmissionBearing_InnerDowel']['target'].Name))
        bb=byid[pre+'sleeve']['shape'].BoundBox;near=min(abs(bb.YMin),abs(bb.YMax));far=max(abs(bb.YMin),abs(bb.YMax))
        for station,pick in [(near,1442),(far,1293)]:
            measured=1534-station/.7257142857142856
            stations.append(dict(id=pre+'sleeve',source_pick_x_px=pick,measured_source_x_px=measured,passed=abs(measured-pick)<1e-7))
    # Check actual shaft cross sections: ten rectangular crests and the new step.
    for y,tip in [(0,41.5),(190,34.8),(430,34.8)]:
        corners=[origin+App.Vector(x,y,z) for x,z in [(-100,-100),(100,-100),(100,100),(-100,100),(-100,-100)]]
        plane=Part.Face(Part.makePolygon(corners))
        edges=shaft.section(plane).Edges
        points=[v for e in edges for v in e.discretize(Deflection=.05)]
        crest=max(math.hypot(v.x-origin.x,v.z-origin.z) for v in points)
        lines=sum(type(e.Curve).__name__=='Line' for e in edges)
        profiles.append(dict(axial_y_mm=y,crest_corner_radius_mm=crest,straight_edges=lines,
            passed=abs(crest-math.hypot(tip,5.5))<1e-6 and lines==30))
    # Nonphysical M257 bore gauge, through the complete shaft length. It is
    # a reserved interface only; there is no clutch solid in the inventory.
    bb=shaft.BoundBox;low=bb.YMin-1;high=bb.YMax+1
    bore=cyl(35.65,low,high)
    for n in range(10):
        tooth=Part.makeBox(11.2,high-low,10,origin+App.Vector(-5.6,low,31.65))
        tooth.rotate(origin,App.Vector(0,1,0),n*36);bore=bore.fuse(tooth)
    gauge=cyl(55,low,high).cut(bore);v=gauge.common(shaft).Volume
    sweeps.append(dict(id='future_M257_nonphysical_bore_gauge',overlap_mm3=v,passed=v<1e-5,
        method='Continuous extruded female profile along complete shaft; R35.65/41.65, width11.2, ten splines.'))
    wrong=cyl(55,low,high).cut(cyl(28.95,low-1,high+1));v=wrong.common(shaft).Volume
    negative.append(dict(id='future_M257_nonphysical_bore_gauge',alteration='Undersized circular bore',overlap_mm3=v,passed=v>1e-5))
    exchange=out/'TransmissionBevelSleeveParts.step';assert sha(exchange)==report['exchange_sha256']
    imported=Part.Shape();imported.read(str(exchange));step_negative=[]
    for name in ['PortBevelWheelSupports_sleeve','PortSmallPlanetTrain_sun','CenterTransmissionCore_cross_shaft','CenterTransmissionCore_bevel_cover']:
        a=byid[name]['shape'].Solids[0];b=min(imported.Solids,key=lambda s:(s.CenterOfMass-a.CenterOfMass).Length).copy()
        b.translate(App.Vector(.001,0,0));fuzzy=min(.0001,max(1e-7,a.getTolerance(1)+b.getTolerance(1)))
        missing=a.cut(b,fuzzy);extra=b.cut(a,fuzzy)
        step_negative.append(dict(id=name,offset_mm=.001,comparison_fuzzy_tolerance_mm=fuzzy,missing_mm3=missing.Volume,extra_mm3=extra.Volume,
            passed=bool(missing.Faces) and bool(extra.Faces) and missing.Volume+extra.Volume>1e-5))
    checks=dims+passages+sweeps+negative+capture+reuse+stations+profiles+step_negative
    passed=all(r['passed'] for r in checks)
    write(out/'interface_checks.json',dict(passed=passed,native_sha256=sha(native),report_sha256=sha(out/'report.json'),exchange_sha256=sha(exchange),
        checker_sha256=sha(Path(__file__)),native_dimension_checks=dims,actual_bush_passage_trials=passages,continuous_shaft_passage_checks=sweeps,
        undersized_bore_negatives=negative,local_capture_trials=capture,reused_definition_checks=reuse,source_station_checks=stations,
        shaft_section_checks=profiles,step_displacement_negatives=step_negative,
        scope='Nominal bearing fits, local capture and shaft-only assembly passages. Complete assembly sequence, clutch geometry, loads and historical fits unqualified.'))
    for row in checks:
        if not row['passed']:print('FAILED',row,flush=True)
    print('PASS' if passed else 'FAIL',len(checks),'independent checks',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
