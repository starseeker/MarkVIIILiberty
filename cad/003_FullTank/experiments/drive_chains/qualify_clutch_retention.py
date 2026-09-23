"""Bind retention geometry to its source, saved-artifact checks and visual review."""
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
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_retention_build');out=p.parse_args().candidate.resolve()
    native=out/'TransmissionWithClutchRetention.FCStd';nh=sha(native);r=read(out/'report.json')
    assert r['native_sha256']==nh and r['native_occurrences']==1653 and r['headless']
    assert r['new_ids']==['ClutchRetention_Wire'] and r['changed_ids']==[f'ClutchCone_Plunger{n}' for n in range(1,7)]
    assert r['affected_ids']==r['changed_ids']+r['new_ids'] and r['unchanged_parent_occurrences']==1646
    assert r['material_passed'] and r['standard_context_checked'] and not r['overlaps']
    assert not r['standard_assembly_modified'] and not r['complete_clutch'] and not r['complete_tank']
    parent=HERE/'clutch_cone_build';pq=read(parent/'qualification.json')
    assert pq['passed'] and pq['accepted_for_main_clutch_development'] and pq['native_occurrences']==1652
    assert sha(parent/'qualification.json')==r['parent_qualification_sha256']
    assert sha(parent/'TransmissionWithClutchCone.FCStd')==pq['native_sha256']==r['parent_native_sha256']
    for rel,h in r['input_hashes'].items():assert sha(ROOT/rel)==h and sha(out/'inputs'/Path(rel).name)==h,rel
    source=read(HERE/'clutch_retention_sources.json')
    assert sha(ROOT/'cad/001_Survey/mark_viii_parts.sqlite')==source['survey_sha256']
    assert source['inventory']['new_wire']==1 and source['inventory']['spool_allocation_is_not_an_extra_piece']
    for rel,h in source['source_assets'].items():assert sha(ROOT/rel)==h,rel
    assert len(r['standard_native_hashes'])==20
    for rel,h in r['standard_native_hashes'].items():assert sha(STAGE/'build'/rel)==h,rel
    artifacts=dict(r['artifact_hashes'])
    for rel,h in artifacts.items():assert sha(out/rel)==h,rel
    names=['material_checks.json','independent_checks.json','exchange_checks.json','variants/report.json','visual_review.json','source_review/render_receipt.json','reproduction.json']
    receipts={n:read(out/n) for n in names}
    for name,row in receipts.items():
        assert row['native_sha256']==nh,name
        if name!='source_review/render_receipt.json':assert row['passed'],name
        if 'checks' in row:assert all(c['passed'] for c in row['checks']),name
    material=receipts['material_checks.json'];assert len(material['pairs'])==r['material_pairs']==68 and material['standard_context_checked']
    assert all(abs(x['intersection_mm3'])<1e-5 for x in material['pairs'])
    independent=receipts['independent_checks.json'];assert len(independent['checks'])>=84
    for suffix in ['/actual through passage','/misaligned wire catches solid head','/bore tangent frame']:
        assert sum(x['name'].endswith(suffix) for x in independent['checks'])==6
    exchange=receipts['exchange_checks.json'];assert len(exchange['checks'])==9
    assert sum(x['scope']=='Definitions' for x in exchange['checks'])==2
    for name in ['independent_checks.json','exchange_checks.json']:assert receipts[name]['checker_sha256']==sha(HERE/'check_clutch_retention.py')
    for rel,h in exchange['artifact_hashes'].items():assert sha(out/rel)==h
    variants=receipts['variants/report.json'];assert len(variants['scenarios'])==2
    assert variants['checker_sha256']==sha(HERE/'check_clutch_retention_variants.py') and variants['parts_sha256']==sha(HERE/'clutch_retention_parts.py')
    assert variants['standard_native_hashes']==r['standard_native_hashes']
    for item in variants['scenarios']:
        rel='variants/'+item['name']+'.json';row=read(out/rel);names.append(rel)
        assert sha(out/rel)==item['report_sha256'] and row['passed'] and not row['overlaps']
        assert len(row['checks'])==22 and all(x['passed'] for x in row['checks'])
        assert all(abs(x['intersection_mm3'])<1e-5 for x in row['pairs'])
        rel='variants/'+item['name']+'.FCStd';assert sha(out/rel)==item['native_sha256']==row['native_sha256'];artifacts[rel]=sha(out/rel)
    render=receipts['source_review/render_receipt.json'];assert render['renderer_sha256']==sha(HERE/'render_clutch_retention_review.py')
    assert render['helper_sha256']==sha(HERE/'detail_render.py') and render['base_renderer_sha256']==sha(STAGE/'lib/visual_review.py')
    assert render['source_sha256']==sha(ROOT/render['source_path']) and len(render['image_hashes'])==5
    for rel,h in render['image_hashes'].items():assert sha(out/'source_review'/rel)==h
    visual=receipts['visual_review.json'];assert visual['image_hashes']==render['image_hashes']
    assert visual['source_render_receipt_sha256']==sha(out/'source_review/render_receipt.json')
    rebuild=receipts['reproduction.json'];assert rebuild['builder_sha256']==sha(HERE/'clutch_retention_build.py') and rebuild['checker_sha256']==sha(HERE/'check_clutch_retention.py')
    for rel,h in rebuild['evidence_hashes'].items():assert sha(out/'reproduction'/rel)==h
    rr=read(out/'reproduction/report.json');assert rr['input_hashes']==r['input_hashes'] and rr['parent_native_sha256']==r['parent_native_sha256']
    assert rr['native_sha256']==sha(out/'reproduction/TransmissionWithClutchRetention.FCStd') and rr['native_occurrences']==1653
    for name in ['material_checks.json','independent_checks.json','exchange_checks.json']:
        row=read(out/'reproduction'/name);assert row['passed'] and row['native_sha256']==rr['native_sha256']
    diagnostic=read(out/'diagnostics/receipt.json');assert diagnostic['accepted_native_sha256']==nh
    for rel,h in diagnostic['evidence_hashes'].items():assert sha(out/'diagnostics'/rel)==h
    names.append('diagnostics/receipt.json')
    with zipfile.ZipFile(native) as archive:xml=ET.fromstring(archive.read('Document.xml'))
    external=[x.attrib for x in xml.iter('XLink') if x.get('file','')];assert not external
    tree=subprocess.check_output(['git','ls-tree','-r','-z','HEAD','--','cad'],cwd=ROOT);preserved=[]
    for entry in tree.split(b'\0'):
        if not entry:continue
        meta,name=entry.split(b'\t',1);name=name.decode();oid=meta.decode().split()[2]
        if name.startswith('cad/intermediate_') and name.endswith('.png'):
            data=(ROOT/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,name
            preserved.append(dict(path=name,sha256=sha(ROOT/name),git_blob=oid))
    assert len(preserved)>=92
    snapshots=read(out/'progression_snapshots.json')
    expected={'isometric.png':'intermediate_snapshot_iso_clutch_retention_001.png',
        'retention.png':'intermediate_snapshot_detail_clutch_retention_001.png',
        'head_section.png':'intermediate_snapshot_detail_plunger_wire_001.png'}
    assert set(snapshots)==set(expected.values())
    for src,dst in expected.items():assert sha(ROOT/'cad'/dst)==snapshots[dst]==render['image_hashes'][src]
    names.append('progression_snapshots.json')
    names+=['report.json','definition_order.json','source_review/index.html']
    result=dict(passed=True,status='checked_approximate_plunger_retention',native_sha256=nh,parent_native_sha256=r['parent_native_sha256'],
        parent_qualification_sha256=r['parent_qualification_sha256'],native_occurrences=1653,new_physical_occurrences=1,
        changed_parent_occurrences=6,unchanged_parent_occurrences=1646,accepted_for_main_clutch_development=True,
        complete_spring_retention_geometry=True,complete_clutch=False,complete_installation=False,integrated_in_standard_tank=False,
        historical_fit_qualified=False,load_qualified=False,complete_tank=False,native_external_file_references=external,
        standard_native_hashes=r['standard_native_hashes'],input_hashes=r['input_hashes'],source_dossier_sha256=sha(HERE/'clutch_retention_sources.json'),
        receipt_hashes={n:sha(out/n) for n in names},artifact_hashes=artifacts,preserved_progression_images=preserved,new_progression_images=snapshots,qualifier_sha256=sha(Path(__file__)),
        remaining=['Outer clutch drum, flywheel/crankshaft engagement and clutch-stop brake; recheck wire tail against future engine geometry',
            'Wire gauge conversion, routing and twist are estimates; no locking-strength or historical manufacturing-fit claim',
            'Air circuit, engine/cooling, remaining interiors and standard assembly integration',
            'Complete inventory/geometry/evidence coverage and later selected poses'])
    (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS:1653components; one SH861K wire and six drilled plunger heads accepted with stated approximations.')

if __name__=='__main__':main()
