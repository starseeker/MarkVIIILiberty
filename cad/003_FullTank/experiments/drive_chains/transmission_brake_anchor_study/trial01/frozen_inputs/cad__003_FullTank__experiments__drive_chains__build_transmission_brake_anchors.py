"""Install source-counted rear brackets and retained pins on the segmented bands."""
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
p.add_argument('--controls',type=Path,default=HERE/'transmission_brake_anchor_study/controls.json')
a=p.parse_args();parent=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithBrakeAnchors.FCStd';assert not native.exists()
prior=read(parent/'report.json');source=parent/prior['native_file'];m=read(parent/'isolated/manifest.json')
assert sha(source)==prior['native_sha256']==m['native_sha256']
assert read(parent/'independent_checks.json')['local_link_checks_passed']
assert read(parent/'definition_preservation_checks.json')['passed'] and read(parent/'exchange_checks.json')['passed']
packet=HERE/'transmission_brake_anchor_study/sources.json';sources=read(packet)
assert all(sha(ROOT/f)==digest for f,digest in sources['source_hashes'].items())
band_path=HERE/'transmission_brake_band_study/controls.json';bc=read(band_path)['controls'];c=read(a.controls)['controls']
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_brake_anchor_parts import parts
from transmission_brake_band_parts import rotate_theta
V=App.Vector;flip=App.Rotation(V(1,0,0),180)
new,changed,d=parts(c,bc,prior);rows={v['name']:v for v in m['occurrences']}
locked=[Path(__file__),a.controls.resolve(),packet,band_path,STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py',
        parent/'report.json',parent/'isolated/manifest.json',parent/'independent_checks.json',
        parent/'definition_preservation_checks.json',parent/'exchange_checks.json']
locked+=sorted({Path(module.__file__).resolve() for module in list(sys.modules.values())
    if getattr(module,'__file__',None) and Path(module.__file__).resolve().parent==HERE
    and str(module.__file__).endswith('.py')})
locked=sorted(set(locked));inputs={str(f.relative_to(ROOT)):sha(f) for f in locked}
doc=App.openDocument(str(source));defs={};records={};marks={}
specs=[('low_bracket','MX49',['SNL:39:024','SNL:39:027']),
       ('track_bracket','MX47',['SNL:41:019','SNL:41:021']),
       ('low_pin','M348',['SNL:137:017']),('track_pin','M353',['SNL:142:027']),
       ('spring','MX81',['SNL:219:020']),('spacer','MX82',['SNL:218:010']),
       ('steel_rivet','Countersunk steel rivet 3/8 x 1-3/8',['SNL:191:011']),
       ('long_copper_rivet','Countersunk copper rivet 1/4 x 1-3/8',['SNL:192:012']),
       ('low_retainer_rivet','Button rivet 3/16 x 1-3/8',['SNL:166:009']),
       ('track_retainer_rivet','Button rivet 3/16 x 7/8',['SNL:166:007'])]
for role,mark,rids in specs:
    body=doc.addObject('PartDesign::Body','Def_BrakeAnchor_'+role);doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedRearAnchor').Shape=new[role]
    ids=sorted({pid for rec in sources['source_records'] if rec['record_id'] in rids for pid in rec['part_ids']})
    metadata(body,DefinitionKey='brake_anchor_'+role,SourcePartMark=mark,SourceRecords=rids,SurveyIds=ids,
        Representation='assembly',Coverage='reconstruction',ParameterUpdate='Regenerate with build_transmission_brake_anchors.py',
        ReconstructionStatus='Source identity, quantity and listed stock; estimated hidden bracket, pin and spring form. Later SNL fittings used with earlier segmented lining. Coupling screws unresolved; service sequence not qualified.')
    defs[role]=body;records[role]=rids;marks[role]=mark
for role,s in changed.items():
    body=doc.getObject('Def_BrakeBand_'+role);body.Tip.Shape=s
    metadata(body,RearAnchorRevision='Rear split widened; steel-rivet holes added and covered lining-rivet grips extended through the bracket foot.',
        RearAnchorUpdate='Regenerate with build_transmission_brake_anchors.py')
expected={};revised={};assembly_revisions={};added_children={};assemblies=[]
def link(name,role,owner,pose,owners):
    obj=doc.addObject('App::Link',name);owner.addObject(obj);obj.setLink(defs[role]);obj.LinkPlacement=pose
    metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=records[role])
    expected[name]=dict(definition=defs[role].Name,frame=list(owner.getGlobalPlacement().multiply(pose).toMatrix().A),owners=owners)
    added_children.setdefault(owner.Name,[]).append(obj.Name)
def capture(name):
    row=rows[name];obj=doc.getObject(row['object']);owner=doc.getObject(row['owners'][-1])
    revised[name]=dict(definition=obj.LinkedObject.Name,
        frame=list(owner.getGlobalPlacement().multiply(obj.LinkPlacement).toMatrix().A),owners=row['owners'])
for hand in ['Port','Starboard']:
    for role,label in [('low','LowSpeed'),('track','Track')]:
        prefix=hand+label+'Brake';dr=d['brakes'][role];bd=d['band_details']['brakes'][role]
        for half in ['Upper','Lower']:
            hp=prefix+half;hg=doc.getObject(hp);capture(hp+'Band')
            for i,angle in enumerate(bd['segment_angles_rad'],1):
                sg=doc.getObject(hp+'Segment'+str(i));sg.Placement=App.Placement(V(),rotate_theta(angle))
                assembly_revisions[sg.Name]=dict(local=list(sg.Placement.toMatrix().A),world=list(sg.getGlobalPlacement().toMatrix().A))
                for j in [8,9] if i==3 else []:
                    obj=doc.getObject(sg.Name+'Rivet'+str(j));local=obj.LinkPlacement
                    obj.setLink(defs['long_copper_rivet']);obj.LinkPlacement=local
                    metadata(obj,SourceRecords=records['long_copper_rivet'],RearAnchorRevision='Longer source-listed stock through rear bracket foot.')
                capture(sg.Name+'Lining')
                for j in range(1,10):capture(sg.Name+'Rivet'+str(j))
            joint=doc.addObject('App::Part',hp+'AnchorJoint');hg.addObject(joint)
            joint.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:rear-brake-anchor:'+joint.Name))
            assemblies.append(joint.Name);added_children.setdefault(hg.Name,[]).append(joint.Name)
            owners=rows[hp+'Band']['owners']+[joint.Name]
            link(hp+'AnchorBracket',role+'_bracket',joint,App.Placement(),owners)
            for steel in dr['steel_joints']:
                link(hp+'AnchorSteelRivet'+str(steel['index']),'steel_rivet',joint,App.Placement(App.Matrix(*steel['frame'])),owners)
            retained=(half==('Lower' if hand=='Port' else 'Upper')) if role=='low' else (half==('Upper' if hand=='Port' else 'Lower'))
            if retained:
                link(hp+'RetainerSpring','spring',joint,App.Placement(V(-dr['anchor_radius_mm'],dr['spring_y_mm'],0),App.Rotation()),owners)
                sx,sz=dr['retainer_stud_xz_mm'];sign=dr['outward_sign'];y=dr['lug_y_mm']-sign*c['lug_stock']/2
                link(hp+'RetainerRivet',role+'_retainer_rivet',joint,App.Placement(V(sx,y,sz),flip if sign<0 else App.Rotation()),owners)
                if role=='low':
                    y=dr['lug_y_mm']-c['lug_stock']/2-c['spring_spacer_stock']
                    link(hp+'RetainerSpacer','spacer',joint,App.Placement(V(sx,y,sz),App.Rotation()),owners)
        brake=doc.getObject(prefix);owners=rows[prefix+'UpperBand']['owners'][:-1]
        link(prefix+'AnchorPin',role+'_pin',brake,App.Placement(V(-dr['anchor_radius_mm'],0,0),flip if hand=='Starboard' else App.Rotation()),owners)
assert len(expected)==82 and len(revised)==248 and len(assembly_revisions)==24 and len(assemblies)==8
doc.Root.Label='Powertrain development — rear brake anchor joints'
doc.Root.RegistrationStatus='Rear band brackets and retained pins reconstructed; hidden joint layout estimated. Front ears, controls and coupling details remain incomplete.'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==prior['native_sha256'] and all(sha(ROOT/f)==digest for f,digest in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in locked:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
folder=out/'changed_shapes';folder.mkdir()
for name,s in {**{'Def_BrakeAnchor_'+k:v for k,v in new.items()},**{'Def_BrakeBand_'+k:v for k,v in changed.items()}}.items():s.exportBrep(str(folder/(name+'.brep')))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=inputs,controls=c,details=d,
    changed_definitions=sorted('Def_BrakeBand_'+k for k in changed),new_definitions=sorted('Def_BrakeAnchor_'+k for k in new),
    expected_new_occurrences=expected,expected_revised_occurrences=revised,assembly_revisions=assembly_revisions,
    added_children=added_children,new_assemblies=assemblies,affected_occurrences=sorted(set(expected)|set(revised)),
    expected_physical_occurrences=len(rows)+82,expected_definition_count=len(m['definitions'])+10,
    expected_assembly_count=len(m['assemblies'])+8,historical_geometry_qualified=False,installation_qualified=False,
    front_ears_and_controls_pending=True,coupling_detail_unresolved=True,standard_assembly_modified=False))
print('Saved',len(rows)+82,'physical occurrences; 330 affected; historical joint layout remains conditional.',flush=True)
