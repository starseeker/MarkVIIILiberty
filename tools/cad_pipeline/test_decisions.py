import copy
import json
from pathlib import Path
import tempfile
import unittest
import decisions

class DecisionTests(unittest.TestCase):
    def test_reopen_only_changed_dependency_and_never_resolve_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=root/'context.json';p.write_text(json.dumps({'frame':[1,2,3],'neighbor':4}))
            d={'path':'context.json','pointer':'/frame'};d['sha256']=decisions.dependency_hash(d,root)
            row=dict(id='approx',status='reviewed_approximation',scope='local static',reason='source review',
                     uncertainty='documented',limits='no service qualification',reopen_when=['changed interface'],dependencies=[d],review='test')
            ledger={'decisions':[row,dict(copy.deepcopy(row),id='identity',status='open_identity')]}
            p.write_text(json.dumps({'frame':[1,2,3],'neighbor':99}))
            report=decisions.inspect(ledger,root);self.assertTrue(report['all_dependencies_current'])
            self.assertEqual(report['decisions'][1]['action'],'retain_open')
            p.write_text(json.dumps({'frame':[1,2,4],'neighbor':99}))
            report=decisions.inspect(ledger,root);self.assertFalse(report['all_dependencies_current'])
            self.assertTrue(all(v['action']=='reopen_review' for v in report['decisions']))

if __name__=='__main__': unittest.main()
