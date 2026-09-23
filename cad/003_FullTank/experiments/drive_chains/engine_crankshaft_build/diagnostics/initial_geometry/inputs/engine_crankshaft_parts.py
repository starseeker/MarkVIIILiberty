"""Liberty crankshaft and bearings, in the inherited crankcase coordinates.

X runs nose to gear end, Y port, Z up. Analytic machining envelopes are used;
the unprinted casting, forging, bearing and hardware sizes remain estimates.
"""
import math
import FreeCAD as App
import Part
from engine_crossmember_parts import box
from transmission_stud_parts import hex_x
from transmission_input_installation_parts import formed_pin

V=App.Vector
X,Y,Z=V(1,0,0),V(0,1,0),V(0,0,1)

def cyl(r,a,b,y=0,z=0):
    return Part.makeCylinder(r,b-a,V(a,y,z),X)

def ring(ro,ri,a,b):
    return cyl(ro,a,b).cut(cyl(ri,a-1,b+1))

def polygon(points,delta):
    return Part.Face(Part.makePolygon(points+points[:1])).extrude(delta)

def translated(s,delta):
    s=s.copy();s.translate(delta);return s

def half(s,sign):
    b=s.BoundBox
    return s.common(box(b.XMin-1,b.XMax+1,b.YMin-1,b.YMax+1,
                        0 if sign>0 else b.ZMin-1,b.ZMax+1 if sign>0 else 0))

def cheek(a,b,phase,c):
    u=V(0,math.sin(phase),math.cos(phase));v=V(0,math.cos(phase),-math.sin(phase))
    throw=c['stroke']/2;r0=c['web_root_radius'];r1=c['web_pin_radius']
    q=(r0-r1)/throw;h=math.sqrt(1-q*q)
    points=[X*a+u*(r0*q)+v*(r0*h),X*a+u*(throw+r1*q)+v*(r1*h),
            X*a+u*(throw+r1*q)-v*(r1*h),X*a+u*(r0*q)-v*(r0*h)]
    return cyl(r0,a,b).fuse(cyl(r1,a,b,u.y*throw,u.z*throw)).fuse(polygon(points,X*(b-a)))

def parts(c,cc,taper,originals,progress=None):
    p={};occ=[]
    def audit(name,s):
        assert not s.isNull() and s.isValid() and len(s.Solids)==1,(name,len(s.Solids),s.isValid())
        if progress:progress(name,s)
    def add(key,name,xyz=V(),rotation=None,assembly='EngineRotatingAssembly'):
        occ.append(dict(key=key,name='EngineCrank_'+name,xyz=list(xyz),rotation=list((rotation or App.Rotation()).Q),assembly=assembly))
    first=cc['nose_to_first_row'];pitch=cc['cylinder_pitch'];rows=[first+i*pitch for i in range(7)]
    short=c['main_bearing_short_length'];long=c['main_bearing_long_length'];play=c['journal_endplay']/2
    seats=[(first+short/2-long,first+short/2)]+[(x-short/2,x+short/2) for x in rows[1:]]
    outer=cc['crankshaft_diameter']/2+cc['main_bearing_shell_stock']
    jr=c['journal_diameter']/2;inner=jr+c['bearing_diametral_clearance']/2;throw=c['stroke']/2
    phases=[c['static_phase_deg']+d for d in [0,-120,120,120,-120,0]]
    d=dict(main_rows=rows,bearing_spans=seats,bearing_inner_radius=inner,bearing_outer_radius=outer,
           crank_phases_deg=phases,cylinder_numbers_nose_to_gear=[6,5,4,3,2,1],taper=taper,
           crankpin_stations=[],oil_passages=[],bearing_ports=[],dowel_positions=[],estimated_profiles=True)
    # Continuous nose journal and taper, then separate journals joined only by
    # cheeks and offset crankpins. There is no fictitious shaft through the bays.
    rear,front=taper['rear'],taper['front'];rrear,rfront=taper['rear_radius'],taper['front_radius']
    shaft=Part.makeCone(rrear,rfront,front-rear,V(rear,0,0),X)
    shaft=shaft.fuse(cyl(c['output_thread_radius'],rear-c['output_thread_length'],rear))
    journals=[(front,seats[0][1]+play)]+[(a-play,b+play) for a,b in seats[1:]]
    for a,b in journals:shaft=shaft.fuse(cyl(jr,a,b))
    cheeks=[];pins=[]
    for i,phase_deg in enumerate(phases):
        phase=math.radians(phase_deg);u=V(0,math.sin(phase),math.cos(phase));pin=u*throw
        left=journals[i][1];right=journals[i+1][0];w=c['web_stock']
        for a,b in [(left,left+w),(right-w,right)]:
            s=cheek(a,b,phase,c);cheeks.append((a,b,pin));shaft=shaft.fuse(s)
        a,b=left+w,right-w
        shaft=shaft.fuse(cyl(c['crankpin_diameter']/2,a,b,pin.y,pin.z));pins.append((a,b,pin))
        d['crankpin_stations'].append(dict(cylinder=6-i,center=[(a+b)/2,pin.y,pin.z],running_span=[a,b],phase_deg=phase_deg))
    flange0=rows[-1]+c['gear_flange_back'];flange1=flange0+c['gear_flange_stock']
    shaft=shaft.fuse(cyl(c['gear_flange_radius'],flange0,flange1))
    tc=c['thrust_center'];tcs=c['thrust_center_stock'];shoulder=tc+tcs/2
    shaft=shaft.fuse(cyl(c['thrust_shaft_shoulder_radius'],shoulder,shoulder+c['thrust_shaft_shoulder_stock']))
    audit('solid forging before hollows',shaft)
    # Main and pin cavities are open until the separately owned plugs are added.
    for i,(a,b) in enumerate(journals):
        lo=rear-c['output_thread_length']-1 if i==0 else a-c['web_stock']-1
        hi=flange1+1 if i==6 else b+c['web_stock']+1
        shaft=shaft.cut(cyl(c['main_hollow_radius'],lo,hi))
        # Radial journal oil drill; arbitrary clocking, explicit approximation.
        x=(seats[i][0]+seats[i][1])/2
        tool=Part.makeCylinder(c['oil_drill_radius'],jr+2,V(x,0,0),-Z)
        shaft=shaft.cut(tool);d['oil_passages'].append(dict(kind='main_radial',start=[x,0,0],end=[x,0,-jr-2]))
    for a,b,pin in pins:
        shaft=shaft.cut(cyl(c['pin_hollow_radius'],a-c['web_stock']-1,b+c['web_stock']+1,pin.y,pin.z))
        axis=pin/throw;start=V((a+b)/2,pin.y,pin.z);end=start+axis*(c['crankpin_diameter']/2+2)
        shaft=shaft.cut(Part.makeCylinder(c['oil_drill_radius'],(end-start).Length,start,axis))
        d['oil_passages'].append(dict(kind='pin_radial',start=list(start),end=list(end)))
    # LIB36 oil rises through the rear web of each throw into its crankpin.
    for a,b,pin in cheeks[1::2]:
        start=V((a+b)/2,0,0);end=start+pin
        shaft=shaft.cut(Part.makeCylinder(c['oil_drill_radius'],throw,start,pin/throw))
        d['oil_passages'].append(dict(kind='rear_web',start=list(start),end=list(end)))
    # Tapered key, a flat-head retaining screw, and two extraction holes (LIB18).
    kx=(rear+front)/2;ka=kx-c['key_length']/2;kb=kx+c['key_length']/2
    slope=(rfront-rrear)/(front-rear)
    def radius(x):return rrear+(x-rear)*slope
    def keyshape(width,extra=0):
        pts=[V(ka-extra,radius(ka-extra)-c['key_depth'],-width/2),V(kb+extra,radius(kb+extra)-c['key_depth'],-width/2),
             V(kb+extra,radius(kb+extra)+taper['keyway_depth']-c['key_top_gap'],-width/2),
             V(ka-extra,radius(ka-extra)+taper['keyway_depth']-c['key_top_gap'],-width/2)]
        return polygon(pts,V(0,0,width))
    key=keyshape(c['key_width']);shaft=shaft.cut(keyshape(c['key_width']+.1,.05))
    top=radius(kx)+taper['keyway_depth']-c['key_top_gap'];sr=c['key_screw_diameter']/2
    sh=c['key_screw_head_height'];hr=c['key_screw_head_radius'];length=c['key_screw_length']
    # Axis normal to the sloping top face makes the countersink genuinely flush.
    normal=V(-slope,1,0);normal.normalize();head=V(kx,top,0)
    screw=Part.makeCylinder(sr,length-sh,head-normal*length,normal).fuse(Part.makeCone(sr,hr,sh,head-normal*sh,normal))
    receiver=Part.makeCylinder(sr+.05,length+.2,head-normal*(length+.1),normal)
    receiver=receiver.fuse(Part.makeCone(sr+.05,hr+.05,sh,head-normal*sh,normal))
    shaft=shaft.cut(receiver);key=key.cut(receiver)
    for x in [kx-c['key_length']/4,kx+c['key_length']/4]:
        key=key.cut(Part.makeCylinder(sr,key.BoundBox.YLength+2,V(x,key.BoundBox.YMin-1,0),Y))
    screw=screw.cut(box(kx-hr-1,kx+hr+1,top-.7,top+2,-.6,.6))
    p['key']=key;p['key_screw']=screw
    add('key','FlywheelKey');add('key_screw','FlywheelKeyScrew')
    pinx=rear-c['output_thread_length']+3.5
    shaft=shaft.cut(Part.makeCylinder(c['output_cotter_diameter']/2+.1,2*c['output_thread_radius']+2,V(pinx,-c['output_thread_radius']-1,0),Y))
    p['shaft']=shaft.removeSplitter();add('shaft','Forging')
    p['output_nut']=hex_x(c['output_nut_af'],rear-c['output_nut_length'],rear).cut(cyl(c['output_thread_radius']+c['thread_clearance'],rear-c['output_nut_length']-1,rear+1))
    add('output_nut','OutputNut')
    pincontrols=dict(cotter_center_spacing=c['output_cotter_diameter']*.52,cotter_diameter=c['output_cotter_diameter'],
        crown_radius=c['output_thread_radius'],cotter_head_gap=.8,cotter_exit_gap=.8,cotter_bend_radius=3.,cotter_bend_angle=35,
        cotter_length=c['output_cotter_length'],cotter_eye_radius=4.,cotter_eye_rise=2.,cotter_eye_join_overlap=.03)
    p['output_cotter'],d['output_cotter']=formed_pin(pincontrols);add('output_cotter','OutputCotter',V(pinx,0,0))
    d.update(key_center=[kx,top,0],key_span=[ka,kb],key_screw_normal=list(normal),output_cotter_x=pinx,gear_flange_span=[flange0,flange1])
    audit('hollow keyed forging',p['shaft'])
    # Bearing shells retain outer supporting material under shallow inner oil
    # grooves. The long front shell has paired oil entries as drawn in LIB31.
    for label,length in [('long',long),('short',short)]:
        for sign,word in [(1,'upper'),(-1,'lower')]:
            shell=half(ring(outer,inner,0,length),sign)
            feeds=[length*.25,length*.75] if label=='long' else [length*.5]
            for x in feeds:
                # Distribution cross: short axial channel plus circumferential
                # inner groove. Exact width/depth are named approximations.
                w=c['bearing_oil_groove_width'];depth=c['bearing_oil_groove_depth']
                shell=shell.cut(cyl(inner+depth,x-w/2,x+w/2))
                shell=shell.cut(Part.makeCylinder(c['bearing_oil_feed_radius'],outer+2,V(x,0,0),Z*sign))
                local=box(x-length*.1,x+length*.1,-w/2,w/2,inner-depth,inner+depth)
                if sign<0:local.rotate(V(),X,180)
                shell=shell.cut(local)
            # Dowel remains recessed below the running surface; its hole is
            # visible through the liner, as shown in the front-bearing figure.
            dx=length*.5 if label=='long' else length*.72
            shell=shell.cut(Part.makeCylinder(c['dowel_diameter']/2+c['dowel_clearance'],outer+2,V(dx,0,0),Z*sign))
            for x in [length*(i+1)/(int(length/10)+1) for i in range(int(length/10))]:
                shell=shell.cut(ring(inner+c['bearing_oil_groove_depth'],inner-.1,x-1,x+1).common(box(-1,length+1,-outer-1,outer+1,-2,2)))
            p[label+'_'+word]=shell.removeSplitter()
    p['dowel']=Part.makeCylinder(c['dowel_diameter']/2,c['dowel_length'],V(),Z)
    upper=originals['upper'].copy();lower=originals['lower'].copy()
    for i,(a,b) in enumerate(seats):
        label='long' if i==0 else 'short';length=b-a;dx=a+(length*.5 if i==0 else length*.72)
        annulus=ring(cc['bearing_boss_radius'],outer,a,b)
        upper=upper.fuse(half(annulus,1));lower=lower.fuse(half(annulus,-1))
        for sign,word in [(1,'upper'),(-1,'lower')]:
            add(label+'_'+word,'Main%d_%s'%(i+1,word),V(a,0,0),assembly='EngineMainBearings')
            pos=V(dx,0,sign*c['dowel_radial_start']);rot=App.Rotation(X,180) if sign<0 else App.Rotation()
            add('dowel','Main%d_%s_Dowel'%(i+1,word),pos,rot,assembly='EngineMainBearings');d['dowel_positions'].append(list(pos))
            cutter=Part.makeCylinder(c['dowel_diameter']/2+c['dowel_clearance'],c['dowel_length']+.1,pos,Z*sign)
            if sign>0:upper=upper.cut(cutter)
            else:lower=lower.cut(cutter)
        # Lower-case radial feeds stop at the existing nut-access cavity;
        # pressure pipes and front camshaft leads are separate pending pieces.
        for x in ([a+length*.25,a+length*.75] if i==0 else [(a+b)/2]):
            lower=lower.cut(Part.makeCylinder(c['bearing_oil_feed_radius'],70,V(x,0,0),-Z))
            d['bearing_ports'].append([x,0,-outer])
        if i==0:
            for x in [a+length*.25,a+length*.75]:
                tool=ring(outer+c['bearing_oil_groove_depth'],outer-.1,x-1.5,x+1.5)
                upper=upper.cut(tool);lower=lower.cut(tool)
            for sign in [-1,1]:
                tool=Part.makeCylinder(1.5,length*.5,V(a+length*.25,0,sign*outer),X)
                if sign>0:upper=upper.cut(tool)
                else:lower=lower.cut(tool)
    # The nose bearing receiver is larger than the earlier casing hypothesis.
    # Cast a split thrust housing around its two sleeve seats, attached to the
    # existing joint flange. Axial sleeve location is estimated, source topology.
    rowoff=c['thrust_ball_row_offset'];ostock=c['thrust_outer_stock'];offset=c['thrust_outer_offset']
    left_race=tc-offset-ostock;right_race=tc+offset
    sleeveleft=left_race-c['thrust_sleeve_stock'];sleeveright=right_race+ostock+c['thrust_sleeve_stock']
    housing=ring(c['thrust_seat_radius'],c['thrust_outer_bore'],sleeveleft-3,sleeveright+3)
    housing=housing.cut(cyl(c['thrust_sleeve_outer_radius']+c['thrust_seat_gap'],sleeveleft,sleeveright))
    upper=upper.fuse(half(housing,1));lower=lower.fuse(half(housing,-1))
    # Keep all sixteen inherited through-stud passages open after saddle growth.
    for x in [first-cc['nose_second_web_spacing']]+rows:
        for sign in [-1,1]:
            tool=Part.makeCylinder(cc['bearing_stud_bore_radius'],cc['deck_center_height']+90,V(x,sign*cc['bearing_stud_half_spacing'],-80))
            upper=upper.cut(tool);lower=lower.cut(tool)
    # Raising the estimated gear chamber floor clears the integral shaft flange.
    last=rows[-1];end=last+cc['gear_end_after_last_row'];wall=cc['case_wall'];width=cc['body_half_width']-wall
    upper=upper.cut(box(last+wall,end-wall,-width,width,cc['gear_chamber_floor']-wall,cc['gear_chamber_floor']))
    upper=upper.fuse(box(last+wall,end-wall,-width,width,c['gear_floor_height']-wall,c['gear_floor_height']))
    for x,y,r in [(last+78,0,cc['gear_vertical_bore_radius']),(last+25,55,cc['gear_oil_trap_radius'])]:
        upper=upper.cut(Part.makeCylinder(r,c['gear_floor_height']+2,V(x,y,-1)))
    p['upper']=upper;p['lower']=lower
    audit('revised upper case',upper);audit('revised lower case',lower)
    # Three races, two cages and forty balls constitute one catalogue bearing.
    # Ball counts, race sizes and groove radii are estimates, not catalogue data.
    ball=c['thrust_ball_radius'];pitchr=c['thrust_ball_pitch_radius'];gr=ball+c['thrust_groove_allowance']
    center=ring(c['thrust_center_outer_radius'],jr+.1,-tcs/2,tcs/2)
    for x in [-rowoff,rowoff]:center=center.cut(Part.makeTorus(pitchr,gr,V(x,0,0),X))
    p['thrust_center']=center;add('thrust_center','ThrustCenter',V(tc,0,0),assembly='EngineThrustBearing')
    outerrace=ring(c['thrust_outer_radius'],c['thrust_outer_bore'],0,ostock)
    outerrace=outerrace.cut(Part.makeTorus(pitchr,gr,V(tc-rowoff-left_race,0,0),X))
    p['thrust_outer']=outerrace
    add('thrust_outer','ThrustLeftRace',V(left_race,0,0),assembly='EngineThrustBearing')
    flip=App.Rotation(Z,180)
    add('thrust_outer','ThrustRightRace',V(right_race+ostock,0,0),flip,assembly='EngineThrustBearing')
    cage=ring(c['thrust_cage_outer_radius'],c['thrust_cage_inner_radius'],-c['thrust_cage_stock']/2,c['thrust_cage_stock']/2)
    ballcenters=[]
    for i in range(c['thrust_balls_per_row']):
        angle=2*math.pi*i/c['thrust_balls_per_row'];pos=V(0,pitchr*math.cos(angle),pitchr*math.sin(angle));ballcenters.append(pos)
        cage=cage.cut(Part.makeSphere(ball+c['thrust_cage_ball_gap'],pos))
    p['thrust_cage']=cage;p['thrust_ball']=Part.makeSphere(ball)
    for sign,word in [(-1,'Left'),(1,'Right')]:
        x=tc+sign*rowoff;add('thrust_cage','Thrust'+word+'Cage',V(x,0,0),assembly='EngineThrustBearing')
        for i,pos in enumerate(ballcenters):add('thrust_ball','Thrust%sBall%02d'%(word,i+1),V(x,pos.y,pos.z),assembly='EngineThrustBearing')
    sr=c['thrust_sleeve_outer_radius'];st=c['thrust_sleeve_stock'];sl=c['thrust_sleeve_length']
    sleeve=ring(sr,c['thrust_outer_bore'],0,st).fuse(ring(sr,c['thrust_outer_radius']+c['thrust_seat_gap'],st,sl))
    p['thrust_sleeve']=sleeve.removeSplitter()
    add('thrust_sleeve','ThrustLeftSleeve',V(sleeveleft,0,0));add('thrust_sleeve','ThrustRightSleeve',V(sleeveright,0,0),flip)
    nutend=tc-tcs/2;nutstart=nutend-c['thrust_nut_length']
    nut=ring(c['thrust_nut_neck_radius'],jr+c['thread_clearance'],nutstart,nutend-4).fuse(ring(c['thrust_nut_radius'],jr+c['thread_clearance'],nutend-4,nutend))
    for i in range(c['thrust_nut_slot_count']):
        cut=box(nutstart-1,nutstart+3,0,c['thrust_nut_radius']+1,-c['thrust_nut_slot_width']/2,c['thrust_nut_slot_width']/2)
        cut.rotate(V(),X,i*360/c['thrust_nut_slot_count']);nut=nut.cut(cut)
    p['thrust_nut']=nut.removeSplitter();add('thrust_nut','ThrustNut')
    d.update(thrust_sleeve_span=[sleeveleft,sleeveright],thrust_race_spans=[[left_race,left_race+ostock],[tc-tcs/2,tc+tcs/2],[right_race,right_race+ostock]],
             thrust_ball_rows=[tc-rowoff,tc+rowoff],thrust_nut_span=[nutstart,nutend],thrust_housing_span=[sleeveleft-3,sleeveright+3])
    for key,s in p.items():audit(key,s)
    return p,occ,d
