"""Rounded bent armor blades and source-identified partial louver frame plates."""
import math
import FreeCAD as App
import Part
import Sketcher
from .upper_parts import prism


def blade_section(a):
    """Closed YZ section: two tangent legs, concentric 90-degree circular bends."""
    t, r, h = (a[k] for k in ['louver_blade_thickness','louver_bend_radius','louver_blade_width'])
    outer = r+t
    c = h/2-outer*math.sqrt(2)
    q = math.sqrt(2)
    p = [(0,h/2),(c+outer/q,outer/q),(c+outer/q,-outer/q),(0,-h/2),
         (-t/q,-h/2+t/q),(c+r/q,-r/q),(c+r/q,r/q),(-t/q,h/2-t/q)]
    v = lambda yz: App.Vector(*yz, 0)
    edges = []
    for i in range(len(p)):
        j=(i+1)%len(p)
        if i in {1,5}:
            radius = outer if i == 1 else r
            edges.append(Part.Arc(v(p[i]), v((c+radius,0)), v(p[j])))
        else:
            edges.append(Part.LineSegment(v(p[i]),v(p[j])))
    return edges


def stock(a):
    role=a['role']; L=a['length']; W=a['width']; t=a['louver_guard_thickness']
    def box(x0,x1,y0,y1,z0,z1):
        return [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],(0,0,z1-z0)
    if role=='guard':
        h=a['hand']; H=a['guard_height']; lip=a['louver_guard_lip']
        pts=[(W/2,0),(W/2+t,0),(W/2+t,H-t),(W/2+lip,H-t),(W/2+lip,H),(W/2,H)]
        return [(0,h*y,z) for y,z in pts],(L,0,0)
    if role=='port_frame':return box(0,L,W/2-t,W/2,0,90)
    if role in {'front_frame','rear_frame'}:
        x0,x1=(L-t,L) if role=='front_frame' else (0,t)
        # The independent low port plate owns the final t mm on the outlet.
        y1=W/2-t if a['bank']=='outlet' else W/2
        return box(x0,x1,-W/2,y1,0,90)
    if role=='cover':return box(16,L-16,W/2-20,W/2-6,92,98)
    if role in {'front_retainer','rear_retainer'}:
        x0,x1=(L-12,L-6) if role=='front_retainer' else (6,12)
        return box(x0,x1,-W/2+6,W/2-20,14,20)
    if role=='packing_plate':return box(0,40,0,14,0,6)
    if role=='packing_strip':return box(16,L-16,W/2-20,W/2-6,84,86)
    raise ValueError('Unknown louver component role '+role)


def build(doc,name,a):
    from .cad_build import sketch_polygon,pad
    body=doc.addObject('PartDesign::Body',name)
    if a['role']=='blade':
        section=body.newObject('Sketcher::SketchObject','BentArmorSection')
        # Local sketch x/y map to roof Y/Z, with extrusion along roof X.
        rotation=App.Rotation(App.Vector(0,1,0),App.Vector(0,0,1),App.Vector(1,0,0),'ZXY')
        section.Placement=App.Placement(App.Vector(16,0,20+a['louver_blade_width']/2),rotation)
        for curve in blade_section(a):
            i=section.addGeometry(curve,False)
            section.addConstraint(Sketcher.Constraint('Block',i))
        pad(body,section,a['length']-32)
    else:
        pts,vec=stock(a)
        direction=App.Vector(*vec)
        placement=App.Placement(App.Vector(*pts[0]),App.Rotation(App.Vector(0,0,1),direction))
        inverse=placement.inverse(); local=[inverse.multVec(App.Vector(*p)) for p in pts]
        if max(abs(p.z) for p in local)>1e-7:raise ValueError('Nonplanar louver stock')
        sketch=sketch_polygon(body,'PlateSection',[(p.x,p.y) for p in local],placement)
        pad(body,sketch,direction.Length)
    return body
