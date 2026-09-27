"""Check every inherited nonphysical shape archive outside the linked definitions."""
import argparse,hashlib,json,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def archive(p):
    with zipfile.ZipFile(p) as z:
        root=ET.fromstring(z.read('Document.xml'));shapes={o.get('name'):sha_bytes(z.read(v.get('file'))) for o in root.findall('ObjectData/Object') for v in o.findall('Properties/Property[@name="Shape"]/Part')}
    tips={p.find('Link').get('value') for o in root.findall('ObjectData/Object') for p in o.findall('Properties/Property[@name="Tip"]') if p.find('Link') is not None}
    return shapes,tips
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');source=ROOT/r['source_native'];native=out/r['native_file']
assert sha(native)==r['native_sha256'] and sha(source)==r['source_native_sha256']
m=read(source.parent/'isolated/manifest.json');old,tips=archive(source);new,_=archive(native)
names=set(old)-set(m['definitions'])-tips
checks=[dict(name=n,source_brep_sha256=old[n],candidate_brep_sha256=new.get(n),passed=old[n]==new.get(n)) for n in sorted(names)]
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),source_native_sha256=sha(source),checker_sha256=sha(Path(__file__)),scope='Exact archive BRep preservation for every inherited nonphysical shape outside linked definitions and their tips.')
(out/'inherited_guide_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(len(checks),'inherited shapes',result['passed']);assert result['passed'] and len(checks)==13
