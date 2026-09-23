"""Independent native receiver, material, neighbor and continuous path checks."""
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
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=HERE/'engine_lower_drive_installation')
p.add_argument('--local-only',action='store_true');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    cmd=[sys.executable,__file__,'--candidate',str(out),'--worker']
    if a.local_only:cmd.append('--local-only')
    with (out/'independent_check.log').open('w') as log:
        sys.exit(subprocess.run(cmd,env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves
    from lib.worker import placement_errors,check_build
    V=App.Vector;X,Z=V(1,0,0),V(0,0,1)
    r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};checks=[]
    def ck(name,passed,detail=None):
        checks.append(dict(name=name,passed=bool(passed),detail=detail))
        write(out/'check_progress.json',dict(completed=len(checks),last=name,failures=[x for x in checks if not x['passed']]))
        print(name, bool(passed), flush=True)
    def zero(name,shape):
        v=abs(shape.Volume);ck(name,v<1e-5,v)
    ck('2170 unique physical occurrences',len(items)==len(byid)==2170)
    case=byid['EngineCase_lower']['target'].Shape
    ck('one valid integral casing',case.isValid() and len(case.Solids)==1)
    origin=V(*r['engine_origin']);apex=r['main_apex'];c=r['receiver_controls'];uc=r['controls']
    middle=r['datums']['mid_z'];hlo,hhi=r['datums']['housing_span']
    # Actual cylindrical native surfaces, and material surrounding the receiver.
    surfaces=[f.Surface for f in case.Faces if isinstance(f.Surface,Part.Cylinder)]
    vertical=[s for s in surfaces if abs(s.Axis.z)>.999999 and math.hypot(s.Center.x-apex,s.Center.y)<1e-5]
    expected_radius=uc['housing_radius']+c['lug_radial_clearance']
    ck('cylindrical receiver at driver axis',any(abs(s.Radius-expected_radius)<1e-6 for s in vertical))
    stations=[hlo+c['lug_end_inset']+1,middle,hhi-c['lug_end_inset']-1]
    witnesses=[]
    for z in stations:
        for i in range(16):
            if z==middle and i in [0,8]:continue  # retaining-screw drilling
            angle=2*math.pi*i/16;rad=uc['housing_radius']+1.5
            witnesses.append(case.isInside(V(apex+rad*math.cos(angle),rad*math.sin(angle),z),1e-7,False))
    ck('lug has circumferential supporting material at three heights',all(witnesses),dict(samples=len(witnesses)))
    # Entire removable set includes the two complete five-piece clamp sets.
    moving=[n for n in r['unit_ids'] if n!='EngineLowerDrive_HousingRetainingScrew']
    ck('16 constituents withdraw together',len(moving)==16)
    local=[]
    for n in moving:
        s=byid[n]['shape'].copy();s.translate(-origin);local.append(s)
    unit=Part.makeCompound(local);b=unit.BoundBox
    enclosing=Part.makeCylinder(uc['housing_radius'],b.ZLength+2,V(apex,0,b.ZMin-1),Z)
    zero('whole removable unit lies in cylindrical passage envelope',unit.cut(enclosing))
    travel=b.ZMax-case.BoundBox.ZMin+1
    swept=Part.makeCylinder(uc['housing_radius'],b.ZLength+travel,V(apex,0,b.ZMin-travel),Z)
    zero('continuous downward envelope clears actual casing',swept.common(case))
    lowered=unit.copy();lowered.translate(V(0,0,-travel))
    ck('withdrawn entire unit lies below casing',lowered.BoundBox.ZMax<case.BoundBox.ZMin,
       dict(travel_mm=travel,unit_top_mm=lowered.BoundBox.ZMax,case_bottom_mm=case.BoundBox.ZMin))
    # Source oil entries sit above the lug and receive drainage from above.
    # Check a connected radial-then-upward route, not an assumed 12mm radial
    # drill through the external rear wall. The recess is real saved material.
    oil_z=r['datums']['bearing_span'][1]-uc['dowel_end_offset']
    for sign in [-1,1]:
        route=Part.makeCylinder(uc['oil_port_diameter']/2,2.75,V(apex+sign*(uc['housing_radius']-1),0,oil_z),V(sign,0,0))
        upward=Part.makeCylinder(uc['oil_port_diameter']/2,c['bay_top_z']-.5-oil_z+uc['oil_port_diameter']/2,
            V(apex+sign*(uc['housing_radius']+1.75),0,oil_z-uc['oil_port_diameter']/2),Z)
        zero('oil entry radial route remains exposed '+str(sign),route.common(case))
        zero('oil entry receives drainage from above '+str(sign),upward.common(case))
    seat=apex+r['datums']['retaining_screw_span'][1]
    ck('retaining screw has cast head-seat material',all(case.isInside(V(seat-.1,y,middle+z),1e-7,False)
       for y,z in [(8,0),(-8,0),(0,8),(0,-8)]))
    zero('retaining screw clearance bore is open',case.common(Part.makeCylinder(uc['retaining_screw_diameter']/2,
        seat-apex-44,V(apex+44,0,middle),X)))
    ox,oz=c['oil_center_x'],c['oil_mount_z'];rim=(c['oil_open_radius']+c['oil_flange_radius'])/2
    ck('continuous bottom oil-pump mounting rim',all(case.isInside(V(ox+rim*math.cos(i*math.pi/36),
       rim*math.sin(i*math.pi/36),oz+.5),1e-7,False) for i in range(72)))
    zero('bottom opening is unobstructed',case.common(Part.makeCylinder(c['oil_open_radius']-.1,
       c['oil_well_top_z']-oz,V(ox,0,oz-.01),Z)))
    ck('bottom opening retains offset from driver',abs(apex-ox)>20,abs(apex-ox))
    zero('rear water-pump passage is unobstructed',case.common(Part.makeCylinder(c['pump_open_radius']-.1,
       c['pump_mount_x']-c['pump_tunnel_front_x'],V(c['pump_tunnel_front_x'],0,-uc['pump_axis_drop']),X)))
    ck('rear opening leaves bottom rim stock',(-uc['pump_axis_drop']-c['pump_open_radius'])-oz>=8,
       (-uc['pump_axis_drop']-c['pump_open_radius'])-oz)
    # Independent, intentionally fixed boundary: reject edits leaking into the
    # bearing seats, top joint, general sump, mountings or other casing regions.
    allowed=Part.makeBox(285,220,225,V(1090,-110,-260))
    pn=ROOT/r['parent_native'];assert sha(pn)==r['parent_native_sha256']
    parent=App.openDocument(str(pn));old={i['id']:i for i in leaves(parent.Root)}
    before=old['EngineCase_lower']['target'].Shape
    missing,added=before.cut(case),case.cut(before)
    zero('no removed casing material outside receiving region',missing.cut(allowed))
    zero('no added casing material outside receiving region',added.cut(allowed))
    ck('receiver change actually adds and removes material',added.Volume>1000 and missing.Volume>1000,
       dict(added_mm3=added.Volume,removed_mm3=missing.Volume))
    def hashes(path):
        with zipfile.ZipFile(path) as archive:
            tree=ET.fromstring(archive.read('Document.xml'))
            return {obj.get('name'):hashlib.sha256(archive.read(prop.get('file'))).hexdigest()
                for obj in tree.findall('./ObjectData/Object') for prop in obj.findall('./Properties/Property[@name="Shape"]/Part') if prop.get('file')}
    previous,current=hashes(pn),hashes(native);compared=set();failures=[];fallback=[]
    for n,item in old.items():
        now=byid[n];t,angle=placement_errors(item['shape'].Placement,now['shape'].Placement)
        if t>=1e-6 or angle>=1e-8:failures.append(n+' frame')
        if n=='EngineCase_lower':continue
        target,dest=item['target'],now['target']
        if target.Name in compared:continue
        compared.add(target.Name)
        if previous.get(target.Name) and previous.get(target.Name)==current.get(dest.Name):continue
        fallback.append(target.Name)
        mv,av=abs(target.Shape.cut(dest.Shape).Volume),abs(dest.Shape.cut(target.Shape).Volume)
        if max(mv,av)>=1e-5:failures.append(dict(name=n,missing=mv,added=av))
    ck('2169 other occurrences retain material and all2170retain frames',len(old)==2170 and not failures,
       dict(definitions=len(compared),fallback=fallback,failures=failures))
    # Validate saved driver/case material against all affected physical context,
    # including standard tank components absent from the development document.
    candidates=dict(byid)
    if not a.local_only:
        standard=check_build(STAGE/'build');tank=App.openDocument(standard['build']['top_document'])
        for item in leaves(tank.Root):
            if item['representation']!='layout' and item['id'] not in byid:candidates['Standard_'+item['id']]=item
    def intersects(a,b):return all(getattr(a,k+'Min')<=getattr(b,k+'Max')+1e-7 and getattr(b,k+'Min')<=getattr(a,k+'Max')+1e-7 for k in ['X','Y','Z'])
    boxes={n:i['shape'].BoundBox for n,i in candidates.items()};pairs=[];seen=set()
    for n in ['EngineCase_lower']+r['unit_ids']:
        one=byid[n]['shape']
        for other,row in candidates.items():
            key=tuple(sorted([n,other]))
            if n==other or key in seen or not intersects(boxes[n],boxes[other]):continue
            seen.add(key);volume=abs(one.common(row['shape']).Volume)
            pairs.append(dict(a=n,b=other,overlap_mm3=volume,passed=volume<1e-5))
            if len(pairs)%25==0:
                print('Material pairs',len(pairs),flush=True)
                write(out/'material_progress.json',dict(checked=len(pairs),failed=[x for x in pairs if not x['passed']]))
    ck('affected material has no overlaps',all(p['passed'] for p in pairs),[p for p in pairs if not p['passed']])
    # The continuous casing envelope is proven above. Check actual parts against
    # the retained driving gear during separation; full pump assemblies are absent.
    gear=byid['EngineGear_DrivingBevel']['shape'].copy();gear.translate(-origin)
    phases=[]
    for dz in [0,.5,1,2,5,10,20,40,80,travel]:
        shifted=unit.copy();shifted.translate(V(0,0,-dz));v=abs(shifted.common(gear).Volume)
        phases.append(dict(down_mm=dz,overlap_mm3=v,passed=v<1e-5))
    ck('actual removable unit separates from retained main gear at sampled stations',all(x['passed'] for x in phases),phases)
    result=dict(passed=all(x['passed'] for x in checks),checks=checks,material_pairs=pairs,
        native_sha256=sha(native),checker_sha256=sha(Path(__file__)),standard_context_checked=not a.local_only,
        continuous_case_withdrawal_checked=True,main_gear_withdrawal_sampled=True,
        full_tank_service_path_checked=False,complete_pump_fit_checked=False,historical_dimensions_qualified=False)
    write(out/'independent_checks.json',result)
    print(len(checks),'checks;',len(pairs),'material pairs;',result['passed'],flush=True)
    assert result['passed']
finally:
    runtime.close()
