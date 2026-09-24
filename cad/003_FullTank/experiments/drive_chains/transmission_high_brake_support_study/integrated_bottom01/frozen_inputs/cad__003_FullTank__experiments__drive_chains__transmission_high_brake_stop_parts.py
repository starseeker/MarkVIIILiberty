"""M363 retention and M366 bottom-stop interfaces around the saved M362 fork.

The catalogue controls split-pin stock and nominal hardware sizes. Cast shelf,
formed sections and hidden transverse arrangement are explicit approximations.
"""
import math
import FreeCAD as App
import Part
from transmission_high_brake_support_parts import tn_plate
from transmission_brake_anchor_parts import strip
from transmission_brake_stop_parts import hexagon
from transmission_input_installation_parts import formed_pin
V=App.Vector


def frame(point,t,n):
    y=n.cross(t)
    return App.Placement(point,App.Rotation(App.Matrix(t.x,y.x,n.x,0,t.y,y.y,n.y,0,t.z,y.z,n.z,0,0,0,0,1)))


def parts(c,receiver,old_bracket,band_targets):
    anchor=V(*receiver['anchor_center']);outer=receiver['fork_outer_width']
    seat=-outer/2;cross=outer/2+c['cotter_diameter']/2+c['cotter_axial_gap'];tip=seat+c['pin_under_head_length']
    pin=Part.makeCylinder(c['pin_diameter']/2,c['pin_under_head_length'],V(0,seat,0),V(0,1,0)).fuse(
        Part.makeCylinder(c['pin_head_radius'],c['pin_head_stock'],V(0,seat-c['pin_head_stock'],0),V(0,1,0)))
    crosshole=Part.makeCylinder(c['cotter_diameter']/2+c['cotter_hole_gap'],c['pin_diameter']+2,V(-c['pin_diameter']/2-1,cross,0),V(1,0,0))
    pin=pin.cut(crosshole)
    cotter,cd=formed_pin(dict(c,crown_radius=c['pin_diameter']/2));cotter.rotate(V(),V(0,0,1),-90)
    # Bake the analytic rotation into a child while preserving identity definition placement.
    cotter=Part.makeCompound([cotter])
    shapes=dict(anchor_pin=pin,anchor_cotter=cotter)
    angle=math.radians(c['bottom_slope_deg']);t=V(math.cos(angle),0,math.sin(angle));n=V(-math.sin(angle),0,math.cos(angle));o=V(*c['bottom_plane_origin'])
    lo,hi=c['bottom_limits'];w=c['bottom_width'];stock=c['bottom_stock'];station=c['mount_station']
    stop=tn_plate(o,t,n,[(lo,-stock),(hi,-stock),(hi,0),(lo,0)],-w/2,w/2)
    additions=[];bores=[];through=[];mounts=[]
    for sign in [-1,1]:
        y=sign*c['mount_y'];y0=y-c['receiver_width']/2;y1=y+c['receiver_width']/2
        half=c['receiver_length']/2
        additions.append(tn_plate(o,t,n,[(station-half,0),(station+half,0),(station+half,c['receiver_stock']),(station-half,c['receiver_stock'])],y0,y1))
        cheek0,cheek1=sorted([sign*receiver['fork_gap']/2,sign*outer/2])
        additions.append(strip(anchor,o+t*station+n*c['receiver_stock']/2,c['receiver_rib_width'],cheek0,cheek1-cheek0))
        q=o+t*station+V(0,y,0);f=frame(q,t,n);mounts.append(f)
        depth=c['mount_length']-stock-c['lock_stock']+c['blind_gap']
        drill=Part.makeCylinder(c['mount_diameter']/2+c['mount_bore_gap'],depth+1,V(0,0,-1));drill.Placement=f;bores.append(drill)
        drill=Part.makeCylinder(c['mount_diameter']/2+c['mount_bore_gap'],stock+c['lock_stock']+2,V(0,0,-stock-c['lock_stock']-1));drill.Placement=f;through.append(drill)
    added=Part.makeCompound(additions)
    bracket=old_bracket.multiFuse(additions).cut(Part.makeCompound(bores))
    # Preserve the retained eye bore and the band-foot radial envelope in all
    # newly proposed ribs. Actual neighbor checks remain separate.
    bracket=bracket.cut(Part.makeCylinder(receiver['pin_bore_radius'],w+2,anchor+V(0,-w/2-1,0),V(0,1,0)))
    bracket=bracket.cut(Part.makeCylinder(receiver['band_clearance_radius'],w+2,V(0,-w/2-1,0),V(0,1,0)))
    half=c['lock_length']/2;low=-stock-c['lock_stock'];outer_tab=c['mount_y']+c['mount_head_af']/2
    lock=tn_plate(o,t,n,[(station-half,low),(station+half,low),(station+half,-stock),(station-half,-stock)],-outer_tab-c['lock_stock'],outer_tab+c['lock_stock'])
    for sign in [-1,1]:
        y0,y1=sorted([sign*outer_tab,sign*(outer_tab+c['lock_stock'])]);half=c['lock_tab_half_length']
        tab=tn_plate(o,t,n,[(station-half,low+.1),(station+half,low+.1),(station+half,low-c['lock_tab_height']),(station-half,low-c['lock_tab_height'])],y0,y1)
        lock=lock.fuse(tab)
    stop=stop.cut(Part.makeCompound(through));lock=lock.cut(Part.makeCompound(through))
    head=hexagon(c['mount_head_af'],c['mount_head_stock']);head.translate(V(0,0,-c['mount_head_stock']))
    shapes['mount_screw']=Part.makeCylinder(c['mount_diameter']/2,c['mount_length']).fuse(head)
    head=hexagon(c['stop_head_af'],c['stop_head_stock']);head.translate(V(0,0,-c['stop_screw_length']-c['stop_head_stock']))
    shapes['stop_screw']=Part.makeCylinder(c['stop_screw_diameter']/2,c['stop_screw_length'],V(0,0,-c['stop_screw_length'])).fuse(head)
    shapes['stop_nut']=hexagon(c['stop_nut_af'],c['stop_nut_stock']).cut(Part.makeCylinder(c['stop_screw_diameter']/2+c['stop_bore_gap'],c['stop_nut_stock']+2,V(0,0,-1)))
    targets=Part.makeCompound(band_targets);stops=[];stop_holes=[]
    for u in c['stop_stations']:
        q=o+t*u
        # Find first contact for the complete flat screw tip, not a ray through
        # its centre. This compensates only for the local physical interface;
        # source camera and neighboring geometry remain unchanged.
        def tool(height):return Part.makeCylinder(c['stop_screw_diameter']/2,height+50,q-n*50,n)
        low,high=0.,100.
        assert tool(high).common(targets).Solids and not tool(low).common(targets).Solids
        for _ in range(30):
            mid=(low+high)/2
            if tool(mid).common(targets).Solids:high=mid
            else:low=mid
        contact=low;advance=contact-c['stop_tip_gap']
        screw_frame=frame(q+n*advance,t,n);nut_frame=frame(q-n*(stock+c['stop_nut_stock']),t,n)
        drill=Part.makeCylinder(c['stop_screw_diameter']/2+c['stop_bore_gap'],stock+2,V(0,0,-stock-1));drill.Placement=frame(q,t,n);stop_holes.append(drill)
        stops.append(dict(station=u,contact_advance_mm=contact,tip_advance_mm=advance,screw_frame=list(screw_frame.toMatrix().A),nut_frame=list(nut_frame.toMatrix().A)))
    shapes.update(anchor_bracket=bracket,bottom_stop=stop.cut(Part.makeCompound(stop_holes)),bottom_lock_plate=lock)
    for role,s in shapes.items():
        assert s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.Placement.isIdentity(),(role,s.isValid(),len(s.Solids),s.Placement)
    detail=dict(anchor_center=list(anchor),pin_head_seat_y_mm=seat,pin_tip_y_mm=tip,cotter_cross_y_mm=cross,cotter=cd,
        bottom_frame=list(frame(o,t,n).toMatrix().A),mount_seat_frames=[list(f.toMatrix().A) for f in mounts],mount_receiving_depth_mm=depth,stops=stops,
        limits=['Unprinted pin dimensions and installed head side are estimates.','Cotter uses two round legs and an overlapping eye construction; source nominal length is interpreted per developed leg, not a claim of exact manufactured stock volume.','M362 lower shelf, transverse MX76 pair and M366 stock are reconstructed estimates.','Stop screw adjustment is computed from actual retained band/anchor envelopes at the fixed estimated stop axes; standard setting and threads remain approximate.','Full service sequence, top/back stops, clip and controls are pending.'])
    return shapes,detail,dict(bracket_addition=added,bracket_receiving_holes=Part.makeCompound(bores),pin_crosshole=crosshole)
