"""M769 source-profile hypothesis: two-eye head, bowed web and nominal rod socket."""
import FreeCAD as App
import Part
V=App.Vector;Y=V(0,1,0)

def make(c):
    center=complex(*c['front_eyes_px'][0]);scale=complex(*c['side_complex_scale'])
    def point(p,y=0):
        q=-(complex(*p)-center)/scale
        return V(q.real,y,q.imag)
    stock=c['web_stock_mm'];curves={}
    for name,points in [('Upper',c['web_upper_px']),('Lower',c['web_lower_px'])]:
        curve=Part.BSplineCurve();curve.interpolate([point(p,-stock/2) for p in points]);curves[name]=curve.toShape()
    upper,lower=curves['Upper'],curves['Lower']
    wire=Part.Wire([upper,Part.makeLine(upper.Vertexes[-1].Point,lower.Vertexes[-1].Point),lower.reversed(),Part.makeLine(lower.Vertexes[0].Point,upper.Vertexes[0].Point)])
    web=Part.Face(wire).extrude(Y*stock)
    vertices=[point(p,-stock/2) for p in c['head_outline_px']]
    head=Part.Face(Part.makePolygon(vertices+vertices[:1])).extrude(Y*stock)
    q=web.fuse(head)
    eyes=[point(p) for p in c['front_eyes_px']]
    for eye in eyes:q=q.fuse(Part.makeCylinder(c['eye_outer_radius_mm'],stock,eye-Y*stock/2,Y))
    # Direction and position are inferred from the local figure, not printed.
    axis=point(c['socket_rear_px'])-point(c['socket_front_px']);axis.normalize()
    rear=point(c['socket_rear_px']);front=rear-axis*c['socket_length_mm']
    socket=Part.makeCylinder(c['socket_outer_radius_mm'],c['socket_length_mm'],front,axis)
    q=q.fuse(socket)
    for eye in eyes:q=q.cut(Part.makeCylinder(c['pin_bore_radius_mm'],stock+2,eye-Y*(stock/2+1),Y))
    q=q.cut(Part.makeCylinder(c['socket_bore_radius_mm'],c['socket_depth_mm']+1,rear+axis,-axis))
    clean=q.copy().removeSplitter()
    if clean.isValid() and len(clean.Solids)==1 and clean.getTolerance(1)<=q.getTolerance(1)+1e-10:q=clean
    assert q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4
    return q,curves,dict(front_eyes_mm=[list(v) for v in eyes],socket_rear_mm=list(rear),socket_front_mm=list(front),socket_axis=list(axis),
        web_stock_mm=stock,curve_records={k:dict(degree=e.Curve.Degree,knots=e.Curve.getKnots(),multiplicities=e.Curve.getMultiplicities(),poles=[list(v) for v in e.Curve.getPoles()]) for k,e in curves.items()})
