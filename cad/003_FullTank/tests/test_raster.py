"""Exercise compiled depth clipping and occlusion with independently known planes."""
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lib.raster import paint


class RasterChecks(unittest.TestCase):
    def test_crossing_depth_planes_and_clipped_triangle(self):
        # The first surface is z=x. The second is z=5, with reversed winding.
        vertices = [[[-10,-10,-10],[30,-10,30],[-10,30,-10]],
                    [[-10,30,5],[30,-10,5],[-10,-10,5]]]
        with tempfile.TemporaryDirectory() as folder:
            pixels,depth = paint(vertices,[[255,0,0],[0,0,255]],20,20,folder)
        for y in range(20):
            for x in range(20):
                if x+y+1 <= 20:
                    self.assertEqual(list(pixels[y,x]),[0,0,255] if x+0.5<5 else [255,0,0])
                    self.assertAlmostEqual(depth[y,x],max(x+0.5,5))
                else:
                    self.assertTrue(np.isneginf(depth[y,x]))

    def test_nonfinite_or_out_of_range_coordinates_rejected(self):
        for bad in [float('nan'),float('inf'),1e300]:
            with self.assertRaisesRegex(ValueError,"Invalid raster"):
                paint([[[bad,0,0],[1,1,1],[2,0,0]]],[[0,0,0]],5,5,'/tmp/markviii_raster_rejected')


if __name__ == '__main__':
    unittest.main()
