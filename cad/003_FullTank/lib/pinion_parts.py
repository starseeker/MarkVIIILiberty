"""Parametric pinion solids from the inspected, source-counted native fixtures."""
import math
import FreeCAD as App
import Part
from .track_parts import cylinder_y,feature
from .idler_parts import block
from .drive_mount_parts import annulus,drill
from .drive_mount_geometry import bearing_points,backing_points
from .wheel_parts import button_rivet


def casting(a):
    gear=cylinder_y(a['sprocket_radius'],a['tooth_width'])
    tools=[]
    for n in range(int(a['teeth'])):
        t=2*math.pi*n/a['teeth']
        tools.append(cylinder_y(a['chain_relief_radius'],a['tooth_width']+2,
                     x=a['chain_pitch_radius']*math.sin(t),z=a['chain_pitch_radius']*math.cos(t)))
    for n in range(6):
        t=2*math.pi*(n+.5)/6
        tools.append(cylinder_y(a['web_hole_radius'],a['tooth_width']+2,
                     x=a['web_hole_circle']*math.sin(t),z=a['web_hole_circle']*math.cos(t)))
    gear=gear.cut(Part.makeCompound(tools))
    pieces=[cylinder_y(a['hub_radius'],a['casting_length']),gear]
    pin_cuts=[]
    for side in [-1,1]:
        for end in [-1,1]:
            y=side*a['bank_center']+end*(a['roller_length']/2+a['roller_end_gap']+a['flange_stock']/2)
            web=cylinder_y(a['bank_web_radius'],a['flange_stock'],y=y)
            bosses=[]
            for n in range(9):
                t=2*math.pi*n/9
                x,z=a['roller_circle']*math.sin(t),a['roller_circle']*math.cos(t)
                bosses.append(cylinder_y(a['boss_radius'],a['flange_stock'],x=x,y=y,z=z))
                pin_cuts.append(cylinder_y(a['pin_bore_radius'],a['flange_stock']+2,x=x,y=y,z=z))
            pieces.append(web.multiFuse(bosses))
    shape=pieces[0].multiFuse(pieces[1:])
    tools=pin_cuts+[cylinder_y(a['casting_bore_radius'],a['casting_length']+2)]
    depth=a['casting_length']/2-a['counterbore_bottom']
    if depth<=0:raise ValueError('Pinion casting lost its common-bearing counterbore')
    for side in [-1,1]:
        tools.append(cylinder_y(a['counterbore_radius'],depth+1,
                     y=side*(a['counterbore_bottom']+(depth+1)/2)))
    return shape.cut(Part.makeCompound(tools))


def roller_pin(a):
    L=a['pin_length'];r=a['pin_diameter']/2;head_start=L-a['head_stock']
    shape=cylinder_y(r,head_start,y=head_start/2)
    shape=shape.fuse(cylinder_y(a['head_radius'],a['head_stock'],y=L-a['head_stock']/2))
    shape=shape.cut(Part.makeCylinder(a['oil_bore_diameter']/2,L-a['roller_axis_on_pin']+11,
                   App.Vector(0,L+1,0),App.Vector(0,-1,0)))
    shape=shape.cut(Part.makeCylinder(a['oil_radial_diameter']/2,r+1,
                   App.Vector(0,a['roller_axis_on_pin'],0),App.Vector(1,0,0)))
    return shape.cut(Part.makeCylinder((a['cotter_nominal_diameter']+a['cotter_hole_clearance'])/2,
                     2*r+2,App.Vector(0,a['cotter_from_inner_end'],-r-1),App.Vector(0,0,1)))


def cotter(a):
    wire=a['cotter_wire_radius'];half=a['cotter_center_spacing']/2
    top=a['pin_diameter']/2+a['cotter_head_gap'];stem=a['cotter_nominal_length']
    pieces=[Part.makeCylinder(wire,stem,App.Vector(sign*half,0,top-stem),App.Vector(0,0,1))
            for sign in [-1,1]]
    radius=a['cotter_eye_radius'];z=top+a['cotter_eye_rise']
    points=[App.Vector(-half,0,top),App.Vector(-radius,0,z)]
    points += [App.Vector(radius*math.cos(t),0,z+radius*math.sin(t))
               for t in [math.pi-i*math.pi/12 for i in range(1,13)]]
    points.append(App.Vector(half,0,top))
    for start,end in zip(points,points[1:]):
        delta=end-start
        pieces.append(Part.makeCylinder(wire,delta.Length,start,delta))
    pieces += [Part.makeSphere(wire,p) for p in points]
    return pieces[0].multiFuse(pieces[1:])


def pipe_plug(diameter,insertion,af,stock,flush=False):
    shape=cylinder_y(diameter/2,insertion,y=-insertion/2)
    if not flush:
        shape=shape.fuse(Part.makeBox(af,stock,af,App.Vector(-af/2,0,-af/2)))
    return shape


def fixed_shaft(a):
    m=a['mount'];R=a['shaft_diameter']/2;j=m['journal_diameter']/2;s=m['shoulder']
    shape=cylinder_y(R,2*s).fuse(cylinder_y(j,a['shaft_length']))
    shape=shape.cut(cylinder_y(a['shaft_oil_bore_diameter']/2,a['shaft_length']+2))
    shape=shape.cut(block(-m['key_width']/2,m['key_width']/2,m['key_start'],
                         a['shaft_end']+a['keyway_end_overrun'],m['key_bottom'],R+1))
    for sign in [-1,1]:
        shape=shape.cut(Part.makeCylinder(a['shaft_oil_radial_diameter']/2,R+1,
                       App.Vector(0,sign*a['bush_center'],0),App.Vector(0,0,1)))
    return shape


def build(doc,name,a):
    role=a['role'];m=a['mount']
    if role=='casting':shape=casting(a)
    elif role=='roller':
        shape=cylinder_y(a['roller_radius'],a['roller_length'])
        shape=shape.cut(cylinder_y(a['roller_bore_radius'],a['roller_length']+2))
    elif role=='pin':shape=roller_pin(a)
    elif role=='cotter':shape=cotter(a)
    elif role=='pin_plug':
        shape=pipe_plug(a['plug_shank_diameter'],a['plug_insertion'],a['plug_head_af'],a['plug_head_stock'])
    elif role=='shaft':shape=fixed_shaft(a)
    elif role in {'shaft_outer_plug','shaft_inner_plug'}:
        shape=pipe_plug(a['shaft_plug_shank_diameter'],a['shaft_plug_insertion'],
                       a['shaft_plug_head_af'],a['shaft_plug_head_stock'],role=='shaft_inner_plug')
    elif role=='inner_bearing':
        ri=m['journal_diameter']/2+m['journal_running_gap']
        shape=annulus(m['barrel_radius'],ri,m['shoulder'],a['shaft_end'])
        shape=shape.fuse(annulus(m['flange_radius'],ri,m['outside'],a['shaft_end']))
        shape=drill(shape,bearing_points(m),m['bearing_screw_diameter']+m['fastener_hole_clearance'])
    elif role=='inner_rivet':
        return button_rivet(doc,name,a['inner_rivet_diameter'],a['inner_rivet_length'],a['shaft_end']-m['shell'])
    else:raise ValueError('Unknown pinion component '+role)
    shape=shape.removeSplitter()
    if not shape.isValid() or len(shape.Solids)!=1:
        raise ValueError('Invalid/disconnected pinion component '+role)
    body=doc.addObject('PartDesign::Body',name)
    feature(body,'Reconstructed'+role.title().replace('_',''),shape)
    if role=='cotter':
        body.addProperty('App::PropertyString','InstalledForm','Evidence')
        body.InstalledForm='Unsplayed supplied-length approximation; deployed forming and retention unqualified'
    return body


def hull_tools(clearance,outer_side,hand):
    a=clearance['values'];m=a['mount'];result=[]
    center=clearance['stations']['port' if hand==1 else 'starboard']
    patterns=[(bearing_points(m),m['bearing_screw_diameter']+m['fastener_hole_clearance'])]
    if outer_side:patterns.append((backing_points(m),m['backing_rivet_diameter']+m['fastener_hole_clearance']))
    for points,diameter in patterns:
        for x,z in points:result.append(cylinder_y(diameter/2,6000,x=center[0]+x,z=center[2]+z))
    result.append(cylinder_y(m['barrel_radius'],6000,x=center[0],z=center[2]))
    return result
