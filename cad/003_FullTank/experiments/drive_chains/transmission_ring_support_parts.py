"""Correct the M318 station and reconstruct recessed ring-bolt receivers.

Callout15 identifies the inner bolt in Plate22. The previously compared outer
bolt belongs to the case joint and must not control this pin-ring installation.
"""
import math
import FreeCAD as App
import Part

from transmission_pin_parts import pin_parts,positioned
from transmission_core_parts import cylinder,revolve
from transmission_stud_parts import hex_x


def revised_ring_supports(base,controls,gear,original_carrier):
    c=dict(base)
    for name in ['bolt_circle_radius','bolt_boss_back_y','bolt_boss_radius','post_radius']:
        c[name]=controls[name]
    # Rebuild from the pre-support carrier so no obsolete radius202mm receiver
    # or bore survives. All large-planet pin and sleeve controls are retained.
    shapes,carrier,dimensions=pin_parts(c,gear,original_carrier)
    ring=shapes['pin_ring'];low,high=dimensions['ring_faces_y_mm']
    envelope=revolve(c['pin_boss_envelope_profile'])
    seat=controls['bolt_head_seat_y'];end=dimensions['bolt_fastening']['tip_y_mm']
    shank=cylinder(c['bolt_diameter']/2,seat,end)
    head=hex_x(c['bolt_head_af'],-c['bolt_head_stock'],0)
    head.rotate(App.Vector(),App.Vector(0,0,1),90);head.translate(App.Vector(0,seat,0))
    drill=Part.makeCylinder(c['bolt_cotter_diameter']/2+c['cotter_hole_gap'],c['bolt_diameter']+2,
        App.Vector(-c['bolt_diameter']/2-1,dimensions['bolt_fastening']['cotter_axis_y_mm'],0),App.Vector(1,0,0))
    shapes['bolt']=shank.fuse(head).cut(drill).removeSplitter()
    for n in range(3):
        angle=n*2*math.pi/3+math.pi/3;radius=c['bolt_circle_radius']
        boss=positioned(cylinder(c['bolt_boss_radius'],c['bolt_boss_front_y'],650),radius,angle).common(envelope)
        recess=positioned(cylinder(controls['bolt_nut_recess_radius'],c['bolt_boss_back_y'],651),radius,angle)
        bore=positioned(cylinder(c['bolt_diameter']/2+c['pin_hole_gap'],low-1,c['bolt_boss_back_y']+1),radius,angle)
        carrier=carrier.fuse(boss).cut(recess).cut(bore)
        # The shorter source-positioned head seats in the projecting ring boss.
        # An inferred counterbore keeps its axial insertion/access path open.
        access=positioned(cylinder(controls['bolt_head_access_radius'],low-1,seat),radius,angle)
        ring=ring.cut(access)
    result={name:shapes[name] for name in ['bolt','bolt_nut','bolt_cotter']}
    result.update(pin_ring=ring.removeSplitter(),carrier=carrier.removeSplitter())
    for name,shape in result.items():
        assert shape.isValid() and len(shape.Solids)==1,name
    dimensions.update(bolt_head_seat_y_mm=seat,bolt_head_access_radius_mm=controls['bolt_head_access_radius'],
        bolt_circle_radius_mm=c['bolt_circle_radius'],bolt_nut_recess_radius_mm=controls['bolt_nut_recess_radius'],
        bolt_head_faces_y_mm=[seat-c['bolt_head_stock'],seat],
        bolt_shank_length_mm=end-seat,
        bolt_nut_recess_min_nominal_wall_mm=c['bolt_boss_radius']-controls['bolt_nut_recess_radius'],
        bolt_counterbore_min_nominal_wall_mm=c['post_radius']-controls['bolt_head_access_radius'])
    return result,dimensions
