"""Partial M289 shaft and M292 brake drum, tied to an explicit drawing scale."""
import FreeCAD as App
import Part


def cylinder(radius, low, high):
    return Part.makeCylinder(radius, high - low, App.Vector(0, low, 0), App.Vector(0, 1, 0))


def spline_tools(a, low, high):
    tools = [cylinder(a['small_bore_radius'], low, high)]
    for n in range(int(a['splines'])):
        shape = Part.makeBox(a['spline_width'], high - low, a['spline_depth'] + 2,
                             App.Vector(-a['spline_width'] / 2, low, a['small_bore_radius'] - 2))
        shape.rotate(App.Vector(), App.Vector(0, 1, 0), 360 * n / a['splines'])
        tools.append(shape)
    return Part.makeCompound(tools)


def parts(a, controls, calibration):
    scale = calibration['mm_per_pixel']
    pixel_center = calibration['sprocket_center_x_px']
    y = lambda x: (pixel_center - x) * scale
    picks = calibration['picks']
    outer, inner = map(y, picks['shaft_ends_x'])
    shoulder = y(picks['outer_journal_end_x'])
    journal_high, journal_low = map(y, picks['inner_journal_x'])
    root = a['small_bore_radius'] - controls['shaft_root_radial_gap']
    core = cylinder(root, inner, shoulder)
    features = [cylinder(controls['outer_journal_radius'], shoulder, outer),
                cylinder(controls['inner_journal_radius'], journal_low, journal_high)]
    width = a['spline_width'] - 2 * controls['shaft_spline_side_gap']
    bottom = a['small_bore_radius'] - 2
    top = a['small_bore_radius'] + a['spline_depth'] - controls['shaft_spline_tip_gap']
    for n in range(int(a['splines'])):
        tooth = Part.makeBox(width, shoulder - inner, top - bottom,
                            App.Vector(-width / 2, inner, bottom))
        tooth.rotate(App.Vector(), App.Vector(0, 1, 0), 360 * n / a['splines'])
        features.append(tooth)
    shaft = core.multiFuse(features).removeSplitter()

    high, low = map(y, picks['brake_outer_faces_x'])
    middle = (high + low) / 2
    radius = (picks['brake_outer_diameter_y'][1] - picks['brake_outer_diameter_y'][0]) * scale / 2
    rim_inner = radius - controls['drum_rim_stock']
    web_outer = rim_inner - controls['drum_blend_radial']
    hub = controls['drum_hub_radius']
    web_low, web_high = middle - controls['drum_web_stock'] / 2, middle + controls['drum_web_stock'] / 2
    # A revolved I-section with tapered rim transitions. Exact cast blends are unknown.
    inset = controls['drum_rim_turn_inset']
    profile = [(0, low), (hub, low), (hub, web_low), (web_outer, web_low),
               (rim_inner, low + inset), (rim_inner, low), (radius, low),
               (radius, high), (rim_inner, high), (rim_inner, high - inset),
               (web_outer, web_high), (hub, web_high),
               (hub, -a['small_overall_width'] / 2), (0, -a['small_overall_width'] / 2)]
    points = [App.Vector(r, axial, 0) for r, axial in profile]
    face = Part.Face(Part.makePolygon(points + [points[0]]))
    drum = face.revolve(App.Vector(), App.Vector(0, 1, 0), 360)
    drum = drum.cut(spline_tools(a, low - 1, 1)).removeSplitter()
    for name, shape in [('shaft', shaft), ('drum', drum)]:
        if not shape.isValid() or len(shape.Solids) != 1:
            raise ValueError('Invalid output rotor: ' + name)
    return {'shaft': shaft, 'drum': drum}, dict(
        shaft_length_mm=outer - inner, shaft_ends_local_y_mm=[inner, outer],
        outer_journal_shoulder_y_mm=shoulder,
        inner_journal_local_y_mm=[journal_low, journal_high],
        drum_rim_local_y_mm=[low, high], drum_outer_radius_mm=radius,
        shaft_root_radius_mm=root, drum_profile_radial_axial_mm=profile)
