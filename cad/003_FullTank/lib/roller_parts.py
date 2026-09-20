"""Revolved roller profiles, oil-drilled pins, split retainers and spring stacks."""
import math
import FreeCAD as App
import Part
import Sketcher
from .track_parts import cylinder_y,feature
from .roller_geometry import ring_dimensions,ring_station


def revolution(doc,name,curves,angle=360,rotation=0):
    body=doc.addObject('PartDesign::Body',name)
    sketch=body.newObject('Sketcher::SketchObject','RadialSection')
    sketch.Placement=App.Placement(App.Vector(),App.Rotation(App.Vector(0,1,0),rotation))
    for curve in curves:
        i=sketch.addGeometry(curve,False);sketch.addConstraint(Sketcher.Constraint('Block',i))
    rev=body.newObject('PartDesign::Revolution','TurnedProfile')
    rev.Profile=sketch;rev.ReferenceAxis=(sketch,['V_Axis']);rev.Angle=angle
    doc.recompute();sketch.Visibility=False
    if rev.Shape.isNull() or not rev.Shape.isValid():raise ValueError('Invalid roller revolution '+name)
    return body


def lines(points):
    return [Part.LineSegment(App.Vector(*p,0),App.Vector(*q,0)) for p,q in zip(points,points[1:]+points[:1])]


def roller_profile(a,upper=False):
    R=a['roller_diameter']/2;w=a['roller_width']/2;inner=a['tube_od']/2+a['roller_bore_clearance']
    rim=a['roller_flange_width'];waist=a['roller_waist_radius'];corner=3
    v=lambda p:App.Vector(*p,0)
    result=[]
    def line(p,q):result.append(Part.LineSegment(v(p),v(q)))
    def arc(p,m,q):result.append(Part.Arc(v(p),v(m),v(q)))
    def blend(p,q):
        curve=Part.BSplineCurve()
        curve.buildFromPolesMultsKnots([v(p),v((p[0],p[1]+(q[1]-p[1])/3)),
                                       v((q[0],p[1]+2*(q[1]-p[1])/3)),v(q)],[4,4],[0,1],False,3)
        result.append(curve)
    line((inner,-w),(R-corner,-w))
    arc((R-corner,-w),(R-corner+corner/math.sqrt(2),-w+corner-corner/math.sqrt(2)),(R,-w+corner))
    line((R,-w+corner),(R,-w+rim))
    if upper:
        blend((R,-w+rim),(a['roller_upper_hub_radius'],w-corner))
        line((a['roller_upper_hub_radius'],w-corner),(a['roller_upper_hub_radius'],w))
        line((a['roller_upper_hub_radius'],w),(inner,w))
    else:
        blend((R,-w+rim),(waist,-12))
        line((waist,-12),(waist,12))
        blend((waist,12),(R,w-rim))
        line((R,w-rim),(R,w-corner))
        arc((R,w-corner),(R-corner+corner/math.sqrt(2),w-corner+corner/math.sqrt(2)),(R-corner,w))
        line((R-corner,w),(inner,w))
    line((inner,w),(inner,-w))
    return result


def build(doc,name,a):
    role=a['role']
    if role=='upper_support':
        from .cad_build import pad
        body=doc.addObject('PartDesign::Body',name)
        sketch=body.newObject('Sketcher::SketchObject','AngleSection')
        # Local +Y points away from the shell; a yaw of 180 degrees installs
        # the same symmetric M2092 at the opposite end of the pin.
        L=a['roller_support_length'];t=a['roller_support_thickness']
        w=a['roller_support_width'];top=a['roller_clamp_seat']
        toe=a['roller_pin_flat_height'];r=a['roller_support_root_radius']
        sketch.Placement=App.Placement(App.Vector(-L/2,0,0),App.Rotation(App.Vector(0,1,0),90))
        v=lambda y,z:App.Vector(-z,y,0)
        points=[(0,toe),(t,toe),(t,top-t-r)]
        curves=[Part.LineSegment(v(*p),v(*q)) for p,q in zip(points,points[1:])]
        curves.append(Part.Arc(v(t,top-t-r),v(t+r-r/math.sqrt(2),top-t-r+r/math.sqrt(2)),v(t+r,top-t)))
        points=[(t+r,top-t),(w,top-t),(w,top),(0,top),(0,toe)]
        curves += [Part.LineSegment(v(*p),v(*q)) for p,q in zip(points,points[1:])]
        for curve in curves:
            i=sketch.addGeometry(curve,False);sketch.addConstraint(Sketcher.Constraint('Block',i))
        shape=pad(body,sketch,L).Shape
        dx=a['roller_pin_diameter']/2+a['roller_ubolt_clearance']+a['roller_ubolt_diameter']/2
        y=a['roller_ubolt_diameter']/2+a['roller_clamp_gap']
        for sign in [-1,1]:
            shape=shape.cut(Part.makeCylinder(a['roller_fastener_bore']/2,top+2,App.Vector(sign*dx,y,-1)))
            shape=shape.cut(Part.makeCylinder(a['roller_support_mount_bore']/2,w+2,
                App.Vector(sign*a['roller_support_mount_pitch']/2,-1,(toe+top-t)/2),App.Vector(0,1,0)))
        feature(body,'StapleAndAttachmentHoles',shape.removeSplitter())
        return body
    if role in {'lower','upper'}:return revolution(doc,name,roller_profile(a,role=='upper'))
    if role=='tube':
        L=a['tube_length']/2;ro=a['tube_od']/2;ri=a['tube_id']/2
        body=revolution(doc,name,lines([(ri,-L),(ro,-L),(ro,L),(ri,L)]))
        shape=body.Shape;ring_i,_,width,_=ring_dimensions(a)
        for sign in [-1,1]:
            y=sign*ring_station(a)
            groove=cylinder_y(ro+1,width+2*a['roller_axial_gap'],y=y).cut(cylinder_y(ring_i-a['roller_ring_seat_clearance'],width+4,y=y))
            shape=shape.cut(groove)
        feature(body,'RetainerGrooves',shape.removeSplitter());return body
    if role=='bush':
        L=a['roller_bush_length']/2;ro=(a['tube_id']-a['roller_bush_fit'])/2;ri=(a['roller_pin_diameter']+a['roller_bush_fit'])/2
        c=1
        return revolution(doc,name,lines([(ri+c,-L),(ro-c,-L),(ro,-L+c),(ro,L-c),(ro-c,L),(ri+c,L),(ri,L-c),(ri,-L+c)]))
    if role=='ring':
        ri,ro,w,angle=ring_dimensions(a)
        return revolution(doc,name,lines([(ri,-w/2),(ro,-w/2),(ro,w/2),(ri,w/2)]),angle,-90+(360-angle)/2)
    if role=='spring_plate':
        ri=a['tube_od']/2+a['roller_bore_clearance'];y=a['roller_spring_length']/2;t=a['roller_spring_plate_thickness']
        hub=a['roller_center_offset']-a['roller_width']/2-a['roller_axial_gap']-t
        # SNL29 has the outer flange toward the spring and the hub toward
        # the roller. This also leaves the projecting track-pin heads clear.
        return revolution(doc,name,lines([(ri,hub+t),(54,hub+t),(65,y+t),(a['roller_spring_plate_radius'],y+t),
                                          (a['roller_spring_plate_radius'],y),(62,y),(51,hub),(ri,hub)]))
    body=doc.addObject('PartDesign::Body',name)
    if role=='pin':
        R=a['roller_pin_diameter']/2;L=a['roller_pin_length']
        shape=cylinder_y(R,L)
        # One SNL-listed plug supplies the provisional blind longitudinal gallery.
        bore=Part.makeCylinder(a['roller_oil_bore']/2,L-20,App.Vector(0,-L/2,0),App.Vector(0,1,0))
        shape=shape.cut(bore)
        for sign in [-1,1]:
            shape=shape.cut(Part.makeCylinder(2,2*R+2,App.Vector(0,sign*(a['tube_length']/2-a['roller_bush_length']/2),-R-1)))
            # HB141 and the HB88/89 / SNL29 sections show the pin suspended
            # beneath the angle toe. The former bottom flats were reversed.
            reach=a['roller_pin_flat_length'];z=a['roller_pin_flat_height']
            shape=shape.cut(Part.makeBox(2*R+2,reach,R-z+1,
                App.Vector(-R-1,sign*L/2-(reach if sign==1 else 0),z)))
        feature(body,'OilGalleryAndEndFlats',shape.removeSplitter())
    elif role=='spring':
        from scipy.optimize import brentq
        radius=(a['roller_spring_inside']+a['roller_spring_wire'])/2
        wire=a['roller_spring_wire']/2;length=a['roller_spring_length'];turns=a['roller_spring_turns']
        rise=brentq(lambda h:h+2*wire/math.sqrt(1+(h/(turns*2*math.pi*radius))**2)-length,length-2*wire,length)
        helix=Part.makeHelix(rise/turns,rise,radius)
        tangent=helix.Edges[0].tangentAt(helix.Edges[0].FirstParameter)
        section=Part.Wire([Part.makeCircle(wire,App.Vector(radius,0,0),tangent)])
        shape=Part.Wire(helix.Edges).makePipeShell([section],True,True)
        shape.translate(App.Vector(0,0,-rise/2));shape.rotate(App.Vector(),App.Vector(1,0,0),-90)
        feature(body,'ThreeCoilLoadedSpring',shape)
    elif role=='ubolt':
        rr=a['roller_pin_diameter']/2+a['roller_ubolt_clearance']+a['roller_ubolt_diameter']/2
        ztop=a['roller_ubolt_top'];wire=a['roller_ubolt_diameter']/2
        path=Part.Wire([Part.makeLine(App.Vector(-rr,0,ztop),App.Vector(-rr,0,0)),
                        Part.Arc(App.Vector(-rr,0,0),App.Vector(0,0,-rr),App.Vector(rr,0,0)).toShape(),
                        Part.makeLine(App.Vector(rr,0,0),App.Vector(rr,0,ztop))])
        section=Part.Wire([Part.makeCircle(wire,App.Vector(-rr,0,ztop),App.Vector(0,0,1))])
        feature(body,'BentStaple',path.makePipeShell([section],True,False))
    elif role=='nut':
        r=a['roller_nut_af']/math.sqrt(3);height=a['roller_nut_height']
        pts=[App.Vector(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3),0) for i in range(6)]
        shape=Part.Face(Part.makePolygon(pts+pts[:1])).extrude(App.Vector(0,0,height))
        feature(body,'PlainHexNut',shape.cut(Part.makeCylinder(a['roller_fastener_bore']/2,height+2,App.Vector(0,0,-1))))
    elif role=='washer':
        height=a['roller_washer_thickness'];ro=a['roller_washer_od']/2;ri=a['roller_fastener_bore']/2
        shape=Part.makeCylinder(ro,height).cut(Part.makeCylinder(ri,height))
        shape=shape.cut(Part.makeBox(ro+1,1,height+2,App.Vector(0,-.5,-1)))
        feature(body,'SplitLockWasher',shape)
    elif role=='plug':
        # Q52C nominal pipe size is retained; unthreaded envelope is approximate.
        shape=Part.makeCylinder(a['roller_oil_bore']/2-.2,12,App.Vector(),App.Vector(0,1,0))
        shape=shape.fuse(Part.makeBox(12.7,5,12.7,App.Vector(-6.35,-5,-6.35)))
        feature(body,'SquareHeadPipePlug',shape.removeSplitter())
    else:raise ValueError('Unknown roller component '+role)
    return body
