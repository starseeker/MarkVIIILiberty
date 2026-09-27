"""Conditional selector jaws with a radial passage and tangential drive walls.

This is an interface hypothesis, pending the complete handle reconstruction.
Keep the journal and lower linkage geometry identical to the accepted parent.
"""
import FreeCAD as App
import Part
from driver_control_linkage_parts_v3 import strut
from driver_low_selector_parts import axle, prism

V = App.Vector
X, Y = V(1, 0, 0), V(0, 1, 0)


def selector(old, proposed, side, kind):
    d = V(*old['selector_gate_direction'])
    n = V(-d.z, 0, d.x)
    t = old['selector_web_stock']
    center = (old['selector_gate_lower_radius'] + old['selector_gate_upper_radius']) / 2
    lo = center - proposed['jaw_radial_halfspan_mm']
    hi = center + proposed['jaw_radial_halfspan_mm']
    half = proposed['jaw_tangential_halfspan_mm']
    wall = proposed['jaw_wall_mm']
    sign = 1 if side == 'Port' else -1
    high = kind == 'High'
    eye = V(*old['bell_relative_to_main' if high else 'front_relative_to_main'])

    shape = axle(old['selector_hub_radius'], old['selector_journal_width'], V())
    shape = shape.fuse(strut(V(), d * hi, old['selector_gate_halfwidth'], t))
    shape = shape.fuse(strut(V(), eye, 15 if high else 16, 12.7))
    shape = shape.fuse(axle(17 if high else 23, 12.7, eye))
    shape = shape.fuse(prism(d, n, lo, hi, half, -t / 2, t / 2))
    reach = (sign * old['selector_gate_outward_depth'] if high
             else -sign * old['selector_gate_inward_depth'])
    opposite = -sign * t / 2 if high else sign * t / 2
    y0, y1 = sorted([reach, opposite])
    for direction in [-1, 1]:
        lip = prism(d, n, lo, hi, wall / 2, y0, y1)
        lip.translate(n * direction * (half - wall / 2))
        shape = shape.fuse(lip)
    shape = shape.cut(axle(old['selector_journal_radius'], 200, V()))
    shape = shape.cut(axle(6.5 if high else old['pin_radius'] + .1, 200, eye))
    shape = shape.cut(Part.makeCylinder(1.5, 34, V(), -X))
    cleaned = shape.copy().removeSplitter()
    assert cleaned.isValid() and len(cleaned.Solids) == 1
    return cleaned
