"""Static clutch-stop drive, in the transmission core frame (X forward).

Source identities/counts and selected sizes are retained in the adjacent dossier.
Hidden head/socket contours, drum profile and belt pitch convention are inferred.
The scored belt is one assembly representation; scores are not a link inventory.
"""
import math
import FreeCAD as App
import Part
from air_pressure_pump_parts import box, xc, moved
from air_pump_mount_parts import belt_center
from transmission_input_parts import revolve, spline
from transmission_stud_parts import hex_x


def bolt_axes(c):
    return [(c['bolt_circle']*math.cos(math.radians(c['bolt_clock']+360*n/c['bolt_count'])),
             c['bolt_circle']*math.sin(math.radians(c['bolt_clock']+360*n/c['bolt_count'])))
            for n in range(c['bolt_count'])]


def rounded_head(half, radius, start, end):
    # Exact rounded rectangle, built with analytic straight/circular boundaries.
    s=box(start,end,-half,half,-half+radius,half-radius)
    s=s.fuse(box(start,end,-half+radius,half-radius,-half,half))
    for y in [-half+radius,half-radius]:
        for z in [-half+radius,half-radius]:s=s.fuse(xc(radius,start,end,y,z))
    return s.removeSplitter()


def revised_flange(c,ic,bc):
    start=ic['pinion_shoulder']+2*bc['cone_width']+ic['cone_front_gap']
    s=xc(ic['coupling_radius'],start,ic['coupling_end'])
    s=s.fuse(xc(ic['coupling_flange_radius'],ic['coupling_flange_start'],ic['coupling_end']))
    s=s.cut(spline(ic['spline_root']+ic['spline_gap'],ic['spline_tip']+ic['spline_gap'],
        ic['spline_width']+2*ic['spline_gap'],ic['spline_count'],start-1,ic['washer_start']))
    s=s.cut(xc(ic['coupling_nut_recess'],ic['washer_start'],ic['coupling_end']+1))
    for y,z in bolt_axes(c):
        s=s.cut(xc(c['bolt_diameter']/2+c['receiver_gap'],c['flange_back']-1,c['joint_face']+1,y,z))
    return s.removeSplitter()


def belt_datums(c,pc):
    k=math.tan(math.radians(c['groove_angle']/2))
    inset=(c['groove_width']-c['belt_top_width'])/(2*k)
    pinset=(pc['pulley_groove_width']-c['belt_top_width'])/(2*math.tan(math.radians(pc['pulley_groove_angle']/2)))
    rd=c['drum_radius']-inset-c['belt_pitch_depth']
    rp=pc['pulley_radius']-pinset-c['belt_pitch_depth']
    center=belt_center(c['belt_length'],rd,rp);alpha=math.asin((rd-rp)/center)
    return dict(drive_pitch_radius=rd,pump_pitch_radius=rp,center_distance=center,
        angle=alpha,top_inset=inset,pump_top_inset=pinset,pitch_plane=c['groove_plane'],
        straight_length=math.sqrt(center*center-(rd-rp)**2),pitch_length=c['belt_length'])


def belt(c,pc):
    d=belt_datums(c,pc);rd=d['drive_pitch_radius'];rp=d['pump_pitch_radius']
    center=d['center_distance'];alpha=d['angle'];x=c['groove_plane']
    outer=c['belt_pitch_depth'];inner=outer-c['belt_depth'];w=c['belt_top_width']/2
    wi=w-c['belt_depth']*math.tan(math.radians(c['groove_angle']/2))
    assert wi>0 and d['top_inset']>0
    def section(r):return [(x-w,r+outer),(x+w,r+outer),(x+wi,r+inner),(x-wi,r+inner)]
    def arc(r,z,start,span):
        pts=[App.Vector(xx,rr,0) for xx,rr in section(r)]
        s=Part.Face(Part.makePolygon(pts+pts[:1])).revolve(App.Vector(),App.Vector(1,0,0),math.degrees(span))
        s.rotate(App.Vector(),App.Vector(1,0,0),math.degrees(start));s.translate(App.Vector(0,0,z));return s
    pieces=[arc(rp,center,alpha,math.pi-2*alpha),arc(rd,0,math.pi-alpha,math.pi+2*alpha)]
    ca,sa=math.cos(alpha),math.sin(alpha)
    for sign in [-1,1]:
        normal=App.Vector(0,sign*ca,sa);p0=App.Vector(x,sign*rd*ca,rd*sa)
        p1=App.Vector(x,sign*rp*ca,center+rp*sa)
        pts=[p0+App.Vector(xx,0,0)+normal*rr for xx,rr in [(-w,outer),(w,outer),(wi,inner),(-wi,inner)]]
        pieces.append(Part.Face(Part.makePolygon(pts+pts[:1])).extrude(p1-p0))
    s=pieces[0].multiFuse(pieces[1:]).removeSplitter()
    assert s.isValid() and len(s.Solids)==1,('unscored belt',s.isValid(),len(s.Solids))
    # Parameterize an entire pitch path counterclockwise from right pump tangent.
    pump_arc=rp*(math.pi-2*alpha);straight=d['straight_length'];drive_arc=rd*(math.pi+2*alpha)
    def sample(distance):
        if distance<pump_arc:
            theta=alpha+distance/rp;r=rp;z=center
        elif distance<pump_arc+straight:
            t=(distance-pump_arc)/straight
            p=App.Vector(x,-rp*ca,center+rp*sa)*(1-t)+App.Vector(x,-rd*ca,rd*sa)*t
            return p,App.Vector(0,-ca,sa)
        elif distance<pump_arc+straight+drive_arc:
            theta=math.pi-alpha+(distance-pump_arc-straight)/rd;r=rd;z=0
        else:
            t=(distance-pump_arc-straight-drive_arc)/straight
            p=App.Vector(x,rd*ca,rd*sa)*(1-t)+App.Vector(x,rp*ca,center+rp*sa)*t
            return p,App.Vector(0,ca,sa)
        normal=App.Vector(0,math.cos(theta),math.sin(theta))
        return App.Vector(x,0,z)+normal*r,normal
    cuts=[]
    for n in range(c['belt_mark_count']):
        p,normal=sample((n+.5)*c['belt_length']/c['belt_mark_count'])
        tangent=App.Vector(1,0,0).cross(normal);half=c['belt_mark_width']/2
        root=p+normal*(outer-c['belt_mark_depth'])
        pts=[root+App.Vector(xx,0,0)+tangent*tt for xx,tt in [(-w-1,-half),(w+1,-half),(w+1,half),(-w-1,half)]]
        cuts.append(Part.Face(Part.makePolygon(pts+pts[:1])).extrude(normal*(c['belt_mark_depth']+1)))
    s=s.cut(Part.makeCompound(cuts)).removeSplitter()
    d.update(outer_offset=outer,inner_offset=inner,inner_width=2*wi,
        scored_junctions=c['belt_mark_count'],physical_link_count_known=False)
    return s,d


def build(c,pc,ic,bc):
    parts={};occ=[];axes=bolt_axes(c);r=c['bolt_diameter']/2;gap=c['receiver_gap']
    # M858 enclosing cup, V rim and rear fastening web are a single casting.
    xx=c['groove_plane'];R=c['drum_radius'];root=R-c['groove_depth']
    top=c['groove_width']/2;bottom=top-c['groove_depth']*math.tan(math.radians(c['groove_angle']/2))
    web_end=c['joint_face']+c['drum_web_stock'];cover_end=web_end+c['cover_stock']
    profile=[(c['joint_face'],c['drum_web_bore']),(c['joint_face'],R),(xx-top,R),
        (xx-bottom,root),(xx+bottom,root),(xx+top,R),(c['drum_end'],R),
        (c['drum_end'],c['drum_inside']),(c['drum_inner_transition_end'],c['drum_inside']),
        (c['drum_inner_transition_start'],c['drum_groove_inside']),(web_end,c['drum_groove_inside']),
        (web_end,c['drum_web_bore'])]
    drum=revolve(profile)
    cover=xc(c['cover_radius'],web_end,cover_end).cut(xc(30,web_end-1,cover_end+1))
    receiver=revolve([(c['box_start'],0),(c['box_start'],c['box_neck_radius']),
        (c['box_transition_start'],c['box_neck_radius']),(c['box_transition_end'],c['box_outer_radius']),
        (c['box_end'],c['box_outer_radius']),(c['box_end'],0)])
    receiver=receiver.cut(rounded_head(c['head_half_width']+c['head_radial_gap'],
        c['head_corner_radius']+c['head_radial_gap'],c['box_start']-1,c['head_end']+c['head_axial_gap']))
    receiver=receiver.cut(xc(c['shaft_radius']+gap,c['head_end'],c['box_end']+1))
    for y,z in axes:
        hole=xc(r+gap,c['joint_face']-1,c['box_end']+1,y,z)
        drum=drum.cut(hole);cover=cover.cut(hole);receiver=receiver.cut(hole)
        receiver=receiver.cut(xc(c['box_nut_relief_radius'],c['bolt_seat'],c['box_end']+1,y,z))
    parts['drum']=drum.removeSplitter();parts['box']=receiver.removeSplitter()
    parts['half_cover']=cover.common(box(web_end-1,cover_end+1,-200,200,0,200)).removeSplitter()
    shaft=rounded_head(c['head_half_width'],c['head_corner_radius'],c['head_start'],c['head_end'])
    shaft_end=c['head_start']+c['shaft_length'];spline_start=shaft_end-c['spline_length']
    shaft=shaft.fuse(xc(c['shaft_radius'],c['head_end']-.1,shaft_end))
    teeth=spline(c['spline_root_radius'],c['spline_radius'],c['spline_width'],c['spline_count'],spline_start,shaft_end)
    # Clip flat-tooth corners to the transferred outside diameter.
    shaft=shaft.fuse(teeth.common(xc(c['spline_radius'],spline_start,shaft_end)))
    parts['shaft']=shaft.removeSplitter()
    parts['bolt']=hex_x(c['bolt_head_af'],-c['bolt_head_height'],0).fuse(xc(r,0,c['bolt_length'])).removeSplitter()
    parts['nut']=hex_x(c['bolt_nut_af'],0,c['bolt_nut_height']).cut(xc(r+c['nut_gap'],-1,c['bolt_nut_height']+1)).removeSplitter()
    parts['washer']=xc(c['washer_radius'],0,c['washer_stock']).cut(xc(c['washer_bore_radius'],-1,c['washer_stock']+1))
    parts['washer']=parts['washer'].cut(box(-1,c['washer_stock']+1,0,c['washer_radius']+1,-c['washer_split']/2,c['washer_split']/2)).removeSplitter()
    parts['belt'],bd=belt(c,pc)
    revised=revised_flange(c,ic,bc)
    def add(name,key,xyz=(0,0,0),angle=0):occ.append(dict(name='ClutchDrive_'+name,key=key,xyz=list(xyz),angle=angle))
    for key in ['drum','box','shaft','belt']:add(key,key)
    add('HalfCover1','half_cover');add('HalfCover2','half_cover',angle=180)
    for n,(y,z) in enumerate(axes,1):
        add(f'Set{n}_Bolt','bolt',(c['flange_back'],y,z))
        add(f'Set{n}_Washer','washer',(c['bolt_seat'],y,z))
        add(f'Set{n}_Nut','nut',(c['bolt_seat']+c['washer_stock'],y,z))
    for key,s in {**parts,'revised_flange':revised}.items():
        assert s.isValid() and len(s.Solids)==1,(key,s.isValid(),len(s.Solids))
    return parts,occ,revised,dict(belt=bd,bolt_axes=axes,cover_limits=[web_end,cover_end],
        shaft_end=shaft_end,spline_start=spline_start,
        bolt_protrusion=c['flange_back']+c['bolt_length']-c['bolt_seat']-c['washer_stock']-c['bolt_nut_height'])
