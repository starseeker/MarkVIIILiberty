"""Deterministic local CAD stages with evidence-bound reuse and compact reports.

This trusted-project runner invokes no model and never promotes a candidate.
Source interpretation and visual acceptance remain separately recorded reviews.
"""
import argparse
import ast
import fcntl
import glob
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/cad_packets'))
from common import digest, identifier, read, regular, sha, write


def substitute(value, variables):
    for name, replacement in variables.items():
        value = value.replace('{'+name+'}', replacement)
    return value


def files(patterns, variables, output=False, allow_missing=False):
    result = {}
    run = Path(variables['run']).resolve()
    for pattern in patterns:
        expanded = substitute(pattern, variables)
        if output and ('..' in Path(expanded).parts or not Path(expanded).resolve().is_relative_to(run)):
            raise ValueError('Stage output pattern escapes run directory: '+expanded)
        matches = sorted(glob.glob(expanded, recursive=True))
        matches = [Path(p) for p in matches if not Path(p).is_dir()]
        if not matches and not allow_missing:
            raise ValueError('Missing declared file: '+expanded)
        for path in matches:
            path = regular(path)
            if output and not path.resolve().is_relative_to(run):
                raise ValueError('Stage output escapes run directory: '+str(path))
            result[str(path.resolve())] = sha(path)
    return result


def pointer(value, path):
    if path == '':
        return value
    for key in path.lstrip('/').split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def python_sources(entries, search_paths):
    """Hash the local static import closure; dynamic/data inputs stay explicit."""
    pending = [Path(p).resolve() for p in entries]
    roots = [Path(p).resolve() for p in search_paths]
    result = {}

    def modules(base, name):
        parts = name.split('.') if name else []
        found = []
        for i in range(len(parts)+1):
            package = base.joinpath(*parts[:i])/'__init__.py'
            if package.is_file(): found.append(package)
        target = base.joinpath(*parts)
        if parts and target.with_suffix('.py').is_file(): found.append(target.with_suffix('.py'))
        return found

    while pending:
        path = regular(pending.pop()).resolve()
        if str(path) in result: continue
        result[str(path)] = sha(path)
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for base in roots:
                        pending.extend(modules(base, alias.name))
            elif isinstance(node, ast.ImportFrom):
                bases = roots
                if node.level:
                    base = path.parent
                    for _ in range(node.level-1): base = base.parent
                    bases = [base]
                for base in bases:
                    pending.extend(modules(base, node.module or ''))
                    for alias in node.names:
                        if alias.name != '*':
                            name = '.'.join(x for x in (node.module, alias.name) if x)
                            pending.extend(modules(base, name))
    return result


def receipts(stage, variables):
    outputs = files(stage['outputs'], variables, output=True)
    for spec in stage.get('receipts', []):
        path = Path(substitute(spec['file'], variables))
        if str(path.resolve()) not in outputs:
            raise ValueError('Receipt is not a declared output: '+str(path))
        data = read(regular(path))
        for check in spec['checks']:
            actual = pointer(data, check['pointer'])
            expected = sha(regular(substitute(check['sha256_file'], variables))) if 'sha256_file' in check else check['equals']
            if type(actual) is not type(expected) or actual != expected:
                raise ValueError(f'Receipt failed: {path.name}{check["pointer"]}: {actual!r}')


def load_plan(path):
    plan = read(regular(path))
    if plan.get('version') != 1 or plan.get('mode') != 'local_development':
        raise ValueError('Expected version1 local_development plan')
    identifier(plan['id'])
    seen = set()
    for stage in plan['stages']:
        identifier(stage['id'])
        if stage['id'] in seen or not set(stage.get('needs', [])).issubset(seen):
            raise ValueError('Stages must be unique and in dependency order')
        seen.add(stage['id'])
        for key in ('command', 'inputs', 'outputs'):
            if not isinstance(stage.get(key), list) or not stage[key] or not all(isinstance(x, str) for x in stage[key]):
                raise ValueError('Missing/non-string '+key+' for '+stage['id'])
        if not 0 < stage.get('timeout_seconds', 1800) <= 43200:
            raise ValueError('Invalid stage timeout')
        if not isinstance(stage.get('reentrant', False), bool):
            raise ValueError('reentrant must be boolean')
    return plan


def execute(command, cwd, log, timeout, lock_fd):
    start = time.monotonic()
    process = None
    try:
        with log.open('wb') as stream:
            # Children retain the run lock if the controller is killed. A new
            # invocation cannot duplicate an orphaned worker while it executes.
            process = subprocess.Popen(command, cwd=cwd, stdout=stream,
                stderr=subprocess.STDOUT, start_new_session=True, pass_fds=(lock_fd,))
            try:
                code = process.wait(timeout=timeout)
                return dict(returncode=code, timed_out=False, elapsed_seconds=time.monotonic()-start)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                return dict(returncode=process.returncode, timed_out=True,
                            elapsed_seconds=time.monotonic()-start)
    except BaseException:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        raise


def runtime(plan, variables, area, lock_fd):
    spec = plan['runtime']
    log = area / 'runtime_probe.log'
    result = execute([substitute(s, variables) for s in spec['command']],
                     variables['root'], log, 60, lock_fd)
    if result['returncode'] or result['timed_out']:
        raise ValueError('Runtime probe failed; see '+str(log))
    probe = json.loads(log.read_text())
    for check in spec.get('checks', []):
        if pointer(probe, check['pointer']) != check['equals']:
            raise ValueError('Runtime differs from qualified plan: '+check['pointer'])
    resolved = [str(Path(substitute(p, variables)).resolve()) for p in spec.get('files', [])]
    return dict(probe=probe, files=files(resolved, variables),
                resolved_files={substitute(p, variables): str(Path(substitute(p, variables)).resolve())
                                for p in spec.get('files', [])},
                python=sys.version, executable=str(Path(sys.executable).resolve()))


def signature(stage, plan, variables, runtime_record):
    return dict(stage=stage, common_inputs=files(plan.get('common_inputs', []), variables),
                inputs=files(stage['inputs'], variables), runtime=runtime_record, runtime_spec=plan['runtime'],
                environment={key: os.environ.get(key) for key in plan.get('environment_keys', [])},
                python_sources=python_sources([substitute(x, variables) for x in stage.get('python_sources', [])],
                    [substitute(x, variables) for x in plan.get('python_paths', [])]),
                runner_sha256=sha(Path(__file__)),
                record_helpers_sha256=sha(ROOT / 'tools/cad_packets/common.py'))


def reusable(record, identity, stage, variables):
    if not record or record.get('status') != 'passed' or record.get('identity') != identity:
        return False
    try:
        if files(stage['outputs'], variables, output=True) != record['outputs']:
            return False
        receipts(stage, variables)
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return False
    return True


def locked(path):
    if not path.exists():
        return False
    with path.open('r') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(lock, fcntl.LOCK_UN)
            return False
        except BlockingIOError:
            return True


def compact(area):
    state = read(area / 'state.json') if (area / 'state.json').exists() else {}
    held = locked(area / 'run.lock')
    observed = 'worker_lock_held' if held else 'no_worker_lock'
    if state.get('status') == 'running' and not held:
        observed = 'interrupted_or_missing_terminal_record'
    return dict(run=area.parent.name, recorded_status=state.get('status', 'not_started'),
                observation=observed, current_stage=state.get('current_stage'),
                stages=state.get('stages', []), metrics=state.get('metrics', {}),
                error=state.get('error'), review_required=True,
                evidence_freshness='not rechecked by status',
                note='Status reports saved outcomes and the current worker lock; use verify to recheck evidence.')


def verify(run_id, root=ROOT):
    """Read-only freshness audit; does not launch CAD or consume model inference."""
    identifier(run_id)
    workspace = Path(root).resolve() / '.work/cad-pipeline' / run_id
    area = workspace / 'records'
    if locked(area / 'run.lock'):
        raise ValueError('Worker is live; poll status instead of reading changing outputs')
    state = read(area / 'state.json')
    plan = load_plan(state['plan'])
    variables = dict(root=str(Path(root).resolve()), run=str(workspace), python=sys.executable)
    rt = read(area / 'runtime.json')
    current_runtime_files = {str(Path(substitute(p, variables)).resolve()): sha(Path(substitute(p, variables)).resolve())
                             for p in plan['runtime'].get('files', [])}
    aliases = {substitute(p, variables): str(Path(substitute(p, variables)).resolve())
               for p in plan['runtime'].get('files', [])}
    runtime_current = current_runtime_files == rt['files'] and aliases == rt['resolved_files'] and sys.version == rt['python']
    rows = []
    current = {}
    for stage in plan['stages']:
        try:
            record = read(area / stage['id'] / 'latest.json')
            valid = runtime_current and reusable(record, digest(signature(stage, plan, variables, rt)), stage, variables)
            valid = valid and all(current[n] for n in stage.get('needs', []))
            reason = None if valid else 'Stale/missing inputs, outputs, runtime, result or dependency'
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            valid, reason = False, str(exc)
        current[stage['id']] = valid
        rows.append(dict(id=stage['id'], current=valid, reason=reason))
    return dict(run=run_id, evidence_current=all(current.values()), stages=rows,
                model_invocations=0, review_required=True, production_promoted=False)


def run(plan_path, run_id, root=ROOT):
    identifier(run_id)
    root = Path(root).resolve()
    plan_path = Path(plan_path).resolve()
    plan = load_plan(plan_path)
    workspace = root / '.work/cad-pipeline' / run_id
    area = workspace / 'records'
    area.mkdir(parents=True, exist_ok=True)
    variables = dict(root=str(root), run=str(workspace), python=sys.executable)
    state = dict(status='running', plan=str(plan_path), plan_sha256=sha(plan_path),
                 current_stage=None, stages=[], metrics=dict(executed=0, reused=0, failures=0,
                    execution_seconds=0., reused_prior_execution_seconds=0., model_invocations=0,
                    orchestrating_assistant_usage='not measured by deterministic runner'))
    identity_path = area / 'run_identity.json'
    with (area / 'run.lock').open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('Run/worker is still live; do not restart it') from exc
        previous_state = read(area / 'state.json') if (area / 'state.json').exists() else {}
        invocation = len(list(area.glob('invocation_*.json'))) + 1
        if identity_path.exists():
            if read(identity_path) != dict(plan_id=plan['id'], workspace=str(workspace)):
                raise ValueError('Run ID belongs to a different plan')
        else:
            write(identity_path, dict(plan_id=plan['id'], workspace=str(workspace)))
        write(area / 'state.json', state)
        try:
            rt = runtime(plan, variables, area, lock.fileno())
            write(area / 'runtime.json', rt)
            for stage in plan['stages']:
                name = stage['id']
                state['current_stage'] = name
                write(area / 'state.json', state)
                folder = area / name
                folder.mkdir(exist_ok=True)
                latest = folder / 'latest.json'
                previous = read(latest) if latest.exists() else None
                existing_outputs = files(stage['outputs'], variables, output=True, allow_missing=True)
                sig = signature(stage, plan, variables, rt)
                identity = digest(sig)
                if reusable(previous, identity, stage, variables):
                    state['metrics']['reused'] += 1
                    state['metrics']['reused_prior_execution_seconds'] += previous['execution']['elapsed_seconds']
                    state['stages'].append(dict(id=name, status='reused', evidence=str(latest)))
                    print(name+': reused', flush=True)
                    write(area / 'state.json', state)
                    continue
                if not stage.get('reentrant', False) and (previous or existing_outputs or
                        previous_state.get('current_stage') == name and previous_state.get('status') == 'running'):
                    raise ValueError('Immutable stage '+name+' needs a fresh run ID; previous evidence retained')
                attempt = len(list(folder.glob('attempt_*'))) + 1
                attempt_dir = folder / ('attempt_'+str(attempt).zfill(3))
                attempt_dir.mkdir()
                # Keep exact prior output bytes for an intentionally reentrant
                # derived stage. No native parent or whole repository is copied.
                old_outputs = existing_outputs
                if old_outputs:
                    import shutil
                    for path in old_outputs:
                        source = Path(path)
                        if source.is_file():
                            dest = attempt_dir / 'prior_outputs' / source.relative_to(workspace)
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source, dest)
                record = dict(status='running', identity=identity, signature=sig,
                              command=[substitute(s, variables) for s in stage['command']],
                              started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                              log=str(attempt_dir / 'run.log'))
                write(attempt_dir / 'record.json', record)
                write(latest, record)
                print(name+': running', flush=True)
                result = execute(record['command'], root, Path(record['log']),
                                 stage.get('timeout_seconds', 1800), lock.fileno())
                record['execution'] = result
                state['metrics']['executed'] += 1
                state['metrics']['execution_seconds'] += result['elapsed_seconds']
                if result['returncode'] or result['timed_out']:
                    record['status'] = 'failed'
                    write(attempt_dir / 'record.json', record); write(latest, record)
                    raise ValueError('Stage '+name+' failed; see '+record['log'])
                try:
                    if signature(stage, plan, variables, rt) != sig:
                        raise ValueError('Declared stage inputs changed during execution')
                    record['outputs'] = files(stage['outputs'], variables, output=True)
                    receipts(stage, variables)
                    record['status'] = 'passed'
                except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
                    record.update(status='failed', error=str(exc))
                    write(attempt_dir / 'record.json', record); write(latest, record)
                    raise
                write(attempt_dir / 'record.json', record); write(latest, record)
                state['stages'].append(dict(id=name, status='passed', evidence=str(latest)))
                write(area / 'state.json', state)
                print(name+': passed', flush=True)
            state.update(status='mechanical_stages_passed_review_required', current_stage=None)
        except BaseException as exc:
            state.update(status='interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed',
                         error=str(exc))
            state['metrics']['failures'] += 1
            raise
        finally:
            write(area / 'state.json', state)
            write(area / ('invocation_'+str(invocation).zfill(3)+'.json'), state)
    return compact(area)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='operation', required=True)
    r = sub.add_parser('run'); r.add_argument('plan', type=Path); r.add_argument('--id', required=True)
    s = sub.add_parser('status'); s.add_argument('id')
    v = sub.add_parser('verify'); v.add_argument('id')
    a = p.parse_args()
    if a.operation == 'run':
        print(json.dumps(run(a.plan, a.id), indent=2))
    elif a.operation == 'verify':
        result = verify(a.id)
        print(json.dumps(result, indent=2))
        if not result['evidence_current']:
            raise SystemExit(1)
    else:
        identifier(a.id)
        print(json.dumps(compact(ROOT / '.work/cad-pipeline' / a.id / 'records'), indent=2))


if __name__ == '__main__':
    main()
