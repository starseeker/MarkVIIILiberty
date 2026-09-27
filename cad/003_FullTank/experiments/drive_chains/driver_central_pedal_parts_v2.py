"""Complete central pedal/bridle solids; inferred joint graph and unprinted sections."""
import math
import FreeCAD as App
import Part
from driver_control_linkage_parts_v3 import strut
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
def axle(radius,width,point=V()):return Part.makeCylinder(radius,width,point-Y*width/2,Y)
def finish(q):
    clean=q.copy().removeSplitter()
    if clean.isValid() and len(clean.Solids)==1 and clean.getTolerance(1)<=q.getTolerance(1)+1e-10:q=clean
    assert q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4
    return q
def rectangle(x,y,z,wy,hz):
    points=[V(x,y+dy,z+dz) for dy,dz in [(-wy/2,-hz/2),(wy/2,-hz/2),(wy/2,hz/2),(-wy/2,hz/2)]]
    return Part.Wire(Part.makePolygon(points+points[:1]).Edges)
def pedal(c):
    angle=c['pedal_long_axis_deg'];rotation=App.Rotation(Y,-angle)
    eye=rotation.inverted().multVec(V(*c['pedal_output_relative_main_mm']))
    low=eye.x-c['pedal_output_eye_radius_mm'];tip=low+c['pedal_overall_mm']
    half=c['pedal_halfdepth_mm'];flange=c['pedal_flange_stock_mm'];width=c['pedal_flange_width_mm'];web=c['pedal_web_stock_mm']
    q=axle(c['pedal_hub_radius_mm'],c['pedal_hub_width_mm'])
    length=tip-50
    q=q.fuse(Part.makeBox(length,web,2*half,V(0,-web/2,-half)))
    for z in [-half,half-flange]:q=q.fuse(Part.makeBox(length,width,flange,V(0,-width/2,z)))
    # Full rounded rectangular pad; its stated dimensions are not a crop envelope.
    L,W,t,r=c['pad_length_mm'],c['pad_width_mm'],c['pad_stock_mm'],c['pad_corner_radius_mm'];start=tip-L
    pad=Part.makeBox(L-2*r,W,t,V(start+r,-W/2,half)).fuse(Part.makeBox(L,W-2*r,t,V(start,-W/2+r,half)))
    for x in [start+r,tip-r]:
        for y in [-W/2+r,W/2-r]:pad=pad.fuse(Part.makeCylinder(r,t,V(x,y,half),Z))
    q=q.fuse(pad)
    throat,cheek=c['pedal_fork_throat_mm'],c['pedal_fork_cheek_mm']
    for sign in [-1,1]:
        lane=sign*(throat+cheek)/2
        arm=strut(V(),eye,14,cheek);arm.translate(Y*lane)
        q=q.fuse(arm).fuse(axle(c['pedal_output_eye_radius_mm'],cheek,eye+Y*lane))
    q=q.cut(axle(c['pedal_journal_radius_mm'],200)).cut(axle(c['front_pin_bore_radius_mm'],100,eye))
    q=q.cut(Part.makeCylinder(1.5,40,V(),Z))
    q=finish(q);q=q.transformGeometry(rotation.toMatrix())
    return finish(q),dict(long_axis_world=list(rotation.multVec(X)),overall_axis_extrema_mm=[low,tip],pad_axis_limits_mm=[start,tip],fork_head_seat_y_mm=throat/2+cheek)
def bridle(c,rear):
    front=V(*c['pedal_output_relative_main_mm']);t=c['bridle_stock_mm'];wide=c['bridle_front_halfwidth_mm'];lane=c['bridle_rear_lane_mm']
    cross=front-X*30
    q=Part.makeBox(t,2*wide,t,cross-V(t/2,wide,t/2))
    q=q.fuse(strut(front,cross,12,t)).fuse(axle(18,t,front))
    guides={}
    for sign in [-1,1]:
        end=V(rear.x,sign*lane,rear.z);tail=end+V(35,0,-10)
        points=[cross+Y*sign*wide,V(-190,sign*wide,-160),V(-280,sign*68,-225),tail]
        wires=[rectangle(p.x,p.y,p.z,t,t) for p in points]
        arm=Part.makeLoft(wires,True,False)
        flat=strut(tail,end,t/2,t);flat.translate(Y*sign*lane)
        q=q.fuse(arm).fuse(flat).fuse(axle(c['bridle_rear_eye_radius_mm'],t,end))
        curve=Part.BSplineCurve();curve.interpolate(points+[end]);guides['Port' if sign>0 else 'Starboard']=curve.toShape()
    q=q.cut(axle(c['front_pin_bore_radius_mm'],300,front)).cut(axle(c['bridle_bolt_bore_radius_mm'],300,rear))
    return finish(q),guides,dict(front_center=list(front),rear_center=list(rear),rear_outside_y_mm=lane+t/2,spacer_halfspan_mm=lane-t/2)
def suspension(c):
    end=V(*c['bridle_rear_relative_swing_mm']);width=c['sleeve_length_mm'];t=c['suspension_stock_mm']
    q=axle(c['suspension_hub_radius_mm'],width).fuse(strut(V(),end,15,t)).fuse(axle(c['suspension_lower_radius_mm'],t,end))
    q=q.cut(axle(c['suspension_bore_radius_mm'],150)).cut(axle(c['suspension_bore_radius_mm'],150,end))
    q=q.cut(Part.makeCylinder(1.5,40,V(),X))
    sleeve=axle(c['sleeve_outer_radius_mm'],width).cut(axle(c['sleeve_bore_radius_mm'],width+2))
    sleeve=sleeve.cut(Part.makeCylinder(1.5,30,V(),X))
    return finish(q),finish(sleeve)
def spacer(c):
    length=2*c['bridle_rear_lane_mm']-c['bridle_stock_mm']
    return finish(axle(c['spacer_outer_radius_mm'],length).cut(axle(c['spacer_bore_radius_mm'],length+2)))
