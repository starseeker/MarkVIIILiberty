"""MX5 case-to-channel joints, with explicitly inferred cast bosses and taper.

All shapes use the transmission core frame. Four bosses are integral additions
to the retained M263 casting. Threads are nominal cylindrical envelopes. The
boss outline and channel taper are hypotheses, not historical dimensions.
"""
import FreeCAD as App
import Part
from transmission_frame_parts import xz_plate
from transmission_stud_parts import cylinder_x
from transmission_input_installation_parts import formed_pin


def moved(shape, xyz, rotation=None):
    s = shape.copy()
    s.Placement = App.Placement(App.Vector(*xyz), rotation or App.Rotation()).multiply(s.Placement)
    return s


def case_mount_parts(c, old_case, channels, nut, pin_controls):
    """Return definitions, installed core-local shapes and interface datums."""
    x = c['frame_front_x']
    height, stock = c['channel_height'], c['channel_stock']
    taper = c['flange_root_stock'] - stock
    slope = taper / (height - stock)
    seat = x - c['flange_root_stock'] - c['washer_root_allowance']
    tip = seat - c['nut_height'] - c['tip_projection']
    end = tip + c['stud_length']
    pin_x = seat - c['nut_height'] + c['nut_slot_depth'] / 2
    radius = c['stud_diameter'] / 2
    bore = radius + c['receiver_gap']
    definitions = {}
    stud = cylinder_x(radius, 0, c['stud_length'])
    tool = Part.makeCylinder(c['cotter_diameter']/2 + c['cotter_hole_gap'],
        2*radius+2, App.Vector(pin_x-tip, -radius-1, 0), App.Vector(0,1,0))
    definitions['stud'] = stud.cut(tool).removeSplitter()
    definitions['nut'] = nut.copy()
    definitions['cotter'], pin_detail = formed_pin(pin_controls)
    wh = c['washer_height']/2
    def inner_face(local_z):
        return x - c['flange_root_stock'] + slope*(c['stud_flange_height']+local_z-stock)
    # Washer nut seat is local X=0; the opposite face follows the flange taper.
    definitions['washer'] = xz_plate([(0,-wh),(inner_face(-wh)-seat,-wh),
        (inner_face(wh)-seat,wh),(0,wh)],-c['washer_width']/2,c['washer_width']/2)
    # Preserve two analytic half-cylinder faces and their half-ellipse trims.
    # A single full-period ellipse gave a repeatable STEP mass error despite
    # empty Boolean differences. Refining this seam recreates that weakness.
    half = Part.makeCylinder(bore,c['washer_root_allowance']+taper+3,
        App.Vector(-1,0,0),App.Vector(1,0,0),180)
    other = half.copy(); other.rotate(App.Vector(),App.Vector(1,0,0),180)
    definitions['washer'] = definitions['washer'].cut(half).cut(other)
    case = old_case.copy()
    revised = {}
    installed = {}
    mounts = []
    bosses = []
    holes = []
    outward = App.Rotation(App.Vector(0,0,1),180)
    for label, sign, zbase, channel in [
        ('Upper',1,c['top_web_z'],channels['top']),
        ('Lower',-1,c['bottom_web_z'],channels['bottom'])]:
        # Keep the exterior channel planes and inherited member placement.
        wedges = []
        for profile in [[(-stock,stock),(-c['flange_root_stock'],stock),(-stock,height)],
            [(-c['channel_depth']+stock,stock),(-c['channel_depth']+c['flange_root_stock'],stock),(-c['channel_depth']+stock,height)]]:
            if taper:
                wedges.append(xz_plate([(xx,sign*zz) for xx,zz in profile],
                    -c['channel_half_span'],c['channel_half_span']))
        member = channel.multiFuse(wedges) if wedges else channel.copy()
        member_holes = []
        z = zbase + sign*c['stud_flange_height']
        for side, y in [('Port',c['stud_half_span']),('Starboard',-c['stud_half_span'])]:
            name = label+side
            bosses.append(cylinder_x(c['boss_radius'],x,end+c['blind_gap']+c['blind_stock'],y,z))
            holes.append(cylinder_x(bore,x-1,end+c['blind_gap'],y,z))
            member_holes.append(cylinder_x(bore,-c['flange_root_stock']-1,1,y,sign*c['stud_flange_height']))
            transforms = dict(stud=App.Placement(App.Vector(tip,y,z),App.Rotation()),
                nut=App.Placement(App.Vector(seat,y,z),outward),
                cotter=App.Placement(App.Vector(pin_x,y,z),outward),
                washer=App.Placement(App.Vector(seat,y,z),App.Rotation(App.Vector(1,0,0),0 if sign>0 else 180)))
            for key, placement in transforms.items():
                shape = definitions[key].copy()
                shape.Placement = placement.multiply(shape.Placement)
                installed[name+'_'+key] = shape
            mounts.append(dict(name=name,channel=label,y=y,z=z,channel_z=zbase,
                placements={k:list(v.toMatrix().A) for k,v in transforms.items()}))
        revised[label] = member.cut(Part.makeCompound(member_holes)).removeSplitter()
        installed[label+'_channel'] = moved(revised[label],[x,0,zbase])
    case = case.multiFuse(bosses).cut(Part.makeCompound(holes)).removeSplitter()
    revised['case'] = case
    installed['case'] = case
    for key, shape in list(definitions.items())+list(revised.items()):
        assert shape.isValid() and len(shape.Solids)==1, (key,shape.isValid(),len(shape.Solids))
    return definitions, revised, installed, dict(mounts=mounts,stud_tip_x=tip,
        stud_embedded_end_x=end,cotter_axis_x=pin_x,nut_seat_x=seat,
        US_thread_x=[end-c['US_thread_length'],end],SAE_thread_x=[tip,tip+c['SAE_thread_length']],
        boss_front_x=end+c['blind_gap']+c['blind_stock'],channel_slope=slope,
        pin=pin_detail,source_profile_fit_qualified=False)
