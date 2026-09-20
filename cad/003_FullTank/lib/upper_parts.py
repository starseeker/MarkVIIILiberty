"""Upper armor plates in enclosure-local assembly coordinates.

HB35 dimensions control the shell. Unmeasured stations and planar bend/joint
approximations are explicit parameters. These are plates, not fused enclosures.
"""
import math
import FreeCAD as App
import Part


def box(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,App.Vector(x0,y0,z0))


def prism(points, vector):
    vs=[App.Vector(*p) for p in points]
    return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(App.Vector(*vector))


def xz(points,y,width):
    return ([(x,y,z) for x,z in points], (0,width,0))


def xy(points,z,thickness):
    return ([(x,y,z) for x,y in points], (0,0,thickness))


def rect(x0,x1,y0,y1):
    return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]


def cylinder(radius,center,normal,length=3000):
    v=App.Vector(*normal);v.normalize()
    return Part.makeCylinder(radius,length,App.Vector(*center)-v*length/2,v)


def slot(center,length,height,axis='y'):
    # Stadium-ended slots reproduce the rounded viewing slits seen in HB30.
    x,y,z=center;r=height/2;half=(length-height)/2
    if axis=='y':
        return box(x-half,x+half,y-1500,y+1500,z-r,z+r).fuse(
            [cylinder(r,(x-half,y,z),(0,1,0)),cylinder(r,(x+half,y,z),(0,1,0))])
    return box(x-1500,x+1500,y-half,y+half,z-r,z+r).fuse(
        [cylinder(r,(x,y-half,z),(1,0,0)),cylinder(r,(x,y+half,z),(1,0,0))])


def main_stock(kind,a,hand):
    L,W,H,t,r=(a[k] for k in ['upper_length','main_turret_width','upper_height','upper_wall','upper_roof'])
    front=L/2;aft=-L/2;wing=front-a['upper_front_chamfer'];dw=a['driver_width']
    knee=aft+a['upper_rear_rake'];kh=H-a['upper_rear_drop'];crown=knee+a['upper_roof_bend_length']
    fc=a['upper_flap_station'];fw=a['upper_flap_length'];fh=a['upper_flap_height'];g=a['upper_closed_gap']
    j0=fc-fw/2-g-a['upper_flap_border'];j1=fc+fw/2+g+a['upper_flap_border']
    y=W/2-t if hand==1 else -W/2
    if kind=='main_side_front':return xz(rect(j1,wing,0,H),y,t)
    if kind=='main_side_rear':return xz([(aft,0),(j0,0),(j0,H),(crown,H),(knee,kh)],y,t)
    if kind=='main_junction':return xz(rect(j0,j1,0,H),y,t)
    if kind=='main_flap':return xz(rect(fc-fw/2,fc+fw/2,H*.52-fh/2,H*.52+fh/2),y,t)
    if kind=='main_front':
        # Lower central opening communicates with driver's enclosure.
        return ([(front,-dw/2,a['driver_height']),(front,dw/2,a['driver_height']),
                 (front,dw/2,H),(front,-dw/2,H)],(-t,0,0))
    if kind=='main_wing':
        y0=hand*dw/2;y1=hand*W/2
        dx=wing-front;dy=y1-y0;length=math.hypot(dx,dy)
        inward=(-abs(dy)/length*t,hand*dx/length*t,0)
        return ([(front,y0,0),(wing,y1,0),(wing,y1,H),(front,y0,H)],inward)
    if kind=='main_rear':
        # Horizontal section thickness t; normal thickness reduced by rake.
        # Correct the X offset to preserve printed thickness normal to the face.
        dx=t*math.hypot(kh,knee-aft)/kh
        yy=0 if hand==1 else -W/2+t
        return xz([(aft,0),(aft+dx,0),(knee+dx,kh),(knee,kh)],yy,W/2-t)
    if kind=='main_roof':
        slope=(H-kh)/(crown-knee);shift=r*math.sqrt(1+slope*slope)
        # Offset slope in its normal direction, intersect at horizontal underside.
        inner_crown=crown+(shift-r)/slope
        yy=0 if hand==1 else -W/2
        return xz([(knee,kh),(crown,H),(front,H),(front,H-r),(inner_crown,H-r),(knee,kh-shift)],yy,W/2)
    if kind=='roof_door':
        yy=g/2 if hand==1 else -g/2-a['upper_door_width']
        xc=a['upper_door_station'];ll=a['upper_door_length']
        return xy(rect(xc-ll/2,xc+ll/2,yy,yy+a['upper_door_width']),H,r)
    raise ValueError(kind)


def stock(kind,a):
    h=a.get('hand',1)
    if kind.startswith('main_') or kind=='roof_door':return main_stock(kind,a,h)
    if kind.startswith('driver_'):
        L,W,H,t=(a[k] for k in ['driver_length','driver_width','driver_height','driver_wall'])
        if kind=='driver_side':return xz(rect(0,L,0,H-t),W/2-t if h==1 else -W/2,t)
        if kind=='driver_front':return ([(L-t,-W/2+t,0),(L-t,W/2-t,0),(L-t,W/2-t,H-t),(L-t,-W/2+t,H-t)],(t,0,0))
        if kind=='driver_roof':return xy(rect(0,L,-W/2,W/2),H-t,t)
    if kind.startswith('lookout_'):
        W,I,H,t,r=(a[k] for k in ['lookout_width','lookout_inside','lookout_height','lookout_wall','lookout_roof'])
        if kind=='lookout_side':return xz(rect(-W/2,W/2,0,H-r),W/2-t if h==1 else -W/2,t)
        if kind=='lookout_end':
            x=W/2-t if h==1 else -W/2
            return ([(x,-I/2,0),(x,I/2,0),(x,I/2,H-r),(x,-I/2,H-r)],(t,0,0))
        if kind=='lookout_roof':
            w=W/2+a['lookout_roof_overhang'];return xy(rect(-w,w,-w,w),H-r,r)
    raise ValueError('Unknown upper plate: '+kind)


def cuts(kind,a):
    hand=a.get('hand',1);tools=[]
    pl,ph=a['upper_peep_length'],a['upper_peep_height']
    if kind.startswith('main_') or kind=='roof_door':
        L,W,H,t=(a[k] for k in ['upper_length','main_turret_width','upper_height','upper_wall'])
        piw,pih=a['upper_pistol_length'],a['upper_pistol_height']
        if kind=='main_side_front':
            x=(a['upper_flap_station']+a['upper_flap_length']/2+a['upper_closed_gap']+a['upper_flap_border']+L/2-a['upper_front_chamfer'])/2
            tools.append(box(x-piw/2,x+piw/2,-W,W,H*.65-pih/2,H*.65+pih/2))
        elif kind=='main_side_rear':
            for x in [a["upper_rear_peep_station"],a["upper_forward_peep_station"]]:tools.append(slot((x,0,H*.73),pl,ph))
            # HB43 port/starboard ordering differs; do not mirror longitudinal stations.
            mount=a["upper_port_mount_station"] if hand==1 else a["upper_starboard_mount_station"]
            pistol=a["upper_port_pistol_station"] if hand==1 else a["upper_starboard_pistol_station"]
            tools.append(cylinder(a['upper_side_mount_diameter']/2,(mount,0,H*.49),(0,1,0)))
            tools.append(box(pistol-piw/2,pistol+piw/2,-W,W,H*.68-pih/2,H*.68+pih/2))
        elif kind=='main_junction':
            fc=a['upper_flap_station'];fw=a['upper_flap_length']/2+a['upper_closed_gap'];fh=a['upper_flap_height']/2+a['upper_closed_gap']
            tools.append(box(fc-fw,fc+fw,-W,W,H*.52-fh,H*.52+fh))
        elif kind=='main_front':tools.append(slot((L/2,0,(H+a['driver_height'])/2),pl,ph,'x'))
        elif kind=='main_wing':
            center=(L/2-a['upper_front_chamfer']/2,hand*(W+a['driver_width'])/4,H*.49)
            tools.append(cylinder(a['upper_wing_mount_diameter']/2,center,(1,hand*a['upper_front_chamfer']/((W-a['driver_width'])/2),0)))
            # Butt/miter approximation: trim against the front plate and side stock.
            tools.extend(prism(*main_stock(k,a,hand)) for k in ['main_front','main_side_front'])
        elif kind=='main_rear':
            kh=H-a['upper_rear_drop'];rake=a['upper_rear_rake'];normal=(-kh,0,rake)
            tools.append(cylinder(a['upper_rear_mount_diameter']/2,(-L/2+rake/2,0,kh/2),normal))
            if hand==1:tools.append(slot((-L/2,W*.35,H*.57),pl,ph,'x'))
            else:tools.append(box(-L,L,-W*.35-piw/2,-W*.35+piw/2,H*.57-pih/2,H*.57+pih/2))
        elif kind=='main_roof':
            # Plan outline follows front center and wings; wall stock is removed
            # at joints so independent physical plates have no material overlap.
            plan=prism(*xy([(-L,-W),(-L,W),(L/2-a['upper_front_chamfer'],W/2),(L/2,a['driver_width']/2),(L/2,-a['driver_width']/2),(L/2-a['upper_front_chamfer'],-W/2)],-100,H+200))
            blank=prism(*stock(kind,a));tools.append(blank.cut(plan))
            for k in ['main_side_front','main_side_rear','main_junction','main_front','main_wing','main_rear']:
                tools.append(prism(*main_stock(k,a,hand)))
            xc=a['upper_door_station'];ll=a['upper_door_clear_length']/2;ww=a['upper_door_clear_width']/2
            tools.append(box(xc-ll,xc+ll,-ww,ww,H-100,H+100))
            xc=a['upper_lookout_station'];ww=a['lookout_inside']/2
            tools.append(box(xc-ww,xc+ww,-ww,ww,H-100,H+100))
    elif kind=='driver_side':tools.append(slot((a['driver_length']*.48,0,a['driver_height']*.64),pl,ph))
    elif kind=='driver_front':tools.append(slot((a['driver_length'],0,a['driver_height']*.66),pl,ph,'x'))
    elif kind=='driver_roof':tools.append(cylinder(a['upper_periscope_diameter']/2,(a['driver_length']*.30,0,a['driver_height']),(0,0,1)))
    elif kind=='lookout_side':tools.append(slot((0,0,a['lookout_height']*.60),pl,ph))
    elif kind=='lookout_end':tools.append(slot((0,0,a['lookout_height']*.60),pl,ph,'x'))
    elif kind=='lookout_roof':
        for x in [-a['lookout_inside']*.25,a['lookout_inside']*.25]:tools.append(cylinder(a['upper_periscope_diameter']/2,(x,0,a['lookout_height']),(0,0,1)))
    return tools


def build(doc,name,builder,a):
    from .cad_build import sketch_polygon,pad
    from .track_parts import feature
    kind=builder.removeprefix('upper_');pts,vec=stock(kind,a)
    body=doc.addObject('PartDesign::Body',name)
    origin=App.Vector(*pts[0]);direction=App.Vector(*vec)
    placement=App.Placement(origin,App.Rotation(App.Vector(0,0,1),direction))
    inverse=placement.inverse()
    local=[inverse.multVec(App.Vector(*p)) for p in pts]
    if max(abs(p.z) for p in local)>1e-7:raise ValueError('Nonplanar plate stock')
    sketch=sketch_polygon(body,'PlateSection',[(p.x,p.y) for p in local],placement)
    blank=pad(body,sketch,direction.Length)
    shape=blank.Shape
    tools=cuts(kind,a)
    for tool in tools:
        if not tool.isNull():shape=shape.cut(tool)
    shape=shape.removeSplitter()
    if tools:feature(body,'OpeningsAndJointTrims',shape)
    return body
