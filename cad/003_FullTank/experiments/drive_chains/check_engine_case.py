"""Inspect saved cast material, cavities, interfaces and inherited tank context."""
import argparse,math
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'engine_case_build');p.add_argument('--worker',action='store_true');p.add_argument('--local-only',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    args=[sys.executable,__file__,'--candidate',str(out),'--worker']+(['--local-only'] if a.local_only else [])
    with (out/'interface_check.log').open('w') as log:sys.exit(subprocess.run(args,env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,shape_signature
    from lib.worker import same_shape,placement_errors,check_build
    V=App.Vector;native=out/'DrivetrainWithEngineCase.FCStd';r=read(out/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};c=r['controls'];d=r['datums'];checks=[]
    upper=doc.Def_EngineCase_upper.Shape;lower=doc.Def_EngineCase_lower.Shape;origin=V(*d['origin']);last=c['nose_to_first_row']+6*165.1
    def ck(name,result,detail=None):
        checks.append(dict(name=name,passed=bool(result),detail=detail))
        if len(checks)%25==0:print('Geometry checks',len(checks),flush=True)
    def near(name,value,expected=0,tol=1e-6):ck(name,abs(value-expected)<tol,dict(actual=value,expected=expected,tolerance=tol))
    def inside(name,s,p,expected=True):ck(name,s.isInside(V(*p),1e-7,False)==expected,dict(point=p,expected_material=expected))
    def gap(name,a,b):near(name,a.distToShape(b)[0])
    ck('1911 unique physical occurrences',len(items)==len(byid)==1911 and all(i['representation']!='layout' for i in items))
    ck('two physically owned castings',len(leaves(doc.EngineCrankcase))==2 and doc.EngineCrankcase in doc.TankLibertyEngine.Group and doc.TankLibertyEngine in doc.PowerplantDevelopment.Group)
    ck('two case identities retained',doc.Def_EngineCase_upper.OriginalMark=='LQ207A' and doc.Def_EngineCase_lower.OriginalMark=='LQ180A')
    ck('all affected shapes valid single solids',all(byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1 for n in r['exchange_ids']))
    ck('hidden shared definitions',not doc.Definitions.Visibility)
    ck('curved lower casting surfaces retained',any(type(f.Surface).__name__ not in ['Plane','Cylinder'] for f in lower.Faces))
    near('separate upper/lower material',upper.common(lower).Volume,0,1e-5);gap('lapped case joint seated',upper,lower)
    near('upper case joint datum',upper.optimalBoundingBox(False).ZMin,0)
    near('lower case joint datum',lower.optimalBoundingBox(False).ZMax,0)
    near('conditional source bore',c['piston_bore'],127)
    near('conditional source shaft diameter',c['crankshaft_diameter'],66.675)
    near('conditional source V angle',c['bank_angle'],45)
    near('conditional source pitch',c['cylinder_pitch'],165.1)
    near('conditional nose-to-mount row',c['nose_to_first_row'],(6+21/32)*25.4)
    # Inspect actual roof bores and remaining casting land independently.
    angle=math.radians(22.5)
    for i in range(6):
        x=c['nose_to_first_row']+(i+.5)*165.1
        for sign in [-1,1]:
            axis=V(0,sign*math.sin(angle),math.cos(angle));center=V(x,0,0)+axis*(c['deck_center_height']*math.cos(angle))
            witness=Part.makeCylinder(63.5,30,center-axis*20,axis)
            near('cylinder%d side%d source bore remains open'%(i,sign),upper.common(witness).Volume,0,1e-5)
            receiver_radius=63.5+c['cylinder_spigot_stock']+c['cylinder_spigot_clearance']
            faces=[f for f in upper.Faces if isinstance(f.Surface,Part.Cylinder)
                   and abs(f.Surface.Radius-receiver_radius)<1e-6
                   and abs(abs(f.Surface.Axis.dot(axis))-1)<1e-7
                   and abs(f.CenterOfMass.x-x)<receiver_radius+1e-6]
            ck('cylinder%d side%d analytic spigot receiver retained'%(i,sign),bool(faces),dict(radius_mm=receiver_radius,faces=len(faces)))
            inside('cylinder%d side%d surrounding deck land'%(i,sign),upper,list(center+V(72,0,0)-axis*3))
        inside('upper bay%d hollow'%i,upper,[x,0,110],False)
        inside('lower bay%d hollow'%i,lower,[x,0,-100],False)
        inside('lower bay%d side wall'%i,lower,[x,c['body_half_width']-c['case_wall']/2,-15])
    # Eight upper cross webs and seven main seats are distinct source counts.
    webxs=[c['nose_to_first_row']-c['nose_second_web_spacing']]+[c['nose_to_first_row']+i*165.1 for i in range(7)]
    for i,x in enumerate(webxs):
        inside('upper web%d center material'%i,upper,[x,0,100])
        for sign in [-1,1]:
            inside('upper web%d side%d source window disposition'%(i,sign),upper,[x,sign*105,110],i in [0,1,7])
            witness=Part.makeCylinder(6.35,120,V(x,sign*c['bearing_stud_half_spacing'],-60))
            near('web%d side%d through bearing stud receiver'%(i,sign),upper.common(witness).Volume+lower.common(witness).Volume,0,1e-5)
    for i in range(7):
        x=c['nose_to_first_row']+i*165.1
        witness=Part.makeCylinder(33.3375,c['main_seat_width']-2,V(x-c['main_seat_width']/2+1,0,0),V(1,0,0))
        near('main bearing%d open shaft envelope'%i,upper.common(witness).Volume+lower.common(witness).Volume,0,1e-5)
        inside('upper main saddle%d material'%i,upper,[x,0,44])
        inside('lower main saddle%d material'%i,lower,[x,0,-44])
    for sign in [-1,1]:
        for i in range(7):
            x=c['nose_to_first_row']+i*165.1
            inside('mounting flange%d side%d bearing land'%(i,sign),upper,[x,sign*215.9,4])
            inside('mounting flange%d side%d unresolved hole not invented'%(i,sign),upper,[x,sign*215.9,6])
    inside('dry gear chamber void',upper,[last+60,100,100],False)
    inside('wet space below gear chamber',upper,[last+60,100,20],False)
    inside('gear chamber separating floor',upper,[last+60,100,c['gear_chamber_floor']-c['case_wall']/2])
    for port in d['gear_ports']:
        axis=V(*port['axis']);base=V(*port['origin']);witness=Part.makeCylinder(port['radius']-.5,320,base,axis)
        near('gear roof '+port['name']+' passage',upper.common(witness).Volume,0,1e-5)
    for y in [-19,19]:
        witness=Part.makeCylinder(5,130,V(c['nose_to_first_row']+50,y,-174),V(1,0,0))
        near('oil gallery '+str(y)+' open',lower.common(witness).Volume,0,1e-5)
    pump_x=last+c['oil_pump_receiver_after_last_row']
    witness=Part.makeCylinder(c['oil_pump_receiver_radius']-.5,20,V(pump_x,0,-c['gear_well_depth']-1))
    near('large lower pump opening',lower.common(witness).Volume,0,1e-5)
    inside('pump flange remaining land',lower,[pump_x,80,-c['gear_well_depth']+4])
    # Exact CAD edge-to-edge distances between retained section curves reveal
    # thin regions that nominal stock controls alone cannot certify.
    section=d['lower_section'];edges={}
    for key in ['outer_poles','inner_poles']:
        edges[key]=[]
        for poles in section[key]:
            curve=Part.BezierCurve();curve.setPoles([V(0,*p) for p in poles]);edges[key].append(curve.toShape())
    wall=min(a.distToShape(b)[0] for a in edges['outer_poles'] for b in edges['inner_poles'])
    ck('curved trough side wall meets selected stock',wall>=c['case_wall']-1e-6,dict(actual_minimum_mm=wall,selected_stock_mm=c['case_wall']))
    # Installation and revised support joints use actual saved world material.
    up=byid['EngineCase_upper']['shape'];lo=byid['EngineCase_lower']['shape']
    near('nose-to-flywheel axial gap',up.BoundBox.XMin-byid['ClutchDrum_flywheel']['shape'].BoundBox.XMax,c['output_clearance_to_flywheel'])
    for side in ['Left','Right']:
        rail=byid['EngineSuspension_'+side+'Rail']['shape'];gap(side+' upper mounting flange on rail',up,rail)
        near(side+' rail reaches extended engine mounting rows',rail.BoundBox.XMax,c['suspension_rail_front_x'])
        gap(side+' front yoke pad on rail',byid['EngineSuspension_FrontBracket']['shape'],rail)
        yoke=byid['EngineSuspension_FrontBracket']['shape']
        gap(side+' front rail bolt head on yoke',byid['EngineSuspension_'+side+'FrontRailBolt']['shape'],yoke)
        gap(side+' front cap lock on rail',byid['EngineSuspension_'+side+'CapLock']['shape'],rail)
        # Preserve material below the blind screw so a through hole cannot pass.
        sc=r['suspension_controls'];cc=r['crossmember_controls'];sgn=1 if side=='Left' else -1
        bottom=origin.z+sc['engine_mount_z_offset_from_crankshaft']-sc['rail_height']
        inside(side+' front cap blind floor',yoke,[cc['front_x']+sc['front_pad_x']+sc['front_cap_x_offset'],sgn*sc['rail_half_spacing'],bottom-sc['front_cap_boss_depth']+1])
    gap('front yoke on packing',byid['EngineSuspension_FrontBracket']['shape'],byid['EngineSuspension_FrontPacking']['shape'])
    clearance=lo.distToShape(byid['EngineSuspension_FrontBracket']['shape'])[0]
    ck('lower casting has positive yoke clearance',clearance>1,clearance)
    j=next(j for j in r['suspension_datums']['joints'] if j['name']=='FrontPivot');axis=V(*j['axis']);base=V(*j['base'])
    witness=Part.makeCylinder(19.05/2,j['grip'],base,axis)
    for n in ['EngineFrame_FrontCleat','EngineSuspension_FrontBracket']:near(n+' revised pivot bore',byid[n]['shape'].common(witness).Volume,0,1e-5)
    near('original pivot shaft retained',witness.cut(byid['EngineSuspension_FrontPivotBolt']['shape']).Volume,0,1e-5)
    gap('pivot head on cleat',byid['EngineSuspension_FrontPivotBolt']['shape'],byid['EngineFrame_FrontCleat']['shape'])
    for a1,b1 in [('FrontPivotNut','FrontPivotLock')]:gap(a1+' to '+b1,byid['EngineSuspension_'+a1]['shape'],byid['EngineSuspension_'+b1]['shape'])
    print('Checking inherited1902 occurrences.',flush=True)
    parent=App.openDocument(str(HERE/'engine_suspension_build/DrivetrainWithEngineSuspension.FCStd'));old={i['id']:i for i in leaves(parent.Root)};failed=[]
    for n,i in old.items():
        if n in r['changed_ids']:continue
        t,angle2=placement_errors(i['shape'].Placement,byid[n]['shape'].Placement)
        if not(same_shape(shape_signature(i['shape']),shape_signature(byid[n]['shape'])) and t<1e-6 and angle2<1e-8):failed.append(n)
    ck('1902 unaffected parent occurrences preserved',len(old)-7==1902 and not failed,failed)
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),scope='Two partial castings and revised static supports; engine internals and mounting identity conflicts remain open'))
    candidates=dict(byid);affected=set(r['exchange_ids']);pairs=[];seen=set()
    if not a.local_only:
        standard=check_build(STAGE/'build');tank=App.openDocument(standard['build']['top_document'])
        for i in leaves(tank.Root):
            if i['representation']!='layout' and i['id'] not in byid:candidates['Standard_'+i['id']]=i
    boxes={n:i['shape'].BoundBox for n,i in candidates.items()}
    def overlaps(a,b):return all(getattr(a,k+'Min')<=getattr(b,k+'Max')+1e-7 and getattr(b,k+'Min')<=getattr(a,k+'Max')+1e-7 for k in ['X','Y','Z'])
    for n in sorted(affected):
        for other in sorted(candidates):
            pair=tuple(sorted([n,other]))
            if n==other or pair in seen or not overlaps(boxes[n],boxes[other]):continue
            seen.add(pair);volume=abs(byid[n]['shape'].common(candidates[other]['shape']).Volume)
            pairs.append(dict(a=n,b=other,overlap_mm3=volume,passed=volume<1e-5))
            if len(pairs)%20==0:write(out/'material_progress.json',dict(checked=len(pairs),failed=[x for x in pairs if not x['passed']]))
    failures=[x for x in pairs if not x['passed']]
    write(out/'material_checks.json',dict(passed=not failures,native_sha256=sha(native),pairs=pairs,overlaps=failures,standard_context_checked=not a.local_only))
    print(len(checks),'independent;',len(pairs),'material pairs;',len(failures),'overlaps.',flush=True)
    assert all(x['passed'] for x in checks) and not failures
finally:
    runtime.close()
