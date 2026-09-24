"""Conditional low/track brake stops; all unprinted sections are estimates.

Stop coordinates: U tangent forward/up, V opposite world Y, W radially outward.
The origin is the drum axis. Analytic foot arcs retain the backing radii.
This module does not establish that M341/M342 and MX95/MX96 are identical.
"""
import math
import FreeCAD as App
import Part
from transmission_brake_anchor_parts import steel_rivet
from transmission_frame_joint_parts import rivet

V = App.Vector


def box(u0, u1, v0, v1, w0, w1):
    return Part.makeBox(u1-u0, v1-v0, w1-w0, V(u0, v0, w0))


def plate(points, v0, width):
    vertices = [V(u, v0, w) for u, w in points]
    return Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(V(0, width, 0))


def hexagon(af, height):
    radius = af/math.sqrt(3)
    ps = [V(radius*math.cos(i*math.pi/3), radius*math.sin(i*math.pi/3), 0) for i in range(6)]
    return Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(V(0, 0, height))


def screw(length, c):
    head = hexagon(c['screw_head_af'], c['screw_head_height'])
    head.translate(V(0, 0, -c['screw_head_height']))
    return head.fuse(Part.makeCylinder(c['screw_diameter']/2, length))


def basis(angle):
    a = math.radians(angle)
    tangent, radial = V(-math.sin(a), 0, math.cos(a)), V(math.cos(a), 0, math.sin(a))
    return App.Rotation(tangent, V(0, -1, 0), radial, 'ZXY')


def arc_foot(inner, outer, start, end, width):
    def p(r, a):
        return V(r*math.sin(a), -width/2, r*math.cos(a))
    def arc(r, a, b):
        return Part.Arc(p(r, a), p(r, (a+b)/2), p(r, b)).toShape()
    edges = [arc(outer, start, end), Part.makeLine(p(outer, end), p(inner, end)),
             arc(inner, end, start), Part.makeLine(p(inner, start), p(outer, start))]
    return Part.Face(Part.Wire(edges)).extrude(V(0, width, 0))


def parts(c, anchor, saved_bands, stations, mount_xz):
    outer = {role: anchor['details']['brakes'][role]['band_outer_radius_mm'] for role in ['low', 'track']}
    band_stock = anchor['details']['new_band_controls']['steel_stock']
    rotation = basis(c['angle_deg'])
    stop_pose = App.Placement(V(), rotation)
    lower_pose = App.Placement(V(), App.Rotation(V(1, 0, 0), 180))
    rivet_controls = dict(steel_shank_diameter=c['lug_rivet_diameter'],
        steel_stock_length=c['lug_rivet_stock_length'], steel_head_radius=c['lug_rivet_head_radius'],
        steel_countersink_angle_deg=90., steel_head_recess=.15,
        steel_tail_radius=c['lug_rivet_tail_radius'], steel_tail_spotface=.4,
        steel_hole_clearance=c['hole_clearance'], foot_stock=c['foot_stock'])
    shapes = {}
    shapes['lug_rivet'], rd = steel_rivet(rivet_controls, band_stock)
    shapes['bar_rivet'], brd = rivet(c['lug_rivet_diameter'], c['bar_rivet_stock_length'],
        c['bracket_stock']+c['bar_stock'], head_ratio=2.25)
    shapes['M343_screw'] = screw(c['tangent_screw_length'], c)
    shapes['MX88_screw'] = screw(c['radial_screw_length'], c)
    shapes['nut'] = hexagon(c['nut_af'], c['nut_height']).cut(
        Part.makeCylinder(c['screw_diameter']/2+c['thread_bore_clearance'], c['nut_height']+2, V(0, 0, -1)))
    details = dict(rotation=list(rotation.Q), brakes={}, lug_rivet=rd, bar_rivet=brd)
    bar_inner = c['bar_inner_radius']
    bar_outer = bar_inner+c['bar_stock']
    tangent_axis_radius = (bar_inner+bar_outer)/2
    for role in ['low', 'track']:
        radius = outer[role]
        width = anchor['details']['brakes'][role]['band_width_mm']
        foot = arc_foot(radius, radius+c['foot_stock'], math.radians(c['foot_start_delta_deg']),
                        math.radians(c['foot_end_delta_deg']), width)
        # Flat radial screw seat and separate tangential threaded boss.
        lug = foot.multiFuse([
            box(-10, 10, -10, 10, radius+c['seat_base_offset'], radius+c['seat_height']),
            box(c['boss_u0'], c['boss_u1'], -c['boss_width']/2, c['boss_width']/2,
                radius+c['boss_base_offset'], tangent_axis_radius+c['boss_radial_margin'])])
        hole = Part.makeCylinder(c['screw_diameter']/2+c['thread_bore_clearance'],
            c['boss_u1']-c['boss_u0']+2, V(c['boss_u0']-1, 0, tangent_axis_radius), V(1, 0, 0))
        lug = lug.cut(hole)
        backing = saved_bands[role].copy()
        joints = []
        delta = math.radians(c['lug_rivet_delta_deg'])
        radial = V(math.sin(delta), 0, math.cos(delta))
        for i, v in enumerate([-c['lug_rivet_half_span'], 0, c['lug_rivet_half_span']], 1):
            at = radial*(radius-band_stock+.15)+V(0, v, 0)
            pose = App.Placement(at, App.Rotation(V(0, 0, 1), radial))
            hole_r = c['lug_rivet_diameter']/2+c['hole_clearance']
            tool = Part.makeCylinder(hole_r, rd['grip_mm']+12, V(0, 0, -3)).fuse(
                Part.makeCone(c['lug_rivet_head_radius']+3, hole_r, rd['head_depth_mm']+3, V(0, 0, -3)))
            local_tool = tool.copy(); local_tool.Placement = pose
            lug = lug.cut(local_tool)
            tool.Placement = lower_pose.inverse().multiply(stop_pose).multiply(pose)
            backing = backing.cut(tool)
            spot = Part.makeCylinder(c['lug_rivet_tail_radius']+.05, rd['tail_height_mm']+4, V(0, 0, rd['grip_mm']))
            spot.Placement = pose
            lug = lug.cut(spot)
            joints.append(dict(index=i, frame=list(pose.toMatrix().A)))
        shapes[role+'_lug'] = lug
        shapes[role+'_lower_band'] = backing
        details['brakes'][role] = dict(outer_radius_mm=radius, band_width_mm=width, rivets=joints,
            radial_tip_w_mm=radius+c['seat_height'], tangent_axis_w_mm=tangent_axis_radius)

    half_span = abs(stations['track']-stations['low'])/2
    # Port stop coordinates have +V inboard. The starboard bar is rotated
    # through 180 degrees about W; its U-symmetric profile allows this reuse.
    bar = box(-c['bar_half_width'], c['bar_half_width'], -half_span-c['bar_end_margin'],
              half_span+c['bar_end_margin'], bar_inner, bar_outer)
    for v in [-half_span, half_span]:
        bar = bar.cut(Part.makeCylinder(c['screw_diameter']/2+c['thread_bore_clearance'],
            c['bar_stock']+2, V(0, v, bar_inner-1)))
    mx, mz = mount_xz
    inverse = rotation.inverted()
    def uw(x, z):
        pt = inverse.multVec(V(x, 0, z)); return (pt.x, pt.z)
    t = c['bracket_stock']; height = c['mount_tab_half_height']
    tab = plate([uw(mx, mz-height), uw(mx+t, mz-height), uw(mx+t, mz+height), uw(mx, mz+height)],
                -c['bracket_web_width']/2, c['bracket_web_width'])
    start = V(*[0, 0, 0])
    su, sw = uw(mx+t/2, mz-height+3)
    start = V(su, 0, sw); end = V(0, 0, bar_inner-t/2)
    normal = V(-(end-start).z, 0, (end-start).x); normal.normalize()
    corners = [start-normal*t/2, start+normal*t/2, end+normal*t/2, end-normal*t/2]
    strut = plate([(p.x, p.z) for p in corners], -c['bracket_web_width']/2, c['bracket_web_width'])
    foot = box(-c['bracket_foot_half_width'], c['bracket_foot_half_width'],
        -c['bracket_foot_half_span'], c['bracket_foot_half_span'], bar_inner-t, bar_inner)
    bracket = tab.multiFuse([strut, foot])
    hole_origin = inverse.multVec(V(mx-1, 0, mz))
    hole_axis = inverse.multVec(V(1, 0, 0))
    bracket = bracket.cut(Part.makeCylinder(c['mount_bore_radius'], t+2, hole_origin, hole_axis))
    offset_v = (stations['low']+stations['track'])/2-stations['mount']
    joints = []
    for i, (u, v) in enumerate([(u, v) for u in [-c['bar_rivet_half_width'], c['bar_rivet_half_width']]
                                for v in [-c['bar_rivet_half_span'], c['bar_rivet_half_span']]], 1):
        hole = Part.makeCylinder(c['lug_rivet_diameter']/2+c['hole_clearance'], t+c['bar_stock']+2,
            V(u, v, bar_inner-t-1))
        bracket = bracket.cut(hole)
        hole.translate(V(0, offset_v, 0)); bar = bar.cut(hole)
        joints.append(dict(index=i, bracket_uvw_mm=[u, v, bar_inner-t]))
    shapes['M341_bracket'] = bracket
    shapes['M342_bar'] = bar
    details.update(bar_inner_radius_mm=bar_inner, bar_outer_radius_mm=bar_outer,
        band_half_span_mm=half_span, bar_joint_offset_v_mm=offset_v, support_rivets=joints,
        mounting_stud_shift_mm=t, mount_tab_contact_xz_mm=[mx, mz])
    for name, s in shapes.items():
        if not s.isValid() or len(s.Solids) != 1:
            raise ValueError((name, s.isValid(), len(s.Solids)))
        if not s.Placement.isIdentity():
            raise ValueError('Definition frame is not identity: '+name)
    return shapes, details
