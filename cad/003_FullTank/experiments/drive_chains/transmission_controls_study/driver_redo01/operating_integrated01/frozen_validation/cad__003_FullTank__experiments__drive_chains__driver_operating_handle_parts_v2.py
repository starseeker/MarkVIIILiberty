"""Estimated complete operating handles, inboard fulcrums and source-sized pivots.

Canonical axes are radial X, vehicle-transverse Y and tangential Z. The handle
origin is its second pivot. Its source-length interpretation is in the packet.
"""
import math
import FreeCAD as App
import Part
from transmission_brake_stop_parts import hexagon
from transmission_input_installation_parts import formed_pin

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def plate_xy(points, z, stock):
    vertices = [V(x, y, z) for x, y in points]
    return Part.Face(Part.makePolygon(vertices + vertices[:1])).extrude(Z * stock)


def plate_xz(points, width):
    vertices = [V(x, -width / 2, z) for x, z in points]
    return Part.Face(Part.makePolygon(vertices + vertices[:1])).extrude(Y * width)


def clean(q):
    s = q.copy().removeSplitter()
    assert s.isValid() and len(s.Solids) == 1
    return s


def fulcrum(c):
    t = c['fulcrum_stock_mm']
    z = c['fulcrum_ear_tangent_mm']
    r = c['pivot_radial_mm']
    q = Part.makeCylinder(c['hub_radius_mm'], c['journal_width_mm'], -Y * c['journal_width_mm'] / 2, Y)
    arm = plate_xz([(-10, -25 - t / 2), (-10, -25 + t / 2),
                    (r + 30, z + t / 2), (r + 15, z + t / 2),
                    (r + 15, z - t / 2), (r + 30, z - t / 2)], 24)
    eye = Part.makeCylinder(c['pivot_eye_radius_mm'], t, V(r, 0, z - t / 2), Z)
    q = q.fuse(arm).fuse(eye)
    q = q.cut(Part.makeCylinder(c['journal_radius_mm'], 100, -Y * 50, Y))
    q = q.cut(Part.makeCylinder(c['pivot_bore_radius_mm'], 200, V(r, 0, -100), Z))
    q = q.cut(Part.makeCylinder(1.5, 34, V(), X))
    return clean(q)


def handle(c, side):
    sign = 1 if side == 'Port' else -1
    stock = c['handle_stock_mm']
    # Rise from the offset heel plane to the shared selector plane.
    rise = -(c['fulcrum_ear_tangent_mm'] + c['fulcrum_stock_mm'] / 2
             + c['pivot_side_gap_mm'] + stock / 2)
    heel = [(-20, 0), (-20, 55), (15, 77), (50, 88), (140, 89.35),
            (140, 76.65), (50, 72), (15, 61), (20, 0)]
    q = plate_xy([(x, sign * y) for x, y in heel], -stock / 2, stock)
    q = q.fuse(Part.makeCylinder(c['pivot_eye_radius_mm'], stock, -Z * stock / 2, Z))
    upper = c['upper_handle_outward_mm']
    stations = [(140., 83., 0.), (205., 83., rise), (276., 83., rise),
                (305., upper, rise), (375., upper, rise), (815., upper, rise + c['handle_upper_tangent_mm'])]
    sections = []
    for radial, offset, tangent in stations:
        pts = [V(radial, sign * offset + y, tangent + z)
               for y, z in [(-6.35, -stock / 2), (6.35, -stock / 2),
                            (6.35, stock / 2), (-6.35, stock / 2)]]
        sections.append(Part.Wire(Part.makePolygon(pts + pts[:1]).Edges))
    q = q.fuse(Part.makeLoft(sections, True, True))
    tip = c['handle_length_mm'] - c['pivot_eye_radius_mm']
    grip_rise = rise + c['handle_upper_tangent_mm']
    grip = V(tip - 120, sign * upper, grip_rise)
    q = q.fuse(Part.makeCylinder(10.5, 109.5, grip, X))
    q = q.fuse(Part.makeSphere(10.5, V(tip - 10.5, sign * upper, grip_rise)))
    q = q.cut(Part.makeCylinder(c['pivot_bore_radius_mm'], 200, V(0, 0, -100), Z))
    return clean(q), dict(selector_plane_rise_mm=rise, radial_tip_mm=tip,
                         grip_centerline_y_mm=sign * upper,
                         length_datum='Overall radial extent from the -25 mm pivot-eye extremity to grip tip; inferred interpretation of HB148.')


def hardware(c):
    grip = c['fulcrum_stock_mm'] + c['pivot_side_gap_mm'] + c['handle_stock_mm']
    height, depth = c['nut_thickness_mm'], c['nut_slot_depth_mm']
    station = grip + height - c['cotter_axis_below_nut_top_mm']
    head = hexagon(c['bolt_head_af_mm'], c['bolt_head_height_mm'])
    head.translate(-Z * c['bolt_head_height_mm'])
    bolt = Part.makeCylinder(c['bolt_radius_mm'], c['bolt_length_mm']).fuse(head)
    bolt = bolt.cut(Part.makeCylinder(c['cotter']['cotter_diameter'] / 2 + .1, 40, V(-20, 0, station), X))
    nut = hexagon(c['nut_af_mm'], height - depth)
    nut = nut.fuse(Part.makeCylinder(c['nut_crown_radius_mm'], depth, Z * (height - depth)))
    nut = nut.cut(Part.makeCylinder(c['pivot_bore_radius_mm'], height + 2, -Z))
    for angle in [0, 60, 120]:
        slot = Part.makeBox(50, c['nut_slot_width_mm'], depth + 1,
                            V(-25, -c['nut_slot_width_mm'] / 2, height - depth))
        slot.rotate(V(), Z, angle)
        nut = nut.cut(slot)
    cotter, detail = formed_pin(c['cotter'])
    # Map the pin axis to X, keeping its split plane axial through the nut slots.
    cotter.rotate(V(), Z, -90)
    return dict(bolt=clean(bolt), nut=clean(nut), cotter=clean(cotter)), dict(
        nut_seat_mm=grip, cotter_axis_mm=station, bolt_length_mm=c['bolt_length_mm'],
        cotter=detail, cotter_split_plane='Local XZ, through the axial crown slots.')
