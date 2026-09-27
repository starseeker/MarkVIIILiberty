"""Estimated complete M784 swing link and source-length M772 clutch lever."""
import math
import FreeCAD as App
import Part
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)


def web(points,stock):
    vs=[V(x,-stock/2,z) for x,z in points]
    return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(Y*stock)


def strut(a,b,halfwidth,stock):
    direction=b-a;direction.normalize();normal=V(-direction.z,0,direction.x)*halfwidth
    points=[a+normal,b+normal,b-normal,a-normal]
    return web([(p.x,p.z) for p in points],stock)


def swing_link(c):
    t=c['swing_web_stock'];width=c['swing_journal_width'];a=V(*c['swing_front_eye']);b=V(*c['swing_rear_eye'])
    q=Part.makeCylinder(24,width,-Y*width/2,Y)
    q=q.fuse(strut(V(),b,13,t)).fuse(strut(a,b,12,t)).fuse(strut(V(),a,11,t))
    q=q.fuse(web([(0,0),(a.x,a.z),(b.x,b.z)],t))
    for point in [a,b]:q=q.fuse(Part.makeCylinder(c['swing_eye_radius'],t,point-Y*t/2,Y))
    q=q.cut(Part.makeCylinder(c['swing_bore_diameter']/2,width+2,-Y*(width/2+1),Y))
    for point in [a,b]:q=q.cut(Part.makeCylinder(6.5,t+2,point-Y*(t/2+1),Y))
    # A drilled oil passage is part of the casting; HB oil arrows do not justify
    # inventing a separate nipple. Its size/clocking are explicit estimates.
    q=q.cut(Part.makeCylinder(1.5,26,V(0,0,0),Z))
    return q.removeSplitter()


def clutch_lever(c):
    t=c['lever_stock'];width=c['lever_boss_width'];angle=math.radians(90-c['lever_included_angle_degrees'])
    bell=V(c['clutch_bell_radius']*math.cos(angle),0,c['clutch_bell_radius']*math.sin(angle))
    q=Part.makeCylinder(30,width,-Y*width/2,Y)
    q=q.fuse(web([(-17,0),(17,0),(12,650),(-12,650)],t))
    q=q.fuse(strut(V(),bell,15,t)).fuse(Part.makeCylinder(17,t,bell-Y*t/2,Y))
    # Integrally represented grip; unprinted section, but exact printed reach.
    tip=c['clutch_hand_length'];gripradius=10.5
    q=q.fuse(Part.makeCylinder(gripradius,tip-gripradius-620,V(0,0,620),Z)).fuse(Part.makeSphere(gripradius,V(0,0,tip-gripradius)))
    q=q.cut(Part.makeCylinder(c['lever_bore_diameter']/2,width+2,-Y*(width/2+1),Y))
    q=q.cut(Part.makeCylinder(6.5,t+2,bell-Y*(t/2+1),Y))
    q=q.cut(Part.makeCylinder(1.5,32,V(),-X))
    return q.removeSplitter(),bell
