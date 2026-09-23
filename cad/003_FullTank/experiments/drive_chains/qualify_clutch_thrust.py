"""Bind saved geometry, source/visual review and repeat-build evidence for the thrust packet."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--candidate',type=Path,default=HERE/'clutch_thrust_build')
    out=parser.parse_args().candidate.resolve();native=out/'TransmissionWithClutchThrust.FCStd';nh=sha(native);r=read(out/'report.json')
    assert nh==r['native_sha256'] and r['native_occurrences']==1581
    assert len(r['new_ids'])==32 and len(r['affected_ids'])==33 and r['changed_ids']==['ClutchStack_thrust']
    assert len(set(r['affected_ids']))==33 and set(r['affected_ids'])==set(r['new_ids']+r['changed_ids'])
    assert r['unchanged_parent_occurrences']==1548 and r['headless'] and r['material_passed']
    assert not r['standard_assembly_modified'] and not r['complete_clutch'] and not r['complete_tank']
    parent=HERE/'clutch_stack_build';pq=read(parent/'qualification.json')
    assert pq['passed'] and pq['native_occurrences']==1549 and pq['accepted_for_main_clutch_development']
    assert sha(parent/'qualification.json')==r['parent_qualification_sha256']
    assert sha(parent/'TransmissionWithClutchStack.FCStd')==pq['native_sha256']==r['parent_native_sha256']
    for rel,h in r['input_hashes'].items():
        assert sha(ROOT/rel)==h and sha(out/'inputs'/Path(rel).name)==h,rel
    dossier=read(HERE/'clutch_thrust_sources.json')
    assert sha(ROOT/'cad/001_Survey/mark_viii_parts.sqlite')==dossier['survey_sha256']
    assert dossier['inventory']['new_physical']==32 and not dossier['inventory']['assembly_heading_is_extra_physical_part']
    for rel,h in dossier['source_assets'].items():assert sha(ROOT/rel)==h,rel
    assert len(r['standard_native_hashes'])==20
    for rel,h in r['standard_native_hashes'].items():assert sha(STAGE/'build'/rel)==h,rel
    artifacts={'ClutchThrustDefinitions.step':'definition_step_sha256','ClutchThrustInstallation.step':'step_sha256','inputs/parent_thrust.brep':'parent_thrust_sha256'}
    for rel,k in artifacts.items():assert sha(out/rel)==r[k],rel
    names=['material_checks.json','independent_checks.json','exchange_checks.json','assembly_exchange_checks.json',
           'variants/report.json','visual_review.json','source_review/render_receipt.json','reproduction.json']
    receipts={n:read(out/n) for n in names}
    for n,receipt in receipts.items():
        assert receipt['native_sha256']==nh,n
        if n!='source_review/render_receipt.json':assert receipt['passed'],n
        if 'checks' in receipt:assert all(x['passed'] for x in receipt['checks']),n
    material=receipts['material_checks.json'];assert material['standard_context_checked']
    assert len(material['pairs'])==r['material_pairs']==95
    assert all(abs(x['intersection_mm3'])<1e-5 for x in material['pairs'])
    for name,count in [('independent_checks.json',460),('exchange_checks.json',4),('assembly_exchange_checks.json',33)]:
        assert len(receipts[name]['checks'])==count
        assert receipts[name]['checker_sha256']==sha(HERE/'check_clutch_thrust.py')
    assert receipts['exchange_checks.json']['step_sha256']==r['definition_step_sha256']
    assert receipts['assembly_exchange_checks.json']['step_sha256']==r['step_sha256']
    assert len(read(out/'definition_order.json'))==4
    v=receipts['variants/report.json'];assert v['checker_sha256']==sha(HERE/'check_clutch_thrust_variants.py')
    assert v['parts_sha256']==sha(HERE/'clutch_thrust_parts.py') and v['standard_native_hashes']==r['standard_native_hashes']
    assert len(v['scenarios'])==2
    for name,summary in zip(['smaller','larger'],v['scenarios']):
        rel=f'variants/{name}.json';row=read(out/rel);names.append(rel)
        assert summary=={k:v for k,v in row.items() if k!='pairs'}
        assert row['passed'] and not row['overlaps'] and len(row['pairs'])==row['material_pairs']==95
        assert len(row['contacts'])==90 and all(x['passed'] for x in row['contacts'])
        assert row['controls']['ball_count']==30 and row['controls']['ball_diameter']==6.35
    render=receipts['source_review/render_receipt.json']
    assert render['renderer_sha256']==sha(HERE/'render_clutch_thrust_review.py')
    assert render['helper_sha256']==sha(HERE/'detail_render.py')
    assert render['base_renderer_sha256']==sha(STAGE/'lib/visual_review.py')
    assert render['source_sha256']==sha(ROOT/render['source_path'])
    for name,h in render['image_hashes'].items():assert sha(out/'source_review'/name)==h,name
    visual=receipts['visual_review.json'];assert len(visual['image_hashes'])==7
    assert visual['image_hashes']==render['image_hashes'] and visual['source_render_receipt_sha256']==sha(out/'source_review/render_receipt.json')
    for name,h in r['render_hashes'].items():assert sha(out/'previews'/name)==h,name
    rebuild=receipts['reproduction.json'];assert rebuild['builder_sha256']==sha(HERE/'clutch_thrust_build.py')
    assert rebuild['checker_sha256']==sha(HERE/'check_clutch_thrust.py')
    for rel,h in rebuild['evidence_hashes'].items():assert sha(out/'reproduction'/rel)==h,rel
    rebuilt=read(out/'reproduction/report.json')
    assert rebuilt['input_hashes']==r['input_hashes'] and rebuilt['parent_native_sha256']==r['parent_native_sha256']
    assert rebuilt['native_sha256']==sha(out/'reproduction/TransmissionWithClutchThrust.FCStd')
    for name in ['material_checks.json','independent_checks.json','exchange_checks.json','assembly_exchange_checks.json']:
        receipt=read(out/'reproduction'/name);assert receipt['passed'] and receipt['native_sha256']==rebuilt['native_sha256']
    with zipfile.ZipFile(native) as archive:xml=ET.fromstring(archive.read('Document.xml'))
    external=[x.attrib for x in xml.iter('XLink') if x.get('file','')];assert not external
    tree=subprocess.check_output(['git','ls-tree','-r','-z','HEAD','--','cad'],cwd=ROOT);preserved=[]
    for entry in tree.split(b'\0'):
        if not entry:continue
        meta,name=entry.split(b'\t',1);name=name.decode();oid=meta.decode().split()[2]
        if name.startswith('cad/intermediate_') and name.endswith('.png'):
            data=(ROOT/name).read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            assert actual==oid,name;preserved.append(dict(path=name,sha256=sha(ROOT/name),git_blob=oid))
    assert len(preserved)>=84
    names+=['report.json','definition_order.json','source_review/index.html']
    result=dict(passed=True,status='checked_approximate_clutch_thrust_mechanism',native_sha256=nh,
        parent_native_sha256=r['parent_native_sha256'],parent_qualification_sha256=r['parent_qualification_sha256'],
        native_occurrences=1581,new_physical_occurrences=32,changed_parent_occurrences=1,unchanged_parent_occurrences=1548,
        accepted_for_main_clutch_development=True,complete_clutch=False,complete_installation=False,integrated_in_standard_tank=False,
        historical_fit_qualified=False,load_qualified=False,complete_tank=False,native_external_file_references=external,
        standard_native_hashes=r['standard_native_hashes'],input_hashes=r['input_hashes'],source_dossier_sha256=sha(HERE/'clutch_thrust_sources.json'),
        receipt_hashes={n:sha(out/n) for n in names},artifact_hashes={n:sha(out/n) for n in artifacts},
        preserved_progression_images=preserved,qualifier_sha256=sha(Path(__file__)),
        remaining=['Cones, linings and rivets; six spring-plunger sets with real receiving interfaces',
                   'Ring shape, race/cage manufacture and preload remain estimates; HB/SNL identity transfers remain unresolved',
                   'Crankshaft/flywheel interfaces, clutch-stop band, pump air circuit, supports, lubrication, brakes and controls',
                   'Standard tank integration and all other incomplete systems'])
    (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 1581 physical components; static thrust geometry qualified with stated approximations. Full clutch and tank remain incomplete.')


if __name__=='__main__':main()
