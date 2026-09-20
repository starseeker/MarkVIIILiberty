"""Regression checks for restart, failed-stage and artifact invalidation behavior."""
import tempfile
import unittest
from pathlib import Path
from validation_checkpoint import Checkpoints,StageYield


class CheckpointTests(unittest.TestCase):
    def test_restart_reuses_only_completed_stage(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);(out/'proof').write_text('native evidence')
            first=Checkpoints(out,{'input':'a'},max_stages=1)
            with self.assertRaises(StageYield):first.result('one',lambda:42,['proof'])
            second=Checkpoints(out,{'input':'a'})
            self.assertEqual(second.result('one',lambda:self.fail('Completed stage ran again'),['proof']),42)
            self.assertEqual(second.finish()['completed_stages'],1)

    def test_failure_is_not_a_completed_stage(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);checks=Checkpoints(out,{'input':'a'})
            def fail():
                (out/'partial').write_text('unfinished')
                raise ValueError('native contact failed')
            with self.assertRaises(ValueError):checks.result('one',fail,['partial'])
            recovered=Checkpoints(out,{'input':'a'})
            self.assertIsNone(recovered.get('one',['partial']))
            self.assertEqual(recovered.result('one',lambda:43,['partial']),43)

    def test_changed_input_or_artifact_rejects_reuse(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);(out/'proof').write_text('original')
            checks=Checkpoints(out,{'input':'a'});checks.put('one',{'value':42},['proof'])
            self.assertIsNone(Checkpoints(out,{'input':'b'}).get('one',['proof']))
            (out/'proof').write_text('modified')
            self.assertIsNone(Checkpoints(out,{'input':'a'}).get('one',['proof']))
            with self.assertRaises(ValueError):checks.finish()

    def test_directory_addition_and_corrupt_receipt_reject_reuse(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);(out/'native').mkdir();(out/'native/a').write_text('a')
            checks=Checkpoints(out,{'input':'a'});checks.put('one',{'value':42},['native'])
            (out/'native/b').write_text('b')
            self.assertIsNone(Checkpoints(out,{'input':'a'}).get('one',['native']))
            (checks.root/'one.json').write_text('{interrupted receipt')
            self.assertIsNone(Checkpoints(out,{'input':'a'}).get('one',['native']))


if __name__=='__main__':unittest.main()
