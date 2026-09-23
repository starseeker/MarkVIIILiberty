"""Verify saved suspension interfaces independently of the constructor."""
import argparse
from collections import Counter
import math
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=HERE/'engine_suspension_build');p.add_argument('--worker',action='store_true');p.add_argument('--local-only',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    args=[sys.executable,__file__,'--candidate',str(out),'--worker']
    if a.local_only:args.append('--local-only')
    with (out/'interface_check.log').open('w') as log:
        sys.exit(subprocess.run(args,env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,shape_signature
    from lib.worker import same_shape,placement_errors,check_build
    V=App.Vector;Z=V(0,0,1)
    native=out/'DrivetrainWithEngineSuspension.FCStd';r=read(out/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};c=r['controls'];cc=r['crossmember_controls'];d=r['datums'];checks=[]
    def ck(name,result,detail=None):checks.append(dict(name=name,passed=bool(result),detail=detail))
    def near(name,actual,expected,tol=1e-6):ck(name,abs(actual-expected)<tol,dict(actual=actual,expected=expected,tolerance=tol))
    def body(key):return doc.getObject('Def_EngineSuspension_'+key).Shape
    def inst(name):return byid['EngineSuspension_'+name]['shape']
    def gap(name,one,two):near(name,one.distToShape(two)[0],0)
    ck('1909 unique physical occurrences',len(items)==len(byid)==1909 and all(i['representation']!='layout' for i in items))
    ck('86 engine-mount pieces including14 separately sourced floor rivets',len(leaves(doc.EngineMounts))==86 and len(leaves(doc.FloorAttachments))==14)
    for group,count in [('FrontSuspension',15),('LeftRearSuspension',22),('RightRearSuspension',22),('LongitudinalSupports',2)]:
        ck(group+' source-allocated ownership',len(leaves(doc.getObject(group)))==count and doc.getObject(group) in doc.EngineMounts.Group)
    ck('all61 additions valid single solids',len(r['new_ids'])==61 and all(byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1 for n in r['exchange_ids']))
    ck('definitions hidden',not doc.Definitions.Visibility)
    expected={'left_rail':1,'right_rail':1,'left_bracket':1,'right_bracket':1,'front_bracket':1,'rear_packing':2,'front_packing':1,'bevel_washer':4,
              'half_bolt':10,'half_nut':10,'half_lock':12,'rear_bolt':4,'rear_nut':4,'rear_lock':4,'pivot_bolt':1,'pivot_nut':1,'pivot_lock':1,'cap':2}
    actual=Counter(byid[n]['definition'].removeprefix('engine_suspension_') for n in r['new_ids'])
    ck('exact SNL242 remaining61-piece inventory',dict(actual)==expected,dict(actual))
    # Source diameters/lengths are literals independent of the constructor's controls.
    for key,diam,length in [('half_bolt',12.7,44.45),('rear_bolt',15.875,63.5),('pivot_bolt',19.05,63.5),('cap',12.7,38.1)]:
        s=body(key);cyl=[f for f in s.Faces if type(f.Surface).__name__=='Cylinder']
        ck(key+' source shaft dimensions',any(abs(f.Surface.Radius-diam/2)<1e-6 and abs(f.BoundBox.ZLength-length)<1e-6 for f in cyl))
        witness=Part.makeCylinder(diam/2,length)
        near(key+' complete shaft material',witness.cut(s).Volume,0,1e-5)
        near(key+' head below under-head datum',s.BoundBox.ZMin,-c['head_height_ratio']*diam)
    near('conditional HB44 half bolt-row spacing',c['rail_half_spacing'],8.5*25.4)
    rail_low=r['crankshaft_axis_z']+c['engine_mount_z_offset_from_crankshaft']-c['rail_height']
    for side,sign in [('Left',1),('Right',-1)]:
        rail=inst(side+'Rail');bb=rail.BoundBox
        near(side+' rail aft end',bb.XMin,c['rail_rear_x'])
        near(side+' rail forward end',bb.XMax,c['rail_front_x'])
        near(side+' rail engine mounting plane',bb.ZMax,r['crankshaft_axis_z']+c['engine_mount_z_offset_from_crankshaft'])
        near(side+' rail row center',(bb.YMin+bb.YMax)/2,sign*215.9)
        near(side+' rail width',bb.YLength,c['rail_width'])
        near(side+' rail height',bb.ZLength,c['rail_height'])
        # A span away from bracket bores exposes the actual open rail section.
        x=(c['rail_rear_x']+c['rail_front_x'])/2;y=sign*215.9;z=rail_low+c['rail_height']/2
        ck(side+' rail has open C web space',not rail.isInside(V(x,y,z),1e-7,False))
        ck(side+' rail web faces outboard',rail.isInside(V(x,y+sign*(c['rail_width']/2-c['rail_web']/2),z),1e-7,False))
        gap(side+' rear top pad seated on rail',inst(side+'Bracket'),rail)
        gap(side+' front pad seated on rail',inst('FrontBracket'),rail)
        gap(side+' packing on bracket',inst(side+'Packing'),inst(side+'Bracket'))
        gap(side+' packing on crossmember',inst(side+'Packing'),byid['EngineFrame_RearChannel']['shape'])
    inner_gap=inst('LeftRail').BoundBox.YMin-inst('RightRail').BoundBox.YMax
    ck('conditional aviation bearer gap exceeds14-7/8in minimum',inner_gap>=14.875*25.4,dict(actual=inner_gap,minimum=14.875*25.4))
    gap('front packing on cleat ledge',inst('FrontPacking'),byid['EngineFrame_FrontCleat']['shape'])
    gap('front packing on yoke',inst('FrontPacking'),inst('FrontBracket'))
    gap('front yoke against cleat upright',inst('FrontBracket'),byid['EngineFrame_FrontCleat']['shape'])
    # Check actual wedge material on either side of the central bore.
    wedge=body('bevel_washer');slope=math.tan(math.radians(c['rear_channel_upper_taper_deg']))
    for x in [-10,10]:
        z=c['bevel_washer_center_stock']-slope*x
        ck('bevel slope interior x'+str(x),wedge.isInside(V(x,10,z-.01),1e-7,False))
        ck('bevel slope exterior x'+str(x),not wedge.isInside(V(x,10,z+.01),1e-7,False))
    near('bevel bore source5/8 bolt envelope',wedge.common(Part.makeCylinder(15.875/2,30,V(0,0,-1))).Volume,0,1e-7)
    receiving={'left_rail':'LeftRail','right_rail':'RightRail','left_bracket':'LeftBracket','right_bracket':'RightBracket','front_bracket':'FrontBracket'}
    def receiver(key,j):
        if key.startswith('EngineFrame_'):return byid[key]['shape']
        if key=='rear_packing':return inst(('Left' if j['name'].startswith('Left') else 'Right')+'Packing')
        return inst(receiving[key])
    for j in d['joints']:
        name=j['name'];base=V(*j['base']);axis=V(*j['axis']);key=j['hardware']
        if key=='cap':
            side='Left' if name.startswith('Left') else 'Right';bolt=inst(name)
            witness=Part.makeCylinder(12.7/2,38.1,base,axis)
            for k in j['receiver_keys']:near(name+' nominal thread/clearance in '+k,receiver(k,j).common(witness).Volume,0,1e-7)
            near(name+' full shank retained',witness.cut(bolt).Volume,0,1e-5)
            gap(name+' head on lock',bolt,inst(side+'CapLock'))
            gap(name+' lock on rail',inst(side+'CapLock'),inst(side+'Rail'))
            ck(name+' blind bore retains casting floor',j['blind_floor']>3,j['blind_floor'])
            p=V(base.x,base.y,d['cap_boss_bottom_world_z']+1)
            ck(name+' actual boss floor material',inst('FrontBracket').isInside(p,1e-7,False))
            continue
        diam={'half':12.7,'rear':15.875,'pivot':19.05}[key]
        length={'half':44.45,'rear':63.5,'pivot':63.5}[key]
        witness=Part.makeCylinder(diam/2,j['grip'],base,axis)
        for k in j['receiver_keys']:near(name+' bore through '+k,receiver(k,j).common(witness).Volume,0,1e-7)
        near(name+' complete clamped shank',witness.cut(inst(name+'Bolt')).Volume,0,1e-5)
        gap(name+' head on first receiver',inst(name+'Bolt'),receiver(j['receiver_keys'][0],j))
        gap(name+' nut on lock',inst(name+'Nut'),inst(name+'Lock'))
        near(name+' positive source bolt protrusion',j['thread_protrusion'],length-j['grip']-diam*(c['lock_stock_ratio']+c['nut_height_ratio']))
        ck(name+' full nut threaded engagement',j['thread_protrusion']>0,j['thread_protrusion'])
        if key=='rear':
            bevel=name.replace('Base','Bevel')
            gap(name+' bevel on tapered channel',inst(bevel),byid['EngineFrame_RearChannel']['shape'])
            gap(name+' lock on bevel',inst(name+'Lock'),inst(bevel))
        else:gap(name+' lock on last receiver',inst(name+'Lock'),receiver(j['receiver_keys'][-1],j))
    print('Checking inherited material and the two receiving revisions.',flush=True)
    parent=App.openDocument(str(HERE/'engine_crossmember_build/DrivetrainWithEngineCrossmembers.FCStd'));old={i['id']:i for i in leaves(parent.Root)}
    failed=[]
    for n,i in old.items():
        if n in r['changed_ids']:continue
        other=byid[n];t,ang=placement_errors(i['shape'].Placement,other['shape'].Placement)
        if not(same_shape(shape_signature(i['shape']),shape_signature(other['shape'])) and t<1e-6 and ang<1e-8):failed.append(n)
    ck('1846 inherited occurrences preserved including all floors',len(old)-2==1846 and not failed,failed)
    front=byid['EngineFrame_FrontCleat']['shape'];of=old['EngineFrame_FrontCleat']['shape']
    near('original front cleat material preserved',of.cut(front).Volume,0,1e-5)
    expected_add=cc['cleat_stock']*2*cc['cleat_half_width']*(c['packing_stock']+c['front_hub_height'])-math.pi*(19.05/2+c['hole_radial_allowance'])**2*cc['cleat_stock']
    near('cleat upright and source pivot bore only',front.cut(of).Volume,expected_add,1e-4)
    rear=byid['EngineFrame_RearChannel']['shape'];ob=old['EngineFrame_RearChannel']['shape'];radius=15.875/2+c['hole_radial_allowance']
    near('rear channel original material loses4 base bores only',ob.cut(rear).Volume,4*math.pi*radius**2*cc['channel_flange'],1e-4)
    width=cc['channel_depth']-cc['channel_web'];extra=slope*(c['rear_base_bolt_x']+cc['channel_depth']/2)
    added=.5*width**2*slope*(2*cc['channel_half_span'])-4*math.pi*radius**2*extra
    near('rear upper taper material less four bores',rear.cut(ob).Volume,added,1e-4)
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),scope='Static provisional full support inventory; tank engine flange and historical mounting unqualified'))
    candidates=dict(byid);affected=set(r['exchange_ids']);pairs=[];seen=set()
    if not a.local_only:
        standard=check_build(STAGE/'build');tank=App.openDocument(standard['build']['top_document'])
        for i in leaves(tank.Root):
            if i['representation']!='layout' and i['id'] not in byid:candidates['Standard_'+i['id']]=i
    bounds={n:i['shape'].BoundBox for n,i in candidates.items()}
    def overlap(a,b):return all(getattr(a,k+'Min')<=getattr(b,k+'Max')+1e-7 and getattr(b,k+'Min')<=getattr(a,k+'Max')+1e-7 for k in ['X','Y','Z'])
    for n in sorted(affected):
        for other in sorted(candidates):
            pair=tuple(sorted([n,other]))
            if n==other or pair in seen or not overlap(bounds[n],bounds[other]):continue
            seen.add(pair);vol=abs(byid[n]['shape'].common(candidates[other]['shape']).Volume)
            pairs.append(dict(a=n,b=other,overlap_mm3=vol,passed=vol<1e-5))
            if len(pairs)%20==0:
                write(out/'material_progress.json',dict(checked=len(pairs),failed=[x for x in pairs if not x['passed']]))
                print('Material pairs',len(pairs),flush=True)
    failures=[x for x in pairs if not x['passed']]
    write(out/'material_checks.json',dict(passed=not failures,native_sha256=sha(native),pairs=pairs,overlaps=failures,standard_context_checked=not a.local_only))
    print(len(checks),'independent checks;',len(pairs),'material pairs;',len(failures),'overlaps.',flush=True)
    assert all(x['passed'] for x in checks) and not failures
finally:
    runtime.close()
