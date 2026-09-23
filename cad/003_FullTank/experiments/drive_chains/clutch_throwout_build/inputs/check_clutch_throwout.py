"""Independent saved-native dimensions, receiver witnesses and context clearances."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent; STAGE=HERE.parents[1]; ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=HERE/'clutch_throwout_build')
p.add_argument('--local-only',action='store_true')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    args=[sys.executable,__file__,'--candidate',str(out),'--worker']
    if a.local_only:args.append('--local-only')
    with (out/'interface_check.log').open('w') as log:
        sys.exit(subprocess.run(args,env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves,shape_signature
    from lib.worker import check_build,same_shape,placement_errors
    V=App.Vector
    native=out/'TransmissionWithClutchThrowout.FCStd';r=read(out/'report.json');nh=sha(native)
    assert nh==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items}
    origin=doc.TransmissionCore.Placement.Base;c=r['controls'];checks=[]
    shapes={}
    for n in r['new_ids']+['FrontClutch_Coupling']:
        s=byid[n]['shape'].copy();s.translate(-origin);shapes[n]=s
    def ck(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
    def near(name,actual,expected,tol=1e-6):ck(name,abs(actual-expected)<tol,dict(actual=actual,expected=expected,tolerance=tol))
    def at(s,v):return s.isInside(V(*v),1e-7,False)
    ck('source units distinct from inferred commercial children',len(doc.ClutchThrowoutBearingLeft.Group)==len(doc.ClutchThrowoutBearingRight.Group) and r['datums']['source_bearing_units']==2)
    ck('all added native parts valid and single solid',all(shapes[n].isValid() and len(shapes[n].Solids)==1 for n in r['new_ids']))
    ck('unique occurrence count includes preserved parent',len(items)==len(byid)==1681+len(r['new_ids']))
    coupling=shapes['FrontClutch_Coupling']
    # Inspect actual collar planes, not just the placement/control table.
    planes=[]
    for face in coupling.Faces:
        if type(face.Surface).__name__=='Plane' and abs(face.normalAt(0,0).x)>1-1e-8:
            planes.append(face.CenterOfMass.x)
    ck('receiver axial surfaces still present',any(abs(x-744.95)<1e-6 for x in planes) and any(abs(x-821.95)<1e-6 for x in planes),sorted(set(round(x,6) for x in planes)))
    for side,sign in [('Left',1),('Right',-1)]:
        prefix='ClutchThrowout_'+side
        outer=shapes[prefix+'BearingOuter'];inner=shapes[prefix+'BearingInner'];cage=shapes[prefix+'BearingCage']
        bb=outer.copy().cleaned().BoundBox
        near(side+' printed OD via axial extent',bb.XLength,72)
        near(side+' printed OD via vertical extent',bb.ZLength,72)
        near(side+' printed width',bb.YLength,17)
        spheres=[f.Surface.Radius for f in outer.Faces if type(f.Surface).__name__=='Sphere']
        ck(side+' analytic spherical outer race retained',len(spheres)==1)
        if spheres:
            analytic=math.pi*17*(36**2-spheres[0]**2)+math.pi*17**3/12
            near(side+' race analytic volume',outer.Volume,analytic,1e-4)
        near(side+' rear flange running clearance',bb.XMin-744.95,2.5)
        near(side+' front flange running clearance',821.95-bb.XMax,2.5)
        center=V((bb.XMin+bb.XMax)/2,(bb.YMin+bb.YMax)/2,(bb.ZMin+bb.ZMax)/2)
        rot=App.Rotation(V(0,0,1),0 if sign==1 else 180)
        def point(x,y,z):return center+rot.multVec(V(x,y,z))
        for t in [.2,1.8,3.9,5.5]:
            unit=V(math.cos(t),0,math.sin(t))
            inside=point(unit.x*17.49,0,unit.z*17.49);outside=point(unit.x*17.51,0,unit.z*17.51)
            ck(side+' source35mm bore '+str(t),not inner.isInside(inside,1e-7,False) and inner.isInside(outside,1e-7,False))
        balls=[shapes[n] for n in r['new_ids'] if n.startswith(prefix+'Ball')]
        ck(side+' two actual ball rows',len({round(s.Solids[0].CenterOfMass.y,5) for s in balls})==2)
        near(side+' cage fits inside source bearing width',max(0,cage.copy().cleaned().BoundBox.YMax-bb.YMax,bb.YMin-cage.copy().cleaned().BoundBox.YMin),0)
        ck(side+' cage has open individual pockets',all(cage.common(b).Volume<1e-5 for b in balls))
        ck(side+' balls clear both races',all(b.common(inner).Volume<1e-5 and b.common(outer).Volume<1e-5 for b in balls))
        for suffix in ['InnerWasher','OuterWasher']:
            washer=shapes[prefix+suffix]
            near(side+suffix+' clamps inner race',washer.distToShape(inner)[0],0)
            ck(side+suffix+' clears rolling outer race',washer.distToShape(outer)[0]>1.49)
        pin=shapes[prefix+'Pin'];lever=shapes[prefix+'Lever']
        bore=Part.makeCylinder(17.49,16.98,center-V(0,8.49,0),V(0,1,0))
        near(side+' bearing bore is a void',inner.common(bore).Volume,0,1e-5)
        ck(side+' pin occupies bearing bore',pin.common(bore).Volume>15000)
        near(side+' pin journal clearance',pin.distToShape(inner)[0],.05)
        for suffix in ['Pin','Nut','Lockwasher','RetainerWasher','InnerWasher','OuterWasher','PinLockScrew','PinLockNut','Lever']:
            near(side+suffix+' no coupling intrusion',shapes[prefix+suffix].common(coupling).Volume,0,1e-5)
        # Pin stem lies in real fork bore. Check through a witness cylinder.
        v=point(0,29,0)
        witness=Part.makeCylinder(12.6,.5,v-V(0,.25,0),V(0,1,0))
        near(side+' real fork pin receiving hole',lever.common(witness).Volume,0,1e-5)
        ck(side+' stem present in receiving hole',pin.common(witness).Volume>230)
        near(side+' screw tip meets stem flat',shapes[prefix+'PinLockScrew'].distToShape(pin)[0],0)
        near(side+' locking nut seats on real boss',shapes[prefix+'PinLockNut'].distToShape(lever)[0],0)
        ck(side+' fork belongs to throwout assembly',byid[prefix+'Lever']['object'].getParentGeoFeatureGroup()==doc.ClutchThrowout)
        ck(side+' bearing nested under its catalogue unit',byid[prefix+'BearingOuter']['object'].getParentGeoFeatureGroup()==doc.getObject('ClutchThrowoutBearing'+side))
    shaft=shapes['ClutchThrowout_Shaft'];shaft_center=V(c['shaft_center_x'],0,c['shaft_center_z'])
    # Unkeyed central journal gives an independent material/void diameter witness.
    ck('shaft estimated38.1mm journal actually modeled',shaft.isInside(shaft_center+V(19.04,0,0),1e-7,False) and not shaft.isInside(shaft_center+V(19.06,0,0),1e-7,False))
    keys=[n for n in r['new_ids'] if 'MainKey' in n]
    ck('three main keys; two auxiliary keys pending',len(keys)==3)
    for name,levername in zip(keys,['RightLever','LeftLever','OperatingLever']):
        key=shapes[name];lever=shapes['ClutchThrowout_'+levername]
        near(name+' real shaft keyway',key.common(shaft).Volume,0,1e-5)
        near(name+' real lever keyway',key.common(lever).Volume,0,1e-5)
        ck(name+' engages shaft and lever bore regions',key.copy().cleaned().BoundBox.ZMin<shaft_center.z+19.05 and key.copy().cleaned().BoundBox.ZMax>shaft_center.z+19.15)
    # The parent is compared as saved world geometry, independently of the build.
    pn=HERE/'clutch_stop_band_build/TransmissionWithClutchStopBand.FCStd'
    assert sha(pn)==r['parent_native_sha256']
    parent=App.openDocument(str(pn));old=leaves(parent.Root)
    preserved=True
    for i in old:
        now=byid[i['id']]
        t,angle=placement_errors(i['shape'].Placement,now['shape'].Placement)
        preserved=preserved and same_shape(shape_signature(i['shape']),shape_signature(now['shape'])) and t<1e-6 and angle<1e-8
    ck('all1681 parent occurrences preserve geometry and world placement',preserved)
    report=dict(passed=all(x['passed'] for x in checks),native_sha256=nh,checker_sha256=sha(Path(__file__)),checks=checks,
                scope='Installed bearings/forks/main shaft only; brackets, retention, complete brake and historical fit pending')
    write(out/'independent_checks.json',report)
    print('Independent geometry:',len(checks),'checks; failures:',[x for x in checks if not x['passed']],flush=True)
    physical=items
    standard_hashes={}
    if not a.local_only:
        standard=check_build(STAGE/'build');standard_hashes=standard['native_hashes']
        tank=App.openDocument(standard['build']['top_document'])
        physical=items+[i for i in leaves(tank.Root) if i['representation']=='assembly']
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=[];seen=set()
    for name in r['new_ids']:
        s=byid[name]['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near_ids=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for idx in near_ids:
            other=physical[idx];pair=tuple(sorted([name,other['id']]))
            if name==other['id'] or pair in seen:continue
            seen.add(pair);volume=s.common(other['shape']).Volume
            pairs.append(dict(a=name,b=other['id'],intersection_mm3=volume))
        overlaps=[x for x in pairs if abs(x['intersection_mm3'])>1e-5]
        write(out/'material_progress.json',dict(last=name,pairs=len(pairs),overlaps=overlaps))
        print(name,len(pairs),'pairs;',len(overlaps),'overlaps',flush=True)
    write(out/'material_checks.json',dict(passed=not overlaps,native_sha256=nh,pairs=pairs,overlaps=overlaps,
        standard_context_checked=not a.local_only,standard_native_hashes=standard_hashes))
    assert report['passed'] and not overlaps
finally:
    runtime.close()
