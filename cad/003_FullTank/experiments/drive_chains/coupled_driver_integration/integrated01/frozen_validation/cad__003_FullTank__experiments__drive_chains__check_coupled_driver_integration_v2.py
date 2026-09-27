"""Combine preserved physical qualification with the resolved complete guide-geometry audit."""
import argparse,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');native=out/r['native_file']
initial=out/'diagnostics/guide_serialization01/initial_integration_checks.json';q=read(initial);guidepath=out/'guide_geometry_checks.json';g=read(guidepath)
assert q['native_sha256']==g['native_sha256']==r['native_sha256']==sha(native)
assert q['source_native_sha256']==g['source_native_sha256']==r['source_native_sha256']==sha(ROOT/r['source_native'])
pr=read(ROOT/r['prototype']/'report.json');assert q['prototype_native_sha256']==sha(ROOT/r['prototype']/pr['native_file'])
assert q['checker_sha256']==sha(H/'check_coupled_driver_integration.py') and g['checker_sha256']==sha(H/'check_coupled_guide_geometry.py')
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
assert all(sha(ROOT/f)==h for f,h in g['source_hashes'].items())
assert all(sha(ROOT/r['prototype']/f)==h for f,h in q['transferred_receipts'].items())
assert g['passed'] and all(v['passed'] for v in g['checks']) and all(g['negative_controls'].values())
expected={n+' complete curve retained outside physical hierarchy' for n in r['nonphysical_guides']}
assert {v['name'] for v in q['checks'] if not v['passed']}==expected
byname={v['name']:v for v in g['checks']}
checks=[]
for v in q['checks']:
    if v['name'] in expected:
        name=v['name'].split(' complete curve retained')[0]
        v=dict(v,passed=byname[name]['passed'],method='Complete world curve signature, trim intervals, vertices, native metadata and nonphysical ownership; location bookkeeping may differ.',guide_geometry_receipt_sha256=sha(guidepath))
    checks.append(v)
checks.append(dict(name='All13 inherited nonphysical shapes preserve geometry',passed=all(v['passed'] for v in g['checks'] if v['inherited']),guide_geometry_receipt_sha256=sha(guidepath)))
q.update(passed=all(v['passed'] for v in checks),checks=checks,checker_sha256=sha(Path(__file__)),initial_physical_checker_sha256=sha(H/'check_coupled_driver_integration.py'),initial_checks_sha256=sha(initial),guide_geometry_checks_sha256=sha(guidepath),resolution='Native save changed curve topology-location serialization; complete analytic and spline geometry retained within1e-9mm, with translated/pole/trim negative controls. No model edit or physical tolerance relaxation.')
write(out/'independent_checks.json',q);print('INTEGRATION',len(checks),'checks',q['passed']);assert q['passed']
