"""Saved identities and installed counts, including reused upper/lower hardware."""
import argparse,json,sys,zipfile
import xml.etree.ElementTree as E
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
source=H/'transmission_high_brake_support_study/sources.json';s=read(source);records={v['record_id']:v for v in s['source_records']}
with zipfile.ZipFile(native) as z:xml=E.fromstring(z.read('Document.xml'))
props={o.get('name'):{v.get('name'):v.find('String').get('value') for v in o.findall('Properties/Property') if v.find('String') is not None} for o in xml.findall('ObjectData/Object')}
checks=[]
specs=[('Def_HighBrakeUpper_top_stop','M399','SNL:223:005',2),('Def_HighBrakeUpper_back_stop','M398','SNL:223:003',2),('Def_HighBrakeUpper_clip','M365','SNL:66:022',2),('Def_HighBrakeSupport_mount_screw','MX60','SNL:205:006',8),('Def_HighBrakeStops_stop_screw','M400','SNL:205:022',6),('Def_HighBrakeStops_stop_nut','','SNL:205:023',6)]
for key,mark,record,count in specs:
 actual=props[key];occ=[v['name'] for v in m['occurrences'] if v['definition']==key]
 passed=actual['SourcePartMark']==mark and json.loads(actual['SourceRecords'])==[record] and json.loads(actual['SurveyIds'])==records[record]['part_ids'] and len(occ)==count
 checks.append(dict(definition=key,record=record,source_description=records[record]['description'],part_ids=records[record]['part_ids'],occurrences=occ,passed=passed))
key='Def_HighBrakeSupport_anchor_lock_plate';actual=props[key];occ=[v['name'] for v in m['occurrences'] if v['definition']==key]
checks.append(dict(role='Four MX61 common plates share one definition without invented Survey ID',passed=actual['SourcePartMark']=='MX61' and not json.loads(actual['SourceRecords']) and not json.loads(actual['SurveyIds']) and len(occ)==4))
physical_ids={pid for v in m['occurrences'] for pid in json.loads(props[v['definition']].get('SurveyIds','[]'))}
for suffix in ['BottomStopSetScrewAssembly1','BottomStopSetScrewAssembly2','UpperStopSetScrewAssembly']:
 for hand in ['Port','Starboard']:
  name=hand+'HighSpeedBrake'+suffix;actual=props[name];ids=records['SNL:205:020']['part_ids']
  passed=json.loads(actual['SourceRecords'])==['SNL:205:020'] and json.loads(actual['SurveyIds'])==ids and not set(ids)&physical_ids and len(m['assemblies'][name]['children'])==2
  checks.append(dict(assembly=name,record='SNL:205:020',aggregate_ids=ids,passed=passed))
write(out/'catalogue_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),sources_sha256=sha(source),checker_sha256=sha(Path(__file__)),scope='M399/M398/M365 quantities and identities, all six M400/nut pairs and four shared MX61 plates. Eight of catalogue ten MX60 screws located; two remain unallocated. Handbook plates and later SNL individual washers remain separate alternatives.',inventory_complete=False))
print('Saved upper catalogue checks',len(checks),'passed',all(v['passed'] for v in checks));assert all(v['passed'] for v in checks)
