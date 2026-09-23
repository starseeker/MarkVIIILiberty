"""Require unchanged serialized geometry and assembly properties outside the body."""
from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as ET
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains'
old=h/'engine_water_pump_mounting_study';new=h/'engine_water_pump_passage_study'
properties={'Placement','LinkPlacement','LinkTransform','Scale','ScaleVector','LinkedObject','Group','Tip','Label','Label2','OccurrenceId','DefinitionId','SurveyIds','SourceRecord','Coverage','Representation','Subsystem','QuantityRole'}
def data(base):
    r=json.loads((base/'report.json').read_text());p=base/r['native_file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==r['native_sha256']
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        xml=ET.fromstring(z.read('Document.xml'))
        shapes={o.get('name'):hashlib.sha256(z.read(p.get('file'))).hexdigest() for o in xml.findall('./ObjectData/Object') for p in o.findall('./Properties/Property[@name="Shape"]/Part') if p.get('file')}
        state={(o.get('name'),p.get('name')):ET.tostring(p).decode() for o in xml.findall('./ObjectData/Object') for p in o.findall('./Properties/Property') if p.get('name') in properties}
        body=xml.find('./ObjectData/Object[@name="'+r['definitions']['body']+'"]')
        tip=body.find('./Properties/Property[@name="Tip"]/Link').get('value')
        types={o.get('name'):o.get('type') for o in xml.findall('./Objects/Object')}
    return r,shapes,state,types,{r['definitions']['body'],tip}
a,b=data(old),data(new);changed=sorted(k for k in a[1] if a[1][k]!=b[1].get(k))
checks=dict(shape_inventory_preserved=a[1].keys()==b[1].keys(),only_pump_body_changed=set(changed)==a[4]==b[4],
    assembly_metadata_and_frames_identical=a[2]==b[2],object_types_identical=a[3]==b[3],controls_identical=a[0]['controls']==b[0]['controls'],
    derived_datums_identical=a[0]['datums']==b[0]['datums'],physical_count=a[0]['native_occurrences']==b[0]['native_occurrences']==2246)
result=dict(passed=all(checks.values()),checks=checks,changed_serialized_shapes=changed,unchanged_serialized_shapes=len(a[1])-len(changed),
    checked_properties=len(a[2]),previous_native_sha256=a[0]['native_sha256'],native_sha256=b[0]['native_sha256'])
(new/'previous_checkpoint_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed']
