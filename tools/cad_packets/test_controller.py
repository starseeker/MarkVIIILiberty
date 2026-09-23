"""Meaningful negative controls for routing, provenance, transport, and timeouts."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from common import ROOT, code_hashes, contained, load_packet, regular, route, sha, write
from controller import event_summary, verify_record
from isolation import execute


class ControllerTests(unittest.TestCase):
    def test_uncertainty_and_missing_review_force_xhigh(self):
        p=dict(category='reviewed_implementation',reviewed=dict(dimensions=True,sources=True,interfaces=True),risks=[])
        self.assertEqual(route(p)['effort'],'medium')
        for changed in [dict(p,category='typo'),dict(p,risks=['source_conflict']),dict(p,reviewed={})]:
            self.assertEqual(route(changed)['effort'],'xhigh')
        self.assertEqual(route(p,diagnosis=True)['effort'],'xhigh')

    def test_path_escape_symlink_and_hardlink_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);(base/'good').write_text('x')
            for name in ['../escape','/absolute']:
                with self.assertRaises(ValueError):contained(base,name)
            (base/'link').symlink_to(base/'good')
            with self.assertRaises(ValueError):regular(base/'link')
            (base/'hard').hardlink_to(base/'good')
            with self.assertRaises(ValueError):regular(base/'hard')

    def test_stale_input_rejected(self):
        p=json.loads((ROOT/'benchmarks/cad_work_packets/packets/stack.json').read_text())
        p['inputs'][0]['sha256']='0'*64
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'packet.json';write(path,p)
            with self.assertRaises(ValueError):load_packet(path)

    def test_transport_needs_one_complete_thread_and_valid_events(self):
        good=[dict(type='thread.started',thread_id='unique'),dict(type='turn.completed',usage=dict(input_tokens=100,output_tokens=20))]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'events'
            for events,expected in [(good,True),(good[:1],False),(good+[dict(type='turn.failed')],False),
                                    (good+[good[1]],False)]:
                path.write_text('\n'.join(json.dumps(e) for e in events))
                self.assertEqual(event_summary(path)['transport_ok'],expected)
            path.write_text(path.read_text()+'\nbroken')
            self.assertFalse(event_summary(path)['transport_ok'])

    def test_saved_artifact_tampering_and_extra_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);(out/'artifacts').mkdir(); artifact=out/'artifacts/data';artifact.write_text('good')
            packet=ROOT/'benchmarks/cad_work_packets/packets/stack.json'
            write(out/'request.json',dict(packet_path=str(packet),packet_sha256=sha(packet),code_hashes=code_hashes()))
            write(out/'result.json',dict(request_sha256=sha(out/'request.json'),record_hashes={'artifacts/data':sha(artifact)}))
            verify_record(out)
            artifact.write_text('bad')
            with self.assertRaises(ValueError):verify_record(out)
            artifact.write_text('good');(out/'artifacts/extra').write_text('unreviewed')
            with self.assertRaises(ValueError):verify_record(out)

    def test_timeout_is_recorded(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)
            result=execute([sys.executable,'-c','import time; time.sleep(10)'],out,out/'stdout',out/'stderr',.05)
            self.assertTrue(result['timed_out']);self.assertNotEqual(result['returncode'],0)


if __name__=='__main__':unittest.main()
