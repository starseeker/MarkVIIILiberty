"""Independent study checks; unresolved installation clashes remain failures."""
import argparse
from collections import Counter
import hashlib
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'engine_lower_drive_study')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'independent_check.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],
            env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves
    from lib.worker import placement_errors
    V=App.Vector
    native=out/'DrivetrainWithLowerDriveStudy.FCStd';r=read(out/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};checks=[]
    def ck(name,passed,detail=None):
        checks.append(dict(name=name,passed=bool(passed),detail=detail))
        write(out/'check_progress.json',dict(completed=len(checks),last=name,failures=[r for r in checks if not r['passed']]))
        if not passed:print('FAIL',name,detail,flush=True)
    def near(name,value,target,tolerance=1e-5):ck(name,abs(value-target)<tolerance,dict(actual=value,target=target))
    def definition(key):return doc.getObject('Def_EngineLowerDrive_'+key).Shape
    new=sorted(n for n in byid if n.startswith('EngineLowerDrive_'))
    counts=Counter(byid[n]['definition'].removeprefix('engine_lower_drive_') for n in new)
    ck('2170 unique physical occurrences',len(items)==len(byid)==2170)
    ck('17 source-owned constituents',counts==dict(driver=1,bush=2,housing_flywheel=1,housing_distributor=1,dowel=1,bolt=2,nut=2,washer=4,cotter=2,retaining_screw=1),dict(counts))
    ck('10 shared definitions and hidden library',len({byid[n]['definition'] for n in new})==10 and not doc.Definitions.Visibility)
    ck('new components are valid single solids',all(byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1 for n in new))
    ck('engine owns lower distribution unit',doc.EngineLowerDistributionDrive in doc.TankLibertyEngine.Group)
    for n in [1,2]:ck('clamp set'+str(n)+' has five physical leaves',len(leaves(doc.getObject('EngineLowerDriveClampSet'+str(n))))==5)
    driver,bush=definition('driver'),definition('bush');c=r['controls']
    for key,n,mate,face,sign,offset in [('upper',22,33,c['upper_face'],-1,0),('lower',21,21,c['lower_face'],1,-c['pump_axis_drop'])]:
        pitch=n*c['module']/2;distance=math.hypot(pitch,mate*c['module']/2)-face/2
        delta=math.atan2(n,mate);radius=distance*math.sin(delta);z=offset+sign*distance*math.cos(delta)
        flags=[driver.isInside(V(radius*math.cos(2*math.pi*i/(n*32)),radius*math.sin(2*math.pi*i/(n*32)),z),1e-7,False) for i in range(n*32)]
        count=sum(flags[i] and not flags[i-1] for i in range(len(flags)))
        ck(key+' bevel native tooth count',count==n,count)
    # Recover the journal shoulders from material along a line outside the shaft.
    line=Part.makeLine(V(24,0,-250),V(24,0,0));segments=sorted(driver.common(line).Edges,key=lambda e:e.BoundBox.ZMin)
    ck('two gear shoulders bound journal',len(segments)==2,len(segments))
    lo,hi=segments[0].BoundBox.ZMax,segments[1].BoundBox.ZMin
    endplay=(hi-lo)-bush.BoundBox.ZLength
    ck('printed bearing endplay',.127-1e-6<=endplay<=.2032+1e-6,endplay)
    def cylindrical_radii(shape):
        return sorted({round(f.Surface.Radius,7) for f in shape.Faces if isinstance(f.Surface,Part.Cylinder)
            and abs(f.Surface.Axis.z)>.999999})
    sr=min(cylindrical_radii(driver),key=lambda x:abs(x-16))
    br=min(cylindrical_radii(bush),key=lambda x:abs(x-16))
    clearance=2*(br-sr)
    ck('printed diametrical bearing clearance',.0381-1e-6<=clearance<=.0635+1e-6,clearance)
    near('journal radial bearing separation',driver.distToShape(bush)[0],clearance/2)
    ck('continuous hollow driver',not driver.common(Part.makeCylinder(7.9,230,V(0,0,-230),V(0,0,1))).Faces)
    spline_z=lo+10;rad=8.8
    flags=[not driver.isInside(V(rad*math.cos(2*math.pi*i/360),rad*math.sin(2*math.pi*i/360),spline_z),1e-7,False) for i in range(360)]
    runs=sum(flags[i] and not flags[i-1] for i in range(360))
    ck('six estimated internal spline grooves present',runs==6,runs)
    mid=(bush.BoundBox.ZMin+bush.BoundBox.ZMax)/2
    ck('longitudinal bearing oil groove is open',not bush.isInside(V(br+.3,0,mid),1e-7,False))
    ck('bearing retains material beside groove',bush.isInside(V(br+.3,2,mid),1e-7,False))
    for key,sign in [('housing_distributor',1),('housing_flywheel',-1)]:
        s=definition(key)
        for n,z in enumerate([(bush.BoundBox.ZMin+mid)/2,(bush.BoundBox.ZMax+mid)/2]):
            ck(key+' window'+str(n)+' remains open',not s.isInside(V(sign*28,0,z),1e-7,False))
        ck(key+' end collar material',s.isInside(V(sign*30,0,bush.BoundBox.ZMax-3),1e-7,False))
        ck(key+' upper cup opening',not s.isInside(V(sign*31,0,s.BoundBox.ZMax-.8),1e-7,False))
        ck(key+' upper cup outer lip',s.isInside(V(sign*35,0,s.BoundBox.ZMax-.8),1e-7,False))
        ck(key+' lower end retains corresponding stock',s.isInside(V(sign*31,0,s.BoundBox.ZMin+.8),1e-7,False))
    outer=max(cylindrical_radii(definition('housing_distributor')))
    pass_envelope=Part.makeCylinder(outer-.25,250,V(0,0,-250),V(0,0,1))
    ck('complete integral driver clears housing-diameter receiving lug envelope',
       abs(driver.cut(pass_envelope).Volume)<1e-5,dict(housing_radius=outer,required_radial_margin=.25))
    near('printed clamp under-head length',definition('bolt').BoundBox.XMax,23.8125)
    near('printed dowel length',definition('dowel').BoundBox.XLength,9.525)
    near('printed dowel diameter',definition('dowel').BoundBox.YLength,4.7625)
    near('printed housing screw under-head length',max(f.BoundBox.XMax for f in definition('retaining_screw').Faces if isinstance(f.Surface,Part.Cylinder)),82.55)
    near('printed housing screw diameter',2*next(f.Surface.Radius for f in definition('retaining_screw').Faces if isinstance(f.Surface,Part.Cylinder)),9.525)
    # Check all previously saved material, independently of builder signatures.
    pn=HERE/'engine_gear_build/DrivetrainWithEngineGear.FCStd';assert sha(pn)==r['parent_native_sha256']
    parent=App.openDocument(str(pn));old={i['id']:i for i in leaves(parent.Root)}
    def hashes(path):
        with zipfile.ZipFile(path) as archive:
            tree=ET.fromstring(archive.read('Document.xml'))
            return {o.get('name'):hashlib.sha256(archive.read(prop.get('file'))).hexdigest()
                for o in tree.findall('./ObjectData/Object') for prop in o.findall('./Properties/Property[@name="Shape"]/Part') if prop.get('file')}
    previous,current=hashes(pn),hashes(native);compared=set();failures=[];fallback=[]
    for name,item in old.items():
        now=byid[name];t,angle=placement_errors(item['shape'].Placement,now['shape'].Placement)
        if t>=1e-6 or angle>=1e-8:failures.append(name+' frame')
        target=item['target'];dest=now['target']
        if target.Name in compared:continue
        compared.add(target.Name)
        if previous.get(target.Name) and previous.get(target.Name)==current.get(dest.Name):continue
        fallback.append(target.Name)
        missing=target.Shape.cut(dest.Shape).Volume;extra=dest.Shape.cut(target.Shape).Volume
        if max(abs(missing),abs(extra))>=1e-5:failures.append(dict(name=name,missing=missing,extra=extra))
    ck('2153 parent occurrences preserve full material and frames',len(old)==2153 and not failures,
       dict(unique_definitions=len(compared),fallback=fallback,failures=failures))
    def overlap_bounds(a,b):return all(getattr(a,k+'Min')<=getattr(b,k+'Max')+1e-7 and getattr(b,k+'Min')<=getattr(a,k+'Max')+1e-7 for k in ['X','Y','Z'])
    pairs=[];seen=set()
    for name in new:
        one=byid[name]['shape']
        for other,row in byid.items():
            key=tuple(sorted([name,other]))
            if name==other or key in seen or not overlap_bounds(one.BoundBox,row['shape'].BoundBox):continue
            seen.add(key);volume=one.common(row['shape']).Volume
            pairs.append(dict(a=name,b=other,overlap_mm3=volume,internal=other in new,passed=abs(volume)<1e-5))
            write(out/'material_progress.json',dict(completed=len(pairs),overlaps=[r for r in pairs if not r['passed']]))
    internal=[p for p in pairs if p['internal']]
    ck('new assembly has no internal material overlaps',all(p['passed'] for p in internal),[p for p in internal if not p['passed']])
    external=[p for p in pairs if not p['internal'] and not p['passed']]
    result=dict(component_checks_passed=all(c['passed'] for c in checks),
        installation_passed=all(p['passed'] for p in pairs),checks=checks,material_pairs=pairs,
        unresolved_external_interferences=external,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),
        standard_context_checked=False,scope='Development geometry only; source review, STEP, parameter trial, case revision and standard integration remain open.')
    write(out/'independent_checks.json',result)
    print('Component checks',result['component_checks_passed'],'checks',len(checks),'pairs',len(pairs),'external clashes',len(external),flush=True)
    assert result['component_checks_passed'],'Component study itself has failed checks; see report'
finally:
    runtime.close()
