"""Separate output sleeves, dowels and retaining rings; all inferred fits explicit."""
import FreeCAD as App
import Part

from transmission_output_parts import cylinder


def parts(shaft, shaft_dimensions, rotor_controls, controls, picks, calibration):
    scale = calibration['mm_per_pixel']
    center = calibration['sprocket_center_x_px']
    y = lambda pixel: (center - pixel) * scale
    ring_width = picks['ring_width_px'] * scale
    ring = cylinder(controls['ring_outer_radius'], -ring_width/2, ring_width/2).cut(
        cylinder(controls['ring_inner_radius'], -ring_width, ring_width))
    # A radial opening keeps the retaining ring a separate, single C-shaped solid.
    ring = ring.cut(Part.makeBox(controls['ring_outer_radius']+1, ring_width+2,
                                controls['ring_gap_width'],
                                App.Vector(0,-ring_width/2-1,-controls['ring_gap_width']/2))).removeSplitter()
    ring_stations = [y(pixel) for pixel in picks['ring_center_x_px']]
    updated = shaft.copy()
    for station in ring_stations:
        low, high = station-ring_width/2-controls['ring_axial_gap'], station+ring_width/2+controls['ring_axial_gap']
        groove = cylinder(100, low, high).cut(cylinder(controls['ring_groove_radius'], low-1, high+1))
        updated = updated.cut(groove)
    inner_low, inner_high = shaft_dimensions['inner_journal_local_y_mm']
    outer_high, outer_low = map(y, picks['outer_bush_barrel_end_x_px'])
    definitions = {'ring':ring}; installations = []; dimensions = {}
    for role, low, high, journal in [
            ('inner',inner_low,inner_high,rotor_controls['inner_journal_radius']),
            ('outer',outer_low,outer_high,rotor_controls['outer_journal_radius'])]:
        axial = (low+high)/2; length = high-low
        radius = controls[role+'_bush_radius']; flange = controls[role+'_flange_radius']
        stock = controls['inner_flange_stock'] if role=='inner' else picks['outer_flange_stock_px']*scale
        bore = journal+controls['journal_radial_gap']
        body = cylinder(radius,-length/2,length/2).multiFuse([
            cylinder(flange,-length/2-stock,-length/2), cylinder(flange,length/2,length/2+stock)])
        body = body.cut(cylinder(bore,-length/2-stock-1,length/2+stock+1))
        pin_start = journal-controls['dowel_radial_engagement']
        # The sleeve hole opens radially for pin insertion; the shaft pocket is blind.
        hole = Part.makeCylinder(controls['dowel_diameter']/2+controls['dowel_hole_radial_gap'],
                                 radius+1-pin_start+controls['dowel_hole_bottom_gap'],
                                 App.Vector(pin_start-controls['dowel_hole_bottom_gap'],0,0), App.Vector(1,0,0))
        body = body.cut(hole).removeSplitter()
        shaft_hole = hole.copy(); shaft_hole.translate(App.Vector(0,axial,0))
        updated = updated.cut(shaft_hole)
        definitions[role+'_bush'] = body
        installations.append(dict(role=role,center_y_mm=axial,dowel_start_x_mm=pin_start))
        dimensions[role] = dict(journal_radius_mm=journal, bore_radius_mm=bore,
                               barrel_radius_mm=radius, flange_radius_mm=flange,
                               barrel_length_mm=length, overall_length_mm=length+2*stock,
                               flange_stock_mm=stock, barrel_limits_local_y_mm=[low,high])
    definitions['dowel'] = Part.makeCylinder(controls['dowel_diameter']/2,controls['dowel_length'],
                                            App.Vector(),App.Vector(1,0,0))
    updated = updated.removeSplitter()
    for name, shape in [*definitions.items(),('shaft',updated)]:
        if not shape.isValid() or len(shape.Solids)!=1:
            raise ValueError('Invalid native sleeve/ring part: '+name)
    return updated, definitions, dict(bushes=dimensions,installations=installations,
                                     ring_stations_local_y_mm=ring_stations,ring_width_mm=ring_width)
