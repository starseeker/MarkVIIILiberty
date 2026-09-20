"""Inferred constant-stock narrowing of the casing at the transmission end."""
import math
import FreeCAD as App
import Part
from casing_parts import capsule


def narrowed_front(old, a, detail, route, shell):
    start, end = detail['taper_start_x'], detail['taper_end_x']
    rear, front = a['outside_width'] / 2, detail['front_outside_width'] / 2
    stock = a['sheet_stock']
    slope = (front - rear) / (end - start)
    assert slope < 0
    corner_shift = stock * (math.sqrt(1 + slope * slope) - 1) / slope
    b = old.BoundBox

    def clip(inside):
        t = stock if inside else 0
        shift = corner_shift if inside else 0
        points = [(b.XMin - 1, rear - t), (start + shift, rear - t),
                  (end + shift, front - t), (b.XMax + 1, front - t)]
        xy = points + [(x, -y) for x, y in points[::-1]]
        vertices = [App.Vector(x, y, b.ZMin - 1) for x, y in xy]
        return Part.Face(Part.makePolygon(vertices + vertices[:1])).extrude(App.Vector(0, 0, b.ZLength + 2))

    big, small = route['roller_pinion_axis_xz_mm'], route['candidate_transmission_axis_xz_mm']
    radii = shell['outside_contour_radii_mm']
    outside = capsule(big, small, radii, a['outside_width']).common(clip(False))
    inside = capsule(big, small, [r - stock for r in radii], a['outside_width'] - 2 * stock).common(clip(True))
    shaped = outside.cut(inside)
    hole = Part.makeCylinder(detail['small_hub_radius'] + detail['hub_gap'], a['outside_width'] + 2,
                             App.Vector(small[0], -rear - 1, small[1]), App.Vector(0, 1, 0))
    shaped = shaped.cut(hole)
    split = start - 10
    front_box = Part.makeBox(b.XMax - split + 1, b.YLength + 2, b.ZLength + 2,
                             App.Vector(split, b.YMin - 1, b.ZMin - 1))
    retained = old.cut(front_box)
    result = retained.fuse(shaped.common(front_box)).removeSplitter()
    if not result.isValid() or len(result.Solids) != 1:
        raise ValueError('Invalid/disconnected narrowed casing')
    rear_box = Part.makeBox(split - b.XMin, b.YLength + 2, b.ZLength + 2,
                            App.Vector(b.XMin, b.YMin - 1, b.ZMin - 1))
    unchanged = result.common(rear_box).cut(old).Volume + old.common(rear_box).cut(result).Volume
    thickness = []
    for x in [start - 5, (start + end) / 2, end + 5, small[0]]:
        half = rear if x < start else front if x > end else rear + slope * (x - start)
        derivative = slope if start < x < end else 0
        for side in [-1, 1]:
            point = App.Vector(x, side * half, small[1] + 130)
            normal = App.Vector(-derivative, side, 0)
            normal.normalize()
            line = Part.makeLine(point + normal, point - normal * (stock + 1))
            cut = result.common(line)
            lengths = [edge.Length for edge in cut.Edges]
            thickness.append(dict(x_mm=x, side=side, thickness_segments_mm=lengths,
                                  passed=len(lengths) == 1 and abs(lengths[0] - stock) < 1e-6))
    return result, dict(rear_region_symmetric_difference_mm3=unchanged,
                        taper_slope=slope, inside_corner_shift_mm=corner_shift,
                        removed_volume_mm3=old.cut(result).Volume,
                        added_volume_mm3=result.cut(old).Volume,
                        sheet_thickness_checks=thickness)
