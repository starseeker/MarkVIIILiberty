"""Provisional complete clutch-stop linkage with source-sized retaining hardware.

Definition frames are either stated local axes or TransmissionCore coordinates.
The right-angle linkage, carrier and shared mounting are engineering hypotheses.
"""
import math
import FreeCAD as App
import Part
from clutch_support_parts import hex_z
from clutch_cone_parts import cap, ztool
from front_clutch_parts import spring
from transmission_input_installation_parts import formed_pin

V = App.Vector
X, Y, Z = V(1,0,0), V(0,1,0), V(0,0,1)

def moved(shape, xyz=V(), rotation=None):
    result = shape.copy()
    result.Placement = App.Placement(xyz, rotation or App.Rotation()).multiply(result.Placement)
    return result

def cyl(r, length, start=V(), axis=Z):
    return Part.makeCylinder(r, length, start, axis)

def polygon(points, extrusion):
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(extrusion)

def nut(diameter, af, height):
    return hex_z(af, 0, height).cut(cyl(diameter/2+.1,height+2,V(0,0,-1))).removeSplitter()

def cotter(diameter, length, radius, head_gap=.8):
    controls=dict(cotter_center_spacing=diameter*.52,cotter_diameter=diameter,
        crown_radius=radius,cotter_head_gap=head_gap,cotter_exit_gap=.8,
        cotter_bend_radius=2,cotter_bend_angle=35,cotter_length=length,
        cotter_eye_radius=3,cotter_eye_rise=2,cotter_eye_join_overlap=.03)
    return formed_pin(controls)

def parts(c, old, band_controls, bd, support_controls):
    p, occ, joints = {}, [], []
    def add(key, name, xyz=V(), rotation=None, assembly='ClutchStopLinkage'):
        occ.append(dict(key=key,name='ClutchBrake_'+name,xyz=list(xyz),
            rotation=list((rotation or App.Rotation()).Q),assembly=assembly))
    br=bd['band_inner_radius']; outer=bd['band_outer_radius']
    x0,x1=bd['band_axial_extent'];width=x1-x0;cx=band_controls['band_center_x']
    start=bd['arc_start_rad'];end=bd['arc_end_rad'];stock=c['anchor_stock']
    def radial(a):return V(0,math.cos(a),math.sin(a))
    def at(r,a,x=x0):return V(x,0,0)+radial(a)*r
    def arc(r,a,b):return Part.Arc(at(r,a),at(r,(a+b)/2),at(r,b)).toShape()
    finish=start+math.radians(c['anchor_sweep_deg'])
    shoe=Part.Face(Part.Wire([arc(outer,start,finish),Part.makeLine(at(outer,finish),at(outer+stock,finish)),
        arc(outer+stock,finish,start),Part.makeLine(at(outer+stock,start),at(outer,start))])).extrude(X*width)

    # The anchor bends outward to the shared two-bolt mounting plate. Its
    # unprinted bend/profile is represented by a connected constant-stock web.
    root=at(outer+stock/2,finish-.04,cx)
    tip=V(sum(c['mount_x'])/2,c['mount_head_y']+c['mount_grip']+stock/2,c['mount_z']+18)
    direction=tip-root;direction.normalize();normal=V(0,-direction.z,direction.y)
    normal.normalize()
    sections=[]
    for center,w in [(root,width),(tip,40)]:
        pts=[center-X*w/2-normal*stock/2,center+X*w/2-normal*stock/2,
             center+X*w/2+normal*stock/2,center-X*w/2+normal*stock/2]
        sections.append(Part.makePolygon(pts+[pts[0]]))
    web=Part.makeLoft(sections,True,False)
    my=c['mount_head_y']+c['mount_grip']; mz=c['mount_z'];xa=min(c['mount_x'])-20;xb=max(c['mount_x'])+20
    foot=Part.makeBox(xb-xa,stock,40,V(xa,my,mz-20))
    anchor=shoe.fuse(web).fuse(foot).removeSplitter()

    band=old['ClutchStopBand_band'].copy();lining=old['ClutchStopBand_lining'].copy()
    r=c['anchor_rivet_diameter']/2;seat=br+c['spotface'];tailseat=outer+stock-c['spotface'];grip=tailseat-seat
    tailvol=math.pi*r*r*(c['anchor_rivet_blank_length']-grip)
    lo,hi=0.,2*c['rivet_tail_radius']
    for _ in range(70):
        h=(lo+hi)/2;vol=math.pi*h*(3*c['rivet_tail_radius']**2+h*h)/6
        if vol<tailvol:lo=h
        else:hi=h
    tailh=(lo+hi)/2
    head=cap(c['rivet_head_radius'],c['rivet_head_height']);head.rotate(V(),X,180)
    p['anchor_rivet']=head.fuse(cyl(r,grip)).fuse(cap(c['rivet_tail_radius'],tailh,grip)).removeSplitter()
    for da in c['anchor_rivet_angles_deg']:
        angle=start+math.radians(da);n=radial(angle);rot=App.Rotation(Z,n)
        for dx in c['anchor_rivet_x_offsets']:
            base=at(seat,angle,cx+dx);name='AnchorRivet%d'%(len(joints)+1)
            add('anchor_rivet',name,base,rot,'ClutchStopAnchor')
            dr=r+c['rivet_clearance'];hr=c['rivet_head_radius']+c['head_clearance'];tr=c['rivet_tail_radius']+c['head_clearance']
            tool=ztool([(0,-8),(hr,-8),(hr,0),(dr,0),(dr,grip),(tr,grip),(tr,grip+tailh+1),(0,grip+tailh+1)])
            tool=moved(tool,base,rot)
            anchor=anchor.cut(tool);band=band.cut(tool);lining=lining.cut(tool)
            joints.append(dict(name='ClutchBrake_'+name,base=list(base),radial=list(n),
                angle_rad=angle,grip=grip,tail_height=tailh,tail_volume=tailvol))
    p['anchor']=anchor.removeSplitter();add('anchor','Anchor',assembly='ClutchStopAnchor')

    # Band pin and eyebolt. The bolt axis follows the free-end tangent,
    # pointing across and below the opening, toward the fixed end.
    eye=V(*bd['eye_axis_point']);axis=V(0,-math.sin(end),math.cos(end));normal=X.cross(axis)
    frame=App.Rotation(X,axis,normal,'XYZ')
    pinstart=-width/2;pinlength=c['band_pin_length'];pr=c['band_pin_radius'];ps=c['band_pin_cotter_station']
    pin=cyl(pr,pinlength,V(pinstart,0,0),X).fuse(cyl(pr+3,4,V(pinstart-4,0,0),X))
    pin=pin.cut(cyl(3.175/2+.1,2*pr+2,V(pinstart+ps,-pr-1,0),Y)).removeSplitter()
    p['band_pin']=pin;add('band_pin','BandPin',eye)
    p['band_cotter'],bcd=cotter(3.175,22.225,pr)
    add('band_cotter','BandCotter',eye+V(pinstart+ps,0,0))
    t=c['eye_thickness'];er=c['eye_outer_radius'];stem_r=c['eyebolt_diameter']/2
    eb=cyl(er,t,V(-t/2,0,0),X).fuse(cyl(stem_r,c['eyebolt_stem_length']-5,V(0,5,0),Y))
    eb=eb.cut(cyl(pr+.05,t+2,V(-t/2-1,0,0),X)).removeSplitter()
    p['eyebolt']=eb;add('eyebolt','Eyebolt',eye,frame)
    # Continue the open clevis throat along the eyebolt shank beyond the
    # original circular eye relief, preserving both pin-bearing ears.
    band=band.cut(cyl(stem_r+.15,30,eye+axis*2,axis)).removeSplitter()
    output=eye+axis*c['eyebolt_bell_station'];pivot=output+X*c['bell_arm_x']
    input_offset=(c['rod_y']-pivot.y)/axis.y;input_point=pivot+axis*input_offset
    rod_eye=V(c['rod_pin_x'],c['rod_y'],input_point.z)

    # Bell crank is constructed in a plane tangent to the opening: local X
    # receives the stop rod and local Y receives the spring-loaded eyebolt.
    ws=c['bell_web_stock'];arm=c['bell_arm_x'];iw=c['bell_input_width'];ow=c['bell_output_width']
    bell=cyl(c['bell_hub_radius'],ws,V(0,0,-ws/2))
    bell=bell.fuse(Part.makeBox(arm,16,ws,V(-arm,-8,-ws/2)))
    bell=bell.fuse(Part.makeBox(16,input_offset,ws,V(-8,0,-ws/2)))
    bell=bell.fuse(cyl(15,ow,V(-arm,-ow/2,0),Y)).fuse(cyl(16,iw,V(-iw/2,input_offset,0),X))
    bell=bell.cut(cyl(c['bell_receiver_radius'],ws+2,V(0,0,-ws/2-1)))
    bell=bell.cut(cyl(stem_r+.15,ow+2,V(-arm,-ow/2-1,0),Y))
    bell=bell.cut(cyl(c['rod_diameter']/2+.15,iw+2,V(-iw/2-1,input_offset,0),X)).removeSplitter()
    p['bell']=bell;add('bell','BellCrank',pivot,frame)

    z_to_axis=App.Rotation(Z,axis)
    p['eye_adjuster']=nut(c['eyebolt_diameter'],19.05,c['eyebolt_adjuster_height'])
    p['eye_plain_nut']=nut(c['eyebolt_diameter'],19.05,c['eyebolt_plain_nut_height'])
    p['eye_washer']=cyl(c['eyebolt_washer_od']/2,c['eyebolt_washer_stock']).cut(cyl(c['eyebolt_washer_id']/2,c['eyebolt_washer_stock']+2,V(0,0,-1)))
    first=c['eye_first_nut_station'];adjust=first+c['eyebolt_plain_nut_height'];wash=adjust+c['eyebolt_adjuster_height']
    spring_start=wash+c['eyebolt_washer_stock'];front=c['eyebolt_bell_station']-ow/2
    spring_end=front-c['eyebolt_washer_stock'];back=c['eyebolt_bell_station']+ow/2
    for key,name,station in [('eye_plain_nut','EyeJam1',first),('eye_adjuster','EyeAdjust1',adjust),
        ('eye_washer','EyeWasher1',wash),('eye_washer','EyeWasher2',spring_end),
        ('eye_adjuster','EyeAdjust2',back),('eye_plain_nut','EyeJam2',back+c['eyebolt_adjuster_height'])]:
        add(key,name,eye+axis*station,z_to_axis)
    sc=dict(spring_turns=c['spring_turns'],spring_end_turns=1,spring_wire_radius=c['spring_wire_radius'],
        spring_inside_radius=c['spring_mean_radius']-c['spring_wire_radius'],spring_rear_seat=0,
        spring_length=spring_end-spring_start,spring_transition_turns=.5,spring_end_pitch=c['spring_end_pitch'],
        spring_end_grind_fraction=.65,spring_samples_per_turn=32)
    p['spring'],spine,sd=spring(sc);add('spring','Spring',eye+axis*spring_start,App.Rotation(X,axis))

    # M4151 is represented as a forged fork and an integral threaded stem.
    gap=c['rod_fork_gap'];cheek=c['rod_fork_stock'];fr=c['rod_fork_radius'];half=gap/2+cheek
    fork=cyl(fr,2*half,V(0,-half,0),Y).fuse(Part.makeBox(42,2*half,2*fr,V(-42,-half,-fr)))
    fork=fork.cut(Part.makeBox(44,gap,2*fr+2,V(-28,-gap/2,-fr-1)))
    fork=fork.cut(cyl(c['rod_pin_radius']+.1,2*half+2,V(0,-half-1,0),Y))
    nh=c['rod_nut_height'];rod_end=input_point.x-iw/2-2*nh-4
    rod=fork.fuse(cyl(c['rod_diameter']/2,rod_eye.x-32-rod_end,V(rod_end-rod_eye.x,0,0),X)).removeSplitter()
    p['rod']=rod;add('rod','StopRod',rod_eye)
    p['rod_nut']=nut(c['rod_diameter'],c['rod_nut_af'],nh)
    for k,xx in enumerate([input_point.x-iw/2-2*nh,input_point.x-iw/2-nh,input_point.x+iw/2,input_point.x+iw/2+nh],1):
        add('rod_nut','RodNut%d'%k,V(xx,input_point.y,input_point.z),App.Rotation(Z,X))
    rp=c['rod_pin_radius'];rl=c['rod_pin_length'];rs=c['rod_pin_cotter_station']
    rodpin=cyl(rp,rl,V(0,-half,0),Y).fuse(cyl(rp+3,4,V(0,-half-4,0),Y))
    rodpin=rodpin.cut(cyl(3.175/2+.1,2*rp+2,V(-rp-1,-half+rs,0),X)).removeSplitter()
    p['rod_pin']=rodpin;add('rod_pin','RodPin',rod_eye)
    p['rod_cotter'],rcd=cotter(3.175,25.4,rp)
    add('rod_cotter','RodCotter',rod_eye+V(0,-half+rs,0),App.Rotation(Z,-90))
    lever=old['ClutchThrowout_LeftLever'].cut(cyl(rp+.1,50,rod_eye-Y*25,Y)).removeSplitter()

    # The carrier shares the two catalogue anchor bolts. Cast receiving lugs
    # are added to SH953A; no extra mounting fasteners are silently invented.
    carrier=Part.makeBox(xb+20-xa,c['carrier_stock'],40,V(xa,my+stock,mz-20))
    bearing_low=-ws/2-.2-c['carrier_bearing_length'];bearing_high=-ws/2-.2
    boss=cyl(20,c['carrier_bearing_length'],pivot+normal*bearing_low,normal)
    # Rise outside the receiving lugs, then run above them to the pivot.
    # This also separates the carrier from the adjacent anchor's formed web.
    a=V(xb+10,my+stock+c['carrier_stock']/2,mz+55)
    upright=Part.makeBox(16,c['carrier_stock'],65,V(xb+2,my+stock,mz-10))
    b=pivot+normal*(bearing_low+5)
    tangent=b-a;tangent.normalize();across=V(0,-tangent.z,tangent.y)
    across.normalize()
    sections=[]
    for center,w in [(a,16),(b,32)]:
        pts=[center-X*w/2-across*c['carrier_stock']/2,center+X*w/2-across*c['carrier_stock']/2,
             center+X*w/2+across*c['carrier_stock']/2,center-X*w/2+across*c['carrier_stock']/2]
        sections.append(Part.makePolygon(pts+[pts[0]]))
    connector=Part.makeLoft(sections,True,False)
    carrier=carrier.fuse(upright).fuse(connector).fuse(boss)
    carrier=carrier.cut(cyl(c['bell_receiver_radius'],50,pivot-normal*35,normal)).removeSplitter()
    p['carrier']=carrier;add('carrier','Carrier')
    left=old['ClutchSupport_LeftBracket'].copy();ft=support_controls['floor_top']
    mt=[]
    p['mount_bolt']=cyl(c['mount_diameter']/2,c['mount_length']).fuse(hex_z(c['mount_head_af'],-c['mount_head_height'],c['mount_head_height'])).removeSplitter()
    p['mount_nut']=nut(c['mount_diameter'],19.05,c['mount_nut_height'])
    lock=cyl(12,c['mount_lock_stock']).cut(cyl(c['mount_diameter']/2+.15,c['mount_lock_stock']+2,V(0,0,-1)))
    lock=lock.cut(Part.makeBox(15,1.2,c['mount_lock_stock']+2,V(0,-.6,-1))).removeSplitter();p['mount_lock']=lock
    for k,x in enumerate(c['mount_x'],1):
        left=left.fuse(cyl(20,c['mount_grip'],V(x,c['mount_head_y'],mz),Y))
        left=left.fuse(Part.makeBox(30,12,mz-ft+10,V(x-15,c['mount_head_y']+14,ft)))
        cutter=cyl(c['mount_diameter']/2+.15,80,V(x,c['mount_head_y']-1,mz),Y)
        left=left.cut(cutter);p['anchor']=p['anchor'].cut(cutter);p['carrier']=p['carrier'].cut(cutter)
        seat=my+stock+c['carrier_stock'];origin=V(x,c['mount_head_y'],mz)
        add('mount_bolt','AnchorBolt%d'%k,origin,App.Rotation(Z,Y),'ClutchStopAnchor')
        add('mount_lock','AnchorLock%d'%k,V(x,seat,mz),App.Rotation(Z,Y),'ClutchStopAnchor')
        add('mount_nut','AnchorNut%d'%k,V(x,seat+c['mount_lock_stock'],mz),App.Rotation(Z,Y),'ClutchStopAnchor')
        mt.append(dict(axis_start=list(origin),axis=[0,1,0],clamped_grip=seat-c['mount_head_y']))

    # M4165 shoulder pin, source5/8 crown nut and its single5/32x1 split pin.
    tr=c['bell_pin_thread_diameter']/2;thread_start=ws/2+.2;thread_end=thread_start+c['bell_nut_height']+3
    pin=cyl(c['bell_pivot_radius'],thread_start-bearing_low,V(0,0,bearing_low))
    pin=pin.fuse(cyl(c['bell_pin_head_radius'],c['bell_pin_head_height'],V(0,0,bearing_low-c['bell_pin_head_height'])))
    pin=pin.fuse(cyl(tr,thread_end-thread_start,V(0,0,thread_start)))
    station=c['bell_cotter_station'];cr=c['bell_nut_crown_radius'];cd=c['bell_cotter_diameter']
    pin=pin.cut(cyl(cd/2+.1,2*tr+2,V(-tr-1,0,station),X)).removeSplitter()
    p['bell_pin']=pin;add('bell_pin','BellPin',pivot,frame)
    nh=c['bell_nut_height'];slots=c['bell_nut_slot_depth']
    crown=hex_z(c['bell_nut_af'],0,nh-slots).fuse(cyl(cr,slots,V(0,0,nh-slots)))
    crown=crown.cut(cyl(tr+.1,nh+2,V(0,0,-1)))
    for a in [0,60,120]:
        cut=Part.makeBox(30,cd+.25,slots+1,V(-15,-(cd+.25)/2,nh-slots));cut.rotate(V(),Z,a)
        crown=crown.cut(cut)
    p['bell_nut']=crown.removeSplitter();add('bell_nut','BellNut',pivot+normal*thread_start,frame)
    p['bell_cotter'],ccd=cotter(cd,c['bell_cotter_length'],cr,1.2)
    # Y-running split pin is rotated to the crown's X slot in its local frame.
    add('bell_cotter','BellCotter',pivot+normal*station,frame.multiply(App.Rotation(Z,-90)))

    revisions={'ClutchStopBand_band':band,'ClutchStopBand_lining':lining,
        'ClutchSupport_LeftBracket':left,'ClutchThrowout_LeftLever':lever}
    p={k:s.removeSplitter() for k,s in p.items()}
    revisions={k:s.removeSplitter() for k,s in revisions.items()}
    for key,s in list(p.items())+list(revisions.items()):
        assert s.isValid() and len(s.Solids)==1,(key,s.isValid(),len(s.Solids))
    assert len(occ)==35,len(occ)
    details=dict(eye=list(eye),eye_axis=list(axis),bell_pivot=list(pivot),bell_normal=list(normal),
        bell_input=list(input_point),bell_input_offset=input_offset,rod_eye=list(rod_eye),
        rod_end_x=rod_end,rod_fork_outer_half_width=half,rivet_joints=joints,rivet_grip=grip,
        mounts=mt,spring_controls=sc,spring=sd,spring_stations=[spring_start,spring_end],
        bell_carrier_seats=[bearing_low,bearing_high],bell_pin_thread_start=thread_start,
        cotters=dict(band=bcd,rod=rcd,bell=ccd),
        mounting_hypothesis='Anchor and carrier share two source bolts on revised left bracket lugs; exact attachment and crank orientation unprinted.',
        historical_fit_qualified=False,complete_brake_inventory_provisional=True)
    return p,occ,revisions,details,spine
