"""Drill the shared plunger head and sweep a length-constrained retaining wire."""
import FreeCAD as App
import Part
from clutch_collar_parts import locking_wire


def build(c,parent_report,plunger_blank):
    pc=parent_report['controls'];d=parent_report['datums']
    length=pc['plunger_length'];height=pc['plunger_head_height'];radius=pc['plunger_head_radius']
    hole_x=length-height/2
    assert c['wire_diameter']/2<c['head_drill_radius']<height/2
    assert plunger_blank.Placement.isIdentity()
    hole=Part.makeCylinder(c['head_drill_radius'],2*(radius+1),App.Vector(hole_x,0,-radius-1),App.Vector(0,0,1))
    plunger=plunger_blank.cut(hole).removeSplitter()
    # One shared shape; each installed head's transverse bore is tangent to its circle.
    occurrences=[dict(r) for r in parent_report['occurrences'] if r['key']=='plunger']
    import math
    pitch=(occurrences[0]['xyz'][1]**2+occurrences[0]['xyz'][2]**2)**.5
    for row in occurrences:row['angle']=math.degrees(math.atan2(row['xyz'][2],row['xyz'][1]))
    params=dict(c,joint_face=d['plunger_tail']+hole_x,collar_lip_stock=0.,bolt_head_height=0.,bolt_circle=pitch)
    wire,spine,wd=locking_wire(params)
    assert all(s.isValid() and len(s.Solids)==1 for s in [plunger,wire])
    return plunger,wire,spine,occurrences,dict(wd,head_hole_x_local=hole_x,wire_plane=params['joint_face'],
        pitch_radius=pitch,head_wall_axial=height/2-c['head_drill_radius'],head_height=height,
        plunger_tail=d['plunger_tail'],head_radius=radius)
