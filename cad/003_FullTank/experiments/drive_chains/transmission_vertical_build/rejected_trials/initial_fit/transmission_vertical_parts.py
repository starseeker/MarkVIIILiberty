"""Vertical reversing shaft, keyed levers, opposed bearings and their mountings.

The two bearing forms share a definition. The opposed blind journals and the
upper lever's integral rounded finger are documented reconstruction hypotheses.
"""
import math
import FreeCAD as App
import Part
from transmission_stud_parts import cylinder_x,hex_x


def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,App.Vector(x0,y0,z0))
def zc(r,z0,z1,x=0,y=0):return Part.makeCylinder(r,z1-z0,App.Vector(x,y,z0))
def xc(r,x0,x1,y=0,z=0):return Part.makeCylinder(r,x1-x0,App.Vector(x0,y,z),App.Vector(1,0,0))


def key_disk(c,extra=0):
    radial=c['journal_radius']+c['key_exposure'];r=c['key_radius']+extra;w=c['key_width']+2*extra
    disk=Part.makeCylinder(r,w,App.Vector(radial,-w/2,0),App.Vector(0,1,0))
    return disk.common(box(radial-r-1,radial+extra,-w,w,-r-1,r+1)).removeSplitter()


def lever_blank(c,length,zmid,hub_low):
    hub=zc(c['lever_hub_radius'],hub_low,hub_low+c['lever_hub_height'])
    width=c['arm_width'];tip=c['arm_tip_width'];start=c['arm_start_x'];end=length
    z=zmid-c['arm_stock']/2
    curves=[]
    for sign in [1,-1]:
        curve=Part.BSplineCurve();curve.interpolate([App.Vector(start,sign*width/2,z),
            App.Vector(length*.48,sign*width*.42,z),App.Vector(end,sign*tip/2,z)])
        curves.append(curve.toShape())
    wire=Part.Wire([curves[0],Part.makeLine(curves[0].Vertexes[-1].Point,curves[1].Vertexes[-1].Point),
        curves[1].reversed(),Part.makeLine(curves[1].Vertexes[0].Point,curves[0].Vertexes[0].Point)])
    arm=Part.Face(wire).extrude(App.Vector(0,0,c['arm_stock']))
    shape=hub.fuse(arm).cut(zc(c['journal_radius']+c['journal_gap'],hub_low-1,hub_low+c['lever_hub_height']+1))
    return shape


def vertical_parts(c,old_case,old_rod):
    x,y=c['shaft_xy'];top=c['upper_bearing_base_z'];bottom=c['lower_bearing_open_z']
    upper_seat=top-c['axial_gap'];lower_seat=bottom+c['axial_gap']
    upper_hub_low=upper_seat-c['lever_hub_height'];lower_hub_low=lower_seat
    upper_key_z=upper_hub_low+c['lever_hub_height']/2;lower_key_z=lower_hub_low+c['lever_hub_height']/2
    shaft_low=bottom-c['bearing_depth']+c['axial_gap'];shaft_high=top+c['bearing_depth']-c['axial_gap']
    shaft=zc(c['journal_radius'],shaft_low,shaft_high,x,y).fuse(zc(c['body_radius'],lower_hub_low+c['lever_hub_height'],upper_hub_low,x,y))
    key=key_disk(c);keycut=key_disk(c,c['key_gap']);key_locations=[]
    for z,angle in [(upper_key_z,0),(lower_key_z,c['lower_lever_angle'])]:
        cutter=keycut.copy();cutter.rotate(App.Vector(),App.Vector(0,0,1),angle);cutter.translate(App.Vector(x,y,z));shaft=shaft.cut(cutter)
        key_locations.append(dict(z=z,angle=angle))
    rod_x,rod_z=c['rod_axis_xz'];reach=rod_x-x
    upper=lever_blank(c,reach-c['finger_neck_setback'],rod_z,upper_hub_low)
    neck=xc(c['finger_neck_radius'],reach-c['finger_neck_setback']-c['finger_overlap'],reach)
    neck.translate(App.Vector(0,0,rod_z))
    upper=upper.fuse(neck).fuse(Part.makeSphere(c['finger_radius'],App.Vector(reach,0,rod_z)))
    lower=lever_blank(c,c['lower_arm_length'],lower_key_z,lower_hub_low)
    lower=lower.fuse(zc(c['lower_eye_radius'],lower_key_z-c['arm_stock']/2,lower_key_z+c['arm_stock']/2,c['lower_arm_length'],0))
    lower=lower.cut(zc(c['lower_eye_bore'],lower_key_z-c['arm_stock'],lower_key_z+c['arm_stock'],c['lower_arm_length'],0))
    for k,z,shape in [('upper',upper_key_z,upper),('lower',lower_key_z,lower)]:
        slot=box(c['journal_radius']-1,c['journal_radius']+c['key_exposure']+c['key_gap'],
            -c['key_width']/2-c['key_gap'],c['key_width']/2+c['key_gap'],z-c['key_radius']-c['key_gap'],z+c['key_radius']+c['key_gap'])
        shape=shape.cut(slot)
        if k=='lower':shape.rotate(App.Vector(),App.Vector(0,0,1),c['lower_lever_angle']);lower=shape
        else:upper=shape
    upper.translate(App.Vector(x,y,0));lower.translate(App.Vector(x,y,0))
    # Replace the provisional vertical hole at the rod's free end with a
    # transverse socket for the lever's integral rounded finger. Fill only
    # the old hole inside the original cylindrical rod stock.
    stock=Part.makeCylinder(c['rod_radius'],c['rod_end_stock_length'],App.Vector(rod_x,c['rod_start_y'],rod_z),App.Vector(0,1,0))
    fill=zc(c['rod_hole_radius'],rod_z-c['rod_radius']-1,rod_z+c['rod_radius']+1,rod_x,y).common(stock)
    rod=old_rod.fuse(fill).cut(xc(c['rod_hole_radius'],rod_x-c['rod_radius']-1,rod_x+c['rod_radius']+1,y,rod_z))
    # Bearing local origin is its shaft center at the open journal face.
    seat=c['case_seat_x']-x;back=c['nut_seat_x']-x
    bearing=zc(c['bearing_radius'],0,c['bearing_height'])
    bearing=bearing.fuse(box(back,seat,-c['foot_half_width'],c['foot_half_width'],c['foot_z_margin'],c['bearing_height']-c['foot_z_margin']))
    bearing=bearing.cut(zc(c['journal_radius']+c['journal_gap'],-1,c['bearing_depth']))
    zmid=c['bearing_height']/2
    for dy in [-c['fastener_offset'],c['fastener_offset']]:bearing=bearing.cut(xc(c['fastener_radius']+c['fastener_gap'],back-1,seat+1,dy,zmid))
    # Printed MX12 length sets the embedded end, not a fitted length change.
    stud_tip=c['nut_seat_x']-c['nut_height']-c['tip_projection'];stud_start=stud_tip+c['stud_length']
    pin_axis=c['nut_seat_x']-c['nut_height']+c['nut_slot_depth']/2
    stud=xc(c['fastener_radius'],-c['stud_length'],0)
    stud=stud.cut(Part.makeCylinder(c['cotter_radius']+c['cotter_gap'],20,App.Vector(pin_axis-stud_start,-10,0),App.Vector(0,1,0)))
    bolt_length=c['bolt_head_seat_x']-stud_tip
    bolt=xc(c['fastener_radius'],-bolt_length,0).fuse(hex_x(c['bolt_head_af'],0,c['bolt_head_height']))
    bolt=bolt.cut(Part.makeCylinder(c['cotter_radius']+c['cotter_gap'],20,App.Vector(pin_axis-c['bolt_head_seat_x'],-10,0),App.Vector(0,1,0)))
    case=old_case.copy();mounts=[]
    for label,base,sign in [('Upper',top,1),('Lower',bottom,-1)]:
        z=base+sign*zmid
        land=box(c['case_seat_x'],c['land_front_x'],y-c['land_half_width'],c['land_inner_y'],z-c['land_half_height'],z+c['land_half_height'])
        case=case.fuse(land)
        for kind,dy in [('bolt',c['fastener_offset']),('stud',-c['fastener_offset'])]:
            yy=y+dy
            if kind=='bolt':
                tool=xc(c['fastener_radius']+c['fastener_gap'],c['case_seat_x']-1,c['bolt_head_seat_x']+1,yy,z)
                tool=tool.fuse(xc(c['head_relief_radius'],c['bolt_head_seat_x'],c['head_relief_end_x'],yy,z))
            else:tool=xc(c['fastener_radius']+c['fastener_gap'],c['case_seat_x']-1,stud_start+c['blind_gap'],yy,z)
            case=case.cut(tool)
            mounts.append(dict(label=label,kind=kind,y=yy,z=z,fastener_base_x=stud_start if kind=='stud' else c['bolt_head_seat_x']))
    result=dict(shaft=shaft,upper_lever=upper,lower_lever=lower,key=key,bearing=bearing,stud=stud,bolt=bolt,case=case,rod=rod)
    result={k:s.removeSplitter() for k,s in result.items()}
    for k,s in result.items():assert s.isValid() and len(s.Solids)==1,(k,s.isValid(),len(s.Solids))
    return result,dict(shaft_z_mm=[shaft_low,shaft_high],upper_hub_z_mm=[upper_hub_low,upper_seat],lower_hub_z_mm=[lower_hub_low,lower_hub_low+c['lever_hub_height']],
        key_locations=key_locations,mounts=mounts,stud_start_x_mm=stud_start,stud_tip_x_mm=stud_tip,cotter_axis_x_mm=pin_axis,bolt_underhead_length_mm=bolt_length,
        stud_US_thread_x_mm=[stud_start-c['stud_US_thread_length'],stud_start],stud_SAE_thread_x_mm=[stud_tip,stud_tip+c['stud_SAE_thread_length']],
        upper_finger_center_mm=[rod_x,y,rod_z],lower_link_hole_mm=[x+c['lower_arm_length']*math.cos(math.radians(c['lower_lever_angle'])),y+c['lower_arm_length']*math.sin(math.radians(c['lower_lever_angle'])),lower_key_z],
        rod_added_mm3=rod.cut(old_rod).Volume,rod_removed_mm3=old_rod.cut(rod).Volume,case_added_mm3=case.cut(old_case).Volume,case_removed_mm3=old_case.cut(case).Volume)
