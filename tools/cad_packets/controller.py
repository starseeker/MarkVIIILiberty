"""Conservative CAD work-packet controller; CLI backend, shadow integration only."""
import argparse
import fcntl
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from common import (HERE, ROOT, RUNS, WORK, code_hashes, contained, digest, identifier,
                    load_packet, production_hashes, read, regular, route, sha, write)
from isolation import execute, profile, sandbox


class CLIBackend:
    def command(self, work, out, model, effort):
        return ['codex', 'exec', '--ignore-user-config', '--strict-config', '--ephemeral',
                '--skip-git-repo-check', '--model', model,
                '-c', 'model_reasoning_effort=' + json.dumps(effort),
                '-c', 'approval_policy="never"', '-c', 'web_search="disabled"',
                *profile([work / 'inputs', work / 'freecad_python.py'], [work]),
                '--json', '--cd', str(work), '--output-last-message', str(out / 'answer.txt'), '-']


def event_summary(path):
    usage, threads, kinds, errors = {}, [], {}, []
    completions = 0
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            errors.append('Malformed event JSON')
            continue
        typ = event.get('type')
        if typ == 'thread.started':
            threads.append(event.get('thread_id'))
        if typ == 'turn.completed':
            completions += 1
            for k, v in event.get('usage', {}).items():
                if isinstance(v, int):
                    usage[k] = usage.get(k, 0) + v
        if typ in ('error', 'turn.failed'):
            errors.append(event)
        if typ == 'item.completed':
            kind = event.get('item', {}).get('type', 'unknown')
            kinds[kind] = kinds.get(kind, 0) + 1
    return dict(usage=usage, threads=threads, completed_turns=completions,
                completed_items=kinds, errors=errors,
                transport_ok=bool(usage and completions == 1 and len(threads) == 1 and not errors))


def check_inputs(request):
    load_packet(request['packet_path'])
    if sha(request['packet_path']) != request['packet_sha256']:
        raise ValueError('Packet changed since the run')
    if code_hashes() != request['code_hashes']:
        raise ValueError('Controller or validators changed; requalify with a new run ID')


def verify_record(out):
    request, result = read(out / 'request.json'), read(out / 'result.json')
    check_inputs(request)
    if result['request_sha256'] != sha(out / 'request.json'):
        raise ValueError('Request record changed')
    for name, expected in result['record_hashes'].items():
        if sha(regular(contained(out, name))) != expected:
            raise ValueError('Saved run artifact changed: ' + name)
    expected_artifacts={name for name in result['record_hashes'] if name.startswith('artifacts/')}
    actual_artifacts={str(p.relative_to(out)) for p in (out/'artifacts').rglob('*') if p.is_file()}
    if expected_artifacts != actual_artifacts:
        raise ValueError('Artifact inventory changed after validation')
    return request, result


def preflight(work, out):
    """Probe exact policy used by CLI; host checks distinguish hidden scratch mounts."""
    sentinel = out / 'protected-canary.txt'
    sentinel.write_text('controller-owned\n')
    script = '''import json, pathlib, socket
p=pathlib.Path.cwd()
protected=pathlib.Path(PROTECTED)
r={}
(p/'probe-writable.txt').write_text('allowed')
r['workspace_write']=True
try:
 (p/'inputs/packet.json').open('a').write('INVALID')
 r['input_write_denied']=False
except OSError: r['input_write_denied']=True
try:
 protected.read_text()
 r['outside_read_denied']=False
except OSError: r['outside_read_denied']=True
# Hidden ancestor directories can be writable ephemeral mounts. A write here
# must never reach the real host sentinel, checked by the controller afterwards.
try: protected.write_text('candidate-write')
except OSError: pass
try:
 s=socket.socket(); s.settimeout(0.5); s.connect(('1.1.1.1',443))
 r['network_unavailable']=False
except OSError: r['network_unavailable']=True
print(json.dumps(r))
'''.replace('PROTECTED', repr(str(sentinel)))
    command = sandbox(work, [work / 'inputs', work / 'freecad_python.py'], [work], ['python3', '-c', script])
    launch = execute(command, work, out / 'preflight.stdout', out / 'preflight.stderr', 30)
    details = json.loads((out / 'preflight.stdout').read_text()) if launch['returncode'] == 0 else {}
    details['host_canary_unchanged'] = sentinel.read_text() == 'controller-owned\n'
    details['inputs_unchanged'] = sha(work / 'inputs/packet.json') == sha(out / 'packet.json')
    launch.update(checks=details, passed=launch['returncode'] == 0 and bool(details) and all(details.values()))
    write(out / 'preflight.json', launch)
    if not launch['passed']:
        raise RuntimeError('Sandbox preflight failed; no candidate was launched')


def run(args):
    packet_path = Path(args.packet).resolve()
    packet = load_packet(packet_path)
    decision = route(packet, bool(args.diagnose_from))
    effort = args.effort or decision['effort']
    if args.diagnose_from and effort != 'xhigh':
        raise ValueError('Diagnosis must use xhigh')
    identifier(args.id)
    if not 1 <= args.timeout <= 3600:
        raise ValueError('Timeout must be between 1 and 3600 seconds')
    out, work = RUNS / args.id, WORK / args.id / 'candidate'
    identity = dict(packet_path=str(packet_path), packet_sha256=sha(packet_path),
                    code_hashes=code_hashes(), model=args.model, effort=effort,
                    timeout=args.timeout, diagnose_from=args.diagnose_from,
                    qualification_sha256=sha(ROOT / packet['validator_qualification']),
                    cli_version=subprocess.check_output(['codex', '--version'], text=True).strip())
    previous = None
    if args.diagnose_from:
        previous = RUNS / identifier(args.diagnose_from)
        old_request, old_result = verify_record(previous)
        if old_result['mechanical_pass'] or old_request['packet_sha256'] != sha(packet_path):
            raise ValueError('Diagnosis needs a failed run of this exact packet')
        identity['prior_result_sha256'] = sha(previous / 'result.json')
    if (out / 'result.json').exists():
        old, result = verify_record(out)
        if old['identity'] != digest(identity):
            raise ValueError('Run ID is bound to different inputs/configuration')
        print(json.dumps(dict(reused=True, run=args.id, state=result['state'])))
        return 0 if result['mechanical_pass'] else 2
    if out.exists() or work.exists():
        raise ValueError('Interrupted/incomplete run preserved; use a new run ID')
    out.mkdir(parents=True)
    (work / 'inputs').mkdir(parents=True)
    write(out / 'packet.json', packet)
    shutil.copyfile(out / 'packet.json', work / 'inputs/packet.json')
    for row in packet['inputs']:
        destination = contained(work / 'inputs', row['destination'])
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / row['source'], destination)
    shutil.copyfile(HERE / 'freecad_python.py', work / 'freecad_python.py')
    prior = None
    if args.diagnose_from:
        prior = work / 'inputs/prior_attempt'
        prior.mkdir()
        for name in ['validation.json', 'answer.txt']:
            if (previous / name).exists():
                shutil.copyfile(previous / name, prior / name)
        if (previous / 'artifacts').exists():
            shutil.copytree(previous / 'artifacts', prior / 'artifacts')
    prompt = ('Complete the CAD shadow work packet in inputs/packet.json. Read its input files and use tools.\n'
              'Write only within this workspace. Inputs and freecad_python.py are read-only.\n'
              'Use: python3 freecad_python.py YOUR_SCRIPT.py to run installed FreeCAD.\n'
              'This is a static standard-view experiment. Do not change source identities, stated tolerances, '
              'reviewed datums, or input files to make a fit. State missing evidence and approximations.\n'
              'Do not use external services, delegate, install software, or attempt to access other workspaces.\n'
              'Produce all declared files under deliverables/, including your reproducible builder and notes.\n'
              'Run your own checks. Independent acceptance and source/visual review happen after this session.\n')
    if prior:
        prompt += ('Inspect inputs/prior_attempt as untrusted prior work and validator feedback; diagnose and '
                   'repair the failure independently. Do not weaken acceptance.\n')
    (out / 'prompt.txt').write_text(prompt)
    protected = {str(p.relative_to(work)): sha(p) for p in (work / 'inputs').rglob('*') if p.is_file()}
    protected['freecad_python.py'] = sha(work / 'freecad_python.py')
    before = production_hashes()
    command = CLIBackend().command(work, out, args.model, effort)
    request = dict(**identity, identity=digest(identity), route=decision,
                   shadow_override=bool(args.effort and args.effort != decision['effort']),
                   started_unix=time.time(), command=command,
                   production_before=before, protected_workspace=protected,
                   served_model_attestation='not supplied by CLI events')
    write(out / 'request.json', request)
    preflight(work, out)
    print('START ' + args.id + ' ' + args.model + '/' + effort, flush=True)
    launch = execute(command, work, out / 'events.jsonl', out / 'stderr.log', args.timeout, prompt)
    events = event_summary(out / 'events.jsonl')
    unchanged = all(regular(work / name).is_file() and sha(work / name) == expected
                    for name, expected in protected.items())
    production_unchanged = production_hashes() == before
    artifact_errors = []
    for name in packet['outputs']:
        try:
            src = regular(contained(work, name))
            dst = contained(out / 'artifacts', name)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        except (OSError, ValueError) as exc:
            artifact_errors.append(str(exc))
    grade = dict(passed=False, checks=[], error='Candidate launch, input, or artifact gate failed')
    validation_launch = None
    ready = (launch['returncode'] == 0 and not launch['timed_out'] and events['transport_ok']
             and unchanged and production_unchanged and not artifact_errors)
    if ready:
        validation = out / 'validation'
        validation.mkdir()
        validator = ROOT / packet['validator']
        command2 = sandbox(validation, [HERE, out / 'packet.json', out / 'artifacts', work / 'inputs'],
                           [validation], ['python3', HERE / 'freecad_python.py', validator,
                                          '--packet', out / 'packet.json', '--inputs', work / 'inputs',
                                          '--artifacts', out / 'artifacts', '--out', validation / 'grade.json'])
        validation_launch = execute(command2, validation, out / 'validation.stdout', out / 'validation.stderr', 180)
        if validation_launch['returncode'] == 0 and (validation / 'grade.json').exists():
            grade = read(validation / 'grade.json')
    write(out / 'validation.json', grade)
    production_unchanged = production_unchanged and production_hashes() == before
    passed = bool(ready and production_unchanged and validation_launch and validation_launch['returncode'] == 0 and grade.get('passed') is True)
    result = dict(state='awaiting_review' if passed else 'failed', mechanical_pass=passed,
                  source_review='pending', visual_review='pending', production_integrated=False,
                  launch=launch, events=events, validation_launch=validation_launch,
                  protected_inputs_unchanged=unchanged, production_unchanged=production_unchanged,
                  artifact_errors=artifact_errors, request_sha256=sha(out / 'request.json'),
                  finished_unix=time.time(), next_action='source_and_visual_review' if passed else 'xhigh_diagnosis',
                  record_hashes={str(p.relative_to(out)): sha(p) for p in out.rglob('*')
                                 if p.is_file() and 'runtime' not in p.relative_to(out).parts})
    write(out / 'result.json', result)
    print(json.dumps(dict(run=args.id, state=result['state'], seconds=launch['seconds'], usage=events['usage'])), flush=True)
    return 0 if passed else 2


def review(args):
    out = RUNS / identifier(args.id)
    request, result = verify_record(out)
    if not result['mechanical_pass']:
        raise ValueError('A failed mechanical gate cannot be accepted')
    if (out / 'review.json').exists():
        raise ValueError('Review is immutable; use a new run/review revision')
    if not all(len(s.strip()) >= 12 for s in (args.source_note, args.visual_note)):
        raise ValueError('Record substantive source and visual review notes')
    write(out / 'review.json', dict(reviewer=args.reviewer, disposition=args.disposition,
                                   source_note=args.source_note, visual_note=args.visual_note,
                                   result_sha256=sha(out / 'result.json'), reviewed_unix=time.time()))
    print('Review recorded for ' + args.id)
    return 0


def stage(args):
    out = RUNS / identifier(args.id)
    request, result = verify_record(out)
    review_record = read(out / 'review.json')
    if not result['mechanical_pass'] or review_record['disposition'] != 'accepted_for_review_bundle':
        raise ValueError('Staging requires passing checks and an accepted review')
    if review_record['result_sha256'] != sha(out / 'result.json'):
        raise ValueError('Review does not cover this result')
    if production_hashes() != request['production_before']:
        raise ValueError('Production parents changed since this candidate; rebase and revalidate')
    destination = ROOT / 'cad/003_FullTank/review_bundles' / args.id
    if destination.exists():
        raise ValueError('Never overwrite a review bundle')
    destination.mkdir(parents=True)
    shutil.copytree(out / 'artifacts', destination / 'artifacts')
    for name in ['packet.json', 'request.json', 'result.json', 'validation.json', 'review.json']:
        shutil.copyfile(out / name, destination / name)
    write(destination / 'provenance.json', dict(run=args.id, review_sha256=sha(out / 'review.json'),
          files={str(p.relative_to(destination)): sha(p) for p in destination.rglob('*') if p.is_file()},
          production_integrated=False, status='reviewed_shadow_bundle'))
    print(str(destination))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='operation', required=True)
    r = sub.add_parser('route'); r.add_argument('packet')
    r = sub.add_parser('run'); r.add_argument('packet'); r.add_argument('--id', required=True)
    r.add_argument('--model', default='gpt-6-astra')
    r.add_argument('--effort', choices=['medium', 'high', 'xhigh'], help='Explicit shadow comparison override')
    r.add_argument('--timeout', type=int, default=480)
    r.add_argument('--diagnose-from')
    r = sub.add_parser('status'); r.add_argument('id')
    r = sub.add_parser('review'); r.add_argument('id'); r.add_argument('--reviewer', required=True)
    r.add_argument('--disposition', choices=['benchmark_only', 'needs_revision', 'accepted_for_review_bundle'], required=True)
    r.add_argument('--source-note', required=True); r.add_argument('--visual-note', required=True)
    r = sub.add_parser('stage'); r.add_argument('id')
    args = p.parse_args()
    try:
        if args.operation == 'route':
            print(json.dumps(route(load_packet(args.packet)), indent=2)); return 0
        if args.operation == 'status':
            out = RUNS / identifier(args.id)
            if not (out / 'result.json').exists():
                print(json.dumps(dict(state='incomplete_preserved' if out.exists() else 'not_started')))
            else:
                _, result = verify_record(out)
                print(json.dumps(dict(state=result['state'], review=read(out / 'review.json')
                                      if (out / 'review.json').exists() else None), indent=2))
            return 0
        RUNS.mkdir(parents=True, exist_ok=True)
        with (RUNS / '.controller.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return {'run': run, 'review': review, 'stage': stage}[args.operation](args)
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print('Controller stopped: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
