"""Estimated paired driver side plates, with real sloping-floor mounting faces.

Source identities/counts live in the work packet. These are a support-interface
reconstruction, not a claimed tracing of the complete seat-support plate shape.
"""
import FreeCAD as App
import Part
from transmission_input_installation_parts import formed_pin
from transmission_brake_stop_parts import hexagon
V=App.Vector; X=V(1,0,0); Y=V(0,1,0); Z=V(0,0,1)


def shaft(length, radius, end_radius, shoulder, keeper_station):
    q=Part.makeCylinder(radius,2*shoulder,-Y*shoulder,Y)
    for sign in [-1,1]:
        q=q.fuse(Part.makeCylinder(end_radius,length/2-shoulder,Y*(sign*shoulder),Y*sign))
        q=q.cut(Part.makeCylinder(2.5,2*end_radius+2,V(-end_radius-1,sign*keeper_station,0),X))
    return q.removeSplitter()


def plate(c, sign, separation, rear_height, main_height, normal, slope):
    """Canonical origin: rear shaft X, vehicle center Y, floor top Z there."""
    t=c['plate_stock']; outer=c['nut_seat_y']; inner=outer-t
    a,b=-70.,separation-25.
    ys=[sign*inner,sign*(outer+55)]
    points=[V(x,y,slope*x) for x,y in [(a,ys[0]),(b,ys[0]),(b,ys[1]),(a,ys[1])]]
    foot=Part.Face(Part.makePolygon(points+[points[0]])).extrude(normal*t)
    # A small internal overlap joins the bent foot and the vertical web. The
    # external underside is the original floor plane, without floating pads.
    profile=[(a,slope*a+t/normal.z-.3),(b,slope*b+t/normal.z-.3),
             (separation+20,main_height-15),(separation,main_height),
             (0,rear_height),(-35,rear_height-15),(a,rear_height-40)]
    points=[V(x,sign*inner,z) for x,z in profile]
    web=Part.Face(Part.makePolygon(points+[points[0]])).extrude(Y*(sign*t))
    q=foot.fuse(web)
    for x,z,r in [(0,rear_height,24),(separation,main_height,31)]:
        q=q.fuse(Part.makeCylinder(r,t,V(x,sign*inner,z),Y*sign))
    # Drill after all unions, including the bosses.
    for x,z,r in [(0,rear_height,12.15),(separation,main_height,14.15)]:
        q=q.cut(Part.makeCylinder(r,t+2,V(x,sign*(inner-1),z),Y*sign))
    for x in [-40.,-10.,separation-80.,separation-50.]:
        p=V(x,sign*(outer+27.5),slope*x)
        q=q.cut(Part.makeCylinder(6.5,t+2,p-normal,normal))
    return q.removeSplitter()


def parts(c, separation, rear_height, main_height, normal, slope):
    shoulder=c['nut_seat_y']-c['plate_stock']
    shapes={
        'Def_DriverMainShaft_MountStudy':shaft(628.65,19.0119,14,shoulder,c['nut_seat_y']+16.5),
        'Def_DriverSwingShaft_MountStudy':shaft(c['swing_length'],12.7,12,shoulder,c['nut_seat_y']+10),
    }
    keeper_data={}
    for kind,pc in [('Main',c['main_keeper']),('Swing',c['swing_keeper'])]:
        shapes['Def_Driver'+kind+'Keeper_MountStudy'],keeper_data[kind]=formed_pin(pc)
    for side,sign in [('Port',1),('Starboard',-1)]:
        shapes['Def_Driver'+side+'SupportPlate_MountStudy']=plate(c,sign,separation,rear_height,main_height,normal,slope)
    head=hexagon(19.05,8);head.translate(-Z*8)
    shapes['Def_DriverSupportBolt_MountStudy']=Part.makeCylinder(6.35,31.75).fuse(head).removeSplitter()
    return shapes,keeper_data
