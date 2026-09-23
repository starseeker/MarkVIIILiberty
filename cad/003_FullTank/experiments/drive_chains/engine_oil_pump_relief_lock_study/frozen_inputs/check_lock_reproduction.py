from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as E
root=Path('/home/cyapp/MarkVIIILiberty');a=root/'cad/003_FullTank/experiments/drive_chains/engine_oil_pump_relief_lock_study';b=root/'.work/engine-oil-pump/relief_lock_reproduction'
sha=lambda x:hashlib.sha256(x).hexdigest()
def data(folder):
 r=json.loads((folder/'report.json').read_text());f=folder/r['native_file'];assert sha(f.read_bytes())==r['native_sha256']
 with zipfile.ZipFile(f) as z:
  assert z.testzip() is None;t=E.fromstring(z.read('Document.xml'));objects=t.findall('./ObjectData/Object')
  shapes={o.get('name'):sha(z.read(p.get('file'))) for o in objects for p in o.findall('./Properties/Property[@name="Shape"]/Part') if p.get('file')}
  state={(o.get('name'),p.get('name')):E.tostring(p).decode() for o in objects for p in o.findall('./Properties/Property') if p.get('name')!='Uid'}
  types={o.get('name'):o.get('type') for o in t.findall('./Objects/Object')}
 return r,shapes,state,types
x,y=data(a),data(b);changes=[k for k,v in x[2].items() if y[2].get(k)!=v]
checks=dict(identical_inputs=x[0]['input_hashes']==y[0]['input_hashes'],identical_serialized_shapes=x[1]==y[1],identical_object_properties=x[2]==y[2],identical_types=x[3]==y[3],physical_counts=x[0]['physical_count']==y[0]['physical_count']==105,identical_controls_and_datums=x[0]['controls']==y[0]['controls'] and x[0]['datums']==y[0]['datums'])
result=dict(passed=all(checks.values()),checks=checks,serialized_shapes=len(x[1]),object_properties=len(x[2]),objects=len(x[3]),excluded_properties=['Uid (new document object UUIDs)'],changed_properties=changes,candidate_native_sha256=x[0]['native_sha256'],fresh_native_sha256=y[0]['native_sha256'])
(a/'reproduction_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed']
