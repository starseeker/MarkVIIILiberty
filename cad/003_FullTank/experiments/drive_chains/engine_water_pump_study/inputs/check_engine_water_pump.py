"""Saved-native pump interfaces, source dimensions, rotation and material checks."""
import argparse
import hashlib
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'engine_water_pump_study')
p.add_argument('--preservation',action='store_true');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    command=[sys.executable,__file__,'--candidate',str(out),'--worker']
    if a.preservation:command.append('--preservation')
    with (out/'independent_check.log').open('w') as log:
        sys.exit(subprocess.run(command,env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves
    from lib.worker import placement_errors
    V=App.Vector;X,Y,Z=V(1,0,0),V(0,1,0),V(0,0,1)
    r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};checks=[]
    c=r['controls'];d=r['datums'];inverse=doc.EngineWaterPump.getGlobalPlacement().inverse()
    def ck(name,passed,detail=None):
        checks.append(dict(name=name,passed=bool(passed),detail=detail))
        write(out/'check_progress.json',dict(completed=len(checks),failures=[t for t in checks if not t['passed']]))
        print(name,bool(passed),flush=True)
    def local(ident):
        shape=byid[ident]['shape'].copy();shape.Placement=inverse.multiply(shape.Placement);return shape
    def part(suffix):return local('EngineWaterPump_'+suffix)
    ck('unique physical occurrences match parent plus pump',len(items)==len(byid)==2170+len(r['new_ids']))
    ck('all new saved parts are valid single solids',all(byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1 for n in r['new_ids']))
    hierarchy=[]
    for row in r['occurrences']:
        item=byid[row['name']];obj=item['object'];target=item['target']
        hierarchy.append(obj.TypeId=='App::Link' and obj in doc.getObject(row['assembly']).Group
            and target.Placement.Base.Length<1e-8 and abs(target.Placement.Rotation.Angle)<1e-8
            and target.DefinitionId=='engine_water_pump_'+row['key'])
    ck('all pump links have correct parents and identity definitions',all(hierarchy))
    shaft=part('GearedShaft');imp=part('Impeller');body=part('BodyCasting');cover=part('InletCover');retainer=part('BearingRetainer')
    bearing=Part.makeCompound([local(n) for n in r['new_ids'] if 'BearingBall' in n or 'bearing_' in n])
    def cylinders(shape):return [f.Surface for f in shape.Faces if isinstance(f.Surface,Part.Cylinder)]
    inner=part('bearing_inner');outer=part('bearing_outer')
    ck('bearing printed bore 0.6693 inch',any(abs(s.Radius-.6693*25.4/2)<1e-6 for s in cylinders(inner)))
    ck('bearing printed outside 1.8504 inch',any(abs(s.Radius-1.8504*25.4/2)<1e-6 for s in cylinders(outer)))
    ck('bearing printed width 0.5512 inch',abs(outer.BoundBox.XLength-.5512*25.4)<1e-6,outer.BoundBox.XLength)
    ck('one geared shaft and two packing boxes',len([n for n in r['new_ids'] if n.endswith('GearedShaft')])==1 and len([n for n in r['new_ids'] if n.endswith('Packing')])==2)
    key=part('ImpellerKey');ck('printed key length and width',abs(key.BoundBox.XLength-15.875)<1e-6 and abs(key.BoundBox.ZLength-4.7625)<1e-6)
    ck('bearing shoulder meets inner race',shaft.distToShape(inner)[0]<1e-5)
    ck('bearing retainer has axial shoulder allowance',0<=retainer.distToShape(outer)[0]<=.127)
    # Nominal shaft centerline passes through all stationary parts. This detects
    # an accidentally capped packing, retainer, pump body or inlet cover.
    for name,shape,lo,hi in [('retainer',retainer,41,124),('body',body,108,147),('cover',cover,180,206)]:
        probe=Part.makeCylinder(3,hi-lo,V(lo,0,0),X)
        ck(name+' axial passage open',abs(shape.common(probe).Volume)<1e-5)
    ck('impeller inside open centrifugal chamber',abs(imp.common(body).Volume)<1e-5)
    ck('inlet printed 2 inch outer diameter',any(abs(s.Radius-25.4)<1e-6 and abs(s.Axis.z)>.99 for s in cylinders(cover)))
    # Check complete inlet passage and two outlet bores against the actual solids.
    endx=c['inlet_neck_x']+c['inlet_bend_radius'];bend=c['inlet_bend_radius']
    probes=[]
    for i in range(9):
        angle=i*math.pi/16;pos=V(c['inlet_neck_x']+bend*math.sin(angle),0,-bend+bend*math.cos(angle))
        probes.append(abs(cover.common(Part.makeSphere(4,pos)).Volume)<1e-5)
    ck('curved inlet centerline is open',all(probes))
    wall_radius=c['inlet_od']/2-c['inlet_wall']/2
    wall_z=-bend-c['inlet_stub_length']+.2
    ck('inlet end wall remains continuous around full circumference',all(cover.isInside(
        V(endx+wall_radius*math.cos(i*math.pi/32),wall_radius*math.sin(i*math.pi/32),wall_z),1e-7,False) for i in range(64)))
    for sign in [-1,1]:
        probe=Part.makeCylinder(5,c['outlet_tip_y']-35,V(c['scroll_center_x'],sign*35,sign*c['outlet_offset_z']),Y*sign)
        ck('outlet open '+str(sign),abs(body.common(probe).Volume)<1e-5)
    ck('eight source stud sets',all(len([row for row in r['occurrences'] if row['key']==key_])==8 for key_ in ['cover_stud','cover_nut','cover_washer','cover_cotter']))
    stud=doc.getObject(r['definitions']['cover_stud']).Shape
    ck('stud printed length 1-3/16 inch',abs(stud.BoundBox.XLength-30.1625)<1e-6)
    # Actual installed material against all development context, without exclusions.
    boxes={n:i['shape'].BoundBox for n,i in byid.items()};pairs=[];seen=set()
    def intersects(a,b):return all(getattr(a,k+'Min')<=getattr(b,k+'Max')+1e-7 and getattr(b,k+'Min')<=getattr(a,k+'Max')+1e-7 for k in ['X','Y','Z'])
    for n in r['new_ids']:
        for other,row in byid.items():
            key_=tuple(sorted([n,other]))
            if n==other or key_ in seen or not intersects(boxes[n],boxes[other]):continue
            seen.add(key_);volume=abs(byid[n]['shape'].common(row['shape']).Volume)
            pairs.append(dict(a=n,b=other,overlap_mm3=volume,passed=volume<1e-5))
            if len(pairs)%25==0:
                write(out/'material_progress.json',dict(checked=len(pairs),failed=[t for t in pairs if not t['passed']]))
                print('Material pairs',len(pairs),flush=True)
    ck('all pump and context pairs clear',all(t['passed'] for t in pairs),[t for t in pairs if not t['passed']])
    # Integral vertical driver meshes with the newly saved horizontal shaft.
    driver=local('EngineLowerDrive_IntegralDriver');samples=[]
    for i in range(9):
        theta=i*360/21/8;one,two=driver.copy(),shaft.copy()
        one.rotate(V(),Z,theta);two.rotate(V(),X,-theta)
        volume=abs(one.common(two).Volume);gap=one.distToShape(two)[0]
        samples.append(dict(driver_deg=theta,pump_deg=-theta,overlap_mm3=volume,gap_mm=gap,passed=volume<1e-5 and gap>1e-6))
        print('Mesh sample',i,samples[-1]['passed'],flush=True)
    wrong=shaft.copy();wrong.rotate(V(),X,180/21);overlap=abs(wrong.common(driver).Volume)
    ck('actual pump mesh throughout tooth pitch',all(t['passed'] for t in samples),samples)
    ck('half-tooth phase negative control collides',overlap>10,overlap)
    rotor=Part.makeCompound([part(name) for name in ['GearedShaft','Impeller','ImpellerKey','ImpellerNut','ImpellerCotter']])
    stationary=Part.makeCompound([retainer,body,cover,part('FrontGland'),part('RearGland'),part('GlandSpring')])
    rotor_checks=[]
    for theta in range(0,360,45):
        shape=rotor.copy();shape.rotate(V(),X,theta);volume=abs(shape.common(stationary).Volume)
        rotor_checks.append(dict(angle_deg=theta,overlap_mm3=volume,passed=volume<1e-5))
    ck('complete keyed rotor clears stationary pump at eight angles',all(t['passed'] for t in rotor_checks),rotor_checks)
    if a.preservation:
        pn=ROOT/r['parent_native'];assert sha(pn)==r['parent_native_sha256']
        parent=App.openDocument(str(pn));old={i['id']:i for i in leaves(parent.Root)}
        def hashes(path):
            with zipfile.ZipFile(path) as z:
                tree=ET.fromstring(z.read('Document.xml'))
                return {o.get('name'):hashlib.sha256(z.read(v.get('file'))).hexdigest() for o in tree.findall('./ObjectData/Object') for v in o.findall('./Properties/Property[@name="Shape"]/Part') if v.get('file')}
        previous,current=hashes(pn),hashes(native);compared=set();failures=[];fallback=[]
        for n,item in old.items():
            now=byid[n];dt,angle=placement_errors(item['shape'].Placement,now['shape'].Placement)
            if dt>=1e-6 or angle>=1e-8:failures.append(n+' frame')
            target,dest=item['target'],now['target']
            if target.Name in compared:continue
            compared.add(target.Name)
            if previous.get(target.Name) and previous.get(target.Name)==current.get(dest.Name):continue
            fallback.append(target.Name);mv,av=abs(target.Shape.cut(dest.Shape).Volume),abs(dest.Shape.cut(target.Shape).Volume)
            if max(mv,av)>=1e-5:failures.append(dict(name=n,missing=mv,added=av))
        ck('all2170 parent materials and frames preserved',len(old)==2170 and not failures,dict(fallback=fallback,failures=failures))
    result=dict(passed=all(t['passed'] for t in checks),checks=checks,material_pairs=pairs,
        native_sha256=sha(native),checker_sha256=sha(Path(__file__)),parent_material_checked=a.preservation,
        standard_context_checked=False,case_mounting_qualified=False,historical_dimensions_qualified=False)
    write(out/'independent_checks.json',result)
    assert result['passed'],'Saved-pump checks failed; inspect receipts'
finally:
    runtime.close()
