"""Nested clutch bearing/sleeve, keyed cone support and end retention."""
import FreeCAD as App
import Part
from transmission_input_parts import spline


def xc(radius, low, high):
    return Part.makeCylinder(radius, high-low, App.Vector(low, 0, 0), App.Vector(1, 0, 0))


def box(low, high, inner, outer, half_width):
    return Part.makeBox(high-low, outer-inner, 2*half_width, App.Vector(low, inner, -half_width))


def build(c, parent_controls, parent_collar):
    rear = parent_controls['collar_bore_step']
    front = parent_controls['collar_front']
    # Keep the checked six-hole rear lip; replace the formerly vacant body/bore.
    collar = parent_collar.fuse(xc(c['collar_body_radius'],
        parent_controls['joint_face']+parent_controls['collar_lip_stock'], front))
    collar = collar.cut(xc(parent_controls['collar_rear_bore_radius'],
        parent_controls['joint_face']-1, rear))
    collar = collar.cut(xc(c['main_bore_radius'], rear, front+1)).removeSplitter()
    bearing = xc(c['main_bore_radius'], c['bearing_rear'], c['bearing_front'])
    bearing = bearing.cut(xc(c['bearing_front_bore_radius'], c['bearing_rear']-1, c['bearing_front']+1))
    bearing = bearing.cut(xc(c['bearing_rear_bore_radius'], c['bearing_rear']-1, c['relief_rear']))
    bearing = bearing.cut(xc(c['relief_radius'], c['relief_rear'], c['relief_front'])).removeSplitter()
    fillets = [e for e in bearing.Edges if hasattr(e.Curve, 'Radius')
        and abs(e.Curve.Radius-c['relief_radius']) < 1e-6]
    assert len(fillets) == 2
    bearing = bearing.makeFillet(c['relief_fillet'], fillets)
    sleeve = xc(c['sleeve_radius'], rear, rear+c['sleeve_length'])
    sleeve = sleeve.fuse(xc(c['main_bore_radius'], rear, c['bearing_rear'])).removeSplitter()
    sleeve = sleeve.cut(spline(c['sleeve_bore_radius'], c['sleeve_spline_root_radius'],
        c['sleeve_spline_width'], c['sleeve_spline_count'], rear-1, rear+c['sleeve_length']+1)).removeSplitter()
    support = xc(c['support_radius'], c['support_rear'], c['support_front'])
    support = support.fuse(xc(c['support_flange_radius'], c['support_flange_start'], c['support_front'])).removeSplitter()
    fillets = [e for e in support.Edges if hasattr(e.Curve, 'Radius')
        and abs(e.Curve.Radius-c['support_radius']) < 1e-6
        and abs(e.CenterOfMass.x-c['support_flange_start']) < 1e-6]
    assert len(fillets) == 1
    support = support.makeFillet(c['support_fillet'], fillets)
    support = support.cut(xc(c['collar_body_radius']+c['support_running_gap'],
        c['support_rear']-1, c['support_front']+1))
    key = box(0, c['key_length'], 0, c['key_radial_height'], c['key_width']/2)
    occurrences = []
    for n in range(c['key_count']):
        angle = 360*n/c['key_count']
        lower = c['key_rear']-c['key_end_gap']
        upper = c['key_rear']+c['key_length']+c['key_end_gap']
        slot = box(lower, upper, c['key_bed_radius'], c['support_flange_radius']+1,
            c['key_width']/2+c['key_side_gap'])
        slot.rotate(App.Vector(), App.Vector(1,0,0), angle)
        collar = collar.cut(slot)
        slot = box(c['support_rear']-1, c['support_front']+1, 0,
            c['key_bed_radius']+c['key_radial_height']+c['key_roof_gap'],
            c['key_width']/2+c['key_side_gap'])
        slot.rotate(App.Vector(), App.Vector(1,0,0), angle)
        support = support.cut(slot)
        rotation = App.Rotation(App.Vector(1,0,0), angle)
        position = rotation.multVec(App.Vector(c['key_rear'], c['key_bed_radius'], 0))
        occurrences.append(dict(name=f'ClutchStack_Key{n+1}', key='key',
            xyz=[position.x,position.y,position.z], angle=angle))
    # SNL21: 28 is the large thrust collar; 30 is a separate EXTERNAL ring.
    thrust = xc(c['main_bore_radius'], c['bearing_front'], c['thrust_front'])
    thrust = thrust.fuse(xc(c['thrust_outer_radius'], front, c['thrust_front']))
    lip = xc(c['thrust_outer_radius'], c['thrust_lip_rear'], front)
    lip = lip.cut(xc(c['collar_body_radius']+c['thrust_outer_running_gap'],
        c['thrust_lip_rear']-1, front+1))
    thrust = thrust.fuse(lip).cut(xc(c['bearing_front_bore_radius'],
        c['bearing_front']-1, c['thrust_front']+1)).removeSplitter()
    snap = xc(c['snap_outer_radius'], c['snap_rear'], c['snap_front'])
    snap = snap.cut(xc(c['snap_inner_radius'], c['snap_rear']-1, c['snap_front']+1))
    opening = box(c['snap_rear']-1, c['snap_front']+1, 0,
        c['snap_outer_radius']+1, c['snap_gap_width']/2)
    opening.rotate(App.Vector(), App.Vector(1,0,0), c['snap_gap_angle'])
    snap = snap.cut(opening).removeSplitter()
    groove = xc(c['collar_body_radius']+1, c['snap_rear'], c['snap_front'])
    groove = groove.cut(xc(c['snap_inner_radius'], c['snap_rear']-1, c['snap_front']+1))
    collar = collar.cut(groove).removeSplitter()
    parts = dict(bearing=bearing, sleeve=sleeve, support=support.removeSplitter(), key=key, thrust=thrust, snap=snap)
    for key_name in ['bearing','sleeve','support','thrust','snap']:
        occurrences.append(dict(name='ClutchStack_'+key_name, key=key_name, xyz=[0,0,0], angle=0))
    for name, shape in {**parts, 'collar':collar}.items():
        assert shape.isValid() and len(shape.Solids)==1, (name,shape.isValid(),len(shape.Solids))
    return parts, occurrences, collar
