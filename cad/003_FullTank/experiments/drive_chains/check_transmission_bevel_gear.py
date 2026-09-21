"""Independently inspect saved bevel mesh, tooth counts, bearings and clutch."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_bevel_gear_build');p.add_argument('--worker',action='store_true')
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
    report=read(out/'report.json');native=out/'TransmissionBevelGearCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    origin=App.Vector(*report['shaft_axis_world_mm']);checks=[];mesh=[]
    def record(kind,passed,**kw):
        row=dict(kind=kind,passed=bool(passed),**kw);checks.append(row)
        write(out/'interface_progress.json',dict(completed=len(checks),mesh_completed=len(mesh),failed=[r for r in checks if not r['passed']]))
    def radial_runs(shape,axis,station,radius,samples):
        flags=[]
        for n in range(samples):
            angle=2*math.pi*n/samples;a=radius*math.cos(angle);b=radius*math.sin(angle)
            point=App.Vector(a,station,b) if axis=='Y' else App.Vector(station,a,b)
            flags.append(shape.isInside(origin+point,1e-7,True))
        return sum(flags[n] and not flags[n-1] for n in range(samples))
    distance=math.hypot(46*25.4/6,14*25.4/6);station_radius=distance-25
    for name,n,other,axis,sign in [('PortBevelDrive_wheel',46,14,'Y',1),('StarboardBevelDrive_wheel',46,14,'Y',-1),('CenterBevelDrive_pinion',14,46,'X',1)]:
        angle=math.atan2(n,other);radial=station_radius*math.sin(angle);axial=sign*station_radius*math.cos(angle)
        count=radial_runs(byid[name]['shape'],axis,axial,radial,n*16)
        record('native tooth count',count==n,id=name,expected_teeth=n,measured_teeth=count,section_radial_axial_mm=[radial,axial])
        surfaces=[f.Surface for f in byid[name]['shape'].Faces if isinstance(f.Surface,Part.BSplineSurface)]
        cubic=sum(3 in [s.UDegree,s.VDegree] for s in surfaces)
        record('native cubic surfaces',cubic>=2*n,id=name,cubic_surface_count=cubic)
    pinion=byid['CenterBevelDrive_pinion']['shape']
    for hand,sign in [('Port',1),('Starboard',-1)]:
        wheel=byid[hand+'BevelDrive_wheel']['shape']
        for n in range(13):
            angle=n*360/46/12;gear=wheel.copy();gear.rotate(origin,App.Vector(0,1,0),sign*angle)
            drive=pinion.copy();drive.rotate(origin,App.Vector(1,0,0),-46/14*angle)
            volume=gear.common(drive).Volume;gap=gear.distToShape(drive)[0]
            mesh.append(dict(hand=hand,wheel_rotation_deg=sign*angle,pinion_rotation_deg=-46/14*angle,overlap_mm3=volume,gap_mm=gap,passed=volume<1e-5 and gap>0))
            record('sampled bevel mesh',mesh[-1]['passed'],**{k:v for k,v in mesh[-1].items() if k!='passed'})
        wrong=pinion.copy();wrong.rotate(origin,App.Vector(1,0,0),180/14);v=wheel.common(wrong).Volume
        record('mesh wrong-phase negative',v>1,id=hand,overlap_mm3=v)
        bearing=doc.getObject(hand+'ThrustBearing')
        record('catalogue bearing quantity',len(json.loads(bearing.SurveyIds))==1 and json.loads(bearing.CatalogueQuantity)==1,id=bearing.Name)
        group_items=[i for name,i in byid.items() if name.startswith(hand+'ThrustBearing_')]
        record('bearing decomposition',len(group_items)==19 and all(json.loads(i['target'].SurveyIds)==[] for i in group_items),id=bearing.Name,leaf_count=len(group_items))
        for role in ['rotating_race','stationary_race']:
            name=hand+'ThrustBearing_'+role;shape=byid[name]['shape']
            radii=set(round(f.Surface.Radius,6) for f in shape.Faces if isinstance(f.Surface,Part.Cylinder) and abs(abs(f.Surface.Axis.y)-1)<1e-7)
            record('printed bearing radial envelope',radii=={52.5,77.5},id=name,cylindrical_radii_mm=sorted(radii))
        low=min(i['shape'].BoundBox.YMin for i in group_items);high=max(i['shape'].BoundBox.YMax for i in group_items)
        record('printed bearing width',abs(high-low-40)<1e-6,id=bearing.Name,width_mm=high-low)
        balls=[i for i in group_items if 'ball' in i['id']];definitions={i['target'].Name for i in balls}
        record('shared bearing balls',len(balls)==16 and len(definitions)==1,id=bearing.Name,balls=len(balls),definitions=len(definitions))
        for item in balls:
            center=item['shape'].CenterOfMass;radius=math.hypot(center.x-origin.x,center.z-origin.z)
            record('ball native radius and pitch',abs(radius-65)<1e-6 and abs(item['shape'].Volume-4/3*math.pi*1000)<1e-5,id=item['id'],pitch_radius_mm=radius)
    clutch=byid['CenterBevelDrive_clutch']['shape'];shaft=byid['CenterTransmissionCore_cross_shaft']['shape']
    dogs=radial_runs(clutch,'Y',-16,90,1440)
    record('four native clutch dogs',dogs==4,measured_dogs=dogs)
    splines=radial_runs(clutch,'Y',-16,39,1440)
    record('ten native clutch splines',splines==10,measured_splines=splines)
    for angle in [-2,2]:
        shifted=clutch.copy();shifted.rotate(origin,App.Vector(0,1,0),angle)
        for hand,engaged in [('Port',False),('Starboard',True)]:
            v=shifted.common(byid[hand+'BevelDrive_clutch_ring']['shape']).Volume
            record('ahead dog engagement',v>1 if engaged else v<1e-5,hand=hand,twist_deg=angle,overlap_mm3=v)
    for hand,sign in [('Port',1),('Starboard',-1)]:
        for name in [hand+'BevelWheelSupports_inner_bush',hand+'SmallPlanetTrain_sun_bush']:
            bush=byid[name]['shape'];bb=bush.BoundBox;low=min(bb.YMin,bb.YMin+sign*650);high=max(bb.YMax,bb.YMax+sign*650)
            outer=Part.makeCylinder(40.5,high-low,origin+App.Vector(0,low,0),App.Vector(0,1,0))
            bore=Part.makeCylinder(35.65,high-low+2,origin+App.Vector(0,low-1,0),App.Vector(0,1,0))
            v=outer.cut(bore).common(shaft).Volume
            record('continuous bush shaft passage',v<1e-5,id=name,overlap_mm3=v)
    # Printed Timken bore must admit the unfinished shaft's outboard splines.
    outer=Part.makeCylinder(74.6125,240,origin+App.Vector(215,0,0),App.Vector(1,0,0))
    bore=Part.makeCylinder(34.925,242,origin+App.Vector(214,0,0),App.Vector(1,0,0))
    v=outer.cut(bore).common(pinion).Volume
    record('Timken bore shaft passage',v<1e-5,overlap_mm3=v,scope='Input shaft alone, axial215..455mm; bearing assembly still pending.')
    for hand,sign in [('Port',1),('Starboard',-1)]:
        for role,blank_length,seat in [('short',53.975,38),('long',60.325,31.65)]:
            name=hand+'BevelDrive_rivet_'+role+'0';shape=byid[name]['target'].Shape
            flange=byid[hand+'BevelWheelSupports_sleeve']['target'].Shape
            end=max(f.CenterOfMass.y for f in flange.Faces if isinstance(f.Surface,Part.Plane) and 82<f.CenterOfMass.y<83)
            for face,direction in [(seat,-1),(end,1)]:
                start=face-6 if direction<0 else face
                cap=shape.common(Part.makeCylinder(20,6,App.Vector(0,start,0),App.Vector(0,1,0)))
                expected=math.pi*(15.875/2)**2*(blank_length-(end-seat))
                record('both native rivet heads present',abs(cap.Volume-expected)<1e-5,id=name,seat_y_mm=face,
                    cap_volume_mm3=cap.Volume,assumed_head_volume_mm3=expected)
            for delta in [-.3,.3]:
                moved=byid[name]['shape'].copy();moved.translate(App.Vector(0,sign*delta,0))
                receiver=hand+'BevelWheelSupports_sleeve' if delta<0 else hand+'BevelDrive_'+('wheel' if role=='short' else 'clutch_ring')
                overlap=moved.common(byid[receiver]['shape']).Volume
                record('native rivet axial capture',overlap>1e-5,id=name,delta_y_mm=sign*delta,receiver=receiver,overlap_mm3=overlap)
    exchange=out/'TransmissionBevelGearParts.step';assert sha(exchange)==report['exchange_sha256']
    imported=Part.Shape();imported.read(str(exchange))
    for name in ['PortBevelDrive_wheel','CenterBevelDrive_pinion','CenterBevelDrive_clutch','PortThrustBearing_rotating_race']:
        a=byid[name]['shape'].Solids[0];b=min(imported.Solids,key=lambda s:(s.CenterOfMass-a.CenterOfMass).Length).copy()
        b.translate(App.Vector(.001,0,0));fuzzy=min(.0001,max(1e-7,a.getTolerance(1)+b.getTolerance(1)))
        missing=a.cut(b,fuzzy);extra=b.cut(a,fuzzy)
        record('STEP displacement negative',bool(missing.Faces) and bool(extra.Faces) and missing.Volume+extra.Volume>1e-5,
            id=name,offset_mm=.001,fuzzy_mm=fuzzy,missing_mm3=missing.Volume,extra_mm3=extra.Volume)
    passed=all(r['passed'] for r in checks)
    write(out/'interface_checks.json',dict(passed=passed,native_sha256=sha(native),report_sha256=sha(out/'report.json'),exchange_sha256=sha(exchange),
        checker_sha256=sha(Path(__file__)),checks=checks,mesh_trials=mesh,
        scope='Native tooth counts/spline surfaces,26 mesh samples, clutch engagement, printed bearing envelope and shaft-only passages; not load/contact-stress or full-motion qualification.'))
    for row in checks:
        if not row['passed']:print('FAILED',row,flush=True)
    print('PASS' if passed else 'FAIL',len(checks),'independent checks',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
