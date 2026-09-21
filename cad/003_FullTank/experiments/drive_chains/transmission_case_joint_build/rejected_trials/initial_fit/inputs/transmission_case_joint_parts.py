"""M263/M264 joint: inferred flange lands, fourteen MX8 sets and two M326 seals.

The source establishes identities and quantities, not the full bolt pattern or
machining dimensions. Existing case and bearing datums remain authoritative.
"""
import FreeCAD as App
import Part
from transmission_stud_parts import cylinder_x, hex_x


def mating_faces(shape, station):
    return Part.makeCompound([f for f in shape.Faces
        if f.BoundBox.XLength < 1e-6 and abs(f.BoundBox.XMin-station) < 1e-6])


def case_joint_parts(c, old_case, old_cover):
    gap=c['joint_gap'];seat=c['half_grip'];radius=c['flange_radius']
    case=old_case.copy();cover=old_cover.copy();holes=[];reliefs=[]
    axes=[(y,sign*z) for sign in [1,-1] for y,z in c['upper_axes_yz']]
    for y,z in axes:
        case=case.fuse(cylinder_x(radius,-seat,-gap/2,y,z))
        cover=cover.fuse(cylinder_x(radius,gap/2,seat,y,z))
        holes.append(cylinder_x(c['bolt_diameter']/2+c['receiver_gap'],-seat-1,seat+1,y,z))
        # Flat lands provide real bearing faces and room for the head/nut.
        reliefs.extend([cylinder_x(radius,-seat-35,-seat,y,z),
                        cylinder_x(radius,seat,seat+35,y,z)])
    cutters=Part.makeCompound(holes+reliefs)
    case=case.cut(cutters).removeSplitter();cover=cover.cut(cutters).removeSplitter()
    # Use the rear casting's two planar lands. The nominal gasket thickness
    # fills the existing split. Support on the cover is checked independently.
    # Exclude the four disconnected brake-cap lands at larger transverse Y.
    faces=[f for f in mating_faces(case,-gap/2).Faces if abs(f.CenterOfMass.y)<1]
    seals=[f.extrude(App.Vector(gap,0,0)) for f in faces]
    assert len(seals)==2,[(s.Volume,str(s.BoundBox)) for s in seals]
    seals.sort(key=lambda s:s.CenterOfMass.z,reverse=True)
    bolt=cylinder_x(c['bolt_diameter']/2,-seat,seat+c['nut_height']+c['end_projection'])
    bolt=bolt.fuse(hex_x(c['head_af'],-seat-c['head_height'],-seat))
    pin=seat+c['nut_height']-c['slot_depth']/2
    bolt=bolt.cut(Part.makeCylinder(c['cotter_diameter']/2+c['cotter_hole_gap'],c['bolt_diameter']+2,
        App.Vector(pin,-c['bolt_diameter']/2-1,0),App.Vector(0,1,0)))
    shapes=dict(case=case,cover=cover,bolt=bolt,gasket_upper=seals[0],gasket_lower=seals[1])
    shapes={k:s.removeSplitter() for k,s in shapes.items()}
    for name,s in shapes.items():assert s.isValid() and len(s.Solids)==1,(name,s.isValid(),len(s.Solids))
    return shapes,dict(axes_yz_mm=axes,head_seat_x_mm=-seat,nut_seat_x_mm=seat,cotter_axis_x_mm=pin,
        bolt_tip_x_mm=seat+c['nut_height']+c['end_projection'],
        bolt_underhead_length_mm=2*seat+c['nut_height']+c['end_projection'],
        thread_limits_x_mm=[seat-c['thread_runin'],seat+c['nut_height']+c['end_projection']],
        gasket_volumes_mm3=[s.Volume for s in seals],gasket_thickness_mm=gap,
        added_case_mm3=case.cut(old_case).Volume,removed_case_mm3=old_case.cut(case).Volume,
        added_cover_mm3=cover.cut(old_cover).Volume,removed_cover_mm3=old_cover.cut(cover).Volume)
