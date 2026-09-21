"""Paired M265/M266 brake-bearing reconstruction with explicit inferred fits.

A common bush supports adjacent M277 neck and M269 hub journals. The stationary
rear saddle is reconstructed as an extension of M263, closed by M266. This
architecture is a section-led hypothesis, not an original manufacturing drawing.
"""
import FreeCAD as App
import Part
from transmission_core_parts import cylinder, revolve, box
from transmission_stud_parts import cylinder_x


def brake_bearing_parts(c, old_case, old_drum, old_plain_case, nut):
    lo=c['bush_low'];hi=c['bush_high'];flange=c['bush_flange_stock']
    seat_lo=lo+flange;seat_hi=hi-flange;mid=(lo+hi)/2
    bore=c['journal_radius']+c['running_gap'];outer=c['bush_radius']
    assert lo < seat_lo < c['dowel_y'] < seat_hi < hi
    bush=cylinder(outer,lo,hi).fuse(cylinder(c['bush_flange_radius'],lo,seat_lo)).fuse(cylinder(c['bush_flange_radius'],seat_hi,hi))
    bush=bush.cut(cylinder(bore,lo-1,hi+1))
    profile=[(outer,seat_lo),(c['cap_end_radius'],seat_lo),
        (c['cap_radius'],seat_lo+c['cap_end_taper']),(c['cap_radius'],seat_hi-c['cap_end_taper']),
        (c['cap_end_radius'],seat_hi),(outer,seat_hi)]
    shell=revolve(profile)
    cap=shell.common(box(c['split_gap'],200,lo-1,hi+1,-200,200))
    saddle=shell.common(box(-250,-c['split_gap'],lo-1,hi+1,-200,200))
    # Rear bridge passes outside the high-speed drum. A tapered web connects
    # it to the rear semicircular saddle; transverse thickness is inferred.
    bridge=box(c['bridge_back'],c['bridge_front'],c['bridge_root_y'],seat_hi,
        -c['bridge_half_height'],c['bridge_half_height'])
    web=box(c['bridge_back'],-70,seat_lo,seat_hi,-c['web_half_height'],c['web_half_height'])
    web=web.cut(cylinder(outer,lo-1,hi+1))
    rear=saddle.fuse(bridge).fuse(web)
    axes=[]
    for sign in [-1,1]:
        z=sign*c['stud_axis_z'];axes.append([mid,z])
        rear=rear.fuse(cylinder_x(c['ear_radius'],c['stud_start']-c['blind_stock'],-c['split_gap'],mid,z))
        cap=cap.fuse(cylinder_x(c['ear_radius'],c['split_gap'],c['nut_seat'],mid,z))
        receiver=cylinder_x(c['stud_diameter']/2+c['hole_gap'],c['stud_start']-c['blind_gap'],c['nut_seat']+1,mid,z)
        rear=rear.cut(receiver);cap=cap.cut(receiver)
        cap=cap.cut(cylinder_x(c['nut_relief_radius'],c['nut_seat'],150,mid,z))
    # Bush flanges locate it axially in both half saddles.
    rear=rear.cut(cylinder(c['bush_flange_radius']+.15,lo-.5,seat_lo)).cut(cylinder(c['bush_flange_radius']+.15,seat_hi,hi+.5))
    cap=cap.cut(cylinder(outer,lo-1,hi+1));rear=rear.cut(cylinder(outer,lo-1,hi+1))
    pin_hole=cylinder_x(c['dowel_diameter']/2+c['dowel_hole_gap'],c['dowel_start']-c['blind_gap'],c['cap_radius']+1,c['dowel_y'],0)
    bush=bush.cut(pin_hole);cap=cap.cut(pin_hole)
    # Retain the already qualified M269 spline, ring pocket, web and rim.
    # Only thicken the journal outside its former R58 envelope.
    old_r=c['old_drum_hub_radius'];drum_end=old_drum.copy().cleaned().BoundBox.YMax
    hub_add=cylinder(c['journal_radius'],c['drum_hub_start'],drum_end).cut(cylinder(old_r-.1,c['drum_hub_start']-1,drum_end+1))
    drum=old_drum.fuse(hub_add).removeSplitter()
    case=old_case.copy()
    for sign in [1,-1]:
        placed=rear.copy()
        if sign<0:placed.rotate(App.Vector(),App.Vector(1,0,0),180)
        case=case.fuse(placed)
    tip=c['stud_start']+c['stud_length'];pin=c['nut_seat']+c['nut_height']-c['slot_depth']/2
    stud=cylinder_x(c['stud_diameter']/2,c['stud_start'],tip)
    stud=stud.cut(Part.makeCylinder(c['cotter_diameter']/2+c['cotter_hole_gap'],c['stud_diameter']+2,
        App.Vector(pin,-c['stud_diameter']/2-1,0),App.Vector(0,1,0)))
    shapes=dict(bush=bush,cap=cap,stud=stud,nut=nut.copy(),case=case,drum=drum)
    shapes={key:shape.removeSplitter() for key,shape in shapes.items()}
    for key,s in shapes.items():
        assert s.isValid() and len(s.Solids)==1,(key,s.isValid(),len(s.Solids))
    d=dict(bush_limits_y_mm=[lo,hi],cap_limits_y_mm=[seat_lo,seat_hi],stud_axes_yz_mm=axes,
        journal_radius_mm=c['journal_radius'],bush_bore_mm=bore,stud_tip_mm=tip,
        US_thread_limits_mm=[c['stud_start'],c['stud_start']+c['US_thread_length']],
        SAE_thread_limits_mm=[tip-c['SAE_thread_length'],tip],cotter_axis_mm=pin,
        dowel_origin_mm=[c['dowel_start'],c['dowel_y'],0],
        journal_gap_y_mm=[drum_end,old_plain_case.copy().cleaned().BoundBox.YMin],
        drum_bearing_overlap_mm=min(drum_end,hi)-lo,
        plain_case_bearing_overlap_mm=hi-max(lo,old_plain_case.copy().cleaned().BoundBox.YMin))
    return shapes,d
