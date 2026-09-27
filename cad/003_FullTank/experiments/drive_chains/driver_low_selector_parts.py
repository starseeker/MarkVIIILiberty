"""Low selector jaws and diagonal connecting link; source topology, estimated sections."""
import FreeCAD as App
import Part
from driver_control_linkage_parts_v3 import strut
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
def axle(radius,width,point):return Part.makeCylinder(radius,width,point-Y*width/2,Y)
def prism(d,n,radial0,radial1,halfwidth,y0,y1):
    pts=[d*radial0-n*halfwidth+Y*y0,d*radial1-n*halfwidth+Y*y0,d*radial1+n*halfwidth+Y*y0,d*radial0+n*halfwidth+Y*y0]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(Y*(y1-y0))
def selector(c,side):
    d=V(*c['selector_gate_direction']);n=V(-d.z,0,d.x);t=c['selector_web_stock'];eye=V(*c['front_relative_to_main']);width=c['selector_journal_width'];s=1 if side=='Port' else -1
    q=axle(c['selector_hub_radius'],width,V())
    q=q.fuse(strut(V(),d*c['selector_gate_upper_radius'],c['selector_gate_halfwidth'],t))
    q=q.fuse(strut(V(),eye,16,12.7)).fuse(axle(23,12.7,eye))
    # Full C jaw: a radial spine with two inward axial lips. The opening is
    # physical empty space for the later operating lever, not a painted slot.
    low,high=c['selector_gate_lower_radius'],c['selector_gate_upper_radius'];lip=c['selector_gate_lip_stock'];inside=-s*c['selector_gate_inward_depth'];outside=s*t/2
    y0,y1=sorted([inside,outside])
    for a,b in [(low,low+lip),(high-lip,high)]:q=q.fuse(prism(d,n,a,b,c['selector_gate_halfwidth'],y0,y1))
    q=q.cut(axle(c['selector_journal_radius'],200,V())).cut(axle(c['pin_radius']+.1,200,eye))
    q=q.cut(Part.makeCylinder(1.5,34,V(),-X))
    return q.removeSplitter()
def connecting(c,rear,front):
    # Same source part and same plane at both installations. Eye positions are
    # expressed in the retained M783-based definition frame.
    t=c['connecting_stock'];q=strut(rear,front,c['connecting_halfwidth'],t);q.translate(Y*rear.y)
    for point in [rear,front]:q=q.fuse(axle(c['connecting_eye_radius'],t,point))
    for point in [rear,front]:q=q.cut(axle(c['pin_radius']+.1,200,point))
    return q.removeSplitter()
def joint_pin(c):
    seat=c['pin_head_seat_y'];q=Part.makeCylinder(c['pin_radius'],c['pin_length'],V(0,seat,0),-Y)
    q=q.fuse(Part.makeCylinder(14,4.5,V(0,seat,0),Y))
    q=q.cut(Part.makeCylinder(2.5,21.05,V(-10.525,c['pin_keeper_y'],0),X))
    return q.removeSplitter()
