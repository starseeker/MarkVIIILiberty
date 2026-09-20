"""Inferred link oil passages and stock-length formed split-pin tails."""
import math
import FreeCAD as App
import Part


def oil_tools(a,detail):
    r=detail['oil_hole_diameter']/2
    return [Part.makeCylinder(r,a['bar_end_radius']+1,App.Vector(x,0,-a['bar_end_radius']-1),App.Vector(0,0,1))
            for x in [0,a['pitch']]]


def formed_cotter(old,a,detail):
    radius=detail['cotter_bend_radius'];angle=math.radians(detail['cotter_bend_angle'])
    wire=(a['cotter_diameter']-a['cotter_center_spacing'])/2;half=a['cotter_center_spacing']/2
    top=a['pin_diameter']/2+a['cotter_head_gap']
    start=-a['pin_diameter']/2-wire-detail['cotter_pin_exit_gap']
    straight=top-start;arc=radius*angle;tail=a['cotter_length']-straight-arc
    if tail<=0:raise ValueError('Source cotter leg length cannot span selected bend')
    b=old.BoundBox
    kept=old.common(Part.makeBox(b.XLength+2,b.YLength+2,b.ZMax-start+1,App.Vector(b.XMin-1,b.YMin-1,start)))
    legs=[];endpoints=[]
    for sign in [-1,1]:
        p=lambda t:App.Vector(sign*(half+radius*(1-math.cos(t))),0,start-radius*math.sin(t))
        end=p(angle)+App.Vector(sign*math.sin(angle),0,-math.cos(angle))*tail
        path=Part.Wire([Part.Arc(p(0),p(angle/2),p(angle)).toShape(),Part.makeLine(p(angle),end)])
        section=Part.Wire([Part.makeCircle(wire,p(0),App.Vector(0,0,-1))])
        legs.append(path.makePipeShell([section],True,False))
        endpoints.append([end.x,end.y,end.z])
    shape=kept.multiFuse(legs).removeSplitter()
    if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid/disconnected formed cotter')
    return shape,dict(straight_length_mm=straight,bend_arc_length_mm=arc,remaining_tail_length_mm=tail,
        total_leg_centerline_mm=straight+arc+tail,nominal_leg_length_mm=a['cotter_length'],
        bend_start_z_mm=start,tail_endpoints=endpoints,old_volume_mm3=old.Volume,new_volume_mm3=shape.Volume,
        proxy_volume_change_mm3=shape.Volume-old.Volume,exact_material_volume_conserved=False)
