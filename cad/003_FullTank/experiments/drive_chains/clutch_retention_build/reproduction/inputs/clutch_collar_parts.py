"""Catalogue-shaped coupling, sliding collar, end bearing and locking wire."""
import math
import FreeCAD as App
import Part
from air_pressure_pump_parts import xc,box
from transmission_input_parts import spline
from clutch_drive_parts import hex_x


def wire_path(c,tail):
    x=c['joint_face']+c['collar_lip_stock']+c['bolt_head_height']/2
    radius=c['bolt_circle'];angle=math.radians(c['wire_seam_angle']);gap=math.radians(c['wire_seam_half_angle'])
    u=App.Vector(0,math.cos(angle),math.sin(angle));v=App.Vector(0,-math.sin(angle),math.cos(angle));axis=App.Vector(1,0,0)
    base=App.Vector(x+c['wire_bridge_height'],0,0)+u*(radius*math.cos(gap));a=c['wire_twist_radius'];turn=c['wire_twist_turns'];handle=c['wire_bend_handle']
    def helix(t,phase):return base+axis*t+a*(u*math.cos(phase+2*math.pi*turn*t/tail)+v*math.sin(phase+2*math.pi*turn*t/tail))
    def tangent(phase):
        p=axis+a*(2*math.pi*turn/tail)*(-u*math.sin(phase)+v*math.cos(phase));p.normalize();return p
    def circle(theta):return App.Vector(x,radius*math.cos(theta),radius*math.sin(theta))
    def ct(theta):return App.Vector(0,-math.sin(theta),math.cos(theta))
    def bezier(p0,p1,p2,p3,t):return p0*(1-t)**3+p1*(3*t*(1-t)**2)+p2*(3*t*t*(1-t))+p3*t**3
    pts=[helix(tail*(1-n/60),math.pi/2) for n in range(61)];cuts=[0,len(pts)-1]
    start=angle+gap;end=angle+2*math.pi-gap;p0=pts[-1];p3=circle(start)
    p1=p0-tangent(math.pi/2)*handle;p2=p3-ct(start)*handle
    pts.extend(bezier(p0,p1,p2,p3,n/24) for n in range(1,25));cuts.append(len(pts)-1)
    for n in range(1,205):
        pts.append(circle(start+(end-start)*n/204))
        if n%51==0:cuts.append(len(pts)-1)
    p0=pts[-1];p3=helix(0,3*math.pi/2);p1=p0+ct(end)*handle;p2=p3-tangent(3*math.pi/2)*handle
    pts.extend(bezier(p0,p1,p2,p3,n/24) for n in range(1,25));cuts.append(len(pts)-1)
    pts.extend(helix(tail*n/60,3*math.pi/2) for n in range(1,61));cuts.append(len(pts)-1)
    curve=Part.BSplineCurve();curve.interpolate(pts)
    return curve,pts,cuts


def locking_wire(c):
    low,high=3.,25.
    assert wire_path(c,low)[0].toShape().Length<c['wire_length']<wire_path(c,high)[0].toShape().Length
    for _ in range(36):
        middle=(low+high)/2;curve,pts,cuts=wire_path(c,middle)
        if curve.toShape().Length<c['wire_length']:low=middle
        else:high=middle
    curve,pts,cuts=wire_path(c,(low+high)/2);edges=[]
    for start,end in zip(cuts,cuts[1:]):
        piece=curve.copy();piece.segment(curve.parameter(pts[start]),curve.parameter(pts[end]));edges.append(piece.toShape())
    profile=Part.Wire([Part.makeCircle(c['wire_diameter']/2,pts[0],curve.tangent(curve.FirstParameter)[0])])
    shape=Part.Wire(edges).makePipeShell([profile],True,True)
    return shape,Part.Wire([curve.toShape()]),dict(centerline_length=curve.toShape().Length,tail_axial_length=(low+high)/2,sweep_spans=len(edges))


def build(c,dc):
    joint=c['joint_face'];seat=c['spring_seat'];end=joint+c['collar_lip_stock'];pocket=c['bearing_pocket_start'];R=c['flange_radius']
    coupling=xc(c['coupling_body_radius'],c['coupling_rear'],joint)
    coupling=coupling.fuse(xc(R,seat,seat+c['spring_flange_stock'])).fuse(xc(R,joint-c['coupling_joint_stock'],joint)).removeSplitter()
    fillets=[e for e in coupling.Edges if hasattr(e.Curve,'Radius') and abs(e.Curve.Radius-c['coupling_body_radius'])<1e-6 and any(abs(e.CenterOfMass.x-x)<1e-6 for x in [seat,seat+c['spring_flange_stock'],joint-c['coupling_joint_stock']])]
    assert len(fillets)==3
    coupling=coupling.makeFillet(c['fillet_radius'],fillets)
    gap=.15
    coupling=coupling.cut(spline(dc['spline_root_radius']+gap,dc['spline_radius']+gap,dc['spline_width']+2*gap,dc['spline_count'],c['coupling_rear']-1,pocket))
    coupling=coupling.cut(xc(c['bearing_pocket_radius'],pocket,joint+1))
    collar=xc(c['collar_body_radius'],joint,c['collar_front']).fuse(xc(R,joint,end))
    collar=collar.fuse(xc(c['collar_front_radius'],c['collar_front_flange_start'],c['collar_front'])).removeSplitter()
    collar=collar.cut(xc(c['collar_rear_bore_radius'],joint-1,c['collar_bore_step']))
    collar=collar.cut(xc(c['collar_front_bore_radius'],c['collar_bore_step'],c['collar_front']+1))
    ring=xc(c['ring_body_radius'],pocket,joint).fuse(xc(c['bearing_pocket_radius'],c['ring_shoulder'],joint))
    ring=ring.cut(xc(c['ring_bore_radius'],pocket-1,joint+1)).removeSplitter()
    bush=xc(c['bearing_pocket_radius'],pocket,c['ring_shoulder']).cut(xc(c['ring_body_radius']+c['bush_running_gap'],pocket-1,c['ring_shoulder']+1)).removeSplitter()
    bolt=hex_x(c['bolt_head_af'],0,c['bolt_head_height']).fuse(xc(c['bolt_diameter']/2,-c['bolt_length'],0)).removeSplitter()
    bolt=bolt.cut(Part.makeCylinder(c['head_drill_radius'],2*c['bolt_head_af'],App.Vector(c['bolt_head_height']/2,0,-c['bolt_head_af']),App.Vector(0,0,1))).removeSplitter()
    occ=[]
    for n in range(c['bolt_count']):
        theta=2*math.pi*n/c['bolt_count'];y=c['bolt_circle']*math.cos(theta);z=c['bolt_circle']*math.sin(theta)
        collar=collar.cut(xc(c['bolt_diameter']/2+c['clearance_hole_gap'],joint-1,end+1,y,z))
        coupling=coupling.cut(xc(c['bolt_diameter']/2+c['thread_envelope_gap'],end-c['bolt_length']-c['blind_tip_clearance'],joint+1,y,z))
        occ.append(dict(name=f'ClutchCollar_Screw{n+1}',key='screw',xyz=[end,y,z],angle=math.degrees(theta)))
    parts=dict(collar=collar.removeSplitter(),ring=ring,bush=bush,screw=bolt)
    parts['wire'],spine,wd=locking_wire(c)
    for key in ['collar','ring','bush','wire']:occ.append(dict(name='ClutchCollar_'+key,key=key,xyz=[0,0,0],angle=0))
    for key,s in {**parts,'coupling':coupling}.items():
        assert s.isValid() and len(s.Solids)==1,(key,s.isValid(),len(s.Solids))
    return parts,occ,coupling.removeSplitter(),spine,dict(wire=wd,thread_engagement=c['bolt_length']-c['collar_lip_stock'],
        blind_back_wall=c['coupling_joint_stock']-(c['bolt_length']-c['collar_lip_stock']+c['blind_tip_clearance']))
