"""Independently verify the saved merged hierarchy against each source native.

Exact BRep matches or verified material equivalence plus composed frames transfer local checks;
this explicitly does not qualify the unresolved global floor/manifold interfaces.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import xml.etree.ElementTree as ET
import zipfile

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

def shapes(path):
    with zipfile.ZipFile(path) as z:
        t=ET.fromstring(z.read('Document.xml'))
        return {o.get('name'):hashlib.sha256(z.read(part.get('file'))).hexdigest()
                for o in t.findall('./ObjectData/Object')
                for part in o.findall('./Properties/Property[@name="Shape"]/Part') if part.get('file')}

try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves,COLORS
    from detail_render import shaded_detail
    V=App.Vector;r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']
    source_reports={}
    for key,ref in r['parent_reports'].items():
        path=ROOT/ref['path'];assert sha(path)==ref['sha256']
        source_reports[key]=read(path)
    water_axis_z=-source_reports['drive']['controls']['pump_axis_drop']
    doc=App.openDocument(str(native));items=leaves(doc.Root);current={row['id']:row for row in items}
    blobs=shapes(native);engine=doc.TankLibertyEngine.getGlobalPlacement();checks=[];rows=[]
    def ck(name,passed,**detail):
        checks.append(dict(name=name,passed=bool(passed),**detail));print(name,bool(passed),flush=True)
        write(out/'check_progress.json',dict(checks=checks,occurrences=rows))
    ck('2393 unique physical occurrences',len(items)==len(current)==2393)
    ck('water axis follows independently bound lower-drive dimension',
       abs(doc.EngineWaterPump.Placement.Base.z-water_axis_z)<1e-7,
       expected_engine_z_mm=water_axis_z,actual_engine_z_mm=doc.EngineWaterPump.Placement.Base.z)
    equivalence={}
    def compare(name,source_shape,source_blob,expected,scope):
        item=current[name];actual=item['shape'].Placement
        err=max((actual.multVec(v)-expected.multVec(v)).Length for v in [V(),V(13,0,0),V(0,17,5)])
        same=blobs[item['target'].Name]==source_blob
        same_material=same;pair=(source_blob,blobs[item['target'].Name])
        if not same:
            if pair not in equivalence:
                one,two=source_shape.copy(),item['target'].Shape.copy()
                ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(1e-4,max(1e-7,ta+tb))
                missing,added=one.cut(two),two.cut(one)
                fm,fa=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
                record=dict(source_sha256=pair[0],candidate_sha256=pair[1],definition=item['target'].Name,
                    missing_mm3=missing.Volume,added_mm3=added.Volume,fuzzy_missing_faces=fm,fuzzy_added_faces=fa,
                    source_tolerance_mm=ta,candidate_tolerance_mm=tb,
                    passed=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and
                    abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and
                    ta<=1e-4 and tb<=max(ta,1e-7)+1e-10)
                equivalence[pair]=record
                write(out/'material_equivalence_progress.json',list(equivalence.values()))
                print('material equivalence',item['target'].Name,record['passed'],flush=True)
            same_material=equivalence[pair]['passed']
        rows.append(dict(name=name,scope=scope,exact_definition_brep=same,frame_error_mm=err,
                         material_equivalent=same_material,passed=same_material and err<1e-7))
    for key in ['water','drive','oil']:
        ref=r['parent_natives'][key];path=ROOT/ref['path'];assert sha(path)==ref['sha256']
        source=App.openDocument(str(path));source_blobs=shapes(path)
        try:
            if key=='oil':
                pose=json.loads(source.EngineOilPump.ProposedEnginePlacementJSON)
                basis=engine.multiply(App.Placement(V(pose['x'],pose['y'],pose['z']),App.Rotation()))
                for row in r['oil_occurrences']:
                    link=source.getObject(row['name']);old=link.LinkedObject
                    expected=basis.multiply(source.getObject(row['assembly']).getGlobalPlacement()).multiply(link.LinkPlacement).multiply(old.Shape.Placement)
                    compare(row['name'],old.Shape,source_blobs[old.Name],expected,'oil')
                    now=doc.getObject(row['name']);parent=doc.getObject(row['assembly'])
                    assert now in parent.Group and now.LinkedObject==doc.getObject(r['definitions'][row['key']])
                    for prop in ['DefinitionKey','SourceRecords','SourcePartMark']:
                        assert getattr(now.LinkedObject,prop)==getattr(old,prop),(row['name'],prop)
            else:
                inverse=source.TankLibertyEngine.getGlobalPlacement().inverse()
                source_items={row['id']:row for row in leaves(source.Root)}
                if key=='water':
                    preserved={name for name in source_items if name!='EngineCase_lower' and
                               not name.startswith(('EngineWaterPump_','EngineLowerDrive_'))}
                    ck('unchanged parent coverage derived from source native',
                       preserved==set(r['preserved_parent_ids']) and len(preserved)==2152)
                    source_engine=source.TankLibertyEngine.getGlobalPlacement()
                    ck('inherited engine registration preserved',
                       max((engine.multVec(v)-source_engine.multVec(v)).Length
                           for v in [V(),V(13,0,0),V(0,17,5)])<1e-7)
                    for name in sorted(preserved):
                        row=source_items[name]
                        compare(name,row['target'].Shape,source_blobs[row['target'].Name],row['shape'].Placement,'unchanged_parent')
                for name,row in source_items.items():
                    if not name.startswith('EngineWaterPump_' if key=='water' else 'EngineLowerDrive_'):continue
                    expected=inverse.multiply(row['shape'].Placement)
                    if key=='water':
                        old_z=source.EngineWaterPump.Placement.Base.z
                        expected=App.Placement(V(0,0,water_axis_z-old_z),App.Rotation()).multiply(expected)
                    expected=engine.multiply(expected)
                    compare(name,row['target'].Shape,source_blobs[row['target'].Name],expected,key)
        finally:App.closeDocument(source.Name)
    receiver_report=ROOT/r['receiver_report'];rr=read(receiver_report)
    ref=receiver_report.parent/rr['native_file'];assert sha(ref)==r['receiver_native_sha256']
    receiver=App.openDocument(str(ref));old=receiver.Def_EngineCase_lower
    compare('EngineCase_lower',old.Shape,shapes(ref)[old.Name],engine.multiply(old.Shape.Placement),'receiver')
    App.closeDocument(receiver.Name)
    ck('all saved definitions and composed frames match sources',
       len(rows)==len({row['name'] for row in rows})==2393 and all(row['passed'] for row in rows),
       counts={k:sum(row['scope']==k for row in rows) for k in ['unchanged_parent','water','drive','oil','receiver']},
       failures=[row for row in rows if not row['passed']])
    ck('pump parentage and identities preserved',doc.EngineOilPump in doc.TankLibertyEngine.Group and
       doc.EngineWaterPump in doc.TankLibertyEngine.Group and len(r['definitions'])==40)
    local=read(receiver_report.parent/'independent_checks.json')
    ck('local mechanical evidence bound to exact receiver',local['local_mechanical_passed'] and
       local['native_sha256']==rr['native_sha256'] and
       sha(receiver_report.parent/'independent_checks.json')==r['input_hashes'][str((receiver_report.parent/'independent_checks.json').relative_to(ROOT))])
    result=dict(passed=all(row['passed'] for row in checks),native_sha256=sha(native),checker_sha256=sha(Path(__file__)),
        checks=checks,occurrences=rows,physical_occurrences=len(current),material_equivalence=list(equivalence.values()),
        local_mechanical_reuse=dict(receiver_checks=len(local['checks']),case_pairs=len(local['material_pairs']),
            cross_component_pairs=len(local['cross_component_pairs']),basis='Exact BReps or strict bidirectional material equivalence, plus every composed frame verified in this hierarchy'),
        standard_assembly_modified=False,installation_qualified=False,hydraulic_circuit_qualified=False,
        inherited_floor_envelope_gap_mm=local['inherited_floor_envelope_gap_mm'])
    write(out/'independent_checks.json',result)
    if a.render:
        inverse=engine.inverse();display={};roles={}
        for name,row in current.items():
            role=('PumpOil' if name.startswith('EngineOilPump_') else 'PumpWater' if name.startswith('EngineWaterPump_')
                  else 'PumpDrive' if name.startswith('EngineLowerDrive_') else 'PumpCase' if name=='EngineCase_lower'
                  else 'PumpFloor' if name=='hull_floor_5' else None)
            if role is None:continue
            s=row['shape'].copy();s.Placement=inverse.multiply(s.Placement);display[name]=s;roles[name]=role
        COLORS.update(PumpCase=(.60,.65,.63),PumpOil=(.80,.66,.42),PumpWater=(.42,.66,.76),
                      PumpDrive=(.59,.61,.67),PumpFloor=(.77,.36,.35))
        for name,direction in [('isometric',(.7,-1,.6)),('section',(0,-1,0)),('floor_context',(0,-1,0))]:
            items=[];cut=Part.makeBox(480,145,530,V(1010,0,-420))
            for ident,s in display.items():
                if roles[ident]=='PumpFloor' and name!='floor_context':continue
                if name=='isometric':
                    shown=s.common(Part.makeBox(330,220,415,V(1060,-110,-400))) if roles[ident]=='PumpCase' else s.copy()
                else:shown=s.common(cut)
                if not shown.Solids:continue
                items.append(dict(shape=shown,target=SimpleNamespace(Shape=shown),definition=ident,
                    system=roles[ident],representation='assembly'))
            shaded_detail(items,out/(name+'.svg'),direction,'Saved coupled pump hierarchy | '+name,.08)
        write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
            images={f.name:sha(f) for f in out.glob('*.png')},source='Actual2393-occurrence saved native; only local affected components displayed',
            display_only_sections=True,installation_qualified=False))
    assert result['passed']
finally:
    runtime.close()
