"""Reconstruct casing stock, openings and source-counted joints for a chain route."""
import FreeCAD as App
import Part
from casing_parts import shells
from casing_mount_parts import joint, cutter, round_rectangle
from casing_cap_parts import cap_joint
from casing_trim_parts import trim, drill
from casing_front_parts import narrowed_front


def reconstruct(controls, route, wall, centers, support_joints, big_hub_radius, small_hub_radius):
    casing, mount, cap, trimming, support, front = [controls[k] for k in
        ['casing', 'mount', 'cap', 'trim', 'support', 'front']]
    shapes, dimensions = shells(casing, route, big_hub_radius, small_hub_radius)
    wb = wall.BoundBox
    slab = Part.makeBox(wb.XLength, 6000, 6000, App.Vector(wb.XMin, -3000, -1000))
    section = shapes['body'].common(slab).BoundBox
    gap = casing['passage_straight_gap']
    z0, z1 = section.ZMin-gap, section.ZMax+gap
    width, radius = section.YLength+2*gap, casing['passage_corner_radius']
    opening = dict(width_mm=width, bottom_z_mm=z0, top_z_mm=z1, corner_radius_mm=radius)
    shell = dict(dimensions=dimensions, wall_opening_changes=[opening])
    wall_tools = []
    for cy in centers.values():
        assert wb.YMin < cy-width/2 < cy+width/2 < wb.YMax
        assert wb.ZMin < z0 < z1 < wb.ZMax
        wall_tools.append(round_rectangle(wb.XMin-1, wb.XLength+2, cy-width/2,
                                          cy+width/2, z0, z1, radius))
    revised_wall = wall.cut(Part.makeCompound(wall_tools)).removeSplitter()

    angle, wall_stations = joint(mount, casing, route, shell, wb)
    case_tools = [cutter(s,mount['case_rivet_diameter']+mount['hole_diameter_clearance'])
                  for s in wall_stations['case']]
    flange_tools = [cutter(s,mount['wall_rivet_diameter']+mount['hole_diameter_clearance'])
                    for s in wall_stations['wall']]
    angle = angle.cut(Part.makeCompound(case_tools+flange_tools)).removeSplitter()
    shapes['body'] = shapes['body'].cut(Part.makeCompound(case_tools)).removeSplitter()
    tools = []
    for cy in centers.values():
        for tool in flange_tools:
            one = tool.copy()
            one.translate(App.Vector(0,cy,0))
            tools.append(one)
    revised_wall = revised_wall.cut(Part.makeCompound(tools)).removeSplitter()

    cap_parts, cap_stations, cap_dimensions = cap_joint(cap,casing,route,shell)
    trim_parts, trim_stations = trim(trimming,casing,route,shell)
    for owner in ['Body','Cap']:
        tools = [cutter(s,cap['rivet_diameter']+cap['hole_diameter_clearance'])
                 for s in cap_stations['rivets'] if s['owner']==owner]
        shapes[owner.lower()] = shapes[owner.lower()].cut(Part.makeCompound(tools)).removeSplitter()
        tools = [drill(s,trimming) for s in trim_stations if s['owner']==owner]
        shapes[owner.lower()] = shapes[owner.lower()].cut(Part.makeCompound(tools)).removeSplitter()
    tools = [cutter(s,support['case_rivet_diameter']+support['hole_diameter_clearance'])
             for j in support_joints if j['hand']=='Port' for s in j['stations']['case_rivets']]
    assert len(tools)==14
    shapes['body'] = shapes['body'].cut(Part.makeCompound(tools)).removeSplitter()
    shapes['body'], taper_report = narrowed_front(shapes['body'],casing,front,route,dimensions)

    replacements = dict(Def_Casing_body=shapes['body'],Def_Casing_cap=shapes['cap'],
                        Def_CasingWallAngle=angle,Def_hull_engine_back=revised_wall)
    replacements.update({'Def_CapJoint'+name:part['shape'] for name,part in cap_parts.items()})
    for name,shape in replacements.items():
        assert shape.Placement.isIdentity() and shape.isValid() and len(shape.Solids)==1,name

    poses = {}
    def pose(hand,name,center,axis=(0,1,0)):
        poses[hand+name] = App.Placement(App.Vector(*center)+App.Vector(0,centers[hand],0),
                                       App.Rotation(App.Vector(0,1,0),App.Vector(*axis)))
    for hand in centers:
        for role in ['wall','case']:
            for n,s in enumerate(wall_stations[role]):
                pose(hand,'CasingWall_'+role.title()+'Rivet%02d'%n,s['center'],s['axis'])
        for s in cap_stations['rivets']:
            pose(hand,'CasingCap_'+s['name'],s['center'],s['axis'])
        for s in cap_stations['bolts']:
            x,y,z=s['center']; grip=s['grip']
            for suffix,xx in [('Bolt',x+grip/2),('Washer',x-grip/2-cap['washer_stock']),
                              ('Nut',x-grip/2-cap['washer_stock']-cap['nut_stock'])]:
                pose(hand,'CasingCap_'+s['name']+suffix,[xx,y,z],s['axis'])
    assert len(poses)==134
    details = dict(dimensions=dimensions,wall_opening=opening,wall_stations=wall_stations,
                   cap_stations=cap_stations,cap_dimensions=cap_dimensions,
                   trim_stations=trim_stations,taper_report=taper_report,
                   regenerated_trim_names=list(trim_parts))
    return replacements,poses,trim_parts,details
