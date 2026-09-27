"""Source-identified low-speed links with explicitly estimated sections and joint stack."""
import FreeCAD as App
import Part
from driver_control_linkage_parts_v3 import strut
from transmission_input_installation_parts import formed_pin
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
def axle(radius,width,point):return Part.makeCylinder(radius,width,point-Y*width/2,Y)
def offset_web(a,b,halfwidth,stock):
    # Ruled rectangular forging between parallel transverse sections; lateral
    # set is explicit, keeping the lower rod eye on its catalogue plan lane.
    axis=V(b.x-a.x,0,b.z-a.z);axis.normalize();cross=V(-axis.z,0,axis.x)*halfwidth;wires=[]
    for p in [a,b]:
        pts=[p+cross-Y*stock/2,p-cross-Y*stock/2,p-cross+Y*stock/2,p+cross+Y*stock/2]
        wires.append(Part.makePolygon(pts+[pts[0]]))
    return Part.makeLoft(wires,True,True)
def parts(c,separation):
    p=V(*c['low_knee_relative']);r=V(*c['low_rod_relative']);t=c['low_web_stock'];knee_r=c['low_pin_radius'];bore=knee_r+.1
    suspension=axle(24,32,V()).fuse(strut(V(),p,13,t)).fuse(axle(26,16,p))
    suspension=suspension.cut(axle(12.85,34,V())).cut(axle(bore,18,p)).cut(Part.makeCylinder(1.5,26,V(),Z)).removeSplitter()
    upper=p+Y*c['brake_boss_y'];brake=axle(26,12.7,upper).fuse(offset_web(upper,r,12,12.7)).fuse(axle(16,12.7,r))
    brake=brake.cut(axle(bore,14.7,upper)).cut(axle(6.5,14.7,r)).removeSplitter()
    rear=p+Y*c['connecting_y'];front=V(separation-10,c['connecting_y'],-150);mid=V((front.x+rear.x)/2,c['connecting_y'],-265)
    arc=Part.Arc(rear,mid,front).toShape();center=arc.Curve.Center;radius=arc.Curve.Radius
    def expanded(point,amount):return center+(point-center)*((radius+amount)/radius)
    half=14.;a,m,b=[expanded(v,half) for v in [rear,mid,front]];aa,mm,bb=[expanded(v,-half) for v in [rear,mid,front]]
    outline=Part.Wire([Part.Arc(a,m,b).toShape(),Part.makeLine(b,bb),Part.Arc(bb,mm,aa).toShape(),Part.makeLine(aa,a)])
    connecting=Part.Face(outline);connecting.translate(-Y*5);connecting=connecting.extrude(Y*10).fuse(axle(25,10,rear)).fuse(axle(16,10,front))
    connecting=connecting.cut(axle(bore,12,rear)).cut(axle(6.5,12,front)).removeSplitter()
    seat=c['pin_head_seat_y'];length=c['low_pin_length'];station=c['pin_keeper_y']
    pin=Part.makeCylinder(knee_r,length,V(0,seat,0),Y).fuse(Part.makeCylinder(14,5,V(0,seat-5,0),Y))
    pin=pin.cut(Part.makeCylinder(2.5,2*knee_r+2,V(-knee_r-1,station,0),X)).removeSplitter()
    washer=Part.makeCylinder(15,3.175,V(),Y).cut(Part.makeCylinder(bore,5.175,V(0,-1,0),Y)).removeSplitter()
    keeper,kd=formed_pin(c['low_keeper'])
    return dict(Def_DriverLowSuspension_M760=suspension,Def_DriverLowConnecting_M762=connecting,Def_DriverLowBrake_M763=brake,Def_DriverLowSuspensionPin_M761=pin,Def_DriverLowLinkWasher_SH220A=washer,Def_DriverLowSuspensionKeeper=keeper),dict(knee=list(p),rod=list(r),connecting_front=list(front),connecting_rear=list(rear),brake_upper=list(upper),keeper=kd,connecting_arc_radius_mm=radius)
