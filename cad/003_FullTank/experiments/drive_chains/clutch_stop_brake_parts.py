"""Receiving geometry for the source-sized clutch-stop brake reconstruction."""
from clutch_drive_parts import build as drive_parts
from air_pump_mount_parts import build as mount_parts


def receiving_drive(drive_controls, pump_controls, mount_controls,
                    input_controls, original_cover, original_housing):
    """Propagate the printed drum diameter through its pulley, belt and supports.

    The provisional uniform drum wall is retained. This changes both pulley
    and brake lands; it does not preserve the old pulley diameter merely to
    avoid updating the belt closure. Main clutch and cardan revisions made
    after the original drive packet must remain untouched by the caller.
    """
    c = dict(drive_controls)
    delta = 9.25 * 25.4 / 2 - c['drum_radius']
    for key in ['drum_radius', 'drum_inside', 'drum_groove_inside']:
        c[key] += delta
    parts, _, _, details = drive_parts(c, pump_controls,
        input_controls['stack'], input_controls['bearing'])
    mc = dict(mount_controls)
    mc['belt_drive_pitch_radius'] = details['belt']['drive_pitch_radius']
    mc['belt_pump_pitch_radius'] = details['belt']['pump_pitch_radius']
    mounts, occurrences, receivers, md = mount_parts(mc, pump_controls,
        original_cover, original_housing)
    assert abs(md['pump_origin'][2] - details['belt']['center_distance']) < 1e-8
    return dict(drum=parts['drum'], belt=parts['belt']), mounts, occurrences, receivers, dict(
        drive_controls=c, mount_controls=mc, belt=details['belt'], mounts=md,
        radial_change_mm=delta, source_drum_diameter_mm=9.25*25.4)


def band_parts(c):
    """Form M4158/M4159 and their 17 rivets; anchor/actuator follow separately.

    The integral returned eye and its clock are reconstruction assumptions.
    The neutral-radius arc consumes the printed lining cut length. Each rivet
    uses a real receiving hole and recessed head; its upset tail conserves the
    selected blank volume. Coordinates are local to TransmissionCore.
    """
    import math
    import FreeCAD as App
    import Part
    from air_pressure_pump_parts import cyl, moved
    from clutch_cone_parts import cap, ztool

    width = c['lining_width']
    x0 = c['band_center_x'] - width / 2
    ri = c['drum_diameter'] / 2 + c['released_gap']
    neutral = ri + c['lining_stock'] / 2
    br = ri + c['lining_stock']
    t = c['steel_stock']
    mid = br + t / 2
    sweep = c['lining_cut_length'] / neutral
    gap = 2 * math.pi - sweep
    start = math.radians(c['opening_clock_deg']) + gap / 2
    end = start + sweep
    curl = c['eye_inside_radius'] + t / 2
    trans = math.radians(c['return_transition_deg'])
    lap = math.radians(c['return_lap_deg'])
    assert 0 < gap < math.pi / 2 and sweep - trans - lap > math.pi

    def point(radius, angle, x=x0):
        return App.Vector(x, radius * math.cos(angle), radius * math.sin(angle))

    def arc(radius, a, b, center=None):
        center = center or App.Vector(x0, 0, 0)
        return Part.Arc(*[center + App.Vector(0, radius * math.cos(v), radius * math.sin(v))
                          for v in [a, (a+b)/2, b]]).toShape()

    def sector(inner, outer, a, b):
        edges = [arc(outer, a, b), Part.makeLine(point(outer, b), point(inner, b)),
                 arc(inner, b, a), Part.makeLine(point(inner, a), point(outer, a))]
        return Part.Face(Part.Wire(edges)).extrude(App.Vector(width, 0, 0))

    base_band = sector(br, br+t, start, end)
    lining = sector(ri, br, start, end)
    eye = point(mid+curl, end)
    # Semicircular fold has exact normal stock and remains open at the free edge.
    fold_edges = [arc(curl+t/2, end+math.pi, end, eye),
        Part.makeLine(eye+point(curl+t/2, end, 0), eye+point(curl-t/2, end, 0)),
        arc(curl-t/2, end, end+math.pi, eye),
        Part.makeLine(eye+point(curl-t/2, end+math.pi, 0), eye+point(curl+t/2, end+math.pi, 0))]
    fold = Part.Face(Part.Wire(fold_edges)).extrude(App.Vector(width, 0, 0))

    # A smooth assumed return joins the roll to a contacting doubled strip.
    # Offset both edges NORMAL to the selected centerline, not radially.
    def profile(u, side):
        rr = mid + t + (2*curl-t)*(1 - 3*u*u + 2*u*u*u)
        dr = (2*curl-t)*(-6*u+6*u*u)
        aa = end - trans*u
        n = point(1, aa, 0)
        tangent = App.Vector(0, -math.sin(aa), math.cos(aa))
        derivative = n*dr - tangent*(rr*trans)
        normal = App.Vector(0, -derivative.z, derivative.y)
        normal.normalize()
        return point(rr, aa) + normal*(side*t/2)

    curves = []
    ns = c['return_profile_samples']
    for side in [1, -1]:
        curve = Part.BSplineCurve()
        pts = [profile(i/(ns-1), side) for i in range(ns)]
        curve.interpolate(Points=pts)
        curves.append(curve)
    outer, inner = [curve.toShape() for curve in curves]
    edges = [outer, Part.makeLine(profile(1,1), profile(1,-1)),
             inner.reversed(), Part.makeLine(profile(0,-1), profile(0,1))]
    returned = Part.Face(Part.Wire(edges)).extrude(App.Vector(width,0,0))
    lap_shape = sector(br+t, br+2*t, end-trans-lap, end-trans)
    band = base_band.fuse(fold).fuse(returned).fuse(lap_shape).removeSplitter()
    # Central relief makes two rolled ears for the subsequent pin/eyebolt joint.
    slot_radius = c['eye_inside_radius'] + 3.0
    slot = Part.makeCylinder(slot_radius, c['eye_slot_width'],
        App.Vector(c['band_center_x']-c['eye_slot_width']/2, eye.y, eye.z), App.Vector(1,0,0))
    band = band.cut(slot).removeSplitter()
    assert band.isValid() and len(band.Solids) == 1, ('formed band', band.isValid(), len(band.Solids))
    assert lining.isValid() and len(lining.Solids) == 1

    residual = max(Part.Vertex(profile((i+.37)/97, side)).distToShape(curves[j].toShape())[0]
                   for j,side in enumerate([1,-1]) for i in range(97))
    assert residual < .001, residual
    blanks = dict(band=band.copy(), lining=lining.copy())
    parts, occurrences, joints = {}, [], []
    band_tools, lining_tools = [], []

    def place(name, key, xyz, radial):
        rot = App.Rotation(App.Vector(0,0,1), radial)
        occurrences.append(dict(name='ClutchStopBand_'+name, key=key,
                                xyz=list(xyz), rotation=list(rot.Q)))
        return rot

    def tail_height(radius, volume):
        # Spherical cap: V = pi*h*(3*a^2+h^2)/6, strictly increasing in h.
        lo, hi = 0., 2*radius
        assert math.pi*hi*(3*radius*radius+hi*hi)/6 > volume
        for _ in range(70):
            h=(lo+hi)/2
            if math.pi*h*(3*radius*radius+h*h)/6 < volume:lo=h
            else:hi=h
        return (lo+hi)/2

    # Counterbored tail seats flatten the small region around each rivet.
    r = c['lining_rivet_diameter']/2
    head_r = c['lining_rivet_head_radius']
    head_depth = head_r-r  # selected90-degree included head angle
    head_top = ri+c['lining_rivet_recess']
    tail_seat = br+t-c['spotface_depth']
    grip = tail_seat-head_top
    assert head_depth < grip < c['lining_rivet_blank_length']
    volume = math.pi*r*r*(c['lining_rivet_blank_length']-grip)
    height = tail_height(c['lining_rivet_tail_radius'], volume)
    rivet = Part.makeCone(head_r,r,head_depth).fuse(cyl(r,head_depth,grip))
    rivet = rivet.fuse(cap(c['lining_rivet_tail_radius'],height,grip)).removeSplitter()
    parts['lining_rivet'] = rivet
    number = 0
    for n in range(c['lining_rivet_stations']):
        along = c['lining_rivet_start_margin'] + n*(c['lining_cut_length']-
            c['lining_rivet_start_margin']-c['lining_rivet_end_margin'])/(c['lining_rivet_stations']-1)
        angle = start+along/neutral
        radial = point(1,angle,0)
        for dx in c['lining_rivet_axial_offsets']:
            number += 1
            base = point(head_top,angle,c['band_center_x']+dx)
            rot = place(f'LiningRivet{number:02}','lining_rivet',base,radial)
            shaft_r = r+c['rivet_radial_gap']
            hr = head_r+c['head_seat_radial_gap']
            tr = c['lining_rivet_tail_radius']+c['head_seat_radial_gap']
            cutter = ztool([(0,-3),(hr,-3),(hr,0),(shaft_r,head_depth),
                (shaft_r,grip),(tr,grip),(tr,grip+height+1),(0,grip+height+1)])
            tool = moved(cutter,base,rot)
            band_tools.append(tool);lining_tools.append(tool)
            joints.append(dict(name=occurrences[-1]['name'],kind='lining',base=list(base),
                radial=list(radial),head_top_radius=head_top,tail_seat_radius=tail_seat,
                grip=grip,tail_height=height,tail_volume=volume,angle_rad=angle))

    r = c['fold_rivet_diameter']/2
    seat = br+c['spotface_depth']
    tail_seat = br+2*t-c['spotface_depth']
    grip = tail_seat-seat
    assert 0 < grip < c['fold_rivet_blank_length']
    volume = math.pi*r*r*(c['fold_rivet_blank_length']-grip)
    height = tail_height(c['fold_rivet_tail_radius'],volume)
    head = cap(c['fold_rivet_head_radius'],c['fold_rivet_head_height'])
    head.rotate(App.Vector(),App.Vector(1,0,0),180)
    rivet = head.fuse(cyl(r,0,grip)).fuse(cap(c['fold_rivet_tail_radius'],height,grip)).removeSplitter()
    parts['fold_rivet'] = rivet
    angle = end-trans-lap/2
    radial = point(1,angle,0)
    for n,dx in enumerate(c['fold_rivet_axial_offsets'],1):
        base = point(seat,angle,c['band_center_x']+dx)
        rot = place(f'FoldRivet{n}','fold_rivet',base,radial)
        dr = r+c['rivet_radial_gap'];hr=c['fold_rivet_head_radius']+c['head_seat_radial_gap']
        tr = c['fold_rivet_tail_radius']+c['head_seat_radial_gap']
        cutter = ztool([(0,-5),(hr,-5),(hr,0),(dr,0),(dr,grip),
                        (tr,grip),(tr,grip+height+1),(0,grip+height+1)])
        tool = moved(cutter,base,rot)
        band_tools.append(tool);lining_tools.append(tool)
        joints.append(dict(name=occurrences[-1]['name'],kind='fold',base=list(base),
            radial=list(radial),head_seat_radius=seat,tail_seat_radius=tail_seat,
            grip=grip,tail_height=height,tail_volume=volume,angle_rad=angle))

    parts['band'] = band.cut(Part.makeCompound(band_tools)).removeSplitter()
    parts['lining'] = lining.cut(Part.makeCompound(lining_tools)).removeSplitter()
    for key in ['band','lining']:
        occurrences.append(dict(name='ClutchStopBand_'+key,key=key,xyz=[0,0,0],rotation=[0,0,0,1]))
    for key,shape in parts.items():
        assert shape.isValid() and len(shape.Solids)==1,(key,shape.isValid(),len(shape.Solids))
    assert len(occurrences)==19
    curves_out = dict(lining_neutral=arc(neutral,start,end),
                     return_outer=outer,return_inner=inner)
    d = dict(lining_inner_radius=ri,lining_neutral_radius=neutral,band_inner_radius=br,
        band_outer_radius=br+t,arc_start_rad=start,arc_end_rad=end,wrap_angle_deg=math.degrees(sweep),
        opening_angle_deg=math.degrees(gap),band_axial_extent=[x0,x0+width],
        eye_axis_point=[c['band_center_x'],eye.y,eye.z],eye_axis=[1,0,0],
        eye_slot_radius=slot_radius,return_profile_max_residual_mm=residual,
        rivet_joints=joints,anchor_present=False,operating_linkage_present=False,
        complete_brake=False,historical_form_qualified=False)
    return parts,occurrences,d,curves_out,blanks
