"""Audit the completed experiment's provenance and preservation of project CAD."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'results/pilot_01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())

def main():
    m=read(HERE/'manifest.json');protocol=read(OUT/'protocol.json')
    for key,path in [('manifest_sha256',HERE/'manifest.json'),('grader_sha256',HERE/'grade.py'),
                     ('runner_sha256',HERE/'run.py'),('protocol_sha256',HERE/'README.md')]:
        assert sha(path)==protocol[key],key
    for rel,h in m['fixture_hashes'].items():assert sha(HERE/rel)==h,rel
    for rel,h in m['source_files'].items():assert sha(ROOT/rel)==h,rel
    original=read(HERE/'results/production_baseline.json')
    for rel,h in original['sha256'].items():assert sha(ROOT/rel)==h,rel
    expected={f'{case}_{effort}_{n}' for case in m['cases'] for effort in m['efforts'] for n in [1,2,3]}
    paths=list(OUT.glob('*/result.json'))
    assert {p.parent.name for p in paths}==expected
    threads=set();artifact_hashes={};passes={e:0 for e in m['efforts']}
    for path in paths:
        r=read(path);folder=path.parent;request=read(folder/'request.json')
        assert request['command']==r['command']
        assert r['transport_ok'] and not r['unexpected_tool_events'],folder.name
        for file,h in r['artifact_hashes'].items():assert sha(folder/file)==h,folder/file
        assert r['prompt_sha256']==sha(HERE/'fixtures'/r['case']/'prompt.txt')
        assert r['schema_sha256']==sha(HERE/'fixtures'/r['case']/'schema.json')
        for name,h in r['image_hashes'].items():assert sha(HERE/'fixtures'/name)==h
        assert r['command'][r['command'].index('--model')+1]==m['model']
        assert 'model_reasoning_effort='+json.dumps(r['effort']) in r['command']
        events=[json.loads(line) for line in (folder/'events.jsonl').read_text().splitlines()]
        ids=[e['thread_id'] for e in events if e['type']=='thread.started']
        assert len(ids)==1 and ids[0] not in threads;threads.add(ids[0])
        reported={}
        for event in events:
            if event['type']=='turn.completed':
                for k,v in event['usage'].items():reported[k]=reported.get(k,0)+v
        assert reported==r['usage']
        v2=read(folder/'result_v2.json');grade=read(folder/'grading_v2/grade.json')
        assert v2['answer_sha256']==sha(folder/'answer.json')==grade['answer_sha256']
        assert v2['original_result_sha256']==sha(path)
        assert v2['grader_sha256']==sha(HERE/'grade_v2.py')==grade['grader_sha256']
        assert v2['passed']==grade['passed']==all(c['passed'] for c in grade['checks'])
        assert v2['passed_checks']==sum(c['passed'] for c in grade['checks'])
        passes[r['effort']]+=int(v2['passed'])
        for artifact in folder.rglob('*'):
            if artifact.is_file() and 'runtime' not in artifact.parts and '.FCStd.' not in artifact.name:
                artifact_hashes[str(artifact.relative_to(HERE))]=sha(artifact)
    for p in [HERE/'grade.py',HERE/'grade_v2.py',HERE/'reference.py',HERE/'run.py',HERE/'prepare.py',
              HERE/'manifest.json',HERE/'README.md',HERE/'results/grader_amendment.json',HERE/'results/runtime.json']:
        artifact_hashes[str(p.relative_to(HERE))]=sha(p)
    result=dict(passed=True,trials=27,distinct_threads=len(threads),tool_using_trials=0,
                production_documents_unchanged=len(original['sha256']),passes=passes,
                artifact_sha256=artifact_hashes)
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'}))

if __name__=='__main__':main()
