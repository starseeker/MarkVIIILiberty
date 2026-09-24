"""Fresh four-part generator replay; permit only new assembly UUID differences."""
import argparse,hashlib,json,uuid,zipfile
import xml.etree.ElementTree as E
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--reproduction',type=Path,required=True);a=p.parse_args()
folders=[a.candidate.resolve(),a.reproduction.resolve()];assert folders[0]!=folders[1]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
reports=[json.loads((f/'report.json').read_text()) for f in folders];archives=[];natives=[]
for folder,r in zip(folders,reports):
    native=folder/r['native_file'];assert sha(native)==r['native_sha256'];natives.append(native)
    with zipfile.ZipFile(native) as z:
        xml=E.fromstring(z.read('Document.xml'));breps={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.endswith('.brp')}
    types={o.get('name'):o.get('type') for o in xml.findall('Objects/Object')}
    props={(o.get('name'),v.get('name')):E.tostring(v) for o in xml.findall('ObjectData/Object') for v in o.findall('Properties/Property')}
    archives.append((breps,types,props))
left,right=archives;variable={(n,'Uid') for n,t in left[1].items() if t=='App::Part'}
assert {n for n,k in variable}=={'Root','Definitions','PortControlJoint','StarboardControlJoint'}
uuids=[]
for _,types,props in archives:
    values=[]
    for k in variable:
        elem=E.fromstring(props[k]);assert elem.get('type')=='App::PropertyUUID';value=elem.find('Uuid').get('value');assert str(uuid.UUID(value))==value.lower();values.append(value)
    assert len(set(values))==4;uuids.append(values)
changed={k for k in left[2] if left[2][k]!=right[2].get(k)}
checks={k:reports[0][k]==reports[1][k] for k in ['controls','details','joints','specs','input_hashes','parent_native_sha256','parent_qualification_sha256']}
checks.update(all_archive_breps_exact=left[0]==right[0],all_object_types_exact=left[1]==right[1],all_property_keys_exact=left[2].keys()==right[2].keys(),only_four_new_assembly_uuids_may_differ=changed<=variable,
              all_exported_definition_breps_exact=all(sha(folders[0]/(role+'.brep'))==sha(folders[1]/(role+'.brep')) for role in ['fork','pin','cotter','nut']))
record=dict(passed=all(checks.values()),checks=checks,native_sha256=sha(natives[0]),reproduction_native_sha256=sha(natives[1]),
    checker_sha256=sha(Path(__file__)),archive_brep_count=len(left[0]),persistent_property_count=len(left[2]),changed_property_keys=sorted(changed),new_assembly_uuids=uuids,
    scope='Fresh parameter-driven fork/pin/cotter construction and nut reuse. Every saved shape, frame, stable property and input must reproduce; only four newly generated assembly UUIDs may differ.')
(folders[0]/'generator_reproduction_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print('Fresh joint generator:',len(checks),'checks,',len(left[0]),'archive BReps;',record['passed']);assert record['passed']
