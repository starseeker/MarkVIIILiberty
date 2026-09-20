"""Separate revolved rims, perforated disks, formed diaphragms and upset rivets."""
import math
import FreeCAD as App
import Part
import Sketcher
from .roller_parts import revolution,lines
from .track_parts import cylinder_y,feature
from .wheel_geometry import joint_points,rotate_point


def hole(shape,x,z,r,y,length):
    return shape.cut(cylinder_y(r,length,x=x,y=y,z=z))


def build(doc,name,a):
    role=a['role'];R=a['idler_diameter']/2
    face=a['wheel_rim_center']-a['wheel_rim_width']/2+a['wheel_rim_land_stock']
    disk=a['wheel_disk_stock'];flange=a['wheel_flange_stock'];boss_stock=a['wheel_boss_flange_stock']
    short,long=joint_points(a);clear=a['wheel_rivet_hole_clearance']
    if role=='drive_rim':
        w=a['wheel_rim_width']/2;land=a['wheel_rim_land_stock']
        outer=a['drive_diameter']/2;inner=a['drive_inner_diameter']/2
        lip=a['drive_lip_inner_radius'];count=int(a['drive_teeth'])
        body=revolution(doc,name,lines([(inner,-w),(outer,-w),(outer,w),
            (lip,w),(lip,-w+land),(inner,-w+land)]))
        tools=[]
        for n in range(count):
            angle=2*math.pi*n/count;radius=a['drive_root_radius']+a['drive_groove_radius']
            tools.append(cylinder_y(a['drive_groove_radius'],2*w+2,
                x=radius*math.sin(angle),z=radius*math.cos(angle)))
        for n in range(24):
            x,z=rotate_point(0,a['wheel_rim_rivet_radius'],7.5+n*15)
            tools.append(cylinder_y((a['wheel_rim_rivet_diameter']+clear)/2,2*w+2,x=x,z=z))
        shape=body.Shape.cut(Part.makeCompound(tools)).removeSplitter()
        feature(body,'InferredToothReliefsAndAttachmentDrilling',shape)
        edges=[]
        for edge in shape.Edges:
            b=edge.BoundBox
            if abs(b.YLength-2*w)<1e-6 and b.XLength<1e-6 and b.ZLength<1e-6:
                p=edge.Vertexes[0].Point
                if abs(math.hypot(p.x,p.z)-outer)<1e-5:edges.append(edge)
        if len(edges)!=2*count:raise ValueError('Drive rim lost axial crest edges')
        rounded=shape.makeFillet(a['drive_crest_radius'],edges)
        if not rounded.isValid() or len(rounded.Solids)!=1 or rounded.cut(shape).Volume>1e-5:
            raise ValueError('Drive crest rounding invalid or added material')
        feature(body,'InferredCrestRounding',rounded)
        body.addProperty('App::PropertyInteger','ToothHypothesis','Reconstruction');body.ToothHypothesis=count
        body.addProperty('App::PropertyString','SourceConflict','Reconstruction')
        body.SourceConflict='HB130/HB133 print 35 teeth; HB119 prints 9:37. Exact profile and engagement unqualified.'
        return body
    if role=='rim':
        w=a['wheel_rim_width']/2;land=a['wheel_rim_land_stock']
        ri=a['wheel_rim_land_inner_radius'];neck=R-a['wheel_running_stock']
        body=revolution(doc,name,lines([(ri,-w),(R,-w),(R,w),(neck,w),(neck,-w+land),(ri,-w+land)]))
        shape=body.Shape
        for n in range(24):
            x,z=rotate_point(0,a['wheel_rim_rivet_radius'],7.5+n*15)
            shape=hole(shape,x,z,(a['wheel_rim_rivet_diameter']+clear)/2,0,2*w+2)
        feature(body,'RimAttachmentDrilling',shape.removeSplitter());return body
    if role=='disk':
        body=revolution(doc,name,lines([(a['wheel_boss_nose_radius']+a['wheel_disk_bore_gap'],-disk/2),
            (a['wheel_disk_radius'],-disk/2),(a['wheel_disk_radius'],disk/2),
            (a['wheel_boss_nose_radius']+a['wheel_disk_bore_gap'],disk/2)]))
        shape=body.Shape
        for n in range(6):
            x,z=rotate_point(0,a['wheel_lightening_radius'],30+n*60)
            shape=hole(shape,x,z,a['wheel_lightening_hole_radius'],0,disk+2)
            for x,z in short+long:
                x,z=rotate_point(x,z,n*60)
                shape=hole(shape,x,z,(a['wheel_small_rivet_diameter']+clear)/2,0,disk+2)
        for n in range(24):
            x,z=rotate_point(0,a['wheel_rim_rivet_radius'],7.5+n*15)
            shape=hole(shape,x,z,(a['wheel_rim_rivet_diameter']+clear)/2,0,disk+2)
        feature(body,'LighteningAndJointHoles',shape.removeSplitter());return body
    if role=='boss':
        end=a['wheel_boss_length']/2;outer=face-flange;inner=outer-boss_stock
        bore=(a['wheel_bush_od']+a['wheel_bush_bore_clearance'])/2
        nose=a['wheel_boss_nose_radius'];hub=a['wheel_boss_body_radius'];fl=a['wheel_boss_flange_radius']
        points=[(bore,-end),(nose,-end),(nose,-outer),(fl,-outer),(fl,-inner),(hub,-inner),
                (hub,inner),(fl,inner),(fl,outer),(nose,outer),(nose,end),(bore,end)]
        body=revolution(doc,name,lines(points));shape=body.Shape
        for n in range(6):
            for x,z in long:
                x,z=rotate_point(x,z,n*60)
                shape=hole(shape,x,z,(a['wheel_small_rivet_diameter']+clear)/2,0,2*end+2)
        feature(body,'BossFlangeDrilling',shape.removeSplitter());return body
    if role=='bush':
        L=a['wheel_bush_length']/2;ri=a['wheel_bush_id']/2;ro=a['wheel_bush_od']/2;c=a['wheel_bush_chamfer']
        return revolution(doc,name,lines([(ri+c,-L),(ro-c,-L),(ro,-L+c),(ro,L-c),
                                          (ro-c,L),(ri+c,L),(ri,L-c),(ri,-L+c)]))
    if role in {'diaphragm_x','diaphragm_y'}:
        from .cad_build import pad
        body=doc.addObject('PartDesign::Body',name)
        sketch=body.newObject('Sketcher::SketchObject','RelievedDiaphragmSection')
        t=a['wheel_web_stock'];edge=face-flange
        # Sketch XY maps to world YZ. Bezier boundaries express the uncertain
        # formed web explicitly, independently of the five-X / one-Y identities.
        sketch.Placement=App.Placement(App.Vector(-t/2,0,0),App.Rotation(App.Vector(1,1,1),120))
        def v(y,z):return App.Vector(y,z,0)
        def spline(points):
            curve=Part.BSplineCurve();curve.buildFromPolesMultsKnots([v(*p) for p in points],[4,4],[0,1],False,3)
            return curve
        top=a['wheel_web_outer_radius'];dip=a['wheel_web_center_radius']
        low=a['wheel_web_inner_radius'];inner_center=a['wheel_web_center_inner_radius']
        flat=a['wheel_web_flat_halfwidth']
        curves=[spline([(-edge,top),(-edge*.85,top),(-flat-(edge-flat)*.3,dip),(-flat,dip)]),
                Part.LineSegment(v(-flat,dip),v(flat,dip)),
                spline([(flat,dip),(flat+(edge-flat)*.3,dip),(edge*.85,top),(edge,top)]),
                Part.LineSegment(v(edge,top),v(edge,low)),
                spline([(edge,low),(edge*.65,low),(edge*.5,inner_center),(0,inner_center)]),
                spline([(0,inner_center),(-edge*.5,inner_center),(-edge*.65,low),(-edge,low)]),
                Part.LineSegment(v(-edge,low),v(-edge,top))]
        for curve in curves:
            i=sketch.addGeometry(curve,False);sketch.addConstraint(Sketcher.Constraint('Block',i))
        shape=pad(body,sketch,t).Shape
        width=a['wheel_flange_width'];lo=a['wheel_flange_inner_radius'];hi=a['wheel_flange_outer_radius']
        for side in [-1,1]:
            start=edge if side==1 else -face
            shape=shape.fuse(Part.makeBox(width,flange,hi-lo,App.Vector(-width/2,start,lo)))
            for x,z in short+long:
                shape=hole(shape,x,z,(a['wheel_small_rivet_diameter']+clear)/2,side*(face-flange/2),flange+2)
        feature(body,'FormedFlangesAndDrilling',shape.removeSplitter());return body
    if role.startswith('rivet_'):
        kind=role[6:];d=a['wheel_rim_rivet_diameter'] if kind=='rim' else a['wheel_small_rivet_diameter']
        stock=a['wheel_'+kind+'_rivet_length'];grip=disk+(a['wheel_rim_land_stock'] if kind=='rim' else flange+(boss_stock if kind=='long' else 0))
        return button_rivet(doc,name,d,stock,grip,a['wheel_rivet_head_ratio'],a['wheel_rivet_head_height_ratio'])
    raise ValueError('Unknown wheel role '+role)


def button_rivet(doc,name,d,stock,grip,head_ratio=.85,height_ratio=.6):
    """Inferred button heads; conserve the specified cylindrical stock volume."""
    from scipy.optimize import brentq
    r=d/2;base=head_ratio*d;factory=height_ratio*d
    capvol=lambda h:math.pi*h*(3*base*base+h*h)/6
    excess=math.pi*r*r*(stock-grip)
    if excess<=0:raise ValueError('Rivet stock cannot span reconstructed joint')
    upset=brentq(lambda h:capvol(h)-excess,1e-6,stock)
    v=lambda x,y:App.Vector(x,y,0)
    def mid(h):
        sphere=(base*base+h*h)/(2*h)
        return math.sqrt(sphere*sphere-(sphere-h/2)**2)
    curves=[Part.Arc(v(0,-grip/2-factory),v(mid(factory),-grip/2-factory/2),v(base,-grip/2)),
        Part.LineSegment(v(base,-grip/2),v(r,-grip/2)),Part.LineSegment(v(r,-grip/2),v(r,grip/2)),
        Part.LineSegment(v(r,grip/2),v(base,grip/2)),
        Part.Arc(v(base,grip/2),v(mid(upset),grip/2+upset/2),v(0,grip/2+upset)),
        Part.LineSegment(v(0,grip/2+upset),v(0,-grip/2-factory))]
    body=revolution(doc,name,curves)
    expected=math.pi*r*r*stock+capvol(factory)
    if abs(body.Shape.Volume-expected)>1e-4:raise ValueError('Wheel rivet upset lost stock volume')
    for key,val in [('SourceStockLength',stock),('InstalledGrip',grip),('UpsetHeight',upset)]:
        body.addProperty('App::PropertyLength',key,'Reconstruction');setattr(body,key,val)
    return body
