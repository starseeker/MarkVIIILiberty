"""Independent saved-native interface, identity and STEP checks for clutch drive."""
import argparse,json,math,subprocess,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_drive_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'check_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    r=read(out/'report.json');native=out/'TransmissionWithClutchDrive.FCStd';assert sha(native)==r['native_sha256']
    for path,h in r['input_hashes'].items():assert sha(REPO/path)==h,path
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    origin=doc.TransmissionCore.Placement.Base;s={}
    for n,i in byid.items():s[n]=i['shape'].copy();s[n].translate(-origin)
    c=r['controls'];d=r['details'];b=d['belt'];md=r['mount_details'];mc=r['mount_controls'];pc=r['pump_controls'];checks=[]
    def ck(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=passed))
    def zero(name,shape):ck(name,shape.Volume,0.0)
    def gap(name,a,b,want=0.0):ck(name,a.distToShape(b)[0],want)
    def shift(shape,v):out=shape.copy();out.translate(App.Vector(*v));return out
    def xc(rad,a,b,y=0,z=0):return Part.makeCylinder(rad,b-a,App.Vector(a,y,z),App.Vector(1,0,0))
    def zc(rad,a,b,x,y):return Part.makeCylinder(rad,b-a,App.Vector(x,y,a))
    def ids(i):return json.loads(getattr(i['object'],'SurveyIds',getattr(i['target'],'SurveyIds','[]')))
    ck('1520 unique physical leaves',len(byid),1520)
    ck('30 new physical occurrences',len(r['new_ids']),30)
    ck('valid single solids for114 affected leaves',all(s[n].isValid() and len(s[n].Solids)==1 for n in r['affected_ids']))
    sources=read(HERE/'clutch_drive_sources.json');rows={x['record_id']:x for x in sources['records']}
    expected={rows[rid]['part_ids'][0]:n for rid,n in [('SNL:34:012',1),('SNL:74:027',2),('SNL:83:035',1),('SNL:211:031',1),('SNL:31:013',24),('SNL:18:011',1)]}
    ck('source identity expansion for30 pieces',dict(Counter(pid for n in r['new_ids'] for pid in ids(byid[n]))),expected)
    sets={}
    for n in r['new_ids']:
        if n.startswith('ClutchDrive_Set'):sets.setdefault(n.rsplit('_',1)[0],[]).append(byid[n]['object'].SetPiece)
    ck('eight sets with separate bolt nut and washer',len(sets)==8 and all(sorted(v)==['bolt','nut','washer'] for v in sets.values()))
    ck('half covers reuse one definition',byid['ClutchDrive_HalfCover1']['target']==byid['ClutchDrive_HalfCover2']['target'])
    ck('shaft keeps SNL identity distinct from handbook',ids(byid['ClutchDrive_shaft'])==['P_6bc6b194198fd225'])
    ck('belt belongs to fuel pressure',byid['ClutchDrive_belt']['system'],'FuelPressure')
    drum=s['ClutchDrive_drum'];housing=s['ClutchDrive_box'];shaft=s['ClutchDrive_shaft'];belt=s['ClutchDrive_belt']
    flange=s['InputHousing_coupling'];covers=[s['ClutchDrive_HalfCover'+str(n)] for n in [1,2]]
    gap('stop drum web seats on M246 flange',drum,flange)
    gap('cover halves meet at split plane',*covers)
    for n,cover in enumerate(covers,1):
        gap(f'half{n} seats on drum web',cover,drum);gap(f'half{n} seats on M855',cover,housing)
        ck(f'half{n} translates into web as negative control',shift(cover,[-.2,0,0]).common(drum).Volume>.01)
    gap('captured head rear endplay',shaft,Part.makeCompound(covers),c['head_axial_gap'])
    # Isolate the retaining corner so the running bore does not set this distance.
    witness=xc(4,c['head_end']+c['head_axial_gap'],c['head_end']+c['head_axial_gap']+.2,30,25)
    zero('M855 retaining material beyond shaft head',witness.cut(housing))
    gap('captured head forward endplay',shaft,witness,c['head_axial_gap'])
    for sign,receiver in [(-1,Part.makeCompound(covers)),(1,housing)]:
        ck(f'axial stop prevents shaft displacement{sign}',shift(shaft,[sign*.4,0,0]).common(receiver).Volume>.01)
    turned=shaft.copy();turned.rotate(App.Vector(),App.Vector(1,0,0),2)
    ck('head/socket transmit torque after radial clearance',turned.common(housing).Volume>.01)
    bore=xc(c['shaft_radius'],c['head_end']+1,c['box_end']+.1)
    zero('shaft passage is continuous through front of box',bore.common(housing))
    ck('HB-transferred overall shaft length',shaft.BoundBox.XLength,285.75)
    middle=xc(25.39,c['box_end']+1,d['spline_start']-1)
    zero('HB-transferred2in shaft body present',middle.cut(shaft))
    spline_slice=shaft.common(Part.makeBox(c['spline_length']-2,150,150,App.Vector(d['spline_start']+1,-75,-75)))
    zero('enlarged spline stays within transferred4.359in OD',spline_slice.cut(xc(55.3593,d['spline_start'],d['shaft_end'])))
    # Count occupied sectors of an independent radial sample beyond the root.
    occupied=[];rr=(c['spline_root_radius']+c['spline_radius'])/2
    for n in range(720):
        angle=2*math.pi*(n+.23)/720
        occupied.append(shaft.isInside(App.Vector(d['shaft_end']-3,rr*math.cos(angle),rr*math.sin(angle)),1e-6,False))
    ck('ten distinct external spline teeth',sum(occupied[n] and not occupied[n-1] for n in range(720)),10)
    # Matching eight-axis bores, fastener seating and usable nut access.
    grip=flange.fuse(drum).fuse(Part.makeCompound(covers)).fuse(housing)
    for n in range(1,9):
        theta=math.radians(22.5+(n-1)*45);y=68*math.cos(theta);z=68*math.sin(theta)
        bolt=s[f'ClutchDrive_Set{n}_Bolt'];washer=s[f'ClutchDrive_Set{n}_Washer'];nut=s[f'ClutchDrive_Set{n}_Nut']
        gap(f'set{n} head on transmission flange',bolt,flange)
        gap(f'set{n} washer on coupling box',washer,housing)
        gap(f'set{n} nut on washer',nut,washer)
        gap(f'set{n} smooth nut/shank clearance',nut,bolt,c['nut_gap'])
        ck(f'set{n} printed2-7/8in underhead length',bolt.BoundBox.XLength-c['bolt_head_height'],73.025)
        ck(f'set{n} shank protrudes past nut',bolt.BoundBox.XMax-nut.BoundBox.XMax,d['bolt_protrusion'])
        zero(f'set{n} continuous half-inch passage',xc(6.34,475,530.01,y,z).common(grip))
        zero(f'set{n} nut access from open front',xc(12,530.1,584,y,z).common(housing))
        ck(f'set{n} head advance hits flange',shift(bolt,[.2,0,0]).common(flange).Volume>.01)
        ck(f'set{n} nut advance hits washer',shift(nut,[-.2,0,0]).common(washer).Volume>.01)
    # Shaft-fit region of existing M246 must be unchanged by new flange holes.
    parent=App.openDocument(str(HERE/'air_pump_mount_build/TransmissionWithAirPump.FCStd'));parent.recompute()
    old={i['id']:i for i in leaves(parent.Root)}['InputHousing_coupling']['shape'].copy();old.translate(-origin)
    protected=xc(55,300,491)
    zero('M246 spline and retaining-nut pocket preserved missing',old.common(protected).cut(flange))
    zero('M246 spline and retaining-nut pocket preserved added',flange.common(protected).cut(old))
    # Closed physical loop fits both V grooves, with contact on flanks.
    pulley=s['AirPump_pulley'];C=b['center_distance'];rd=b['drive_pitch_radius'];rp=b['pump_pitch_radius']
    alpha=math.asin((rd-rp)/C);length=2*C*math.cos(alpha)+rd*(math.pi+2*alpha)+rp*(math.pi-2*alpha)
    ck('closed pitch path equals printed54in under stated convention',length,1371.6)
    ck('physical belt single closed-loop solid',len(belt.Solids)==1 and belt.isValid())
    aperture=Part.makeBox(2,40,C-rd-rp-40,App.Vector(c['groove_plane']-1,-20,rd+20))
    zero('belt loop retains an open central aperture',belt.common(aperture))
    gap('belt contacts pump groove flanks',belt,pulley)
    gap('belt contacts drive groove flanks',belt,drum)
    zero('belt does not penetrate pump pulley',belt.common(pulley));zero('belt does not penetrate stop drum',belt.common(drum))
    ck('axially shifted belt detects pulley misalignment',shift(belt,[.3,0,0]).common(pulley).Volume>.01)
    ck('axially shifted belt detects driver misalignment',shift(belt,[.3,0,0]).common(drum).Volume>.01)
    ck('lowered belt detects driver radial interference',shift(belt,[0,0,.3]).common(drum).Volume>.01)
    ck('pump and driver groove centre planes match',420+(pc['pulley_rim_start']+pc['pulley_rim_end'])/2,c['groove_plane'])
    # Changed support height retains full existing seated stacks on both sides.
    base=s['AirPump_base'];top=md['rail_top'];bottom=md['rail_bottom']
    for row in md['datums']:
        name='PumpMount_'+row['side'];bracket=s[name+'_Bracket']
        gap(name+' raised pump foot seats on rail',base,bracket)
        gap(name+' rear nut stays seated',s[name+'_MX98_Nut'],bracket)
        gap(name+' lower washer supports raised rail',s[name+'_MX99_LowerWasher'],bracket)
        gap(name+' half nut supports lower washer',s[name+'_MX99_HalfNut'],s[name+'_MX99_LowerWasher'])
        gap(name+' upper washer seats on raised rail',s[name+'_MX99_UpperWasher'],bracket)
        gap(name+' upper nut seats on washer',s[name+'_MX99_SmallNut'],s[name+'_MX99_UpperWasher'])
        for n,(x,y,z) in enumerate(row['foot_axes'],1):
            gap(name+f' base{n} bolt head seats',s[name+f'_Base{n}_Bolt'],base)
            gap(name+f' base{n} washer seats',s[name+f'_Base{n}_Washer'],bracket)
            gap(name+f' base{n} nut seats',s[name+f'_Base{n}_Nut'],s[name+f'_Base{n}_Washer'])
            zero(name+f' base{n} hole passes pump and rail',zc(4.76,bottom-.1,top+pc['foot_stock']+.1,x,y).common(base.fuse(bracket)))
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__))))
    print('Independent',len(checks),'checks; failed',json.dumps([x for x in checks if not x['passed']]),flush=True)
    mass=calculator(out/'check_runtime/mass');keys=read(out/'definition_order.json')
    imported=Part.Shape();path=out/'ClutchDriveDefinitions.step';imported.read(str(path))
    assert sha(path)==r['definition_step_sha256'] and imported.isValid() and len(imported.Solids)==len(keys)
    remaining=list(imported.Solids);exchange=[]
    for key in keys:
        one=doc.getObject(key).Shape.Solids[0]
        idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length+abs(one.Volume-remaining[j].Volume)/max(one.Area,1))
        two=remaining.pop(idx);ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        raw_missing=one.cut(two).Volume;raw_added=two.cut(one).Volume
        missing=one.cut(two,fuzzy);added=two.cut(one,fuzzy)
        ma,mb=mass(one,key+'_native'),mass(two,key+'_step');dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length;bound=(one.Area+two.Area)/2*(ta+tb)
        passed=raw_missing<1e-5 and raw_added<1e-5 and not missing.Faces and not added.Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=bound and dc<max(1e-6,ta+tb)
        exchange.append(dict(definition=key,passed=passed,raw_missing_mm3=raw_missing,raw_added_mm3=raw_added,
            volume_difference_mm3=dv,centroid_difference_mm=dc,surface_tolerance_bound_mm3=bound,native_tolerance=ta,step_tolerance=tb))
        write(out/'exchange_progress.json',dict(last=key,completed=len(exchange),failed=[x for x in exchange if not x['passed']]))
    write(out/'exchange_checks.json',dict(passed=all(x['passed'] for x in exchange),checks=exchange,native_sha256=sha(native),step_sha256=sha(path),checker_sha256=sha(Path(__file__))))
    print('Definition STEP',len(exchange),'checks; failed',json.dumps([x for x in exchange if not x['passed']]),flush=True)
    assembly=Part.Shape();path=out/'ClutchDriveInstallation.step';assembly.read(str(path))
    assert sha(path)==r['step_sha256'] and assembly.isValid() and len(assembly.Solids)==114
    remaining=list(assembly.Solids);placed=[]
    for n in r['step_ids']:
        one=byid[n]['shape'].Solids[0];idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length)
        two=remaining.pop(idx);ma,mb=mass(one,n+'_native'),mass(two,n+'_step')
        dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length;dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        bound=(one.Area+two.Area)/2*(one.getTolerance(1)+two.getTolerance(1))
        placed.append(dict(id=n,passed=dc<max(1e-6,one.getTolerance(1)+two.getTolerance(1)) and dv<bound,
            centroid_difference_mm=dc,volume_difference_mm3=dv,surface_tolerance_bound_mm3=bound))
    write(out/'assembly_exchange_checks.json',dict(passed=all(x['passed'] for x in placed),checks=placed,native_sha256=sha(native),step_sha256=sha(path),
        scope='114 affected placed solids: count,validity,centroid and explicit-accuracy mass; detailed geometry separately checked for22 definitions.',checker_sha256=sha(Path(__file__))))
    print('Placed STEP',len(placed),'checks; failed',json.dumps([x for x in placed if not x['passed']]),flush=True)
    sys.exit(0 if all(x['passed'] for x in checks+exchange+placed) else 1)
finally:runtime.close()
