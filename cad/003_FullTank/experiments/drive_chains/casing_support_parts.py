"""Assumed Z-section casing supports tied to retained hull receiving planes."""
import FreeCAD as App
import Part
from casing_mount_parts import cutter


def support(a,casing,route,shell,sign,receiver_local_y,hull_stock):
    t=a['bracket_stock'];half=casing['outside_width']/2
    x=shell['dimensions']['cap_seam_x_mm']+a['bracket_forward_offset']
    z=route['roller_pinion_axis_xz_mm'][1]+a['bracket_web_axis_offset']
    x0=x-a['bracket_width']/2
    def box(y0,y1,z0,z1):
        y0,y1=sorted([y0,y1]);return Part.makeBox(a['bracket_width'],y1-y0,z1-z0,App.Vector(x0,y0,z0))
    case=box(sign*half,sign*(half+t),z,z+a['case_leg_height'])
    web=box(sign*half,receiver_local_y,z,z+t)
    foot=box(receiver_local_y-sign*t,receiver_local_y,z-a['hull_leg_drop'],z+t)
    shape=case.multiFuse([web,foot]).removeSplitter()
    case_grip=casing['sheet_stock']+t;stations=[]
    for count,height in [(4,z+a['case_rivet_vertical_end']),(3,z+a['case_leg_height']-a['case_rivet_vertical_end'])]:
        for n in range(count):
            xx=x0+a['case_rivet_end']+n*(a['bracket_width']-2*a['case_rivet_end'])/(count-1)
            stations.append(dict(center=[xx,sign*(half+(t-casing['sheet_stock'])/2),height],axis=[0,sign,0],grip=case_grip))
    bolts=[dict(center=[x+dx,receiver_local_y+sign*(hull_stock-t)/2,z-a['hull_leg_drop']/2],
                axis=[0,sign,0],grip=hull_stock+t) for dx in [-a['hull_bolt_halfpitch'],a['hull_bolt_halfpitch']]]
    for s in stations:shape=shape.cut(cutter(s,a['case_rivet_diameter']+a['hole_diameter_clearance']))
    for s in bolts:shape=shape.cut(cutter(s,12.7+a['hole_diameter_clearance']))
    shape=shape.removeSplitter()
    if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid support bracket')
    return shape,dict(case_rivets=stations,hull_bolts=bolts),dict(center_x_mm=x,web_base_z_mm=z,
         case_face_local_y_mm=sign*half,hull_face_local_y_mm=receiver_local_y,span_mm=abs(receiver_local_y)-half)
