"""Integrate the reviewed coupled station into the retained complete development hierarchy."""
import argparse, uuid
from pathlib import Path
from control_rebuild_io_v2 import App, H, ROOT, Saved, pose, read, write, sha
from lib.cad_build import metadata
p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
planpath=a.plan.resolve();plan=read(planpath);assert plan['passed']
assert all(sha(ROOT/f)==h for f,h in plan['input_hashes'].items())
parent,prototype=[Saved(ROOT/plan[k]) for k in ['parent','prototype']]
assert read(parent.folder/'qualification.json')['local_static_checks_passed']
assert read(H/'driver_support_outline_study/study_receipt.json')['source_disposition']=='reviewed_local_approximation'
assert read(prototype.folder/'visual01/visual_review.json')['disposition']=='reviewed_local_approximation'
inputs=[Path(__file__),H/'control_rebuild_io_v2.py',H.parents[1]/'lib/cad_build.py',planpath]
hashes=plan['input_hashes']|{str(f.relative_to(ROOT)):sha(f) for f in inputs}
# Capture the eight current route wires and ten saved seat construction sections.
guide_records={};guide_shapes={}
for native,names in [(prototype.native,None),(ROOT/plan['guide_native'],[g['name'] for g in read((ROOT/plan['guide_native']).parent/'report.json')['guides']])]:
    doc=App.openDocument(str(native))
    try:
        objects=doc.NonphysicalCenterlines.Group if names is None else [doc.getObject(n) for n in names]
        for obj in objects:
            assert hasattr(obj,'Shape') and not obj.Shape.Solids
            name=obj.Name if names is None else 'Seat'+obj.Name
            props={k:getattr(obj,k) for k in obj.PropertiesList if obj.getGroupOfProperty(k)=='Reconstruction'}
            props.update(Physical=False,SourceNative=str(native.relative_to(ROOT)),SourceObject=obj.Name)
            guide_shapes[name]=obj.Shape.copy()
            guide_records[name]=dict(source_native=str(native.relative_to(ROOT)),source_native_sha256=sha(native),source_object=obj.Name,
                group='StationRouteCenterlines' if names is None else 'SeatConstructionSections',properties=props,frame=list(obj.Shape.Placement.toMatrix().A))
    finally:App.closeDocument(doc.Name)
assert len(guide_records)==18
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
doc=App.openDocument(str(parent.native));added={'Definitions':[]}
for key in plan['new_definitions']:
    assert doc.getObject(key) is None
    body=doc.addObject('PartDesign::Body',key);doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedStationPart').Shape=prototype.definition(key)
    metadata(body,**plan['metadata'][key]);added['Definitions'].append(key)
for key in plan['changed_definitions']:
    body=doc.getObject(key);body.Tip.Shape=prototype.definition(key);metadata(body,**plan['metadata'][key])
for name,spec in plan['new_assembly_specs'].items():
    assert doc.getObject(name) is None
    owner=doc.getObject(spec['owner']);group=doc.addObject('App::Part',name);owner.addObject(group)
    group.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:coupled-station-integration:'+name))
    group.Placement=owner.getGlobalPlacement().inverse().multiply(pose(spec['frame']))
    metadata(group,Coverage='reviewed_local_approximation',Subsystem='BowStructure' if name.startswith('Bow') else 'DriverStation')
    added.setdefault(owner.Name,[]).append(name)
for name,spec in plan['expected_new_occurrences'].items():
    assert doc.getObject(name) is None
    owner=doc.getObject(spec['owners'][-1]);obj=doc.addObject('App::Link',name);owner.addObject(obj);obj.setLink(doc.getObject(spec['definition']))
    obj.LinkPlacement=owner.getGlobalPlacement().inverse().multiply(pose(spec['frame']))
    metadata(obj,OccurrenceId=name,Coverage='reviewed_local_approximation',Subsystem='BowStructure' if name.startswith(('hull_','upper_')) else 'DriverStation',SourceRecords=plan['metadata'].get(spec['definition'],prototype.manifest['definitions'][spec['definition']]['properties']).get('SourceRecords',[]))
    added.setdefault(owner.Name,[]).append(name)
for name,spec in plan['expected_changed_occurrences'].items():
    owner=doc.getObject(spec['owners'][-1]);obj=doc.getObject(parent.rows[name]['object'])
    obj.LinkPlacement=owner.getGlobalPlacement().inverse().multiply(pose(spec['frame']))
for group in ['StationRouteCenterlines','SeatConstructionSections']:
    assert doc.getObject(group) is None
    g=doc.addObject('App::DocumentObjectGroup',group);metadata(g,Physical=False,Purpose='Retained construction geometry; excluded from physical hierarchy and BOM.')
    for name,v in guide_records.items():
        if v['group']!=group:continue
        assert doc.getObject(name) is None
        obj=doc.addObject('PartDesign::Feature',name);obj.Shape=guide_shapes[name];g.addObject(obj);obj.Visibility=False;metadata(obj,**v['properties'])
doc.Root.Label='Powertrain development — coupled bow, driver controls and supported seat'
doc.Root.RegistrationStatus='Reviewed local static approximation: connected driver/seat supports, complete source-length rods, relocated floor mounts and bow panels. Shaft identities, support outline, seat curves, M772 delayed set and handle datum remain conditional. Foot/reverse and unidentified seat adjustment fittings remain unfinished. No historical pose, motion or service qualification.'
doc.Definitions.Visibility=False;doc.recompute();native=out/'PowertrainControlRebuild.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
assert all(sha(ROOT/f)==h for f,h in hashes.items())
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(parent.native.relative_to(ROOT)),source_native_sha256=sha(parent.native),parent_native=str(parent.native.relative_to(ROOT)),parent_native_sha256=sha(parent.native),
    prototype=str(prototype.folder.relative_to(ROOT)),prototype_native_sha256=sha(prototype.native),plan=str(planpath.relative_to(ROOT)),plan_sha256=sha(planpath),input_hashes=hashes,details=prototype.report['details'],
    **{k:plan[k] for k in ['new_occurrences','new_definitions','changed_definitions','expected_new_occurrences','expected_changed_occurrences','new_assembly_specs','standard_replaced_occurrences','new_tank_parts','new_development_context']},
    added_children=added,nonphysical_guides=guide_records,expected_physical_occurrences=len(parent.rows)+len(plan['new_occurrences']),expected_definition_count=len(parent.manifest['definitions'])+len(plan['new_definitions']),expected_assembly_count=len(parent.manifest['assemblies'])+len(plan['new_assembly_specs']),geometry_integrated=True,standard_assembly_modified=False,historical_geometry_qualified=False,installation_qualified=False,packet_complete=False))
print('Saved coupled station integration; independent verification pending.',flush=True)
