"""Connect four M337 links to the saved M338 supports with retained M339 pins."""
import argparse
from pathlib import Path
import shutil
import sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--controls',type=Path,default=HERE/'transmission_brake_link_study/controls.json')
a=p.parse_args();parent=a.source.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithBrakeLinks.FCStd';assert not native.exists()
r=read(parent/'report.json');source=parent/r['native_file'];m=read(parent/'isolated/manifest.json')
assert sha(source)==r['native_sha256']==m['native_sha256']
assert read(parent/'independent_checks.json')['local_brake_checks_passed']
assert read(parent/'definition_preservation_checks.json')['passed'] and read(parent/'exchange_adaptive_checks.json')['passed']
support_path=HERE/'transmission_brake_suspension_study/trial02/report.json';support=read(support_path)
packet=HERE/'transmission_brake_link_study/sources.json';sources=read(packet)
assert all(sha(ROOT/f)==v for f,v in sources['source_hashes'].items())
import FreeCAD as App
import Part
from lib.cad_build import metadata
from transmission_brake_link_parts import dimensions,parts
V=App.Vector;rows={v['name']:v for v in m['occurrences']};c=read(a.controls)['controls']
def position(frame):return [frame[3],frame[7],frame[11]]
upper=position(rows['PortTrackBracket']['frame']);interface=r['interfaces']['PortTrackBrake'];band=read(parent/'../controls.json')['controls']
plate_row=rows['TransmissionFrame_MiddleDiaphragm'];plate_record=m['definitions'][plate_row['definition']]
assert sha(Path(plate_record['brep_path']))==plate_record['brep_sha256']
plate=Part.Shape();plate.read(plate_record['brep_path']);plate.Placement=App.Placement(App.Matrix(*plate_row['frame']))
d=dimensions(c,support,upper,interface['center_mm'],plate.BoundBox.XMax);shapes,cotter=parts(c,d)
loaded=[Path(module.__file__).resolve() for module in list(sys.modules.values()) if getattr(module,'__file__',None)
        and Path(module.__file__).resolve().parent==HERE and str(module.__file__).endswith('.py')]
locked=sorted(set(loaded+[Path(__file__),a.controls.resolve(),packet,support_path,STAGE/'lib/cad_build.py',STAGE/'lib/evidence.py',
    parent/'report.json',parent/'isolated/manifest.json',parent/'independent_checks.json',parent/'definition_preservation_checks.json',parent/'exchange_adaptive_checks.json',parent/'../controls.json']))
inputs={str(v.resolve().relative_to(ROOT)):sha(v) for v in locked}
doc=App.openDocument(str(source));defs={};records={}
for role,mark,rids in [('link','M337',['SNL:119:023','HB:nomenclature:207:035']),
    ('pin','M339',['SNL:137:024','HB:nomenclature:207:038']),('cotter','Split pin 1/4 x 1-1/2',['SNL:141:014','SNL:137:025'])]:
    body=doc.addObject('PartDesign::Body','Def_BrakeLink_'+role);doc.Definitions.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedBrakeLinkage').Shape=shapes[role]
    ids=sorted({pid for rec in sources['source_records'] if rec['record_id'] in rids for pid in rec['part_ids']})
    metadata(body,DefinitionKey='brake_link_'+role,SourcePartMark=mark,SourceRecords=rids,SurveyIds=ids,
        Representation='assembly',Coverage='reconstruction',ParameterUpdate='Regenerate with build_transmission_brake_links.py',
        ReconstructionStatus='Four separate pivot pins follow SNL137; earlier two-pin count unresolved. Inboard-side placement, clevis, section and lower-eye station estimated; lower attachment pending.')
    defs[role]=body;records[role]=rids
expected={};interfaces={};added_children={};repositioned={};assembly_shifts={}
for hand in ['Port','Starboard']:
    for role in ['LowSpeed','Track']:
        prefix=hand+role;row=rows[prefix+'Bracket'];pose=App.Placement(App.Matrix(*row['frame']))
        owner=doc.getObject(row['owners'][-1]);sign=-1 if hand=='Port' else 1
        width=band['low' if role=='LowSpeed' else 'track']['width']+2*band['steel_side_overhang']
        shift=sign*(width/2+c['lower_stock']/2+c['link_band_side_clearance'])
        owner.Placement=App.Placement(V(0,shift,0),App.Rotation()).multiply(owner.Placement)
        assembly_shifts[owner.Name]=[0,shift,0];pose.Base=pose.Base+V(0,shift,0)
        for inherited in [prefix+'Bracket']+([prefix+'Stop'] if role=='Track' else []):
            before=rows[inherited];frame=list(before['frame']);frame[7]+=shift
            repositioned[inherited]=dict(definition=before['definition'],frame=frame,owners=before['owners'])
        interfaces[prefix]=dict(bracket=prefix+'Bracket',upper_mm=list(pose.Base),band_width_mm=width,
            band_center_y_mm=row['frame'][7],support_axial_shift_mm=shift,
            lower_mm=list(pose.multVec(V(*d['lower_eye_relative_mm']))),lower_bore_diameter_mm=c['lower_pin_diameter']+2*c['lower_bore_allowance'])
        placements=[('SuspensionLink','link',App.Placement()),('SuspensionPin','pin',App.Placement())]
        placements += [('SuspensionCotter'+str(i),'cotter',App.Placement(V(0,y,0),App.Rotation()))
            for i,y in enumerate([-d['cotter_y_mm'],d['cotter_y_mm']],1)]
        for suffix,key,local in placements:
            name=prefix+suffix;obj=doc.addObject('App::Link',name);owner.addObject(obj);obj.setLink(defs[key])
            world=pose.multiply(local);obj.LinkPlacement=owner.getGlobalPlacement().inverse().multiply(world)
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecords=records[key])
            expected[name]=dict(definition=defs[key].Name,frame=list(world.toMatrix().A),owners=row['owners'])
            added_children.setdefault(owner.Name,[]).append(name)
doc.Root.Label='Powertrain development — brake suspension links and individual pivots'
doc.Root.RegistrationStatus='Four M337 links retained at transversely repositioned M338 brackets; four separate M339 pins are a source-selection hypothesis. Band anchor brackets and lower fastening pending.'
doc.Definitions.Visibility=False;doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert len(expected)==16 and sha(source)==r['native_sha256'] and all(sha(ROOT/f)==v for f,v in inputs.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in locked:shutil.copy2(f,frozen/str(f.resolve().relative_to(ROOT)).replace('/','__'))
folder=out/'new_shapes';folder.mkdir()
for key,s in shapes.items():s.exportBrep(str(folder/('Def_BrakeLink_'+key+'.brep')))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=inputs,controls=c,dimensions=d,cotter=cotter,interfaces=interfaces,
    changed_definitions=[],new_definitions=sorted('Def_BrakeLink_'+k for k in shapes),new_assemblies=[],
    expected_new_occurrences=expected,expected_repositioned_occurrences=repositioned,assembly_shifts_mm=assembly_shifts,
    added_children=added_children,affected_occurrences=sorted(set(expected)|set(repositioned)),
    expected_physical_occurrences=len(rows)+16,expected_definition_count=len(m['definitions'])+3,expected_assembly_count=len(m['assemblies']),
    historical_geometry_qualified=False,installation_qualified=False,lower_attachment_pending=True,standard_assembly_modified=False))
print('Saved',len(rows)+16,'physical occurrences; lower pivot distance',d['pin_center_distance_mm'],flush=True)
