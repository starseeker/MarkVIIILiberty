from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as E
root=Path('/home/cyapp/MarkVIIILiberty');a=root/'cad/003_FullTank/experiments/drive_chains/engine_water_pump_passage_study';b=root/'.work/engine-water-pump-passage/fresh_nominal'
read=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
properties={'Placement','LinkPlacement','LinkTransform','Scale','ScaleVector','LinkedObject','Group','Tip','Label','Label2','OccurrenceId','DefinitionId','SurveyIds','SourceRecord','Coverage','Representation','Subsystem','QuantityRole'}
def data(path):
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  xml=E.fromstring(z.read('Document.xml'))
  shapes={o.get('name'):sha(z.read(p.get('file'))) for o in xml.findall('./ObjectData/Object') for p in o.findall('./Properties/Property[@name="Shape"]/Part') if p.get('file')}
  state={(o.get('name'),p.get('name')):E.tostring(p).decode() for o in xml.findall('./ObjectData/Object') for p in o.findall('./Properties/Property') if p.get('name') in properties}
  types={o.get('name'):o.get('type') for o in xml.findall('./Objects/Object')}
  return shapes,state,types
ra,rb=read(a/'report.json'),read(b/'report.json');pa,pb=a/ra['native_file'],b/rb['native_file']
assert sha(pa.read_bytes())==ra['native_sha256'] and sha(pb.read_bytes())==rb['native_sha256']
da,db=data(pa),data(pb)
checks=dict(input_hashes_identical=ra['input_hashes']==rb['input_hashes'],parent_native_identical=ra['parent_native_sha256']==rb['parent_native_sha256'],serialized_geometry_identical=da[0]==db[0],placement_hierarchy_identity_and_metadata_identical=da[1]==db[1],object_types_identical=da[2]==db[2],physical_count=ra['native_occurrences']==rb['native_occurrences']==2246)
result=dict(passed=all(checks.values()),checks=checks,candidate_native_sha256=ra['native_sha256'],fresh_native_sha256=rb['native_sha256'],serialized_shapes=len(da[0]),checked_properties=len(da[1]),scope='Independent empty-output rebuild; exact serialized BRep, all object types, placement/link/hierarchy/identity metadata and frozen inputs compared. Fresh builder also saved/reopened2246 occurrences; nominal native acceptance applies through these identical geometry/assembly data.')
(a/'reproduction_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));assert result['passed']
