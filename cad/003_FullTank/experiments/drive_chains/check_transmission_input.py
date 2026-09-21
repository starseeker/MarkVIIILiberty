"""Independent checks of saved bearing envelopes, installation passages and reuse."""
import argparse,json,math
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_input_build');p.add_argument('--worker',action='store_true')
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
    report=read(out/'report.json');native=out/'TransmissionInputCandidate.FCStd'
    assert report['passed'] and report['rendering_complete'] and sha(native)==report['native_sha256']
    assert all(sha(ROOT/n)==h for n,h in report['input_hashes'].items())
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    checks=[]
    def check(name,value,expected,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=bool(passed)))
    def local(name):return byid[name]['target'].Shape.Solids[0]
    def world(name):return byid[name]['shape'].Solids[0]
    origin=App.Vector(*report['shaft_axis_world_mm'])
    def gauge(radius,x0,x1):return Part.makeCylinder(radius,x1-x0,origin+App.Vector(x0,0,0),App.Vector(1,0,0))
    check('one native leaf per occurrence',len(items),1287)
    roller_targets=set()
    for n in range(2):
        pre='InputBearing'+str(n)+'_';cup=local(pre+'cup');inner=local(pre+'inner_race');cage=local(pre+'cage')
        check(pre+'cone width from saved faces',inner.BoundBox.XLength,54.229)
        check(pre+'cup width from saved faces',cup.BoundBox.XLength,44.45)
        # BoundBox may use a cached display triangulation after reopening.
        # The saved analytic cylinder is the dimensional authority.
        radii=[f.Surface.Radius for f in cup.Faces if isinstance(f.Surface,Part.Cylinder)]
        check(pre+'cup outside diameter',2*max(radii),149.225)
        bores=[f.Surface.Radius for f in inner.Faces if isinstance(f.Surface,Part.Cylinder)]
        check(pre+'printed cone bore surface exists',any(abs(r-34.925)<1e-6 for r in bores),True)
        cone=doc.getObject('InputCone'+str(n));assembly=doc.getObject('InputBearing'+str(n))
        check(pre+'cone children are race, cage and16 rollers',len(cone.Group),18)
        check(pre+'assembly owns cup and cone',len(assembly.Group),2)
        check(pre+'commercial assembly counted once',json.loads(assembly.CatalogueQuantity),1)
        check(pre+'cone identity canonical',json.loads(cone.SurveyIds)[0],'P_4cc795fc081b212c')
        check(pre+'cup identity canonical',json.loads(byid[pre+'cup']['target'].SurveyIds)[0],'P_96630a0821aef275')
        for m in range(16):
            name=pre+'roller'+str(m).zfill(2);roller_targets.add(byid[name]['target'].Name)
            check(name+'not an extra catalogue bearing',json.loads(byid[name]['target'].SurveyIds),[])
            for race in ['inner_race','cup']:
                gap=world(name).distToShape(world(pre+race))[0]
                check(name+'_'+race+'_running clearance',gap,.0399733888735147)
            check(name+'_cage clearance positive',world(name).distToShape(world(pre+'cage'))[0]>.25,True)
        # Each through-window has two disjoint conical wall patches. Count
        # unique inclined cone axes, not topological face fragments.
        pocket_axes=[]
        for f in cage.Faces:
            s=f.Surface
            if not isinstance(s,Part.Cone) or abs(s.Axis.x)>1-1e-7:continue
            if not any(s.Axis.cross(axis).Length<1e-7 and (s.Apex-apex).cross(axis).Length<1e-6 for axis,apex in pocket_axes):
                pocket_axes.append((s.Axis,s.Apex))
        check(pre+'perforated cage has sixteen distinct conical pockets',len(pocket_axes),16)
    check('all32 rollers reuse one native definition',len(roller_targets),1)
    # The actual conical surfaces must share a virtual apex, not just look tapered.
    for name in ['inner_race','cup','roller']:
        shape=local('InputBearing1_'+name if name!='roller' else 'InputBearing1_roller00')
        cones=[f.Surface for f in shape.Faces if isinstance(f.Surface,Part.Cone)]
        check(name+' has one rolling cone',len(cones),1)
        # Roller clearance offsets its virtual apex slightly; the nominal
        # construction is checked separately in the dimension report.
        if name!='roller':check(name+' apex on common axis',(cones[0].Apex-App.Vector(-200,0,0)).Length,0.0)
        else:
            check('roller axis passes nominal common apex',(cones[0].Apex-App.Vector(-200,0,0)).cross(cones[0].Axis).Length,0.0)
            check('roller semi-angle matches half race-angle difference',abs(cones[0].SemiAngle),math.radians(2.090082092550843))
    a=world('InputBearing0_inner_race');b=world('InputBearing1_inner_race')
    check('inboard cone axial limits',a.BoundBox.XMin-origin.x,203.0)
    check('outboard cone axial limits',b.BoundBox.XMax-origin.x,351.458)
    check('bearings opposed',doc.InputBearing0.Placement.Rotation.multVec(App.Vector(1,0,0)).dot(doc.InputBearing1.Placement.Rotation.multVec(App.Vector(1,0,0))),-1.0)
    shaft=world('CenterBevelDrive_pinion');housing=world('InputHousing_housing')
    prior_doc=App.openDocument(str(ROOT/'transmission_bevel_gear_build/TransmissionBevelGearCandidate.FCStd'));prior_doc.recompute()
    prior_items={i['id']:i for i in leaves(prior_doc.Root)}
    edit_region=gauge(48.0001,195,500)
    old_head=prior_items['CenterBevelDrive_pinion']['shape'].cut(edit_region)
    new_head=shaft.cut(edit_region)
    check('all pinion material outside shaft-extension cylinder retained',old_head.cut(new_head).Volume+new_head.cut(old_head).Volume,0.0)
    old_flanks=[f for f in prior_items['CenterBevelDrive_pinion']['shape'].Faces if isinstance(f.Surface,Part.BSplineSurface)]
    new_flanks=[f for f in shaft.Faces if isinstance(f.Surface,Part.BSplineSurface)]
    check('accepted pinion spline-surface count retained',len(new_flanks),len(old_flanks))
    check('accepted pinion spline-surface total area retained',sum(f.Area for f in new_flanks),sum(f.Area for f in old_flanks),1e-5)
    # Cylindrical gauge sweeps bound every translated cup position through the
    # open end of the one-piece housing; this catches a trapped-bearing model.
    cup_sweep=gauge(74.6125,212.525,460)
    check('cups can enter through the housing open end',housing.common(cup_sweep).Volume,0.0)
    shaft_region=gauge(100,203.0001,491)
    bore_gauge=gauge(34.925,203,492)
    check('cone bore can pass all shaft steps and spline crests',shaft.common(shaft_region).cut(bore_gauge).Volume,0.0)
    blocked=housing.fuse(gauge(80,407,408).cut(gauge(74,406,409)))
    check('negative: undersize entry obstructs cup sweep',blocked.common(cup_sweep).Volume>1,True)
    for key,count in [('spacer_shim',13),('flange_shim',16),('gland_bolt',4),('gland_nut',8)]:
        check(key+' installed count',sum(n.startswith('InputHousing_'+key) for n in byid),count)
    check('washer clears pinion material',world('InputHousing_washer').common(shaft).Volume,0.0)
    check('cotter passes through shaft cross-hole',world('InputHousing_cotter').common(shaft).Volume,0.0)
    check('cotter fits the slotted nut',world('InputHousing_cotter').common(world('InputHousing_nut')).Volume,0.0)
    check('packing contacts coupling surface',world('InputHousing_felt').distToShape(world('InputHousing_coupling'))[0],0.0)
    for a,b in [('InputBearing1_inner_race','InputHousing_coupling'),('InputHousing_coupling','InputHousing_washer'),('InputHousing_washer','InputHousing_nut')]:
        check(a+' axially seats '+b,world(a).distToShape(world(b))[0],0.0)
    exchange=Part.Shape();exchange.read(str(out/'TransmissionInputParts.step'));unmatched=list(exchange.Solids)
    for name in ['InputHousing_coupling','InputHousing_housing','InputBearing1_cage','CenterBevelDrive_pinion']:
        a=world(name);index=min(range(len(unmatched)),key=lambda n:(a.CenterOfMass-unmatched[n].CenterOfMass).Length);b=unmatched.pop(index)
        b.translate(App.Vector(.25,0,0));fuzzy=min(.0001,max(1e-7,a.getTolerance(1)+b.getTolerance(1)))
        check('negative: displaced STEP '+name,a.cut(b,fuzzy).Volume+b.cut(a,fuzzy).Volume>1,True)
    assert sha(native)==report['native_sha256']
    result=dict(passed=all(r['passed'] for r in checks),checks=checks,check_count=len(checks),native_sha256=sha(native),
        report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),scope='Nominal saved geometry, assembly passages and commercial decomposition; no load, preload, sealing or complete transmission qualification.')
    write(out/'interface_checks.json',result);print('PASS' if result['passed'] else 'FAIL',len(checks),[r for r in checks if not r['passed']],flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
