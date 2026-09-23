"""Working drum, dished flywheel and source-length wire geometry."""
import math
import FreeCAD as App
import Part
from transmission_input_parts import spline,revolve
from clutch_drive_parts import hex_x
from transmission_planet_parts import gear_outline


def xc(radius,low,high,y=0,z=0):
    return Part.makeCylinder(radius,high-low,App.Vector(low,y,z),App.Vector(1,0,0))


def inward_wire_path(c,tail):
    """Keep the six-head circle; place the paired tail inward in the head plane."""
    x=c['wire_plane'];R=c['wire_pitch_radius'];angle=math.radians(c['wire_seam_angle']);gap=math.radians(c['wire_seam_half_angle'])
    radial=App.Vector(0,math.cos(angle),math.sin(angle));tangent=App.Vector(0,-math.sin(angle),math.cos(angle));axis=App.Vector(1,0,0)
    base=axis*x+radial*(R*math.cos(gap)-c['wire_bridge_inward']);a=c['wire_twist_radius'];turns=c['wire_twist_turns'];handle=c['wire_bend_handle']
    def helix(t,phase):return base-radial*t+a*(axis*math.cos(phase+2*math.pi*turns*t/tail)+tangent*math.sin(phase+2*math.pi*turns*t/tail))
    def ht(phase):
        v=-radial+a*2*math.pi*turns/tail*(-axis*math.sin(phase)+tangent*math.cos(phase));v.normalize();return v
    def circle(t):return App.Vector(x,R*math.cos(t),R*math.sin(t))
    def ct(t):return App.Vector(0,-math.sin(t),math.cos(t))
    def bezier(a,b,c,d,t):return a*(1-t)**3+b*3*t*(1-t)**2+c*3*t*t*(1-t)+d*t**3
    pts=[helix(tail*(1-n/60),math.pi/2) for n in range(61)];cuts=[0,len(pts)-1]
    lo=angle+gap;hi=angle+2*math.pi-gap;p0=pts[-1];p3=circle(lo)
    p1=p0-ht(math.pi/2)*handle;p2=p3-ct(lo)*handle
    pts.extend(bezier(p0,p1,p2,p3,n/24) for n in range(1,25));cuts.append(len(pts)-1)
    for n in range(1,205):
        pts.append(circle(lo+(hi-lo)*n/204))
        if n%51==0:cuts.append(len(pts)-1)
    p0=pts[-1];p3=helix(0,3*math.pi/2);p1=p0+ct(hi)*handle;p2=p3-ht(3*math.pi/2)*handle
    pts.extend(bezier(p0,p1,p2,p3,n/24) for n in range(1,25));cuts.append(len(pts)-1)
    pts.extend(helix(tail*n/60,3*math.pi/2) for n in range(1,61));cuts.append(len(pts)-1)
    curve=Part.BSplineCurve();curve.interpolate(pts);return curve,pts,cuts


def inward_wire(c):
    low,high=3.,50.
    lengths=[inward_wire_path(c,t)[0].toShape().Length for t in [low,high]]
    assert lengths[0]<c['wire_length']<lengths[1],(lengths,c['wire_length'])
    for _ in range(38):
        mid=(low+high)/2
        if inward_wire_path(c,mid)[0].toShape().Length<c['wire_length']:low=mid
        else:high=mid
    curve,pts,cuts=inward_wire_path(c,(low+high)/2);edges=[]
    for lo,hi in zip(cuts,cuts[1:]):
        piece=curve.copy();piece.segment(curve.parameter(pts[lo]),curve.parameter(pts[hi]));edges.append(piece.toShape())
    profile=Part.Wire([Part.makeCircle(c['wire_diameter']/2,pts[0],curve.tangent(curve.FirstParameter)[0])])
    solid=Part.Wire(edges).makePipeShell([profile],True,True)
    assert solid.isValid() and len(solid.Solids)==1
    return solid,Part.Wire([curve.toShape()]),dict(centerline_length=curve.toShape().Length,tail_inward_length=(low+high)/2,sweep_spans=len(edges))


def drum_shape(c,cone_report):
    d=cone_report['datums'];large=App.Vector(d['large_face'][0],d['large_face'][1],0)
    small=App.Vector(d['small_face'][0],d['small_face'][1],0)
    tangent=small-large;tangent.normalize();normal=App.Vector(-tangent.y,tangent.x,0)
    b=c['drum_inner_bend_radius'];t=c['drum_stock'];center=small-normal*b
    inner=App.Vector(center.x+b,center.y,0);outer=App.Vector(center.x+b+t,center.y,0)
    angle=math.atan2(normal.y,normal.x)
    mid=lambda radius: center+App.Vector(math.cos(angle/2),math.sin(angle/2),0)*radius
    inner_bottom=App.Vector(inner.x,c['drum_flange_inner_radius'],0);outer_bottom=App.Vector(outer.x,c['drum_flange_inner_radius'],0)
    edges=[Part.makeLine(large,small),Part.Arc(small,mid(b),inner).toShape(),Part.makeLine(inner,inner_bottom),
        Part.makeLine(inner_bottom,outer_bottom),Part.makeLine(outer_bottom,outer),
        Part.Arc(outer,mid(b+t),small+normal*t).toShape(),Part.makeLine(small+normal*t,large+normal*t),Part.makeLine(large+normal*t,large)]
    shape=Part.Face(Part.Wire(edges)).revolve(App.Vector(),App.Vector(1,0,0),360)
    return shape,dict(bolt_seat=inner.x,flywheel_joint=outer.x,bend_center=[center.x,center.y],
        bend_tangent_radius=center.y,contact_large=[large.x,large.y],contact_small=[small.x,small.y],normal=[normal.x,normal.y])


def build(c,cone_report,retention_report):
    drum,d=drum_shape(c,cone_report);stack=cone_report['parent_controls'];collar_rear=842.95
    rear=collar_rear+c['hub_rear_setback'];spline_end=collar_rear+stack['sleeve_length']+c['spline_shoulder_gap']
    root=stack['sleeve_bore_radius']-c['spline_radial_gap'];tip=stack['sleeve_spline_root_radius']-c['spline_radial_gap']
    journal=stack['bearing_front_bore_radius']-c['journal_running_gap'];front=c['journal_front']+c['flywheel_web_stock_axial']
    joint=d['flywheel_joint'];rim_front=joint+c['flywheel_rim_stock'];wo=c['flywheel_web_outer_radius'];wf=c['flywheel_rim_front_transition_radius']
    R=c['flywheel_diameter']/2;n=c['starter_teeth'];module=2*R/(n+2);pitch=n*module/2;gear_root=pitch-1.25*module
    # One actual flywheel body: removable tapered hub, external sliding teeth,
    # journal, dished web and toothed rim. The engine crankshaft is not a stub here.
    profile=[(rear,root),(spline_end,root),(spline_end,journal),(c['journal_front'],journal),(joint,wo),
        (joint,gear_root),(rim_front,gear_root),(rim_front,wf),(joint+c['flywheel_web_stock_axial'],wo),
        (front,journal),(front,c['taper_front_radius']),(rear,c['taper_rear_radius'])]
    flywheel=revolve(profile)
    splines=spline(root,tip,stack['sleeve_spline_width']-2*c['spline_side_gap'],stack['sleeve_spline_count'],rear,spline_end)
    # Hollow the additional spline envelope with the same extended taper.
    slope=(c['taper_front_radius']-c['taper_rear_radius'])/(front-rear)
    bore=Part.makeCone(c['taper_rear_radius']-slope,c['taper_front_radius']+slope,front-rear+2,App.Vector(rear-1,0,0),App.Vector(1,0,0))
    flywheel=flywheel.fuse(splines.cut(bore)).removeSplitter()
    face,tooth_report=gear_outline(n,pitch,gear_root,R,c['starter_pressure_angle'],c['starter_tooth_thinning'],c['starter_flank_samples'])
    teeth=face.extrude(App.Vector(0,c['flywheel_rim_stock'],0));teeth.translate(App.Vector(0,joint,0));teeth.rotate(App.Vector(),App.Vector(0,0,1),-90)
    teeth=teeth.cut(xc(gear_root-.25,joint-1,rim_front+1));flywheel=flywheel.fuse(teeth).removeSplitter()
    # Full through slot permits sliding the flywheel over the key on a tapered shaft.
    lo=rear-1;hi=front+1;depth=c['keyway_depth'];half=c['keyway_width']/2
    vertices=[App.Vector(lo,0,-half),App.Vector(hi,0,-half),App.Vector(hi,c['taper_front_radius']+slope+depth,-half),App.Vector(lo,c['taper_rear_radius']-slope+depth,-half)]
    slot=Part.Face(Part.makePolygon(vertices+vertices[:1])).extrude(App.Vector(0,0,2*half));flywheel=flywheel.cut(slot).removeSplitter()
    screw=hex_x(c['bolt_head_af'],0,c['bolt_head_height']).fuse(xc(c['bolt_diameter']/2,-c['bolt_length'],0)).removeSplitter()
    screw=screw.cut(Part.makeCylinder(c['head_drill_radius'],2*c['bolt_head_af'],App.Vector(c['bolt_head_height']/2,0,-c['bolt_head_af']),App.Vector(0,0,1))).removeSplitter()
    occurrences=[]
    for k in range(c['bolt_count']):
        angle=c['bolt_phase']+360*k/c['bolt_count'];theta=math.radians(angle);y=c['bolt_circle']*math.cos(theta);z=c['bolt_circle']*math.sin(theta)
        drum=drum.cut(xc(c['bolt_diameter']/2+c['bolt_hole_gap'],d['bolt_seat']-1,joint+1,y,z))
        flywheel=flywheel.cut(xc(c['bolt_diameter']/2+c['thread_envelope_gap'],joint-.1,d['bolt_seat']+c['bolt_length']+c['blind_tip_gap'],y,z))
        rotation=App.Rotation(App.Vector(1,0,0),angle).multiply(App.Rotation(App.Vector(0,1,0),180))
        occurrences.append(dict(name=f'ClutchDrum_Screw{k+1}',key='screw',xyz=[d['bolt_seat'],y,z],rotation=list(rotation.Q),parent='Drum'))
    wc=dict(c,wire_plane=d['bolt_seat']-c['bolt_head_height']/2,wire_pitch_radius=c['bolt_circle'])
    wire,spine,wd=inward_wire(wc)
    rc=dict(retention_report['controls'],wire_bridge_inward=10.,wire_bend_handle=3.,wire_plane=retention_report['datums']['wire_plane'],wire_pitch_radius=retention_report['datums']['pitch_radius'])
    retained,retained_spine,rd=inward_wire(rc)
    parts=dict(drum=drum.removeSplitter(),flywheel=flywheel.removeSplitter(),screw=screw,wire=wire)
    for key in ['drum','flywheel','wire']:occurrences.append(dict(name='ClutchDrum_'+key,key=key,xyz=[0,0,0],rotation=[0,0,0,1],parent='Flywheel' if key=='flywheel' else 'Drum'))
    for key,shape in parts.items():assert shape.isValid() and len(shape.Solids)==1,(key,shape.isValid(),len(shape.Solids))
    d.update(hub_rear=rear,spline_front=spline_end,spline_root=root,spline_tip=tip,journal_radius=journal,
        taper_front=front,flywheel_front=rim_front,starter_tooth_profile=tooth_report,wire=wd,retention_wire=rd,
        thread_engagement=c['bolt_length']-c['drum_stock'],blind_back_wall=rim_front-(d['bolt_seat']+c['bolt_length']+c['blind_tip_gap']))
    return parts,occurrences,retained,dict(drum=spine,retention=retained_spine),d
