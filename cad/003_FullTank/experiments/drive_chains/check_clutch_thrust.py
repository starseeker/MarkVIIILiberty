"""Independently inspect saved clutch thrust geometry, contacts and STEP exchange."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_thrust_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'check_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    r=read(out/'report.json');native=out/'TransmissionWithClutchThrust.FCStd';nh=sha(native);assert nh==r['native_sha256']
    for path,h in r['input_hashes'].items():assert sha(ROOT/path)==h,path
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    origin=doc.TransmissionCore.Placement.Base;s={}
    for n,i in byid.items():s[n]=i['shape'].copy();s[n].translate(-origin)
    c=r['controls'];pc=r['parent_controls'];checks=[];contact_diagnostics=[]
    def ck(name,passed,detail=None):
        checks.append(dict(name=name,passed=bool(passed),detail=detail))
        write(out/'check_progress.json',dict(completed=len(checks),last=name,failed=[x for x in checks if not x['passed']]))
    def near(name,actual,expected,tol=1e-6):ck(name,abs(actual-expected)<tol,dict(actual=actual,expected=expected,tolerance=tol))
    def shift(shape,delta):q=shape.copy();q.translate(App.Vector(*delta));return q
    def xc(radius,rear,front,y=0,z=0):return Part.makeCylinder(radius,front-rear,App.Vector(rear,y,z),App.Vector(1,0,0))
    cage=s['ClutchThrust_Cage'];stop=s['ClutchThrust_Stop'];thrust=s['ClutchStack_thrust']
    balls=[f'ClutchThrust_Ball{n:02}' for n in range(1,31)]
    ck('1581 distinct physical occurrences',len(byid)==1581)
    ck('32 new physical occurrences',len(r['new_ids'])==32 and set(r['new_ids'])==set(balls+['ClutchThrust_Cage','ClutchThrust_Stop']))
    ck('33 affected valid single solids',all(s[n].isValid() and len(s[n].Solids)==1 for n in r['affected_ids']))
    ck('all 30 balls share one definition',len({byid[n]['target'].Name for n in balls})==1)
    ck('retainer assembly owns cage and 30 balls',all(byid[n]['object'].getParentGeoFeatureGroup()==doc.ClutchBallRetainer for n in balls+['ClutchThrust_Cage']))
    ck('ring owned by thrust assembly',byid['ClutchThrust_Stop']['object'].getParentGeoFeatureGroup()==doc.ClutchThrust)
    ck('source assembly is not a physical leaf','ClutchBallRetainer' not in byid and doc.ClutchBallRetainer.SourceRecord=='SNL:164:002')
    ck('definition library stays hidden after headless reopen',not doc.Definitions.Visibility)
    records={row['record_id']:row for row in read(out/'inputs/clutch_thrust_sources.json')['records']}
    expected=Counter(pid for rid,count in [('SNL:164:004',1),('SNL:164:005',30),('SNL:165:003',1)] for pid in records[rid]['part_ids'] for _ in range(count))
    actual=Counter(pid for n in r['new_ids'] for pid in json.loads(byid[n]['object'].SurveyIds))
    ck('source quantity expansion',actual==expected,dict(actual))
    ck('all new occurrences belong to drivetrain',all(byid[n]['system']=='Drivetrain' for n in r['new_ids']))
    # Independent dimensional relationships; do not import the candidate builder.
    floor=pc['thrust_front']-c['race_floor_depth'];center=floor+3.175;pitch=c['ball_pitch_radius']
    ck('catalogue quarter-inch conversion',c['ball_diameter']==.25*25.4 and c['ball_count']==30)
    for n,name in enumerate(balls):
        ball=s[name];angle=2*math.pi*n/30;want=App.Vector(center,pitch*math.cos(angle),pitch*math.sin(angle))
        near(name+'/center',(ball.Solids[0].CenterOfMass-want).Length,0)
        ck(name+'/sphere diameter',all(abs(v-6.35)<1e-6 for v in [ball.BoundBox.XLength,ball.BoundBox.YLength,ball.BoundBox.ZLength]))
        near(name+'/analytic volume',ball.Volume,4*math.pi*3.175**3/3)
        for label,race,sign in [('rear race',thrust,-1),('front race',stop,1)]:
            contact=want+App.Vector(sign*3.175,0,0);vertex=Part.Vertex(contact)
            near(name+'/'+label+' contact point on ball',vertex.distToShape(ball)[0],0)
            near(name+'/'+label+' contact point on race',vertex.distToShape(race)[0],0)
            ck(name+'/'+label+' material behind contact',race.isInside(contact+App.Vector(sign*.01,0,0),1e-7,False))
            contact_diagnostics.append(dict(ball=name,race=label,whole_shape_distance=ball.distToShape(race)[0],
                point_on_ball=vertex.distToShape(ball)[0],point_on_race=vertex.distToShape(race)[0]))
            near(name+'/'+label+' no overlap',ball.common(race).Volume,0)
        near(name+'/cage clearance',ball.distToShape(cage)[0],.125)
        ck(name+'/actual cage pocket',not cage.isInside(want,1e-6,True))
        mid=angle+math.pi/30
        ck(name+'/material bridge',cage.isInside(App.Vector(center,pitch*math.cos(mid),pitch*math.sin(mid)),1e-6,True))
    area=math.pi*((pitch+c['cage_half_width'])**2-(pitch-c['cage_half_width'])**2-30*c['cage_hole_radius']**2)
    near('perforated cage analytic volume',cage.Volume,area*c['cage_stock'],1e-5)
    near('cage axial stock',cage.BoundBox.XLength,c['cage_stock'])
    near('adjacent balls stay separate',s[balls[0]].distToShape(s[balls[1]])[0],2*pitch*math.sin(math.pi/30)-6.35)
    ck('aft displaced ball hits rear race',shift(s[balls[0]],[-.1,0,0]).common(thrust).Volume>.01)
    ck('forward displaced ball hits front race',shift(s[balls[0]],[.1,0,0]).common(stop).Volume>.01)
    for name,one,two in [('ring/collar',stop,thrust),('cage/rear race',cage,thrust),('cage/front race',cage,stop)]:
        near(name+' no overlap',one.common(two).Volume,0)
        ck(name+' positive clearance',one.distToShape(two)[0]>1e-3)
    parent=Part.Shape();parent.read(str(out/'inputs/parent_thrust.brep'));assert sha(out/'inputs/parent_thrust.brep')==r['parent_thrust_sha256']
    rear=xc(140,pc['bearing_front']-.1,1002.95)
    near('original bearing/housing seating region retains all material',parent.common(rear).cut(thrust).Volume,0)
    near('race refinement only removes material',thrust.cut(parent).Volume,0)
    near('shaft bore remains open',xc(pc['bearing_front_bore_radius']-.01,pc['bearing_front']-.1,pc['thrust_front']+.1).common(thrust).Volume,0)
    near('bearing contact retained',thrust.distToShape(s['ClutchStack_bearing'])[0],0)
    near('separate external snap ring retains gap',thrust.distToShape(s['ClutchStack_snap'])[0],1.0)
    near('ring bore remains open',xc(pitch-c['stop_bore_offset']-.01,floor+6.35+.01,floor+6.35+c['stop_plate_stock']+.1).common(stop).Volume,0)
    for n in range(6):
        a=math.radians(c['plunger_phase_deg'])+2*math.pi*n/6;y=c['plunger_pitch_radius']*math.cos(a);z=c['plunger_pitch_radius']*math.sin(a)
        near(f'plunger hole{n+1} open',xc(c['plunger_hole_radius']-.01,floor+6.35-.1,floor+6.35+c['stop_plate_stock']+.1,y,z).common(stop).Volume,0)
        witness=App.Vector(floor+6.35+c['stop_plate_stock']/2,y+(c['plunger_hole_radius']+.2)*math.cos(a),z+(c['plunger_hole_radius']+.2)*math.sin(a))
        ck(f'plunger hole{n+1} has receiving wall',stop.isInside(witness,1e-6,True))
    result=dict(passed=all(x['passed'] for x in checks),native_sha256=nh,checker_sha256=sha(Path(__file__)),checks=checks,
        contact_diagnostics=contact_diagnostics,contact_method='Expected axial tangent point must lie on both saved surfaces, with material immediately beyond the race. See preserved whole_shape_distance diagnostic; numerical thresholds unchanged.')
    write(out/'independent_checks.json',result);print('Independent checks',len(checks),'failed',[x for x in checks if not x['passed']],flush=True)
    mass=calculator(out/'check_runtime/mass');keys=read(out/'definition_order.json')
    imported=Part.Shape();path=out/'ClutchThrustDefinitions.step';imported.read(str(path))
    assert sha(path)==r['definition_step_sha256'] and imported.isValid() and len(imported.Solids)==4
    remaining=list(imported.Solids);exchange=[]
    for key in keys:
        one=doc.getObject(key).Shape.Solids[0]
        idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length+abs(one.Volume-remaining[j].Volume)/max(one.Area,1))
        two=remaining.pop(idx);ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        missing,added=one.cut(two).Volume,two.cut(one).Volume
        ma,mb=mass(one,key+'_native'),mass(two,key+'_step');dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length
        bound=(one.Area+two.Area)/2*(ta+tb)
        passed=missing<1e-5 and added<1e-5 and not one.cut(two,fuzzy).Faces and not two.cut(one,fuzzy).Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=bound and dc<max(1e-6,ta+tb)
        exchange.append(dict(definition=key,passed=passed,raw_missing_mm3=missing,raw_added_mm3=added,volume_difference_mm3=dv,centroid_difference_mm=dc,surface_tolerance_bound_mm3=bound))
    write(out/'exchange_checks.json',dict(passed=all(x['passed'] for x in exchange),checks=exchange,native_sha256=nh,step_sha256=sha(path),checker_sha256=sha(Path(__file__))))
    imported=Part.Shape();path=out/'ClutchThrustInstallation.step';imported.read(str(path));assert sha(path)==r['step_sha256'] and imported.isValid() and len(imported.Solids)==33
    remaining=list(imported.Solids);placed=[]
    for name in r['affected_ids']:
        one=byid[name]['shape'].Solids[0];idx=min(range(len(remaining)),key=lambda j:(one.CenterOfMass-remaining[j].CenterOfMass).Length)
        two=remaining.pop(idx);ma,mb=mass(one,name+'_native'),mass(two,name+'_step');dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length
        bound=(one.Area+two.Area)/2*(one.getTolerance(1)+two.getTolerance(1))
        placed.append(dict(id=name,passed=dv<=bound and dc<max(1e-6,one.getTolerance(1)+two.getTolerance(1)),volume_difference_mm3=dv,centroid_difference_mm=dc,surface_tolerance_bound_mm3=bound))
    write(out/'assembly_exchange_checks.json',dict(passed=all(x['passed'] for x in placed),checks=placed,native_sha256=nh,step_sha256=sha(path),checker_sha256=sha(Path(__file__)),scope='33 placed solids: count, validity, mass and centroid; four definitions checked for two-way material equality.'))
    print('STEP',len(exchange),len(placed),'failures',[x for x in exchange+placed if not x['passed']],flush=True)
    sys.exit(0 if all(x['passed'] for x in checks+exchange+placed) else 1)
finally:
    runtime.close()
