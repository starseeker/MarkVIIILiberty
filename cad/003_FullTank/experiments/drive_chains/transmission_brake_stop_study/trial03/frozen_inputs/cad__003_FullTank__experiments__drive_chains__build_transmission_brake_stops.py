"""Build an experimental shared brake-stop arrangement from the qualified parent."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid

H=Path(__file__).resolve().parent; STAGE=H.parents[1]; ROOT=STAGE.parents[1]
sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--source',type=Path,default=H/'transmission_brake_front_study/trial01')
p.add_argument('--controls',type=Path,default=H/'transmission_brake_stop_study/controls.json')
p.add_argument('--mount-controls',type=Path,help='Optional source-proportioned lower bearing boss trial')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithBrakeStops.FCStd';assert not native.exists()
parent=a.source.resolve();prior=read(parent/'report.json');source=parent/prior['native_file']
m=read(parent/'isolated/manifest.json');assert sha(source)==m['native_sha256']==prior['native_sha256']
assert read(parent/'independent_checks.json')['local_front_checks_passed']
assert read(parent/'exchange_checks.json')['passed']
assert read(parent/'definition_preservation_checks.json')['passed']
packet=H/'transmission_brake_stop_study/sources.json';sources=read(packet)
assert all(sha(ROOT/f)==s for f,s in sources['source_hashes'].items())
c=read(a.controls)['controls']
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_brake_stop_parts import parts
V=App.Vector
rows={r['name']:r for r in m['occurrences']};castings={};mount_revisions={};mount_details={}
anchor=read(H/'transmission_brake_anchor_study/trial01/report.json')
bands={}
for role in ['low','track']:
    d=m['definitions']['Def_BrakeBand_'+role+'_band'];f=Path(d['brep_path']);assert sha(f)==d['brep_sha256']
    s=Part.Shape();s.read(str(f));bands[role]=s
if a.mount_controls:
    from transmission_brake_stop_mount_parts import revise
    inherited={}
    for role in ['cap','bracket']:
        d=m['definitions']['Def_FixedBearing_inner_'+role];f=Path(d['brep_path']);assert sha(f)==d['brep_sha256']
        s=Part.Shape();s.read(str(f));inherited[role]=s
    hardware={k:v['value'] for k,v in read(H/'transmission_stud_controls.json')['controls'].items()}
    castings,mount_revisions,mount_details=revise(read(a.mount_controls)['controls'],c,hardware,inherited,rows)
    rows.update(mount_revisions)
center=V(*[rows['PortLowSpeedBrakeUpperBand']['frame'][i] for i in [3,7,11]])
nut=rows['PortFixedBearing_inner_Stud01_Nut']['frame']
stations=dict(low=center.y,track=rows['PortTrackBrakeUpperBand']['frame'][7],mount=nut[7])
shapes,details=parts(c,anchor,bands,stations,[nut[3]-center.x,nut[11]-center.z])
doc=App.openDocument(str(source));definitions={};new={};revised={};groups=[]
for name,s in castings.items():
    body=doc.getObject(name);body.Tip.Shape=s
    metadata(body,BrakeStopMountRevision='Lower bearing bosses follow relative HB134/135 station; shaft/socket and oil interfaces retained. Unqualified casting profile.')
for name,row in mount_revisions.items():
    obj=doc.getObject(name);owner=doc.getObject(row['owners'][-1])
    obj.setLink(doc.getObject(row['definition']))
    obj.LinkPlacement=owner.getGlobalPlacement().inverse().multiply(App.Placement(App.Matrix(*row['frame'])))
    metadata(obj,BrakeStopMountRevision='Inferred MX36 lower / MX10 upper allocation and lower boss station; source lengths unchanged.')
    revised[name]=row
specs={
    'low_lug':('MX86',['SNL:122:022']), 'track_lug':('MX87',['SNL:122:024']),
    'lug_rivet':('Quarter-inch countersunk steel rivet',['SNL:191:007']),
    'bar_rivet':('Quarter-inch button rivet',['SNL:41:026']),
    'M343_screw':('M343',['SNL:205:012']), 'MX88_screw':('MX88',['SNL:205:016']),
    'nut':('Half-inch SAE hex nut',['SNL:205:013','SNL:205:017']),
    'M341_bracket':('M341',['SNL:41:025']), 'M342_bar':('M342',['SNL:41:024']),
    'low_lower_band':('M344',[]), 'track_lower_band':('M349',[])}
for role,s in shapes.items():
    body=doc.addObject('PartDesign::Body','Def_BrakeStop_'+role);doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','EstimatedBrakeStop').Shape=s
    mark,rids=specs[role]
    metadata(body,DefinitionKey='brake_stop_'+role,SourcePartMark=mark,SourceRecords=rids,
        SurveyIds=sorted({pid for rec in sources['source_records'] if rec['record_id'] in rids for pid in rec['part_ids']}),
        Representation='assembly',Coverage='reconstruction_trial',
        ParameterUpdate='Regenerate with build_transmission_brake_stops.py',
        ReconstructionStatus='UNQUALIFIED trial: source counts, estimated geometry and transverse/mounting arrangement; MX95/MX96 mapping unresolved.')
    if role.endswith('_lower_band'):
        inherited=doc.getObject('Def_BrakeBand_'+role.split('_')[0]+'_band')
        for prop in ['SourceRecords','SurveyIds']:
            if prop in inherited.PropertiesList:setattr(body,prop,getattr(inherited,prop))
        metadata(body,ParentDefinition=inherited.Name,Revision='Lower band only: three countersunk stop-lug rivet holes. Upper band unchanged.')
    definitions[role]=body

def group(name,parent,world=None):
    obj=doc.addObject('App::Part',name);parent.addObject(obj)
    obj.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:brake-stop:'+name))
    if world is not None:obj.Placement=parent.getGlobalPlacement().inverse().multiply(world)
    groups.append(name);return obj

def owners(obj):
    result=[obj.Name]
    while True:
        parents=[v for v in obj.InList if v.TypeId=='App::Part' and obj in v.Group]
        if not parents:break
        assert len(parents)==1
        obj=parents[0];result.insert(0,obj.Name)
    return result

def add(name,role,owner,local):
    obj=doc.addObject('App::Link',name);owner.addObject(obj);obj.setLink(definitions[role]);obj.LinkPlacement=local
    metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=specs[role][1])
    new[name]=dict(definition=definitions[role].Name,owners=owners(owner),
        frame=list(owner.getGlobalPlacement().multiply(local).toMatrix().A))

stop_rotation=App.Rotation(*details['rotation'])
root=group('TransmissionBrakeStops',doc.Root)
radial=stop_rotation.multVec(V(0,0,1))
for hand,sign in [('Port',1),('Starboard',-1)]:
    mid=(stations['low']+stations['track'])/2
    support_pose=App.Placement(V(center.x,sign*mid,center.z),stop_rotation)
    support=group(hand+'BrakeStopSupport',root,support_pose)
    turn=App.Rotation(V(0,0,1),180) if sign<0 else App.Rotation()
    add(hand+'BrakeStopBar','M342_bar',support,App.Placement(V(),turn))
    mounting_v=sign*(mid-stations['mount'])
    add(hand+'BrakeStopBracket','M341_bracket',support,App.Placement(V(0,mounting_v,0),App.Rotation()))
    for j in details['support_rivets']:
        u,v,w=j['bracket_uvw_mm']
        add(hand+'BrakeStopBarRivet'+str(j['index']),'bar_rivet',support,
            App.Placement(V(u,v+mounting_v,w),App.Rotation()))
    # Retain source-length studs and the existing nut/cotter relationships.
    # The reduced coarse-thread embedding is a candidate, not an accepted fit.
    mount_index='01' if sign>0 else '03'
    for suffix in ['Stud','Nut','Cotter']:
        name=hand+'FixedBearing_inner_Stud'+mount_index+'_'+suffix
        obj=doc.getObject(name);pose=App.Placement(App.Matrix(*rows[name]['frame']))
        pose.Base+=V(c['bracket_stock'],0,0)
        owner=doc.getObject(rows[name]['owners'][-1]);obj.LinkPlacement=owner.getGlobalPlacement().inverse().multiply(pose)
        metadata(obj,BrakeStopTrial='Advanced by estimated bracket stock; minimum retained embedding and nut/cotter stack require validation.')
        revised[name]=dict(rows[name],frame=list(pose.toMatrix().A))
    for role,label in [('low','LowSpeed'),('track','Track')]:
        prefix=hand+label+'Brake';d=details['brakes'][role]
        world=App.Placement(V(center.x,sign*stations[role],center.z),stop_rotation)
        joint=group(prefix+'LowerStopJoint',doc.getObject(prefix+'Lower'),world)
        add(prefix+'StopLug',role+'_lug',joint,App.Placement())
        for j in d['rivets']:
            add(prefix+'StopLugRivet'+str(j['index']),'lug_rivet',joint,App.Placement(App.Matrix(*j['frame'])))
        # M343 tangent tip bears on the +U bar edge; nut seats on lug boss.
        axis_w=d['tangent_axis_w_mm']
        add(prefix+'StopScrew','M343_screw',joint,
            App.Placement(V(c['bar_half_width']+c['tangent_screw_length'],0,axis_w),App.Rotation(V(0,0,1),V(-1,0,0))))
        add(prefix+'StopScrewNut','nut',joint,
            App.Placement(V(c['boss_u1'],0,axis_w),App.Rotation(V(0,0,1),V(1,0,0))))
        v=sign*(mid-stations[role])
        add(prefix+'StopBarSetScrew','MX88_screw',support,
            App.Placement(V(0,v,d['radial_tip_w_mm']+c['radial_screw_length']),App.Rotation(V(1,0,0),180)))
        add(prefix+'StopBarSetScrewNut','nut',support,
            App.Placement(V(0,v,details['bar_outer_radius_mm']),App.Rotation()))
        name=prefix+'LowerBand';obj=doc.getObject(name);pose=obj.LinkPlacement
        obj.setLink(definitions[role+'_lower_band']);obj.LinkPlacement=pose
        revised[name]=dict(rows[name],definition=definitions[role+'_lower_band'].Name)
assert len(new)==44 and len(revised)==(32 if a.mount_controls else 10) and len(groups)==7
doc.Root.Label='Powertrain development — UNQUALIFIED brake-stop trial'
doc.Root.RegistrationStatus='Conditional shared crossbar and bearing-cap attachment; source and installation unresolved.'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==prior['native_sha256']
folder=out/'changed_shapes';folder.mkdir()
for role,s in shapes.items():s.exportBrep(str(folder/('Def_BrakeStop_'+role+'.brep')))
for key,s in castings.items():s.exportBrep(str(folder/(key+'.brep')))
locked=[Path(__file__),H/'transmission_brake_stop_parts.py',a.controls.resolve(),packet,
    H/'transmission_brake_anchor_parts.py',H/'transmission_frame_joint_parts.py',parent/'report.json',parent/'isolated/manifest.json',
    H/'transmission_brake_anchor_study/trial01/report.json']
if a.mount_controls:
    locked += [a.mount_controls.resolve(),H/'transmission_brake_stop_mount_parts.py',H/'transmission_stud_controls.json',
        H/'transmission_brake_stop_study/mount_review/source_stack_analysis.json']
frozen=out/'frozen_inputs';frozen.mkdir()
for f in locked:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes={str(f.relative_to(ROOT)):sha(f) for f in locked},controls=c,details=details,
    source_identity_mapping='M341/M342 catalogue geometry represented by an explicit hypothesis; not a resolved alias for MX95/MX96.',
    expected_new_occurrences=new,expected_revised_occurrences=revised,new_assemblies=groups,
    new_definitions=['Def_BrakeStop_'+k for k in shapes],changed_definitions=list(castings),mount_revision=mount_details,
    affected_occurrences=sorted(set(new)|set(revised)),expected_physical_occurrences=len(m['occurrences'])+len(new),
    expected_definition_count=len(m['definitions'])+len(shapes),expected_assembly_count=len(m['assemblies'])+len(groups),
    status='experimental_not_qualified',historical_geometry_qualified=False,installation_qualified=False,
    standard_assembly_modified=False))
print('Saved experimental brake-stop assembly:',native,flush=True)
