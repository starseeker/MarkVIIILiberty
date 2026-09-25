"""Reconstruct the estimated shared M330 lower arm using its original construction."""
import FreeCAD as App
import Part
from transmission_brake_front_parts import cy
from transmission_brake_anchor_parts import strip

V = App.Vector


def lever(c):
    eye_width = 2*c['lug_y']-c['lug_stock']-2*c['eye_side_clearance']
    bore = c['pin_diameter']/2+c['pin_bore_allowance']
    swivel = V(c['swivel_forward_offset'], 0, 0)
    end = V(c['lever_end_x'], 0, c['lever_end_z'])
    shape = cy(c['lever_eye_radius'], eye_width).multiFuse([
        cy(c['lever_head_radius'], c['swivel_width'], swivel),
        strip(V(), swivel, c['lever_web_width'], -c['swivel_width']/2, c['swivel_width']),
        strip(V(c['lever_leg_root_x'], 0, c['lever_leg_root_z']), end,
              c['lever_leg_width'], -c['lever_leg_stock']/2, c['lever_leg_stock']),
        cy(c['lever_end_radius'], c['lever_leg_stock'], end)])
    shape = shape.cut(Part.makeBox(200, c['swivel_gap'], 150,
                                  V(c['lever_slot_start_x'], -c['swivel_gap']/2, -75)))
    shape = shape.cut(cy(bore, eye_width+2)).cut(
        cy(c['swivel_radius']+c['swivel_bore_allowance'], c['swivel_width']+2, swivel))
    return shape.cut(cy(c['lever_end_bore_radius'], c['lever_leg_stock']+2, end))
