"""Archive exact standard context bytes without repeating geometry validation.

The initial qualification verified the generated standard-native paths. Preserve
that receipt unchanged, and bind its exact source bytes at durable archival paths
for subsequent verification. No geometric predicate or result is changed.
"""
import argparse,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();path=out/'qualification.json';q=read(path)
assert q['local_static_checks_passed'] and not (out/'qualification_initial.json').exists()
assert all(sha(ROOT/f)==digest for f,digest in q['dependencies'].items())
standard=H/'transmission_brake_front_study/trial01/standard_context_manifest.json';sources=read(standard)['native_files']
original=out/'qualification_initial.json';shutil.copy2(path,original);prior_sha=sha(original)
mapping={};archive=out/'frozen_standard_context';archive.mkdir()
for file,digest in sources.items():
    source=ROOT/file;assert sha(source)==digest==q['dependencies'][file]
    relative=source.relative_to(ROOT/'cad/003_FullTank/build/native');target=archive/relative
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);assert sha(target)==digest
    mapping[file]=dict(archived_path=str(target.relative_to(ROOT)),sha256=digest)
    del q['dependencies'][file];q['dependencies'][str(target.relative_to(ROOT))]=digest
worker=Path(__file__).resolve();frozen=out/'frozen_validation'/str(worker.relative_to(ROOT)).replace('/','__');shutil.copy2(worker,frozen)
receipt=out/'standard_context_archive.json'
write(receipt,dict(initial_qualification_sha256=prior_sha,standard_manifest_sha256=sha(standard),worker_sha256=sha(worker),native_files=mapping,
    scope='Byte-identical archival relocation of standard native context verified by the existing saved-material audit. Original qualification preserved unchanged. No geometry or acceptance result changed.'))
for file in [original,worker,frozen,receipt]:q['dependencies'][str(file.relative_to(ROOT))]=sha(file)
q['qualification_revision']=2;q['archival_context_receipt']=str(receipt.relative_to(ROOT));q['initial_qualification_sha256']=prior_sha
assert sha(original)==prior_sha
write(path,q)
print('Archived',len(mapping),'standard context natives;',len(q['dependencies']),'bound dependencies.',flush=True)
