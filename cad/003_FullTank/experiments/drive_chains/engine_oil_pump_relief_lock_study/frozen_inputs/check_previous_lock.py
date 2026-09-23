from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as ET
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains';old=h/'engine_oil_pump_hardware_study';new=h/'engine_oil_pump_relief_lock_study'
props={'Placement','LinkPlacement','LinkTransform','Scale','ScaleVector','LinkedObject','Tip','Label','Label2','DefinitionKey','PhysicalRole','SourcePartMark','SourceRecords','RepresentationNote'}
def data(base):
    r=json.loads((base/'report.json').read_text());native=base/r['native_file'];assert hashlib.sha256(native.read_bytes()).hexdigest()==r['native_sha256']
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None;xml=ET.fromstring(z.read('Document.xml'))
        shapes={o.get('name'):hashlib.sha256(z.read(p.get('file'))).hexdigest() for o in xml.findall('./ObjectData/Object') for p in o.findall('./Properties/Property[@name="Shape"]/Part') if p.get('file')}
        state={(o.get('name'),p.get('name')):ET.tostring(p).decode() for o in xml.findall('./ObjectData/Object') for p in o.findall('./Properties/Property') if p.get('name') in props}
        types={o.get('name'):o.get('type') for o in xml.findall('./Objects/Object')};allowed=set()
        for key in ['lower_body','relief_cage']:
            name='Def_'+key;obj=xml.find('./ObjectData/Object[@name="'+name+'"]');allowed|={name,obj.find('./Properties/Property[@name="Tip"]/Link').get('value')}
        groups={o.get('name'):[i.get('value') for i in o.findall('./Properties/Property[@name="Group"]/LinkList/Link')] for o in xml.findall('./ObjectData/Object') if o.find('./Properties/Property[@name="Group"]') is not None}
    return r,shapes,state,types,allowed,groups
a,b=data(old),data(new);changed=[k for k,v in a[1].items() if b[1].get(k)!=v];new_shapes=sorted(b[1].keys()-a[1].keys());frame_changes=[k for k,v in a[2].items() if b[2].get(k)!=v]
group_failures=[]
for name,values in a[5].items():
    now=b[5].get(name)
    if name in ['Definitions','EngineOilPumpRelief']:
        if now is None or not set(values).issubset(now):group_failures.append(name)
    elif now!=values:group_failures.append(name)
checks=dict(only_lower_casting_and_relief_cage_changed=set(changed).issubset(a[4]) and 'Def_lower_body' in changed,old_shapes_preserved=set(a[1]).issubset(b[1]),one_wire_and_one_reference_added=len(new_shapes)==3,existing_frames_and_identity_unchanged=not frame_changes,old_types_preserved=all(b[3].get(k)==v for k,v in a[3].items()),groups_preserved=not group_failures,physical_counts=a[0]['physical_count']==104 and b[0]['physical_count']==105)
result=dict(passed=all(checks.values()),checks=checks,changed_serialized_shapes=changed,unchanged_serialized_shapes=len(a[1])-len(changed),new_serialized_shapes=new_shapes,checked_properties=len(a[2]),frame_changes=frame_changes,group_failures=group_failures,previous_native_sha256=a[0]['native_sha256'],native_sha256=b[0]['native_sha256'])
(new/'previous_checkpoint_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed']
