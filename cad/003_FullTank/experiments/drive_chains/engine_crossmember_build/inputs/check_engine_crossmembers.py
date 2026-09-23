"""Independent saved-native inventory, material, floor and neighbor verification."""
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
p.add_argument('--candidate',type=Path,default=HERE/'engine_crossmember_build')
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
    V=App.Vector
    native=out/'DrivetrainWithEngineCrossmembers.FCStd';r=read(out/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};c=r['controls'];checks=[]
    def ck(name,result,detail=None):checks.append(dict(name=name,passed=bool(result),detail=detail))
    def near(name,actual,expected,tol=1e-6):ck(name,abs(actual-expected)<tol,dict(actual=actual,expected=expected,tolerance=tol))
    def body(key):return doc.getObject('Def_EngineFrame_'+key).Shape
    def inst(name):return byid['EngineFrame_'+name]['shape']
    def gap(name,s1,s2):near(name,s1.distToShape(s2)[0],0)
    ck('1848 unique physical occurrences',len(items)==len(byid)==1848 and all(i['representation']!='layout' for i in items))
    ck('25 physical engine-frame pieces under Powerplant',len(leaves(doc.PowerplantDevelopment))==25)
    ck('SNL63 nested front channel has4 children',len(leaves(doc.FrontCrossmember))==4)
    ck('SNL63 nested rear channel has7 children',len(leaves(doc.RearCrossmember))==7)
    ck('SNL175 direct floor joints have14 extra rivets',len(leaves(doc.FloorAttachments))==14)
    ck('two replacement context plates',len(leaves(doc.EngineFloorReplacementContext))==2)
    ck('definitions hidden',not doc.Definitions.Visibility)
    ck('affected shapes valid single solids',all(byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1 for n in r['exchange_ids']))
    expected={'front_channel':1,'rear_channel':1,'cleat':1,'left_gusset':1,'right_gusset':1,'front_rivet':2,'rear_rivet':4,'channel_floor_rivet':10,'gusset_floor_rivet':4}
    counts=Counter(i['definition'].removeprefix('engine_frame_') for i in leaves(doc.PowerplantDevelopment))
    ck('exact engine-frame definition inventory',dict(counts)==expected,dict(counts))
    ck('frame group has correct Powerplant ownership',doc.EngineMounts in doc.PowerplantDevelopment.Group and all(doc.getObject(n) in doc.EngineMounts.Group for n in ['FrontCrossmember','RearCrossmember','FloorAttachments']))
    # Inspect real cylindrical shaft surfaces and material budgets independently of forming receipts.
    for key,diam,length,grip in [('front_rivet',15.875,53.975,c['channel_web']+c['cleat_stock']),
                               ('rear_rivet',17.4625,53.975,c['channel_web']+c['gusset_stock']),
                               ('channel_floor_rivet',17.4625,47.625,6+c['channel_flange']),
                               ('gusset_floor_rivet',17.4625,47.625,6+c['gusset_stock'])]:
        s=body(key);radius=diam*c['head_radius_ratio'];height=diam*c['head_height_ratio']
        hv=math.pi*height*(3*radius**2+height**2)/6
        near(key+' source blank volume retained after forming',s.Volume,math.pi*(diam/2)**2*length+hv,1e-4)
        cylinders=[f for f in s.Faces if type(f.Surface).__name__=='Cylinder']
        ck(key+' source shaft radius and grip',any(abs(f.Surface.Radius-diam/2)<1e-6 and abs(f.BoundBox.ZLength-grip)<1e-6 for f in cylinders))
        near(key+' factory head height',s.BoundBox.ZMin,-height)
        ck(key+' connected factory and upset heads',s.isInside(V(diam*.65,0,-height*.25),1e-7,False) and s.isInside(V(diam*.65,0,grip+height*.25),1e-7,False))
    for which,floor in [('Front','hull_floor_6'),('Rear','hull_floor_7')]:
        s=inst(which+'Channel');b=s.BoundBox;d=c['channel_depth']/2;x=c[which.lower()+'_x']
        near(which+' span',b.YLength,2*c['channel_half_span'])
        near(which+' height',b.ZLength,c['channel_height'])
        near(which+' longitudinal station',(b.XMin+b.XMax)/2,x)
        near(which+' floor seat',b.ZMin,533.05)
        gap(which+' floor bearing face',s,byid[floor]['shape'])
        ck(which+' open C section void',not s.isInside(V(x,100,c['floor_top']+c['channel_height']/2),1e-7,False))
        ck(which+' full web material',s.isInside(V(x+d-c['channel_web']/2,100,c['floor_top']+c['channel_height']/2),1e-7,False))
    for side in ['Left','Right']:
        gap(side+' gusset on floor',inst(side+'Gusset'),byid['hull_floor_7']['shape'])
        gap(side+' gusset on channel',inst(side+'Gusset'),inst('RearChannel'))
    gap('cleat on front channel',inst('FrontCleat'),inst('FrontChannel'))
    receiving={'front_channel':'FrontChannel','rear_channel':'RearChannel','cleat':'FrontCleat','left_gusset':'LeftGusset','right_gusset':'RightGusset'}
    for j in r['datums']['joints']:
        base=V(*j['base']);axis=V(*j['axis']);rv=byid[j['name']]['shape']
        witness=Part.makeCylinder(j['diameter']/2,j['grip'],base,axis)
        receivers=[inst(receiving[key]) for key in j['receivers']]
        if 'floor' in j:receivers.append(byid[j['floor']]['shape'])
        for k,s in enumerate(receivers):
            near(j['name']+' receiver%d bore'%k,s.common(witness).Volume,0,1e-7)
            gap(j['name']+' receiver%d seat'%k,rv,s)
        # A shank witness must be completely filled, ruling out a head-only model.
        near(j['name']+' continuous shank',witness.cut(rv).Volume,0,1e-5)
    # Compare against the immutable parent, including complete inherited geometry.
    parent=App.openDocument(str(HERE/'clutch_brake_linkage_build/TransmissionWithClutchBrake.FCStd'))
    old={i['id']:i for i in leaves(parent.Root)};failures=[]
    for n,i in old.items():
        if n=='hull_floor_7':continue
        j=byid[n];t,ang=placement_errors(i['shape'].Placement,j['shape'].Placement)
        if not(same_shape(shape_signature(i['shape']),shape_signature(j['shape'])) and t<1e-6 and ang<1e-8):failures.append(n)
    ck('1820 inherited shapes and placements preserved',len(old)-1==1820 and not failures,failures)
    standard=check_build(STAGE/'build');tank=App.openDocument(standard['build']['top_document']);std={i['id']:i for i in leaves(tank.Root)}
    prior=old['hull_floor_7']['shape'].multiFuse([std['hull_floor_5']['shape'],std['hull_floor_6']['shape']]).removeSplitter()
    updated=byid['hull_floor_7']['shape'].multiFuse([byid['hull_floor_5']['shape'],byid['hull_floor_6']['shape']]).removeSplitter()
    # Independent floor bore positions, from the14 source-allocated joints.
    points=[(c[which+'_x']+c['channel_floor_rivet_x'],y) for which in ['front','rear'] for y in c['channel_floor_rivet_y']]
    points += [(c['rear_x']+c['gusset_floor_rivet_x'],sign*c['gusset_y']+dy) for sign in [-1,1] for dy in [-c['gusset_rivet_y'],c['gusset_rivet_y']]]
    expected_floor=prior
    for x,y in points:expected_floor=expected_floor.cut(Part.makeCylinder(17.4625/2+c['hole_radial_allowance'],8,V(x,y,526.05)))
    near('floor union no extra material',updated.cut(expected_floor).Volume,0,1e-5)
    near('floor union no missing material including inherited holes',expected_floor.cut(updated).Volume,0,1e-5)
    near('floor14 new source-sized bores only',prior.Volume-updated.Volume,14*math.pi*(17.4625/2+c['hole_radial_allowance'])**2*6,1e-4)
    for key,value in [('floor_5_6_seam',byid['hull_floor_5']['shape'].BoundBox.XMin),('floor_6_7_seam',byid['hull_floor_7']['shape'].BoundBox.XMax)]:near(key,value,c[key])
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),scope='Crossmembers and14 direct floor joints; estimated source placement, no historical qualification'))
    candidates=dict(byid);affected=set(r['exchange_ids']);pairs=[];seen=set()
    if not a.local_only:
        for n,i in std.items():
            if i['representation']!='layout' and n not in byid:candidates['Standard_'+n]=i
    bounds={n:i['shape'].BoundBox for n,i in candidates.items()}
    def overlap(a,b):return all(getattr(a,k+'Min')<=getattr(b,k+'Max')+1e-7 and getattr(b,k+'Min')<=getattr(a,k+'Max')+1e-7 for k in ['X','Y','Z'])
    for n in sorted(affected):
        for other in sorted(candidates):
            key=tuple(sorted([n,other]))
            if n==other or key in seen or not overlap(bounds[n],bounds[other]):continue
            seen.add(key);vol=abs(byid[n]['shape'].common(candidates[other]['shape']).Volume)
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
