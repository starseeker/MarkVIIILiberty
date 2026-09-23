"""Source-sized release bearings and explicitly approximate shaft/fork interfaces."""
import math
import FreeCAD as App
import Part

V = App.Vector
Y = V(0, 1, 0)


def cylinder(radius, start, length, x=0, z=0):
    return Part.makeCylinder(radius, length, V(x, start, z), Y)


def annulus(outer, inner, start, length):
    return cylinder(outer, start, length).cut(cylinder(inner, start-1, length+2))


def hex_nut(diameter, across_flats, height):
    rr = across_flats / math.sqrt(3)
    pts = [V(rr*math.cos(j*math.pi/3), 0, rr*math.sin(j*math.pi/3)) for j in range(6)]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(Y*height).cut(cylinder(diameter/2+.1, -1, height+2))


def web_polygon(points, width):
    pts = [V(x, -width/2, z) for x, z in points]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(Y*width)


def parts(c):
    """Definitions have identity placement. Occurrences are parent-relative rigid frames."""
    p, occ = {}, []
    def add(key, name, xyz, rotation=None, assembly='ClutchThrowout'):
        occ.append(dict(key=key, name='ClutchThrowout_'+name, xyz=xyz,
                        rotation=rotation or [0, 0, 0, 1], assembly=assembly))
    br=c['ball_radius']; pitch=c['ball_pitch_radius']; row=c['ball_row_offset']
    width=c['bearing_width']; outer=c['bearing_diameter']/2; bore=c['bearing_bore']/2
    spherical_radius=math.hypot(pitch,row)+br+c['race_clearance']
    # Align the spherical surface pole axis with the bearing axis. A transverse
    # sphere parameterization produced defective STEP trims in OCC7.8.0.
    p['bearing_outer']=cylinder(outer,-width/2,width).cut(Part.makeSphere(spherical_radius,V(0,0,0),Y))
    inner=annulus(c['inner_shoulder_radius'],bore,-width/2,width)
    for y in [-row,row]:
        inner=inner.cut(Part.makeTorus(pitch,br+c['race_clearance'],V(0,y,0),Y))
    p['bearing_inner']=inner
    p['bearing_ball']=Part.makeSphere(br)
    cage=annulus(c['cage_outer_radius'],c['cage_inner_radius'],-c['cage_half_width'],2*c['cage_half_width'])
    ball_centers=[]
    for j,y in enumerate([-row,row]):
        for k in range(c['balls_per_row']):
            t=2*math.pi*k/c['balls_per_row']
            v=V(pitch*math.cos(t),y,pitch*math.sin(t));ball_centers.append(list(v))
            radial=V(math.cos(t),0,math.sin(t))
            # Inferred radial cylindrical windows; retain material bridges at
            # the axial rims and avoid coincident spherical trimming seams.
            cage=cage.cut(Part.makeCylinder(br+c['cage_ball_clearance'],12,v-radial*6,radial))
    p['bearing_cage']=cage.removeSplitter()
    # Cupped guards clamp only the inner ring. The larger diameter is relieved
    # away from the outer race, so it does not lock the rolling outer ring.
    p['bearing_washer']=annulus(c['washer_seat_radius'],c['washer_bore_radius'],0,c['washer_thickness']).fuse(
        annulus(c['washer_outer_radius'],c['washer_bore_radius'],c['washer_outer_relief'],c['washer_thickness']-c['washer_outer_relief'])).removeSplitter()
    p['retainer_washer']=annulus(c['washer_seat_radius'],15.875/2+.1,0,3.175)
    p['pin_nut']=hex_nut(15.875,23.8125,14.2875)
    lock=annulus(14.3,15.875/2+.15,0,3.5)
    p['pin_lockwasher']=lock.cut(Part.makeBox(20,5,.8,V(0,-.5,-.4)))
    # Positive-side pin is defined relative to the bearing center. Other side
    # is a180deg rotation about Z, preserving up and giving outward pin axes.
    pin=cylinder(15.875/2,-36,23.5).fuse(cylinder(c['pin_journal_radius'],-12.5,25))
    pin=pin.fuse(cylinder(21,12.5,7.5)).fuse(cylinder(c['pin_stem_radius'],20,18)).fuse(cylinder(16,38,5))
    p['bearing_pin']=pin.removeSplitter()
    # Flat on stem receives the pin locking screw without material penetration.
    p['bearing_pin']=p['bearing_pin'].cut(Part.makeBox(10,18,40,V(11.7,20,-20)))
    h=c['bearing_center_z']-c['shaft_center_z']; dx=c['bearing_center_x']-c['shaft_center_x']
    hw=c['lever_hub_width']; wt=c['lever_web_thickness']
    hub=cylinder(c['lever_hub_radius'],-hw/2,hw)
    lever=hub.fuse(web_polygon([(-25,0),(25,0),(dx+18,h),(dx-18,h)],wt))
    lever=lever.fuse(cylinder(c['lever_top_radius'],-wt/2,wt,dx,h))
    lever=lever.fuse(Part.makeBox(12,wt,18,V(dx+12,-wt/2,h-9)))
    lever=lever.cut(cylinder(c['shaft_bore_radius'],-hw/2-1,hw+2))
    lever=lever.cut(cylinder(c['pin_lever_bore_radius'],-wt/2-1,wt+2,dx,h))
    keyz=c['shaft_radius']-c['key_depth_in_shaft'];kw=c['key_width'];ka=c['key_fit_allowance']
    keycut=Part.makeBox(kw+2*ka,hw+2,kw+2*ka,V(-kw/2-ka,-hw/2-1,keyz-ka))
    lever=lever.cut(keycut)
    # M4175 inferred radial screw, axis X, source7/16in from its plain nut.
    screw_r=c['pin_lock_screw_diameter']/2
    lever=lever.cut(Part.makeCylinder(screw_r+.1,20,V(dx+10,0,h),V(1,0,0))).removeSplitter()
    p['right_lever']=lever
    # The source5/8x7/8cup setscrew for M4162 gets a real receiving bore;
    # that screw is retained as pending until its shaft retention is detailed.
    p['left_lever']=lever.cut(Part.makeCylinder(15.875/2+.1,25,V(-40,0,0),V(1,0,0))).removeSplitter()
    p['pin_lock_screw']=Part.makeCylinder(screw_r,c['pin_lock_screw_length'],V(0,0,0),V(1,0,0)).fuse(
        Part.makeBox(5,9,9,V(c['pin_lock_screw_length'],-4.5,-4.5))).removeSplitter()
    nut=hex_nut(c['pin_lock_screw_diameter'],17.4625,9.525)
    nut.rotate(V(0,0,0),V(0,0,1),-90);p['pin_lock_nut']=nut
    # Source five keys apportioned three on main shaft, two future auxiliary.
    p['key']=Part.makeBox(kw,c['key_length'],kw,V(-kw/2,-c['key_length']/2,keyz))
    shaft=cylinder(c['shaft_radius'],c['shaft_y_min'],c['shaft_y_max']-c['shaft_y_min'])
    shaft=shaft.fuse(cylinder(25,c['shaft_y_min']-8,8))
    key_ys=[-c['lever_y'],c['lever_y'],c['operating_lever_y']]
    for y in key_ys:
        shaft=shaft.cut(Part.makeBox(kw+2*ka,c['key_length']+2*ka,kw+2*ka,
            V(-kw/2-ka,y-c['key_length']/2-ka,keyz-ka)))
    shaft=shaft.cut(Part.makeCylinder(2.1,50,V(-25,259,0),V(1,0,0)))
    p['shaft']=shaft.removeSplitter()
    ex,ez=c['operating_eye_x'],c['operating_eye_z']
    operating=hub.fuse(web_polygon([(-18,0),(18,-8),(ex+10,ez-10),(ex-10,ez+10)],wt))
    operating=operating.fuse(cylinder(18,-wt/2,wt,ex,ez))
    operating=operating.cut(cylinder(c['shaft_bore_radius'],-hw/2-1,hw+2)).cut(keycut)
    p['operating_lever']=operating.cut(cylinder(c['operating_eye_bore'],-wt/2-1,wt+2,ex,ez)).removeSplitter()
    for side,sign in [('Left',1),('Right',-1)]:
        rot=App.Rotation(V(0,0,1),0 if sign==1 else 180)
        center=V(c['bearing_center_x'],sign*c['bearing_center_y'],c['bearing_center_z'])
        def place(key,name,local=(0,0,0),assembly='ClutchThrowout'):
            add(key,side+name,list(center+rot.multVec(V(*local))),list(rot.Q),assembly)
        assembly='ClutchThrowoutBearing'+side
        for key in ['bearing_outer','bearing_inner','bearing_cage']:
            place(key,key.title().replace('_',''),assembly=assembly)
        for k,v in enumerate(ball_centers):place('bearing_ball','Ball%02d'%(k+1),v,assembly)
        place('bearing_pin','Pin')
        place('bearing_washer','OuterWasher',(0,width/2,0))
        flip=rot.multiply(App.Rotation(V(0,0,1),180))
        add('bearing_washer',side+'InnerWasher',list(center+rot.multVec(V(0,-width/2,0))),list(flip.Q))
        place('retainer_washer','RetainerWasher',(0,-15.675,0))
        place('pin_lockwasher','Lockwasher',(0,-19.175,0))
        place('pin_nut','Nut',(0,-33.4625,0))
        lever_center=V(c['shaft_center_x'],sign*c['lever_y'],c['shaft_center_z'])
        # Fork geometry is mirrored by rotation and dx changes sign only when
        # the separately controlled shaft and bearing stations coincide.
        assert abs(dx)<1e-8, 'Nonvertical fork needs an explicit handed profile revision'
        add('left_lever' if sign==1 else 'right_lever',side+'Lever',list(lever_center),list(rot.Q))
        place('pin_lock_screw','PinLockScrew',(11.7,c['lever_y']-c['bearing_center_y'],0))
        place('pin_lock_nut','PinLockNut',(24,c['lever_y']-c['bearing_center_y'],0))
    origin=[c['shaft_center_x'],0,c['shaft_center_z']]
    add('shaft','Shaft',origin)
    add('operating_lever','OperatingLever',[origin[0],c['operating_lever_y'],origin[2]])
    for n,y in enumerate(key_ys):add('key','MainKey%d'%(n+1),[origin[0],y,origin[2]])
    for key,shape in p.items():
        assert shape.isValid() and len(shape.Solids)==1,(key,len(shape.Solids))
    d=dict(bearing_centers=[[c['bearing_center_x'],s*c['bearing_center_y'],c['bearing_center_z']] for s in [1,-1]],
           bearing_internal_ball_centers=ball_centers,spherical_outer_race_radius=spherical_radius,
           shaft_origin=origin,main_key_stations=key_ys,source_bearing_units=2,
           inferred_pieces_per_bearing=3+len(ball_centers),shaft_brackets_present=False,
           complete_throwout=False,source_shaft_station_difference_mm=c['shaft_center_x']-709.8697)
    return p,occ,d
