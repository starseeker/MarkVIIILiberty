"""Source-length cap studs with inferred castle nuts and formed split pins."""
import math
import FreeCAD as App
import Part

from transmission_support_parts import box
from transmission_output_parts import cylinder as cylinder_y


def cylinder_x(radius,x0,x1,y=0,z=0):
    return Part.makeCylinder(radius,x1-x0,App.Vector(x0,y,z),App.Vector(1,0,0))


def hex_x(af,x0,x1):
    radius=af/math.sqrt(3)
    pts=[App.Vector(x0,radius*math.cos(i*math.pi/3),radius*math.sin(i*math.pi/3)) for i in range(6)]
    return Part.Face(Part.makePolygon(pts+pts[:1])).extrude(App.Vector(x1-x0,0,0))


def split_pin(c):
    half=c['cotter_center_spacing']/2
    wire=(c['cotter_diameter']-c['cotter_center_spacing'])/2
    head=-c['crown_radius']-c['cotter_head_gap']
    bend=c['crown_radius']+c['cotter_exit_gap']
    radius=c['cotter_bend_radius'];angle=math.radians(c['cotter_bend_angle'])
    straight=bend-head;arc=radius*angle;tail=c['cotter_length']-straight-arc
    if tail<=0 or wire<=0:raise ValueError('Cotter stock cannot span the proposed joint')
    pieces=[];endpoints=[]
    for sign in [-1,1]:
        p=lambda t:App.Vector(0,bend+radius*math.sin(t),sign*(half+radius*(1-math.cos(t))))
        start=App.Vector(0,head,sign*half)
        end=p(angle)+App.Vector(0,math.cos(angle),sign*math.sin(angle))*tail
        path=Part.Wire([Part.makeLine(start,p(0)),Part.Arc(p(0),p(angle/2),p(angle)).toShape(),Part.makeLine(p(angle),end)])
        section=Part.Wire([Part.makeCircle(wire,start,App.Vector(0,1,0))])
        pieces.append(path.makePipeShell([section],True,False));endpoints.append([end.x,end.y,end.z])
    eye=c['cotter_eye_radius'];top=head-c['cotter_eye_rise']
    points=[App.Vector(0,head,-half),App.Vector(0,top,-eye)]
    points += [App.Vector(0,top-eye*math.sin(a),eye*math.cos(a))
               for a in [math.pi-i*math.pi/16 for i in range(1,17)]]
    points.append(App.Vector(0,head,half))
    for a,b in zip(points,points[1:]):
        delta=b-a;pieces.append(Part.makeCylinder(wire,delta.Length,a,delta))
    pieces += [Part.makeSphere(wire,p) for p in points]
    shape=pieces[0].multiFuse(pieces[1:]).removeSplitter()
    return shape,dict(straight_length_mm=straight,bend_arc_length_mm=arc,tail_length_mm=tail,
                      total_leg_centerline_mm=straight+arc+tail,tail_endpoints=endpoints,
                      wire_radius_mm=wire,under_eye_y_mm=head,bend_start_y_mm=bend,
                      exact_stock_volume_conserved=False)


def hardware(c,support):
    height=c['nut_height'];slot=c['slot_depth'];rad=c['stud_diameter']/2
    nut=hex_x(c['nut_af'],0,height-slot).fuse(cylinder_x(c['crown_radius'],height-slot,height))
    slots=[]
    for angle in [0,60,120]:
        tool=box(height-slot,height+1,-2*c['crown_radius'],2*c['crown_radius'],
                 -(c['cotter_diameter']+c['cotter_slot_gap'])/2,(c['cotter_diameter']+c['cotter_slot_gap'])/2)
        tool.rotate(App.Vector(),App.Vector(1,0,0),angle);slots.append(tool)
    nut=nut.cut(cylinder_x(rad+c['nut_bore_gap'],-1,height+1)).cut(Part.makeCompound(slots)).removeSplitter()
    cotter,detail=split_pin(c)
    shapes=dict(nut=nut,cotter=cotter);undrilled={}
    for mark in ['MX9','MX10','MX36']:
        length=c[mark+'_length'];blank=cylinder_x(rad,0,length);undrilled[mark]=blank
        hole_x=length-c['stud_end_projection']-slot/2
        bore=Part.makeCylinder(c['cotter_diameter']/2+c['cotter_hole_gap'],c['stud_diameter']+2,
                              App.Vector(hole_x,-rad-1,0),App.Vector(0,1,0))
        shapes[mark]=blank.cut(bore).removeSplitter()
    tip=c['MX9_length']-c['US_thread_length']-support['split_gap']-c['US_thread_recess']
    seat=tip-height-c['stud_end_projection']
    d=dict(stud_tip_x_mm=tip,cap_seating_x_mm=seat,cotter_axis_x_mm=seat+height-slot/2,
           stud_tail_x_mm={m:tip-c[m+'_length'] for m in ['MX9','MX10','MX36']},cotter=detail)
    for key,shape in shapes.items():
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid '+key)
    return shapes,d,undrilled


def receiving_castings(old_bracket,old_cap,role,c,support,dimensions,stack,swap=False):
    radius=support['ear_radius'];bore_radius=c['stud_diameter']/2+support['stud_hole_gap']
    bosses=[];holes=[];spotfaces=[];install=[]
    for index,(y,z) in enumerate(dimensions['stud_axes_yz_mm']):
        mark='MX9' if role=='outer' else ('MX36' if (z>0)!=swap else 'MX10')
        tail=stack['stud_tail_x_mm'][mark]
        bosses.append(cylinder_x(radius,tail-c['blind_end_gap']-c['blind_end_stock'],-support['split_gap'],y,z))
        holes.append(cylinder_x(bore_radius,tail-c['blind_end_gap'],1,y,z))
        spotfaces.append(cylinder_x(radius+.01,stack['cap_seating_x_mm'],200,y,z))
        install.append(dict(index=index+1,mark=mark,y_mm=y,z_mm=z,tail_x_mm=tail,
                            blind_bore_bottom_x_mm=tail-c['blind_end_gap'],
                            US_thread_front_x_mm=tail+c['US_thread_length']))
    bracket_blank=old_bracket.multiFuse(bosses)
    socket=cylinder_y(dimensions['socket_radius_mm'],-dimensions['length_mm']/2-1,dimensions['length_mm']/2+1)
    bracket_blank=bracket_blank.cut(socket)
    bracket=bracket_blank.cut(Part.makeCompound(holes)).removeSplitter()
    cap=old_cap.cut(Part.makeCompound(spotfaces)).removeSplitter()
    for key,shape in [('bracket',bracket),('cap',cap)]:
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid receiving '+role+' '+key)
    return bracket,cap,install,bracket_blank
