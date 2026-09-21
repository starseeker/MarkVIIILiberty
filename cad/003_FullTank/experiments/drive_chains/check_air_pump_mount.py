"""Check saved pump installation: receiving material, contacts, provenance and STEP."""
import argparse,json,math,subprocess,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'air_pump_mount_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'check_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    report=read(out/'report.json');native=out/'TransmissionWithAirPump.FCStd'
    assert sha(native)==report['native_sha256']
    for path,h in report['input_hashes'].items():assert sha(REPO/path)==h,path
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    origin=doc.TransmissionCore.Placement.Base;s={}
    for n,i in byid.items():
        s[n]=i['shape'].copy();s[n].translate(-origin)
    c=report['controls'];pc=report['pump_controls'];d=report['details'];top=d['rail_top'];bottom=d['rail_bottom']
    checks=[]
    def ck(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=passed))
    def zero(name,shape):ck(name,shape.Volume,0.0)
    def gap(name,a,b,want=0.0):ck(name,a.distToShape(b)[0],want)
    def shifted(shape,v):result=shape.copy();result.translate(App.Vector(*v));return result
    def zc(r,x,y,a,b):return Part.makeCylinder(r,b-a,App.Vector(x,y,a))
    def xc(r,a,b,y,z):return Part.makeCylinder(r,b-a,App.Vector(a,y,z),App.Vector(1,0,0))
    cover=s['CenterTransmissionCore_bevel_cover'];house=s['InputHousing_housing'];base=s['AirPump_base']
    ck('1490 unique physical leaves',len(byid),1490)
    new=report['new_ids'];ck('83 added leaves:51 pump and32 supports/fasteners',len(new),83)
    ck('affected saved leaves valid single solids',all(s[n].isValid() and len(s[n].Solids)==1 for n in new+report['changed_ids']))
    def identities(i):return json.loads(getattr(i['object'],'SurveyIds',getattr(i['target'],'SurveyIds','[]')))
    actual=Counter(pid for n in new if n.startswith('PumpMount_') for pid in identities(byid[n]))
    expected={'P_cec20ebdc71e3183':1,'P_3768344358815bd6':1,'P_6be2db25439ff6f1':2,
        'P_fa532874f22959fa':2,'P_45c99004b6de95df':2,'P_439737f0c7a6fd2c':2,'P_176800c10e8abdc4':2,
        'P_ca31ef7ef32a21b2':2,'P_59a6582b5f14ece2':2,'P_f794938be06e19d3':4,'P_55c06904318526e8':12}
    ck('physical installation identity expansion',dict(actual),expected)
    sets={}
    for n in new:
        if n.startswith('PumpMount_') and '_Base' in n:
            sets.setdefault(n.rsplit('_',1)[0],[]).append(byid[n]['object'].SetPiece)
    ck('four sets each have one bolt,nut,washer',len(sets)==4 and all(sorted(v)==['Bolt','Nut','Washer'] for v in sets.values()))
    ck('fuel-pressure ownership of pump and base hardware',all(byid[n]['system']=='FuelPressure' for n in new if n.startswith('AirPump_') or '_Base' in n))
    ck('drivetrain owns brackets and transmission studs',all(byid[n]['system']=='Drivetrain' for n in new if n.startswith('PumpMount_') and '_Base' not in n))
    for row in d['datums']:
        name='PumpMount_'+row['side'];y=row['rear_axis'][1];z=row['rear_axis'][2];x,fy,seat=row['front_axis']
        bracket=s[name+'_Bracket'];stud=s[name+'_MX98_Stud'];cn=s[name+'_MX98_Nut'];pin=s[name+'_MX98_Cotter']
        gap(name+' rear lug seated on cover',bracket,cover)
        gap(name+' castle nut seated on lug',cn,bracket)
        gap(name+' rear stud nominal clearance',stud,cover,c['receiver_gap'])
        gap(name+' castle nut bore clearance',cn,stud,c['nut_bore_gap'])
        gap(name+' cotter cross-hole clearance',pin,stud,.05)
        ck(name+' MX98 printed73.025 length',stud.BoundBox.XLength,73.025)
        ck(name+' castle nut lies within SAE thread',d['rear_nut_seat']>=d['rear_sae_thread'][0] and d['rear_nut_seat']+c['mx98_nut_height']<=d['rear_sae_thread'][1])
        ck(name+' advancing castle nut penetrates lug',shifted(cn,[-.2,0,0]).common(bracket).Volume>.01)
        bore=xc(6.34,d['rear_stud_start'],c['rear_face_x']+.01,y,z)
        zero(name+' complete rear stud receiving bore',bore.common(cover))
        floor=xc(5,d['rear_stud_start']-c['blind_gap']-.3,d['rear_stud_start']-c['blind_gap']-.1,y,z)
        zero(name+' rear receiver retains blind floor',floor.cut(cover))
        for sign in [-1,1]:
            # Independent witness for each straight cotter leg through the stud.
            wire=(c['cotter_diameter']-1.21)/2
            leg=Part.makeCylinder(wire-.03,10,App.Vector(d['rear_cotter_station'],y-5,z+sign*1.21/2),App.Vector(0,1,0))
            zero(name+f' cotter leg{sign} present',leg.cut(pin))
        fs=s[name+'_MX99_Stud'];jam=s[name+'_MX102_JamNut'];half=s[name+'_MX99_HalfNut'];small=s[name+'_MX99_SmallNut']
        lw=s[name+'_MX99_LowerWasher'];uw=s[name+'_MX99_UpperWasher']
        gap(name+' MX102 seats on housing boss',jam,house)
        gap(name+' MX102 bore clearance',jam,fs,c['nut_bore_gap'])
        ck(name+' printed jamnut thickness9.525',jam.BoundBox.ZLength,9.525)
        gap(name+' half-inch nut supports lower washer',half,lw)
        gap(name+' lower washer supports rail',lw,bracket)
        gap(name+' upper washer bears on rail',uw,bracket)
        gap(name+' upper nut bears on washer',small,uw)
        gap(name+' upper nut stud clearance',small,fs,c['nut_bore_gap'])
        gap(name+' half-inch nut stud clearance',half,fs,c['nut_bore_gap'])
        ck(name+' lowering upper nut detects seating',shifted(small,[0,0,-.2]).common(uw).Volume>.01)
        bore=zc(6.34,x,fy,d['front_stud_lower'],seat+.01)
        zero(name+' front stud receiving bore is continuous',bore.common(house))
        floor=zc(4,x,fy,d['front_stud_lower']-c['blind_gap']-.3,d['front_stud_lower']-c['blind_gap']-.1)
        zero(name+' front receiver has blind floor',floor.cut(house))
        gap(name+' pump foot on bracket',base,bracket)
        for n,(bx,by,bz) in enumerate(row['foot_axes'],1):
            bolt=s[name+f'_Base{n}_Bolt'];washer=s[name+f'_Base{n}_Washer'];nut=s[name+f'_Base{n}_Nut']
            gap(name+f' base{n} head seats on casting',bolt,base)
            gap(name+f' base{n} washer seats on bracket',washer,bracket)
            gap(name+f' base{n} nut seats on washer',nut,washer)
            gap(name+f' base{n} nut shank clearance',nut,bolt,c['nut_bore_gap'])
            ck(name+f' base{n} underhead length',bolt.BoundBox.ZLength-c['base_bolt_head_height'],31.75)
            ck(name+f' base{n} thread protrudes past nut',nut.BoundBox.ZMin-bolt.BoundBox.ZMin>2)
            bore=zc(4.76,bx,by,bottom-.1,top+pc['foot_stock']+.1)
            zero(name+f' base{n} continuous through-bore',bore.common(base.fuse(bracket)))
            ck(name+f' base{n} lowered head enters casting',shifted(bolt,[0,0,-.2]).common(base).Volume>.01)
    # Adding mounting material must not invade any formerly clear bearing bore.
    oldhouse=Part.Shape();oldhouse.read(str(out/'inputs/parent_housing.brep'))
    cylinder=xc(74.70,c['front_stud_x']-17,c['front_stud_x']+17,0,0)
    zero('M250 mounting bosses preserve original cup passage',house.cut(oldhouse).common(cylinder))
    ck('pump pulley plane beyond the coupling flange',d['belt']['plane_x']-16>s['InputHousing_coupling'].BoundBox.XMax)
    # Independent belt-length expression, without importing the geometry builder.
    rr=d['belt']['drive_pitch_radius'];pr=d['belt']['pump_pitch_radius'];cc=d['belt']['center_distance'];alpha=math.asin((rr-pr)/cc)
    length=2*cc*math.cos(alpha)+rr*(math.pi+2*alpha)+pr*(math.pi-2*alpha)
    ck('conditional belt equation closes to printed54in',length,1371.6)
    ck('new pump height is distinct from former clearance-only210mm',cc>300)
    write(out/'independent_checks.json',dict(passed=all(r['passed'] for r in checks),checks=checks,
        native_sha256=sha(native),checker_sha256=sha(Path(__file__))))
    print('Independent',len(checks),'checks; failed',json.dumps([r for r in checks if not r['passed']]),flush=True)
    mass=calculator(out/'check_runtime/mass');keys=read(out/'definition_order.json')
    imported=Part.Shape();definitions=out/'AirPumpMountDefinitions.step';imported.read(str(definitions))
    assert sha(definitions)==report['definition_step_sha256'] and imported.isValid() and len(imported.Solids)==len(keys)
    remaining=list(imported.Solids);rows=[]
    for key in keys:
        if key in ['cover','housing','pump_base']:
            n={'cover':'CenterTransmissionCore_bevel_cover','housing':'InputHousing_housing','pump_base':'AirPump_base'}[key]
            one=byid[n]['target'].Shape.Solids[0]
        else:one=doc.getObject('Def_PumpMount_'+key).Shape.Solids[0]
        idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length+abs(one.Volume-remaining[j].Volume)/max(one.Area,1))
        two=remaining.pop(idx);ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        raw_missing=one.cut(two).Volume;raw_added=two.cut(one).Volume
        missing=one.cut(two,fuzzy);added=two.cut(one,fuzzy)
        ma,mb=mass(one,key+'_native'),mass(two,key+'_step');dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length;bound=(one.Area+two.Area)/2*(ta+tb)
        passed=raw_missing<1e-5 and raw_added<1e-5 and not missing.Faces and not added.Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=bound and dc<max(1e-6,ta+tb)
        rows.append(dict(definition=key,passed=passed,raw_missing_mm3=raw_missing,raw_added_mm3=raw_added,
            volume_difference_mm3=dv,centroid_difference_mm=dc,surface_tolerance_bound_mm3=bound,native_tolerance=ta,step_tolerance=tb))
    write(out/'exchange_checks.json',dict(passed=all(r['passed'] for r in rows),checks=rows,native_sha256=sha(native),step_sha256=sha(definitions),checker_sha256=sha(Path(__file__))))
    print('Definition STEP',len(rows),'checks; failed',json.dumps([r for r in rows if not r['passed']]),flush=True)
    assembly=Part.Shape();path=out/'AirPumpInstallation.step';assembly.read(str(path))
    assert sha(path)==report['step_sha256'] and assembly.isValid() and len(assembly.Solids)==85
    remaining=list(assembly.Solids);placed=[]
    for n in report['step_ids']:
        one=byid[n]['shape'].Solids[0];idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length)
        two=remaining.pop(idx);ma,mb=mass(one,n+'_native'),mass(two,n+'_step')
        delta=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length;dv=abs(ma['volume_mm3']-mb['volume_mm3'])
        bound=(one.Area+two.Area)/2*(one.getTolerance(1)+two.getTolerance(1))
        placed.append(dict(id=n,passed=delta<max(1e-6,one.getTolerance(1)+two.getTolerance(1)) and dv<bound,
            centroid_difference_mm=delta,volume_difference_mm3=dv,surface_tolerance_bound_mm3=bound))
    write(out/'assembly_exchange_checks.json',dict(passed=all(r['passed'] for r in placed),checks=placed,native_sha256=sha(native),step_sha256=sha(path),
        scope='83 added pieces plus2 revised receivers;85 placed solids checked for validity,count,centroid and explicit-accuracy mass.',checker_sha256=sha(Path(__file__))))
    print('Placed STEP',len(placed),'checks; failed',json.dumps([r for r in placed if not r['passed']]),flush=True)
    sys.exit(0 if all(r['passed'] for r in checks+rows+placed) else 1)
finally:runtime.close()
