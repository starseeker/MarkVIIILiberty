"""Run the existing CAD validation in durable, input-bound stages.

Only the orchestration is transformed in memory. The authored worker, every
check body and the nominal build fingerprint remain unchanged. Re-run this
command after an interruption; incomplete or changed stages run again.
"""
import argparse
import ast
from collections import Counter
import copy
import fcntl
import inspect
from pathlib import Path
import subprocess
import sys
import time
import traceback

from validation_checkpoint import Checkpoints, StageYield, digest, file_sha, write


NOMINAL = {
    'track_components': ['reports/track_components.json', 'reports/track_path.json'],
    'upper_plates': ['reports/upper_plates.json'],
    'hull_plates': ['reports/hull_plates.json'],
    'sponson_plates': ['reports/sponson_plates.json'],
    'louvers': ['reports/louvers.json'],
    'rollers': ['reports/rollers.json'],
    'lower_supports': ['reports/lower_supports.json'],
    'idler_wheels': ['reports/wheel_components.json', 'reports/idler_mounts.json',
                     'reports/drive_mounts.json', 'reports/roller_pinions.json'],
    'step': ['reports/export.json', 'exports'],
}


def statements(source):
    return ast.parse(source).body


def expression(source):
    return ast.parse(source, mode='eval').body


def report_key(node):
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        return None
    target = node.targets[0]
    if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and target.value.id == 'report':
        return target.slice.value if isinstance(target.slice, ast.Constant) else None
    return None


def guard(body, name, paths):
    result = statements(f'if _checkpoints.enter({name}, report, {paths}):\n    pass')[0]
    result.body = body + statements(f'_checkpoints.commit({name}, report, {paths})')
    return result


def transform(source):
    """Wrap complete original blocks; fail closed if worker structure changes."""
    tree = ast.parse(source)
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef) and function.name == 'validate'
    original = copy.deepcopy(function)
    body = function.body
    def find(text):
        return next(i for i, node in enumerate(body) if text in ast.unparse(node))
    start = find('Validating native definitions')
    end = next(i for i in range(start, len(body)) if isinstance(body[i], ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'report' for t in body[i].targets)) + 1
    baseline = statements("_cached = _checkpoints.get('native_baseline', [])\nif _cached is None:\n    pass\nelse:\n    baseline = _cached['baseline']\n    definition_signatures = _cached['definition_signatures']\n    report = _cached['report']")
    baseline[1].body = body[start:end] + statements("_checkpoints.put('native_baseline', dict(baseline=baseline, definition_signatures=definition_signatures, report=report), [])")
    body[start:end] = baseline
    wrapped = ['native_baseline']
    for node in body:
        key = report_key(node)
        if key in NOMINAL:
            old = node.value
            node.value = expression(f'_checkpoints.result({key!r}, lambda: None, {NOMINAL[key]!r})')
            node.value.args[1].body = old
            wrapped.append(key)
    start = find('Validating relocated native dependencies')
    end = next(i for i in range(start, len(body)) if report_key(body[i]) == 'relocated_native_links') + 1
    body[start:end] = [guard(body[start:end], repr('relocated_native'), repr(['verification/relocated_native']))]
    wrapped.append('relocated_native')
    start = find('Validating independent rebuild')
    end = next(i for i in range(start, len(body)) if report_key(body[i]) == 'cached_build_seconds') + 1
    body[start:end] = [guard(body[start:end], repr('independent_rebuild_and_cache'),
                            repr(['verification/rebuild/native', 'verification/rebuild/cache']))]
    wrapped.append('independent_rebuild_and_cache')
    for node in body:
        if not isinstance(node, ast.If) or '_checkpoints' in ast.unparse(node.test) or '_cached' in ast.unparse(node.test):
            continue
        loop = next((n for n in node.body if isinstance(n, ast.For)
                     and isinstance(n.target, ast.Tuple)
                     and any(isinstance(t, ast.Name) and t.id == 'trial' for t in n.target.elts)), None)
        if loop is not None:
            trials = [values[-1] for values in ast.literal_eval(loop.iter)]
            loop.body = [guard(loop.body, 'trial', "['verification/' + trial + '/' + p for p in ('native', 'reports', 'cache')]")]
            wrapped.extend(trials)
            continue
        keys = [report_key(n) for n in node.body if report_key(n)]
        if len(keys) == 1 and keys[0].endswith('_change'):
            key = keys[0]
            folder = 'hull_gap_change' if key == 'hull_spacing_change' else key
            paths = [f'verification/{folder}/{p}' for p in ('native', 'reports', 'cache')]
            node.body = [guard(node.body, repr(key), repr(paths))]
            wrapped.append(key)
    # Check every original raise, assertion and conditional expression survives
    # verbatim. Original bodies are reused directly, never reimplemented here.
    def checks(root):
        result = Counter()
        for node in ast.walk(root):
            if isinstance(node, (ast.Raise, ast.Assert)):
                result[ast.dump(node, include_attributes=False)] += 1
            elif isinstance(node, (ast.If, ast.IfExp, ast.While)):
                result[ast.dump(node.test, include_attributes=False)] += 1
        return result
    before, after = checks(original), checks(function)
    if before - after:
        raise ValueError('Checkpoint transform lost an original check')
    if len(wrapped) != 27 or len(set(wrapped)) != 27:
        raise ValueError('Worker stage structure changed; review checkpoint transform: ' + repr(wrapped))
    ast.fix_missing_locations(tree)
    audit = dict(stages=wrapped, original_check_expressions=sum(before.values()),
                 original_checks_preserved=True, transformed_source_sha256=digest(ast.unparse(tree)))
    return tree, audit


def worker_main(stage, out, limit):
    sys.path.insert(0, str(stage))
    from lib import runtime, worker
    from lib.evidence import FOUNDATION, fingerprint, sha
    try:
        import FreeCAD as App
        import Part
        import numpy
        import scipy
        import fitz
        build = worker.check_build(out)
        script = Path(__file__).resolve()
        binding = dict(fingerprint=fingerprint(), native_hashes=build['native_hashes'],
                       build_report_sha256=sha(out/'reports/build.json'),
                       foundation_source_lock_sha256=sha(FOUNDATION/'data/sources.json'),
                       runner_sha256=sha(script), checkpoint_sha256=sha(script.with_name('validation_checkpoint.py')),
                       runtime=dict(FreeCAD=App.Version(), OpenCASCADE=Part.OCC_VERSION,
                                    Python=sys.version, numpy=numpy.__version__, scipy=scipy.__version__,
                                    fitz=fitz.VersionBind))
        checkpoints = Checkpoints(out, binding, max_stages=limit)
        tree, audit = transform(inspect.getsource(worker.validate))
        write(checkpoints.root/'transformation.json', audit)
        (checkpoints.root/'transformed_validate.py').write_text(ast.unparse(tree)+'\n')
        worker.__dict__['_checkpoints'] = checkpoints
        exec(compile(tree, str(checkpoints.root/'transformed_validate.py'), 'exec'), worker.__dict__)
        staged_validate = worker.validate
        def validated(*args):
            result = staged_validate(*args)
            if fingerprint() != binding['fingerprint']:
                raise ValueError('Authored inputs changed while validating')
            worker.check_build(out)
            result['checkpoint_audit'] = checkpoints.finish()
            write(out/'reports/validation.json', result)
            return result
        worker.validate = validated
        worker.run('validate', out)
        return 0
    except StageYield as done:
        print('Worker completed its stage batch:', done, flush=True)
        return 75
    finally:
        runtime.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--stages-per-worker', type=int, default=3)
    args = parser.parse_args()
    stage = args.stage.resolve(); out = (args.output or stage/'build').resolve()
    if args.worker:
        return worker_main(stage, out, args.stages_per_worker)
    sys.path.insert(0, str(stage))
    from lib.runtime import environment
    runs = out/'verification/runs'; runs.mkdir(parents=True, exist_ok=True)
    with (runs/'validation.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        started = time.time(); attempt = 0
        command = [sys.executable, str(Path(__file__).resolve()), '--stage', str(stage),
                   '--output', str(out), '--worker', '--stages-per-worker', str(args.stages_per_worker)]
        with (runs/'validation.log').open('a', buffering=1) as log:
            while True:
                attempt += 1
                status = dict(complete=False, started_epoch=started, worker_attempt=attempt,
                              runner_sha256=file_sha(__file__))
                write(runs/'validation_status.json', status)
                print(f'Starting validation worker {attempt}; durable log: {log.name}', flush=True)
                log.write(f'\nValidation invocation {started}, worker {attempt}\n')
                completed = subprocess.run(command, env=environment(out), stdout=log, stderr=subprocess.STDOUT)
                if completed.returncode == 75:
                    continue
                status.update(complete=True, exit_code=completed.returncode,
                              passed=completed.returncode == 0, seconds=time.time()-started,
                              log_sha256=file_sha(log.name))
                write(runs/'validation_status.json', status)
                return completed.returncode


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
