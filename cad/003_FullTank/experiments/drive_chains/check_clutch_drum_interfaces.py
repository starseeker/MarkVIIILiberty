"""Independently inspect the saved drum/flywheel mating geometry and wire routes."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_drum_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'interface_check.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    native=out/'TransmissionWithClutchDrum.FCStd';r=read(out/'report.json');nh=sha(native);assert nh==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};origin=doc.TransmissionCore.Placement.Base
    c=r['controls'];d=r['datums'];checks=[];s={}
    for name in r['affected_ids']+['ClutchCone_lining','ClutchStack_sleeve','ClutchStack_bearing','ClutchStack_thrust']+[f'ClutchCone_Plunger{n}' for n in range(1,7)]:
        shape=byid[name]['shape'].copy();shape.translate(-origin);s[name]=shape
    def ck(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
    def near(name,a,b,tol=1e-6):ck(name,abs(a-b)<tol,dict(actual=a,expected=b,tolerance=tol))
    def at(shape,p):return shape.isInside(p,1e-7,False)
    def on(name,shape,p):near(name,Part.Vertex(p).distToShape(shape)[0],0)
    drum=s['ClutchDrum_drum'];fly=s['ClutchDrum_flywheel'];wire=s['ClutchDrum_wire'];retained=s['ClutchRetention_Wire']
    ck('1662 physical occurrences',len(items)==1662)
    ck('nine new pieces and one rerouted existing wire',len(r['new_ids'])==9 and r['changed_ids']==['ClutchRetention_Wire'])
    ck('affected shapes valid single solids',all(s[n].isValid() and len(s[n].Solids)==1 for n in r['affected_ids']))
    ck('flywheel belongs to Powerplant',byid['ClutchDrum_flywheel']['object'].Subsystem=='Powerplant' and byid['ClutchDrum_flywheel']['object'].getParentGeoFeatureGroup()==doc.EngineFlywheelAssembly)
    ck('drum parts belong to Drivetrain',all(byid[n]['object'].Subsystem=='Drivetrain' and byid[n]['object'].getParentGeoFeatureGroup()==doc.ClutchOuterDrumAssembly for n in r['new_ids'] if n!='ClutchDrum_flywheel'))
    ck('six screws share one definition',len({byid[f'ClutchDrum_Screw{n}']['target'].Name for n in range(1,7)})==1)
    # A held-out interior friction-face point, away from lining rivets.
    sin_a=(19.186-17.887)/5;cos_a=math.sqrt(1-sin_a*sin_a);theta=.079
    radial=App.Vector(0,math.cos(theta),math.sin(theta));normal=App.Vector(sin_a,0,0)+radial*cos_a
    mid=App.Vector((958.7506231548401+1020.0701884885083)/2,0,0)+radial*((19.186+17.887)*25.4/4)
    on('lining and drum friction contact/lining',s['ClutchCone_lining'],mid);on('lining and drum friction contact/drum',drum,mid)
    ck('material on opposite sides of friction face',at(drum,mid+normal*.1) and not at(drum,mid-normal*.1) and at(s['ClutchCone_lining'],mid-normal*.1))
    on('drum outer stock',drum,mid+normal*c['drum_stock'])
    near('drum and lining have no overlap',drum.common(s['ClutchCone_lining']).Volume,0,1e-5)
    near('drum and flywheel have no overlap',drum.common(fly).Volume,0,1e-5)
    for radius in [169.,180.,200.]:
        p=App.Vector(d['flywheel_joint'],radius*math.cos(.3),radius*math.sin(.3))
        on('full flange support/drum '+str(radius),drum,p);on('full flange support/flywheel '+str(radius),fly,p)
    near('printed flywheel largest diameter',fly.BoundBox.YLength,19.811*25.4,2e-5)
    tip_faces=[f for f in fly.Faces if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-19.811*25.4/2)<1e-6]
    ck('124 distinct starter tooth tips',len(tip_faces)==124,len(tip_faces))
    tooth_radius=d['starter_tooth_profile']['root_radius_mm']+2
    band_x=(d['flywheel_joint']+d['flywheel_front'])/2
    for n in range(124):
        # gear_outline starts along +X in its original XZ plane; after axial remap that is -Y.
        angle=math.pi-2*math.pi*n/124
        tooth=App.Vector(band_x,(19.811*25.4/2-.1)*math.cos(angle),(19.811*25.4/2-.1)*math.sin(angle))
        valley=App.Vector(band_x,tooth_radius*math.cos(angle+math.pi/124),tooth_radius*math.sin(angle+math.pi/124))
        ck(f'starter tooth{n+1}/material and adjacent space',at(fly,tooth) and not at(fly,valley))
    # Taper and through keyway are physical holes; no engine shaft stub is present.
    for x in [d['hub_rear']+.1,930.,d['taper_front']-.1]:
        rr=c['taper_rear_radius']+(c['taper_front_radius']-c['taper_rear_radius'])*(x-d['hub_rear'])/(d['taper_front']-d['hub_rear'])
        ck('taper material/void '+str(x),not at(fly,App.Vector(x,-rr+.05,0)) and at(fly,App.Vector(x,-rr-.05,0)))
        ck('through keyway '+str(x),not at(fly,App.Vector(x,rr+c['keyway_depth']-.05,0)) and at(fly,App.Vector(x,rr+c['keyway_depth']+.05,0)))
    near('journal clears front bearing by declared allowance',fly.distToShape(s['ClutchStack_bearing'])[0],c['journal_running_gap'],2e-6)
    near('positive spline has no static overlap',fly.common(s['ClutchStack_sleeve']).Volume,0,1e-5)
    turned=fly.copy();turned.rotate(App.Vector(),App.Vector(1,0,0),1)
    ck('relative hub rotation catches sleeve drive faces',turned.common(s['ClutchStack_sleeve']).Volume>.1)
    for n in range(1,7):
        theta=math.radians(60*(n-1));radial=App.Vector(0,math.cos(theta),math.sin(theta));tangent=App.Vector(0,-math.sin(theta),math.cos(theta))
        screw=s[f'ClutchDrum_Screw{n}'];axis=radial*188
        near(f'screw{n}/source overall length',screw.BoundBox.XLength,1.25*25.4+c['bolt_head_height'])
        point=axis+App.Vector(d['bolt_seat']-c['bolt_head_height']/2,0,0)
        ck(f'screw{n}/actual drilled head',not screw.section(Part.makeLine(point-tangent*18,point+tangent*18)).Vertexes)
        ck(f'screw{n}/wire inside passage',at(wire,point) and not at(screw,point))
        for x in [d['bolt_seat']+.1,d['flywheel_joint']-.1,d['flywheel_joint']+2,d['bolt_seat']+31.75-.1]:
            p=axis+App.Vector(x,0,0)
            ck(f'screw{n}/shank and receiving hole '+str(x),at(screw,p) and not at(drum,p) and not at(fly,p))
        near(f'screw{n}/head clears drum bend',screw.common(drum).Volume,0,1e-5)
        # A nominal endwall at the circle centre is insufficient: inspect the complete hole bottom.
        tip=d['bolt_seat']+31.75+c['blind_tip_gap']
        for angle in range(0,360,45):
            a=math.radians(angle);p=axis+App.Vector(tip+.05,0,0)+radial*(7.9*math.cos(a))+tangent*(7.9*math.sin(a))
            ck(f'screw{n}/blind bottom material {angle}',at(fly,p))
    mass=calculator(out/'check_runtime/mass');wire_metrics={}
    for name,shape,file,length,pitch,phase,plane,heads in [
        ('drum',wire,'drum_wire_centerline.brep',48*25.4,188,0,d['bolt_seat']-c['bolt_head_height']/2,'ClutchDrum_Screw'),
        ('retention',retained,'retention_wire_centerline.brep',30*25.4,114,30,1019.3,'ClutchCone_Plunger')]:
        spine=Part.Shape();spine.read(str(out/'inputs'/file));m=mass(shape,name+'_wire')
        ck(name+'/one continuous open wire',len(spine.Edges)==1 and len(spine.Vertexes)==2)
        near(name+'/source cut length',spine.Length,length,1e-5)
        near(name+'/round section volume',m['volume_mm3'],math.pi*.75**2*length,.05)
        near(name+'/no flywheel intersection',shape.common(fly).Volume,0,1e-5)
        for n in range(1,7):
            theta=math.radians(phase+60*(n-1));p=App.Vector(plane,pitch*math.cos(theta),pitch*math.sin(theta))
            ck(f'{name}/head{n} passage',at(shape,p) and not at(s[heads+str(n)],p))
        wire_metrics[name]=dict(mass=m,centerline_length=spine.Length)
    old=Part.Shape();old.read(str(out/'inputs/parent_plunger_wire.brep'))
    ck('previous axial wire route actually obstructs dished flywheel',old.common(fly).Volume>1)
    result=dict(passed=all(x['passed'] for x in checks),native_sha256=nh,checker_sha256=sha(Path(__file__)),checks=checks,wire_metrics=wire_metrics)
    write(out/'independent_checks.json',result);print('Independent checks',len(checks),'failed',[x for x in checks if not x['passed']],flush=True)
    assert result['passed']
finally:
    runtime.close()
