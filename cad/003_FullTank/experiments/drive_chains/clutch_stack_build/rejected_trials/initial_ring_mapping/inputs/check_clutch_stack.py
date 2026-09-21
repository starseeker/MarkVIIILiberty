"""Saved main-clutch stack, key engagement, retention and STEP exchange checks."""
import argparse,json,math,subprocess,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_stack_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'check_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    r=read(out/'report.json');native=out/'TransmissionWithClutchStack.FCStd';assert sha(native)==r['native_sha256']
    for path,h in r['input_hashes'].items():assert sha(REPO/path)==h,path
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    s={}
    for n,i in byid.items():s[n]=i['shape'].copy();s[n].translate(-origin)
    c=r['controls'];pc=r['parent_controls'];checks=[]
    def ck(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=passed))
        write(out/'check_progress.json',dict(last=name,completed=len(checks),failed=[x for x in checks if not x['passed']]))
    def zero(name,shape):ck(name,shape.Volume,0.0)
    def gap(name,a,b,want=0):ck(name,a.distToShape(b)[0],float(want))
    def moved(shape,xyz):q=shape.copy();q.translate(App.Vector(*xyz));return q
    def xc(rad,a,b):return Part.makeCylinder(rad,b-a,App.Vector(a,0,0),App.Vector(1,0,0))
    def ids(i):return json.loads(getattr(i['object'],'SurveyIds',getattr(i['target'],'SurveyIds','[]')))
    records={row['record_id']:row for row in read(out/'inputs/clutch_stack_sources.json')['records']}
    expected=Counter()
    for rid,count in [('SNL:17:016',1),('SNL:217:024',1),('SNL:67:018',1),('SNL:114:024',4),('SNL:165:001',1)]:
        for pid in records[rid]['part_ids']:expected[pid]+=count
    ck('1548 unique physical leaves',len(byid),1548);ck('eight added physical pieces',len(r['new_ids']),8)
    ck('nine affected valid single solids',all(s[n].isValid() and len(s[n].Solids)==1 for n in r['affected_ids']))
    ck('source inventory expansion',dict(Counter(pid for n in r['new_ids'] for pid in ids(byid[n]))),dict(expected))
    ck('new pieces owned by drivetrain',all(byid[n]['system']=='Drivetrain' for n in r['new_ids']))
    ck('four keys reuse one definition',len({byid[f'ClutchStack_Key{n}']['target'].Name for n in range(1,5)}),1)
    collar=s['ClutchCollar_collar'];bearing=s['ClutchStack_bearing'];sleeve=s['ClutchStack_sleeve'];support=s['ClutchStack_support'];snap=s['ClutchStack_snap']
    parent=Part.Shape();parent.read(str(out/'inputs/parent_collar.brep'));assert sha(out/'inputs/parent_collar.brep')==r['parent_collar_sha256']
    slab=xc(140,pc['joint_face']-.1,pc['joint_face']+pc['collar_lip_stock']-.01)
    zero('six-hole collar lip retains parent material',parent.common(slab).cut(collar))
    zero('six-hole collar lip adds no material',collar.common(slab).cut(parent))
    gap('existing end-ring front remains captured',s['ClutchCollar_ring'],collar)
    gap('existing coupling face still seats',s['FrontClutch_Coupling'],collar)
    for n in range(1,7):gap(f'existing screw{n} retains head seating',s[f'ClutchCollar_Screw{n}'],collar)
    gap('bearing OD seats in revised collar',bearing,collar)
    gap('sleeve flange seats in collar',sleeve,collar)
    gap('bearing rear seats against sleeve flange',bearing,sleeve)
    gap('bearing front seats against snap ring',bearing,snap)
    gap('snap ridge is seated in receiving groove',snap,collar)
    ck('bearing axial extent',bearing.BoundBox.XLength,c['bearing_front']-c['bearing_rear'])
    zero('bearing front journal bore is open',xc(c['bearing_front_bore_radius']-.01,c['relief_front']+6,c['bearing_front']+.1).common(bearing))
    zero('bearing front journal band has material',xc(c['bearing_front_bore_radius']+.4,c['relief_front']+6,c['bearing_front']-.1).cut(xc(c['bearing_front_bore_radius']+.1,c['relief_front']+5,c['bearing_front'])).cut(bearing))
    zero('bearing central relief stays open',xc(c['relief_radius']-.01,c['relief_rear']+6,c['relief_front']-6).common(bearing))
    ck('relief retains two toroidal blending surfaces',sum(type(f.Surface).__name__=='Toroid' for f in bearing.Faces),2)
    rear_band=xc(80,c['bearing_rear']+2,c['relief_rear']-2)
    gap('sleeve barrel nests in rear bearing with radial clearance',bearing.common(rear_band),sleeve.common(rear_band),.15)
    ck('sleeve overlaps rear bearing band',min(sleeve.BoundBox.XMax,bearing.BoundBox.XMax)-max(sleeve.BoundBox.XMin,bearing.BoundBox.XMin),58.0498)
    ck('HB sleeve length transfer',sleeve.BoundBox.XLength,68.2498)
    zero('sleeve minimum internal diameter remains open',xc(44.8337,pc['collar_bore_step']-.1,pc['collar_bore_step']+68.35).common(sleeve))
    x=pc['collar_bore_step']+35;radius=(44.8437+50.525)/2
    voids=[];lands=[]
    for n in range(24):
        theta=2*math.pi*n/24
        voids.append(not sleeve.isInside(App.Vector(x,radius*math.cos(theta),radius*math.sin(theta)),1e-6,True))
        theta+=math.pi/24
        lands.append(sleeve.isInside(App.Vector(x,radius*math.cos(theta),radius*math.sin(theta)),1e-6,True))
    ck('all24internal spline grooves exist',sum(voids),24);ck('all24intervening tooth lands retain material',sum(lands),24)
    ck('bearing radial displacement hits collar',moved(bearing,[0,.2,0]).common(collar).Volume>.01)
    ck('bearing aft displacement hits sleeve flange',moved(bearing,[-.2,0,0]).common(sleeve).Volume>.01)
    ck('bearing forward displacement hits snap ring',moved(bearing,[.2,0,0]).common(snap).Volume>.01)
    ck('sleeve aft displacement hits collar shoulder',moved(sleeve,[-.2,0,0]).common(collar).Volume>.01)
    ck('snap forward displacement hits groove wall',moved(snap,[.2,0,0]).common(collar).Volume>.01)
    ck('snap aft displacement hits groove wall',moved(snap,[-.2,0,0]).common(collar).Volume>.01)
    theta=math.radians(c['snap_gap_angle']);point=App.Vector((c['bearing_front']+c['snap_front'])/2,70*math.cos(theta),70*math.sin(theta))
    ck('snap ring has an actual split',not snap.isInside(point,1e-6,True))
    ck('snap ring is one physical piece',len(snap.Solids),1)
    gap('cone support has running clearance around collar',support,collar,.15)
    wire_gap=support.distToShape(s['ClutchCollar_wire'])[0]
    ck('cone support clears existing formed locking wire',wire_gap>2.5)
    ck('literal key bed retains radial wall stock',c['key_bed_radius']-c['main_bore_radius'],2.475)
    for n in range(1,5):
        key=s[f'ClutchStack_Key{n}'];local=key.copy();local.rotate(App.Vector(),App.Vector(1,0,0),-90*(n-1))
        ck(f'key{n} printed length transfer',local.BoundBox.XLength,107.95)
        ck(f'key{n} literal radial thickness transfer',local.BoundBox.YLength,19.05)
        ck(f'key{n} literal tangential width transfer',local.BoundBox.ZLength,9.525)
        gap(f'key{n} sits on receiving bed',key,collar)
        gap(f'key{n} clears cone-support groove',key,support,.1)
        theta=math.pi*(n-1)/2
        ck(f'key{n} inward displacement hits collar bed',moved(key,[0,-.2*math.cos(theta),-.2*math.sin(theta)]).common(collar).Volume>.01)
    turned=support.copy();turned.rotate(App.Vector(),App.Vector(1,0,0),1)
    ck('support angular displacement engages four keys',all(turned.common(s[f'ClutchStack_Key{n}']).Volume>.01 for n in range(1,5)))
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__))))
    print('Independent',len(checks),'checks; failed',json.dumps([x for x in checks if not x['passed']]),flush=True)
    mass=calculator(out/'check_runtime/mass');keys=read(out/'definition_order.json');path=out/'ClutchStackDefinitions.step';imported=Part.Shape();imported.read(str(path))
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
    path=out/'ClutchStackInstallation.step';assembly=Part.Shape();assembly.read(str(path))
    assert sha(path)==r['step_sha256'] and assembly.isValid() and len(assembly.Solids)==9
    remaining=list(assembly.Solids);placed=[]
    for n in r['step_ids']:
        one=byid[n]['shape'].Solids[0];idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length)
        two=remaining.pop(idx);ma,mb=mass(one,n+'_native'),mass(two,n+'_step')
        dcg=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length;dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        bound=(one.Area+two.Area)/2*(one.getTolerance(1)+two.getTolerance(1))
        placed.append(dict(id=n,passed=dcg<max(1e-6,one.getTolerance(1)+two.getTolerance(1)) and dv<bound,
            centroid_difference_mm=dcg,volume_difference_mm3=dv,surface_tolerance_bound_mm3=bound))
    write(out/'assembly_exchange_checks.json',dict(passed=all(x['passed'] for x in placed),checks=placed,native_sha256=sha(native),step_sha256=sha(path),
        scope='9affected placed solids:validity,count,mass and centroid;6definitions checked separately for geometry.',checker_sha256=sha(Path(__file__))))
    print('Placed STEP',len(placed),'failed',json.dumps([x for x in placed if not x['passed']]),flush=True)
    sys.exit(0 if all(x['passed'] for x in checks+exchange+placed) else 1)
finally:runtime.close()
