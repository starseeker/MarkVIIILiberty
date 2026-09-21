"""Separate bevel-wheel sleeves, two bearing interfaces and their receiver bosses."""
import math
import FreeCAD as App
import Part
from transmission_core_parts import cylinder,box,spline_envelope


def sleeve_parts(c,core,cal,old_shaft,old_case,old_cover,old_sun,gear):
    axial=lambda x:(c['source_bevel_center_x_px']-x)*cal['mm_per_pixel']
    lo=axial(c['sleeve_inner_face_x_px']);flange_end=axial(c['flange_outer_face_x_px'])
    hi=axial(c['sleeve_outer_end_x_px']);bush_hi=axial(c['outer_bush_end_x_px'])
    case_inner=core['bevel_half_width']-core['bevel_end_stock'];dowel_y=axial(c['dowel_center_x_px'])
    retainer_end=bush_hi+c['retainer_stock']
    assert 0<lo<flange_end<c['screw_axial_station']<case_inner<dowel_y<bush_hi<retainer_end<hi
    bore=c['inner_bush_radius']+c['inner_bush_sleeve_gap']
    sleeve=cylinder(c['sleeve_radius'],lo,hi).fuse(cylinder(c['flange_radius'],lo,flange_end)).cut(cylinder(bore,lo-1,hi+1))
    for n in range(c['flange_hole_count']):
        angle=2*math.pi*n/c['flange_hole_count'];hole=cylinder(c['flange_hole_diameter']/2,lo-1,flange_end+1)
        hole.translate(App.Vector(c['flange_hole_circle']*math.cos(angle),0,c['flange_hole_circle']*math.sin(angle)))
        sleeve=sleeve.cut(hole)
    inner=cylinder(c['inner_bush_radius'],lo,hi).cut(cylinder(c['inner_bush_bore'],lo-1,hi+1))
    screw_hole=Part.makeCylinder(c['screw_diameter']/2+c['hole_radial_gap'],c['sleeve_radius']+1-c['screw_tip_radius']+c['hole_bottom_gap'],
        App.Vector(c['screw_tip_radius']-c['hole_bottom_gap'],c['screw_axial_station'],0),App.Vector(1,0,0))
    inner=inner.cut(screw_hole).removeSplitter();sleeve=sleeve.cut(screw_hole).removeSplitter()
    screw=Part.makeCylinder(c['screw_diameter']/2,c['screw_length'],App.Vector(c['screw_tip_radius'],c['screw_axial_station'],0),App.Vector(1,0,0))
    end=c['screw_tip_radius']+c['screw_length']
    screw=screw.cut(box(end-c['screw_slot_depth'],end+1,c['screw_axial_station']-5,c['screw_axial_station']+5,-c['screw_slot_width']/2,c['screw_slot_width']/2)).removeSplitter()
    outer=cylinder(c['outer_bush_radius'],case_inner,bush_hi).fuse(cylinder(c['outer_bush_flange_radius'],case_inner-c['outer_bush_flange_stock'],case_inner))
    outer=outer.cut(cylinder(c['sleeve_radius']+c['outer_bush_running_gap'],case_inner-c['outer_bush_flange_stock']-1,bush_hi+1))
    dowel_hole=Part.makeCylinder(c['dowel_diameter']/2+c['hole_radial_gap'],c['boss_radius']+1-c['dowel_start_radius']+c['hole_bottom_gap'],
        App.Vector(c['dowel_start_radius']-c['hole_bottom_gap'],dowel_y,0),App.Vector(1,0,0))
    outer=outer.cut(dowel_hole).removeSplitter()
    retainer=cylinder(c['retainer_radius'],bush_hi,retainer_end).cut(cylinder(c['sleeve_radius']+c['retainer_running_gap'],bush_hi-1,retainer_end+1)).removeSplitter()
    shaft=old_shaft.copy();case=old_case.copy();cover=old_cover.copy()
    sun_lo,sun_hi=gear['sun_bush_y_mm']
    sun=old_sun.cut(cylinder(bore,sun_lo-1,sun_hi+1)).removeSplitter()
    sun_bush=cylinder(c['inner_bush_radius'],sun_lo,sun_hi).cut(cylinder(c['inner_bush_bore'],sun_lo-1,sun_hi+1)).removeSplitter()
    clutch_half=lo-c['journal_end_gap']
    # A larger central spline admits a future sliding clutch over the journals.
    # These diameters are an assembly hypothesis, not printed dimensions.
    shaft=shaft.fuse(spline_envelope(c['central_spline_root_radius'],c['central_spline_tip_radius'],
        core['cross_shaft_spline_width'],core['splines'],-clutch_half,clutch_half))
    split=core['bevel_split_gap']/2
    halves=[box(-500,-split,-300,300,-300,300),box(split,500,-300,300,-300,300)]
    for sign in [-1,1]:
        y0,y1=sorted([sign*(lo-c['journal_end_gap']),sign*(hi+c['journal_end_gap'])])
        # The bearing bore must pass the rectangular spline crests during
        # assembly. A root-diameter journal would trap an unsplit bush.
        shaft=shaft.fuse(cylinder(c['shaft_journal_radius'],y0,y1))
        sun_y0,sun_y1=sorted([sign*y for y in gear['shaft_journal_y_mm']])
        shaft=shaft.fuse(cylinder(c['shaft_journal_radius'],sun_y0,sun_y1))
        boss=cylinder(c['boss_radius'],case_inner,retainer_end)
        boretool=cylinder(c['outer_bush_radius'],case_inner-1,retainer_end+1)
        sealtool=cylinder(c['retainer_radius'],bush_hi,retainer_end+1)
        hole=dowel_hole.copy()
        if sign<0:
            for s in [boss,boretool,sealtool,hole]:s.rotate(App.Vector(),App.Vector(1,0,0),180)
        case=case.fuse(boss.common(halves[0])).cut(boretool).cut(sealtool)
        cover=cover.fuse(boss.common(halves[1])).cut(boretool).cut(sealtool).cut(hole)
    shapes=dict(sleeve=sleeve,inner_bush=inner,outer_bush=outer,retainer=retainer,screw=screw)
    revised=dict(shaft=shaft.removeSplitter(),case=case.removeSplitter(),cover=cover.removeSplitter(),sun=sun,sun_bush=sun_bush)
    for name,s in dict(shapes,**revised).items():assert s.isValid() and len(s.Solids)==1,name
    return shapes,revised,dict(sleeve_limits_y_mm=[lo,hi],flange_limits_y_mm=[lo,flange_end],outer_bush_limits_y_mm=[case_inner,bush_hi],
        outer_bush_flange_limits_y_mm=[case_inner-c['outer_bush_flange_stock'],case_inner],retainer_limits_y_mm=[bush_hi,retainer_end],
        dowel_origin_mm=[c['dowel_start_radius'],dowel_y,0],shaft_journal_limits_y_mm=[lo-c['journal_end_gap'],hi+c['journal_end_gap']],
        sun_bush_limits_y_mm=gear['sun_bush_y_mm'],sun_journal_limits_y_mm=gear['shaft_journal_y_mm'],
        central_spline_limits_y_mm=[-clutch_half,clutch_half],
        central_spline_radii_mm=[c['central_spline_root_radius'],c['central_spline_tip_radius']],
        source_registration_center_px=c['source_bevel_center_x_px'],source_to_case_registration='Y=(1534-source_x)*inherited_mm_per_pixel',
        inherited_source_bush_inner_x_px=1378,case_seat_adjustment_from_source_mm=case_inner-axial(1378),
        radial_dimensions_mm={k:c[k] for k in ['sleeve_radius','inner_bush_radius','inner_bush_bore','outer_bush_radius','boss_radius','retainer_radius']})
