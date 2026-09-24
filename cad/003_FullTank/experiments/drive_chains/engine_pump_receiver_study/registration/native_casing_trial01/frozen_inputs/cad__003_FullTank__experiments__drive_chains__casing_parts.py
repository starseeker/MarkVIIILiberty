"""Analytic sheet casing and removable cap, with explicit inferred contours."""
import math
import FreeCAD as App
import Part


def capsule(big, small, radii, width):
    """Convex hull of unequal XZ circles, extruded along Y."""
    dx, dz = small[0] - big[0], small[1] - big[1]
    distance = math.hypot(dx, dz)
    ux, uz = dx / distance, dz / distance
    q = (radii[0] - radii[1]) / distance
    assert abs(q) < 1
    v = math.sqrt(1 - q * q)
    normals = [(q * ux - v * uz, q * uz + v * ux),
               (q * ux + v * uz, q * uz - v * ux)]
    upper = [(c[0] + r * normals[0][0], c[1] + r * normals[0][1])
             for c, r in zip([big, small], radii)]
    lower = [(c[0] + r * normals[1][0], c[1] + r * normals[1][1])
             for c, r in zip([big, small], radii)]
    points = [App.Vector(x, -width / 2, z) for x, z in upper + lower[::-1]]
    middle = Part.Face(Part.makePolygon(points + points[:1])).extrude(App.Vector(0, width, 0))
    rounds = [Part.makeCylinder(r, width, App.Vector(c[0], -width / 2, c[1]), App.Vector(0, 1, 0))
              for c, r in zip([big, small], radii)]
    result = middle.multiFuse(rounds).removeSplitter()
    assert result.isValid() and len(result.Solids) == 1
    return result


def shells(a, route, big_hub_radius, small_hub_radius):
    big, small = route['roller_pinion_axis_xz_mm'], route['candidate_transmission_axis_xz_mm']
    pitch_radii = [route['pitch_mm'] / (2 * math.sin(math.pi / route[key]))
                   for key in ['large_teeth', 'small_teeth']]
    inner_radii = [r + a['chain_radial_envelope'] + a['radial_gap'] for r in pitch_radii]
    outer_radii = [r + a['sheet_stock'] for r in inner_radii]
    outer = capsule(big, small, outer_radii, a['outside_width'])
    inner = capsule(big, small, inner_radii, a['outside_width'] - 2 * a['sheet_stock'])
    shape = outer.cut(inner)
    bores = [Part.makeCylinder(r + a['hub_gap'], a['outside_width'] + 2,
                              App.Vector(c[0], -a['outside_width'] / 2 - 1, c[1]), App.Vector(0, 1, 0))
             for c, r in [(big, big_hub_radius), (small, small_hub_radius)]]
    shape = shape.cut(Part.makeCompound(bores)).removeSplitter()
    b = shape.BoundBox
    sx, sz = big[0] + outer_radii[0], big[1] + a['cap_split_axis_height']
    half_gap = a['cap_split_gap'] / 2

    def upper_rear(x, z):
        return Part.makeBox(x - b.XMin + 1, b.YLength + 2, b.ZMax - z + 1,
                            App.Vector(b.XMin - 1, b.YMin - 1, z))

    cap = shape.common(upper_rear(sx - half_gap, sz + half_gap)).removeSplitter()
    body = shape.cut(upper_rear(sx + half_gap, sz - half_gap)).removeSplitter()
    for name, item in [('body', body), ('cap', cap)]:
        if not item.isValid() or len(item.Solids) != 1:
            raise ValueError('Invalid/disconnected casing ' + name)
    assert body.common(cap).Volume < 1e-6
    return dict(body=body, cap=cap), dict(large_pitch_radius_mm=pitch_radii[0],
            small_pitch_radius_mm=pitch_radii[1], outside_contour_radii_mm=outer_radii,
            cap_seam_x_mm=sx, cap_seam_z_mm=sz, gap_mm=body.distToShape(cap)[0],
            complete_shell_volume_mm3=shape.Volume, split_material_removed_mm3=shape.Volume-body.Volume-cap.Volume)
