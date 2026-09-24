"""Revalidate standard-tank files and bind scoped context evidence to final components."""
import argparse,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--standard-manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();c=read(a.contract);out=a.output.resolve();out.parent.mkdir(parents=True,exist_ok=True)
standard=read(a.standard_manifest);assert all(sha(ROOT/f)==v for f,v in standard['native_files'].items());rows={v['name']:v for v in read(ROOT/c['candidate']/'isolated/manifest.json')['occurrences']};increments=[]
for path in c['increments']:
 folder=ROOT/path;r=read(folder/'report.json');m=read(folder/'isolated/manifest.json');q=read(folder/'standard_context_checks.json');assert q['passed'] and sha(folder/r['native_file'])==q['native_sha256']==r['native_sha256']==m['native_sha256'];assert sha(a.standard_manifest)==q['standard_manifest_sha256'];increments.append((folder,r,m,q))
checks=[]
for name in c['affected_occurrences']:
 available=[i for i,(_,r,_,_) in enumerate(increments) if name in r['affected_occurrences']];assert available;selected=max(available);folder,r,m,q=increments[selected];old=next(v for v in m['occurrences'] if v['name']==name);key=old['definition'];final=rows[name];passed=final['definition']==key and final['owners']==old['owners'] and max(abs(x-y) for x,y in zip(final['frame'],old['frame']))<1e-7
 for successor,_,_,_ in increments[selected+1:]:
  data=read(successor/'definition_preservation_checks.json');match=[v for v in data['checks'] if v['definition']==key];passed=passed and len(match)==1 and match[0]['passed']
 checks.append(dict(occurrence=name,passed=bool(passed),context_receipt=str((folder/'standard_context_checks.json').relative_to(ROOT)),context_receipt_sha256=sha(folder/'standard_context_checks.json'),retained_standard_count=q['standard_context_count'],native_sha256=q['native_sha256'],preserved_through=[str(v[0].relative_to(ROOT)) for v in increments[selected+1:]]))
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=c['native_sha256'],contract_sha256=sha(a.contract),standard_manifest_sha256=sha(a.standard_manifest),standard_native_hashes=standard['native_files'],checker_sha256=sha(Path(__file__)),scope='All45 final affected occurrences have current retained-standard context evidence. Source tank files rehashed; earlier part geometry/frame checks reused only through intervening preservation receipts. Does not qualify incomplete standard tank coverage or service motion.',standard_assembly_modified=False,installation_qualified=False)
write(out,result);assert result['passed'];print('Standard context evidence covers',len(checks),'final occurrences',flush=True)
