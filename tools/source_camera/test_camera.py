"""Independent known-camera, failure and reuse tests; no historical inference."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'cad/003_FullTank'))
from lib import source_camera as sc


class CameraTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.source = self.folder/'source.png'; Image.new('RGB', (1000,800)).save(self.source)
        self.world = np.random.default_rng(17).uniform(-200,200,(24,3))
        self.rotation = Rotation.from_euler('xyz',[12,24,8],degrees=True).as_matrix()

    def packet(self, projection='perspective'):
        # Compute expected pixels independently of the implementation projector.
        q = (self.world-[35,-20,-950])@self.rotation.T
        if projection == 'perspective': uv = q[:,:2]*1100/q[:,2,None]+[500,400]
        elif projection == 'orthographic': uv = q[:,:2]*1.1+[500,400]
        else: uv = self.world@np.array([[1,.2,.1],[-.1,.8,.4]]).T+[500,400]
        return dict(source_image=str(self.source),source_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest(),
            image_size_px=[1000,800],projection=projection,geometry_context={'native_sha256':'initial'},
            landmarks=[dict(id=str(i),world_mm=w.tolist(),pixel=p.tolist(),sigma_px=2.,use='fit' if i<16 else 'holdout')
                       for i,(w,p) in enumerate(zip(self.world,uv))])

    def test_known_cameras_and_holdouts(self):
        for projection in ['perspective','orthographic','oblique_affine']:
            with self.subTest(projection=projection):
                packet = self.packet(projection); camera = sc.fit(packet)
                a = sc.assess(camera,packet['landmarks'])
                self.assertLess(a['holdout']['max_px'],1e-6)
                if projection=='perspective':
                    self.assertAlmostEqual(camera['focal_px'],1100,places=5)
                    np.testing.assert_allclose(camera['origin_world_mm'],[35,-20,-950],atol=1e-5)
                    np.testing.assert_allclose(camera['world_to_camera_rotation'],self.rotation,atol=1e-8)

    def test_new_geometry_and_conflicting_holdout_reuse_fixed_camera(self):
        packet = self.packet(); first = sc.cached_fit(packet,self.folder/'cache')
        packet['geometry_context']['native_sha256']='new_unrelated_parts'
        packet['landmarks'][-1]['pixel'][0] += 90
        with patch.object(sc,'fit',side_effect=AssertionError('Must not refit')):
            again = sc.cached_fit(packet,self.folder/'cache')
        self.assertTrue(again['reused']); self.assertEqual(first['camera'],again['camera'])
        self.assertIn('holdout_missing_or_conflicting',again['issues'])
        self.assertEqual(first['fit_key'],again['fit_key'])

    def test_anchor_change_requires_review_and_preserves_previous_fit(self):
        packet = self.packet(); first = sc.cached_fit(packet,self.folder/'cache')
        old_bytes=Path(first['fit_record']).read_bytes()
        packet['landmarks'][0]['world_mm'][0] += 1
        packet['previous_fit_key']=first['fit_key']
        with self.assertRaisesRegex(ValueError,'refit reason'): sc.cached_fit(packet,self.folder/'cache')
        packet['refit_review']={'reason':'Confirmed datum moved in revised assembly','reviewer':'test'}
        second = sc.cached_fit(packet,self.folder/'cache')
        self.assertNotEqual(first['fit_key'],second['fit_key'])
        self.assertEqual(Path(first['fit_record']).read_bytes(),old_bytes)
        packet.pop('refit_review')
        with self.assertRaisesRegex(ValueError,'refit reason'): sc.cached_fit(packet,self.folder/'cache')

    def test_image_change_size_and_tampering_rejected(self):
        packet=self.packet(); result=sc.cached_fit(packet,self.folder/'cache')
        bad=copy.deepcopy(packet);bad['image_size_px']=[800,1000]
        with self.assertRaisesRegex(ValueError,'dimensions'): sc.cached_fit(bad,self.folder/'cache')
        path=Path(result['fit_record']);record=json.loads(path.read_text());record['camera']['focal_px']+=3
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError,'record changed'): sc.cached_fit(packet,self.folder/'cache')
        Image.new('RGB',(1000,800),'red').save(self.source)
        with self.assertRaisesRegex(ValueError,'Source image changed'): sc.cached_fit(packet,self.folder/'cache')

    def test_unsupported_evidence_rejected(self):
        packet=self.packet()
        for row in packet['landmarks']: row['world_mm'][2]=0
        with self.assertRaisesRegex(ValueError,'planar'): sc.fit(packet)
        packet=self.packet();packet['landmarks']=packet['landmarks'][:7]
        with self.assertRaisesRegex(ValueError,'at least 8'): sc.fit(packet)
        with self.assertRaisesRegex(ValueError,'near plane'):
            sc.project_camera(np.array([[1,2,-1.]]),dict(projection='perspective'))

    def test_wrong_projection_and_missing_holdouts_flagged(self):
        packet=self.packet();packet['projection']='orthographic'
        result=sc.cached_fit(packet,self.folder/'cache')
        self.assertIn('holdout_missing_or_conflicting',result['issues'])
        packet=self.packet();packet['landmarks']=packet['landmarks'][:16]
        result=sc.cached_fit(packet,self.folder/'cache')
        self.assertIn('holdout_missing_or_conflicting',result['issues'])

    def test_robust_fit_does_not_hide_outlier(self):
        packet=self.packet();packet['landmarks'][0]['pixel'][0]+=12
        result=sc.cached_fit(packet,self.folder/'cache')
        self.assertFalse(result['assessment']['fit_consistent_with_pick_uncertainty'])
        self.assertIn('fitting_residuals_exceed_uncertainty',result['issues'])

    def test_perspective_occlusion_uses_reciprocal_depth(self):
        from lib.raster import paint
        pixel=np.array([[100.,100.],[500.,100.],[100.,500.]])
        camera=dict(projection='perspective',focal_px=100.,principal_px=[0.,0.])
        surfaces=[]
        for z in [np.array([2.,20.,20.]),np.full(3,4.)]:
            points=np.column_stack([pixel*z[:,None]/100,z])
            surfaces.append(sc.project_camera(points,camera))
        bitmap,_=paint(np.array(surfaces),np.array([[255,0,0],[0,0,255]],dtype=np.uint8),600,600,self.folder)
        self.assertEqual(bitmap[150,150].tolist(),[255,0,0])
        self.assertEqual(bitmap[200,280].tolist(),[0,0,255])


if __name__=='__main__': unittest.main()
