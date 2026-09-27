"""High-selector bearing, short jaw and stock-constrained lower receiving eye."""
import FreeCAD as App
import Part
from driver_control_linkage_parts_v3 import strut
from driver_low_selector_parts import axle,prism
V=App.Vector;X=V(1,0,0);Y=V(0,1,0)
def selector(c,side):
    d=V(*c['selector_gate_direction']);n=V(-d.z,0,d.x);t=c['selector_web_stock'];eye=V(*c['bell_relative_to_main']);width=c['selector_journal_width'];sign=1 if side=='Port' else -1
    q=axle(c['selector_hub_radius'],width,V()).fuse(strut(V(),d*c['selector_gate_upper_radius'],c['selector_gate_halfwidth'],t))
    q=q.fuse(strut(V(),eye,15,12.7)).fuse(axle(17,12.7,eye))
    low,high=c['selector_gate_lower_radius'],c['selector_gate_upper_radius'];lip=c['selector_gate_lip_stock'];inside=sign*c['selector_gate_outward_depth'];outside=-sign*t/2;y0,y1=sorted([inside,outside])
    for a,b in [(low,low+lip),(high-lip,high)]:q=q.fuse(prism(d,n,a,b,c['selector_gate_halfwidth'],y0,y1))
    q=q.cut(axle(c['selector_journal_radius'],200,V())).cut(axle(6.5,200,eye)).cut(Part.makeCylinder(1.5,34,V(),-X))
    return q.removeSplitter()
