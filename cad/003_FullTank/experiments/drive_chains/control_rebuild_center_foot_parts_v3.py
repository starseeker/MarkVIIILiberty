"""Source-correct M640 single-ended arm and M641 vertical-journal floor bracket.

Geometry dimensions remain estimates. HB92 topology supersedes the rejected
opposite-arm/transverse-floor-journal prototype; see source_review02.
"""
import FreeCAD as App
import Part
from rear_control_channel_mount_parts import formed_rivet, prism_xy
from transmission_input_installation_parts import formed_pin
V=App.Vector
X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)

def parts(c):
    t=c['base_stock'];h=c['pivot_height'];jr=c['journal_diameter']/2
    foot=prism_xy(c['foot_vertices'],t)
    shoulder_top=h-c['hub_width']/2
    bracket=foot.fuse(Part.makeCylinder(c['boss_diameter']/2,shoulder_top,Z*0))
    bracket=bracket.fuse(Part.makeCylinder(jr,h+28.575,Z*0))
    for x,y in c['rivet_centers']:
        bracket=bracket.cut(Part.makeCylinder(c['rivet']['hole_diameter']/2,t+2,V(x,y,-1)))
    bracket=bracket.cut(Part.makeCylinder(c['keeper_hole_diameter']/2,2*jr+2,
        V(-jr-1,0,h+c['keeper_station_y']),X))
    hw=c['hub_width'];ew=c['eye_width'];outer=c['arm_radius']
    rocker=Part.makeCylinder(c['boss_diameter']/2,hw,V(0,-hw/2,0),Y)
    rocker=rocker.fuse(Part.makeBox(17.145,ew,outer,V(-8.5725,-ew/2,0)))
    for radius in [c['inner_arm_radius'],outer]:
        rocker=rocker.fuse(Part.makeCylinder(c['eye_diameter']/2,ew,V(0,-ew/2,radius),Y))
    # Receiver voids are cut after every material union.
    rocker=rocker.cut(Part.makeCylinder(c['journal_bore']/2,hw+2,V(0,-hw/2-1,0),Y))
    for radius in [c['inner_arm_radius'],outer]:
        rocker=rocker.cut(Part.makeCylinder(c['eye_bore']/2,ew+2,V(0,-ew/2-1,radius),Y))
    rivet,rd=formed_rivet(c['rivet'],t+c['floor_stock'])
    keeper,kd=formed_pin(c['keeper'])
    shapes=dict(Def_CenterFootBracket_Redo=bracket,Def_ControlRocker_Redo=rocker,
        Def_CenterFootRivet_Redo=rivet,Def_CenterFootKeeper_Redo=keeper)
    for name,s in shapes.items():
        assert s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed(),name
    return shapes,dict(rivet=rd,keeper=kd)
