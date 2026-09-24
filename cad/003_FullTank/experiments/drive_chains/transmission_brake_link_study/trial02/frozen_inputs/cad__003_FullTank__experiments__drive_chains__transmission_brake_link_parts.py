"""Estimated M337 forked links and individually retained M339 pivot pins.

Origin is the upper pivot. +Y is the pin axis, +X forward, +Z upward. Four
identical links share upper/lower pivot stations in X/Z. Source support stock
and the saved band envelope constrain the estimated hidden fork and lower eye.
"""
import math
import FreeCAD as App
import Part
from transmission_input_installation_parts import formed_pin
V=App.Vector


def dimensions(c,support,upper,drum,diaphragm_front):
    upper_radius=support['dimensions']['lug_radius_mm']
    half=support['controls']['lug_stock']/2+c['clevis_side_gap']+c['clevis_cheek_stock']
    inner=support['controls']['lug_stock']/2+c['clevis_side_gap']
    lower_x=diaphragm_front+c['lower_head_radius']+c['lower_frame_clearance']
    lower_radius=drum[0]-lower_x
    lower=V(drum[0]-lower_radius,upper[1],drum[2])-V(*upper)
    return dict(clevis_half_width_mm=half,clevis_inner_half_width_mm=inner,
        clevis_slot_bottom_mm=-upper_radius-c['clevis_bottom_clearance'],
        lower_eye_relative_mm=list(lower),lower_anchor_radius_mm=lower_radius,diaphragm_front_x_mm=diaphragm_front,
        pin_length_mm=2*(half+c['pin_end_extension']),cotter_y_mm=half+c['cotter_station_overhang'],
        pin_center_distance_mm=lower.Length)


def parts(c,d):
    half=d['clevis_half_width_mm'];inner=d['clevis_inner_half_width_mm'];lower=V(*d['lower_eye_relative_mm'])
    def cylinder(radius,center,width):return Part.makeCylinder(radius,width,center+V(0,-width/2,0),V(0,1,0))
    # A straight web joining round eyes, with a wider fork root tapering to the
    # lower strap. Both the fork and section taper are stated approximations.
    direction=V(lower.x,0,lower.z);direction.normalize();normal=V(-direction.z,0,direction.x)
    corners=[-normal*c['web_width']/2,normal*c['web_width']/2,
             lower+normal*c['web_width']/2,lower-normal*c['web_width']/2]
    points=[p+V(0,-half,0) for p in corners]
    web=Part.Face(Part.makePolygon(points+points[:1])).extrude(V(0,2*half,0))
    link=cylinder(c['upper_head_radius'],V(),2*half).multiFuse([web,cylinder(c['lower_head_radius'],lower,2*half)])
    ztop=d['clevis_slot_bottom_mm']-c['clevis_bridge_depth'];zbottom=ztop-c['neck_taper_length']
    # Planar side pockets form the broad fork root to narrow lower strap.
    for sign in [-1,1]:
        y=lambda value:sign*value
        pts=[V(-100,y(half),ztop),V(-100,y(c['lower_stock']/2),zbottom),
             V(-100,y(c['lower_stock']/2),lower.z-100),V(-100,y(half+10),lower.z-100),V(-100,y(half+10),ztop)]
        tool=Part.Face(Part.makePolygon(pts+pts[:1])).extrude(V(200,0,0));link=link.cut(tool)
    slot=Part.makeBox(200,2*inner,200,V(-100,-inner,d['clevis_slot_bottom_mm']))
    link=link.cut(slot)
    link=link.cut(cylinder(c['suspension_pin_diameter']/2+c['upper_bore_allowance'],V(),2*half+2))
    link=link.cut(cylinder(c['lower_pin_diameter']/2+c['lower_bore_allowance'],lower,2*half+2))
    pin=cylinder(c['suspension_pin_diameter']/2,V(),d['pin_length_mm'])
    for y in [-d['cotter_y_mm'],d['cotter_y_mm']]:
        pin=pin.cut(Part.makeCylinder(c['cotter_diameter']/2+c['cotter_hole_allowance'],
            c['suspension_pin_diameter']+2,V(-c['suspension_pin_diameter']/2-1,y,0),V(1,0,0)))
    cotter,detail=formed_pin(c)
    # Existing cotter definition runs along +Y. Rigidly turn it into the
    # pin's cross-hole, along +X, retaining its spread in the X/Z plane.
    cotter.rotate(V(),V(0,0,1),-90)
    shapes=dict(link=link,pin=pin,cotter=cotter)
    for name,s in shapes.items():assert s.isValid() and len(s.Solids)==1,(name,s.isValid(),len(s.Solids))
    return shapes,detail
