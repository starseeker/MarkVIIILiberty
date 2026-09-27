"""Complete upper-handle alternatives with explicit, competing length datums.

Lower stock is constructed identically to the accepted operating handle. The
upper ruled blade and full grip are regenerated; no hull subtraction is used.
"""
import math
import FreeCAD as App
import Part
from driver_operating_handle_parts_v2 import plate_xy, clean

V = App.Vector
X, Z = V(1, 0, 0), V(0, 0, 1)


def dimensions(c, hypothesis):
    rise = -(c['fulcrum_ear_tangent_mm'] + c['fulcrum_stock_mm'] / 2
             + c['pivot_side_gap_mm'] + c['handle_stock_mm'] / 2)
    length = c['handle_length_mm']
    tangent = hypothesis['upper_return_mm']
    outward = c['upper_handle_outward_mm']
    angle = math.radians(c['handle_lateral_angle_deg'])
    datum = hypothesis['length_datum']
    if datum == 'overall_radial_extent':
        tip = length - c['pivot_eye_radius_mm']
    elif datum == 'second_pivot_to_grip_pole':
        tip = math.sqrt(length**2 - outward**2 - (rise + tangent)**2)
    elif datum == 'main_shaft_axis_to_grip_pole':
        tip = (math.sqrt(length**2 - tangent**2) - c['pivot_radial_mm']
               + outward * math.sin(angle)) / math.cos(angle)
    else:
        raise ValueError(datum)
    return dict(radial_tip_mm=tip, upper_return_mm=tangent,
                selector_plane_rise_mm=rise, last_blade_station_mm=tip - 99.8,
                nominal_length_mm=length, length_datum=datum,
                measurement_point='Physical spherical cap pole along the grip cylinder axis; not a bounding-box corner.')


def handle(c, hypothesis, side):
    d = dimensions(c, hypothesis)
    sign = 1 if side == 'Port' else -1
    stock = c['handle_stock_mm']
    heel = [(-20, 0), (-20, 55), (15, 77), (50, 88), (140, 89.35),
            (140, 76.65), (50, 72), (15, 61), (20, 0)]
    q = plate_xy([(x, sign * y) for x, y in heel], -stock / 2, stock)
    q = q.fuse(Part.makeCylinder(c['pivot_eye_radius_mm'], stock, -Z * stock / 2, Z))
    upper, rise = c['upper_handle_outward_mm'], d['selector_plane_rise_mm']
    stations = [(140., 83., 0.), (205., 83., rise), (276., 83., rise),
                (305., upper, rise), (375., upper, rise),
                (d['last_blade_station_mm'], upper, rise + d['upper_return_mm'])]
    sections = []
    for radial, offset, tangent in stations:
        pts = [V(radial, sign * offset + y, tangent + z)
               for y, z in [(-6.35, -stock / 2), (6.35, -stock / 2),
                            (6.35, stock / 2), (-6.35, stock / 2)]]
        sections.append(Part.Wire(Part.makePolygon(pts + pts[:1]).Edges))
    q = q.fuse(Part.makeLoft(sections, True, True))
    tip, tangent = d['radial_tip_mm'], rise + d['upper_return_mm']
    q = q.fuse(Part.makeCylinder(10.5, 109.5, V(tip - 120, sign * upper, tangent), X))
    q = q.fuse(Part.makeSphere(10.5, V(tip - 10.5, sign * upper, tangent)))
    q = q.cut(Part.makeCylinder(c['pivot_bore_radius_mm'], 200, V(0, 0, -100), Z))
    return clean(q), d
