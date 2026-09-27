"""Estimated M641/M640 cast forms with explicit journal and floor attachment stock."""
import FreeCAD as App
import Part
from rear_control_channel_mount_parts import formed_rivet, prism_xy
from transmission_input_installation_parts import formed_pin
V=App.Vector
Y=V(0,1,0)
Z=V(0,0,1)


def parts(c):
    t=c['base_stock'];h=c['pivot_height'];jr=c['journal_diameter']/2
    foot=prism_xy(c['foot_vertices'],t)
    points=[V(-24,-40,t),V(24,-40,t),V(15,-40,h),V(-15,-40,h)]
    web=Part.Face(Part.makePolygon(points+[points[0]])).extrude(Y*8)
    shoulder=Part.makeCylinder(c['boss_diameter']/2,23,V(0,-40,h),Y)
    journal=Part.makeCylinder(jr,68.575,V(0,-40,h),Y)
    bracket=foot.fuse(web).fuse(shoulder).fuse(journal)
    for x,y in c['rivet_centers']:
        bracket=bracket.cut(Part.makeCylinder(c['rivet']['hole_diameter']/2,t+2,V(x,y,-1),Z))
    bracket=bracket.cut(Part.makeCylinder(c['keeper_hole_diameter']/2,2*jr+2,
                         V(0,c['keeper_station_y'],h-jr-1),Z))

    hw=c['hub_width'];ew=c['eye_width'];arm=c['arm_radius']
    rocker=Part.makeCylinder(c['boss_diameter']/2,hw,V(0,-hw/2,0),Y)
    for sign in [-1,1]:
        eye=Part.makeCylinder(c['eye_diameter']/2,ew,V(0,-ew/2,sign*arm),Y)
        bridge=Part.makeBox(17.145,ew,arm,V(-8.5725,-ew/2,min(0,sign*arm)))
        rocker=rocker.fuse(eye).fuse(bridge)
    # Cut all three bores after every union, so arm stock cannot fill a journal.
    rocker=rocker.cut(Part.makeCylinder(c['journal_bore']/2,hw+2,V(0,-hw/2-1,0),Y))
    for sign in [-1,1]:
        rocker=rocker.cut(Part.makeCylinder(c['eye_bore']/2,ew+2,V(0,-ew/2-1,sign*arm),Y))

    rivet,rd=formed_rivet(c['rivet'],t+c['floor_stock'])
    keeper,kd=formed_pin(c['keeper'])
    shapes=dict(Def_CenterFootBracket_Redo=bracket,Def_ControlRocker_Redo=rocker,
                Def_CenterFootRivet_Redo=rivet,Def_CenterFootKeeper_Redo=keeper)
    for name,shape in shapes.items():
        assert shape.Placement.isIdentity() and shape.isValid() and len(shape.Solids)==1 and shape.Solids[0].isClosed(),name
    return shapes,dict(rivet=rd,keeper=kd)
