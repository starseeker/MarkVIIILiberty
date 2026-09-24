"""Install front brake ears, retained pivots and adjustment mechanisms."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--controls',type=Path,default=HERE/'transmission_brake_front_study/controls.json')
a=p.parse_args();parent=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithBrakeFront.FCStd';assert not native.exists()
prior=read(parent/'report.json');source=parent/prior['native_file'];m=read(parent/'isolated/manifest.json')
assert sha(source)==prior['native_sha256']==m['native_sha256']
assert read(parent/'independent_checks.json')['local_anchor_checks_passed']
assert read(parent/'definition_preservation_checks.json')['passed'] and read(parent/'exchange_checks.json')['passed']
packet=HERE/'transmission_brake_front_study/sources.json';sources=read(packet)
assert all(sha(ROOT/f)==digest for f,digest in sources['source_hashes'].items())
c=read(a.controls)['controls']
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_brake_front_parts import parts
from transmission_brake_front_layout import layout
bands={}
for role in ['low','track']:
    record=m['definitions']['Def_BrakeBand_'+role+'_band'];path=Path(record['brep_path'])
    assert sha(path)==record['brep_sha256'];s=Part.Shape();s.read(str(path));bands[role]=s
new,changed,d,curves=parts(c,prior,bands)
fresh,revised,groups=layout(d,c,m)
locked=[Path(__file__),a.controls.resolve(),packet,STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py',
        parent/'report.json',parent/'isolated/manifest.json',parent/'independent_checks.json',
        parent/'definition_preservation_checks.json',parent/'exchange_checks.json']
locked+=sorted({Path(module.__file__).resolve() for module in list(sys.modules.values())
    if getattr(module,'__file__',None) and Path(module.__file__).resolve().parent==HERE
    and str(module.__file__).endswith('.py')})
locked=sorted(set(locked));inputs={str(f.relative_to(ROOT)):sha(f) for f in locked}
doc=App.openDocument(str(source));defs={};records={}
specs=[('low_ear','MX48',['SNL:84:010']),('track_ear','MX46',['SNL:84:011']),
       ('pin','M336',['SNL:137:028']),('screw','M333',['SNL:205:007']),
       ('swivel','M331',['SNL:143:012']),('nut','M332',['SNL:130:007']),
       ('lever','M330',['SNL:118:024']),('spring','M335',['SNL:220:027'])]
for role,mark,rids in specs:
    body=doc.addObject('PartDesign::Body','Def_BrakeFront_'+role);doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedFrontBrakePart').Shape=new[role]
    ids=sorted({pid for rec in sources['source_records'] if rec['record_id'] in rids for pid in rec['part_ids']})
    assert ids,(role,rids)
    metadata(body,DefinitionKey='brake_front_'+role,SourcePartMark=mark,SourceRecords=rids,SurveyIds=ids,
        Representation='assembly',Coverage='reconstruction',ParameterUpdate='Regenerate with build_transmission_brake_front.py',
        ReconstructionStatus='Source identity, count and mechanism arrangement; estimated dimensions and hidden fork/swivel form. Nominal cylindrical thread surfaces. Source registration residuals and service sequence unresolved.')
    defs[role]=body;records[role]=rids
for role,key,rids in [('steel_rivet','Def_BrakeAnchor_steel_rivet',['SNL:191:011']),
                      ('long_copper_rivet','Def_BrakeAnchor_long_copper_rivet',['SNL:192:012']),
                      ('cotter','Def_BrakeLink_cotter',['SNL:137:029','SNL:141:014'])]:
    defs[role]=doc.getObject(key);records[role]=rids
for role,s in changed.items():
    body=doc.getObject('Def_BrakeBand_'+role+'_band');body.Tip.Shape=s
    metadata(body,FrontEarRevision='Front steel-rivet holes; covered lining-rivet tail pockets filled for longer grips through ear feet.',
        FrontEarUpdate='Regenerate with build_transmission_brake_front.py')
curve=doc.addObject('PartDesign::Feature','BrakeFrontSpringCenterline');doc.Definitions.addObject(curve)
curve.Shape=curves['spring_centerline'];curve.Visibility=False
metadata(curve,NonPhysical=True,Role='Estimated extended spring sweep path; ground end trimming is in the solid.',
    ParameterUpdate='Regenerate with build_transmission_brake_front.py')
added_children={'Definitions':['BrakeFrontSpringCenterline']};assemblies=[]
for name,g in groups.items():
    group=doc.addObject('App::Part',name);doc.getObject(g['parent']).addObject(group)
    group.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:front-brake:'+name));assemblies.append(name)
    added_children.setdefault(g['parent'],[]).append(name)
    # The group uses its owning brake/half-band frame unchanged.
    assert max(abs(x-y) for x,y in zip(group.getGlobalPlacement().toMatrix().A,g['frame']))<1e-7
expected={}
for name,row in fresh.items():
    role=row['role'];owner=doc.getObject(row['owners'][-1])
    obj=doc.addObject('App::Link',name);owner.addObject(obj);obj.setLink(defs[role])
    obj.LinkPlacement=App.Placement(App.Matrix(*row['local']))
    metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=records[role])
    expected[name]=dict(definition=defs[role].Name,frame=list(owner.getGlobalPlacement().multiply(obj.LinkPlacement).toMatrix().A),owners=row['owners'])
    added_children.setdefault(owner.Name,[]).append(name)
for name,row in revised.items():
    if row['role']!='long_copper_rivet':continue
    obj=doc.getObject(name);local=obj.LinkPlacement;obj.setLink(defs['long_copper_rivet']);obj.LinkPlacement=local
    metadata(obj,SourceRecords=records['long_copper_rivet'],FrontEarRevision='Longer source-listed stock through front ear foot.')
doc.Root.Label='Powertrain development — front brake adjustment mechanisms'
doc.Root.RegistrationStatus='Front ears and adjustment linkage reconstructed. Hidden joint dimensions estimated; stops, control rods, high-speed brakes and source station residuals remain pending.'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==prior['native_sha256'] and all(sha(ROOT/f)==digest for f,digest in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in locked:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
folder=out/'changed_shapes';folder.mkdir()
for name,s in {**{'Def_BrakeFront_'+k:v for k,v in new.items()},**{'Def_BrakeBand_'+k+'_band':v for k,v in changed.items()},'BrakeFrontSpringCenterline':curves['spring_centerline']}.items():s.exportBrep(str(folder/(name+'.brep')))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=inputs,controls=c,details=d,
    changed_definitions=sorted('Def_BrakeBand_'+k+'_band' for k in changed),new_definitions=sorted('Def_BrakeFront_'+k for k in new),
    nonphysical_features=['BrakeFrontSpringCenterline'],expected_new_occurrences=expected,
    expected_revised_occurrences={n:{k:v[k] for k in ['definition','frame','owners']} for n,v in revised.items()},
    assembly_revisions={},added_children=added_children,new_assemblies=assemblies,
    affected_occurrences=sorted(set(expected)|set(revised)),expected_physical_occurrences=len(m['occurrences'])+100,
    expected_definition_count=len(m['definitions'])+8,expected_assembly_count=len(m['assemblies'])+12,
    historical_geometry_qualified=False,installation_qualified=False,stops_and_control_rods_pending=True,
    coupling_detail_unresolved=True,standard_assembly_modified=False))
print('Saved',len(m['occurrences'])+100,'physical occurrences; 132 affected; front joint layout remains conditional.',flush=True)
