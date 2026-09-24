"""Reopen the relocated final native and independently bind every physical link."""
import argparse,shutil,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];sys.path.insert(0,str(STAGE))
import FreeCAD as App
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
checks=[]
with tempfile.TemporaryDirectory(prefix='relocated_control_joint_',dir=out) as temporary:
    moved=Path(temporary)/native.name;shutil.copy2(native,moved);assert sha(moved)==sha(native)
    validate_native_bindings(dict(native_file=str(moved),render_occurrences=[v['name'] for v in m['occurrences']],landmarks=[]),m)
    doc=App.openDocument(str(moved))
    try:
        checks.append(dict(name='All3173 native link targets remain local after relocation',passed=len(m['occurrences'])==3173 and all(doc.getObject(v['object']).LinkedObject.Document==doc for v in m['occurrences'])))
        for key in r['new_definitions']+list(r['shared_definitions'].values()):
            body=doc.getObject(key);s=body.Shape
            checks.append(dict(name=key+' relocated closed unscaled definition',passed=body.Placement.isIdentity() and s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.getTolerance(1)<=1e-4))
    finally:App.closeDocument(doc.Name)
write(out/'native_portability_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(native),manifest_sha256=sha(out/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Independent archive/placement binding for all3173 physical links plus actual reopening in a temporary relocated directory. Temporary native copy removed after close.'))
print('Relocated native checks:',len(checks),'passed',all(v['passed'] for v in checks));assert all(v['passed'] for v in checks)
