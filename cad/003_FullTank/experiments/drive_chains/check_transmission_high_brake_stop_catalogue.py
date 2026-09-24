"""Read source identities from the saved FCStd; keep assembly totals out of leaves."""
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
for role,mark,record,count in [('anchor_pin','M363','SNL:137:003',2),('anchor_cotter','','SNL:137:004',2),('bottom_stop','M366','SNL:223:004',2),('mount_screw','MX76','SNL:205:009',4),('stop_screw','M400','SNL:205:022',4),('stop_nut','','SNL:205:023',4)]:
 key='Def_HighBrakeStops_'+role;actual=props[key];occ=[v['name'] for v in m['occurrences'] if v['definition']==key]
 passed=actual['SourcePartMark']==mark and json.loads(actual['SourceRecords'])==[record] and json.loads(actual['SurveyIds'])==records[record]['part_ids'] and len(occ)==count
 checks.append(dict(role=role,record=record,source_description=records[record]['description'],part_ids=records[record]['part_ids'],occurrences=occ,passed=passed))
actual=props['Def_HighBrakeStops_bottom_lock_plate'];occ=[v['name'] for v in m['occurrences'] if v['definition']=='Def_HighBrakeStops_bottom_lock_plate']
checks.append(dict(role='MX77 common locking plate without invented Survey ID',passed=actual['SourcePartMark']=='MX77' and not json.loads(actual['SourceRecords']) and not json.loads(actual['SurveyIds']) and len(occ)==2))
for suffix,record,children in [('AnchorPinAssembly','SNL:137:001',2),('BottomStopSetScrewAssembly1','SNL:205:020',2),('BottomStopSetScrewAssembly2','SNL:205:020',2)]:
 for hand in ['Port','Starboard']:
  name=hand+'HighSpeedBrake'+suffix;actual=props[name];ids=records[record]['part_ids']
  physical_ids={pid for v in m['occurrences'] for pid in json.loads(props[v['definition']].get('SurveyIds','[]'))}
  passed=json.loads(actual['SourceRecords'])==[record] and json.loads(actual['SurveyIds'])==ids and not set(ids)&physical_ids and len(m['assemblies'][name]['children'])==children
  checks.append(dict(assembly=name,record=record,aggregate_ids=ids,passed=passed))
write(out/'catalogue_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),sources_sha256=sha(source),checker_sha256=sha(Path(__file__)),scope='Saved source identities and partial installed counts. Four of six M400/nut pairs installed; two upper pairs remain. MX77 unaliased handbook plate is not silently assigned a later lock-washer identity.',inventory_complete=False))
print('Saved catalogue checks',len(checks),'passed',all(v['passed'] for v in checks));assert all(v['passed'] for v in checks)
