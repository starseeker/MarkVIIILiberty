"""Add the M361 rear band end, riveted short-tail joint and six-screw long-tail coupling."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--controls',type=Path,default=H/'transmission_high_brake_study/joint_controls.json')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
parent=H/'transmission_brake_spacer_study/trial01';pr=read(parent/'report.json')
source=parent/pr['native_file'];m=read(parent/'isolated/manifest.json');q=read(parent/'qualification.json')
assert sha(source)==pr['native_sha256']==m['native_sha256']==q['native_sha256'] and q['local_static_checks_passed']
packet=H/'transmission_high_brake_study/source_inventory.json';sources=read(packet)
assert all(sha(ROOT/f)==v for f,v in sources['source_hashes'].items())
joint_packet=H/'transmission_high_brake_study/joint_sources.json';joint_sources=read(joint_packet)
assert all(sha(ROOT/f)==v for f,v in joint_sources['source_hashes'].items())
sources['source_records']+=joint_sources['source_records']
c=read(a.controls)['controls'];band_controls=H/'transmission_high_brake_study/band_controls.json';bc=read(band_controls)['controls']
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_high_brake_joint_parts import parts,rotate_theta
shapes,details=parts(c,bc);native=out/'PowertrainWithHighBrakeJoints.FCStd';assert not native.exists()
locked=[Path(__file__),H/'transmission_high_brake_joint_parts.py',H/'transmission_high_brake_band_parts.py',H/'transmission_brake_anchor_parts.py',H/'transmission_brake_stop_parts.py',band_controls,joint_packet,H/'transmission_brake_band_parts.py',
 H/'transmission_frame_joint_parts.py',a.controls.resolve(),packet,parent/'report.json',parent/'qualification.json',
 parent/'isolated/manifest.json',STAGE/'lib/evidence.py',STAGE/'lib/cad_build.py']
inputs={str(f.relative_to(ROOT)):sha(f) for f in locked};rows={v['name']:v for v in m['occurrences']}
dr=m['definitions']['Def_TransmissionCore_high_drum'];assert sha(dr['brep_path'])==dr['brep_sha256']
drum=Part.Shape();drum.read(dr['brep_path'])
face=next(f for f in drum.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-bc['inner_radius'])<1e-7)
b=face.optimalBoundingBox(False,False);station=(b.YMin+b.YMax)/2
doc=App.openDocument(str(source));defs={};records={};assemblies=[];expected={};interfaces={}
for role,mark,rid in [('long_band','M359','SNL:8:029'),('long_lining','MX109','SNL:8:030'),
                      ('short_band','M360','SNL:9:007'),('short_lining','M364','SNL:9:008'),
                      ('anchor_end','M361','SNL:9:006'),('anchor_rivet','Steel CS rivet5/16x1','SNL:191:008'),('coupling_screw','MX38','SNL:205:008')]:
    definition=doc.addObject('PartDesign::Body','Def_HighBrake_'+role);doc.Definitions.addObject(definition)
    definition.newObject('PartDesign::Feature','ReconstructedHighBrakeStock').Shape=shapes[role]
    record=next(v for v in sources['source_records'] if v['record_id']==rid)
    metadata(definition,DefinitionKey='high_brake_'+role,SourcePartMark=mark,SourceRecords=[rid],
        SurveyIds=record['part_ids'],Representation='assembly',Coverage='partial',
        ParameterUpdate='Regenerate with build_transmission_high_brake_joints.py',
        ReconstructionStatus='SNL continuous long/short lining variant with M361 rear end and coupling hardware. Long-hole pattern, steel stock, formed terminal and anchor profiles estimated. Free ends and external anchor support pending.')
    defs[role]=definition;records[role]=rid
def group(name,parent,pose=None):
    g=doc.addObject('App::Part',name);parent.addObject(g)
    g.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:high-brake:'+name))
    if pose is not None:g.Placement=pose
    assemblies.append(g.Name);return g
root=group('TransmissionHighSpeedBrakes',doc.Root)
for hand,sign in [('Port',1),('Starboard',-1)]:
    receiver=hand+'TransmissionCore_high_drum';world=App.Placement(App.Matrix(*rows[receiver]['frame']))
    center=world.multVec(App.Vector(0,station,0));center.y+=sign*bc['axial_outboard_shift']
    brake=group(hand+'HighSpeedBrake',root,App.Placement(center,App.Rotation()))
    interfaces[brake.Name]=dict(receiver=receiver,drum_station_mm=station,center_world_mm=list(center),
        axial_outboard_shift_mm=bc['axial_outboard_shift'],drum_face_bounds_mm=[b.YMin,b.YMax])
    strap=group(brake.Name+'StrapAssembly',brake)
    metadata(strap,SourceAssemblyMark='M367',SourceRecords=['SNL:229:001','HB:nomenclature:207:062'],Coverage='partial',ReconstructionStatus='Complete-strap catalogue identity represented by its component assemblies; no duplicate solid.')
    groups={}
    for role in ['long','short']:
        band=group(brake.Name+role.title()+'Assembly',strap,App.Placement(App.Vector(),rotate_theta(details['placement_angles_rad'][role])))
        groups[role]=band
        for leaf in ['band','lining']:
            key=role+'_'+leaf;name=brake.Name+role.title()+leaf.title()
            obj=doc.addObject('App::Link',name);band.addObject(obj);obj.setLink(defs[key]);obj.LinkPlacement=App.Placement()
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=[records[key]],Coverage='partial')
            expected[name]=dict(definition=defs[key].Name,frame=list(band.getGlobalPlacement().toMatrix().A),owners=['Root',root.Name,brake.Name,strap.Name,band.Name])
    def installed(name,role,parent,local,owners):
        obj=doc.addObject('App::Link',name);parent.addObject(obj);obj.setLink(defs[role]);obj.LinkPlacement=local
        metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=[records[role]],Coverage='reconstruction_trial')
        expected[name]=dict(definition=defs[role].Name,frame=list(parent.getGlobalPlacement().multiply(local).toMatrix().A),owners=owners)
    inv_short=groups['short'].Placement.inverse()
    short_owners=['Root',root.Name,brake.Name,strap.Name,groups['short'].Name]
    installed(brake.Name+'AnchorEnd','anchor_end',groups['short'],inv_short,short_owners)
    for n,joint in enumerate(details['rivets'],1):
        installed(brake.Name+'AnchorEndRivet'+str(n),'anchor_rivet',groups['short'],inv_short.multiply(App.Placement(App.Matrix(*joint['frame']))),short_owners)
    coupling=group(brake.Name+'RearCoupling',strap)
    owners=['Root',root.Name,brake.Name,strap.Name,coupling.Name]
    for n,joint in enumerate(details['screws'],1):
        installed(brake.Name+'CouplingScrew'+str(n),'coupling_screw',coupling,App.Placement(App.Matrix(*joint['frame'])),owners)
doc.Root.Label='Powertrain development — rear high-speed brake joints'

doc.Root.RegistrationStatus='SNL long/short lining variant; M361 riveted ends and coupling screws installed. Free-end fittings, support brackets/pins, adjustment and stops pending.'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==pr['native_sha256'] and all(sha(ROOT/f)==v for f,v in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in locked:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
folder=out/'changed_shapes';folder.mkdir()
for k,s in shapes.items():s.exportBrep(str(folder/('Def_HighBrake_'+k+'.brep')))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=inputs,controls=c,band_controls=bc,details=details,interfaces=interfaces,
    expected_new_occurrences=expected,affected_occurrences=sorted(expected),new_assemblies=assemblies,
    new_definitions=['Def_HighBrake_'+k for k in shapes],changed_definitions=[],
    expected_physical_occurrences=len(rows)+34,expected_definition_count=len(m['definitions'])+7,
    expected_assembly_count=len(m['assemblies'])+11,historical_geometry_qualified=False,installation_qualified=False,
    standard_assembly_modified=False,packet_complete=False,
    limits=details['limitations']+['Centered printed lining width overhangs image-derived drum face0.589643 mm per edge.','SNL continuous long-strip composition differs from HB six-segment count.']))
print('Saved',len(rows)+34,'occurrences, rear high-speed brake coupling populated; packet remains incomplete.',flush=True)
