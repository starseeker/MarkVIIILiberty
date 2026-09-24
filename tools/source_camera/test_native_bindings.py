"""Check actual FCStd archive/placement bindings against deliberate corruption."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'cad/003_FullTank'))
from lib.camera_review import resolve_packet,validate_native_bindings

class NativeBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=json.loads((ROOT/'benchmarks/source_camera/20260924/native_control/packet.json').read_text())
        cls.packet,cls.manifest=resolve_packet(cls.packet)

    def test_changed_frame_rejected(self):
        m=copy.deepcopy(self.manifest);name=self.packet['landmarks'][0]['anchor']['occurrence']
        row=next(v for v in m['occurrences'] if v['name']==name);row['frame'][3]+=1
        with self.assertRaisesRegex(ValueError,'Native placement differs'): validate_native_bindings(self.packet,m)

    def test_changed_archive_shape_rejected(self):
        m=copy.deepcopy(self.manifest);name=self.packet['landmarks'][0]['anchor']['occurrence']
        row=next(v for v in m['occurrences'] if v['name']==name)
        m['definitions'][row['definition']]['brep_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Native shape differs'): validate_native_bindings(self.packet,m)

    def test_changed_anchor_definition_requires_locator_review(self):
        p=copy.deepcopy(self.packet);p['landmarks'][0]['anchor']['definition_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Anchor definition changed'): resolve_packet(p)

if __name__=='__main__': unittest.main()
