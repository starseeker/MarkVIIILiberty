"""Native sketched lower support webs, flanges and plain attachment bolts."""
import math
import FreeCAD as App
import Part
import Sketcher
from .track_parts import feature


def path_curves(points,ends,offset,half):
    v=lambda p:App.Vector(*p,0)
    result=[];start=(ends[0],points[0][1]+offset)
    def line(a,b):
        if math.dist(a,b)>1e-7:result.append(Part.LineSegment(v(a),v(b)))
    for index,(x,z) in enumerate(points):
        left=(x-half,z+offset);right=(x+half,z+offset)
        if index and abs(start[1]-left[1])>1e-8:
            d=(left[0]-start[0])/3;curve=Part.BSplineCurve()
            curve.buildFromPolesMultsKnots([v(p) for p in [start,(start[0]+d,start[1]),(left[0]-d,left[1]),left]],
                                          [4,4],[0.,1.],False,3)
            result.append(curve)
        else:line(start,left)
        line(left,right);start=right
    line(start,(ends[1],points[-1][1]+offset))
    return result


def band(a,low,high):
    points=a['points'];ends=a['ends'];half=a['lower_support_seat_half_length']
    lower=[c.toShape() for c in path_curves(points,ends,low,half)]
    upper=[c.toShape() for c in path_curves(points,ends,high,half)]
    edges=lower+[Part.makeLine(App.Vector(ends[1],points[-1][1]+low,0),App.Vector(ends[1],points[-1][1]+high,0))]
    edges += [e.reversed() for e in reversed(upper)]
    edges.append(Part.makeLine(App.Vector(ends[0],points[0][1]+high,0),App.Vector(ends[0],points[0][1]+low,0)))
    return Part.Wire(edges)


def build(doc,name,a):
    body=doc.addObject('PartDesign::Body',name)
    if a['role']=='bolt':
        r=a['lower_support_bolt_af']/math.sqrt(3)
        pts=[App.Vector(r*math.cos(i*math.pi/3),0,r*math.sin(i*math.pi/3)) for i in range(6)]
        shape=Part.Face(Part.makePolygon(pts+pts[:1])).extrude(App.Vector(0,a['lower_support_bolt_head_height'],0))
        shape=shape.fuse(Part.makeCylinder(a['lower_support_bolt_diameter']/2,a['lower_support_bolt_length'],App.Vector(),App.Vector(0,-1,0)))
        feature(body,'PlainHeadAndThreadEnvelope',shape.removeSplitter());return body
    from .cad_build import pad
    t=a['lower_support_thickness'];width=a['lower_support_width'];end=a['end_sign']
    toe=a['roller_pin_flat_height'];top=a['roller_clamp_seat']
    sketch=body.newObject('Sketcher::SketchObject','WebContour')
    transform=App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),90));sketch.Placement=transform
    for edge in band(a,toe,top).Edges:
        curve=edge.Curve
        if isinstance(curve,Part.Line):curve=Part.LineSegment(edge.Vertexes[0].Point,edge.Vertexes[-1].Point)
        index=sketch.addGeometry(curve,False);sketch.addConstraint(Sketcher.Constraint('Block',index))
    extrusion=pad(body,sketch,t);extrusion.Reversed=end==1;doc.recompute()
    flange=Part.Face(band(a,top-t,top));flange.Placement=transform
    shape=extrusion.Shape.fuse(flange.extrude(App.Vector(0,end*width,0))).removeSplitter()
    leg=a['roller_pin_diameter']/2+a['roller_ubolt_clearance']+a['roller_ubolt_diameter']/2
    clamp=a['hull_side_thickness']-a['hull_skirt_thickness']+a['roller_ubolt_diameter']/2+a['roller_clamp_gap']
    for x,z in a['points']:
        for direction in [-1,1]:shape=shape.cut(Part.makeCylinder(a['roller_fastener_bore']/2,top+2,
            App.Vector(x+direction*leg,end*clamp,z-1)))
    for x,z in a['bolts']:shape=shape.cut(Part.makeCylinder(a['lower_support_bolt_bore']/2,width+2,
        App.Vector(x,-end,z),App.Vector(0,end,0)))
    feature(body,'FlangeAndOwnedHoles',shape.removeSplitter())
    return body


def hull_tools(holes):
    result=[]
    for h in holes:
        axis=App.Vector(*h['direction']);p=App.Vector(*h['position'])
        result.append(Part.makeCylinder(h['radius'],h['length']+2,p-axis,axis))
    return result
