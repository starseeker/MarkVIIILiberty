"""Liberty main bevel and locking hardware; explicit estimated machining profiles.

Engine-local X runs from nose to gear. Gear definition X=0 is the rear shaft
flange face before shimming. Hardware definitions retain their joint-local frames.
"""
import math
import FreeCAD as App
import Part
from engine_crankshaft_parts import cyl, ring
from engine_crossmember_parts import box
from transmission_stud_parts import hex_x
from transmission_input_installation_parts import formed_pin
from transmission_bevel_tooth import tooth, repeated_teeth
from transmission_core_parts import revolve

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def clean(s):
    refined = s.copy().removeSplitter()
    return refined if refined.isValid() and len(refined.Solids) == 1 else s


def arc_wire(radius, wire, start, sweep, center=V()):
    s = Part.makeTorus(radius, wire, V(), Z, -180, 180, sweep)
    s.rotate(V(), V(1, 1, 1), 120)
    s.rotate(V(), X, start)
    s.translate(center)
    return s


def parts(c, parent, original_shaft, original_nut, progress=None):
    pc, pd = parent['parent_controls'], parent['parent_datums']
    shaft, thrust_nut = original_shaft.copy(), original_nut.copy()
    shapes, occurrences, groups = {}, [], []
    edits = {'shaft': [], 'thrust_nut': []}

    def audit(name, s):
        assert s.isValid() and len(s.Solids) == 1 and s.Volume > 0, name
        if progress:
            progress(name, s)

    def add(key, name, group, base=V(), rotation=None):
        occurrences.append(dict(key=key, name='EngineGear_' + name, assembly=group,
                                xyz=list(base), rotation=list((rotation or App.Rotation()).Q)))

    # A spline-flanked straight bevel, with an analytic conical root blank.
    one, td = tooth(c['teeth'], c['mating_teeth'], 25.4/c['module'], 25.4/c['module'],
                    c['face_width'], c['pressure_angle_deg'], c['tooth_thinning'], c['flank_samples'])
    ro, yo = td['root_radial_axial_outer_mm']
    ri, yi = td['root_radial_axial_inner_mm']
    back = yo+c['root_embed']
    front = back-c['web_stock']
    blank = revolve([(c['bore_radius'], back), (ro, back), (ro, yo-c['root_embed']),
                     (ri, yi-c['root_embed']), (ri, front), (c['bore_radius'], front)])
    tooth_phase = c['tooth_phase_at_reference_deg']+pc['static_phase_deg']-c['reference_crank_phase_deg']
    gear = blank.multiFuse(repeated_teeth(one, c['teeth'], tooth_phase))
    audit('bevel_before_hub', gear)
    gear.rotate(V(), Z, 90)
    gear.translate(V(back+c['shim_stock'], 0, 0))
    web_front = c['shim_stock']+c['web_stock']
    hub_end = web_front+c['hub_length']
    gear = gear.fuse(ring(c['hub_radius'], c['bore_radius'], web_front-.1, hub_end))
    # Figure86 resolves a broad annular claw lip and larger central opening.
    # Opposed rim interruptions and twelve internal slots remain estimates.
    claw_end = hub_end+c['claw_stock']
    claw_ring = ring(c['hub_radius'], c['bore_radius'], hub_end-.1, claw_end)
    reach = c['hub_radius']+1
    a = math.radians(c['claw_angle_deg'])
    center = V(hub_end-.2, 0, 0)
    p0 = V(hub_end-.2, reach, 0)
    pm = V(hub_end-.2, reach*math.cos(a/2), reach*math.sin(a/2))
    p1 = V(hub_end-.2, reach*math.cos(a), reach*math.sin(a))
    # A triangle's chord truncates broad sectors. Retain the full analytic arc.
    boundary = Part.Wire([Part.makeLine(center, p0), Part.Arc(p0, pm, p1).toShape(), Part.makeLine(p1, center)])
    wedge = Part.Face(boundary).extrude(V(c['claw_stock']+.4, 0, 0))
    dog = claw_ring.common(wedge)
    for n in range(c['claw_count']):
        s = dog.copy(); s.rotate(V(), X, n*360/c['claw_count']-c['claw_angle_deg']/2)
        gear = gear.fuse(s)
    for n in range(c['spline_count']):
        tool = box(c['shim_stock']-1, claw_end+1, c['bore_radius']-1,
                   c['bore_radius']+c['spline_depth'], -c['spline_width']/2, c['spline_width']/2)
        tool.rotate(V(), X, n*360/c['spline_count'])
        gear = gear.cut(tool)

    shim = ring(c['shim_radius'], c['shim_bore_radius'], 0, c['shim_stock'])
    flange_back, flange_face = pd['gear_flange_span']
    grip = flange_face-flange_back+c['shim_stock']+c['web_stock']
    exposure = c['bolt_length']-grip-c['nut_stock']
    assert exposure > 0, 'Source bolt length is shorter than the selected installed stack'
    pin_station = grip+c['nut_stock']-c['castle_slot_depth']/2
    radius = c['bolt_diameter']/2
    bolt = hex_x(c['bolt_head_af'], -c['bolt_head_stock'], 0).fuse(cyl(radius, 0, c['bolt_length']))
    bolt = bolt.cut(Part.makeCylinder(c['cotter_diameter']/2+c['cotter_hole_gap'], 2*radius+2,
                                    V(pin_station, -radius-1, 0), Y))
    nut = hex_x(c['nut_af'], 0, c['nut_stock']-c['castle_slot_depth']).fuse(
        cyl(c['castle_radius'], c['nut_stock']-c['castle_slot_depth'], c['nut_stock']))
    nut = nut.cut(cyl(radius+c['nut_bore_gap'], -1, c['nut_stock']+1))
    for angle in [0, 60, 120]:
        width = c['cotter_diameter']+c['castle_slot_gap']
        tool = box(c['nut_stock']-c['castle_slot_depth'], c['nut_stock']+1, -20, 20, -width/2, width/2)
        tool.rotate(V(), X, angle); nut = nut.cut(tool)
    pin_controls = dict(cotter_center_spacing=.52*c['cotter_diameter'], cotter_diameter=c['cotter_diameter'],
        crown_radius=c['castle_radius'], cotter_head_gap=.15, cotter_exit_gap=.15,
        cotter_bend_radius=.7, cotter_bend_angle=35, cotter_length=c['cotter_length'],
        cotter_eye_radius=1.2, cotter_eye_rise=.6, cotter_eye_join_overlap=.02)
    shapes['cotter'], cotter = formed_pin(pin_controls)
    shapes['bolt'], shapes['nut'] = clean(bolt), clean(nut)
    axes = []
    for n in range(c['bolt_count']):
        phi = n*360/c['bolt_count']
        u = V(0, math.sin(math.radians(phi)), math.cos(math.radians(phi)))
        position = u*c['bolt_circle']; axes.append(list(position))
        # Radial flat of each hex gives space both to the journal and gear rim.
        rot = App.Rotation(X, -phi)
        group = 'EngineGearBoltSet%d' % (n+1)
        groups.append(dict(name=group, parent='EngineDrivingGear',
                           xyz=list(V(flange_back, 0, 0)+position), rotation=list(rot.Q)))
        add('bolt', 'Bolt%d' % (n+1), group)
        add('nut', 'Nut%d' % (n+1), group, V(grip, 0, 0))
        add('cotter', 'Cotter%d' % (n+1), group, V(pin_station, 0, 0))
        receiver = cyl(radius+c['receiver_gap'], flange_back-.1, flange_face+.1, position.y, position.z)
        shaft = shaft.cut(receiver); edits['shaft'].append(receiver)
        receiver = cyl(radius+c['receiver_gap'], -.1, web_front+.1, position.y, position.z)
        gear = gear.cut(receiver); shim = shim.cut(receiver)
    shapes['gear'], shapes['shim'] = clean(gear), clean(shim)
    add('gear', 'DrivingBevel', 'EngineDrivingGear', V(flange_face, 0, 0))
    add('shim', 'ThinShim', 'EngineDrivingGear', V(flange_face, 0, 0))

    # Thrust nut radial screw. Canonical screw shank is +Y, with X=0
    # at the lock station and Y=0 at its blind end.
    phi = math.radians(c['lock_angle_deg'])
    normal = V(0, math.cos(phi), math.sin(phi))
    rotation = App.Rotation(X, c['lock_angle_deg'])
    start = V(c['lock_station'], 0, 0)+normal*c['lock_tip_radius']
    length = c['lock_seat_radius']-c['lock_tip_radius']
    screw = Part.makeCylinder(c['lock_screw_diameter']/2, length, V(), Y).fuse(
        Part.makeCylinder(c['lock_head_radius'], c['lock_head_stock'], V(0, length, 0), Y))
    screw = screw.cut(box(-c['lock_driver_slot_width']/2, c['lock_driver_slot_width']/2,
        length+c['lock_head_stock']-c['lock_driver_slot_depth'], length+c['lock_head_stock']+1,
        -c['lock_head_radius']-1, c['lock_head_radius']+1))
    hole_y = c['wire_pitch_radius']-c['lock_tip_radius']
    screw = screw.cut(Part.makeCylinder(c['wire_crosshole_radius'], 2*c['lock_head_radius']+2,
                                      V(0, hole_y, -c['lock_head_radius']-1), Z))
    receiver = Part.makeCylinder(c['lock_screw_diameter']/2+c['receiver_gap'], length+2,
                                 start-normal*c['lock_blind_gap'], normal)
    shaft = shaft.cut(receiver); thrust_nut = thrust_nut.cut(receiver)
    edits['shaft'].append(receiver); edits['thrust_nut'].append(receiver)
    shapes['lock_screw'] = clean(screw)
    add('lock_screw', 'ThrustLockScrew', 'EngineThrustNutLock', start, rotation)

    # An open 330-degree clip: one end traverses the cross-hole and the
    # other turns into the existing zero-degree wrench slot of the nut.
    pitch, wr = c['wire_pitch_radius'], c['wire_radius']
    point = normal*pitch; tangent = V(0, -math.sin(phi), math.cos(phi))
    entry = Part.makeCylinder(wr, c['wire_entry_tail'], point-tangent*c['wire_entry_tail'], tangent)
    arc = arc_wire(pitch, wr, c['lock_angle_deg'], 360-c['lock_angle_deg'])
    bend = c['wire_end_bend_radius']
    corner = arc_wire(bend, wr, 0, 90, V(0, pitch-bend, 0))
    end = V(0, pitch-bend, bend)
    tail = Part.makeCylinder(wr, pitch-bend-c['wire_anchor_radius'], end, -Y)
    wire = clean(entry.fuse(arc).fuse(corner).fuse(tail))
    for segment in [entry, arc, corner, tail]:
        assert segment.cut(wire).Volume < 1e-6, 'Wire union lost a leg'
    shapes['lock_wire'] = wire
    add('lock_wire', 'ThrustLockWire', 'EngineThrustNutLock', V(c['lock_station'], 0, 0))
    shapes['shaft'], shapes['thrust_nut'] = clean(shaft), clean(thrust_nut)
    for name, s in shapes.items():
        audit(name, s)
    assert len(occurrences) == 22
    return shapes, occurrences, groups, dict(bevel=td, tooth_phase_deg=tooth_phase, gear_back=flange_face+c['shim_stock'],
        gear_web_front=flange_face+web_front, gear_apex=flange_face+back+c['shim_stock'],
        hub_end=flange_face+hub_end, claw_end=flange_face+claw_end,
        bolt_axes=axes, grip=grip, bolt_exposure=exposure, cotter_station=flange_back+pin_station,
        cotter=cotter, cotter_controls=pin_controls,
        lock_normal=list(normal), lock_start=list(start), lock_underhead_length=length,
        wire_length=c['wire_entry_tail']+pitch*math.radians(360-c['lock_angle_deg'])+bend*math.pi/2+pitch-bend-c['wire_anchor_radius']), edits
