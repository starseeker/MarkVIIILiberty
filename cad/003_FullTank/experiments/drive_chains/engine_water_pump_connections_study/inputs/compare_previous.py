"""Preserve existing assembly frames and all geometry outside three pump parts."""
from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as ET
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains'
old=h/'engine_water_pump_passage_study';new=h/'engine_water_pump_connections_study'
frame_properties={'Placement','LinkPlacement','LinkTransform','Scale','ScaleVector','LinkedObject','Tip','Label','Label2','OccurrenceId','DefinitionId','Representation','Subsystem','QuantityRole'}
def data(base):
 r=json.loads((base/'report.json').read_text());p=base/r['native_file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['native_sha256']
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None;xml=ET.fromstring(z.read('Document.xml'))
  shapes={o.get('name'):hashlib.sha256(z.read(p.get('file'))).hexdigest() for o in xml.findall('./ObjectData/Object') for p in o.findall('./Properties/Property[@name="Shape"]/Part') if p.get('file')}
  state={(o.get('name'),p.get('name')):ET.tostring(p).decode() for o in xml.findall('./ObjectData/Object') for p in o.findall('./Properties/Property') if p.get('name') in frame_properties}
  types={o.get('name'):o.get('type') for o in xml.findall('./Objects/Object')};allow=set();groups={o.get('name'):[i.get('value') for i in o.findall('./Properties/Property[@name="Group"]/LinkList/Link')] for o in xml.findall('./ObjectData/Object') if o.find('./Properties/Property[@name="Group"]') is not None}
  for key in ['body','cover','plug']:
   name=r['definitions'][key];obj=xml.find('./ObjectData/Object[@name="'+name+'"]');allow|={name,obj.find('./Properties/Property[@name="Tip"]/Link').get('value')}
 return r,shapes,state,types,allow,groups
x,y=data(old),data(new);changed=sorted(k for k in x[1] if x[1][k]!=y[1].get(k));new_shapes=sorted(y[1].keys()-x[1].keys())
frame_changes=[k for k,v in x[2].items() if y[2].get(k)!=v];group_failures=[]
for key,values in x[5].items():
 now=y[5].get(key)
 if key in ['Definitions','EngineWaterPumpBodyAssembly']:
  if now is None or not set(values).issubset(now):group_failures.append(key)
 elif now!=values:group_failures.append(key)
checks=dict(all_old_shapes_retained=set(x[1]).issubset(y[1]),only_body_cover_and_plug_changed=set(changed)==x[4]==y[4],three_new_serialized_shapes=len(new_shapes)==3,
 existing_frames_and_identity_properties_identical=not frame_changes,existing_groups_retained_with_only_expected_additions=not group_failures,
 existing_object_types_retained=all(y[3].get(k)==v for k,v in x[3].items()),one_new_physical_occurrence=x[0]['native_occurrences']==2246 and y[0]['native_occurrences']==2247)
result=dict(passed=all(checks.values()),checks=checks,changed_serialized_shapes=changed,new_serialized_shapes=new_shapes,unchanged_serialized_shapes=len(x[1])-len(changed),checked_properties=len(x[2]),frame_changes=frame_changes,group_failures=group_failures,previous_native_sha256=x[0]['native_sha256'],native_sha256=y[0]['native_sha256'])
(new/'previous_checkpoint_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed']
