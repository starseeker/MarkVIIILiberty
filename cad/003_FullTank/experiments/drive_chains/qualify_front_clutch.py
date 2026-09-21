"""Bind the reviewed front-clutch checkpoint without claiming tank completion."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3];STAGE=HERE.parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'front_clutch_build')
a=p.parse_args();out=a.candidate.resolve()
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=read(out/'report.json');native=out/'TransmissionWithFrontClutch.FCStd'
assert sha(native)==r['native_sha256'] and r['native_occurrences']==1530 and r['new_physical_occurrences']==10
assert r['unchanged_parent_occurrences']==1518 and r['material_passed'] and r['standard_context_checked']
assert sha(HERE/'clutch_drive_build/TransmissionWithClutchDrive.FCStd')==r['parent_native_sha256']
for rel,h in r['input_hashes'].items():assert sha(REPO/rel)==h,rel
dossier=read(HERE/'front_clutch_sources.json')
assert sha(REPO/'cad/001_Survey/mark_viii_parts.sqlite')==dossier['survey_sha256']
for rel,h in dossier['source_assets'].items():assert sha(REPO/rel)==h,rel
for rel,h in r['standard_native_hashes'].items():assert sha(STAGE/'build'/rel)==h,rel
for name,key in [('FrontClutchInstallation.step','step_sha256'),('FrontClutchDefinitions.step','definition_step_sha256'),('spring_spine.brep','spring_spine_sha256')]:assert sha(out/name)==r[key]
names=['material_checks.json','independent_checks.json','exchange_checks.json','assembly_exchange_checks.json','variants/report.json','visual_review.json','source_review/identity_review.json']
receipts={name:read(out/name) for name in names}
for name,receipt in receipts.items():
    assert receipt['passed'] and receipt['native_sha256']==r['native_sha256'],name
    if 'checks' in receipt:assert all(row['passed'] for row in receipt['checks']),name
assert len(receipts['independent_checks.json']['checks'])==70
assert len(receipts['exchange_checks.json']['checks'])==8
assert len(receipts['assembly_exchange_checks.json']['checks'])==12
assert len(receipts['variants/report.json']['scenarios'])==2
assert all(s['passed'] for s in receipts['variants/report.json']['scenarios'])
assert receipts['variants/report.json']['alternate_reading']['expected_interference_detected']
assert receipts['variants/report.json']['parts_sha256']==sha(HERE/'front_clutch_parts.py')
for name in ['independent_checks.json','exchange_checks.json','assembly_exchange_checks.json']:
    assert receipts[name]['checker_sha256']==sha(HERE/'check_front_clutch.py'),name
assert receipts['variants/report.json']['checker_sha256']==sha(HERE/'check_front_clutch_variants.py')
source=read(out/'source_review/render_receipt.json')
identity=receipts['source_review/identity_review.json']
assert identity['survey_sha256']==dossier['survey_sha256']
for rel,h in identity['source_hashes'].items():assert sha(REPO/rel)==h,rel
assert source['native_sha256']==r['native_sha256'] and source['renderer_sha256']==sha(HERE/'render_front_clutch_review.py')
for rel,h in source['input_hashes'].items():assert sha(REPO/rel)==h,rel
for name,h in source['output_hashes'].items():assert sha(out/'source_review'/name)==h,name
for name,h in receipts['visual_review.json']['image_hashes'].items():assert sha(out/name)==h,name
for name,h in r['render_hashes'].items():assert sha(out/'previews'/name)==h,name
with zipfile.ZipFile(native) as archive:xml=ET.fromstring(archive.read('Document.xml'))
links=[dict(x.attrib) for x in xml.iter('XLink')];external=[x for x in links if x.get('file','')]
assert not external,external
tree=subprocess.check_output(['git','ls-tree','-r','-z','HEAD','--','cad'],cwd=REPO)
preserved=[]
for entry in tree.split(b'\0'):
    if not entry:continue
    meta,path=entry.split(b'\t',1);path=path.decode();oid=meta.decode().split()[2]
    if path.startswith('cad/intermediate_') and path.endswith('.png'):
        data=(REPO/path).read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert actual==oid,path;preserved.append(dict(path=path,sha256=sha(REPO/path),git_blob=oid))
assert len(preserved)>=69
result=dict(passed=True,status='checked_approximate_front_coupling_and_external_spring',
    native_sha256=r['native_sha256'],native_occurrences=1530,new_physical_occurrences=10,
    accepted_for_main_clutch_development=True,complete_clutch=False,complete_installation=False,
    integrated_in_standard_tank=False,historical_fit_qualified=False,spring_load_qualified=False,complete_tank=False,
    native_external_file_references=external,standard_native_hashes=r['standard_native_hashes'],
    source_dossier_sha256=sha(HERE/'front_clutch_sources.json'),input_hashes=r['input_hashes'],
    receipt_hashes={name:sha(out/name) for name in names+['report.json','source_review/render_receipt.json']},
    step_sha256=r['step_sha256'],definition_step_sha256=r['definition_step_sha256'],
    preserved_progression_images=preserved,qualifier_sha256=sha(Path(__file__)),
    remaining=['SH999A collar and its fastening joint, main clutch cones, bearings, spring plungers and brake band',
        'Unproven HB-to-SNL coupling dimension transfer; spring diameter and installed-length conventions',
        'Exact hidden cast profiles, thread and clamp-load details',
        'Pump air connections, B6205/MX1 supports, brakes, lubrication, long controls and standard integration'])
(out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS:1530-leaf checkpoint ready for main clutch development; full tank incomplete.')
