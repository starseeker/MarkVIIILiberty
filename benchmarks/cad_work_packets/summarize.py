"""Audit saved shadow results and summarize actual CLI measurements."""
import json
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad_packets'))
from common import production_hashes,read,sha,write
from controller import verify_record
from run_shadow import SCHEDULE

HERE=Path(__file__).resolve().parent


def main():
    rows=[];threads=[];current=production_hashes()
    for case,effort in SCHEDULE:
        run=f'shadow01_{case}_{effort}';out=HERE/'results'/run
        request,result=verify_record(out)
        assert request['effort']==effort and request['model']=='gpt-6-astra'
        assert request['production_before']==current and result['production_unchanged']
        assert read(out/'preflight.json')['passed']
        threads+=result['events']['threads']
        tools=result['events']['completed_items']
        assert tools.get('command_execution',0)>0,'No actual command tool use'
        review=read(out/'review.json') if (out/'review.json').exists() else None
        if review:assert review['result_sha256']==sha(out/'result.json')
        grade=read(out/'validation.json')
        rows.append(dict(run=run,case=case,effort=effort,mechanical_pass=result['mechanical_pass'],
                         seconds=result['launch']['seconds'],usage=result['events']['usage'],tools=tools,
                         checks_passed=grade.get('passed_checks',0),checks_total=grade.get('total_checks',0),
                         review=review,result_sha256=sha(out/'result.json')))
    assert len(threads)==len(set(threads))==6,'Threads are not independent'
    summary={}
    for effort in ['medium','xhigh']:
        selected=[r for r in rows if r['effort']==effort]
        fields=sorted(set(k for r in selected for k in r['usage']))
        summary[effort]=dict(passed=sum(r['mechanical_pass'] for r in selected),total=len(selected),
             mean_seconds=statistics.mean(r['seconds'] for r in selected),
             trials_with_reported_usage=sum(bool(r['usage']) for r in selected),
             trials_without_reported_usage=sum(not r['usage'] for r in selected),
             usage_totals_are_partial=any(not r['usage'] for r in selected),
             reported_usage_only={k:sum(r['usage'].get(k,0) for r in selected) for k in fields})
    write(HERE/'results/summary.json',dict(summary=summary,trials=rows,
          verification=dict(passed=True,unique_threads=len(threads),production_documents_unchanged=len(current)),
          limitations=['One repetition per case','Synthetic geometry fixtures','No automatic promotion',
                       'Requested effort, not served-model attestation','Human/source and builder review remain separate']))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
