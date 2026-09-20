"""Separate shaft, adjuster and bracket solids with exposed inferred interfaces."""
import math
import FreeCAD as App
import Part
from .roller_parts import revolution,lines
from .track_parts import cylinder_y,feature,rounded_rectangle
from .idler_geometry import cap_points,rivet_points


def block(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,App.Vector(x0,y0,z0))


def rounded_xz(x0,x1,z0,z1,y0,y1,r):
    face=Part.Face(rounded_rectangle(x0,x1,z0,z1,r))
    face.rotate(App.Vector(),App.Vector(1,0,0),90)
    face.translate(App.Vector(0,y0,0))
    return face.extrude(App.Vector(0,y1-y0,0))


def hex_y(af,y0,length):
    r=af/math.sqrt(3)
    pts=[App.Vector(r*math.cos(i*math.pi/3),y0,r*math.sin(i*math.pi/3)) for i in range(6)]
    return Part.Face(Part.makePolygon(pts+pts[:1])).extrude(App.Vector(0,length,0))


def opening(a,guard_border=0):
    half=a['idler_guard_length']/2+guard_border;z=a['idler_guard_height']/2+guard_border
    return block(a['screw_head_center']-half,a['screw_head_center']+half,-3000,3000,-z,z)


def neck_opening(a):
    c=a['idler_neck_clearance'];h=a['idler_bracket_halfheight']
    return block(a['idler_bracket_rear_x']-c,a['screw_head_start']+c,-3000,3000,-h-c,h+c)


def hull_tools(clearance,outer_side):
    """Support-owned fixed apertures; local X follows the source screw axis."""
    a=clearance['values'];tools=[neck_opening(a),opening(a,a['idler_guard_border'])]
    for x,z in cap_points(a):tools.append(cylinder_y((a['idler_cap_diameter']+a['idler_cap_bore_clearance'])/2,6000,x=x,z=z))
    if outer_side:
        for x,z in rivet_points(a):tools.append(cylinder_y((a['idler_plate_rivet_diameter']+a['wheel_rivet_hole_clearance'])/2,6000,x=x,z=z))
    for tool in tools:
        tool.rotate(App.Vector(),App.Vector(0,1,0),-clearance['angle_deg'])
        tool.translate(App.Vector(clearance['x'],0,clearance['z']))
    return tools


def build(doc,name,a):
    role=a['role'];end=a['idler_shaft_length']/2;outer=a['shell_outer']
    if role=='shaft':
        r=a['idler_shaft_diameter']/2;small=a['idler_journal_diameter']/2;shoulder=a['bracket_inner']
        body=revolution(doc,name,lines([(0,-end),(small,-end),(small,-shoulder),(r,-shoulder),
            (r,shoulder),(small,shoulder),(small,end),(0,end)]))
        shape=body.Shape
        shape=shape.cut(cylinder_y(a['idler_oil_gallery']/2,2*end+2,z=a['idler_oil_height']))
        for side in [-1,1]:
            shape=shape.cut(Part.makeCylinder((a['idler_screw_diameter']+a['idler_screw_bore_clearance'])/2,2*r+2,
                App.Vector(-r-1,side*a['screw_y'],0),App.Vector(1,0,0)))
            shape=shape.cut(Part.makeCylinder(a['roller_oil_bore']/2,a['idler_oil_plug_depth'],
                App.Vector(0,side*end,a['idler_oil_height']),App.Vector(0,-side,0)))
            shape=shape.cut(Part.makeCylinder(a['idler_locking_bore']/2,end-a['copper_start']+1,
                App.Vector(0,side*a['copper_start'],0),App.Vector(0,side,0)))
            shape=shape.cut(Part.makeCylinder(a['idler_oil_radial_bore']/2,r-a['idler_oil_height']+1,
                App.Vector(0,side*(a['wheel_boss_length']-a['wheel_bush_length'])/2,a['idler_oil_height'])))
        feature(body,'CrossBoresOilGalleryAndLockingDrilling',shape.removeSplitter());return body
    if role=='washer':
        ri=a['idler_shaft_fastener_bore']/2;ro=a['idler_washer_diameter']/2;t=a['idler_washer_stock']
        return revolution(doc,name,lines([(ri,0),(ro,0),(ro,t),(ri,t)]))
    if role=='plate_rivet':
        from .wheel_parts import button_rivet
        return button_rivet(doc,name,a['idler_plate_rivet_diameter'],a['idler_plate_rivet_length'],
                            a['hull_front_thickness']+a['idler_plate_stock'])
    body=doc.addObject('PartDesign::Body',name)
    if role=='nut':
        h=a['idler_nut_stock'];shape=hex_y(a['idler_nut_af'],0,h)
        shape=shape.cut(cylinder_y(a['idler_shaft_fastener_bore']/2,h+2,y=h/2))
    elif role=='adjusting_screw':
        x=a['idler_screw_tip'];head=a['screw_head_start']
        shape=Part.makeCylinder(a['idler_screw_diameter']/2,head-x,App.Vector(x,0,0),App.Vector(1,0,0))
        cap=hex_y(a['idler_screw_head_af'],0,a['idler_screw_head_stock'])
        cap.rotate(App.Vector(),App.Vector(0,0,1),-90);cap.translate(App.Vector(head,0,0))
        shape=shape.fuse(cap)
    elif role=='copper':
        r=a['idler_copper_diameter']/2;t=a['idler_copper_length'];q=a['copper_start']-a['screw_y']
        shape=cylinder_y(r,t,y=t/2)
        shape=shape.cut(Part.makeCylinder(a['idler_screw_diameter']/2,2*r+2,App.Vector(-r-1,-q,0),App.Vector(1,0,0)))
    elif role=='locking_screw':
        length=end+a['idler_locking_head_gap']-a['locking_tip'];stock=a['idler_locking_head_stock']
        shape=cylinder_y(a['idler_locking_diameter']/2,length,y=length/2)
        shape=shape.fuse(cylinder_y(a['idler_locking_head_diameter']/2,stock,y=length+stock/2))
        r=a['idler_locking_head_diameter']/2;w=a['idler_locking_slot']/2
        shape=shape.cut(block(-r-1,r+1,length+stock/2,length+stock+1,-w,w))
    elif role=='cap_screw':
        length=a['idler_cap_length'];h=a['idler_cap_head_stock']
        shape=cylinder_y(a['idler_cap_diameter']/2,length,y=-length/2).fuse(hex_y(a['idler_cap_head_af'],0,h))
    elif role=='bracket':
        h=a['idler_bracket_halfheight'];front=a['screw_head_start'];foot=a['idler_bracket_foot_stock']
        shape=block(a['idler_bracket_rear_x'],front,a['bracket_inner']-outer,a['bracket_outer']-outer,-h,h)
        fh=a['idler_bracket_foot_halfheight']
        shape=shape.fuse(block(a['idler_bracket_foot_rear_x'],a['idler_bracket_foot_front_x'],0,foot,-fh,fh))
        slot=rounded_xz(a['idler_guide_rear_x'],front-a['idler_guide_front_stock'],
            -a['idler_guide_halfheight'],a['idler_guide_halfheight'],-100,100,a['idler_guide_corner'])
        shape=shape.cut(slot)
        # Open the foot beyond the front post so the adjusting-screw head can
        # bear on that post without occupying the foot or flush guard bezel.
        shape=shape.cut(block(front,1000,-100,100,-a['idler_guard_height']/2-a['idler_guard_border'],
                             a['idler_guard_height']/2+a['idler_guard_border']))
        shape=shape.cut(Part.makeCylinder((a['idler_screw_diameter']+a['idler_screw_bore_clearance'])/2,1000,
            App.Vector(-500,a['idler_screw_axis_offset'],0),App.Vector(1,0,0)))
        for x,z in cap_points(a):shape=shape.cut(cylinder_y((a['idler_cap_diameter']+a['idler_cap_bore_clearance'])/2,200,x=x,z=z))
    elif role=='plate':
        y=-a['hull_front_thickness'];h=a['idler_plate_halfheight']
        shape=rounded_xz(a['idler_plate_rear_x'],a['idler_plate_front_x'],-h,h,y-a['idler_plate_stock'],y,a['idler_plate_corner'])
        shape=shape.cut(neck_opening(a)).cut(opening(a,a['idler_guard_border']))
        for x,z in cap_points(a):shape=shape.cut(cylinder_y((a['idler_cap_diameter']+a['idler_cap_bore_clearance'])/2,200,x=x,z=z))
        # All four plates share this provisional drilling. Only the two outer
        # joints have source-identified rivets; inner retention remains open.
        for x,z in rivet_points(a):shape=shape.cut(cylinder_y((a['idler_plate_rivet_diameter']+a['wheel_rivet_hole_clearance'])/2,200,x=x,z=z))
    elif role=='guard':
        shape=opening(a,a['idler_guard_border']).cut(opening(a)).cut(neck_opening(a))
        shape=shape.common(block(-500,1000,-a['idler_guard_stock'],0,-500,500))
    else:raise ValueError('Unknown idler component '+role)
    shape=shape.removeSplitter()
    if len(shape.Solids)!=1 or not shape.isValid():raise ValueError('Invalid/disconnected idler part '+role)
    feature(body,'Reconstructed'+role.title().replace('_',''),shape)
    return body
