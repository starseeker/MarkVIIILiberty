"""Explicit installed M564 wire paths and M567 washer stock; no tolerance resets.

The hook-on-socket mounting is an estimated static reconstruction, not a printed
source detail. Each spring keeps its own installed extension state and centerline.
"""
import math
import FreeCAD as App
import Part

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def washer(bore=13., diameter=22.225, thickness=1.5):
    return Part.makeCylinder(diameter/2, thickness, V(), Y).cut(
        Part.makeCylinder(bore/2, thickness+2, -Y, Y))


def bezier(a, ta, b, tb, ha, hb):
    curve = Part.BezierCurve()
    curve.setPoles([a, a+ta*ha, b-tb*hb, b])
    return curve.toShape()


def spring(socket, seat_x, anchor, near_side, wire_diameter=2.6,
           turns=30, outer_diameter=19.05, washer_thickness=1.5):
    """World-space construction, returned in an identity definition at socket.

    Front 300-degree eye wraps around the fork socket, held by the existing jam
    nut. Rear wire crosses the measured bracket hole and turns outside its cheek.
    Coil centers and hook details are controlled estimates. Solid stock, end
    capture and neighboring material require independent saved-shape checks.
    """
    origin = V(socket)
    anchor = anchor-origin
    seat_x -= origin.x
    socket = V()
    wr = wire_diameter/2
    radius = 12.7+wr+.1
    f = V(seat_x-wr, socket.y, socket.z)
    def point(deg):
        ang = math.radians(deg)
        return f+V(0, radius*math.cos(ang), radius*math.sin(ang))
    # The free tip is separated from the loaded end by a 60-degree opening.
    arc = Part.Arc(point(60), point(210), point(360)).toShape()
    end_eye = point(360)
    lead = end_eye+Z*14
    edges = [arc, Part.makeLine(end_eye, lead)]

    # Estimated coil stations, above the short connection and outside the ear.
    ca = V(f.x+48, socket.y, socket.z+38)
    cb = anchor+V(-35, near_side*18, -10)
    axis = cb-ca
    height = axis.Length
    ez = axis.normalize()
    ex = (Z-ez*Z.dot(ez)).normalize()
    ey = ez.cross(ex).normalize()
    frame = App.Placement(App.Matrix(ex.x,ey.x,ez.x,ca.x,
                                    ex.y,ey.y,ez.y,ca.y,
                                    ex.z,ey.z,ez.z,ca.z,0,0,0,1))
    pitch = height/turns
    assert pitch > wire_diameter+.05, (height,pitch)
    mean = (outer_diameter-wire_diameter)/2
    helix = Part.makeHelix(pitch, height, mean)
    helix.Placement = frame
    he = helix.Edges[0]
    hs, ht = he.valueAt(he.FirstParameter), he.tangentAt(he.FirstParameter)
    he_end, he_tan = he.valueAt(he.LastParameter), he.tangentAt(he.LastParameter)
    edges += [bezier(lead,Z,hs,ht,20,14), *helix.Edges]

    # Hole radius 3.325, ear stock 7.9375. Set wire against the -X bore wall.
    bore_centerline = anchor+V(-(3.325-wr),0,0)
    side_offset = 7.9375/2+wr+.3
    entry = bore_centerline+Y*(near_side*side_offset)
    exit_ = bore_centerline-Y*(near_side*side_offset)
    cross_axis = Y*(-near_side)
    edges += [bezier(he_end,he_tan,entry,cross_axis,16,12),
              Part.makeLine(entry,exit_)]
    tip = exit_+V(-2,-near_side*5,-6)
    edges.append(bezier(exit_,cross_axis,tip,-Z,5,3))
    path = Part.Wire(edges)
    start = edges[0].valueAt(edges[0].FirstParameter)
    tangent = edges[0].tangentAt(edges[0].FirstParameter)
    profile = Part.Wire([Part.makeCircle(wr,start,tangent)])
    shape = path.makePipeShell([profile],True,True)
    assert shape.isValid() and len(shape.Solids)==1 and shape.Solids[0].isClosed()
    assert shape.Placement.isIdentity()
    details = dict(wire_diameter_mm=wire_diameter,coil_outer_diameter_mm=outer_diameter,
                   turns=turns,pitch_mm=pitch,coil_height_mm=height,
                   centerline_length_mm=path.Length,wire_stock_volume_mm3=math.pi*wr**2*path.Length,
                   front_eye_center_world_mm=list(f+origin),front_socket_center_world_mm=list(origin),
                   front_seat_x_mm=seat_x+origin.x,front_hook_mean_radius_mm=radius,
                   rear_anchor_world_mm=list(anchor+origin),rear_crosswire_center_world_mm=list(bore_centerline+origin),
                   rear_crosswire_endpoints_world_mm=[list(entry+origin),list(exit_+origin)],
                   source_family='M564',configuration='estimated installed extension state',
                   hook_hypothesis='Socket-wrapping eye retained behind existing jam nut; crosswire through M4136 hole.')
    return shape, path, details
