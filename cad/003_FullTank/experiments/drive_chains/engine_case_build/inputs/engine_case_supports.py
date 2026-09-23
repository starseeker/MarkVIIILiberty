"""Provisional dropped front yoke, retaining the inherited rail/pivot interfaces.

Coordinates use the front crossmember X station and floor top. The arm contour
is a clearance-driven estimate; it is not a recovered historical casting profile.
"""
import FreeCAD as App
import Part
from engine_crossmember_parts import box
from engine_suspension_parts import yz_plate

V = App.Vector


def front_yoke(case, suspension, crossmember, axis_z):
    c = suspension
    cc = crossmember
    h = cc['channel_height']
    d = cc['channel_depth'] / 2
    cs = cc['cleat_stock']
    hub_bottom = h + c['packing_stock']
    hub_top = hub_bottom + c['front_hub_height']
    x0 = d + cs
    x1 = x0 + c['front_hub_x_stock']
    half_hub = c['front_hub_half_width']
    rail_y = c['rail_half_spacing']
    rail_w = c['rail_width']
    rail_bottom = (axis_z + c['engine_mount_z_offset_from_crankshaft']
                   - c['rail_height'] - cc['floor_top'])
    mid_y = case['front_arm_mid_y']
    assert half_hub < mid_y < rail_y - rail_w / 2
    mid_z = (hub_top + (rail_bottom - hub_top) * (mid_y - half_hub)
             / (rail_y - rail_w / 2 - half_hub) - case['front_arm_mid_drop'])
    outline = [
        (half_hub, hub_top), (mid_y, mid_z),
        (rail_y - rail_w / 2, rail_bottom),
        (rail_y + rail_w / 2, rail_bottom),
        (rail_y + rail_w / 2, rail_bottom - c['front_pad_stock']),
        (rail_y - rail_w / 2, rail_bottom - c['front_arm_depth']),
        (mid_y, mid_z - c['front_arm_depth']),
        (half_hub, hub_top - c['front_arm_depth']),
    ]
    shape = box(x0, x1, -half_hub, half_hub, hub_bottom, hub_top)
    lock_stock = c['lock_stock_ratio'] * c['half_bolt_diameter']
    engagement = c['cap_length'] - c['rail_flange'] - lock_stock
    for sign in [-1, 1]:
        shape = shape.fuse(yz_plate([(sign*y, z) for y, z in outline], x0, x1))
        shape = shape.fuse(box(
            c['front_pad_x'] - c['front_pad_length']/2,
            c['front_pad_x'] + c['front_pad_length']/2,
            sign*rail_y - rail_w/2, sign*rail_y + rail_w/2,
            rail_bottom - c['front_pad_stock'], rail_bottom))
        cap_x = c['front_pad_x'] + c['front_cap_x_offset']
        shape = shape.fuse(Part.makeCylinder(
            c['front_cap_boss_radius'], c['front_cap_boss_depth'],
            V(cap_x, sign*rail_y, rail_bottom-c['front_cap_boss_depth'])))
        shape = shape.cut(Part.makeCylinder(
            c['half_bolt_diameter']/2 + c['hole_radial_allowance'],
            c['front_pad_stock'] + 2,
            V(c['front_pad_x']+c['front_bolt_x_offset'], sign*rail_y,
              rail_bottom-c['front_pad_stock']-1)))
        shape = shape.cut(Part.makeCylinder(
            c['cap_diameter']/2 + c['thread_radial_allowance'],
            engagement + c['cap_blind_extra_depth'] + 1,
            V(cap_x, sign*rail_y, rail_bottom+1), V(0, 0, -1)))
    shape = shape.cut(Part.makeCylinder(
        c['pivot_bolt_diameter']/2 + c['hole_radial_allowance'],
        cs + c['front_hub_x_stock'] + 2,
        V(d-1, 0, (hub_bottom+hub_top)/2), V(1, 0, 0))).removeSplitter()
    assert shape.isValid() and len(shape.Solids) == 1
    return shape, dict(positive_y_arm_profile=outline, extrusion_x=[x0, x1],
                       mid_drop_from_straight_arm=case['front_arm_mid_drop'],
                       historical_profile_proven=False)
