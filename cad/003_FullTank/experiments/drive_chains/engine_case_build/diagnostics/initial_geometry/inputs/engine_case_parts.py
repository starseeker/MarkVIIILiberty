"""Two hollow Liberty crankcase castings with explicit estimated casting sections.

Local X runs from the output nose toward the distributor (tank+X). Z=0 is the
case joint and crankshaft axis; Y is tank port. Cubic lower-section control poles
are retained in datums. No casting profile is represented as a measured drawing.
"""
import math
import FreeCAD as App
import Part
from engine_crossmember_parts import box,xz_plate
V=App.Vector

def polygon_yz(x,points):
    v=[V(x,y,z) for y,z in points];return Part.Wire(Part.makePolygon(v+v[:1]).Edges)

def extrude(wire,length):return Part.Face(wire).extrude(V(length,0,0))

def upper_wire(x,c,scale=1,inside=False,base=-0.0):
    t=c['case_wall'] if inside else 0;slope=math.tan(math.radians(c['bank_angle']/2))
    w=c['body_half_width']*scale-t;d=c['deck_half_width']*scale-t
    roof=c['deck_center_height']*scale-t/math.cos(math.radians(c['bank_angle']/2))
    return polygon_yz(x,[(-w,base),(w,base),(d,roof-slope*d),(0,roof),(-d,roof-slope*d)])

def lower_wire(x,c,scale=1,inside=False):
    t=c['case_wall'] if inside else 0;w=c['body_half_width']*scale-t
    depth=c['lower_pan_depth']*scale-t;trough=c['lower_trough_depth']*scale-t
    # Degree3 Bezier segments, no smoothing or hidden curve fitting.
    segments=[
      [[-w,-24*scale],[-w,-116*scale+t],[-135*scale+t,-150*scale+t],[-55*scale,-depth]],
      [[-55*scale,-depth],[-45*scale,-depth-1],[-50*scale,-trough],[-38*scale,-trough]],
      [[38*scale,-trough],[50*scale,-trough],[45*scale,-depth-1],[55*scale,-depth]],
      [[55*scale,-depth],[135*scale-t,-150*scale+t],[w,-116*scale+t],[w,-24*scale]]]
    top=1 if inside else 0;edges=[Part.makeLine(V(x,-w,top),V(x,-w,-24*scale))]
    for i,pts in enumerate(segments):
        if i==2:edges.append(Part.makeLine(V(x,-38*scale,-trough),V(x,38*scale,-trough)))
        curve=Part.BezierCurve();curve.setPoles([V(x,y,z) for y,z in pts]);edges.append(curve.toShape())
    edges.extend([Part.makeLine(V(x,w,-24*scale),V(x,w,top)),Part.makeLine(V(x,w,top),V(x,-w,top))])
    return Part.Wire(edges),segments

def flange(points,z,stock):
    v=[V(x,y,z) for x,y in points];return Part.Face(Part.makePolygon(v+v[:1])).extrude(V(0,0,stock))

def parts(c,progress=None):
    def audit(label,shape):
        if progress:progress(label,shape)
        assert not shape.isNull() and shape.isValid() and len(shape.Solids)==1,(label,len(shape.Solids),shape.isValid())
    t=c['case_wall'];first=c['nose_to_first_row'];pitch=c['cylinder_pitch'];rows=[first+i*pitch for i in range(7)];last=rows[-1]
    start=first-c['body_start_before_first_row'];end=last+c['gear_end_after_last_row'];angle=math.radians(c['bank_angle']/2)
    webxs=[first-c['nose_second_web_spacing']]+rows;cylinders=[first+(i+.5)*pitch for i in range(6)]
    datums=dict(main_rows=rows,upper_web_stations=webxs,cylinder_stations=cylinders,body_start=start,gear_end=end,bank_angle=c['bank_angle'],
                source_main_bearings=7,source_upper_webs=8,geometry_assumptions=True,engine_mount_holes_drilled=False)
    # Outer cast bodies and projecting upper/lower joint flanges.
    nose_scale=c['nose_half_width']/c['body_half_width']
    upper=Part.makeLoft([upper_wire(0,c,nose_scale),upper_wire(start,c)],True,True)
    upper=upper.fuse(extrude(upper_wire(start,c),end-start))
    fw=c['mount_flange_half_width'];outline=[(0,-c['nose_half_width']),(start,-fw),(last+35,-fw),(end,-184),(end,184),(last+35,fw),(start,fw),(0,c['nose_half_width'])]
    upper=upper.fuse(flange(outline,0,c['mount_flange_stock']))
    lo0,_=lower_wire(0,c,nose_scale);lo1,pol=lower_wire(start,c)
    lower=Part.makeLoft([lo0,lo1],True,True).fuse(extrude(lo1,end-start))
    lw=c['lower_flange_half_width'];lower_outline=[(0,-c['nose_half_width']),(start,-lw),(end,-lw),(end,lw),(start,lw),(0,c['nose_half_width'])]
    lower=lower.fuse(flange(lower_outline,-c['lower_flange_stock'],c['lower_flange_stock']))
    # Distribution-end oil well and forward strainer well are integral casting.
    lower=lower.fuse(box(last-25,end,-90,90,-c['gear_well_depth'],-80))
    well_x=first+.75*pitch;wr=c['forward_well_radius']
    lower=lower.fuse(Part.makeCylinder(wr,c['forward_well_depth']-115,V(well_x,0,-c['forward_well_depth'])))
    audit('outer_upper',upper)
    # Continuous main cavity opens at the joint. A separate dry gear compartment
    # has a horizontal floor, with the wet cavity continuing below it.
    upper_inner=Part.makeLoft([upper_wire(t,c,nose_scale,True,-1),upper_wire(start,c,1,True,-1)],True,True)
    upper_inner=upper_inner.fuse(extrude(upper_wire(start,c,1,True,-1),last-start-t))
    upper=upper.cut(upper_inner)
    upper=upper.cut(extrude(upper_wire(last+t,c,1,True,c['gear_chamber_floor']),end-last-2*t))
    upper=upper.cut(box(last+t,end-t,-c['body_half_width']+t,c['body_half_width']-t,-1,c['gear_chamber_floor']-t))
    li0,_=lower_wire(t,c,nose_scale,True);li1,ipol=lower_wire(start,c,1,True)
    lower_inner=Part.makeLoft([li0,li1],True,True).fuse(extrude(li1,end-start-t))
    lower=lower.cut(lower_inner)
    lower=lower.cut(box(last-25+t,end-t,-90+t,90-t,-c['gear_well_depth']+t,1))
    lower=lower.cut(Part.makeCylinder(wr-t,c['forward_well_depth']-100,V(well_x,0,-c['forward_well_depth']+t)))
    audit('shell_upper',upper)
    datums['lower_section']=dict(degree=3,outer_poles=pol,inner_poles=ipol,fit='Controlled approximation, no source fit residual claimed')
    # Integral transverse webs, main bearing saddles and stud passages.
    boss=c['bearing_boss_radius'];seat=c['main_seat_width'];web=c['web_stock']
    for i,x in enumerate(webxs):
        scale=min(1,nose_scale+(1-nose_scale)*x/start)
        uw=extrude(upper_wire(x-web/2,c,scale),web)
        if i not in [0,1,7]:
            for sign in [-1,1]:
                y0,y1=sorted([sign*73,sign*146]);uw=uw.cut(box(x-web,x+web,y0,y1,72,157))
        lower_section,_=lower_wire(x-web/2,c,scale);dw=extrude(lower_section,web)
        # Nut-access windows below the saddle and lightening around the webs.
        dw=dw.cut(box(x-web,x+web,-66,66,-142,-68))
        for sign in [-1,1]:
            y0,y1=sorted([sign*73,sign*145]);dw=dw.cut(box(x-web,x+web,y0,y1,-118,-52))
        upper=upper.fuse(uw);lower=lower.fuse(dw)
        for sign in [-1,1]:
            y=sign*c['bearing_stud_half_spacing'];top=c['deck_center_height']*scale-abs(y)*math.tan(angle)
            tube=Part.makeCylinder(c['bearing_stud_boss_radius'],top,V(x,y,0));upper=upper.fuse(tube)
    audit('webbed_upper',upper)
    for i,x in enumerate(rows):
        x0=(webxs[0]-seat/2) if i==0 else x-seat/2;x1=x+seat/2
        b=Part.makeCylinder(boss,x1-x0,V(x0,0,0),V(1,0,0))
        upper=upper.fuse(b.common(box(x0-1,x1+1,-boss-1,boss+1,0,boss+1)))
        lower=lower.fuse(b.common(box(x0-1,x1+1,-boss-1,boss+1,-boss-1,0)))
    audit('saddles_upper',upper)
    # Both castings have matching bearing receivers; inserts are separate parts.
    radius=c['crankshaft_diameter']/2+c['main_bearing_shell_stock'];shaft=Part.makeCylinder(radius,end+2,V(-1,0,0),V(1,0,0))
    upper=upper.cut(shaft);lower=lower.cut(shaft)
    for x in webxs:
        for sign in [-1,1]:
            bore=Part.makeCylinder(c['bearing_stud_bore_radius'],c['deck_center_height']+90,V(x,sign*c['bearing_stud_half_spacing'],-80))
            upper=upper.cut(bore);lower=lower.cut(bore)
    audit('studs_upper',upper)
    # Seven pairs of external ribs per side, matching the source structure.
    for x in rows:
        for sign in [-1,1]:
            rib_y=[(sign*(c['body_half_width']-2),c['mount_flange_stock']),
                   (sign*fw,c['mount_flange_stock']),
                   (sign*c['deck_half_width'],c['deck_center_height']-c['deck_half_width']*math.tan(angle))]
            for dx in [-c['mount_rib_pair_spacing']/2,c['mount_rib_pair_spacing']/2]:
                rib=extrude(polygon_yz(x+dx-c['mount_rib_stock']/2,rib_y),c['mount_rib_stock']);upper=upper.fuse(rib)
    audit('ribs_upper',upper)
    # Twelve bores normal to the V-bank seats; exact piston bore remains separate
    # from this estimated spigot receiver diameter.
    spigot=c['piston_bore']/2+c['cylinder_spigot_stock']+c['cylinder_spigot_clearance'];cyl_axes=[]
    for x in cylinders:
        for sign in [-1,1]:
            axis=V(0,sign*math.sin(angle),math.cos(angle));origin=V(x,0,0)
            cutter=Part.makeCylinder(spigot,400,origin,axis);upper=upper.cut(cutter)
            seat_center=origin+axis*(c['deck_center_height']*math.cos(angle))
            cyl_axes.append(dict(x=x,side=sign,axis=list(axis),seat_center=list(seat_center),receiver_radius=spigot))
    audit('cylinders_upper',upper)
    # Gear drive / breather roof openings and two lateral filler connections.
    gx=last+58;ports=[]
    for sign in [-1,1]:
        axis=V(0,sign*math.sin(angle),math.cos(angle));upper=upper.cut(Part.makeCylinder(c['gear_inclined_bore_radius'],400,V(gx,0,0),axis))
        ports.append(dict(name='inclined_'+str(sign),origin=[gx,0,0],axis=list(axis),radius=c['gear_inclined_bore_radius']))
    for name,x,y,r in [('vertical',last+78,0,c['gear_vertical_bore_radius']),('breather',last+14,0,15.0)]:
        # The breather and vertical aperture are separated in X; revise controls
        # if a changed compartment length would join the openings.
        upper=upper.cut(Part.makeCylinder(r,320,V(x,y,0)));ports.append(dict(name=name,origin=[x,y,0],axis=[0,0,1],radius=r))
    upper=upper.cut(Part.makeCylinder(c['gear_oil_trap_radius'],70,V(last+25,55,-1)))
    for x in [cylinders[0],cylinders[-1]]:
        axis=V(0,1,0);center=V(x,160,102)
        upper=upper.fuse(Part.makeCylinder(38,30,center,axis)).cut(Part.makeCylinder(29,65,V(x,135,102),axis))
    audit('ports_upper',upper)
    # Through galleries reserve the two longitudinal oil pipes, without adding
    # unowned pipe material to the casting.
    for y in [-19,19]:lower=lower.cut(Part.makeCylinder(5.5,end-start+2,V(start-1,y,-174),V(1,0,0)))
    # Pump receivers at the distributor end and below its oil well.
    lower=lower.cut(Part.makeCylinder(35,2*t+2,V(end-t-1,0,-154),V(1,0,0)))
    lower=lower.cut(Part.makeCylinder(c['oil_pump_receiver_radius'],c['gear_well_depth']-110,V(last+c['oil_pump_receiver_after_last_row'],0,-c['gear_well_depth']-1)))
    audit('finished_lower',lower)
    refinement={}
    for name,s in [('upper',upper),('lower',lower)]:
        try:
            refined=s.removeSplitter()
            assert refined.isValid() and len(refined.Solids)==1
            refinement[name]='coplanar faces unified'
        except Part.OCCError:
            # OCC7.8 occasionally fails same-domain unification on the valid
            # casting. Preserve the checked original BRep without healing.
            refined=s;refinement[name]='unification raised OCCError; valid original topology retained'
        if name=='upper':upper=refined
        else:lower=refined
    datums['refinement']=refinement
    datums.update(cylinder_axes=cyl_axes,gear_ports=ports,forward_well_x=well_x,main_seat_radius=radius,
                  upper_window_stations=webxs[2:7],bearing_insert_identity_conflict=True)
    for name,s in [('upper',upper),('lower',lower)]:
        assert not s.isNull() and s.isValid() and len(s.Solids)==1,(name,len(s.Solids),s.isValid())
    return {'upper':upper,'lower':lower},datums
