"""Verify the frozen control-rebuild checkpoint without rerunning kernel work."""
import argparse
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=H/'transmission_controls_study/redo01/springs_integrated01')
a=p.parse_args();out=a.candidate.resolve();q=read(out/'qualification.json');r=read(out/'report.json')
assert q['local_static_checks_passed'] and sha(out/r['native_file'])==q['native_sha256']==r['native_sha256']
failed=[f for f,h in q['dependencies'].items() if not (ROOT/f).is_file() or sha(ROOT/f)!=h]
assert not failed,failed
for name,h in q['checks'].items():
 c=read(out/name);assert c['passed'] and c['native_sha256']==q['native_sha256'] and sha(out/name)==h
m=read(out/'isolated/manifest.json')
assert len(m['occurrences'])==q['counts']['physical_occurrences'] and len(m['definitions'])==q['counts']['definitions'] and len(m['assemblies'])==q['counts']['assembly_groups']
print('PASS',q['counts'],len(q['dependencies']),'bound dependencies; historical geometry and operation remain open.')
