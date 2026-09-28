"""Analytic quadrant and complete source-sized mounting hardware; unprinted form inferred."""
import math
from control_rebuild_io_v2 import App,Part
from driver_seat_support_parts import bolt
from engine_suspension_parts import hexagon
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
def radial(radius,deg):
    a=math.radians(deg);return V(radius*math.cos(a),0,radius*math.sin(a))
def disk(radius,p,t):return Part.makeCylinder(radius,t,p-Y*t/2,Y)
def strip(a,b,half,t):
    axis=b-a;axis.normalize();n=V(-axis.z,0,axis.x)*half;p=[a+n,b+n,b-n,a-n]
    return Part.Face(Part.makePolygon([v-Y*t/2 for v in p+[p[0]]])).extrude(Y*t)
def quadrant(c,holes):
    ri,ro=c['inner_radius_mm'],c['outer_radius_mm'];a,b=c['arc_angles_degrees'];mid=(a+b)/2;t=c['quadrant_stock_mm']
    edges=[Part.Arc(radial(ro,a),radial(ro,mid),radial(ro,b)).toShape(),Part.makeLine(radial(ro,b),radial(ri,b)),Part.Arc(radial(ri,b),radial(ri,mid),radial(ri,a)).toShape(),Part.makeLine(radial(ri,a),radial(ro,a))]
    q=Part.Face(Part.Wire(edges)).extrude(Y*t);q.translate(-Y*t/2)
    for deg,point in zip([a,b],holes):
        end=radial((ri+ro)/2,deg);q=q.fuse(disk((ro-ri)/2,end,t)).fuse(strip(end,point,c['ear_radius_mm'],t)).fuse(disk(c['ear_radius_mm'],point,t))
        q=q.cut(Part.makeCylinder(c['bolt_bore_radius_mm'],t+2,point-Y*(t/2+1),Y))
    for deg in c['notch_angles_degrees']:
        # Radial open slot, with an explicit flat bottom and full-thickness opening.
        direction=radial(1,deg);normal=V(-direction.z,0,direction.x);bottom=direction*(ro-c['notch_depth_mm'])
        points=[bottom-normal*c['notch_width_mm']/2,bottom+normal*c['notch_width_mm']/2,bottom+direction*30+normal*c['notch_width_mm']/2,bottom+direction*30-normal*c['notch_width_mm']/2]
        cutter=Part.Face(Part.makePolygon([p-Y*(t/2+1) for p in points+[points[0]]])).extrude(Y*(t+2));q=q.cut(cutter)
    return q.removeSplitter()
def hardware(c,spacer_length):
    b=bolt(9.525,57.15,c['hardware_af_mm'],c['head_height_mm'])
    n=hexagon(c['hardware_af_mm'],0,c['nut_stock_mm']).cut(Part.makeCylinder(4.9,c['nut_stock_mm']+2,-Z)).removeSplitter()
    lock=Part.makeCylinder(c['lock_outer_radius_mm'],c['lock_stock_mm']).cut(Part.makeCylinder(5.,c['lock_stock_mm']+2,-Z))
    lock=lock.cut(Part.makeBox(20,1.2,c['lock_stock_mm']+2,V(0,-.6,-1))).removeSplitter()
    spacer=Part.makeCylinder(c['spacer_outer_radius_mm'],spacer_length).cut(Part.makeCylinder(c['bolt_bore_radius_mm'],spacer_length+2,-Z)).removeSplitter()
    return dict(Bolt=b,Nut=n,Lock=lock,Distance=spacer)
