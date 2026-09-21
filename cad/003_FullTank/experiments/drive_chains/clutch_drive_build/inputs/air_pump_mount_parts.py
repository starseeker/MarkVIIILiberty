"""Source-counted pump supports; inferred rail, boss and stepped-stud geometry.

All shapes and datums use the transmission core frame, X forward,Y port,Z up.
The pump height follows a conditional belt equation, not the previous free-space
placement. No original manufacturing geometry or structural capacity is claimed.
"""
import math
import FreeCAD as App
import Part
from air_pressure_pump_parts import cyl, xc, box, hexagon, bolt, moved
from transmission_input_installation_parts import formed_pin
from transmission_stud_parts import hex_x


def belt_length(center, r1, r2):
    delta=abs(r2-r1)
    return 2*math.sqrt(center*center-delta*delta)+math.pi*(r1+r2)+2*delta*math.asin(delta/center)


def belt_center(length,r1,r2):
    low=abs(r2-r1)+1e-5;high=length/2
    if belt_length(low,r1,r2)>=length:
        raise ValueError('Belt too short for the selected radii')
    for _ in range(70):
        mid=(low+high)/2
        if belt_length(mid,r1,r2)<length:low=mid
        else:high=mid
    return (low+high)/2


def rail(x0,x1,y,r,z0,z1):
    return box(x0,x1,y-r,y+r,z0,z1).fuse(moved(cyl(r,z0,z1),(x0,y,0))).fuse(
        moved(cyl(r,z0,z1),(x1,y,0))).removeSplitter()


def nut(af,height,r,gap):
    return hexagon(af,0,height).cut(cyl(r+gap,-1,height+1)).removeSplitter()


def washer(c):
    return cyl(c['washer_radius'],0,c['washer_stock']).cut(
        cyl(c['washer_bore_radius'],-1,c['washer_stock']+1)).cut(
        box(0,c['washer_radius']+1,-c['washer_split']/2,c['washer_split']/2,-1,c['washer_stock']+1)).removeSplitter()


def build(c,pc,old_cover,old_house):
    center=belt_center(c['belt_length'],c['belt_pump_pitch_radius'],c['belt_drive_pitch_radius'])
    top=center+pc['base_floor'];bottom=top-c['rail_stock'];halfspan=c['pump_foot_hole_y']
    parts={};occ=[];datums=[];gap=c['receiver_gap'];front=c['front_stud_x']
    face=c['rear_face_x'];rear_z=c['rear_joint_z'];lug_end=face+c['rear_lug_stock']
    stud_start=face-c['mx98_us_thread'];stud_end=stud_start+c['mx98_length']
    cotter_x=lug_end+c['mx98_nut_height']-c['mx98_slot_depth']/2
    parts['mx98_stud']=xc(c['mx98_diameter']/2,stud_start,stud_end).cut(
        Part.makeCylinder(c['cotter_diameter']/2+.05,c['mx98_diameter']+2,
            App.Vector(cotter_x,-c['mx98_diameter']/2-1,0),App.Vector(0,1,0)))
    crown=c['mx98_nut_height']-c['mx98_slot_depth']
    cn=hex_x(c['half_nut_af'],0,crown).fuse(xc(c['mx98_crown_radius'],crown,c['mx98_nut_height']))
    cn=cn.cut(xc(c['mx98_diameter']/2+c['nut_bore_gap'],-1,c['mx98_nut_height']+1))
    for angle in [0,60,120]:
        tool=box(crown,c['mx98_nut_height']+1,-20,20,-(c['cotter_diameter']+.5)/2,(c['cotter_diameter']+.5)/2)
        tool.rotate(App.Vector(),App.Vector(1,0,0),angle);cn=cn.cut(tool)
    parts['mx98_nut']=cn.removeSplitter()
    pin_c=dict(cotter_center_spacing=1.21,cotter_diameter=c['cotter_diameter'],crown_radius=c['mx98_crown_radius'],
        cotter_head_gap=.6,cotter_exit_gap=.8,cotter_bend_radius=1.5,cotter_bend_angle=60,
        cotter_length=c['cotter_length'],cotter_eye_radius=2.2,cotter_eye_rise=1.8,cotter_eye_join_overlap=.2)
    parts['mx98_cotter'],pin_detail=formed_pin(pin_c)
    shoulder=bottom-c['washer_stock']
    upper_end=top+c['washer_stock']+c['small_nut_height']+c['front_stud_tip_extra']
    lower=c['front_boss_seat']-c['front_stud_embed']
    parts['mx99_stud']=cyl(6.35,lower,shoulder).fuse(cyl(4.7625,shoulder-.01,upper_end))
    parts['mx102_jam']=nut(c['half_nut_af'],c['jam_nut_height'],6.35,c['nut_bore_gap'])
    parts['half_nut']=nut(c['half_nut_af'],c['half_nut_height'],6.35,c['nut_bore_gap'])
    parts['small_nut']=nut(c['small_nut_af'],c['small_nut_height'],4.7625,c['nut_bore_gap'])
    parts['washer']=washer(c)
    # SAE and US nut thread identities remain separate despite identical smooth
    # inspection envelopes; shared geometry does not establish interchangeability.
    parts['base_nut']=parts['small_nut'].copy()
    parts['base_washer']=parts['washer'].copy()
    parts['base_bolt']=bolt(c['base_bolt_diameter'],c['base_bolt_length'],c['base_bolt_af'],c['base_bolt_head_height'])
    # The source catalogue names integral receivers in M264 and M250 assemblies;
    # local bosses are changes to those castings, not invented extra BOM parts.
    cover=old_cover.copy();house=old_house.copy()
    for sign,label,key in [(1,'Port','bracket_left'),(-1,'Starboard','bracket_right')]:
        y=sign*halfspan;fy=sign*c['front_stud_half_span']
        bracket=rail(face+c['rail_half_width'],c['rail_end_x'],y,c['rail_half_width'],bottom,top)
        bracket=bracket.fuse(box(face,lug_end,y-c['rear_lug_half_width'],y+c['rear_lug_half_width'],rear_z-16,top))
        # A side web joins the tall rear ear to the horizontal ledge. Its outline
        # is deliberately parametric; unshown historical curvature is uncertain.
        pts=[App.Vector(face+1,y-c['web_stock']/2,rear_z+10),
             App.Vector(front+10,y-c['web_stock']/2,bottom+1),
             App.Vector(face+1,y-c['web_stock']/2,bottom+1)]
        web=Part.Face(Part.makePolygon(pts+pts[:1])).extrude(App.Vector(0,c['web_stock'],0))
        bracket=bracket.fuse(web)
        # Transverse rounded ear for the front adjustment stud.
        ear=box(front-15,front+15,min(y,fy),max(y,fy),bottom,top)
        ear=ear.fuse(moved(cyl(15,bottom,top),(front,fy,0)))
        bracket=bracket.fuse(ear)
        holes=[xc(6.35+gap,face-1,lug_end+1,y,rear_z),moved(cyl(4.7625+gap,bottom-1,top+1),(front,fy,0))]
        for x in [c['pump_x']-pc['foot_hole_x'],c['pump_x']+pc['foot_hole_x']]:
            holes.append(moved(cyl(c['base_bolt_diameter']/2+gap,bottom-1,top+1),(x,y,0)))
        parts[key]=bracket.cut(Part.makeCompound(holes)).removeSplitter()
        parts[key]=parts[key].cut(xc(c['rear_flange_relief_radius'],face-1,lug_end+1)).removeSplitter()
        cover=cover.fuse(xc(c['rear_boss_radius'],c['rear_boss_start_x'],face,y,rear_z))
        cover=cover.cut(xc(6.35+gap,stud_start-c['blind_gap'],face+1,y,rear_z))
        boss=moved(cyl(c['front_boss_radius'],c['front_boss_bottom'],c['front_boss_seat']),(front,fy,0))
        # Preserve the existing cup passage even where the added boss root would
        # otherwise protrude inward; the receiver itself stops above this bore.
        boss=boss.cut(xc(74.7125,front-c['front_boss_radius']-1,front+c['front_boss_radius']+1))
        house=house.fuse(boss).cut(moved(cyl(6.35+gap,lower-c['blind_gap'],c['front_boss_seat']+1),(front,fy,0)))
        def add(suffix,k,xyz=(0,0,0),parent='Supports'):
            occ.append(dict(name='PumpMount_'+label+'_'+suffix,key=k,xyz=list(xyz),parent=parent,
                subsystem='FuelPressure' if parent=='BaseFasteners' else 'Drivetrain'))
        add('Bracket',key)
        add('MX98_Stud','mx98_stud',(0,y,rear_z));add('MX98_Nut','mx98_nut',(lug_end,y,rear_z))
        add('MX98_Cotter','mx98_cotter',(cotter_x,y,rear_z))
        add('MX99_Stud','mx99_stud',(front,fy,0));add('MX102_JamNut','mx102_jam',(front,fy,c['front_boss_seat']))
        add('MX99_HalfNut','half_nut',(front,fy,shoulder-c['half_nut_height']))
        add('MX99_LowerWasher','washer',(front,fy,shoulder));add('MX99_UpperWasher','washer',(front,fy,top))
        add('MX99_SmallNut','small_nut',(front,fy,top+c['washer_stock']))
        for n,x in enumerate([c['pump_x']-pc['foot_hole_x'],c['pump_x']+pc['foot_hole_x']],1):
            add(f'Base{n}_Bolt','base_bolt',(x,y,top+pc['foot_stock']),'BaseFasteners')
            add(f'Base{n}_Washer','base_washer',(x,y,bottom-c['washer_stock']),'BaseFasteners')
            add(f'Base{n}_Nut','base_nut',(x,y,bottom-c['washer_stock']-c['small_nut_height']),'BaseFasteners')
        datums.append(dict(side=label,sign=sign,rear_axis=[face,y,rear_z],front_axis=[front,fy,c['front_boss_seat']],
            foot_axes=[[x,y,top] for x in [c['pump_x']-pc['foot_hole_x'],c['pump_x']+pc['foot_hole_x']]]))
    # Global refinement merges pre-existing grease-port edges at X279 and
    # raises their tolerance from3e-7 to6e-4mm. Retain the valid Boolean result
    # and its face divisions so this mounting change preserves that interface.
    revised=dict(cover=cover.removeSplitter(),housing=house)
    parts={k:s.removeSplitter() for k,s in parts.items()}
    for k,s in {**parts,**revised}.items():
        assert s.isValid() and len(s.Solids)==1,(k,s.isValid(),len(s.Solids))
    details=dict(pump_origin=[c['pump_x'],c['pump_y'],center],rail_top=top,rail_bottom=bottom,
        rear_stud_start=stud_start,rear_stud_end=stud_end,rear_nut_seat=lug_end,rear_cotter_station=cotter_x,
        rear_us_thread=[stud_start,stud_start+c['mx98_us_thread']],rear_sae_thread=[stud_end-c['mx98_sae_thread'],stud_end],
        front_stud_lower=lower,front_stud_shoulder=shoulder,front_stud_end=upper_end,
        inferred_front_thread_spans=[[lower,lower+c['front_half_thread_length']],
            [shoulder-c['half_nut_height']-8,shoulder],[shoulder,upper_end]],
        datums=datums,cotter=pin_detail,belt=dict(length=c['belt_length'],pump_pitch_radius=c['belt_pump_pitch_radius'],
        drive_pitch_radius=c['belt_drive_pitch_radius'],center_distance=center,plane_x=c['pump_x']+(pc['pulley_rim_start']+pc['pulley_rim_end'])/2,
        physical_drive_present=False,length_reference_unverified=True,
        radius_scenarios=[dict(radial_shift=t,center=belt_center(c['belt_length'],c['belt_pump_pitch_radius']+t,c['belt_drive_pitch_radius']+t))
            for t in [-c['belt_reference_radius_uncertainty'],0,c['belt_reference_radius_uncertainty']]]))
    return parts,occ,revised,details
