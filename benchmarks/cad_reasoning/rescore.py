"""Apply the documented wrapper correction uniformly, without new model calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    grader=HERE/'grade_v2.py'
    selftest=json.loads((HERE/'results/self_test_v2/self_test.json').read_text())
    assert selftest['passed'] and selftest['grader_sha256']==sha(grader)
    for path in sorted((HERE/'results/pilot_01').glob('*/result.json')):
        original=json.loads(path.read_text());folder=path.parent
        if not original['transport_ok'] or original['unexpected_tool_events']:continue
        answer=folder/'answer.json'
        assert sha(answer)==original['artifact_hashes']['answer.json']
        resultpath=folder/'result_v2.json'
        if resultpath.exists():
            existing=json.loads(resultpath.read_text())
            assert existing['grader_sha256']==sha(grader) and existing['answer_sha256']==sha(answer)
            continue
        command=[sys.executable,str(grader),'--case',original['case'],'--answer',str(answer),'--output',str(folder/'grading_v2')]
        subprocess.run(command,check=True,timeout=180)
        grade=json.loads((folder/'grading_v2/grade.json').read_text())
        result=dict(passed=grade['passed'],passed_checks=grade['passed_checks'],total_checks=grade['total_checks'],
                    answer_sha256=sha(answer),grader_sha256=sha(grader),original_result_sha256=sha(path),
                    v1_passed=original['passed'])
        resultpath.write_text(json.dumps(result,indent=2)+'\n')
        print(folder.name,'v2',result['passed'],'original',original['passed'],flush=True)

if __name__=='__main__':main()
