"""Saved-artifact source dimensions, stock/void witnesses and affected clearances."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=HERE/'clutch_support_build')
p.add_argument('--worker',action='store_true');p.add_argument('--local-only',action='store_true')
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
    V=App.Vector;Y=V(0,1,0);X=V(1,0,0);Z=V(0,0,1)
    native=out/'TransmissionWithClutchSupports.FCStd';r=read(out/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items}
    origin=doc.TransmissionCore.Placement.Base;c=r['controls'];dat=r['datums'];checks=[]
    def ck(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
    def near(name,actual,expected,tolerance=1e-6):ck(name,abs(actual-expected)<tolerance,dict(actual=actual,expected=expected,tolerance=tolerance))
    def local(name):
        s=byid[name]['shape'].copy();s.translate(-origin);return s
    def inside(shape,point):return shape.isInside(V(*point),1e-7,False)
    def distance(a,b):return a.distToShape(b)[0]
    ck('27 mechanism additions, floor context, shaft and lever revisions',len(r['new_mechanism_ids'])==27 and r['context_revision_ids']==['hull_floor_7'] and r['changed_ids']==['ClutchThrowout_Shaft','ClutchThrowout_OperatingLever'])
    ck('unique physical occurrences',len(items)==len(byid)==1786)
    ck('affected solids valid',all(byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1 for n in r['exchange_ids']))
    ck('all definitions hidden',not doc.Definitions.Visibility)
    ck('shared five keys',sum(i['definition']=='clutch_throwout_key' for i in items)==5)
    ck('no invented main-shaft cotter occurrence',not any(n.endswith('MainCotter') for n in byid))
    shaft=doc.getObject('Def_ClutchThrowout_shaft').Shape
    ck('unsupported old main-shaft hole filled',all(inside(shaft,(x,259,0)) for x in [-18,-10,0,10,18]))
    ck('source-sized cup screw has a real cup',not inside(doc.Def_ClutchSupport_cup_screw.Shape,(c['set_screw_tip_x']-.5,0,0)))
    near('cup screw tip bears on shaft flat',distance(local('ClutchSupport_MainSetScrew'),local('ClutchThrowout_Shaft')),0)
    screw=doc.Def_ClutchSupport_cup_screw.Shape
    cylinder_faces=[f for f in screw.Faces if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-15.875/2)<1e-6]
    ck('source5/8x7/8 screw shank',len(cylinder_faces)==1 and abs(cylinder_faces[0].BoundBox.XLength-22.225)<1e-6)
    floor=local('hull_floor_7');ft=dat['floor_top'];th=dat['floor_thickness']
    near('physical floor thickness retained',floor.copy().cleaned().BoundBox.ZLength,6)
    for side,sgn,diameter,length in [('Right',-1,12.7,44.45),('Left',1,15.875,47.625)]:
        bracket=local('ClutchSupport_'+side+'Bracket')
        near(side+' bracket sits on floor',distance(bracket,floor),0)
        near(side+' journal is cylindrical with specified running allowance',distance(bracket,local('ClutchThrowout_Shaft')),0 if side=='Right' else .1)
        # Shaft head touches the right end face, hence its overall distance is0.
        for x,y,z in [(c['main_x'],sgn*c['bracket_y'],c['main_z'])]+([(c['main_x']+c['aux_dx'],c['aux_bracket_y'],c['main_z']+c['aux_dz'])] if side=='Left' else []):
            witness=Part.makeCylinder(19.04,c['journal_width'],V(x,y-c['journal_width']/2,z),Y)
            ck(side+' open shaft journal '+str(x),abs(bracket.common(witness).Volume)<1e-7)
            ck(side+' stock around journal '+str(x),inside(bracket,(x+23,y,z)))
        for m in [m for m in dat['mounts'] if m['side']==side]:
            n=m['name'];cap=local(n);x,y,z=m['center'];radius=diameter/2
            near(n+' underhead length from cylindrical surface',next(f.BoundBox.ZLength for f in cap.Faces if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-radius)<1e-6),length)
            near(n+' head seats below floor',distance(cap,floor),0)
            near(n+' engagement',z+length-ft,length-6)
            bore=Part.makeCylinder(radius+.1,6,V(x,y,ft-6),Z)
            ck(n+' floor clearance through full thickness',abs(floor.common(bore).Volume)<1e-7)
            ck(n+' floor stock outside hole',inside(floor,(x+radius+.5,y,ft-3)))
            ck(n+' blind receiving bore clears tip',not inside(bracket,(x,y,z+length+.5)))
            ck(n+' stock closes blind receiving bore',inside(bracket,(x,y,z+length+1.5)))
            ck(n+' boss surrounds fastener',inside(bracket,(x+radius+1,y,ft+10)))
    # Independent preservation of the parent, allowing only the named shaft regions.
    print('Source dimensions and mount witnesses checked; comparing inherited geometry.',flush=True)
    parent=App.openDocument(str(HERE/'clutch_throwout_build/TransmissionWithClutchThrowout.FCStd'))
    old={i['id']:i for i in leaves(parent.Root)}
    failures=[]
    for n,i in old.items():
        if n in r['changed_ids']:continue
        t,angle=placement_errors(i['shape'].Placement,byid[n]['shape'].Placement)
        if not same_shape(shape_signature(i['shape']),shape_signature(byid[n]['shape'])) or t>=1e-6 or angle>=1e-8:failures.append(n)
    ck('1756 inherited occurrences preserved',not failures and len(old)-2==1756,failures)
    ck('operating arm rearward and below shaft',dat['rod_eyes'][0][0]<dat['main_axis'][0] and dat['rod_eyes'][0][2]<dat['main_axis'][2])
    ck('auxiliary shaft toward transmission',dat['aux_axis'][0]<dat['main_axis'][0])
    old_shaft=old['ClutchThrowout_Shaft']['target'].Shape
    allowed=Part.makeCylinder(2.11,50,V(-25,259,0),X).fuse(Part.makeBox(25,18,18,V(-40,125,-9)))
    missing=old_shaft.cut(shaft).cut(allowed);added=shaft.cut(old_shaft).cut(allowed)
    ck('main shaft changed only at unsupported hole and cup seating flat',abs(missing.Volume)<1e-7 and abs(added.Volume)<1e-7)
    old_lever=old['ClutchThrowout_OperatingLever']['target'].Shape
    new_lever=doc.Def_ClutchThrowout_operating_lever.Shape
    hub_region=Part.makeCylinder(31,44,V(0,-22,0),Y)
    ck('M4164 hub and keyed receiver preserved',abs(old_lever.cut(new_lever).common(hub_region).Volume)<1e-7 and abs(new_lever.cut(old_lever).common(hub_region).Volume)<1e-7)
    for j,y in enumerate(c['aux_lever_ys'],1):
        prefix='ClutchSupport_Aux';key=local(prefix+'Key'+str(j));lever=local(prefix+'Lever'+str(j));ax=dat['aux_axis'][0];az=dat['aux_axis'][2]
        pin=local(prefix+'Taper'+str(j))
        near('No6 taper%d source3in length'%j,pin.copy().cleaned().BoundBox.XLength,76.2)
        ck('No6 taper%d actual conical surface'%j,any(type(f.Surface).__name__=='Cone' for f in pin.Faces))
        ck('Aux key%d reuses M4172'%j,byid[prefix+'Key'+str(j)]['target'].Name=='Def_ClutchThrowout_key')
        near('Aux lever%d keyed fit clearance'%j,distance(key,lever),.1)
        ck('Aux lever%d eye passage'%j,abs(lever.common(Part.makeCylinder(8,18,V(ax,y-9,az+c['aux_eye_height']),Y)).Volume)<1e-7)
        ck('Aux lever%d pin opens both shaft and hub'%j,abs(pin.common(local(prefix+'Shaft')).Volume)<1e-7 and abs(pin.common(lever).Volume)<1e-7)
    near('Aux shaft fits left bracket',distance(local('ClutchSupport_AuxShaft'),local('ClutchSupport_LeftBracket')),.1)
    for side,eye in zip(['Main','Aux'],dat['rod_eyes']):
        fork=local('ClutchSupport_'+side+'Fork');pin=local('ClutchSupport_'+side+'ForkPin');cotter=local('ClutchSupport_'+side+'ForkCotter')
        near(side+' fork pin head seating',distance(fork,pin),0)
        pin_faces=[f for f in pin.Faces if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-8)<1e-6]
        ck(side+' source1-7/8in pin underhead length',any(abs(f.BoundBox.YLength-47.625)<1e-6 for f in pin_faces))
        ck(side+' cotter passes real pin bore',abs(pin.common(cotter).Volume)<1e-7)
        near(side+' rod nut contacts fork',distance(fork,local('ClutchSupport_'+side+'RodNut')),0)
        ck(side+' rod occupies fork threaded socket',distance(fork,local('ClutchSupport_RearAuxRod'))<.101)
    near('source7/8in cotter leg stock budget',dat['cotter']['total_leg_centerline_mm'],22.225)
    ck('source length convention is retained as an assumption',read(HERE/'clutch_support_controls.json')['evidence']['rod'].find('under-head')>=0)
    # Floor is a replacement, not a second plate added to the tank BOM.
    print('Local interfaces checked; loading standard floor and neighboring context.',flush=True)
    standard=check_build(STAGE/'build');ck('standard native hashes unchanged',standard['native_hashes']==r['standard_native_hashes'])
    tank=App.openDocument(standard['build']['top_document']);standard_items=leaves(tank.Root)
    previous_floor=next(i['shape'] for i in standard_items if i['id']=='hull_floor_7')
    actual_floor=byid['hull_floor_7']['shape'];tools=[]
    for m in dat['mounts']:
        point=origin+V(*m['center']);tools.append(Part.makeCylinder(m['diameter']/2+c['cap_hole_clearance']+1e-6,8,point-Z,Z))
    ck('floor revision removes only eight bounded holes',abs(actual_floor.cut(previous_floor).Volume)<1e-7 and abs(previous_floor.cut(actual_floor).cut(Part.makeCompound(tools)).Volume)<1e-7)
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),scope='Physical fit of provisional brackets/controls; not historical mounting proof'))
    print('Independent checks:',len(checks),'failures:',[x for x in checks if not x['passed']],flush=True)
    all_shapes={n:i['shape'] for n,i in byid.items()}
    if not a.local_only:
        all_shapes.update({'Standard:'+i['id']:i['shape'] for i in standard_items if i['representation']!='layout' and i['id'] not in byid})
    bounds={n:s.copy().cleaned().BoundBox for n,s in all_shapes.items()};seen=set();pairs=[]
    for name in r['exchange_ids']:
        for other in all_shapes:
            pair=tuple(sorted((name,other)))
            if name==other or pair in seen or not bounds[name].intersect(bounds[other]):continue
            seen.add(pair);common=all_shapes[name].common(all_shapes[other]);vol=abs(common.Volume)
            pairs.append(dict(parts=pair,volume_mm3=vol,passed=vol<1e-5))
        print(name,'pairs:',len(pairs),'overlaps:',sum(not x['passed'] for x in pairs),flush=True)
        write(out/'material_progress.json',dict(last=name,pairs=len(pairs),overlaps=[x for x in pairs if not x['passed']]))
    write(out/'material_checks.json',dict(passed=all(x['passed'] for x in pairs),native_sha256=sha(native),pairs=pairs,
        standard_context_checked=not a.local_only,overlaps=[x for x in pairs if not x['passed']]))
    assert all(x['passed'] for x in checks) and all(x['passed'] for x in pairs)
finally:
    runtime.close()
