"""Independent saved-artifact checks; no import of the cone geometry builder."""
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
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_cone_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'check_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    native=out/'TransmissionWithClutchCone.FCStd';nh=sha(native);r=read(out/'report.json');assert r['native_sha256']==nh
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)}
    c=r['controls'];pc=r['parent_controls'];tc=r['thrust_controls'];d=r['datums'];origin=doc.TransmissionCore.Placement.Base
    shapes={}
    for n,i in byid.items():shapes[n]=i['shape'].copy();shapes[n].translate(-origin)
    checks=[];bound_diagnostics=[]
    def ck(name,passed,detail=None):
        checks.append(dict(name=name,passed=bool(passed),detail=detail))
        write(out/'check_progress.json',dict(completed=len(checks),last=name,failed=[x for x in checks if not x['passed']]))
    def near(name,value,expected,tol=1e-6):ck(name,abs(value-expected)<tol,dict(actual=value,expected=expected,tolerance=tol))
    def at(shape,point):return shape.isInside(point,1e-7,False)
    def on(name,shape,point):near(name,Part.Vertex(point).distToShape(shape)[0],0)
    def xc(rad,lo,hi,y=0,z=0):return Part.makeCylinder(rad,hi-lo,App.Vector(lo,y,z),App.Vector(1,0,0))
    def contact(name,a,b,point):on(name+'/first surface',a,point);on(name+'/second surface',b,point)
    ck('1652 physical occurrences',len(byid)==1652)
    ck('71 new occurrences',len(r['new_ids'])==71 and len(set(r['new_ids']))==71)
    ck('one refined support',r['changed_ids']==['ClutchStack_support'])
    ck('all72affected single closed solids',all(shapes[n].isValid() and len(shapes[n].Solids)==1 for n in r['affected_ids']))
    ck('definitions hidden',not doc.Definitions.Visibility)
    ck('support reused inside cone container',byid['ClutchStack_support']['object'].getParentGeoFeatureGroup()==doc.ClutchConeAssembly)
    expected={'cone':1,'lining':1,'plug':1,'support_rivet':6,'lining_rivet':43,'plunger':6,'cup':6,'spring':6,'ring':1}
    actual=Counter(byid[n]['definition'].removeprefix('clutch_cone_') for n in r['new_ids']);ck('source quantity expansion',actual==expected,dict(actual))
    for key,count in expected.items():
        names=[n for n in r['new_ids'] if byid[n]['definition']=='clutch_cone_'+key]
        ck(key+'/shared definition',len(names)==count and len({byid[n]['target'].Name for n in names})==1)
        parent=doc.ClutchConeSprings if key in ['plunger','cup','spring','ring'] else doc.ClutchConeAssembly
        ck(key+'/correct owning group',all(byid[n]['object'].getParentGeoFeatureGroup()==parent for n in names))
    rows={x['record_id']:x for x in read(out/'inputs/clutch_cone_sources.json')['records']}
    for n in r['new_ids']:
        obj=byid[n]['object'];ck(n+'/source mapping',json.loads(obj.SurveyIds)==rows[obj.SourceRecord]['part_ids'] and obj.Subsystem=='Drivetrain')
    support=shapes['ClutchStack_support'];cone=shapes['ClutchCone_cone'];lining=shapes['ClutchCone_lining'];ring=shapes['ClutchCone_ring']
    # Printed dimensions independently converted, plus a held-out developed pattern.
    near('large diameter19.186in',c['large_diameter'],19.186*25.4)
    near('small diameter17.887in',c['small_diameter'],17.887*25.4)
    near('slant width2.5in',c['face_slant'],2.5*25.4)
    near('lining stock quarter inch',c['lining_stock'],.25*25.4)
    for rad,diam in [(36.924,c['large_diameter']),(34.424,c['small_diameter'])]:
        near('developed pattern/'+str(rad),rad*2*(93+31/60+36/3600)/360*25.4,diam,.015)
    near('lining maximum diameter',lining.BoundBox.YLength,c['large_diameter'],2e-5)
    sa=(19.186-17.887)/(2*2.5);ca=math.sqrt(1-sa*sa)
    near('cone axial face span',d['small_face'][0]-d['large_face'][0],63.5*ca)
    theta=.071;radial=App.Vector(0,math.cos(theta),math.sin(theta));N=App.Vector(sa,0,0)+radial*ca
    mid=App.Vector((d['small_face'][0]+d['large_face'][0])/2,0,0)+radial*((19.186+17.887)*25.4/4)
    on('friction face point',lining,mid)
    ck('friction face material and air',at(lining,mid-N*.05) and not at(lining,mid+N*.05))
    joint=mid-N*6.35;contact('lining to cone',lining,cone,joint)
    ck('lining full thickness',at(lining,joint+N*.05) and not at(lining,joint-N*.05))
    ck('steel behind lining',at(cone,joint-N*(c['steel_stock']/2)))
    q=math.sqrt(.5);webN=App.Vector(q,0,0)-radial*q
    web=App.Vector(180+c['web_x_intercept'],0,0)+radial*180
    ck('pressed dished web',at(cone,web) and not at(cone,web+webN*(c['steel_stock']/2+.05)) and not at(cone,web-webN*(c['steel_stock']/2+.05)))
    ck('analytic conical and rounded bend surfaces',{'Cone','Toroid'}.issubset({type(f.Surface).__name__ for f in cone.Faces}))
    # The original keyed running bore is retained except for the declared new oil passage.
    parent=Part.Shape();parent.read(str(out/'inputs/parent_support.brep'))
    protected=xc(102,pc['support_rear']-.1,pc['support_front']+.1)
    axis=App.Vector(*d['plug_axis']);plugbase=App.Vector(*d['plug_base'])
    oil=Part.makeCylinder(7.001,30,plugbase-axis*12,axis)
    a=parent.common(protected).cut(oil);b=support.common(protected).cut(oil)
    near('protected support material retained',a.cut(b).Volume,0)
    near('protected support has no new material',b.cut(a).Volume,0)
    # Six actual force paths: stop/head -> plunger/ring -> spring -> cup/support.
    near('plunger printed overall length',c['plunger_length'],4.875*25.4)
    near('plunger printed diameter',c['plunger_diameter'],.375*25.4)
    near('installed spring height from seats',d['spring_length'],c['cup_front']-c['cup_end_stock']-(d['stop_front']+c['plunger_head_height']-4.875*25.4+c['ring_stock']))
    ck('both source free lengths exceed installed length',d['spring_length']<4.625*25.4<5.85*25.4)
    near('32 spring turns',d['spring']['turns'],32)
    ck('spring coil separation',d['spring']['end_pitch']>2*c['spring_wire_radius'] and d['spring']['free_pitch']>2*c['spring_wire_radius'])
    for n in range(1,7):
        angle=math.radians(30+(n-1)*60);radial=App.Vector(0,math.cos(angle),math.sin(angle));paxis=radial*114
        plunger=shapes[f'ClutchCone_Plunger{n}'];cup=shapes[f'ClutchCone_Cup{n}'];spring=shapes[f'ClutchCone_Spring{n}']
        near(f'plunger{n}/overall length',plunger.BoundBox.XLength,123.825)
        ck(f'plunger{n}/axis material',at(plunger,App.Vector(1000,0,0)+paxis))
        near(f'plunger{n}/head stop plane',plunger.BoundBox.XMax-4,d['stop_front'])
        contact(f'plunger{n}/head stop contact',plunger,shapes['ClutchThrust_Stop'],App.Vector(d['stop_front'],0,0)+paxis+radial*5.8)
        contact(f'plunger{n}/thread envelope in ring',plunger,ring,App.Vector(d['plunger_tail']+3,0,0)+paxis+radial*4.7625)
        near(f'cup{n}/plunger clearance',plunger.distToShape(cup)[0],.15,2e-6)
        contact(f'cup{n}/support shoulder',cup,support,App.Vector(d['cup_support_seat'],0,0)+paxis+radial*10.75)
        planes=[f for f in spring.Faces if type(f.Surface).__name__=='Plane']
        ck(f'spring{n}/rear ground seat',any(abs(f.CenterOfMass.x-d['ring_front'])<1e-6 and f.Area>.1 for f in planes))
        ck(f'spring{n}/front ground seat',any(abs(f.CenterOfMass.x-d['spring_front'])<1e-6 and f.Area>.1 for f in planes))
        bb=spring.BoundBox;bound_diagnostics.append(dict(spring=n,conservative_bounds=[bb.XMin,bb.XMax],ground_planes=[(f.CenterOfMass.x,f.Area) for f in planes]))
        near(f'spring{n}/no material behind rear seat',spring.common(xc(12,bb.XMin-1,d['ring_front'],paxis.y,paxis.z)).Volume,0)
        near(f'spring{n}/no material beyond front seat',spring.common(xc(12,d['spring_front'],bb.XMax+1,paxis.y,paxis.z)).Volume,0)
        near(f'spring{n}/ring contact',spring.distToShape(ring)[0],0)
        near(f'spring{n}/cup contact',spring.distToShape(cup)[0],0)
        ck(f'spring{n}/shaft running clearance',spring.distToShape(plunger)[0]>1.57)
    # Every installed rivet has material along its own axis and real through-holes.
    for j in d['rivet_joints']:
        name=j['name'];shape=shapes[name];base=App.Vector(*j['base']);axis=App.Vector(*j['normal'])
        if j['kind']=='support':
            for amount in [1,j['grip']-1]:
                point=base+axis*amount;ck(name+f'/through joint {amount}',at(shape,point) and not at(support,point) and not at(cone,point))
            ck(name+'/both heads',at(shape,base-axis) and at(shape,base+axis*(j['grip']+1)))
        else:
            line=Part.makeLine(base-axis*4,base+axis*(j['surface']+2))
            ck(name+'/axis passes through cone',not cone.section(line).Vertexes)
            for amount in [1,6]:
                point=base+axis*amount;ck(name+f'/through joint {amount}',at(shape,point) and not at(lining,point) and not at(cone,point))
            near(name+'/recessed head',Part.Vertex(base+axis*j['head_top']).distToShape(shape)[0],0)
            ck(name+'/open head recess',not at(lining,base+axis*(j['surface']-.2)) and not at(shape,base+axis*(j['surface']-.2)))
    plug=shapes['ClutchCone_Plug']
    ck('plug shank in real hole',at(plug,plugbase+App.Vector(*d['plug_axis'])*3))
    ck('port passage reaches running bore',not at(support,App.Vector(c['plug_x'],0,0)+App.Vector(*d['plug_axis'])*91))
    near('plug and support no overlap',plug.common(support).Volume,0)
    for key,shape in [('cone',cone),('lining',lining),('support',support)]:
        blank=Part.Shape();blank.read(str(out/'inputs'/(key+'_blank.brep')))
        extra=shape.cut(blank,1e-7)
        ck(key+'/cut only removes blank material',abs(extra.Volume)<1e-5 and not extra.Faces)
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),native_sha256=nh,checker_sha256=sha(Path(__file__)),checks=checks,bound_diagnostics=bound_diagnostics))
    print('Independent checks',len(checks),'failed',[x for x in checks if not x['passed']],flush=True)
    # Explicit-accuracy mass integration and both material directions on definitions.
    mass=calculator(out/'check_runtime/mass');keys=read(out/'definition_order.json');native_mass={};exchange=[]
    loaded=Part.Shape();loaded.read(str(out/'ClutchConeDefinitions.step'));ck('definition STEP solid count',len(loaded.Solids)==10 and loaded.isValid())
    remaining=[(solid,solid.CenterOfMass,solid.Volume) for solid in loaded.Solids]
    for key in keys:
        one=doc.getObject(key).Shape.Solids[0]
        center,volume,area=one.CenterOfMass,one.Volume,one.Area
        idx=min(range(len(remaining)),key=lambda j:(center-remaining[j][1]).Length+abs(volume-remaining[j][2])/max(area,1))
        two=remaining.pop(idx)[0];ta=one.getTolerance(1);tb=two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        ma=mass(one,key+'_native');mb=mass(two,key+'_step');native_mass[key]=ma
        missing=one.cut(two).Volume;added=two.cut(one).Volume;dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length
        passed=missing<1e-5 and added<1e-5 and not one.cut(two,fuzzy).Faces and not two.cut(one,fuzzy).Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=(one.Area+two.Area)/2*(ta+tb) and dc<max(1e-6,ta+tb)
        exchange.append(dict(definition=key,passed=passed,missing_mm3=missing,added_mm3=added,mass_difference_mm3=dv,centroid_difference_mm=dc))
        write(out/'exchange_progress.json',dict(last=key,checks=exchange));print('Definition STEP',key,passed,flush=True)
    write(out/'exchange_checks.json',dict(passed=all(x['passed'] for x in exchange),native_sha256=nh,step_sha256=sha(out/'ClutchConeDefinitions.step'),checker_sha256=sha(Path(__file__)),checks=exchange))
    loaded=Part.Shape();loaded.read(str(out/'ClutchConeInstallation.step'));assert loaded.isValid() and len(loaded.Solids)==72
    # Compute ranking quantities once. Reintegrating six spline springs for each
    # of72pairing searches previously dominated runtime without adding evidence.
    remaining=[(solid,solid.CenterOfMass,solid.Volume) for solid in loaded.Solids];placed=[]
    for name in r['affected_ids']:
        i=byid[name];one=i['shape'].Solids[0];center,volume,area=one.CenterOfMass,one.Volume,one.Area
        idx=min(range(len(remaining)),key=lambda j:(center-remaining[j][1]).Length+abs(volume-remaining[j][2])/max(area,1))
        two=remaining.pop(idx)[0];mb=mass(two,name+'_placed');ma=native_mass[i['target'].Name]
        frame=i['object'].getParentGeoFeatureGroup().getGlobalPlacement().multiply(i['object'].LinkPlacement)
        center=frame.multVec(App.Vector(*ma['center_mm']));dc=(center-App.Vector(*mb['center_mm'])).Length
        dv=abs(ma['volume_mm3']-mb['volume_mm3']);tol=one.getTolerance(1)+two.getTolerance(1)
        passed=dv<=(one.Area+two.Area)/2*tol and dc<max(1e-6,tol)
        placed.append(dict(occurrence=name,passed=passed,mass_difference_mm3=dv,centroid_difference_mm=dc))
        write(out/'placed_progress.json',dict(last=name,completed=len(placed),failed=[x for x in placed if not x['passed']]))
    write(out/'assembly_exchange_checks.json',dict(passed=all(x['passed'] for x in placed),native_sha256=nh,step_sha256=sha(out/'ClutchConeInstallation.step'),checker_sha256=sha(Path(__file__)),checks=placed))
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),native_sha256=nh,checker_sha256=sha(Path(__file__)),checks=checks,bound_diagnostics=bound_diagnostics))
    assert all(x['passed'] for x in checks+exchange+placed)
finally:
    runtime.close()
