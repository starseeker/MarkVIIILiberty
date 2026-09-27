"""Reuse inspected prototype views after strict full-native shape/frame preservation."""
import argparse
from pathlib import Path
import shutil,sys
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');prototype=ROOT/r['prototype']
pr=read(prototype/'report.json');render=read(prototype/'render_receipt.json');visual=read(prototype/'visual_review.json')
for name in ['independent_checks.json','definition_preservation_checks.json']:
 q=read(out/name);assert q['passed'] and q['native_sha256']==r['native_sha256']
assert render['native_sha256']==visual['native_sha256']==pr['native_sha256']==sha(prototype/pr['native_file'])
assert visual['disposition']=='reviewed_local_approximation'
assert r['source_native_sha256']==render['parent_native_sha256']
assert sha(out/r['native_file'])==r['native_sha256']
for name,h in render['images'].items():
 assert sha(prototype/name)==h
 assert not (out/name).exists()
 shutil.copy2(prototype/name,out/name)
render.update(native_sha256=r['native_sha256'],prototype_native_sha256=pr['native_sha256'],
 prototype_render_receipt_sha256=sha(prototype/'render_receipt.json'),
 transfer_worker_sha256=sha(Path(__file__)),
 strict_installation_receipt_sha256=sha(out/'independent_checks.json'),
 inherited_preservation_receipt_sha256=sha(out/'definition_preservation_checks.json'),
 scope='Cached inspected prototype views. All prototype shapes/frames match the full native; all inherited context definitions and frames are preserved. Images are reused, not newly rendered.')
write(out/'render_receipt.json',render)
visual.update(native_sha256=r['native_sha256'],prototype_visual_review_sha256=sha(prototype/'visual_review.json'),
 render_receipt_sha256=sha(out/'render_receipt.json'),review_method='Previously inspected images transferred through strict full-native shape/frame checks.')
write(out/'visual_review.json',visual)
prior=read((ROOT/r['source_native']).parent/'progression_receipt.json')
old=prior['prior']|prior['new'];new={}
for kind,file in [('iso','isometric.png'),('front','front.png'),('plan','plan.png'),('section','mount_section.png')]:
 path=ROOT/('cad/intermediate_snapshot_'+kind+'_control_rebuild_intermediate_001.png')
 assert not path.exists();shutil.copy2(out/file,path);new[str(path.relative_to(ROOT))]=sha(path)
write(out/'progression_receipt.json',dict(prior=old,new=new,previous_count=len(old),new_count=len(new),total_count=len(old)+len(new),
 native_sha256=r['native_sha256'],render_receipt_sha256=sha(out/'render_receipt.json')))
print('Four inspected views transferred through strict geometry checks; progression',len(old)+len(new),flush=True)
