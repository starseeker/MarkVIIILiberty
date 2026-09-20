"""Check known foreground/background planes before trusting the inspection view."""
import tempfile
import unittest

import numpy as np

from transparent_isometric import composite, paint


class TransparentViewTests(unittest.TestCase):
    def test_crossing_armor_and_opaque_planes(self):
        # Armor is the red plane z=x; opaque machinery is blue z=5.
        with tempfile.TemporaryDirectory() as folder:
            armor, armor_depth = paint([[[-10,-10,-10],[30,-10,30],[-10,30,-10]]],
                                       [[255,0,0]],20,20,folder)
            opaque, opaque_depth = paint([[[-10,30,5],[30,-10,5],[-10,-10,5]]],
                                         [[0,0,255]],20,20,folder)
        pixels = composite(opaque, opaque_depth, armor, armor_depth, .2)
        for y in range(20):
            for x in range(20):
                if x+y+1 <= 20:
                    expected = [0,0,255] if x+.5<5 else [51,0,204]
                else:
                    expected = [246,244,237]
                self.assertEqual(pixels[y,x].tolist(), expected)
        np.testing.assert_array_equal(composite(opaque,opaque_depth,armor,armor_depth,0), opaque)
        full = composite(opaque,opaque_depth,armor,armor_depth,1)
        self.assertEqual(full[0,10].tolist(), [255,0,0])
        self.assertEqual(full[0,0].tolist(), [0,0,255])

    def test_invalid_opacity(self):
        for opacity in [-.1, 1.1, float('nan')]:
            with self.assertRaises(ValueError):
                composite(None,None,None,None,opacity)


if __name__ == '__main__':
    unittest.main()
