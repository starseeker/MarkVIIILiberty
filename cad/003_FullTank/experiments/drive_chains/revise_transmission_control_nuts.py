"""Replace the two provisional control nuts with a separate classic U.S. form."""
import argparse,math,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.cad_build import metadata
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_controls_study';parent=packet/'integrated01';r=read(parent/'report.json');q=read(parent/'qualification.json');source=parent/r['native_file'];assert q['local_static_checks_passed'] and sha(source)==q['native_sha256']
review=read(packet/'us_standard_nut_review.json');c=review['selected_controls'];radius=c['across_flats_mm']/math.sqrt(3)
pts=[App.Vector(radius*math.cos(math.radians(i*60)),radius*math.sin(math.radians(i*60)),0) for i in range(6)]
nut=Part.Face(Part.makePolygon(pts+pts[:1])).extrude(App.Vector(0,0,c['height_mm']))
nut=nut.cut(Part.makeCylinder(c['nominal_diameter_mm']/2+c['bore_radial_allowance_mm'],c['height_mm']+2,App.Vector(0,0,-1)))
assert nut.isValid() and len(nut.Solids)==1 and nut.Solids[0].isClosed();nut.exportBrep(str(out/'us_standard_nut.brep'))
doc=App.openDocument(str(source));body=doc.addObject('PartDesign::Body','Def_USStdControlNut');doc.Definitions.addObject(body);body.newObject('PartDesign::Feature','ClassicUSStandardNut').Shape=nut
records=read(packet/'sources.json')['source_records'];ids=next(v['part_ids'] for v in records if v['record_id']=='SNL:195:008')
metadata(body,DefinitionKey='us_standard_3_4_plain_nut',SourcePartMark='3/4 inch U.S. Standard plain nut',SourceRecords=['SNL:195:008'],SurveyIds=ids,Representation='assembly',Coverage='reconstruction_trial',
    ParameterUpdate='Regenerate with revise_transmission_control_nuts.py',ReconstructionStatus='Classic U.S. Standard forged/unfinished envelope; finish applicability remains inferred.',ThreadDescription='Nominal3/4inch10TPI U.S. Standard; cylindrical envelope without thread helix.')
affected=[]
for hand in ['Port','Starboard']:
    link=doc.getObject(hand+'HighSpeedBrakeControlNut');before=link.LinkPlacement;link.setLink(body);assert link.LinkPlacement==before;affected.append(link.Name)
doc.Root.RegistrationStatus='Rear high-speed control joints with separate classic U.S. Standard nuts. Finish and fork/pin datums remain estimates; rods, channel and springs remain pending.'
doc.Definitions.Visibility=False;doc.recompute();native=out/'PowertrainWithUSControlNuts.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
inputs=[Path(__file__),packet/'us_standard_nut_review.json',packet/'sources.json',parent/'qualification.json',parent/'report.json',parent/'isolated/manifest.json',STAGE/'lib/cad_build.py']
frozen=out/'frozen_inputs';frozen.mkdir()
for f in inputs:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),source_native_sha256=sha(source),controls=c,
    input_hashes={str(f.relative_to(ROOT)):sha(f) for f in inputs},new_definitions=['Def_USStdControlNut'],changed_definitions=[],affected_occurrences=affected,
    changed_occurrence_definitions={n:'Def_USStdControlNut' for n in affected},added_children={'Definitions':['Def_USStdControlNut']},
    expected_physical_occurrences=3173,expected_definition_count=546,expected_assembly_count=338,historical_geometry_qualified=False,installation_qualified=False,standard_assembly_modified=False,packet_complete=False))
assert sha(source)==q['native_sha256'];print('Saved source-led nut revision:3173 occurrences /546 definitions /338 assemblies.',flush=True)
