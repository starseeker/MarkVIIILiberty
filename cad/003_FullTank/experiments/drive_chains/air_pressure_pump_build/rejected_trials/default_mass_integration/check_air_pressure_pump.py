"""Inspect saved pump solids, catalogue counts, physical interfaces and STEP."""
import argparse
from collections import Counter
import json,math,sqlite3,subprocess,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=HERE/'air_pressure_pump_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'check_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],
            env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    report=read(out/'report.json');c=report['controls'];native=out/'AirPressurePump.FCStd'
    assert sha(native)==report['native_sha256']
    for path,h in report['input_hashes'].items():assert sha(REPO/path)==h,path
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    byid={i['id']:i for i in items};s={n:i['shape'] for n,i in byid.items()}
    checks=[]
    def ck(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=passed))
    def zero(name,shape):ck(name,shape.Volume,0.0)
    def shift(shape,v):q=shape.copy();q.translate(v);return q
    def zc(radius,a,b):return Part.makeCylinder(radius,b-a,App.Vector(0,0,a))
    def gap(name,one,two,value=0.0):ck(name,one.distToShape(two)[0],value)
    ck('51 unique physical leaves',len(byid),51)
    ck('all physical leaves valid single solids',all(i['shape'].isValid() and len(i['shape'].Solids)==1 for i in items))
    with sqlite3.connect(f'file:{REPO}/cad/001_Survey/mark_viii_parts.sqlite?mode=ro',uri=True) as db:
        expected=Counter({pid:int(q) for pid,q in db.execute('SELECT child_part_id,quantity_per_parent FROM assembly_edges WHERE parent_part_id=?',('P_dd55a02fabc8964b',))})
        ck('four catalogue mounting sets deferred',expected.pop('P_55c06904318526e8'),4)
        ck('shaft container occurs once',expected.pop('P_4cb854d17d3862c4'),1)
        expected.update({pid:int(q) for pid,q in db.execute('SELECT child_part_id,quantity_per_parent FROM assembly_edges WHERE parent_part_id=?',('P_4cb854d17d3862c4',))})
    actual=Counter(pid for i in items for pid in json.loads(i['target'].SurveyIds))
    ck('saved physical identities and counts match frozen survey expansion',dict(actual),dict(expected))
    base=s['AirPump_base'];shaft=s['AirPump_shaft'];pulley=s['AirPump_pulley'];key=s['AirPump_key']
    for station,x in enumerate(c['station_x']):
        eccentric=(1 if station==0 else -1)*c['cam_eccentricity']
        for sign,label in [(1,'Port'),(-1,'Starboard')]:
            name=label+str(station+1);n=App.Vector(0,sign/math.sqrt(2),1/math.sqrt(2))
            piston=s['AirPump_'+name+'_piston'];coil=s['AirPump_'+name+'_spring']
            cylinder=s['AirPump_'+name+'_cylinder'];plug=s['AirPump_'+name+'_displacement_plug']
            contact=App.Vector(x,eccentric,0)+n*c['cam_radius']
            gap(name+' cam contact point on shaft',shaft,Part.Vertex(contact))
            gap(name+' cam contact point on piston foot',piston,Part.Vertex(contact))
            ck(name+' inward piston displacement collides with cam',shift(piston,-n*.2).common(shaft).Volume>.01)
            gap(name+' piston running clearance in cylinder',piston,cylinder,c['cylinder_bore_radius']-c['piston_radius'])
            ck(name+' lateral piston shift detects lost guide clearance',shift(piston,App.Vector(.4,0,0)).common(cylinder).Volume>.01)
            gap(name+' spring bears on piston floor',coil,piston)
            gap(name+' spring bears on cylinder shoulder',coil,cylinder)
            ck(name+' outward spring shift enters shoulder',shift(coil,n*.25).common(cylinder).Volume>.001)
            ck(name+' inward spring shift enters piston floor',shift(coil,-n*.25).common(piston).Volume>.001)
            ck(name+' displacement plug clears piston',plug.distToShape(piston)[0]>.5)
            local_piston=byid['AirPump_'+name+'_piston']['target'].Shape
            zero(name+' hollow piston cup is open',zc(c['piston_inside_radius']-.1,c['piston_cup_start']+c['piston_floor_stock']+.1,c['piston_height']+.1).common(local_piston))
            ck(name+' piston cup retains floor',local_piston.isInside(App.Vector(0,0,c['piston_cup_start']+1),1e-7,False))
            gap(name+' flange seats on base',cylinder,base)
            for k in [1,2]:
                screw=s[f'AirPump_{name}_screw{k}']
                gap(name+f' screw{k} head seats on flange',screw,cylinder)
                ck(name+f' screw{k} nominal under-head length',byid[f'AirPump_{name}_screw{k}']['target'].Shape.BoundBox.ZLength-c['cylinder_bolt_head_height'],19.05)
    for label,sign in [('Rear',-1),('Front',1)]:
        bearing=s['AirPump_'+label+'Bearing'];bush=s['AirPump_'+label+'Bush']
        gap(label+' cover seats on base',bearing,base)
        gap(label+' bush flange seats on cover',bush,bearing)
        gap(label+' shaft running clearance',bush,shaft,c['journal_gap'])
        ck(label+' driven bush flange enters cover',shift(bush,App.Vector(-sign*.2,0,0)).common(bearing).Volume>.01)
        start=App.Vector(sign*(c['body_length']/2+.1),0,0);axis=App.Vector(sign,0,0)
        ring=Part.makeCylinder(24,.8,start,axis).cut(Part.makeCylinder(c['shaft_cavity_radius']+.1,1,start-axis*.1,axis))
        zero(label+' cover encloses complete crankcase opening rim',ring.cut(bearing))
        for k in [1,2,3]:gap(label+f' bearing screw{k} seats',s['AirPump_'+label+'BearingScrew'+str(k)],bearing)
    gap('pulley retained by shaft shoulder',pulley,shaft)
    gap('retaining nut bears on pulley',s['AirPump_shaft_nut'],pulley)
    ck('nut moved into hub collides',shift(s['AirPump_shaft_nut'],App.Vector(-.2,0,0)).common(pulley).Volume>.01)
    ck('key shifted across width interferes with shaft',shift(key,App.Vector(0,.2,0)).common(shaft).Volume>.001)
    ck('key shifted across width interferes with pulley',shift(key,App.Vector(0,.2,0)).common(pulley).Volume>.001)
    for x in [-c['foot_hole_x'],c['foot_hole_x']]:
        for y in [-c['foot_hole_y'],c['foot_hole_y']]:
            hole=Part.makeCylinder(9.525/2,c['foot_stock']+2,App.Vector(x,y,c['base_floor']-1))
            zero(f'base mounting bore{x,y} is open',hole.common(base))
    roof=c['bank_seat']*math.sqrt(2)
    vent=zc(1.4,c['shaft_cavity_radius']-.1,roof+2.5)
    zero('continuous axial vent from crankcase into air-hole cover',vent.common(base.fuse(s['AirPump_AirHoleCover'])))
    ck('51 core plus12 deferred mounting pieces reconciles63',len(items)+12,63)
    write(out/'independent_checks.json',dict(passed=all(r['passed'] for r in checks),checks=checks,
        native_sha256=sha(native),report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__))))
    print('Independent',len(checks),'checks; failed',json.dumps([r for r in checks if not r['passed']]),flush=True)
    # Validate every reusable definition, including both installed spring heights.
    step=out/'AirPressurePumpDefinitions.step';assert sha(step)==report['step_sha256']
    imported=Part.Shape();imported.read(str(step));keys=read(out/'definition_order.json')
    assert imported.isValid() and len(imported.Solids)==len(keys)
    unmatched=list(imported.Solids);mass=calculator(out/'check_runtime/mass');rows=[]
    for key in keys:
        one=doc.getObject('Def_AirPump_'+key).Shape.Solids[0]
        index=min(range(len(unmatched)),key=lambda i:(one.CenterOfMass-unmatched[i].CenterOfMass).Length+abs(one.Volume-unmatched[i].Volume)/max(one.Area,1))
        two=unmatched.pop(index);ta,tb=one.getTolerance(1),two.getTolerance(1)
        fuzzy=min(.0001,max(1e-7,ta+tb))
        raw_missing=one.cut(two).Volume;raw_added=two.cut(one).Volume
        missing=one.cut(two,fuzzy);added=two.cut(one,fuzzy)
        ma,mb=mass(one,key+'_native'),mass(two,key+'_step')
        dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length
        bound=(one.Area+two.Area)/2*(ta+tb)
        passed=(raw_missing<1e-5 and raw_added<1e-5 and not missing.Faces and not added.Faces
            and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=bound and dc<max(1e-6,ta+tb)
            and all(0<=m['estimated_relative_error']<1e-9 for m in [ma,mb]))
        rows.append(dict(definition=key,passed=passed,native_tolerance_mm=ta,step_tolerance_mm=tb,
            raw_missing_mm3=raw_missing,raw_added_mm3=raw_added,missing_mm3=missing.Volume,added_mm3=added.Volume,
            volume_difference_mm3=dv,surface_tolerance_bound_mm3=bound,centroid_difference_mm=dc,native_mass=ma,step_mass=mb))
        write(out/'exchange_progress.json',dict(completed=len(rows),failed=[r for r in rows if not r['passed']]))
    write(out/'exchange_checks.json',dict(passed=all(r['passed'] for r in rows),checks=rows,
        native_sha256=sha(native),step_sha256=sha(step),checker_sha256=sha(Path(__file__))))
    print('STEP',len(rows),'checks; failed',json.dumps([r for r in rows if not r['passed']]),flush=True)
    assembled_path=out/'AirPressurePump.step';assert sha(assembled_path)==report['assembly_step_sha256']
    assembled=Part.Shape();assembled.read(str(assembled_path));remaining=list(assembled.Solids);placements=[]
    assert assembled.isValid() and len(remaining)==51
    for item in items:
        one=item['shape'].Solids[0]
        idx=min(range(len(remaining)),key=lambda i:(one.CenterOfMass-remaining[i].CenterOfMass).Length)
        two=remaining.pop(idx)
        delta=(one.CenterOfMass-two.CenterOfMass).Length
        volume=abs(one.Volume-two.Volume)
        bound=(one.Area+two.Area)/2*(one.getTolerance(1)+two.getTolerance(1))
        placements.append(dict(id=item['id'],passed=delta<1e-5 and volume<max(bound,1e-5),
            centroid_difference_mm=delta,volume_difference_mm3=volume,surface_tolerance_bound_mm3=bound))
    write(out/'assembly_exchange_checks.json',dict(passed=all(r['passed'] for r in placements),checks=placements,
        scope='51 placed solids: validity,count,centroid and mass; detailed Boolean/tolerance checks are in the 17-definition exchange receipt.',
        native_sha256=sha(native),step_sha256=sha(assembled_path),checker_sha256=sha(Path(__file__))))
    print('Assembly STEP',len(placements),'checks; failed',json.dumps([r for r in placements if not r['passed']]),flush=True)
    sys.exit(0 if all(r['passed'] for r in checks+rows+placements) else 1)
finally:
    runtime.close()
