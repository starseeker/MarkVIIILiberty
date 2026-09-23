"""Exercise review/staging transitions in a temporary tree, never production."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad_packets'))
import controller
from common import code_hashes,production_hashes,sha,write


class ReviewGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name);self.runs=self.root/'runs';self.runs.mkdir()
        self.context=contextlib.ExitStack()
        self.context.enter_context(patch.object(controller,'RUNS',self.runs))
        self.context.enter_context(patch.object(controller,'ROOT',self.root))
        self.context.enter_context(contextlib.redirect_stdout(io.StringIO()))

    def tearDown(self):
        self.context.close();self.temp.cleanup()

    def fixture(self,name,passed=True):
        out=self.runs/name;(out/'artifacts/deliverables').mkdir(parents=True)
        artifact=out/'artifacts/deliverables/notes.md';artifact.write_text('Synthetic test artifact')
        packet=ROOT/'benchmarks/cad_work_packets/packets/stack.json'
        write(out/'packet.json',dict(test_fixture=True))
        write(out/'validation.json',dict(passed=passed))
        write(out/'request.json',dict(packet_path=str(packet),packet_sha256=sha(packet),code_hashes=code_hashes(),
                                      production_before=production_hashes()))
        write(out/'result.json',dict(mechanical_pass=passed,request_sha256=sha(out/'request.json'),
                                     record_hashes={'artifacts/deliverables/notes.md':sha(artifact)}))
        return out

    def review(self,name,disposition):
        return controller.review(SimpleNamespace(id=name,reviewer='test harness',disposition=disposition,
          source_note='Synthetic source review for gate testing only.',visual_note='Synthetic visual review for gate testing only.'))

    def test_failed_mechanics_cannot_be_reviewed(self):
        self.fixture('failed',False)
        with self.assertRaises(ValueError):self.review('failed','accepted_for_review_bundle')

    def test_pending_or_benchmark_only_cannot_stage(self):
        self.fixture('pending')
        with self.assertRaises(FileNotFoundError):controller.stage(SimpleNamespace(id='pending'))
        self.review('pending','benchmark_only')
        with self.assertRaises(ValueError):controller.stage(SimpleNamespace(id='pending'))

    def test_accepted_bundle_is_immutable_and_keeps_provenance(self):
        self.fixture('accepted');self.review('accepted','accepted_for_review_bundle')
        controller.stage(SimpleNamespace(id='accepted'))
        target=self.root/'cad/003_FullTank/review_bundles/accepted'
        self.assertTrue((target/'provenance.json').is_file())
        self.assertEqual((target/'artifacts/deliverables/notes.md').read_text(),'Synthetic test artifact')
        with self.assertRaises(ValueError):controller.stage(SimpleNamespace(id='accepted'))

    def test_changed_parent_or_result_invalidates_approval(self):
        out=self.fixture('stale');self.review('stale','accepted_for_review_bundle')
        with patch.object(controller,'production_hashes',return_value={'changed':'parent'}):
            with self.assertRaises(ValueError):controller.stage(SimpleNamespace(id='stale'))
        with (out/'result.json').open('a') as stream:stream.write(' ')
        with self.assertRaises(ValueError):controller.stage(SimpleNamespace(id='stale'))


if __name__=='__main__':unittest.main()
