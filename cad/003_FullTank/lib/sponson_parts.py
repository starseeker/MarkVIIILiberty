"""Individual standard sponson shell plates, with explicit inferred contours.

Longitudinal u is aft from the front aperture edge, v is outward. Source-sized
armor and registered aperture bounds govern this partial, faceted reconstruction.
The open front/outboard bay is reserved for the separate rotating gun shield.
"""
import json
import math
import FreeCAD as App
import Part
from .upper_parts import prism,box

_CACHE={}


def layout(a):
    L,D,H=a['length'],a['depth'],a['height']
    return {'L':L,'D':D,'H':H,'a':.22*L,'b':.80*L,'s':.52*L,
            'q':.32*D,'k':.48*D,'rise':a['sponson_plate_shoulder_rise'],
            'opening_bottom':a['sponson_plate_opening_bottom'],
            'opening_top':H-a['sponson_plate_top_band']}


def roles(hand):
    result=['floor','sloping_bottom','sloping_side','roof','front_vertical','front_wing',
            'front_lower','front_upper','side_lower','side_upper','side','back_wing','back_side','back',
            'shield_bottom_front','shield_bottom_middle','shield_bottom_rear',
            'shield_top_front']
    if hand==-1:result+=['shield_top_middle']
    return result+['shield_top_rear']


def planar_clip(poly,axis,value,keep_greater):
    result=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        dp=(p[axis]-value)*(1 if keep_greater else -1)
        dq=(q[axis]-value)*(1 if keep_greater else -1)
        if dp>=-1e-8:result.append(p)
        if dp*dq < -1e-12:
            t=dp/(dp-dq);result.append(tuple(p[i]+t*(q[i]-p[i]) for i in range(len(p))))
    return result


def plan(a):
    d=layout(a);L,D=d['L'],d['D']
    return [(0,0),(0,d['q']),(d['a'],D),(d['b'],D),(L,d['k']),(L,0)]


def stock(role,a):
    d=layout(a);L,D,H,q,k,A,B,S=(d[x] for x in ['L','D','H','q','k','a','b','s'])
    t=a['sponson_plate_side'];r=a['sponson_plate_roof'];f=a['sponson_plate_floor']
    sh=a['sponson_plate_shield'];rise=d['rise'];bottom=d['opening_bottom'];top=d['opening_top']
    slope=rise/(.75*D)
    z_at=lambda v:max(0,(v-.25*D)*slope)
    def horizontal(poly,z,thickness):return [(u,v,z) for u,v in poly],(0,0,thickness)
    def wall(p,q,z0,z1):
        du,dv=q[0]-p[0],q[1]-p[1];ll=math.hypot(du,dv)
        z0a=z_at(p[1]) if z0 is None else z0;z0b=z_at(q[1]) if z0 is None else z0
        return [(p[0],p[1],z0a),(q[0],q[1],z0b),(q[0],q[1],z1),(p[0],p[1],z1)],(dv/ll*t,-du/ll*t,0)
    poly=plan(a)
    if role=='roof':return horizontal(poly,H-r,r)
    if role=='floor':return horizontal(planar_clip(poly,1,.25*D,False),0,f)
    if role in {'sloping_bottom','sloping_side'}:
        poly=planar_clip(poly,1,.25*D,True)
        poly=planar_clip(poly,0,.62*L,role=='sloping_side')
        th=a['sponson_plate_forward_floor'] if role=='sloping_bottom' else a['sponson_plate_aft_floor']
        fac=th/math.sqrt(1+slope*slope)
        return [(u,v,z_at(v)) for u,v in poly],(0,-slope*fac,fac)
    walls={
        'front_vertical':((0,0),(0,.10*D),None,H-r),
        'front_wing':((0,.10*D),(0,q),None,H-r),
        'front_lower':((0,q),(A,D),None,bottom-sh),
        'front_upper':((0,q),(A,D),top+sh,H-r),
        'side_lower':((A,D),(S,D),None,bottom-sh),
        'side_upper':((A,D),(S,D),top+sh,H-r),
        'side':((S,D),(B,D),None,H-r),
        'back_wing':((B,D),(L,k),None,H-r),
        'back_side':((L,k),(L,.14*D),None,H-r),
        'back':((L,.14*D),(L,0),None,H-r)}
    if role in walls:return wall(*walls[role])
    if role.startswith('shield_'):
        _,level,segment=role.split('_');w=a['sponson_plate_shield_band']
        p,q=(0,q),(A,D);du,dv=q[0]-p[0],q[1]-p[1];ll=math.hypot(du,dv)
        n=(dv/ll*w,-du/ll*w);mid=(A+S)/2
        # Miter intersection of the front inner edge with the side's inner edge.
        inner_v=D-w
        inner_u=p[0]+n[0]+(inner_v-p[1]-n[1])*du/dv
        front=[p,q,(inner_u,inner_v),(p[0]+n[0],p[1]+n[1])]
        middle=[q,(mid,D),(mid,inner_v),(inner_u,inner_v)]
        rear=[(mid,D),(S,D),(S,inner_v),(mid,inner_v)]
        if level=='top' and a['hand']==1 and segment=='front':
            poly=[p,q,(mid,D),(mid,inner_v),(inner_u,inner_v),(p[0]+n[0],p[1]+n[1])]
        else:poly={'front':front,'middle':middle,'rear':rear}[segment]
        return horizontal(poly,bottom-sh if level=='bottom' else top,sh)
    raise ValueError('Unknown sponson plate '+role)


def xyz_spec(spec,hand):
    pts,vec=spec
    return [(-u,hand*v,z) for u,v,z in pts],(-vec[0],hand*vec[1],vec[2])


def openings(role,a):
    """Rounded peep slots and rectangular pistol holes normal to each wall."""
    d=layout(a);D,H,L=d['D'],d['H'],d['L'];h=a['hand']
    edges={'front_wing':((0,.10*D),(0,d['q'])),
           'side':((d['s'],D),(d['b'],D)),
           'back_side':((L,d['k']),(L,.14*D)),
           'back_wing':((d['b'],D),(L,d['k']))}
    if role not in edges:return []
    peep=role!='back_wing' or h==1
    pistol=role in {'front_wing','back_side'} or role=='side' and h==1
    p,q=edges[role];du,dv=q[0]-p[0],q[1]-p[1];ll=math.hypot(du,dv)
    tangent=App.Vector(-du/ll,h*dv/ll,0);normal=App.Vector(-dv/ll,-h*du/ll,0)
    center=App.Vector(-(p[0]+q[0])/2,h*(p[1]+q[1])/2,H*.74)
    up=App.Vector(0,0,1);result=[]
    def rectangle(c,width,height):
        pts=[c+tangent*x+up*z-normal*40 for x,z in [(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2)]]
        return prism([tuple(v) for v in pts],tuple(normal*80))
    if peep:
        radius=a['peep_height']/2;half=(a['peep_length']-a['peep_height'])/2
        tool=rectangle(center,2*half,2*radius)
        for sign in [-1,1]:tool=tool.fuse(Part.makeCylinder(radius,80,center+tangent*(half*sign)-normal*40,normal))
        result.append(tool)
    if pistol:
        center.z=H*.49;result.append(rectangle(center,a['pistol_length'],a['pistol_height']))
    return result


def solids(a):
    key=json.dumps({k:v for k,v in a.items() if k!='role'},sort_keys=True)
    if key in _CACHE:return _CACHE[key]
    result={};prior=[]
    for role in roles(a['hand']):
        spec=xyz_spec(stock(role,a),a['hand']);blank=prism(*spec);solid=blank
        # Explicit butt/miter ownership: floors, roof, walls, then shield infills.
        for other in prior:
            if solid.BoundBox.intersect(other.BoundBox):solid=solid.cut(other)
        for tool in openings(role,a):solid=solid.cut(tool)
        solid=solid.removeSplitter()
        if not solid.isValid() or len(solid.Solids)!=1:raise ValueError('Invalid sponson joint trim '+role)
        if solid.Volume<blank.Volume*.6:raise ValueError('Excessive sponson joint/opening removal '+role)
        result[role]=(spec,solid);prior.append(solid)
    _CACHE[key]=result
    return result


def build(doc,name,a):
    from .cad_build import sketch_polygon,pad
    from .track_parts import feature
    spec,shape=solids(a)[a['role']];pts,vec=spec
    body=doc.addObject('PartDesign::Body',name)
    direction=App.Vector(*vec);placement=App.Placement(App.Vector(*pts[0]),App.Rotation(App.Vector(0,0,1),direction))
    inverse=placement.inverse();local=[inverse.multVec(App.Vector(*p)) for p in pts]
    if max(abs(p.z) for p in local)>1e-7:raise ValueError('Sponson stock is not planar')
    sketch=sketch_polygon(body,'SourcePlateSection',[(p.x,p.y) for p in local],placement)
    pad(body,sketch,direction.Length)
    feature(body,'OpeningsAndJointTrims',shape.copy())
    return body
