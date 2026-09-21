"""Retain the high-speed drum on its small-sun sleeve with the common M290 ring.

The ring itself is reused from the saved assembly. All new mating dimensions
are recorded reconstruction assumptions, not original manufacturing fits.
"""
import FreeCAD as App
from transmission_core_parts import cylinder


def retention_parts(c, ring_controls, cal, output_y, gear, old_sun, old_drum, ring):
    station = output_y + (cal['sprocket_center_x_px']-c['ring_center_source_x_px'])*cal['mm_per_pixel']
    width = ring.BoundBox.YLength
    low, high = station-width/2, station+width/2
    groove_low, groove_high = low-ring_controls['ring_axial_gap'], high+ring_controls['ring_axial_gap']
    sleeve_low = gear['sun_bush_y_mm'][0]
    gear_low = gear['gear_band_y_mm'][0]
    shoulder = old_drum.BoundBox.YMax+c['drum_shoulder_axial_gap']
    collar_high = groove_high+c['collar_outboard_extension']
    bore = min(f.Surface.Radius for f in old_sun.Faces if type(f.Surface).__name__=='Cylinder')
    assert sleeve_low < groove_low < groove_high < collar_high < shoulder < gear_low
    assert ring_controls['ring_groove_radius'] < ring_controls['ring_inner_radius'] < c['collar_radius'] < ring_controls['ring_outer_radius']
    # Complete circular shoulders provide material all the way round the groove;
    # the former spline root alone lay inside the ring's bore.
    sun = old_sun.fuse(cylinder(c['collar_radius'],sleeve_low,collar_high))
    sun = sun.fuse(cylinder(c['sun_shoulder_radius'],shoulder,gear_low+.01))
    sun = sun.cut(cylinder(bore,sleeve_low-1,gear['sun_bush_y_mm'][1]+1))
    ungrooved = sun.removeSplitter()
    cutter = cylinder(100,groove_low,groove_high).cut(cylinder(ring_controls['ring_groove_radius'],groove_low-1,groove_high+1))
    sun = ungrooved.cut(cutter).removeSplitter()
    seat = high+c['drum_ring_axial_gap']
    relief = ring_controls['ring_outer_radius']+c['drum_ring_radial_gap']
    drum = old_drum.cut(cylinder(relief,old_drum.BoundBox.YMin-1,seat))
    drum = drum.cut(cylinder(c['collar_radius']+c['drum_collar_radial_gap'],old_drum.BoundBox.YMin-1,collar_high+c['drum_collar_axial_gap'])).removeSplitter()
    placed_ring = ring.copy();placed_ring.rotate(App.Vector(),App.Vector(0,1,0),c['ring_gap_phase'])
    placed_ring.translate(App.Vector(0,station,0))
    shapes = dict(sun=sun,drum=drum,ring=placed_ring)
    for key,shape in shapes.items():
        assert shape.isValid() and len(shape.Solids)==1,key
    return shapes, dict(ring_center_y_mm=station,ring_limits_y_mm=[low,high],groove_limits_y_mm=[groove_low,groove_high],
        collar_limits_y_mm=[sleeve_low,collar_high],shoulder_limits_y_mm=[shoulder,gear_low],
        drum_ring_seat_y_mm=seat,drum_collar_relief_end_y_mm=collar_high+c['drum_collar_axial_gap'],
        ring_relief_radius_mm=relief,sun_bore_radius_mm=bore,
        spline_engagement_y_mm=[collar_high+c['drum_collar_axial_gap'],old_drum.BoundBox.YMax]),ungrooved
