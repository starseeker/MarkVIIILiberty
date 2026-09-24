"""Exercise freshness, failures and orphan-worker exclusion with real processes."""
import contextlib
import fcntl
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

import pipeline


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name, value in [('shape.txt', 'shape1'), ('neighbor.txt', 'neighbor1'), ('runtime.txt', 'runtime1')]:
            (self.root/name).write_text(value)
        self.builder = self.root/'builder.py'
        self.builder.write_text('''import pathlib,sys
root,out=map(pathlib.Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=True)
(out/'shape.txt').write_text((root/'shape.txt').read_text())
''')
        self.checker = self.root/'checker.py'
        self.checker.write_text('''import pathlib,sys,json,hashlib
root,out=map(pathlib.Path,sys.argv[1:])
shape=out/'shape.txt'
(out/'check.json').write_text(json.dumps({'passed':True,'native_sha256':hashlib.sha256(shape.read_bytes()).hexdigest(),'neighbor':(root/'neighbor.txt').read_text()}))
''')
        self.plan = dict(version=1, mode='local_development', id='fixture',
            runtime=dict(command=['{python}', '-c', 'print("{}")'], files=['{root}/runtime.txt']),
            stages=[dict(id='build', command=['{python}', '{root}/builder.py', '{root}', '{run}/candidate'],
                inputs=['{root}/builder.py', '{root}/shape.txt'], outputs=['{run}/candidate/shape.txt']),
                dict(id='check', needs=['build'], reentrant=True,
                    command=['{python}', '{root}/checker.py', '{root}', '{run}/candidate'],
                    inputs=['{root}/checker.py', '{root}/neighbor.txt', '{run}/candidate/shape.txt'],
                    outputs=['{run}/candidate/check.json'], receipts=[dict(file='{run}/candidate/check.json', checks=[
                        dict(pointer='/passed', equals=True),
                        dict(pointer='/native_sha256', sha256_file='{run}/candidate/shape.txt')])])])
        self.path = self.root/'plan.json'
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.plan))

    def run_plan(self, name='case'):
        with contextlib.redirect_stdout(io.StringIO()):
            return pipeline.run(self.path, name, self.root)

    def test_identical_run_reuses_without_execution(self):
        first = self.run_plan()
        second = self.run_plan()
        self.assertEqual(first['metrics']['executed'], 2)
        self.assertEqual(second['metrics']['executed'], 0)
        self.assertEqual(second['metrics']['reused'], 2)
        self.assertTrue(pipeline.verify('case', self.root)['evidence_current'])

    def test_neighbor_or_checker_changes_only_rerun_context(self):
        self.run_plan()
        (self.root/'neighbor.txt').write_text('moved neighbor')
        self.assertFalse(pipeline.verify('case', self.root)['evidence_current'])
        second = self.run_plan()
        self.assertEqual(second['metrics']['executed'], 1)
        self.assertEqual(second['metrics']['reused'], 1)
        self.checker.write_text(self.checker.read_text()+'\n# corrected checker revision\n')
        third = self.run_plan()
        self.assertEqual(third['metrics']['executed'], 1)
        self.assertEqual(len(list((self.root/'.work/cad-pipeline/case/records/check').glob('attempt_*/prior_outputs/**/check.json'))), 2)

    def test_tampered_native_or_changed_source_requires_new_build(self):
        self.run_plan()
        out = self.root/'.work/cad-pipeline/case/candidate/shape.txt'
        out.write_text('tampered')
        self.assertFalse(pipeline.verify('case', self.root)['evidence_current'])
        with self.assertRaisesRegex(ValueError, 'fresh run ID'):
            self.run_plan()
        self.assertEqual(out.read_text(), 'tampered')
        self.assertEqual(self.run_plan('fresh')['metrics']['executed'], 2)
        (self.root/'shape.txt').write_text('new design')
        with self.assertRaisesRegex(ValueError, 'fresh run ID'):
            self.run_plan('fresh')

    def test_false_receipt_even_with_zero_exit_fails(self):
        self.checker.write_text(self.checker.read_text().replace("'passed':True", "'passed':False"))
        with self.assertRaisesRegex(ValueError, 'Receipt failed'):
            self.run_plan()
        self.assertFalse(pipeline.verify('case', self.root)['evidence_current'])
        self.checker.write_text(self.checker.read_text().replace("'passed':False", "'passed':1"))
        with self.assertRaisesRegex(ValueError, 'Receipt failed'):
            self.run_plan()

    def test_wrong_native_binding_is_rejected(self):
        self.checker.write_text(self.checker.read_text().replace('hashlib.sha256(shape.read_bytes()).hexdigest()', "'wrong-native'"))
        with self.assertRaisesRegex(ValueError, 'native_sha256'):
            self.run_plan()

    def test_transitive_python_change_invalidates_the_relevant_stage(self):
        helper = self.root/'helper.py'; helper.write_text('VALUE=1\n')
        self.checker.write_text('import helper\n'+self.checker.read_text())
        self.plan['python_paths'] = ['{root}']
        self.plan['stages'][1]['python_sources'] = ['{root}/checker.py']
        self.save(); self.run_plan()
        helper.write_text('VALUE=2\n')
        self.assertFalse(pipeline.verify('case', self.root)['evidence_current'])
        result = self.run_plan()
        self.assertEqual(result['metrics']['executed'], 1)
        self.assertEqual(result['metrics']['reused'], 1)

    def test_input_mutation_during_execution_is_rejected(self):
        self.checker.write_text(self.checker.read_text()+"\n(root/'neighbor.txt').write_text('changed during check')\n")
        with self.assertRaisesRegex(ValueError, 'inputs changed'):
            self.run_plan()

    def test_runtime_change_invalidates_reuse(self):
        self.run_plan()
        (self.root/'runtime.txt').write_text('runtime2')
        self.assertFalse(pipeline.verify('case', self.root)['evidence_current'])
        with self.assertRaisesRegex(ValueError, 'fresh run ID'):
            self.run_plan()

    def test_timeout_has_terminal_failure_and_releases_lock(self):
        self.checker.write_text('import time;time.sleep(10)')
        self.plan['stages'][1]['timeout_seconds'] = .05
        self.save()
        with self.assertRaisesRegex(ValueError, 'Stage check failed'):
            self.run_plan()
        area = self.root/'.work/cad-pipeline/case/records'
        self.assertFalse(pipeline.locked(area/'run.lock'))
        self.assertTrue(pipeline.read(area/'check/latest.json')['execution']['timed_out'])

    def test_output_escape_rejected_before_launch(self):
        self.plan['stages'][0]['outputs'] = ['{root}/outside.txt']
        self.save()
        with self.assertRaisesRegex(ValueError, 'escapes run'):
            self.run_plan()
        self.assertFalse((self.root/'.work/cad-pipeline/case/candidate').exists())

    def test_orphan_worker_keeps_lock_after_controller_is_killed(self):
        self.builder.write_text('''import pathlib,os,sys,time
root,out=map(pathlib.Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=True)
(out/'child.pid').write_text(str(os.getpid()))
time.sleep(20)
''')
        code = 'import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import pipeline;pipeline.run(Path(sys.argv[2]),"orphan",Path(sys.argv[3]))'
        parent = subprocess.Popen([sys.executable, '-c', code, str(Path(pipeline.__file__).parent), str(self.path), str(self.root)],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pidfile = self.root/'.work/cad-pipeline/orphan/candidate/child.pid'
        child = None
        try:
            deadline = time.monotonic()+5
            while not pidfile.exists() and time.monotonic() < deadline:
                time.sleep(.02)
            self.assertTrue(pidfile.exists())
            child = int(pidfile.read_text())
            parent.kill(); parent.wait(timeout=5)
            area = self.root/'.work/cad-pipeline/orphan/records'
            self.assertTrue(pipeline.locked(area/'run.lock'))
            with self.assertRaisesRegex(ValueError, 'still live'):
                self.run_plan('orphan')
            os.killpg(child, signal.SIGKILL)
            deadline = time.monotonic()+5
            while pipeline.locked(area/'run.lock') and time.monotonic() < deadline:
                time.sleep(.02)
            self.assertFalse(pipeline.locked(area/'run.lock'))
            self.assertEqual(pipeline.compact(area)['observation'], 'interrupted_or_missing_terminal_record')
        finally:
            if parent.poll() is None: parent.kill(); parent.wait()
            if child:
                with contextlib.suppress(ProcessLookupError): os.killpg(child, signal.SIGKILL)


if __name__ == '__main__':
    unittest.main()
