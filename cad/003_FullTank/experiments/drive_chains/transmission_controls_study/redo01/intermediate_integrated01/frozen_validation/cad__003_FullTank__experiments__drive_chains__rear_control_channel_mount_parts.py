"""Source-counted M4130 floor attachments with explicit profile and rivet hypotheses."""
import math
import FreeCAD as App
import Part
from rear_control_channel_stock import channel
from transmission_brake_stop_parts import hexagon
from transmission_frame_joint_parts import cap
V=App.Vector

def prism_xy(points,height):
    vs=[V(x,y,0) for x,y in points]
    return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,height))

def formed_rivet(c,grip):
    radius=c['diameter']/2
    factory_radius=radius*c['factory_ratio'];tail_radius=radius*c['upset_ratio']
    extra=math.pi*radius**2*(c['stock_length']-grip)
    if extra<=0:raise ValueError('Rivet stock cannot form a retaining tail')
    low,high=0.,2*tail_radius
    for _ in range(80):
        height=(low+high)/2
        if math.pi*height*(3*tail_radius**2+height**2)/6<extra:low=height
        else:high=height
    height=(low+high)/2
    if height>=tail_radius:raise ValueError('Selected stock requires more than a hemispherical upset')
    head=cap(factory_radius,c['factory_height_ratio']*c['diameter']);head.rotate(V(),V(1,0,0),180)
    tail=cap(tail_radius,height);tail.translate(V(0,0,grip))
    shape=Part.makeCylinder(radius,grip).fuse(head).fuse(tail)
    return shape,dict(grip_mm=grip,factory_radius_mm=factory_radius,upset_radius_mm=tail_radius,
                      upset_height_mm=height,upset_stock_volume_mm3=extra)

def parts(c,floor,floor_pose,nut):
    ch=c['channel'];a=c['cleat'];b=c['bolt'];r=c['rivet'];lk=c['lock']
    stock=channel(ch['width'],ch['height'],ch['stock'],ch['length'])
    half=a['width']/2
    foot=prism_xy([(0,-half),(0,half),(-a['reach'],-half)],a['stock'])
    upright=Part.makeBox(a['stock'],a['width'],a['height'],V(-a['stock'],-half,0))
    cleat=foot.fuse(upright)
    cleat=cleat.cut(Part.makeCylinder(b['hole_diameter']/2,a['stock']+2,V(a['bolt_x'],a['bolt_y'],-1)))
    cleat_holes=[];channel_holes=[];floor_holes=[];floor_axes=[]
    channel_pose=App.Placement(V(*ch['placement']),App.Rotation())
    for y in a['rivet_y']:
        cleat_holes.append(Part.makeCylinder(r['hole_diameter']/2,a['stock']+2,V(-a['stock']-1,y,a['rivet_z']),V(1,0,0)))
    cleat=cleat.cut(Part.makeCompound(cleat_holes))
    for station in a['stations_y']:
        for y in a['rivet_y']:
            channel_holes.append(Part.makeCylinder(r['hole_diameter']/2,ch['stock']+2,V(-ch['width']/2-1,station+y,a['rivet_z']),V(1,0,0)))
        world=channel_pose.multVec(V(-ch['width']/2+a['bolt_x'],station+a['bolt_y'],0))
        drill=Part.makeCylinder(b['hole_diameter']/2,c['floor_thickness']+2,world+V(0,0,-c['floor_thickness']-1))
        drill.Placement=floor_pose.inverse().multiply(drill.Placement)
        floor_holes.append(drill);floor_axes.append(list(world))
    stock=stock.cut(Part.makeCompound(channel_holes))
    floor_new=floor.cut(Part.makeCompound(floor_holes))
    head=hexagon(b['head_af'],b['head_height']);head.translate(V(0,0,-b['head_height']))
    bolt=Part.makeCylinder(b['diameter']/2,b['underhead_length']).fuse(head)
    lock=Part.makeCylinder(lk['outer_radius'],lk['thickness']).cut(Part.makeCylinder(lk['inner_radius'],lk['thickness']+2,V(0,0,-1)))
    lock=lock.cut(Part.makeBox(lk['gap'],lk['outer_radius']+1,lk['thickness']+2,V(-lk['gap']/2,0,-1)))
    rivet,rd=formed_rivet(r,a['stock']+ch['stock'])
    shapes=dict(channel=stock,cleat=cleat,bolt=bolt,lock=lock,nut=nut,rivet=rivet,floor=floor_new)
    for key,s in shapes.items():
        if not(s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.Placement.isIdentity()):
            raise ValueError(('Invalid definition',key,s.isValid(),len(s.Solids),str(s.Placement)))
    return shapes,dict(rivet=rd,floor_hole_centers_world_mm=floor_axes,
                       floor_source_pose=list(floor_pose.toMatrix().A)),dict(floor_holes=Part.makeCompound(floor_holes),channel_holes=Part.makeCompound(channel_holes))
