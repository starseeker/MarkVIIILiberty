"""Inventory the reviewed station union, restoring metadata from original native packets."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import App, H, ROOT, Saved, read, write, sha
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
parent=Saved(H/'transmission_controls_study/driver_redo01/operating_integrated01')
prototype=Saved(H/'driver_support_outline_study/trial02')
new=sorted(set(prototype.rows)-set(parent.rows))
newdefs=sorted(set(prototype.manifest['definitions'])-set(parent.manifest['definitions']))
changed=sorted(set(prototype.report['changed_definitions'])&set(parent.manifest['definitions']))
assert len(new)==130 and len(newdefs)==54 and len(changed)==17
# Every use of a genuinely revised shared definition must appear in the reviewed union.
assert all(n in prototype.rows for n,v in parent.rows.items() if v['definition'] in changed)
comparisons=[]
for key,d in prototype.manifest['definitions'].items():
    if key not in parent.manifest['definitions'] or key in changed:continue
    old=parent.manifest['definitions'][key];exact=d['brep_sha256']==old['brep_sha256']
    result=dict(definition=key,exact_brep=exact,source_sha256=old['brep_sha256'],prototype_sha256=d['brep_sha256'])
    if exact:result['passed']=True
    else:
        one,two=parent.definition(key),prototype.definition(key)
        miss,extra=one.cut(two),two.cut(one)
        mv,av=[sum(abs(s.Volume) for s in v.Solids) for v in (miss,extra)]
        fuzzy=[len(one.cut(two,1e-4).Faces),len(two.cut(one,1e-4).Faces)]
        result.update(missing_mm3=mv,added_mm3=av,fuzzy_difference_faces=fuzzy,
            passed=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and
            one.Solids[0].isClosed() and two.Solids[0].isClosed() and mv<1e-5 and av<1e-5 and not any(fuzzy)
            and max(one.getTolerance(1),two.getTolerance(1))<=1e-4)
    comparisons.append(result);write(out/'material_progress.json',comparisons)
    print(key,result['passed'],flush=True)
assert all(r['passed'] for r in comparisons)
inputs=[Path(__file__),H/'control_rebuild_io_v2.py',parent.native,parent.folder/'report.json',parent.folder/'isolated/manifest.json',parent.folder/'qualification.json',prototype.native,prototype.folder/'report.json',prototype.folder/'isolated/manifest.json']
props={k:{} for k in newdefs+changed};origins={k:{} for k in props}
# Older packets supply only fields that later prototypes dropped; present fields win.
folders=[parent.folder,H/'bow_reconstruction_study/trial02',H/'driver_layout_study/trial01',H/'driver_seat_study/trial06',H/'driver_seat_support_study/trial01',H/'coupled_driver_station_study/trial02',prototype.folder]
for folder in folders:
    report=read(folder/'report.json');native=folder/report['native_file'];assert sha(native)==report['native_sha256']
    inputs += [native,folder/'report.json']
    doc=App.openDocument(str(native))
    try:
        for key in props:
            obj=doc.getObject(key)
            if obj is None and folder.name=='trial02' and folder.parent.name=='bow_reconstruction_study':
                obj=doc.getObject(key.replace('Def_BowLayout_','Candidate_'))
            if obj is None:continue
            for name in obj.PropertiesList:
                if obj.getGroupOfProperty(name)=='Reconstruction':
                    props[key][name]=getattr(obj,name);origins[key][name]=dict(native=str(native.relative_to(ROOT)),object=obj.Name)
    finally:App.closeDocument(doc.Name)
# All physical additions and revised parts carry an explicit confidence and update record.
assert all('ReconstructionStatus' in v and 'ParameterUpdate' in v for v in props.values()),[(k,list(v)) for k,v in props.items() if 'ReconstructionStatus' not in v or 'ParameterUpdate' not in v]
identity=list(App.Placement().toMatrix().A)
groups={}
def group(name,owner):groups[name]=dict(owner=owner,frame=identity)
group('BowStructureContext','Root');group('BowHullPanels','BowStructureContext');group('BowUpperEnclosures','BowStructureContext')
group('DriverSeatAssembly','DriverControlFoundation');group('DriverSeatStructure','DriverSeatAssembly');group('DriverSeatAttachments','DriverSeatAssembly');group('DriverSeatStaySupports','DriverSeatAssembly');group('DriverSeatFloorAngles','DriverSeatAssembly')
for side in ['Port','Starboard']:
    for end in ['Front','Rear']:group('DriverSeat'+side+end+'Support','DriverSeatStaySupports')
    group('DriverSeat'+side+'FloorMount','DriverSeatFloorAngles')
expected={}
for name in new:
    row=prototype.rows[name]
    if name.startswith('hull_'):owner='BowHullPanels'
    elif name.startswith('upper_'):owner='BowUpperEnclosures'
    elif any(x in name for x in ['Bearing','Clip']):owner='DriverSeatAttachments'
    elif any(x in name for x in ['Frame','Cushion','BackPadding','Nail']):owner='DriverSeatStructure'
    elif 'Stay' in name:owner=name.split('Stay')[0]+'Support'
    elif 'SupportAngle' in name or 'AngleFloor' in name:owner='DriverSeat'+('Starboard' if 'Starboard' in name else 'Port')+'FloorMount'
    else:raise ValueError(name)
    assert owner in groups
    owners=[owner]
    while owners[0]!='Root':
        n=owners[0];up=groups[n]['owner'] if n in groups else next(k for k,v in parent.manifest['assemblies'].items() if n in v['children']);owners.insert(0,up)
    expected[name]=dict(definition=row['definition'],frame=row['frame'],owners=owners)
frames={n:dict(definition=v['definition'],frame=v['frame'],owners=parent.rows[n]['owners']) for n,v in prototype.rows.items() if n in parent.rows and max(abs(x-y) for x,y in zip(v['frame'],parent.rows[n]['frame']))>1e-7}
for n in set(parent.rows)&set(prototype.rows):assert parent.rows[n]['definition']==prototype.rows[n]['definition']
standard=H/'transmission_brake_front_study/trial01/standard_context_manifest.json';sm=read(standard);inputs.append(standard)
standardnames={v['name'] for v in sm['occurrences'] if v['representation']=='assembly'}
replacements=sorted((set(parent.rows)|set(new))&standardnames)
guides=H/'driver_seat_study/trial06/surface_records/SeatBackSectionGuides.FCStd';gr=guides.parent/'report.json';assert sha(guides)==read(gr)['nonphysical_guides_native_sha256'];inputs += [guides,gr]
for file in [H/'driver_support_outline_study/study_receipt.json',H/'coupled_driver_station_study/study_receipt.json',H/'seat_adjustment_study/evidence_receipt.json']:inputs.append(file)
write(out/'plan.json',dict(parent=str(parent.folder.relative_to(ROOT)),prototype=str(prototype.folder.relative_to(ROOT)),new_occurrences=new,new_definitions=newdefs,changed_definitions=changed,
    expected_new_occurrences=expected,expected_changed_occurrences=frames,new_assembly_specs=groups,metadata=props,metadata_origins=origins,
    inherited_prototype_material=comparisons,guide_native=str(guides.relative_to(ROOT)),standard_replaced_occurrences=replacements,
    new_tank_parts=[n for n in new if n not in standardnames],new_development_context=[n for n in new if n in standardnames],
    input_hashes={str(f.relative_to(ROOT)):sha(f) for f in inputs},passed=True))
print('PLAN',len(new),'additions',len(newdefs),'new definitions',len(changed),'revisions',len(frames),'moved occurrences',len(groups),'groups',flush=True)
