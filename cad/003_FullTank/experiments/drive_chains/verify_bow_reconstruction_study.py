"""Freeze/verify the bow diagnostic and its explicit failures; never promote it."""
import argparse
import hashlib
import json
from pathlib import Path

H=Path(__file__).resolve().parent
ROOT=H.parents[3]
STUDY=H/'bow_reconstruction_study'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');a=p.parse_args()
    folder=STUDY/'trial02';r=read(folder/'report.json');checks=read(folder/'checks01/report.json')
    visual=read(folder/'visual01/visual_review.json');handles=read(folder/'handle_recheck01/report.json')
    digest=sha(folder/r['native_file'])
    assert digest==r['native_sha256']==checks['native_sha256']==handles['bow_native_sha256']
    assert checks['construction_passed'] and all(c['passed'] for c in checks['construction_checks'])
    assert checks['joints_passed'] and all(c['passed'] for c in checks['joints'])
    assert not checks['context_passed'] and len(checks['context_findings'])==2
    assert {v['second'] for v in checks['context_findings']}=={'development:PortDriverOperatingHandle','development:StarboardDriverOperatingHandle'}
    assert all(v['first']=='hull_front_slope' and v['common_volume_mm3']>4400 for v in checks['context_findings'])
    assert visual['disposition']=='reviewed_diagnostic_not_integrated'
    assert visual['native_sha256']==digest and len(visual['inspected_images'])==2
    assert r['candidate_occurrence_count']==40 and len(r['occurrences'])==48
    assert not r['geometry_integrated'] and not r['historical_geometry_qualified']
    assert len(handles['profile_results'])==4
    for profile in handles['profile_results'].values():
        failures=[v for v in profile['pairs'] if not v['passed']]
        assert not profile['passed'] and len(failures)==2
        assert all(v['plate']=='hull_front_slope' and v['common_mm3']>2000 for v in failures)
    old=read(STUDY/'trial01/checks01/report.json')
    assert sha(STUDY/'trial01/checks01/checker_snapshot.py')==old['checker_sha256']
    receipt=STUDY/'study_receipt.json'
    if a.freeze:
        assert not receipt.exists()
        deps={}
        def add(path,expected=None):
            path=Path(path);path=path if path.is_absolute() else ROOT/path
            value=sha(path);assert expected is None or value==expected,str(path)
            deps[str(path.relative_to(ROOT))]=value
        for path in sorted(STUDY.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:add(path)
        for f,d in r['input_hashes'].items():add(f,d)
        for f,d in r['standard_native_files'].items():add(f,d)
        add(r['development_native'],r['development_native_sha256'])
        for f,d in handles['input_hashes'].items():add(f,d)
        for name in ['bow_reconstruction_parts.py','build_bow_reconstruction.py','check_bow_reconstruction.py',
                     'render_bow_reconstruction.py','check_bow_handle_hypotheses.py','verify_bow_reconstruction_study.py']:
            add(H/name)
        for f,d in read(STUDY/'source_review.json')['input_hashes'].items():add(f,d)
        result=dict(diagnostic_complete=True,geometry_promoted=False,native_sha256=digest,
                    construction_checks=len(checks['construction_checks']),joints=len(checks['joints']),
                    context_pairs=len(checks['context_pairs']),context_findings=checks['context_findings'],
                    accepted_checkpoint_unchanged=r['development_native'],
                    scope='Forty source-labelled bow/enclosure replacement plates, native/STEP/material/joint checks and four full-handle rechecks. Two current handle conflicts and unresolved historical interpretation prevent integration.',
                    dependencies=deps)
        receipt.write_text(json.dumps(result,indent=2)+'\n')
    result=read(receipt)
    assert result['diagnostic_complete'] and not result['geometry_promoted'] and result['native_sha256']==digest
    assert all(sha(ROOT/f)==d for f,d in result['dependencies'].items())
    print('PASS: 40-plate bow diagnostic; 255 construction checks, six joints; explicit two-handle installation failure;',len(result['dependencies']),'bound dependencies. No integration.')


if __name__=='__main__':main()
