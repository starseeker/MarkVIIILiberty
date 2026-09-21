"""Check saved front-clutch geometry, fitted interfaces and STEP exchange."""
import argparse,json,math,subprocess,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'front_clutch_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'check_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    r=read(out/'report.json');native=out/'TransmissionWithFrontClutch.FCStd';assert sha(native)==r['native_sha256']
    for path,h in r['input_hashes'].items():assert sha(REPO/path)==h,path
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    s={}
    for n,i in byid.items():s[n]=i['shape'].copy();s[n].translate(-origin)
    c=r['controls'];dc=r['drive_controls'];d=r['details'];checks=[]
    def ck(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=passed))
        write(out/'check_progress.json',dict(last=name,completed=len(checks),failed=[x for x in checks if not x['passed']]))
    def zero(name,shape):ck(name,shape.Volume,0.0)
    def gap(name,a,b,want=0):ck(name,a.distToShape(b)[0],float(want))
    def shifted(shape,xyz):q=shape.copy();q.translate(App.Vector(*xyz));return q
    def xc(rad,a,b,y=0,z=0):return Part.makeCylinder(rad,b-a,App.Vector(a,y,z),App.Vector(1,0,0))
    def zc(rad,a,b,x,y):return Part.makeCylinder(rad,b-a,App.Vector(x,y,a))
    def ids(i):return json.loads(getattr(i['object'],'SurveyIds',getattr(i['target'],'SurveyIds','[]')))
    ck('1530 unique physical leaves',len(byid),1530)
    ck('10 added occurrences',len(r['new_ids']),10)
    ck('12 affected valid single solids',all(s[n].isValid() and len(s[n].Solids)==1 for n in r['affected_ids']))
    ck('source identity expansion',dict(Counter(pid for n in r['new_ids'] for pid in ids(byid[n]))),
        {'P_53a7f4b7d5250df7':1,'P_aa2979bfcb3bde26':2,'P_7e06cb0aa7aaec65':1,'P_2a3cb30ed643c820':6})
    ck('main-clutch SH849C not misassigned to external spring',all('P_4ad519ba5bd5d56b' not in ids(byid[n]) for n in r['new_ids']))
    ck('all new occurrences owned by drivetrain',all(byid[n]['system']=='Drivetrain' for n in r['new_ids']))
    ck('half flanges share one definition',byid['FrontClutch_UpperFlange']['target']==byid['FrontClutch_LowerFlange']['target'])
    for n in [1,2]:
        ck(f'fastener set{n} expands to bolt nut washer',sorted(byid[f'FrontClutch_Set{n}_{k}']['object'].SetPiece for k in ['Bolt','Nut','Washer']),['bolt','nut','washer'])
    upper=s['FrontClutch_UpperFlange'];lower=s['FrontClutch_LowerFlange'];shaft=s['ClutchDrive_shaft'];receiver=s['ClutchDrive_box']
    coupling=s['FrontClutch_Coupling'];spring=s['FrontClutch_Spring']
    gap('upper clamp nominal bore contact',upper,shaft);gap('lower clamp nominal bore contact',lower,shaft)
    gap('split collar retains clamp gap',upper,lower,c['clamp_split_gap'])
    ck('upper collar displacement detects shaft interference',shifted(upper,[0,0,-.2]).common(shaft).Volume>.01)
    ck('lower collar displacement detects shaft interference',shifted(lower,[0,0,.2]).common(shaft).Volume>.01)
    for n,sign in enumerate([-1,1],1):
        bolt=s[f'FrontClutch_Set{n}_Bolt'];nut=s[f'FrontClutch_Set{n}_Nut'];washer=s[f'FrontClutch_Set{n}_Washer']
        gap(f'set{n} head bears on upper half',bolt,upper)
        gap(f'set{n} washer bears on lower half',washer,lower)
        gap(f'set{n} nut bears on washer',nut,washer)
        gap(f'set{n} smooth shank-nut clearance',bolt,nut,c['nut_gap'])
        ck(f'set{n} printed98.425 underhead length',bolt.BoundBox.ZLength-c['bolt_head_height'],98.425)
        ck(f'set{n} printed15.875 shank cylinder',bolt.common(zc(7.9374,-30,30,c['clamp_bolt_x'],sign*c['clamp_bolt_y'])).Volume,
            math.pi*7.9374**2*60,tol=1e-3)
        ck(f'set{n} useful thread protrusion',nut.BoundBox.ZMin-bolt.BoundBox.ZMin,4.7625)
        passage=zc(7.9374,-c['clamp_seat_z']-.1,c['clamp_seat_z']+.1,c['clamp_bolt_x'],sign*c['clamp_bolt_y'])
        zero(f'set{n} clear receiving passage through both halves',passage.common(upper.fuse(lower)))
        zero(f'set{n} bolt does not drill through cardan shaft',passage.common(shaft))
        ck(f'set{n} lowered head detects seating',shifted(bolt,[0,0,-.2]).common(upper).Volume>.01)
        ck(f'set{n} raised nut detects seating',shifted(nut,[0,0,.2]).common(washer).Volume>.01)
    gap('spring rear end seats on upper half flange',spring,upper)
    gap('spring rear end seats on lower half flange',spring,lower)
    gap('spring front end seats on coupling flange',spring,coupling)
    zero('spring clears coupling material',spring.common(coupling))
    ck('spring shift through front seat detects obstruction',shifted(spring,[.2,0,0]).common(coupling).Volume>.01)
    ck('spring shift through rear seat detects obstruction',shifted(spring,[-.2,0,0]).common(upper.fuse(lower)).Volume>.01)
    # A transformed trimmed NURBS face has a conservative bounding box. Measure
    # actual planar ground faces and prove no material extends beyond the seats.
    ground=[f for f in spring.Faces if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).x)>.999999]
    ck('spring has two axial ground faces',len(ground),2)
    stations=sorted(f.CenterOfMass.x for f in ground)
    ck('rear ground face on selected flange datum',stations[0],c['spring_rear_seat'])
    ck('interpreted installed coil envelope107.95',stations[-1]-stations[0],107.95,tol=1e-4)
    seat_slab=Part.makeBox(c['spring_length'],400,400,App.Vector(c['spring_rear_seat'],-200,-200))
    ck('all spring material lies between actual ground planes',len(spring.cut(seat_slab).Faces),0)
    spine=Part.Shape();spine.read(str(out/'spring_spine.brep'));assert sha(out/'spring_spine.brep')==r['spring_spine_sha256']
    points=spine.Edges[0].discretize(Number=1401);arr=np.array([[p.x,p.y,p.z] for p in points]);theta=np.unwrap(np.arctan2(arr[:,2],arr[:,1]))
    ck('saved NURBS centreline winds seven turns',float((theta[-1]-theta[0])/(2*math.pi)),7.0,tol=1e-5)
    radial=np.hypot(arr[:,1],arr[:,2]);ck('spine stays on selected mean cylinder',float(np.max(np.abs(radial-d['spring']['mean_radius'])))<1e-3)
    pitch=np.diff(arr[:,0])/np.diff(theta)*2*math.pi
    ck('near-closed end turn pitch follows selected gauge clearance',float(pitch[:195].mean()),c['spring_end_pitch'],tol=.002)
    ck('five free turns have greater pitch than end turns',float(pitch[250:1150].mean())>float(pitch[:195].mean())+.5)
    # Conservative helix-slope correction plus interpolation margin; this is a
    # geometric adjacent-turn clearance check, not spring-load analysis.
    minimum_pitch=float(pitch.min());bound=minimum_pitch/math.sqrt(1+(float(pitch.max())/(2*math.pi*float(radial.min())))**2)-.002
    ck('adjacent turns retain wire clearance at minimum pitch',bound>2*c['spring_wire_radius'])
    ck('spring curve axial rise retained',float(arr[-1,0]-arr[0,0]),d['spring']['centerline_rise'],tol=1e-5)
    gap('female spline has explicit radial/flank clearance',coupling,shaft,c['coupling_spline_gap'])
    turned=coupling.copy();turned.rotate(App.Vector(),App.Vector(1,0,0),1)
    ck('female spline carries torque after clearance',turned.common(shaft).Volume>.01)
    ck('coupling flange transferred9in diameter',coupling.BoundBox.YLength,228.6,tol=1e-4)
    shell=xc(63.49,c['coupling_rear']+2,d['coupling_flange_start']-c['coupling_flange_fillet']-2).cut(xc(60,c['coupling_rear']+1,d['coupling_flange_start']))
    zero('coupling tube retains transferred5in outer envelope',shell.cut(coupling))
    for n in range(6):
        t=2*math.pi*n/6;y=100*math.cos(t);z=100*math.sin(t)
        zero(f'future collar hole{n+1} open through flange',xc(6.49,d['coupling_flange_start']-.1,d['coupling_front']+.1,y,z).common(coupling))
    before=Part.Shape();before.read(str(out/'inputs/parent_shaft.brep'))
    ck('source-shaped shoulder blends add material',shaft.cut(before).Volume>10)
    zero('shoulder blending preserves all original shaft material',before.cut(shaft))
    ck('fillets leave shaft overall length unchanged',shaft.BoundBox.XLength,285.75)
    ck('shaft has two new toroidal shoulder surfaces',sum(type(f.Surface).__name__=='Toroid' for f in shaft.Faces)>=2)
    witness=xc(4,dc['head_end']+.2,dc['head_end']+.4,30,25)
    zero('M855 retains head stop beyond fillet relief',witness.cut(receiver))
    gap('forward axial head endplay retained',shaft,witness,.2)
    ck('forward shaft displacement still catches head stop',shifted(shaft,[.4,0,0]).common(receiver).Volume>.01)
    zero('blended shaft does not penetrate M855',shaft.common(receiver))
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__))))
    print('Independent',len(checks),'checks; failed',json.dumps([x for x in checks if not x['passed']]),flush=True)
    mass=calculator(out/'check_runtime/mass');keys=read(out/'definition_order.json');path=out/'FrontClutchDefinitions.step';imported=Part.Shape();imported.read(str(path))
    assert sha(path)==r['definition_step_sha256'] and imported.isValid() and len(imported.Solids)==len(keys)
    remaining=list(imported.Solids);exchange=[]
    for key in keys:
        one=doc.getObject(key).Shape.Solids[0]
        idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length+abs(one.Volume-remaining[j].Volume)/max(one.Area,1))
        two=remaining.pop(idx);ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        rm=one.cut(two).Volume;ra=two.cut(one).Volume;missing=one.cut(two,fuzzy);added=two.cut(one,fuzzy)
        ma,mb=mass(one,key+'_native'),mass(two,key+'_step');dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        dcg=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length;bound=(one.Area+two.Area)/2*(ta+tb)
        passed=rm<1e-5 and ra<1e-5 and not missing.Faces and not added.Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=bound and dcg<max(1e-6,ta+tb)
        exchange.append(dict(definition=key,passed=passed,raw_missing_mm3=rm,raw_added_mm3=ra,volume_difference_mm3=dv,
            centroid_difference_mm=dcg,surface_tolerance_bound_mm3=bound,native_tolerance=ta,step_tolerance=tb))
        write(out/'exchange_progress.json',dict(completed=len(exchange),last=key,failed=[x for x in exchange if not x['passed']]))
    write(out/'exchange_checks.json',dict(passed=all(x['passed'] for x in exchange),checks=exchange,native_sha256=sha(native),step_sha256=sha(path),checker_sha256=sha(Path(__file__))))
    print('Definition STEP',len(exchange),'failed',json.dumps([x for x in exchange if not x['passed']]),flush=True)
    path=out/'FrontClutchInstallation.step';assembly=Part.Shape();assembly.read(str(path))
    assert sha(path)==r['step_sha256'] and assembly.isValid() and len(assembly.Solids)==12
    remaining=list(assembly.Solids);placed=[]
    for n in r['step_ids']:
        one=byid[n]['shape'].Solids[0];idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length)
        two=remaining.pop(idx);ma,mb=mass(one,n+'_native'),mass(two,n+'_step')
        dcg=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length;dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        bound=(one.Area+two.Area)/2*(one.getTolerance(1)+two.getTolerance(1))
        placed.append(dict(id=n,passed=dcg<max(1e-6,one.getTolerance(1)+two.getTolerance(1)) and dv<bound,
            centroid_difference_mm=dcg,volume_difference_mm3=dv,surface_tolerance_bound_mm3=bound))
    write(out/'assembly_exchange_checks.json',dict(passed=all(x['passed'] for x in placed),checks=placed,native_sha256=sha(native),step_sha256=sha(path),
        scope='12affected placed solids:validity,count,mass and centroid;8definitions checked separately for geometry.',checker_sha256=sha(Path(__file__))))
    print('Placed STEP',len(placed),'failed',json.dumps([x for x in placed if not x['passed']]),flush=True)
    sys.exit(0 if all(x['passed'] for x in checks+exchange+placed) else 1)
finally:runtime.close()
