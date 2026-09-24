"""MX1 through-bolt joints on inferred common casting-pad planes.

The common receiver plane and twenty-hole distribution are declared development
hypotheses. Keep source uncertainty separate from exact joint geometry.
"""
import FreeCAD as App
import Part

from transmission_stud_parts import cylinder_x, hex_x
from transmission_input_installation_parts import formed_pin


def parts(c, mount, pin_controls, brackets, channels, bracket_dimensions):
    x = mount['frame_front_x']
    head_seat = bracket_dimensions['outer']['foot_front_x_mm']
    nut_seat = x - mount['flange_root_stock'] - mount['washer_root_allowance']
    pin_x = nut_seat - mount['nut_height'] + mount['nut_slot_depth'] / 2
    pin_from_head = head_seat - pin_x
    radius = c['bolt_diameter'] / 2
    bore = radius + c['receiver_radial_clearance']
    bolt = cylinder_x(radius, 0, c['bolt_under_head_length']).fuse(
        hex_x(c['bolt_head_af'], -c['bolt_head_height'], 0))
    bolt = bolt.cut(Part.makeCylinder(c['cotter_diameter']/2 + pin_controls['cotter_hole_gap'],
        2*radius+2, App.Vector(pin_from_head, -radius-1, 0), App.Vector(0,1,0)))
    pc = dict(pin_controls, cotter_diameter=c['cotter_diameter'], cotter_length=c['cotter_length'])
    cotter, pin_detail = formed_pin(pc)
    definitions = dict(bolt=bolt, cotter=cotter)
    revised = {role: shape.copy() for role, shape in brackets.items()}
    revised_channels = {label: shape.copy() for label, shape in channels.items()}
    joints = []
    backward = App.Rotation(App.Vector(0,0,1),180)
    for role in ['inner','outer']:
        for label, sign, web in [('Upper',1,mount['top_web_z']), ('Lower',-1,mount['bottom_web_z'])]:
            z = web + sign*c['flange_height_station']
            for index, y in enumerate(c[role+'_row_offsets']):
                # All bolt heads bear on a true planar receiver. The center
                # outside row otherwise strikes the inferred sloping cast web.
                revised[role] = revised[role].cut(cylinder_x(c['head_spotface_radius'],head_seat,0,y,z))
                revised[role] = revised[role].cut(cylinder_x(bore,x-1,head_seat+1,y,z))
                transforms = dict(
                    bolt=App.Placement(App.Vector(head_seat,y,z),backward),
                    nut=App.Placement(App.Vector(nut_seat,y,z),backward),
                    cotter=App.Placement(App.Vector(pin_x,y,z),backward),
                    washer=App.Placement(App.Vector(nut_seat,y,z),
                        App.Rotation(App.Vector(1,0,0),0 if sign>0 else 180)))
                joints.append(dict(role=role,end=label,index=index,y_local_mm=y,z_local_mm=z,
                    channel_web_z_mm=web,placements={k:list(v.toMatrix().A) for k,v in transforms.items()}))
    # The actual transverse stations come from the saved bearing occurrences.
    # Channel holes are applied by the builder after composing those frames.
    for name, shape in list(definitions.items())+list(revised.items()):
        assert shape.isValid() and len(shape.Solids)==1, name
    return definitions, revised, revised_channels, dict(
        joints=joints,head_seat_x_mm=head_seat,nut_seat_x_mm=nut_seat,
        cotter_axis_x_mm=pin_x,cotter_from_head_mm=pin_from_head,
        bolt_tip_x_mm=head_seat-c['bolt_under_head_length'],
        tip_projection_mm=nut_seat-mount['nut_height']-(head_seat-c['bolt_under_head_length']),
        cotter=pin_detail,pin_controls=pc)
