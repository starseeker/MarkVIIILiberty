"""Add source-sized high-speed lining strips and partial backing blanks."""
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
p.add_argument('--controls',type=Path,default=H/'transmission_high_brake_study/band_controls.json')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
parent=H/'transmission_brake_spacer_study/trial01';pr=read(parent/'report.json')
source=parent/pr['native_file'];m=read(parent/'isolated/manifest.json');q=read(parent/'qualification.json')
assert sha(source)==pr['native_sha256']==m['native_sha256']==q['native_sha256'] and q['local_static_checks_passed']
packet=H/'transmission_high_brake_study/source_inventory.json';sources=read(packet)
assert all(sha(ROOT/f)==v for f,v in sources['source_hashes'].items())
c=read(a.controls)['controls']
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_high_brake_band_parts import parts,rotate_theta
shapes,details=parts(c);native=out/'PowertrainWithHighBrakeBands.FCStd';assert not native.exists()
locked=[Path(__file__),H/'transmission_high_brake_band_parts.py',H/'transmission_brake_band_parts.py',
 H/'transmission_frame_joint_parts.py',a.controls.resolve(),packet,parent/'report.json',parent/'qualification.json',
 parent/'isolated/manifest.json',STAGE/'lib/evidence.py',STAGE/'lib/cad_build.py']
inputs={str(f.relative_to(ROOT)):sha(f) for f in locked};rows={v['name']:v for v in m['occurrences']}
dr=m['definitions']['Def_TransmissionCore_high_drum'];assert sha(dr['brep_path'])==dr['brep_sha256']
drum=Part.Shape();drum.read(dr['brep_path'])
face=next(f for f in drum.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-c['inner_radius'])<1e-7)
b=face.optimalBoundingBox(False,False);station=(b.YMin+b.YMax)/2
doc=App.openDocument(str(source));defs={};records={};assemblies=[];expected={};interfaces={}
for role,mark,rid in [('long_band','M359','SNL:8:029'),('long_lining','MX109','SNL:8:030'),
                      ('short_band','M360','SNL:9:007'),('short_lining','M364','SNL:9:008')]:
    definition=doc.addObject('PartDesign::Body','Def_HighBrake_'+role);doc.Definitions.addObject(definition)
    definition.newObject('PartDesign::Feature','ReconstructedHighBrakeStock').Shape=shapes[role]
    record=next(v for v in sources['source_records'] if v['record_id']==rid)
    metadata(definition,DefinitionKey='high_brake_'+role,SourcePartMark=mark,SourceRecords=[rid,'SNL:119:017'],
        SurveyIds=record['part_ids'],Representation='assembly',Coverage='partial',
        ParameterUpdate='Regenerate with build_transmission_high_brake_bands.py',
        ReconstructionStatus='SNL continuous long/short lining variant. Partial backing blanks: end attachments and hardware pending. Long hole pattern, steel stock, clocking and axial offset estimated.')
    defs[role]=definition;records[role]=rid
def group(name,parent,pose=None):
    g=doc.addObject('App::Part',name);parent.addObject(g)
    g.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:high-brake:'+name))
    if pose is not None:g.Placement=pose
    assemblies.append(g.Name);return g
root=group('TransmissionHighSpeedBrakes',doc.Root)
for hand,sign in [('Port',1),('Starboard',-1)]:
    receiver=hand+'TransmissionCore_high_drum';world=App.Placement(App.Matrix(*rows[receiver]['frame']))
    center=world.multVec(App.Vector(0,station,0));center.y+=sign*c['axial_outboard_shift']
    brake=group(hand+'HighSpeedBrake',root,App.Placement(center,App.Rotation()))
    interfaces[brake.Name]=dict(receiver=receiver,drum_station_mm=station,center_world_mm=list(center),
        axial_outboard_shift_mm=c['axial_outboard_shift'],drum_face_bounds_mm=[b.YMin,b.YMax])
    for role in ['long','short']:
        band=group(brake.Name+role.title()+'Assembly',brake,App.Placement(App.Vector(),rotate_theta(details['placement_angles_rad'][role])))
        for leaf in ['band','lining']:
            key=role+'_'+leaf;name=brake.Name+role.title()+leaf.title()
            obj=doc.addObject('App::Link',name);band.addObject(obj);obj.setLink(defs[key]);obj.LinkPlacement=App.Placement()
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=[records[key]],Coverage='partial')
            expected[name]=dict(definition=defs[key].Name,frame=list(band.getGlobalPlacement().toMatrix().A),owners=['Root',root.Name,brake.Name,band.Name])
doc.Root.Label='Powertrain development — high-speed brake bands in progress'
doc.Root.RegistrationStatus='SNL long/short lining variant; partial backing blanks. High-speed end fittings, anchors, adjustment, stops and hardware pending.'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==pr['native_sha256'] and all(sha(ROOT/f)==v for f,v in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in locked:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
folder=out/'changed_shapes';folder.mkdir()
for k,s in shapes.items():s.exportBrep(str(folder/('Def_HighBrake_'+k+'.brep')))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=inputs,controls=c,details=details,interfaces=interfaces,
    expected_new_occurrences=expected,affected_occurrences=sorted(expected),new_assemblies=assemblies,
    new_definitions=['Def_HighBrake_'+k for k in shapes],changed_definitions=[],
    expected_physical_occurrences=len(rows)+8,expected_definition_count=len(m['definitions'])+4,
    expected_assembly_count=len(m['assemblies'])+7,historical_geometry_qualified=False,installation_qualified=False,
    standard_assembly_modified=False,packet_complete=False,
    limits=['End attachments, lining/steel hardware, anchors, adjuster, lever and stops remain absent.',
        'SNL continuous long strip differs from HB segmented lining count.',
        'Centered printed lining width overhangs the image-derived drum face by0.589643 mm per edge.',
        'Long hole pattern, band stock, clocking and neutral bending datum estimated.']))
print('Saved',len(rows)+8,'occurrences, partial high-speed brake bands.',flush=True)
