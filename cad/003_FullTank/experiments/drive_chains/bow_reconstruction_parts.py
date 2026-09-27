"""Planar bow reconstruction, with explicit normal stock and miter joints.

All points are X/Z. +X is forward, +Z upward, Y is transverse. The floor
route and thickness are reconstruction assumptions, not measured fabrication
dimensions. No retained component is used as a Boolean trimming tool.
"""
import math
import FreeCAD as App
import Part


def line_offset(a, b, distance, interior):
    dx, dz = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dz)
    n = [-dz/length, dx/length]
    if sum(n[i]*interior[i] for i in range(2)) < 0:
        n = [-v for v in n]
    return ([a[i]+distance*n[i] for i in range(2)],
            [b[i]+distance*n[i] for i in range(2)])


def intersection(one, two):
    p, q = one; r, s = two
    u = [q[i]-p[i] for i in range(2)]
    v = [s[i]-r[i] for i in range(2)]
    cross = lambda a, b: a[0]*b[1]-a[1]*b[0]
    den = cross(u, v)
    if abs(den) < 1e-9:
        raise ValueError('Parallel miter lines')
    t = cross([r[i]-p[i] for i in range(2)], v)/den
    return [p[i]+t*u[i] for i in range(2)]


def section(poly, y0, y1):
    points = [App.Vector(x, y0, z) for x, z in poly]
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(App.Vector(0, y1-y0, 0))


def bow_parts(v, points):
    """Return four roles and their geometric datums; hand handled by caller."""
    b, k, d, e, t = (points[n] for n in ['bow_lower', 'floor_bend', 'floor_seam', 'floor_end', 'bow_upper'])
    narrow, wide = v['narrow_half_width'], v['wide_half_width']
    floor = v['floor_thickness']; wall = v['wall_thickness']
    bow_line = line_offset(b, t, wall, [-1, -1])
    floor_lines = [line_offset(p, q, floor, [0, 1]) for p, q in [(b,k),(k,d),(d,e)]]
    bi = intersection(bow_line, floor_lines[0])
    ki = intersection(floor_lines[0], floor_lines[1])
    di = intersection(floor_lines[1], floor_lines[2])
    ei = intersection(floor_lines[2], ([e[0],0], [e[0],1]))
    ti = intersection(bow_line, ([0,t[1]], [1,t[1]]))
    tb = intersection(bow_line, ([0,t[1]-v['roof_thickness']], [1,t[1]-v['roof_thickness']]))
    front = section([b,t,ti,bi], -narrow, narrow)
    first = section([b,k,d,di,ki,bi], -narrow, narrow)
    second = section([d,e,ei,di], -wide, wide)
    # A planform taper carries the narrow forward floor into the broad body.
    # Constant-width extensions let the explicit miter end planes own the ends.
    polygon = [(d[0]+100,-narrow), (d[0]+100,narrow), (d[0],narrow),
               (e[0],wide), (e[0]-100,wide), (e[0]-100,-wide),
               (e[0],-wide), (d[0],-narrow)]
    pp = [App.Vector(x,y,-1000) for x,y in polygon]
    mask = Part.Face(Part.makePolygon(pp+[pp[0]])).extrude(App.Vector(0,0,5000))
    second = second.common(mask).removeSplitter()
    roofs = {}
    for hand in [-1, 1]:
        y0, y1 = sorted([hand*v['driver_inner_half_width'], hand*narrow])
        roofs[hand] = section([[v['main_front_x'],t[1]], ti, tb,
                              [v['main_front_x'],t[1]-v['roof_thickness']]], y0, y1)
    return dict(front_slope=front, floor_1=first, floor_2=second, roof_driver=roofs), dict(
        outer=points, inner=dict(bow_lower=bi, floor_bend=ki, floor_seam=di,
                                floor_end=ei, bow_upper=ti, roof_lower=tb),
        section_assumptions='Faceted floor route; planar bow; sharp miters. Plate identity/split, bend radii, angles and fasteners remain unqualified.')
