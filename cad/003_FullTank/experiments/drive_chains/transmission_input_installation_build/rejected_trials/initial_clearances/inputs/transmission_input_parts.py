"""Nominal input bearing, housing and coupling geometry; dimensions in millimetres.

Bearing race envelopes are printed SNL dimensions. Race tapers, roller count,
fits and casting profiles are explicit reconstruction assumptions. Local X is
the pinion axis, increasing from the bevel centre toward the coupling.
"""
import math
import FreeCAD as App
import Part
from transmission_core_parts import box, spline_envelope
from transmission_stud_parts import hex_x


def cylinder(radius, low, high):
    return Part.makeCylinder(radius, high-low, App.Vector(low,0,0), App.Vector(1,0,0))


def ring(outer, inner, low, high):
    return cylinder(outer,low,high).cut(cylinder(inner,low-1,high+1))


def revolve(points):
    vertices=[App.Vector(x,r,0) for x,r in points]
    return Part.Face(Part.makePolygon(vertices+vertices[:1])).revolve(App.Vector(),App.Vector(1,0,0),360)


def spline(root, tip, width, count, low, high):
    s=spline_envelope(root,tip,width,count,low,high)
    s.rotate(App.Vector(),App.Vector(0,0,1),-90)
    return s


def tapered_bearing(c):
    """One shared cone/cup assembly, small end X0, large cone end X=B.

    Nominal race and roller generators meet at one virtual apex. Roller radii
    are reduced by a stated inspection clearance; no interference or load fit
    is claimed. The cage is a perforated conical shell, not a filled envelope.
    """
    A=c['apex_distance'];B=c['cone_width'];C=c['cup_width'];T=c['bearing_width']
    small=B-T;large=small+C
    ai=math.atan(c['inner_race_radius_at_zero']/A)
    ao=math.atan(c['outer_race_radius_at_zero']/A)
    theta=(ai+ao)/2;gamma=(ao-ai)/2
    ri=lambda x:(A+x)*math.tan(ai)
    ro=lambda x:(A+x)*math.tan(ao)
    rc=lambda x:(A+x)*math.tan(theta)
    cone=revolve([(0,c['bore']/2),(B,c['bore']/2),(B,c['large_rib_radius']),
        (c['large_rib_start'],c['large_rib_radius']),(c['large_rib_start'],ri(c['large_rib_start'])),
        (c['small_rib_end'],ri(c['small_rib_end'])),(c['small_rib_end'],c['small_rib_radius']),(0,c['small_rib_radius'])])
    cup=revolve([(small,ro(small)),(small,c['outside']/2),(large,c['outside']/2),(large,ro(large))])
    x0,x1=c['roller_center_limits'];t0=(A+x0)/math.cos(theta);t1=(A+x1)/math.cos(theta)
    axis=App.Vector(math.cos(theta),math.sin(theta),0)
    origin=App.Vector(x0,rc(x0),0)
    radii=[t*math.tan(gamma) for t in [t0,t1]]
    roller=Part.makeCone(radii[0]-c['race_clearance'],radii[1]-c['race_clearance'],t1-t0,origin,axis)
    ca,cb=c['cage_limits'];wall=c['cage_half_stock']
    cage=revolve([(ca,rc(ca)-wall),(ca,rc(ca)+wall),(cb,rc(cb)+wall),(cb,rc(cb)-wall)])
    cutters=[]
    for n in range(c['roller_count']):
        gap=c['cage_clearance']
        tool=Part.makeCone(radii[0]+gap-gap*math.tan(gamma),radii[1]+gap+gap*math.tan(gamma),
            t1-t0+2*gap,origin-axis*gap,axis)
        tool.rotate(App.Vector(),App.Vector(1,0,0),n*360/c['roller_count']);cutters.append(tool)
    cage=cage.cut(Part.makeCompound(cutters)).removeSplitter()
    shapes=dict(inner_race=cone,cup=cup,cage=cage,roller=roller)
    for k,s in shapes.items():assert s.isValid() and len(s.Solids)==1,k
    return shapes,dict(cone_limits=[0,B],cup_limits=[small,large],apex_mm=[-A,0,0],
        inner_race_angle_degrees=math.degrees(ai),outer_race_angle_degrees=math.degrees(ao),
        roller_axis_angle_degrees=math.degrees(theta),roller_half_angle_degrees=math.degrees(gamma),
        nominal_roller_end_radii=radii,roller_axis_length=t1-t0,roller_count=c['roller_count'])


def input_stack(c,b,old_shaft,old_cover):
    shoulder=c['pinion_shoulder'];small1=shoulder+b['cone_width']
    small2=small1+c['cone_front_gap'];coupling_seat=small2+b['cone_width']
    cup_lo,cup_hi=b['cone_width']-b['bearing_width'],b['cone_width']-b['bearing_width']+b['cup_width']
    cup1=[small1-cup_hi,small1-cup_lo];cup2=[small2+cup_lo,small2+cup_hi]
    spline_start=coupling_seat
    # Retain the accepted pinion teeth exactly; replace only its shaft extension.
    shaft=old_shaft.common(box(-500,shoulder,-200,200,-200,200))
    shaft=shaft.fuse(cylinder(c['journal_radius'],shoulder-.1,spline_start))
    shaft=shaft.fuse(spline(c['spline_root'],c['spline_tip'],c['spline_width'],c['spline_count'],spline_start-.1,c['thread_start']))
    shaft=shaft.fuse(cylinder(c['thread_radius'],c['thread_start']-.1,c['shaft_end']))
    shaft=shaft.fuse(cylinder(c['shoulder_radius'],c['shoulder_start'],shoulder))
    hole=Part.makeCylinder(c['cotter_diameter']/2,2*c['thread_radius']+2,
        App.Vector(c['cotter_station'],-c['thread_radius']-1,0),App.Vector(0,1,0))
    shaft=shaft.cut(hole).removeSplitter()
    # Outer-race distance piece, with a separately modeled 13-leaf shim pack.
    spacer_start=cup1[1];spacer_end=cup2[0]-c['spacer_shim_count']*c['spacer_shim_stock']
    spacer=revolve([(spacer_start,c['spacer_bore']),(spacer_start,c['spacer_outer']-1),
        (spacer_start+1,c['spacer_outer']),(spacer_end-1,c['spacer_outer']),
        (spacer_end,c['spacer_outer']-1),(spacer_end,c['spacer_bore'])])
    shim=ring(c['spacer_outer'],c['spacer_bore'],0,c['spacer_shim_stock'])
    # Housing pilot fits the revised cover boss. The flange/shim joint has its
    # own stock; bearing dimensions do not get reduced to fit the old R72 bore.
    house=cylinder(c['housing_radius'],shoulder,c['housing_end'])
    flange_start=c['cover_end']+c['flange_shim_count']*c['flange_shim_stock']
    house=house.fuse(cylinder(c['flange_radius'],flange_start,flange_start+c['flange_stock']))
    house=house.fuse(cylinder(c['gland_flange_radius'],c['housing_end']-c['gland_flange_stock'],c['housing_end']))
    house=house.cut(cylinder(c['housing_large_end_bore'],shoulder-1,cup1[0]))
    house=house.cut(cylinder(b['outside']/2+c['cup_housing_gap'],cup1[0],c['disk_end']))
    house=house.cut(cylinder(c['packing_radius']+c['gland_housing_gap'],c['disk_end'],c['housing_end']+1))
    flange_shim=ring(c['flange_radius'],c['housing_radius']+c['pilot_gap'],0,c['flange_shim_stock'])
    disk=ring(c['disk_outer'],c['disk_nose_bore'],cup2[1],c['disk_front'])
    disk=disk.fuse(ring(c['disk_outer'],c['coupling_radius']+c['seal_running_gap'],c['disk_front'],c['disk_end']))
    felt=ring(c['packing_radius'],c['coupling_radius'],c['disk_end'],c['packing_end'])
    gland=ring(c['packing_radius'],c['coupling_radius']+c['seal_running_gap'],c['packing_end'],c['gland_end'])
    gland=gland.fuse(ring(c['gland_flange_radius'],c['coupling_radius']+c['seal_running_gap'],c['gland_end']-c['gland_flange_stock'],c['gland_end']))
    coupling=cylinder(c['coupling_radius'],coupling_seat,c['coupling_end'])
    coupling=coupling.fuse(cylinder(c['coupling_flange_radius'],c['coupling_flange_start'],c['coupling_end']))
    coupling=coupling.cut(spline(c['spline_root']+c['spline_gap'],c['spline_tip']+c['spline_gap'],
        c['spline_width']+2*c['spline_gap'],c['spline_count'],coupling_seat-1,c['washer_start']))
    coupling=coupling.cut(cylinder(c['coupling_nut_recess'],c['washer_start'],c['coupling_end']+1))
    # Coupling-to-drive flange pattern is inferred pending the matching shaft.
    for n in range(c['coupling_bolt_count']):
        angle=2*math.pi*n/c['coupling_bolt_count'];tool=cylinder(c['coupling_bolt_radius'],c['coupling_flange_start']-1,c['coupling_end']+1)
        tool.translate(App.Vector(0,c['coupling_bolt_circle']*math.cos(angle),c['coupling_bolt_circle']*math.sin(angle)));coupling=coupling.cut(tool)
    cover=old_cover.fuse(cylinder(c['cover_boss_radius'],c['cover_boss_start'],c['cover_end']))
    cover=cover.cut(cylinder(c['housing_radius']+c['pilot_gap'],shoulder,c['cover_end']+1))
    # Keep the pinion shoulder clear on the inside of the boss.
    cover=cover.cut(cylinder(c['shoulder_radius']+c['pilot_gap'],c['cover_boss_start']-1,shoulder))
    for n in range(2):
        pos=App.Vector(0,0,(-1 if n else 1)*c['mount_bolt_circle'])
        tool=cylinder(c['mount_bolt_radius']+c['bolt_gap'],c['cover_end']-c['mount_embed'],flange_start+c['flange_stock']+1);tool.translate(pos)
        cover=cover.cut(tool);house=house.cut(tool)
        h=cylinder(c['mount_bolt_radius']+c['bolt_gap'],-1,c['flange_shim_stock']+1);h.translate(pos);flange_shim=flange_shim.cut(h)
    for n in range(4):
        angle=math.pi/4+n*math.pi/2;tool=cylinder(c['gland_bolt_radius']+c['bolt_gap'],c['housing_end']-c['gland_flange_stock']-1,c['gland_end']+1)
        tool.translate(App.Vector(0,c['gland_bolt_circle']*math.cos(angle),c['gland_bolt_circle']*math.sin(angle)))
        house=house.cut(tool);gland=gland.cut(tool)
    washer=ring(c['washer_radius'],c['thread_radius']+c['spline_gap'],c['washer_start'],c['nut_start'])
    shapes=dict(shaft=shaft,cover=cover,housing=house,coupling=coupling,spacer=spacer,spacer_shim=shim,
        flange_shim=flange_shim,disk=disk,felt=felt,gland=gland,washer=washer)
    shapes={k:s.removeSplitter() for k,s in shapes.items()}
    for k,s in shapes.items():assert s.isValid() and len(s.Solids)==1,k
    return shapes,dict(bearing_small_end_stations=[small1,small2],cup_limits=[cup1,cup2],
        coupling_seat=coupling_seat,spacer_limits=[spacer_start,spacer_end],flange_start=flange_start,
        source_conflicts=['M249 installed quantity one in SNL112 versus two in SNL134 and HB205; one outer-race spacer is provisional.',
            'MX25 nut printed as one inch despite a half-inch stud; fastener reconstruction pending.',
            'Plate22 coupling is a detached detail; its main-view endpoint cannot constrain complete shaft length.'])


def retention(c):
    """Plain thread envelopes and an unspread split pin; formed ends pending."""
    nut=hex_x(c['nut_af'],c['nut_start'],c['nut_crown_start']).fuse(
        cylinder(c['nut_crown_radius'],c['nut_crown_start'],c['nut_end']))
    nut=nut.cut(cylinder(c['thread_radius']+c['spline_gap'],c['nut_start']-1,c['nut_end']+1))
    for a in [0,60,120]:
        cut=box(c['nut_crown_start'],c['nut_end']+1,-50,50,-c['cotter_slot_width']/2,c['cotter_slot_width']/2)
        cut.rotate(App.Vector(),App.Vector(1,0,0),a);nut=nut.cut(cut)
    half=c['cotter_leg_spacing']/2;wire=(c['cotter_diameter']-c['cotter_leg_spacing'])/2
    start=c['cotter_under_eye'];end=start+c['cotter_length'];pieces=[]
    for sign in [-1,1]:
        pieces.append(Part.makeCylinder(wire,c['cotter_length'],App.Vector(c['cotter_station'],start,sign*half),App.Vector(0,1,0)))
    points=[App.Vector(c['cotter_station'],start,-half),App.Vector(c['cotter_station'],start-2,-c['cotter_eye_radius'])]
    points += [App.Vector(c['cotter_station'],start-2-c['cotter_eye_radius']*math.sin(a),c['cotter_eye_radius']*math.cos(a))
        for a in [math.pi-i*math.pi/24 for i in range(1,25)]]
    points.append(App.Vector(c['cotter_station'],start,half))
    for a,b in zip(points,points[1:]):
        delta=b-a;pieces.append(Part.makeCylinder(wire,delta.Length,a,delta))
    pieces += [Part.makeSphere(wire,p) for p in points]
    cotter=pieces[0].multiFuse(pieces[1:]).removeSplitter()
    bolt=cylinder(c['gland_bolt_radius'],c['gland_bolt_start'],c['gland_bolt_end'])
    bolt=bolt.fuse(hex_x(c['gland_bolt_head_af'],c['gland_bolt_start']-c['gland_bolt_head_height'],c['gland_bolt_start']))
    gland_nut=hex_x(c['gland_nut_af'],0,c['gland_nut_height']).cut(cylinder(c['gland_bolt_radius']+c['bolt_gap'],-1,c['gland_nut_height']+1))
    shapes=dict(nut=nut.removeSplitter(),cotter=cotter,gland_bolt=bolt.removeSplitter(),gland_nut=gland_nut.removeSplitter())
    for k,s in shapes.items():assert s.isValid() and len(s.Solids)==1,k
    return shapes
