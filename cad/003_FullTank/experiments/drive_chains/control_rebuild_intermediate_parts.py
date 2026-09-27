"""Estimated M638/M639 mounting with real receiving stock and source-sized screws."""
import math
import FreeCAD as App
import Part
from rear_control_channel_mount_parts import prism_xy
from transmission_input_installation_parts import formed_pin
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)

def parts(c):
    radius=c['shaft_diameter']/2
    shaft=Part.makeCylinder(radius,c['shaft_length'],V(0,-c['shaft_length']/2,0),Y)
    for sign in [-1,1]:
        shaft=shaft.cut(Part.makeCylinder(c['keeper_bore']/2,2*radius+2,V(0,sign*c['keeper_station_y'],-radius-1),Z))
    height=c['shaft_height']-c['floor_top']-c['strip_thickness']
    width=c['bracket_width'];t=c['foot_stock'];pitch=c['mount_pitch_x']/2
    bracket=Part.makeBox(c['foot_length'],c['foot_width'],t,V(-c['foot_length']/2,-c['foot_width']/2,0))
    web=Part.Face(Part.makePolygon([V(-20,-6,t),V(20,-6,t),V(14,-6,height),V(-14,-6,height),V(-20,-6,t)])).extrude(Y*12)
    bracket=bracket.fuse(web).fuse(Part.makeCylinder(22.225,width,V(0,-width/2,height),Y))
    for sign in [-1,1]:
        bracket=bracket.fuse(Part.makeCylinder(c['mount_boss_diameter']/2,c['mount_boss_height'],V(sign*pitch,0,0)))
    bracket=bracket.cut(Part.makeCylinder(c['journal_bore']/2,width+2,V(0,-width/2-1,height),Y))
    for sign in [-1,1]:
        bracket=bracket.cut(Part.makeCylinder(c['mount_thread_envelope']/2,c['mount_blind_depth']+1,V(sign*pitch,0,-1)))
    strip=Part.makeBox(c['strip_width'],c['strip_length'],c['strip_thickness'],V(-c['strip_width']/2,-c['strip_length']/2,0))
    for y in c['bracket_stations_y']:
        strip=strip.cut(Part.makeCylinder(c['mount_clearance']/2,c['strip_thickness']+2,V(0,y,-1)))
    circum=c['bolt_head_af']/math.sqrt(3)
    head=prism_xy([(circum*math.cos(i*math.pi/3),circum*math.sin(i*math.pi/3)) for i in range(6)],c['bolt_head_height'])
    head.translate(-Z*c['bolt_head_height'])
    screw=Part.makeCylinder(c['bolt_diameter']/2,c['bolt_length']).fuse(head)
    keeper,kd=formed_pin(c['keeper'])
    shapes=dict(Def_ControlIntermediateShaft_Redo=shaft,Def_IntermediateMountBracket_Redo=bracket,
        Def_M3019SupportStrip_Redo=strip,Def_IntermediateMountCapScrew_Redo=screw,Def_IntermediateShaftKeeper_Redo=keeper)
    for name,s in shapes.items():
        assert s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed(),name
    return shapes,dict(bracket_height_mm=height,cap_screw_engagement_mm=c['bolt_length']-c['floor_stock']-c['strip_thickness'],keeper=kd)
