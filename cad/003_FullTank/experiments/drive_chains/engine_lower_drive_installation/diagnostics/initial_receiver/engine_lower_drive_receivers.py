"""Local lower-case receiver reconstruction, in engine coordinates (mm).

LIB23/28 and SNL19 require an integral cylindrical lug and long screw support.
LIB96/107 and SNL14/17 guide the pump openings. Unprinted casting dimensions
remain estimates; this module does not manufacture a pump or certify its fit.
"""
import FreeCAD as App
import Part
from engine_crossmember_parts import box

V = App.Vector
X, Z = V(1, 0, 0), V(0, 0, 1)


def revise(original, c, unit, apex, driver_controls, progress=None):
    def audit(label, shape):
        if progress:
            progress(label, shape)
        assert shape.isValid() and len(shape.Solids) == 1, (label, len(shape.Solids))

    s = original.copy()
    end, width, top = c['bay_rear_x'], c['bay_half_width'], c['bay_top_z']
    floor, wall = c['oil_mount_z'], c['case_wall']
    ox, outer, opening = c['oil_center_x'], c['oil_flange_radius'], c['oil_open_radius']
    # Fill the former rear wall/aperture and connect the enlarged bottom well.
    # Machining follows the complete casting additions, so stale wall stock
    # cannot obstruct the replacement cavity or either receiver.
    s = s.fuse(box(c['bay_front_x'], end, -width, width, floor, top))
    s = s.fuse(Part.makeCylinder(outer, c['oil_well_top_z']-floor, V(ox, 0, floor), Z))
    audit('receiver_outer_well', s)
    px0, px1 = c['pump_tunnel_front_x'], c['pump_mount_x']
    pz = -driver_controls['pump_axis_drop']
    s = s.fuse(Part.makeCylinder(c['pump_boss_radius'], px1-px0, V(px0, 0, pz), X))
    audit('receiver_pump_boss', s)
    s = s.cut(box(c['bay_front_x']+wall, end-wall, -width+wall, width-wall,
                  floor+wall, top+.01))
    s = s.cut(Part.makeCylinder(opening, c['oil_well_top_z']-floor+2,
                                V(ox, 0, floor-1), Z))
    # Large rear opening admits the complete water-pump gear/retainer assembly.
    # It must remain above the continuous oil-pump mounting rim below.
    s = s.cut(Part.makeCylinder(c['pump_open_radius'], px1-px0+2,
                                V(px0-1, 0, pz), X))
    audit('receiver_pump_openings', s)

    lo, hi = unit['housing_span']
    lug_low = lo+c['lug_end_inset']
    lug_high = hi-c['lug_end_inset']
    radius = driver_controls['housing_radius']+c['lug_radial_clearance']
    s = s.fuse(Part.makeCylinder(radius+c['lug_wall'], lug_high-lug_low,
                                V(apex, 0, lug_low), Z))
    mid = unit['mid_z']
    screw_tip, screw_seat = [apex+x for x in unit['retaining_screw_span']]
    boss_start = apex+c['screw_boss_start_offset']
    s = s.fuse(Part.makeCone(c['screw_boss_root_radius'], c['screw_boss_seat_radius'],
                             screw_seat-boss_start, V(boss_start, 0, mid), X))
    audit('receiver_lug_and_screw_support', s)
    # A continuous cylindrical bore preserves the source service direction.
    # Its radius also admits the upper integral gear, not merely the journal.
    s = s.cut(Part.makeCylinder(radius, top-floor+2, V(apex, 0, floor-1), Z))
    s = s.cut(Part.makeCylinder(driver_controls['retaining_screw_diameter']/2+
                                c['screw_radial_clearance'], screw_seat-screw_tip+2,
                                V(screw_tip-1, 0, mid), X))
    audit('receiver_machined', s)
    cleaned = s.copy().removeSplitter()
    if cleaned.isValid() and len(cleaned.Solids) == 1:
        s = cleaned
    audit('receiver_finished', s)
    datums = dict(lug_axis=[apex, 0, 0], lug_span=[lug_low, lug_high],
                  lug_bore_radius=radius, screw_head_seat=[screw_seat, 0, mid],
                  oil_mount_center=[ox, 0, floor], oil_open_radius=opening,
                  oil_axis_offset=apex-ox, pump_axis=[0, 0, pz],
                  pump_mount_center=[px1, 0, pz], pump_open_radius=c['pump_open_radius'],
                  historically_measured=False, complete_pump_fit_checked=False)
    return s, datums
