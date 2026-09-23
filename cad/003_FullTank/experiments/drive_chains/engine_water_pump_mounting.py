"""Estimated case mounting pads, in lower-case definition coordinates (mm)."""
import FreeCAD as App
from engine_water_pump_parts import flange, clean
from engine_crankshaft_parts import cyl


def revise_case(original, c, pump_frame, mount):
    face=mount['case_face_x'];lo=face-c['case_mount_flange_stock']
    # Preserve the established pump receiving bore; the added flange and four
    # ears provide real material behind all four source-length mounting studs.
    pads,centers=flange(c['retainer_flange_radius'],56.,lo,face,
        c['mount_bolt_radius'],c['mount_ear_radius'],4,c['mount_angle_deg'],0)
    holes=[cyl(c['mount_stud_diameter']/2+c['case_mount_bore_clearance'],
        face-c['mount_stud_embed']-.5,face+1,y,z) for y,z in centers]
    pads.Placement=pump_frame.multiply(pads.Placement)
    result=original.fuse(pads)
    for hole in holes:
        hole.Placement=pump_frame.multiply(hole.Placement);result=result.cut(hole)
    result=clean(result)
    return result,dict(case_definition_pump_frame=list(pump_frame.toMatrix().A),
        blind_depth_mm=c['mount_stud_embed']+.5,flange_stock_mm=c['case_mount_flange_stock'],
        pump_open_radius_mm=56.,estimated_casting=True)
