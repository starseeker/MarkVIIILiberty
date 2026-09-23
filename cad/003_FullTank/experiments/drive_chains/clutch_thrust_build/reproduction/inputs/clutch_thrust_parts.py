"""Reconstruct the separate clutch ball cage, balls and spring-stop ring.

The race profile is an explicit geometric approximation, not bearing design data.
Keep the printed 30 balls and quarter-inch diameter independent of that profile.
"""
import math
import FreeCAD as App
import Part


def cylinder(radius, rear, front, y=0, z=0):
    return Part.makeCylinder(radius, front-rear, App.Vector(rear, y, z), App.Vector(1, 0, 0))


def annulus(inner, outer, rear, front):
    return cylinder(outer, rear, front).cut(cylinder(inner, rear-1, front+1))


def interfaces(c, parent):
    radius = c['ball_diameter']/2
    floor = parent['thrust_front']-c['race_floor_depth']
    center = floor+radius
    return dict(race_bottom=floor, ball_center=center, stop_rear=floor+2*radius,
                pocket_face=floor+c['groove_depth'],
                stop_boss_rear=floor+2*radius-c['groove_depth'])


def build(c, parent_controls, parent_thrust):
    d = interfaces(c, parent_controls)
    radius = c['ball_diameter']/2
    pitch = c['ball_pitch_radius']
    groove = c['race_groove_radius']
    assert groove > radius and c['cage_hole_radius'] > radius
    assert c['ball_count'] == 30 and c['ball_diameter'] == 6.35
    assert 2*pitch*math.sin(math.pi/c['ball_count']) > 2*c['cage_hole_radius']
    thrust = parent_thrust.cut(annulus(pitch-c['pocket_half_width'],
        pitch+c['pocket_half_width'], d['pocket_face'], parent_controls['thrust_front']+1))
    # Offset the concave groove centers to retain axial tangent contact with
    # the smaller ball. Equal centers would silently leave unloaded axial gaps.
    rear_groove = Part.makeTorus(pitch, groove,
        App.Vector(d['ball_center']+groove-radius, 0, 0), App.Vector(1, 0, 0))
    thrust = thrust.cut(rear_groove).removeSplitter()
    stop_inner = pitch-c['stop_bore_offset']
    stop = annulus(stop_inner, c['stop_outer_radius'], d['stop_rear'],
                   d['stop_rear']+c['stop_plate_stock'])
    boss = annulus(pitch-c['stop_boss_half_width'], pitch+c['stop_boss_half_width'],
                   d['stop_boss_rear'], d['stop_rear'])
    stop = stop.fuse(boss)
    front_groove = Part.makeTorus(pitch, groove,
        App.Vector(d['ball_center']-groove+radius, 0, 0), App.Vector(1, 0, 0))
    stop = stop.cut(front_groove)
    for n in range(c['plunger_count']):
        a = math.radians(c['plunger_phase_deg'])+2*math.pi*n/c['plunger_count']
        stop = stop.cut(cylinder(c['plunger_hole_radius'], d['stop_rear']-1,
            d['stop_rear']+c['stop_plate_stock']+1,
            c['plunger_pitch_radius']*math.cos(a), c['plunger_pitch_radius']*math.sin(a)))
    stop = stop.removeSplitter()
    half = c['cage_stock']/2
    cage = annulus(pitch-c['cage_half_width'], pitch+c['cage_half_width'], -half, half)
    occurrences = [dict(name='ClutchThrust_Cage', key='cage', xyz=[d['ball_center'], 0, 0]),
                   dict(name='ClutchThrust_Stop', key='stop', xyz=[0, 0, 0])]
    for n in range(c['ball_count']):
        a = 2*math.pi*n/c['ball_count']
        y, z = pitch*math.cos(a), pitch*math.sin(a)
        cage = cage.cut(cylinder(c['cage_hole_radius'], -half-1, half+1, y, z))
        occurrences.append(dict(name=f'ClutchThrust_Ball{n+1:02}', key='ball', xyz=[d['ball_center'], y, z]))
    parts = dict(cage=cage.removeSplitter(), ball=Part.makeSphere(radius), stop=stop)
    for name, shape in dict(parts, thrust=thrust).items():
        assert shape.isValid() and len(shape.Solids) == 1, name
    return parts, occurrences, thrust, d
