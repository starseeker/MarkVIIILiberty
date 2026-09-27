"""Estimated separate support plates/angles and four source-counted seat stays."""
import math
from control_rebuild_io_v2 import App, Part
from bow_reconstruction_parts import section
from engine_suspension_parts import hexagon

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def bolt(diameter, length, af, head_height):
    return hexagon(af, -head_height, 0).fuse(Part.makeCylinder(diameter/2, length)).removeSplitter()


def upper_hardware():
    diameter, af, nut_stock, lock_stock = 19.05, 31.75, 19.05, 3.175
    pin = bolt(diameter, 60.325, af, 12.3825)
    nut = hexagon(af, 0, nut_stock).cut(Part.makeCylinder(9.65, nut_stock+2, -Z))
    lock = Part.makeCylinder(17.4625, lock_stock).cut(Part.makeCylinder(9.7, lock_stock+2, -Z))
    lock = lock.cut(Part.makeBox(19, 1.6, lock_stock+2, V(0, -.8, -1)))
    return pin, nut.removeSplitter(), lock.removeSplitter()


def supports(record, controls, lower_centers, hand):
    """Split the old estimated bent foot into M788 and a plain M786/M787 web.

    Origins and both existing shaft centers stay fixed. Angles follow the two
    actual floor planes; sharp longitudinal bend and dimensions are estimates.
    """
    t, outer = controls['plate_stock'], controls['nut_seat_y']
    inside = outer-t
    base = V(*record['canonical_origin_world_mm'])
    bottom, upper = record['floor_contact_section_world'], record['upper_foot_section_world']
    local = lambda p: [p[0]-base.x, p[1]-base.z]
    yspan = lambda a, b: sorted([hand*a, hand*b])
    foot = section([local(p) for p in bottom+list(reversed(upper))], *yspan(inside, outer+55))
    leaf_top = [[x, z+55] for x, z in upper]
    # The 0.2 mm overlap is internal to the angle, entirely above its floor seat.
    leaf_bottom = [[x, z-.2] for x, z in upper]
    leaf = section([local(p) for p in leaf_bottom+list(reversed(leaf_top))], *yspan(outer, outer+t))
    angle = foot.fuse(leaf)
    front, rear = lower_centers['Front'], lower_centers['Rear']
    main = record['main_shaft_local_mm']
    swing = record['swing_shaft_local_mm']
    web_top = [[front.x+24, front.z-8], [front.x+15, front.z+25],
               [rear.x-24, rear.z+25], [base.x-35, base.z+swing[2]-15],
               [base.x-70, base.z+swing[2]-40]]
    web = section([local(p) for p in upper+web_top], *yspan(inside, outer))
    for point, radius, hole in [(main, 31, 14.15), (swing, 24, 12.15)]:
        x, _, z = point
        web = web.fuse(Part.makeCylinder(radius, t, V(x, hand*inside, z), Y*hand))
        web = web.cut(Part.makeCylinder(hole, t+2, V(x, hand*(inside-1), z), Y*hand))
    # Upper eyes are real receiving holes, at the conditional source joint picks.
    for point in [front, rear]:
        web = web.cut(Part.makeCylinder(6.5, t+2, point-base+Y*(hand*(inside-1)), Y*hand))
    return web.removeSplitter(), angle.removeSplitter(), base


def stay(lower, upper, thickness=6.35):
    """Analytic dogleg strip, canonical lower center at zero; transverse faces Y.

    upper/lower Y are the near faces of the strip. End pads preserve real bolt
    seats normal to Y. The center web's thickness is projected Y stock, not a
    claim of constant-normal rolled strip thickness.
    """
    delta = upper-lower
    assert delta.z > 140
    profiles = []
    for z, fraction in [(0., 0.), (30., 0.), (delta.z-30., 1.), (delta.z, 1.)]:
        x = delta.x*z/delta.z
        y = delta.y*fraction
        pts = [V(x-14, y, z), V(x+14, y, z), V(x+14, y+thickness, z), V(x-14, y+thickness, z)]
        profiles.append(Part.makePolygon(pts+pts[:1]))
    body = Part.makeLoft(profiles, True, True)
    body = body.fuse(Part.makeCylinder(18, thickness, V(), Y))
    body = body.fuse(Part.makeCylinder(20, thickness, delta, Y))
    body = body.cut(Part.makeCylinder(6.5, thickness+2, -Y, Y))
    body = body.cut(Part.makeCylinder(9.65, thickness+2, delta-Y, Y))
    return body.removeSplitter()
