"""Explicit cast-foot and retained horizontal-lever hypothesis for four M4131 fulcrums."""
import math
import FreeCAD as App
import Part
from rear_control_channel_mount_parts import formed_rivet, prism_xy
from transmission_input_installation_parts import formed_pin
V = App.Vector

def lever(c, profile):
    s = Part.makeCylinder(c.get('neck_radius',c['hub_radius']), c['hub_height'])
    if 'neck_radius' in c:
        s = s.fuse(Part.makeCylinder(c['hub_radius'],c['lower_flange_stock']))
        s = s.fuse(Part.makeCylinder(c['hub_radius'],c['top_flange_stock'],V(0,0,c['hub_height']-c['top_flange_stock'])))
    bottom = c.get('arm_bottom',0)
    for point in [profile['brake'], profile['front']]:
        x, y = point
        length = math.hypot(x, y)
        nx, ny = -y/length*c['web_width']/2, x/length*c['web_width']/2
        bridge = prism_xy([(nx,ny), (x+nx,y+ny), (x-nx,y-ny), (-nx,-ny)], c['stock'])
        bridge.translate(V(0,0,bottom))
        s = s.fuse(bridge).fuse(Part.makeCylinder(c['end_radius'],c['stock'],V(x,y,bottom)))
        s = s.cut(Part.makeCylinder(c['end_bore_diameter']/2,c['stock']+2,V(x,y,bottom-1)))
    return s.cut(Part.makeCylinder(c['bore_diameter']/2,c['hub_height']+2,V(0,0,-1)))

def parts(c, channel, channel_pose):
    b, l, w, pin, riv = [c[key] for key in ['bracket','lever','washer','cotter','rivet']]
    stock = b['foot_stock']
    web = b.get('web_stock',stock)
    seat = b.get('seat_height',stock)
    x = b['rivet_x']
    y = max(abs(v) for v in b['rivet_y']) + b['rivet_pad_radius']
    foot = prism_xy([(0,-b['pivot_radius']), (x,-y), (x,y), (0,b['pivot_radius'])],web)
    foot = foot.fuse(Part.makeCylinder(b['pivot_radius'],seat))
    for station in b['rivet_y']:
        foot = foot.fuse(Part.makeCylinder(b['rivet_pad_radius'],stock,V(x,station,0)))
        foot = foot.cut(Part.makeCylinder(riv['hole_diameter']/2,stock+2,V(x,station,-1)))
    bracket = foot.fuse(Part.makeCylinder(b['journal_diameter']/2,b['journal_height'],V(0,0,seat)))
    wire = (pin['cotter_diameter'] - pin['cotter_center_spacing'])/2
    cotter_z = seat + l['hub_height'] + w['stock'] + wire
    bracket = bracket.cut(Part.makeCylinder(b['cotter_hole_diameter']/2,b['journal_diameter']+2,
                           V(0,-b['journal_diameter']/2-1,cotter_z),V(0,1,0)))
    washer = Part.makeCylinder(w['outer_radius'],w['stock']).cut(
        Part.makeCylinder(w['bore_radius'],w['stock']+2,V(0,0,-1)))
    cotter, pin_details = formed_pin(pin)
    cotter.rotate(V(),V(0,1,0),90)
    cotter = Part.makeCompound([cotter])
    rivet, rd = formed_rivet(riv,stock+c['channel_stock'])
    tools = []
    axes = []
    for name, station in c['stations'].items():
        pose = App.Placement(V(*station['pivot']),App.Rotation(V(0,0,1),station['inboard_clock']))
        for y in b['rivet_y']:
            q = pose.multVec(V(x,y,0))
            tool = Part.makeCylinder(riv['hole_diameter']/2,c['channel_stock']+2,q-V(0,0,c['channel_stock']+1))
            tool.Placement = channel_pose.inverse().multiply(tool.Placement)
            tools.append(tool)
            axes.append(dict(owner=name,world_mm=list(q)))
    drilled = channel.cut(Part.makeCompound(tools))
    shapes = dict(bracket=bracket,washer=washer,cotter=cotter,rivet=rivet,channel=drilled)
    for key, profile in c['lever_profiles'].items():
        shapes['lever_'+key] = lever(l,profile)
    for key, s in shapes.items():
        assert s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed(), key
    return shapes,dict(rivet=rd,cotter=pin_details,cotter_center_z_mm=cotter_z,
                       lever_bearing_z_mm=seat,washer_bottom_z_mm=seat+l['hub_height'],
                       rivet_axes=axes),dict(channel_holes=Part.makeCompound(tools))
