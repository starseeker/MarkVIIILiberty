"""Independent saved-native dimensions, receiver witnesses and affected fit."""
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
p.add_argument('--candidate',type=Path,default=HERE/'clutch_brake_linkage_build')
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
    V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
    native=out/'TransmissionWithClutchBrake.FCStd';r=read(out/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};origin=doc.TransmissionCore.Placement.Base
    c=r['controls'];d=r['datums'];checks=[]
    def ck(name,result,detail=None):checks.append(dict(name=name,passed=bool(result),detail=detail))
    def near(name,actual,expected,tol=1e-6):ck(name,abs(actual-expected)<tol,dict(actual=actual,expected=expected,tolerance=tol))
    def local(name):
        s=byid[name]['shape'].copy();s.translate(-origin);return s
    def new(name):return local('ClutchBrake_'+name)
    def body(name):return doc.getObject('Def_ClutchBrake_'+name).Shape
    def inside(s,v):return s.isInside(v,1e-7,False)
    def gap(name,a,b,expected=0):near(name,a.distToShape(b)[0],expected)
    ck('1821 unique physical occurrences',len(items)==len(byid)==1821)
    ck('35 source-allocated additions',len(r['new_ids'])==35 and len(set(r['new_ids']))==35)
    ck('four named receiver revisions',set(r['changed_ids'])=={'ClutchStopBand_band','ClutchStopBand_lining','ClutchSupport_LeftBracket','ClutchThrowout_LeftLever'})
    ck('affected solids valid',all(byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1 for n in r['exchange_ids']))
    ck('definitions hidden',not doc.Definitions.Visibility)
    ck('all new links in brake groups',all(byid[n]['object'] in doc.ClutchStopAnchor.Group+doc.ClutchStopLinkage.Group for n in r['new_ids']))
    # Independent catalogue allocation, not just a total solid count.
    expected={'anchor':1,'anchor_rivet':6,'mount_bolt':2,'mount_nut':2,'mount_lock':2,
        'band_pin':1,'band_cotter':1,'eyebolt':1,'eye_adjuster':2,'eye_washer':2,'eye_plain_nut':2,
        'rod':1,'rod_nut':4,'rod_pin':1,'rod_cotter':1,'bell':1,'spring':1,'carrier':1,
        'bell_pin':1,'bell_nut':1,'bell_cotter':1}
    actual=Counter(byid[n]['definition'].removeprefix('clutch_brake_') for n in r['new_ids'])
    for key,count in expected.items():near('catalogue allocation '+key,actual[key],count)
    ck('SNL8 band assembly owns its26 physical children',len(leaves(doc.ClutchStopBandAssembly))==26)
    ck('anchor bolts are outside nested band inventory',all(byid['ClutchBrake_AnchorBolt%d'%i]['object'] in doc.ClutchStopLinkage.Group for i in [1,2]))
    near('source washer OD',body('eye_washer').BoundBox.XLength,34.925)
    near('source washer stock',body('eye_washer').BoundBox.ZLength,3.175)
    radii=sorted(set(round(f.Surface.Radius,7) for f in body('eye_washer').Faces if type(f.Surface).__name__=='Cylinder'))
    ck('source washer ID',6.35 in radii,radii)
    near('source SH955B nut thickness',body('eye_adjuster').BoundBox.ZLength,9.525)
    near('source SH955D nut thickness',body('rod_nut').BoundBox.ZLength,12.7)
    near('source3/4in stop rod nominal thread',min(f.Surface.Radius for f in body('rod_nut').Faces if type(f.Surface).__name__=='Cylinder')-.1,9.525)
    bolt=body('mount_bolt');faces=[f for f in bolt.Faces if type(f.Surface).__name__=='Cylinder']
    ck('source1/2x2-7/8 anchor bolt',any(abs(f.Surface.Radius-6.35)<1e-6 and abs(f.BoundBox.ZLength-73.025)<1e-6 for f in faces))
    for k,diameter,length in [('band',3.175,22.225),('rod',3.175,25.4),('bell',3.96875,25.4)]:
        detail=d['cotters'][k]
        near(k+' split-pin leg budget',detail['total_leg_centerline_mm'],length)
        # Actual two straight circular legs together span the nominal split-pin diameter.
        rr=[f.Surface.Radius for f in body(k+'_cotter').Faces if type(f.Surface).__name__=='Cylinder']
        near(k+' wire stock radius',min(rr),diameter*.24)
        ck(k+' separate cotter occurrence',len([n for n in r['new_ids'] if n=='ClutchBrake_'+k.title()+'Cotter'])==1)
    headvol=math.pi*c['rivet_head_height']*(3*c['rivet_head_radius']**2+c['rivet_head_height']**2)/6
    near('six source1/4x1 rivet blanks after forming',body('anchor_rivet').Volume,
        math.pi*(6.35/2)**2*25.4+headvol,1e-4)
    near('source rivet shaft radius',min(f.Surface.Radius for f in body('anchor_rivet').Faces if type(f.Surface).__name__=='Cylinder'),3.175)
    anchor=new('Anchor');band=local('ClutchStopBand_band');lining=local('ClutchStopBand_lining')
    for j in d['rivet_joints']:
        base=V(*j['base']);axis=V(*j['radial']);rv=local(j['name']);grip=j['grip']
        for name,shape in [('band',band),('anchor',anchor)]:
            witness=Part.makeCylinder(3.175,grip,base,axis)
            ck(j['name']+' real '+name+' bore',abs(shape.common(witness).Volume)<1e-7)
        gap(j['name']+' seated',rv,anchor)
        ck(j['name']+' lining below metal head',
           (base-axis*c['rivet_head_height']).Length>0 and math.hypot((base-axis*c['rivet_head_height']).y,(base-axis*c['rivet_head_height']).z)>117.975)
    eye=V(*d['eye']);axis=V(*d['eye_axis']);pivot=V(*d['bell_pivot']);normal=V(*d['bell_normal']);reye=V(*d['rod_eye'])
    for name,shape,point,ax,rad,length in [
        ('M4157 ears',band,eye-X*25.4,X,6.35,50.8),
        ('M4156 eye',new('Eyebolt'),eye-X*10,X,6.35,20),
        ('M4152 left lever',local('ClutchThrowout_LeftLever'),reye-Y*10,Y,6.35,20),
        ('M4152 fork',new('StopRod'),reye-Y*17,Y,6.35,34),
        ('M4165 carrier',new('Carrier'),pivot-normal*30,normal,10,25),
        ('M4165 crank',new('BellCrank'),pivot-normal*5,normal,10,10)]:
        ck(name+' receiving bore',abs(shape.common(Part.makeCylinder(rad,length,point,ax)).Volume)<1e-7)
    gap('eyebolt retained inside ears',new('Eyebolt'),band,.1)
    gap('spring rear washer seat',new('Spring'),new('EyeWasher1'))
    gap('spring front washer seat',new('Spring'),new('EyeWasher2'))
    gap('front washer bears on crank',new('EyeWasher2'),new('BellCrank'))
    gap('rear adjusting nut bears on crank',new('EyeAdjust2'),new('BellCrank'))
    gap('eye first jam pair',new('EyeJam1'),new('EyeAdjust1'))
    gap('eye second jam pair',new('EyeAdjust2'),new('EyeJam2'))
    gap('stop-rod fork side allowance',new('StopRod'),local('ClutchThrowout_LeftLever'),.2)
    for a1,b1 in [('RodNut1','RodNut2'),('RodNut2','BellCrank'),('BellCrank','RodNut3'),('RodNut3','RodNut4')]:
        gap(a1+' / '+b1+' seat',new(a1),new(b1))
    for i,m in enumerate(d['mounts'],1):
        start=V(*m['axis_start']);witness=Part.makeCylinder(6.35,m['clamped_grip'],start,Y)
        for name,shape in [('left bracket',local('ClutchSupport_LeftBracket')),('anchor',anchor),('carrier',new('Carrier'))]:
            ck('mount%d %s bore'%(i,name),abs(shape.common(witness).Volume)<1e-7)
        gap('mount%d head seated'%i,new('AnchorBolt%d'%i),local('ClutchSupport_LeftBracket'))
        gap('mount%d lockwasher seated'%i,new('AnchorLock%d'%i),new('Carrier'))
        gap('mount%d nut seated'%i,new('AnchorNut%d'%i),new('AnchorLock%d'%i))
        near('mount%d thread protrusion'%i,c['mount_length']-m['clamped_grip']-c['mount_lock_stock']-c['mount_nut_height'],5.7125)
    gap('shared mounting plate faces',anchor,new('Carrier'))
    ck('eyebolt clears spring bore',new('Eyebolt').common(new('Spring')).Volume<1e-7)
    ck('one M4165 source crown nut',len([n for n in r['new_ids'] if n=='ClutchBrake_BellNut'])==1)
    print('Checking inherited geometry and receiving changes.',flush=True)
    parent=App.openDocument(str(HERE/'clutch_support_build/TransmissionWithClutchSupports.FCStd'));old={i['id']:i for i in leaves(parent.Root)}
    failures=[]
    for n,i in old.items():
        if n in r['changed_ids']:continue
        j=byid[n];t,angle=placement_errors(i['shape'].Placement,j['shape'].Placement)
        if not(same_shape(shape_signature(i['shape']),shape_signature(j['shape'])) and t<1e-6 and angle<1e-8):failures.append(n)
    ck('1782 parent shapes and placements preserved',len(old)-4==1782 and not failures,failures)
    for n in ['ClutchStopBand_band','ClutchStopBand_lining','ClutchThrowout_LeftLever']:
        near(n+' no added material',byid[n]['shape'].cut(old[n]['shape']).Volume,0,1e-5)
    n='ClutchSupport_LeftBracket';near('old left bracket material retained',old[n]['shape'].cut(byid[n]['shape']).Volume,0,1e-5)
    near('left lever receiving hole only',old['ClutchThrowout_LeftLever']['shape'].cut(byid['ClutchThrowout_LeftLever']['shape']).Volume,
        math.pi*6.45**2*18,1e-4)
    App.closeDocument(parent.Name)
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),native_sha256=sha(native),
        checker_sha256=sha(Path(__file__)),checks=checks,scope='Static provisional full stop mechanism; no historical mounting or motion qualification'))
    # Evaluate every bounding-box candidate pair with an affected component.
    candidates=dict(byid);affected=set(r['exchange_ids']);pairs=[];seen=set()
    if not a.local_only:
        standard=check_build(STAGE/'build');tank=App.openDocument(standard['build']['top_document'])
        for i in leaves(tank.Root):
            if i['representation']!='layout' and i['id'] not in byid:candidates['Standard_'+i['id']]=i
    bounds={n:i['shape'].BoundBox for n,i in candidates.items()}
    def overlap(a,b):
        return all(getattr(a,k+'Min')<=getattr(b,k+'Max')+1e-7 and getattr(b,k+'Min')<=getattr(a,k+'Max')+1e-7 for k in ['X','Y','Z'])
    for n in sorted(affected):
        for other in sorted(candidates):
            key=tuple(sorted([n,other]))
            if n==other or key in seen or not overlap(bounds[n],bounds[other]):continue
            seen.add(key);one=byid[n]['shape'];two=candidates[other]['shape'];volume=abs(one.common(two).Volume)
            pairs.append(dict(a=n,b=other,overlap_mm3=volume,passed=volume<1e-5))
            if len(pairs)%20==0:
                write(out/'material_progress.json',dict(checked=len(pairs),failed=[x for x in pairs if not x['passed']]))
                print('Material pairs',len(pairs),flush=True)
    overlaps=[x for x in pairs if not x['passed']]
    write(out/'material_checks.json',dict(passed=not overlaps,native_sha256=sha(native),pairs=pairs,
        standard_context_checked=not a.local_only,overlaps=overlaps))
    print(len(checks),'independent checks;',len(pairs),'material pairs;',len(overlaps),'overlaps.',flush=True)
    assert all(x['passed'] for x in checks) and not overlaps
finally:
    runtime.close()
