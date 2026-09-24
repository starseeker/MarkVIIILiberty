"""Inspect a saved receiver against independent pump/drive native constituents.

Local mechanical checks do not certify historical dimensions, the absent oil
manifold circuit, global engine elevation, or the complete vehicle installation.
"""
import argparse
import itertools
import math
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--render',action='store_true')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    cmd=[sys.executable,__file__,'--candidate',str(out),'--worker']
    if a.render:cmd.append('--render')
    with (out/'check.log').open('w') as log:
        sys.exit(subprocess.run(cmd,env=runtime.environment(out/'check_runtime'),
            stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    V=App.Vector;Z=V(0,0,1)
    r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));case=doc.Def_EngineCase_lower.Shape.copy();App.closeDocument(doc.Name)
    reports={key:read(ROOT/row['path']) for key,row in r['parent_reports'].items()}
    for key,row in r['parent_reports'].items():assert sha(ROOT/row['path'])==row['sha256']
    c=r['controls']['receiver'];oc=reports['oil']['controls'];uc=reports['drive']['controls']
    origin=V(*r['engine_origin']);apex=reports['drive']['main_apex']
    shapes={};roles={};checks=[];pairs=[]
    def ck(name,passed,**detail):
        checks.append(dict(name=name,passed=bool(passed),**detail))
        write(out/'check_progress.json',dict(checks=checks,material_pairs=pairs))
        print(name,bool(passed),flush=True)
    def zero(name,shape,**detail):
        ck(name,abs(shape.Volume)<1e-5,volume_mm3=shape.Volume,**detail)
    def moved(shape,pose):
        s=shape.copy();s.Placement=pose.multiply(s.Placement);return s
    oil_pose=App.Placement(V(oc['pump_axis_x'],0,oc['pump_mount_z']),App.Rotation())
    # Read actual source hierarchy/poses. Close each large parent before opening
    # the next; geometry retained here is only the affected local constituents.
    for key in ['drive','water','oil']:
        row=r['parent_natives'][key];path=ROOT/row['path'];assert sha(path)==row['sha256']
        parent=App.openDocument(str(path))
        if key=='oil':
            oil_defs={name:parent.getObject('Def_'+name).Shape.copy() for name in ['mount_gasket','lower_body','shaft']}
            for item in reports[key]['occurrences']:
                obj=parent.getObject(item['name']);pose=oil_pose.multiply(parent.getObject(item['assembly']).getGlobalPlacement()).multiply(obj.LinkPlacement)
                shapes[item['name']]=moved(obj.LinkedObject.Shape,pose);roles[item['name']]='ReceiverOil'
        else:
            inverse=parent.TankLibertyEngine.getGlobalPlacement().inverse()
            for item in leaves(parent.Root):
                ident=item['id']
                if key=='drive' and ident=='EngineCase_lower':old_case=item['target'].Shape.copy()
                if key=='drive' and ident.startswith('EngineLowerDrive_'):
                    shapes[ident]=moved(item['shape'],inverse);roles[ident]='ReceiverDrive'
                if key=='water' and ident.startswith('EngineWaterPump_'):
                    rise=reports[key]['pump_axis_z']*-1-uc['pump_axis_drop']
                    pose=App.Placement(V(0,0,rise),App.Rotation()).multiply(inverse)
                    shapes[ident]=moved(item['shape'],pose);roles[ident]='ReceiverWater'
                if key=='water' and ident=='hull_floor_5':floor=moved(item['shape'],inverse)
        App.closeDocument(parent.Name)
    ck('one valid case solid',case.isValid() and len(case.Solids)==1,
       max_tolerance_mm=case.getTolerance(1))
    ck('source constituent coverage',len(shapes)==146+77+17,
       oil=sum(v=='ReceiverOil' for v in roles.values()),water=sum(v=='ReceiverWater' for v in roles.values()),
       drive=sum(v=='ReceiverDrive' for v in roles.values()))
    for name,s in shapes.items():
        if not s.BoundBox.intersect(case.BoundBox):continue
        volume=abs(s.common(case).Volume)
        pairs.append(dict(name=name,overlap_mm3=volume,passed=volume<1e-5))
        write(out/'material_progress.json',pairs)
    ck('all local constituents clear case material',all(row['passed'] for row in pairs),
       pairs=len(pairs),failures=[row for row in pairs if not row['passed']])
    cross_pairs=[]
    for (name,s),(other,t) in itertools.combinations(shapes.items(),2):
        if roles[name]==roles[other] or not s.BoundBox.intersect(t.BoundBox):continue
        volume=abs(s.common(t).Volume)
        cross_pairs.append(dict(a=name,b=other,overlap_mm3=volume,passed=volume<1e-5))
        write(out/'cross_component_progress.json',cross_pairs)
    ck('all three local subassemblies mutually clear',all(row['passed'] for row in cross_pairs),
       pairs=len(cross_pairs),failures=[row for row in cross_pairs if not row['passed']])

    # Whole saved gasket footprint, translated just inside the receiving face.
    # This catches unsupported nose/rim regions, not just hand-picked stations.
    gasket=shapes['EngineOilPump_MountGasket'];land=gasket.copy()
    land.translate(V(0,0,gasket.BoundBox.ZLength+.05))
    zero('whole oil gasket has case bearing material',land.cut(case))
    face=gasket.BoundBox.ZMax;embed=reports['oil']['datums']['mounting']['case_engagement_mm']
    studnames=[row['name'] for row in reports['oil']['occurrences'] if row['key']=='mount_stud']
    stud_radius=oc['bolt_diameter']/2
    for name in studnames:
        s=shapes[name];x=(s.BoundBox.XMin+s.BoundBox.XMax)/2;y=(s.BoundBox.YMin+s.BoundBox.YMax)/2
        ring=Part.makeCylinder(stud_radius+2.75,embed-.5,V(x,y,face+.25),Z).cut(
             Part.makeCylinder(stud_radius+.25,embed+1,V(x,y,face-.1),Z))
        zero(name+' receiving sleeve',ring.cut(case))
        cap=Part.makeCylinder(stud_radius-.1,.2,V(x,y,s.BoundBox.ZMax+.6),Z)
        zero(name+' blind end material',cap.cut(case))
    # The final retaining-screw recess must not remove the water joint's full
    # bearing face or the four source-length stud sleeves.
    for row in reports['water']['occurrences']:
        s=shapes[row['name']]
        if row['key']=='shim':
            land=s.copy();land.translate(V(-s.BoundBox.XLength-.05,0,0))
            # The existing joint deliberately bridges .45 mm at the receiver
            # opening and .05 mm around the case stud holes. The prior native
            # and both trials lose the same40.94477mm3 there; those clearances
            # are not required backing. Check every other part of the footprint.
            wc=reports['water']['controls'];wface=c['pump_mount_x'];wz=-uc['pump_axis_drop']
            axis=V(1,0,0);allowances=[Part.makeCylinder(56.,2,V(wface-1,0,wz),axis)]
            for mountrow in reports['water']['occurrences']:
                if mountrow['key']!='mount_stud':continue
                b=shapes[mountrow['name']].BoundBox
                allowances.append(Part.makeCylinder(wc['mount_stud_diameter']/2+wc['case_mount_bore_clearance'],
                    2,V(wface-1,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2),axis))
            backing=land.cut(Part.makeCompound(allowances))
            zero('whole water shim bearing land outside defined clearances',backing.cut(case),
                 inner_opening_radius_mm=56.,stud_hole_radius_mm=4.8625)
            sd=r['datums']['screw_recess'];start=sd['span_x_mm'][0]
            bad=case.cut(Part.makeCylinder(sd['radius_mm'],wface-start+1,V(start,0,sd['axis_z_mm']),axis))
            loss=abs(backing.cut(bad).Volume)
            ck('negative control rejects recess breaking water joint',loss>.1,missing_required_land_mm3=loss)
        if row['key']=='mount_stud':
            b=s.BoundBox;y=(b.YMin+b.YMax)/2;z=(b.ZMin+b.ZMax)/2
            wc=reports['water']['controls'];rad=wc['mount_stud_diameter']/2
            wembed=wc['mount_stud_embed'];wface=c['pump_mount_x'];axis=V(1,0,0)
            sleeve=Part.makeCylinder(rad+2.5,wembed-.5,V(wface-wembed+.25,y,z),axis).cut(
                   Part.makeCylinder(rad+.25,wembed+1,V(wface-wembed-.1,y,z),axis))
            zero(row['name']+' case sleeve',sleeve.cut(case))
    # Derive port axes from the saved gasket's two small fluid openings. They
    # are independent of the new receiver's reported drilled-hole coordinates.
    ports={}
    for f in gasket.Faces:
        surf=f.Surface
        if isinstance(surf,Part.Cylinder) and abs(surf.Axis.z)>.999999 and abs(surf.Radius-4.75)<1e-7:
            ports[(round(surf.Center.x,7),round(surf.Center.y,7))]=surf.Radius
    ck('two actual gasket fluid ports',len(ports)==2,centers=list(ports))
    for index,(x,y) in enumerate(sorted(ports)):
        gauge=Part.makeCylinder(4.4,c['oil_well_top_z']-face+1,V(x,y,face-.5),Z)
        zero('oil socket '+str(index)+' open through receiver',gauge.common(case))
        sleeve=Part.makeCylinder(6.5,12,V(x,y,face+.1),Z).cut(Part.makeCylinder(4.65,13,V(x,y,face),Z))
        zero('oil socket '+str(index)+' has separating wall',sleeve.cut(case))

    # Preserve lower distribution support and source retaining-screw access.
    d=reports['drive']['datums'];radius=uc['housing_radius']+c['lug_radial_clearance']
    cylinders=[f.Surface for f in case.Faces if isinstance(f.Surface,Part.Cylinder)]
    ck('driver receiver cylinder at actual axis',any(abs(s.Axis.z)>.999999 and
       math.hypot(s.Center.x-apex,s.Center.y)<1e-6 and abs(s.Radius-radius)<1e-6 for s in cylinders))
    lo=d['housing_span'][0]+c['lug_lower_end_inset'];hi=d['housing_span'][1]-c['lug_end_inset']
    witnesses=[]
    for height in [lo+1,d['mid_z'],hi-1]:
        for i in range(16):
            if height==d['mid_z'] and i in [0,8]:continue
            t=i*math.pi/8;rad=uc['housing_radius']+1.5
            witnesses.append(case.isInside(V(apex+rad*math.cos(t),rad*math.sin(t),height),1e-7,False))
    ck('continuous supporting lug at three levels',all(witnesses),samples=len(witnesses))
    screw_seat=apex+d['retaining_screw_span'][1]
    ck('retaining screw head seat supported',all(case.isInside(V(screw_seat-.1,y,d['mid_z']+z),1e-7,False)
       for y,z in [(8,0),(-8,0),(0,8),(0,-8)]))
    moving=[s for name,s in shapes.items() if roles[name]=='ReceiverDrive' and name!='EngineLowerDrive_HousingRetainingScrew']
    unit=Part.makeCompound(moving);b=unit.BoundBox
    envelope=Part.makeCylinder(uc['housing_radius'],b.ZLength+2,V(apex,0,b.ZMin-1),Z)
    zero('sixteen-piece driver fits withdrawal envelope',unit.cut(envelope),count=len(moving))
    sweep=Part.makeCylinder(uc['housing_radius'],b.ZMax-case.BoundBox.ZMin+2,V(apex,0,case.BoundBox.ZMin-1),Z)
    zero('driver envelope clears case downward',sweep.common(case),scope='Casing only; pumps absent during withdrawal check')

    # Fixed regional boundary, independent of newly chosen receiver controls.
    # It encloses the revised bottom face/pads but excludes main bearing seats,
    # front mountings and the upper/lower case joint.
    allowed=Part.makeBox(285,220,245,V(1090,-110,-280))
    differences={}
    for label,shape in [('removed',old_case.cut(case)),('added',case.cut(old_case))]:
        differences[label]=shape.Volume
        if shape.Solids or shape.Faces:zero(label+' material confined to receiver region',shape.cut(allowed))
        else:ck(label+' material confined to receiver region',True,volume_mm3=0)
    ck('receiver revision adds and removes actual material',min(differences.values())>1000,**differences)
    oil_bottom=min(s.BoundBox.ZMin for name,s in shapes.items() if roles[name]=='ReceiverOil')
    floor_gap=oil_bottom-floor.BoundBox.ZMax
    # This is reported separately: local success must never hide a failed
    # full-vehicle installation at the inherited engine height.
    result=dict(local_mechanical_passed=all(row['passed'] for row in checks),native_sha256=sha(native),
        checker_sha256=sha(Path(__file__)),checks=checks,material_pairs=pairs,cross_component_pairs=cross_pairs,
        inherited_floor_envelope_gap_mm=floor_gap,global_floor_clear=floor_gap>=0,
        hydraulic_circuit_qualified=False,installation_qualified=False,standard_assembly_modified=False,
        source_documents_unchanged=all(sha(ROOT/row['path'])==row['sha256'] for row in r['parent_natives'].values()),
        limitations=['Missing manifold tubes and complete fluid paths remain unqualified.',
            'Case-only downward withdrawal is not a complete installed service-sequence check.',
            'Global engine elevation and full tank interfaces remain unresolved.'])
    write(out/'independent_checks.json',result)
    if a.render:
        COLORS.update(ReceiverCase=(.60,.65,.63),ReceiverOil=(.80,.66,.42),
                      ReceiverWater=(.42,.66,.76),ReceiverDrive=(.59,.61,.67))
        sources={**shapes,'Case':case};display_roles={**roles,'Case':'ReceiverCase'}
        for title,cut,direction in [
            ('section',Part.makeBox(480,145,530,V(1010,0,-420)),(0,-1,0)),
            ('isometric',Part.makeBox(330,220,415,V(1060,-110,-400)),(.7,-1,.6)),
            ('underside',Part.makeBox(300,220,140,V(1090,-110,-280)),(.4,-.6,-1))]:
            items=[]
            for name,s in sources.items():
                if title=='underside' and display_roles[name]!='ReceiverCase':continue
                if title=='isometric' and name!='Case':shown=s.copy()
                else:
                    if not s.BoundBox.intersect(cut.BoundBox):continue
                    shown=s.common(cut)
                if not shown.Solids:continue
                items.append(dict(shape=shown,target=SimpleNamespace(Shape=shown),definition=name,
                    system=display_roles[name],representation='assembly'))
            shaded_detail(items,out/(title+'.svg'),direction,'Coupled pump receiver trial | '+title,.08)
        write(out/'render_receipt.json',dict(native_sha256=sha(native),checker_sha256=sha(Path(__file__)),
            images={f.name:sha(f) for f in out.glob('*.png')},display_only_sections=True,installation_qualified=False))
    assert result['local_mechanical_passed']
finally:
    runtime.close()
