"""Bind completed clutch-drive receipts; never infer completion of the tank."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3];STAGE=HERE.parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_drive_build')
a=p.parse_args();out=a.candidate.resolve()
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=read(out/'report.json');native=out/'TransmissionWithClutchDrive.FCStd'
assert sha(native)==r['native_sha256'] and r['native_occurrences']==1520 and r['new_physical_occurrences']==30
assert r['material_passed'] and r['standard_context_checked']
assert sha(HERE/'air_pump_mount_build/TransmissionWithAirPump.FCStd')==r['parent_native_sha256']
for rel,h in r['input_hashes'].items():assert sha(REPO/rel)==h,rel
dossier=read(HERE/'clutch_drive_sources.json')
assert sha(REPO/'cad/001_Survey/mark_viii_parts.sqlite')==dossier['survey_sha256']
for rel,h in dossier['source_assets'].items():assert sha(REPO/rel)==h,rel
for rel,h in r['standard_native_hashes'].items():assert sha(STAGE/'build'/rel)==h,rel
for name,key in [('ClutchDriveInstallation.step','step_sha256'),('ClutchDriveDefinitions.step','definition_step_sha256')]:assert sha(out/name)==r[key]
receipt_names=['material_checks.json','independent_checks.json','exchange_checks.json','assembly_exchange_checks.json','variants/report.json','visual_review.json']
receipts={name:read(out/name) for name in receipt_names}
for name,receipt in receipts.items():
    assert receipt['passed'] and receipt['native_sha256']==r['native_sha256'],name
    if 'checks' in receipt:assert all(row['passed'] for row in receipt['checks']),name
assert len(receipts['independent_checks.json']['checks'])==148
assert len(receipts['exchange_checks.json']['checks'])==22
assert len(receipts['assembly_exchange_checks.json']['checks'])==114
assert len(receipts['variants/report.json']['scenarios'])==2
for name in ['independent_checks.json','exchange_checks.json','assembly_exchange_checks.json']:
    assert receipts[name]['checker_sha256']==sha(HERE/'check_clutch_drive.py'),name
assert receipts['variants/report.json']['checker_sha256']==sha(HERE/'check_clutch_drive_variants.py')
source=read(out/'source_review/render_receipt.json')
assert source['native_sha256']==r['native_sha256'] and source['renderer_sha256']==sha(HERE/'render_clutch_drive_review.py')
for rel,h in source['input_hashes'].items():assert sha(REPO/rel)==h,rel
for name,h in source['output_hashes'].items():assert sha(out/'source_review'/name)==h,name
for name,h in receipts['visual_review.json']['image_hashes'].items():assert sha(out/name)==h,name
for name,h in r['render_hashes'].items():assert sha(out/'previews'/name)==h,name
with zipfile.ZipFile(native) as archive:xml=ET.fromstring(archive.read('Document.xml'))
links=[dict(x.attrib) for x in xml.iter('XLink')]
external=[x for x in links if x.get('file','')]
assert not external,external
# Preserve all previously committed progression PNGs, including the user's
# original misspelled filenames; do not include new files in this baseline.
tree=subprocess.check_output(['git','ls-tree','-r','-z','HEAD','--','cad'],cwd=REPO)
preserved=[]
for entry in tree.split(b'\0'):
    if not entry:continue
    meta,path=entry.split(b'\t',1);path=path.decode();oid=meta.decode().split()[2]
    if path.startswith('cad/intermediate_') and path.endswith('.png'):
        data=(REPO/path).read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert actual==oid,path;preserved.append(dict(path=path,sha256=sha(REPO/path),git_blob=oid))
assert len(preserved)>=66
result=dict(passed=True,status='checked_approximate_clutch_stop_drive_for_front_clutch_development',
    native_sha256=r['native_sha256'],native_occurrences=1520,new_physical_occurrences=30,
    accepted_for_front_clutch_development=True,complete_clutch=False,complete_installation=False,
    integrated_in_standard_tank=False,historical_fit_qualified=False,individual_belt_link_inventory_known=False,complete_tank=False,
    native_external_file_references=external,standard_native_hashes=r['standard_native_hashes'],
    source_dossier_sha256=sha(HERE/'clutch_drive_sources.json'),input_hashes=r['input_hashes'],
    receipt_hashes={name:sha(out/name) for name in receipt_names+['report.json','source_review/render_receipt.json']},
    step_sha256=r['step_sha256'],definition_step_sha256=r['definition_step_sha256'],
    preserved_progression_images=preserved,qualifier_sha256=sha(Path(__file__)),
    remaining=['Main compound clutch, front coupling/spring and brake band','Filleted shaft shoulder and exact hidden casting contours',
        'Pump air connections and proprietary belt link inventory','B6205/MX1 supports, brakes, lubrication, long controls and standard integration'])
(out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS:1520-leaf drive checkpoint qualified for continued reconstruction; full tank incomplete.')
