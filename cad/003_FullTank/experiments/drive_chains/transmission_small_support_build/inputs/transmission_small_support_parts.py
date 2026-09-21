"""Small planet support stacks and their separate case/ring receivers.

Port coordinates share the inherited transverse shaft datum. Pins enter toward
the centerline; the alternating ring bolts enter from the case side. Dimensions
not printed in the catalogue are identified in the companion controls.
"""
import math
import FreeCAD as App
import Part
from transmission_core_parts import cylinder
from transmission_pin_parts import ring,positioned,fastening
from transmission_stud_parts import hex_x


def small_support_parts(c,gear,old_case):
    low,high=gear['gear_band_y_mm'];center=gear['planet_center_radius_mm']
    ring_low=high+c['bronze_flange_stock']+c['ring_face_gap']
    ring_high=ring_low+c['ring_stock']
    steel_low=low-c['gear_steel_face_gap']-c['steel_flange_stock']
    parts={}
    parts['bronze']=ring(c['planet_bore_radius'],c['bronze_bore_radius'],low,high).fuse(
        ring(c['bronze_flange_radius'],c['bronze_bore_radius'],high,high+c['bronze_flange_stock'])).removeSplitter()
    parts['steel']=ring(c['steel_radius'],c['pin_radius'],low-c['gear_steel_face_gap'],ring_low).fuse(
        ring(c['steel_flange_radius'],c['pin_radius'],steel_low,low-c['gear_steel_face_gap'])).removeSplitter()
    nut,cotter,pin_hw=fastening(c,'pin',-c['pin_nut_seat_y'],c['pin_radius'])
    for key,s in [('nut',nut),('cotter',cotter)]:
        s.rotate(App.Vector(),App.Vector(1,0,0),180);parts[key]=s
    pin_hw['cotter_axis_y_mm']*=-1;pin_hw['tip_y_mm']*=-1;pin_hw['nut_seat_y_mm']*=-1
    pin=cylinder(c['pin_radius'],pin_hw['tip_y_mm'],ring_high).fuse(
        cylinder(c['pin_head_radius'],ring_high,ring_high+c['pin_head_stock']))
    pin=pin.cut(cylinder(c['pin_bore_diameter']/2,low+6,ring_high+c['pin_head_stock']+1))
    cross=Part.makeCylinder(c['pin_cotter_diameter']/2+c['cotter_hole_gap'],2*c['pin_radius']+2,
        App.Vector(-c['pin_radius']-1,pin_hw['cotter_axis_y_mm'],0),App.Vector(1,0,0))
    parts['pin']=pin.cut(cross).removeSplitter()
    # The same half-inch dished plug definition is reused at a new occurrence
    # placement by the installer. Return its desired local shape for comparison.
    a=c['plug_diameter']/2;h=c['plug_depth'];R=(a*a+h*h)/(2*h)
    base=ring_high+c['pin_head_stock']-1
    origin=App.Vector(0,base-h+R,0)
    plug=Part.makeSphere(R,origin).cut(Part.makeSphere(R-c['plug_stock'],origin))
    parts['plug']=plug.common(cylinder(a,base-h-1,base)).removeSplitter()
    bolt_controls=dict(c,cotter_bend_radius=c['bolt_cotter_bend_radius'])
    parts['bolt_nut'],parts['bolt_cotter'],bolt_hw=fastening(bolt_controls,'bolt',c['bolt_nut_seat_y'],c['bolt_diameter']/2)
    seat=c['bolt_head_seat_y'];head=hex_x(c['bolt_head_af'],-c['bolt_head_stock'],0)
    head.rotate(App.Vector(),App.Vector(0,0,1),90);head.translate(App.Vector(0,seat,0))
    bolt=cylinder(c['bolt_diameter']/2,seat,bolt_hw['tip_y_mm']).fuse(head)
    hole=Part.makeCylinder(c['bolt_cotter_diameter']/2+c['cotter_hole_gap'],c['bolt_diameter']+2,
        App.Vector(-c['bolt_diameter']/2-1,bolt_hw['cotter_axis_y_mm'],0),App.Vector(1,0,0))
    parts['bolt']=bolt.cut(hole).removeSplitter()
    pin_ring=ring(c['ring_outer_radius'],c['ring_inner_radius'],ring_low,ring_high)
    case=old_case.copy();stations=[]
    for n in range(3):
        beta=n*2*math.pi/3;bolt_beta=beta+math.pi/3
        pinhole=positioned(cylinder(c['pin_radius']+c['pin_hole_gap'],c['pin_nut_seat_y']-1,ring_high+1),center,beta)
        pin_ring=pin_ring.cut(pinhole)
        boss=positioned(cylinder(c['pin_boss_radius'],c['pin_nut_seat_y'],steel_low),center,beta)
        # Flat inner thrust seat and outer nut seat on the curved case wall.
        seatcut=positioned(cylinder(c['steel_flange_radius']+c['post_seat_gap'],steel_low,ring_low),center,beta)
        nutcut=positioned(cylinder(c['pin_boss_radius']+c['post_seat_gap'],280,c['pin_nut_seat_y']),center,beta)
        case=case.fuse(boss).cut(seatcut).cut(nutcut).cut(pinhole)
        radius=c['bolt_circle_radius']
        post=positioned(cylinder(c['post_radius'],c['post_case_seat_y'],ring_low),radius,bolt_beta)
        pin_ring=pin_ring.fuse(post)
        boss=positioned(cylinder(c['case_boss_radius'],seat,c['post_case_seat_y']),radius,bolt_beta)
        case=case.fuse(boss)
        innerseat=positioned(cylinder(c['post_radius']+c['post_seat_gap'],c['post_case_seat_y'],ring_high+1),radius,bolt_beta)
        outerseat=positioned(cylinder(c['case_boss_radius']+c['post_seat_gap'],280,seat),radius,bolt_beta)
        bore=positioned(cylinder(c['bolt_diameter']/2+c['pin_hole_gap'],seat-1,ring_high+1),radius,bolt_beta)
        access=positioned(cylinder(c['bolt_access_radius'],c['bolt_nut_seat_y'],ring_high+1),radius,bolt_beta)
        pin_ring=pin_ring.cut(bore).cut(access);case=case.cut(innerseat).cut(outerseat).cut(bore)
        stations.append(dict(index=n,planet_angle_rad=beta,bolt_angle_rad=bolt_beta))
    parts['pin_ring']=pin_ring.removeSplitter();case=case.removeSplitter()
    for key,s in dict(parts,case=case).items():assert s.isValid() and len(s.Solids)==1,key
    return parts,case,dict(ring_faces_y_mm=[ring_low,ring_high],steel_faces_y_mm=[steel_low,ring_low],
        pin_fastening=pin_hw,bolt_fastening=bolt_hw,plug_base_y_mm=base,planet_center_radius_mm=center,
        bolt_circle_radius_mm=c['bolt_circle_radius'],stations=stations)
