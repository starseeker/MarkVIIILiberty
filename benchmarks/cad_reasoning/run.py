"""Run the fixed, balanced 27-trial CLI matrix and grade outside the candidate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    temporary=p.with_suffix(p.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2)+'\n');temporary.replace(p)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--limit',type=int,default=27)
    parser.add_argument('--timeout',type=int,default=240)
    args=parser.parse_args()
    manifest=json.loads((HERE/'manifest.json').read_text())
    for rel,expected in manifest['fixture_hashes'].items():
        assert sha(HERE/rel)==expected,rel
    selftest=json.loads((HERE/'results/self_test/self_test.json').read_text())
    assert selftest['passed'] and selftest['grader_sha256']==sha(HERE/'grade.py')
    resultroot=HERE/'results/pilot_01';resultroot.mkdir(parents=True,exist_ok=True)
    protocol={
        'manifest_sha256':sha(HERE/'manifest.json'), 'grader_sha256':sha(HERE/'grade.py'),
        'runner_sha256':sha(Path(__file__)), 'protocol_sha256':sha(HERE/'README.md'),
        'cli_version':subprocess.run(['codex','--version'],capture_output=True,text=True).stdout.strip(),
        'model':manifest['model'], 'timeout_seconds':args.timeout,
        'read_only_no_tools':True, 'server_model_attestation':'not returned in CLI event stream',
    }
    protocolpath=resultroot/'protocol.json'
    if protocolpath.exists():
        assert json.loads(protocolpath.read_text())==protocol,'Protocol changed; use a new experiment directory'
    else:write(protocolpath,protocol)
    schedule=[];efforts=manifest['efforts'];cases=list(manifest['cases'])
    for repeat in range(3):
        for caseindex,case in enumerate(cases):
            offset=(repeat+caseindex)%3
            for effort in efforts[offset:]+efforts[:offset]:
                schedule.append(dict(case=case,effort=effort,repeat=repeat+1))
    write(resultroot/'schedule.json',schedule)
    for index,trial in enumerate(schedule[:args.limit],1):
        name=f"{trial['case']}_{trial['effort']}_{trial['repeat']}"
        out=resultroot/name;out.mkdir(exist_ok=True)
        if (out/'result.json').exists():
            print('REUSED '+name,flush=True);continue
        work=ROOT/'.work/cad-benchmark/trials'/name;work.mkdir(parents=True,exist_ok=True)
        assert not list(work.iterdir()),'Candidate directory must start empty'
        casefolder=HERE/'fixtures'/trial['case']
        command=['codex','exec','--ignore-user-config','--strict-config','--ephemeral',
            '--skip-git-repo-check','--sandbox','read-only','--model',manifest['model'],
            '-c','model_reasoning_effort='+json.dumps(trial['effort']),
            '--json','--cd',str(work),'--output-schema',str(casefolder/'schema.json'),
            '--output-last-message',str(out/'answer.json')]
        for img in manifest['cases'][trial['case']]['images']:
            command+=['--image',str(HERE/'fixtures'/img)]
        command+=['-']
        record=dict(trial,index=index,command=command,started_unix=time.time(),
                    prompt_sha256=sha(casefolder/'prompt.txt'),schema_sha256=sha(casefolder/'schema.json'),
                    image_hashes={im:sha(HERE/'fixtures'/im) for im in manifest['cases'][trial['case']]['images']})
        write(out/'request.json',record)
        write(resultroot/'progress.json',dict(index=index,total=len(schedule),current=name,status='running',started_unix=record['started_unix']))
        print(f'START {index}/27 {name}',flush=True)
        started=time.monotonic();timedout=False
        with (casefolder/'prompt.txt').open('rb') as prompt, (out/'events.jsonl').open('wb') as events, (out/'stderr.log').open('wb') as errors:
            process=subprocess.Popen(command,stdin=prompt,stdout=events,stderr=errors,start_new_session=True)
            try:returncode=process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timedout=True;os.killpg(process.pid,signal.SIGTERM)
                try:returncode=process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL);returncode=process.wait()
        elapsed=time.monotonic()-started
        events=[];badlines=[]
        for line in (out/'events.jsonl').read_text().splitlines():
            try:events.append(json.loads(line))
            except json.JSONDecodeError:badlines.append(line)
        usage={};unexpected=[]
        for event in events:
            if event.get('type')=='turn.completed':
                for key,value in event.get('usage',{}).items():usage[key]=usage.get(key,0)+value
            if event.get('type','').startswith('item.'):
                item=event.get('item',{})
                if item.get('type') not in ['agent_message','reasoning']:unexpected.append(item)
        answer_path=out/'answer.json'
        parse_error=None
        try:
            answer=json.loads(answer_path.read_text())
            assert isinstance(answer,dict)
        except Exception as e:parse_error=str(e)
        transport_ok=(returncode==0 and not timedout and parse_error is None and bool(usage))
        grade=None;grading_seconds=0
        if transport_ok and not unexpected:
            grade_start=time.monotonic()
            grading=subprocess.run([sys.executable,str(HERE/'grade.py'),'--case',trial['case'],
                '--answer',str(answer_path),'--output',str(out/'grading')],capture_output=True,text=True,timeout=180)
            grading_seconds=time.monotonic()-grade_start
            (out/'grading-launch.log').write_text(grading.stdout+grading.stderr)
            gradefile=out/'grading/grade.json'
            if grading.returncode==0 and gradefile.exists():grade=json.loads(gradefile.read_text())
        record.update(returncode=returncode,timed_out=timedout,cli_seconds=elapsed,grading_seconds=grading_seconds,
            usage=usage,unexpected_tool_events=unexpected,malformed_event_lines=badlines,
            parse_error=parse_error,transport_ok=transport_ok,
            passed=bool(grade and grade['passed'] and not unexpected),
            grade_summary={k:grade[k] for k in ['passed','passed_checks','total_checks']} if grade else None,
            finished_unix=time.time(),artifact_hashes={p.name:sha(p) for p in [out/'events.jsonl',out/'stderr.log',answer_path] if p.exists()})
        write(out/'result.json',record)
        print(f"DONE {name}: pass={record['passed']} infrastructure={transport_ok} tokens={usage} seconds={elapsed:.1f}",flush=True)
    complete=sum((resultroot/f"{t['case']}_{t['effort']}_{t['repeat']}"/'result.json').exists() for t in schedule)
    write(resultroot/'progress.json',dict(status='finished' if complete==27 else 'partial',completed=complete,total=27))
    return 0

if __name__=='__main__':sys.exit(main())
