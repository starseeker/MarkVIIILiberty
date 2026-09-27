"""Read-only restart check for the bounded uninstalled driver fulcrum study."""
import argparse,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();folder=a.candidate.resolve();q=json.loads((folder/'part_qualification.json').read_text());r=json.loads((folder/'report.json').read_text())
assert q['local_part_checks_passed'] and not q['geometry_integrated'] and not q['installation_qualified']
assert hashlib.sha256((folder/r['native_file']).read_bytes()).hexdigest()==q['native_sha256']==r['native_sha256']
for f,h in q['dependencies'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
print('PASS: five-part uninstalled driver study;',len(q['dependencies']),'bound dependencies. Mounting and final end layout remain open.')
