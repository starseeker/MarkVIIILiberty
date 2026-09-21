"""Summarize observations without mistaking checks or repeats for new tasks."""
import json
from pathlib import Path
import statistics

HERE=Path(__file__).resolve().parent
OUT=HERE/'results/pilot_01'

def main():
    rows=[]
    for p in sorted(OUT.glob('*/result.json')):
        row=json.loads(p.read_text())
        v2=p.parent/'result_v2.json'
        row['scoring_version']='v1'
        if v2.exists():
            row['passed']=json.loads(v2.read_text())['passed']
            row['scoring_version']='v2'
        rows.append(row)
    effort_rows=[]
    for effort in ['medium','high','xhigh']:
        group=[r for r in rows if r['effort']==effort]
        good=[r for r in group if r['transport_ok'] and not r['unexpected_tool_events']]
        totals={k:sum(r['usage'].get(k,0) for r in good) for k in
            ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']}
        effort_rows.append(dict(effort=effort,runs=len(group),valid_runs=len(good),
            passes=sum(r['passed'] for r in good),
            mean_cli_seconds=statistics.mean(r['cli_seconds'] for r in good) if good else None,
            total_cli_seconds=sum(r['cli_seconds'] for r in good),
            usage=totals,cases={case:dict(passes=sum(r['passed'] for r in good if r['case']==case),
                runs=sum(r['case']==case for r in good)) for case in ['source','construction','repair']}))
    failures=[]
    for r in rows:
        if not r['passed']:
            name=f"{r['case']}_{r['effort']}_{r['repeat']}"
            gp=OUT/name/('grading_v2' if r['scoring_version']=='v2' else 'grading')/'grade.json'
            grade=json.loads(gp.read_text()) if gp.exists() else {}
            failures.append(dict(trial=name,infrastructure_ok=r['transport_ok'],
                tool_events=r['unexpected_tool_events'],failed_checks=[c for c in grade.get('checks',[]) if not c['passed']]))
    summary=dict(completed=len(rows),planned=27,rescored=sum(r['scoring_version']=='v2' for r in rows),efforts=effort_rows,failures=failures,
        limitations=['Three distinct tasks; three repetitions per setting are not nine distinct problems.',
                     'Tool use prohibited and audited. Not an autonomous CAD workflow comparison.',
                     'CAD functions scored on nominal and varied dimensions plus STEP checks.',
                     'Shared project-derived source interpretation is a reviewed reference, not metrology.',
                     'Cached input and requested settings recorded; no billed-cost estimate or returned-model attestation.'])
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    lines=['# Observed results','',f"{len(rows)} of 27 planned runs recorded; {summary['rescored']} uniformly re-scored with the corrected Python wrapper.",'',
        '| Effort | Source | Construction | Repair | All cases passed | Mean CLI seconds | Input tokens | Cached input | Output tokens | Reasoning tokens |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for e in effort_rows:
        def score(case):
            s=e['cases'][case];return f"{s['passes']}/{s['runs']}"
        u=e['usage'];seconds=f"{e['mean_cli_seconds']:.1f}" if e['mean_cli_seconds'] is not None else '—'
        lines.append(f"| {e['effort']} | {score('source')} | {score('construction')} | {score('repair')} | {e['passes']}/{e['valid_runs']} | {seconds} | {u['input_tokens']:,} | {u['cached_input_tokens']:,} | {u['output_tokens']:,} | {u['reasoning_output_tokens']:,} |")
    lines+=['','Output and reasoning fields are reported as returned by the CLI; do not add them together to infer billed tokens. Each task is all-or-nothing against fixed hard checks.','',
            '## Failures','']
    if not failures:lines.append('None among completed trials.')
    for f in failures:
        lines.append(f"- **{f['trial']}**: "+('; '.join(c['name'] for c in f['failed_checks']) or 'infrastructure/tool-use failure'))
    lines+=['','## Limits','']+['- '+x for x in summary['limitations']]
    lines+=['','For raw evidence see each trial directory: request, CLI events, answer, result, grading checks and native/STEP artifacts.','']
    (OUT/'SUMMARY.md').write_text('\n'.join(lines))
    print('\n'.join(lines[:10]))

if __name__=='__main__':main()
