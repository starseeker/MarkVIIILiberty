"""Partial cap fittings, porous packing envelopes and inferred bearing-feed paths."""
import math
import FreeCAD as App
import Part
from transmission_support_parts import box
from transmission_stud_parts import cylinder_x, hex_x


def cylinder_z(radius,z0,z1,x=0,y=0):
    return Part.makeCylinder(radius,z1-z0,App.Vector(x,y,z0),App.Vector(0,0,1))


def hex_z(af,z0,z1,x=0):
    shape=hex_x(af,z0,z1)
    shape.rotate(App.Vector(),App.Vector(0,1,0),-90)
    shape.translate(App.Vector(x,0,0))
    return shape


def elbow_sweep(c,radius,start_x,end_z):
    x=c['elbow_straight'];r=c['bend_radius']
    start=App.Vector(start_x,0,0);a=App.Vector(x,0,0)
    mid=App.Vector(x+r/math.sqrt(2),0,r*(1-1/math.sqrt(2)))
    b=App.Vector(x+r,0,r);end=App.Vector(x+r,0,end_z)
    path=Part.Wire([Part.makeLine(start,a),Part.Arc(a,mid,b).toShape(),Part.makeLine(b,end)])
    section=Part.Wire([Part.makeCircle(radius,start,App.Vector(1,0,0))])
    return path.makePipeShell([section],True,False)


def fittings(c):
    x=c['elbow_straight']+c['bend_radius'];r=c['tube_od']/2+c['tube_radial_gap']
    blank=elbow_sweep(c,c['elbow_radius'],-c['spigot_length'],c['connector_top'])
    blank=blank.multiFuse([hex_x(c['wrench_af'],0,c['elbow_straight']),
        cylinder_z(c['connector_radius'],c['bend_radius'],c['connector_top'],x),
        cylinder_z(c['flange_radius'],c['flange_bottom'],c['nut_bottom'],x)]).removeSplitter()
    path=elbow_sweep(c,c['flow_radius'],-c['spigot_length']-1,c['seat_bottom']+.01)
    seat=Part.makeCone(r,c['seat_top_radius'],c['connector_top']-c['seat_bottom'],App.Vector(x,0,c['seat_bottom']))
    counterbore=cylinder_z(r,c['seat_bottom']-1,c['connector_top']+1,x)
    elbow=blank.cut(path.fuse(seat).fuse(counterbore)).removeSplitter()
    slope=(c['seat_top_radius']-r)/(c['connector_top']-c['seat_bottom'])
    small=r+(c['sleeve_bottom']-c['seat_bottom'])*slope
    sleeve=Part.makeCone(small,c['seat_top_radius'],c['connector_top']-c['sleeve_bottom'],App.Vector(x,0,c['sleeve_bottom']))
    sleeve=sleeve.fuse(cylinder_z(c['seat_top_radius'],c['connector_top'],c['sleeve_top'],x))
    sleeve=sleeve.cut(cylinder_z(r,c['sleeve_bottom']-1,c['sleeve_top']+1,x)).removeSplitter()
    nut=hex_z(c['nut_af'],c['nut_bottom'],c['nut_top'],x)
    nut=nut.cut(cylinder_z(c['connector_radius']+c['nut_thread_gap'],c['nut_bottom']-1,c['sleeve_top'],x))
    nut=nut.cut(cylinder_z(c['tube_od']/2+c['nut_tube_gap'],c['nut_bottom']-1,c['nut_top']+1,x)).removeSplitter()
    witness=elbow_sweep(c,1,-c['spigot_length']-3,c['nut_top']+1)
    shapes=dict(elbow=elbow,nut=nut,sleeve=sleeve)
    for name,shape in shapes.items():
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid '+name)
    return shapes,dict(connector_x_mm=x,sleeve_lower_radius_mm=small),dict(blank=blank,witness=witness)


def cap_lubrication(cap,lining,d,support,c):
    inlet=App.Vector(d['cup_front_x_mm'],c['inlet_y'],c['inlet_z'])
    receiver=cylinder_x(c['elbow_radius']+c['spigot_radial_gap'],inlet.x-support['cup_stock']-1,inlet.x+1,inlet.y,inlet.z)
    bore_x=math.sqrt(d['bore_radius_mm']**2-c['gallery_z']**2)
    gallery=cylinder_x(c['gallery_radius'],bore_x-1,d['cup_back_x_mm']+support['cup_stock']+2,0,c['gallery_z'])
    revised=cap.cut(receiver).cut(gallery).removeSplitter();lined=lining.cut(gallery).removeSplitter()
    gap=c['packing_wall_gap'];stock=support['cup_stock']
    wool=box(d['cup_back_x_mm']+stock+gap,d['cup_front_x_mm']-stock-gap,
             -support['cup_width']/2+stock+gap,support['cup_width']/2-stock-gap,
             -support['cup_height']/2+stock+gap,support['cup_height']/2-c['packing_top_gap'])
    # Packing conforms to integral hinge lug intrusions into the cup.
    wool=wool.cut(revised).removeSplitter()
    passage=cylinder_x(1,bore_x-1,d['cup_back_x_mm']+stock+2,0,c['gallery_z'])
    shapes=dict(cap=revised,lining_front=lined,wool=wool)
    for name,shape in shapes.items():
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid '+name)
    return shapes,dict(inlet_origin_mm=[inlet.x,inlet.y,inlet.z],gallery_running_exit_x_mm=bore_x,
                       gallery_axis_z_mm=c['gallery_z'],packing_envelope_mm3=wool.Volume),dict(receiver=receiver,gallery=gallery,passage_witness=passage)
