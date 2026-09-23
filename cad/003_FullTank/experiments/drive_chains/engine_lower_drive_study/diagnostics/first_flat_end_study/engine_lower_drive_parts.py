"""Lower Liberty distribution-drive study, before crankcase receiver revision.

Definition axes are engine X/Y/Z with the common main-bevel apex at the origin.
Retain analytic machined surfaces and explicit spline-flank approximations.
"""
import math
import FreeCAD as App
import Part
from engine_crossmember_parts import box
from engine_crankshaft_parts import cyl, ring
from transmission_core_parts import revolve
from transmission_bevel_tooth import tooth, repeated_teeth
from transmission_stud_parts import hex_x
from transmission_input_installation_parts import formed_pin

V=App.Vector
X,Y,Z=V(1,0,0),V(0,1,0),V(0,0,1)


def clean(s):
    result=s.copy().removeSplitter()
    return result if result.isValid() and len(result.Solids)==1 else s


def cylinder_z(radius,low,high):
    assert high>low
    return Part.makeCylinder(radius,high-low,V(0,0,low),Z)


def annulus_z(outer,inner,low,high):
    return cylinder_z(outer,low,high).cut(cylinder_z(inner,low-1,high+1))


def rounded_window(width,low,high,radius,reach):
    """Exact rounded rectangle in YZ, extruded along X."""
    w=width/2;r=radius
    assert high-low>2*r and w>r
    s=box(-reach,reach,-w+r,w-r,low,high).fuse(box(-reach,reach,-w,w,low+r,high-r))
    for y in [-w+r,w-r]:
        for z in [low+r,high-r]:
            s=s.fuse(Part.makeCylinder(r,2*reach,V(-reach,y,z),X))
    return clean(s)


def parts(c,main_phase=90.,progress=None):
    def audit(name,s):
        assert s.isValid() and len(s.Solids)==1 and s.Volume>0,(name,len(s.Solids))
        if progress:progress(name,s)
    shapes={};occ=[];groups=[];teeth={};gears={};backs={}
    for key,n,mate,face,rotation,offset in [
        ('upper',c['upper_teeth'],33,c['upper_face'],-90,0),
        ('lower',c['lower_teeth'],c['pump_mate_teeth'],c['lower_face'],90,-c['pump_axis_drop'])]:
        one,d=tooth(n,mate,25.4/c['module'],25.4/c['module'],face,
                    c['pressure_angle_deg'],c['tooth_thinning'],c['flank_samples'])
        ro,yo=d['root_radial_axial_outer_mm'];ri,yi=d['root_radial_axial_inner_mm']
        embed=c['root_embed'];back=yo+embed
        blank=revolve([(0,yi-embed),(ri,yi-embed),(ro,yo-embed),(ro,back),(0,back)])
        # Parent canonical main angle90 places one tooth down. The pinion
        # presents a gap toward -X and follows any later parent phase change.
        phase=180/n-33/n*(main_phase-90) if key=='upper' else c['lower_tooth_phase_deg']
        s=blank.multiFuse(repeated_teeth(one,n,phase));audit(key+'_gear',s)
        s.rotate(V(),X,rotation);s.translate(V(0,0,offset))
        gears[key]=s;teeth[key]=d;backs[key]=offset+(-back if rotation<0 else back)
    lo,hi=backs['lower'],backs['upper'];assert hi-lo>4*c['housing_end_stock']
    driver=gears['upper'].fuse(gears['lower']).fuse(cylinder_z(c['shaft_radius'],lo-.2,hi+.2))
    driver=driver.cut(cylinder_z(c['bore_radius'],-c['pump_axis_drop']-1,1))
    for n in range(c['spline_count']):
        slot=box(c['bore_radius']-.5,c['bore_radius']+c['spline_depth'],
                 -c['spline_width']/2,c['spline_width']/2,lo-c['lower_face']-4,lo+c['spline_length'])
        slot.rotate(V(),Z,n*360/c['spline_count']);driver=driver.cut(slot)
    shapes['driver']=clean(driver)
    blo,bhi=lo+c['endplay']/2,hi-c['endplay']/2;mid=(blo+bhi)/2
    bore=c['shaft_radius']+c['diametrical_clearance']/2
    flange=c['bush_flange_stock']
    bush=annulus_z(c['bush_radius'],bore,blo,bhi)
    bush=bush.fuse(annulus_z(c['bush_flange_radius'],bore,blo,blo+flange))
    bush=bush.fuse(annulus_z(c['bush_flange_radius'],bore,bhi-flange,bhi))
    bush=bush.common(box(0,60,-60,60,blo-1,bhi+1))
    groove=cylinder_z(c['oil_groove_radius'],blo+c['dowel_end_offset'],bhi-c['dowel_end_offset'])
    groove.translate(V(bore,0,0));bush=bush.cut(groove)
    oil=Part.makeCylinder(c['oil_port_diameter']/2,45,V(0,0,bhi-c['dowel_end_offset']),X)
    dowel_z=blo+c['dowel_end_offset'];dr=c['dowel_diameter']/2
    dowel_hole=Part.makeCylinder(dr+c['fastener_gap'],45,V(0,0,dowel_z),X)
    bush=bush.cut(oil).cut(dowel_hole);shapes['bush']=clean(bush)

    hlo,hhi=blo+c['housing_end_relief'],bhi-c['housing_end_relief']
    h=annulus_z(c['housing_radius'],c['bush_radius']+c['bush_housing_gap'],hlo,hhi)
    h=h.cut(cylinder_z(c['bush_flange_radius']+c['bush_housing_gap'],hlo-1,blo+flange))
    h=h.cut(cylinder_z(c['bush_flange_radius']+c['bush_housing_gap'],bhi-flange,hhi+1))
    # Two broad windows per half retain end collars, middle bridge and side posts.
    for a,b in [(hlo+c['housing_end_stock'],mid-c['center_bridge_stock']/2),
                (mid+c['center_bridge_stock']/2,hhi-c['housing_end_stock'])]:
        h=h.cut(rounded_window(2*c['window_half_width'],a,b,c['window_corner_radius'],50))
    clamp_r=c['clamp_diameter']/2+c['fastener_gap'];grip=c['clamp_grip']
    for y in [-c['clamp_offset'],c['clamp_offset']]:
        # Opposed recessed flats leave the source bolt's full length available
        # for14mm grip, two1mm washers,6.35mm nut and exposed drilled tail.
        for sign in [-1,1]:
            xa,xb=(grip/2,50) if sign>0 else (-50,-grip/2)
            h=h.cut(box(xa,xb,y-c['washer_radius']-1,y+c['washer_radius']+1,
                        mid-c['washer_radius']-1,mid+c['washer_radius']+1))
        h=h.cut(Part.makeCylinder(clamp_r,100,V(-50,y,mid),X))
    # Top radial oil entry continues through the aluminium collar to the bush.
    h=h.cut(oil)
    opposite=oil.copy();opposite.rotate(V(),Z,180);h=h.cut(opposite)
    flywheel=h.common(box(-60,0,-60,60,hlo-1,hhi+1))
    distributor=h.common(box(0,60,-60,60,hlo-1,hhi+1))
    distributor=distributor.cut(dowel_hole)
    screw_start=c['retaining_tip_radius'];sr=c['retaining_screw_diameter']/2
    screw_hole=Part.makeCylinder(sr+c['fastener_gap'],60-screw_start+.1,
                               V(screw_start-.1,0,mid),X)
    distributor=distributor.cut(screw_hole)
    shapes['housing_flywheel'],shapes['housing_distributor']=clean(flywheel),clean(distributor)
    shapes['dowel']=cyl(dr,0,c['dowel_length'])
    shapes['washer']=ring(c['washer_radius'],c['clamp_diameter']/2+c['fastener_gap'],0,c['washer_stock'])
    stack=grip+2*c['washer_stock'];pin_station=stack+c['nut_stock']-c['castle_depth']/2
    bolt=hex_x(c['clamp_head_af'],-c['clamp_head_stock'],0).fuse(cyl(c['clamp_diameter']/2,0,c['clamp_length']))
    bolt=bolt.cut(Part.makeCylinder(c['cotter_diameter']/2+c['cotter_hole_gap'],20,V(pin_station,-10,0),Y))
    shapes['bolt']=clean(bolt)
    nut=hex_x(c['nut_af'],0,c['nut_stock']-c['castle_depth']).fuse(
        cyl(c['nut_crown_radius'],c['nut_stock']-c['castle_depth'],c['nut_stock']))
    nut=nut.cut(cyl(c['clamp_diameter']/2+c['fastener_gap'],-1,c['nut_stock']+1))
    for angle in [0,60,120]:
        slot=box(c['nut_stock']-c['castle_depth'],c['nut_stock']+1,-20,20,
                 -(c['cotter_diameter']+.25)/2,(c['cotter_diameter']+.25)/2)
        slot.rotate(V(),X,angle);nut=nut.cut(slot)
    shapes['nut']=clean(nut)
    pin_controls=dict(cotter_center_spacing=.52*c['cotter_diameter'],cotter_diameter=c['cotter_diameter'],
        crown_radius=c['nut_crown_radius'],cotter_head_gap=.15,cotter_exit_gap=.15,
        cotter_bend_radius=.7,cotter_bend_angle=35,cotter_length=c['cotter_length'],
        cotter_eye_radius=1.2,cotter_eye_rise=.6,cotter_eye_join_overlap=.02)
    shapes['cotter'],pin_report=formed_pin(pin_controls)
    length=c['retaining_screw_length']
    shapes['retaining_screw']=clean(cyl(sr,0,length).fuse(
        hex_x(c['retaining_head_af'],length,length+c['retaining_head_stock'])))
    def add(key,name,base=V(),rotation=None,group='EngineLowerDistributionDrive'):
        occ.append(dict(key=key,name='EngineLowerDrive_'+name,assembly=group,xyz=list(base),
                        rotation=list((rotation or App.Rotation()).Q)))
    add('driver','IntegralDriver');add('bush','DistributorBush')
    add('bush','FlywheelBush',rotation=App.Rotation(Z,180))
    add('housing_flywheel','FlywheelHousing');add('housing_distributor','DistributorHousing')
    add('dowel','BushDowel',V(c['dowel_tip_radius'],0,dowel_z))
    add('retaining_screw','HousingRetainingScrew',V(screw_start,0,mid))
    for n,y in enumerate([-c['clamp_offset'],c['clamp_offset']],1):
        name='EngineLowerDriveClampSet'+str(n)
        groups.append(dict(name=name,parent='EngineLowerDistributionDrive',
                           xyz=[-grip/2-c['washer_stock'],y,mid],rotation=[0,0,0,1]))
        add('bolt','ClampBolt'+str(n),group=name)
        add('washer','HeadWasher'+str(n),group=name)
        add('washer','NutWasher'+str(n),V(grip+c['washer_stock'],0,0),group=name)
        add('nut','ClampNut'+str(n),V(stack,0,0),group=name)
        add('cotter','ClampCotter'+str(n),V(pin_station,0,0),group=name)
    for key,s in shapes.items():audit(key,s)
    assert len(occ)==17
    return shapes,occ,groups,dict(teeth=teeth,gear_back_z=backs,journal_span=[lo,hi],
        bearing_span=[blo,bhi],housing_span=[hlo,hhi],mid_z=mid,bearing_bore_radius=bore,
        clamp_stack=stack,clamp_tail=c['clamp_length']-stack-c['nut_stock'],
        cotter_station=pin_station,cotter_controls=pin_controls,cotter=pin_report,
        dowel_z=dowel_z,retaining_screw_span=[screw_start,screw_start+length],
        pump_axis_z=-c['pump_axis_drop'])
