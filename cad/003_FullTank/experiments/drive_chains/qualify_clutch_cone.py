"""Bind the cone packet's actual saved geometry, independent checks and review."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_cone_build');out=p.parse_args().candidate.resolve()
    native=out/'TransmissionWithClutchCone.FCStd';nh=sha(native);r=read(out/'report.json')
    assert r['native_sha256']==nh and r['native_occurrences']==1652 and r['headless']
    assert len(r['new_ids'])==71 and r['changed_ids']==['ClutchStack_support'] and r['unchanged_parent_occurrences']==1580
    assert set(r['affected_ids'])==set(r['new_ids']+r['changed_ids']) and len(r['affected_ids'])==72
    assert r['material_passed'] and r['standard_context_checked'] and not r['overlaps']
    assert not r['standard_assembly_modified'] and not r['complete_clutch'] and not r['complete_tank']
    parent=HERE/'clutch_thrust_build';pq=read(parent/'qualification.json')
    assert pq['passed'] and pq['accepted_for_main_clutch_development'] and pq['native_occurrences']==1581
    assert sha(parent/'qualification.json')==r['parent_qualification_sha256']
    assert sha(parent/'TransmissionWithClutchThrust.FCStd')==pq['native_sha256']==r['parent_native_sha256']
    for rel,h in r['input_hashes'].items():assert sha(ROOT/rel)==h and sha(out/'inputs'/Path(rel).name)==h,rel
    dossier=read(HERE/'clutch_cone_sources.json')
    assert sha(ROOT/'cad/001_Survey/mark_viii_parts.sqlite')==dossier['survey_sha256']
    assert dossier['inventory']['new_physical']==71 and dossier['inventory']['cone_assembly_nonphysical']
    for rel,h in dossier['source_assets'].items():assert sha(ROOT/rel)==h,rel
    assert len(r['standard_native_hashes'])==20
    for rel,h in r['standard_native_hashes'].items():assert sha(STAGE/'build'/rel)==h,rel
    artifacts={'ClutchConeDefinitions.step':r['definition_step_sha256'],'ClutchConeInstallation.step':r['step_sha256'],
               'inputs/parent_support.brep':r['parent_support_sha256']}
    for rel,h in artifacts.items():assert sha(out/rel)==h,rel
    names=['material_checks.json','independent_checks.json','exchange_checks.json','assembly_exchange_checks.json',
           'variants/report.json','visual_review.json','source_review/render_receipt.json','reproduction.json']
    receipts={n:read(out/n) for n in names}
    for n,receipt in receipts.items():
        assert receipt['native_sha256']==nh,n
        if n!='source_review/render_receipt.json':assert receipt['passed'],n
        if 'checks' in receipt:assert all(c['passed'] for c in receipt['checks']),n
    material=receipts['material_checks.json']
    assert len(material['pairs'])==r['material_pairs']==326 and material['standard_context_checked']
    assert all(abs(x['intersection_mm3'])<1e-5 for x in material['pairs'])
    independent=receipts['independent_checks.json'];assert len(independent['checks'])>=450
    assert sum(x['name'].endswith('/axis passes through cone') for x in independent['checks'])==43
    for name,count in [('exchange_checks.json',10),('assembly_exchange_checks.json',72)]:assert len(receipts[name]['checks'])==count
    for name in ['independent_checks.json','exchange_checks.json','assembly_exchange_checks.json']:
        assert receipts[name]['checker_sha256']==sha(HERE/'check_clutch_cone.py')
    assert receipts['exchange_checks.json']['step_sha256']==artifacts['ClutchConeDefinitions.step']
    assert receipts['assembly_exchange_checks.json']['step_sha256']==artifacts['ClutchConeInstallation.step']
    v=receipts['variants/report.json'];assert v['passed'] and len(v['scenarios'])==2
    assert v['checker_sha256']==sha(HERE/'check_clutch_cone_variants.py') and v['parts_sha256']==sha(HERE/'clutch_cone_parts.py')
    assert v['standard_native_hashes']==r['standard_native_hashes']
    for label in ['smaller','larger']:
        rel='variants/'+label+'.json';row=read(out/rel);names.append(rel)
        assert row['passed'] and not row['overlaps'] and len(row['checks'])==63 and all(c['passed'] for c in row['checks'])
        assert all(abs(pair['intersection_mm3'])<1e-5 for pair in row['pairs'])
        assert row['native_sha256']==sha(out/('variants/'+label+'.FCStd'))
        artifacts['variants/'+label+'.FCStd']=row['native_sha256']
    render=receipts['source_review/render_receipt.json']
    assert render['renderer_sha256']==sha(HERE/'render_clutch_cone_review.py')
    assert render['helper_sha256']==sha(HERE/'detail_render.py') and render['base_renderer_sha256']==sha(STAGE/'lib/visual_review.py')
    assert render['source_sha256']==sha(ROOT/render['source_path']) and len(render['image_hashes'])==7
    for n,h in render['image_hashes'].items():assert sha(out/'source_review'/n)==h,n
    visual=receipts['visual_review.json'];assert visual['image_hashes']==render['image_hashes']
    assert visual['source_render_receipt_sha256']==sha(out/'source_review/render_receipt.json')
    diagnostic=read(out/'diagnostics/receipt.json');assert diagnostic['accepted_native_sha256']==nh
    for rel,h in diagnostic['evidence_hashes'].items():assert sha(out/'diagnostics'/rel)==h,rel
    names.append('diagnostics/receipt.json')
    rebuild=receipts['reproduction.json'];assert rebuild['builder_sha256']==sha(HERE/'clutch_cone_build.py') and rebuild['checker_sha256']==sha(HERE/'check_clutch_cone.py')
    for rel,h in rebuild['evidence_hashes'].items():assert sha(out/'reproduction'/rel)==h,rel
    rr=read(out/'reproduction/report.json');assert rr['input_hashes']==r['input_hashes'] and rr['parent_native_sha256']==r['parent_native_sha256']
    assert rr['native_sha256']==sha(out/'reproduction/TransmissionWithClutchCone.FCStd') and rr['native_occurrences']==1652
    for name in ['material_checks.json','independent_checks.json','exchange_checks.json','assembly_exchange_checks.json']:
        row=read(out/'reproduction'/name);assert row['passed'] and row['native_sha256']==rr['native_sha256']
    for name in ['cone_blank','lining_blank','support_blank','spring_centerline']:
        artifacts['inputs/'+name+'.brep']=sha(out/('inputs/'+name+'.brep'))
    with zipfile.ZipFile(native) as archive:xml=ET.fromstring(archive.read('Document.xml'))
    external=[x.attrib for x in xml.iter('XLink') if x.get('file','')];assert not external
    tree=subprocess.check_output(['git','ls-tree','-r','-z','HEAD','--','cad'],cwd=ROOT);preserved=[]
    for entry in tree.split(b'\0'):
        if not entry:continue
        meta,name=entry.split(b'\t',1);name=name.decode();oid=meta.decode().split()[2]
        if name.startswith('cad/intermediate_') and name.endswith('.png'):
            data=(ROOT/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,name
            preserved.append(dict(path=name,sha256=sha(ROOT/name),git_blob=oid))
    assert len(preserved)>=88
    names+=['report.json','definition_order.json','source_review/index.html']
    result=dict(passed=True,status='checked_approximate_clutch_cone_and_spring_sets',native_sha256=nh,
        parent_native_sha256=r['parent_native_sha256'],parent_qualification_sha256=r['parent_qualification_sha256'],
        native_occurrences=1652,new_physical_occurrences=71,changed_parent_occurrences=1,unchanged_parent_occurrences=1580,
        accepted_for_main_clutch_development=True,complete_spring_retention=False,complete_clutch=False,complete_installation=False,integrated_in_standard_tank=False,
        historical_fit_qualified=False,load_qualified=False,complete_tank=False,native_external_file_references=external,
        standard_native_hashes=r['standard_native_hashes'],input_hashes=r['input_hashes'],source_dossier_sha256=sha(HERE/'clutch_cone_sources.json'),
        receipt_hashes={n:sha(out/n) for n in names},artifact_hashes=artifacts,preserved_progression_images=preserved,
        qualifier_sha256=sha(Path(__file__)),remaining=['SH861K plunger locking wire and head holes; flywheel/drum and crankshaft spline engagement; clutch-stop brake',
            'Historical cone/spring configuration transfer and free-length conflict; source-inferred finishing and fits',
            'Air circuit, engine/cooling and other unfinished interiors, controls and supports',
            'Standard tank integration, complete coverage reconciliation and later selected poses'])
    (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:1652components; cone and spring sets accepted with stated approximations. Full clutch and tank remain incomplete.')


if __name__=='__main__':main()
