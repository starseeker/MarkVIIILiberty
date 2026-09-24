"""Check source identities on physical definitions and shared nut occurrences."""
import argparse,json,sys,zipfile
import xml.etree.ElementTree as E
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
s=read(H/'transmission_controls_study/sources.json');records={v['record_id']:v for v in s['source_records']}
with zipfile.ZipFile(native) as z:xml=E.fromstring(z.read('Document.xml'))
props={o.get('name'):{v.get('name'):v.find('String').get('value') for v in o.findall('Properties/Property') if v.find('String') is not None} for o in xml.findall('ObjectData/Object')}
checks=[]
for role,mark,record in [('fork','M569B','SNL:87:003'),('pin','M568A','SNL:136:007'),('cotter','1/8 x 1 inch split pin','SNL:136:008')]:
    key='Def_ControlJoint_'+role;actual=props[key];occ=[v['name'] for v in m['occurrences'] if v['definition']==key]
    checks.append(dict(role=role,record=record,occurrences=occ,passed=len(occ)==2 and actual['SourcePartMark']==mark and json.loads(actual['SourceRecords'])==[record] and json.loads(actual['SurveyIds'])==records[record]['part_ids']))
for hand in ['Port','Starboard']:
    name=hand+'HighSpeedBrakeControlNut';v=next(v for v in m['occurrences'] if v['name']==name)
    checks.append(dict(occurrence=name,passed=v['definition']=='Def_ClutchBrake_rod_nut' and json.loads(props[name]['SourceRecords'])==['SNL:195:008']))
    group=hand+'HighSpeedBrakeControlJoint'
    checks.append(dict(assembly=group,passed=len(m['assemblies'][group]['children'])==4 and not json.loads(props[group].get('SurveyIds','[]'))))
aggregate=set(records['SNL:195:005']['part_ids']);physical={pid for v in m['occurrences'] for pid in json.loads(props[v['definition']].get('SurveyIds','[]'))}
checks.append(dict(name='Incomplete M575 rod aggregate not counted as an added physical part',passed=not physical&aggregate))
write(out/'catalogue_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),sources_sha256=sha(H/'transmission_controls_study/sources.json'),checker_sha256=sha(Path(__file__)),
    limits=['Two M569B forks assigned to the two brake ends as a documented hypothesis.','Two remaining M575 plain nuts belong to future forward joints; full rod assemblies remain incomplete.','M568A1⅝-inch component length selected;1⅞-inch aggregate conflict remains open.']))
print(len(checks),'catalogue checks passed',all(v['passed'] for v in checks));assert all(v['passed'] for v in checks)
