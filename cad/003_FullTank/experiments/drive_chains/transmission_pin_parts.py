"""Separate planet pins, sleeves, pin rings and fastening with inferred receivers."""
import math
import FreeCAD as App
import Part
from transmission_core_parts import cylinder,box,revolve
from transmission_stud_parts import hex_x,split_pin,cylinder_x


def positioned(shape,radius,angle):
    result=shape.copy();result.rotate(App.Vector(),App.Vector(0,1,0),-math.degrees(angle))
    result.translate(App.Vector(radius*math.cos(angle),0,radius*math.sin(angle)))
    return result


def ring(outer,inner,low,high):
    return cylinder(outer,low,high).cut(cylinder(inner,low-1,high+1))


def fastening(c,role,seat,radius):
    prefix='pin' if role=='pin' else 'bolt'
    height=c[prefix+'_nut_height'];slot=c[prefix+'_nut_slot_depth'];crown=c[prefix+'_nut_crown_radius']
    diameter=c[prefix+'_cotter_diameter'];length=c[prefix+'_cotter_length']
    nut=hex_x(c[prefix+'_nut_af'],0,height-slot).fuse(cylinder_x(crown,height-slot,height))
    cuts=[]
    for angle in [0,60,120]:
        tool=box(height-slot,height+1,-crown-1,crown+1,-(diameter+c['cotter_slot_gap'])/2,(diameter+c['cotter_slot_gap'])/2)
        tool.rotate(App.Vector(),App.Vector(1,0,0),angle);cuts.append(tool)
    nut=nut.cut(cylinder_x(radius+c['nut_bore_gap'],-1,height+1)).cut(Part.makeCompound(cuts)).removeSplitter()
    cotter_controls={k:v for k,v in c.items() if k.startswith('cotter_')}
    cotter_controls.update(cotter_diameter=diameter,cotter_length=length,cotter_center_spacing=diameter/3,crown_radius=crown)
    cotter,detail=split_pin(cotter_controls)
    axis_y=seat+height-slot/2
    for shape,y in [(nut,seat),(cotter,axis_y)]:
        shape.rotate(App.Vector(),App.Vector(0,0,1),90);shape.translate(App.Vector(0,y,0))
    return nut,cotter,dict(cotter_axis_y_mm=axis_y,nut_seat_y_mm=seat,
                           tip_y_mm=seat+height+c['pin_end_projection'],cotter=detail)


def pin_parts(c,gear,carrier):
    low,high=gear['gear_band_y_mm'];center=gear['planet_center_radius_mm']
    ring_high=low-c['bronze_flange_stock']-c['ring_face_gap'];ring_low=ring_high-c['ring_stock']
    boss_front=high+c['gear_steel_face_gap']+c['steel_flange_stock']
    shapes={}
    shapes['bronze']=ring(c['gear_bore_radius'],c['bronze_bore_radius'],low,high).fuse(
        ring(c['bronze_flange_radius'],c['bronze_bore_radius'],low-c['bronze_flange_stock'],low)).removeSplitter()
    shapes['steel']=ring(c['steel_radius'],c['pin_radius'],ring_high,high+c['gear_steel_face_gap']).fuse(
        ring(c['steel_flange_radius'],c['pin_radius'],high+c['gear_steel_face_gap'],boss_front)).removeSplitter()
    shapes['nut'],shapes['cotter'],pin_hw=fastening(c,'pin',c['pin_boss_outboard_y'],c['pin_radius'])
    shapes['bolt_nut'],shapes['bolt_cotter'],bolt_hw=fastening(c,'bolt',c['bolt_boss_back_y'],c['bolt_diameter']/2)
    pin=cylinder(c['pin_radius'],ring_low,pin_hw['tip_y_mm']).fuse(
        cylinder(c['pin_head_radius'],ring_low-c['pin_head_stock'],ring_low))
    # Source half-inch plug establishes the bore diameter, not pin outside diameter.
    pin=pin.cut(cylinder(c['pin_bore_diameter']/2,ring_low-c['pin_head_stock']-1,high-6))
    cross=Part.makeCylinder(c['pin_cotter_diameter']/2+c['cotter_hole_gap'],2*c['pin_radius']+2,
        App.Vector(-c['pin_radius']-1,pin_hw['cotter_axis_y_mm'],0),App.Vector(1,0,0))
    shapes['pin']=pin.cut(cross).removeSplitter()
    a=c['plug_diameter']/2;h=c['plug_depth'];sphere_radius=(a*a+h*h)/(2*h)
    base=ring_low-c['pin_head_stock']+1
    sphere_center=App.Vector(0,base+h-sphere_radius,0)
    plug=Part.makeSphere(sphere_radius,sphere_center).cut(Part.makeSphere(sphere_radius-c['plug_stock'],sphere_center))
    shapes['plug']=plug.common(cylinder(a,base,base+h+1)).removeSplitter()
    bolt=cylinder(c['bolt_diameter']/2,ring_low,bolt_hw['tip_y_mm'])
    head=hex_x(c['bolt_head_af'],-c['bolt_head_stock'],0);head.rotate(App.Vector(),App.Vector(0,0,1),90)
    head.translate(App.Vector(0,ring_low,0));bolt=bolt.fuse(head)
    drill=Part.makeCylinder(c['bolt_cotter_diameter']/2+c['cotter_hole_gap'],c['bolt_diameter']+2,
        App.Vector(-c['bolt_diameter']/2-1,bolt_hw['cotter_axis_y_mm'],0),App.Vector(1,0,0))
    shapes['bolt']=bolt.cut(drill).removeSplitter()
    pin_ring=ring(c['ring_outer_radius'],c['ring_inner_radius'],ring_low,ring_high)
    # Preserve the traced outer dish silhouette while adding the missing local
    # bearing material behind each deeply recessed nut seat.
    boss_envelope=revolve(c['pin_boss_envelope_profile'])
    revised=carrier.copy();stations=[]
    for n in range(3):
        beta=2*math.pi*n/3;bolt_beta=beta+math.pi/3
        pin_hole=positioned(cylinder(c['pin_radius']+c['pin_hole_gap'],ring_low-1,c['pin_boss_outboard_y']+1),center,beta)
        pin_ring=pin_ring.cut(pin_hole)
        boss=positioned(cylinder(c['pin_boss_radius'],boss_front,650),center,beta).common(boss_envelope)
        recess=positioned(cylinder(c['pin_recess_radius'],c['pin_boss_outboard_y'],651),center,beta)
        revised=revised.fuse(boss).cut(recess).cut(pin_hole)
        post=positioned(cylinder(c['post_radius'],ring_high,c['bolt_boss_front_y']),c['bolt_circle_radius'],bolt_beta)
        pin_ring=pin_ring.fuse(post)
        boss=positioned(cylinder(c['bolt_boss_radius'],c['bolt_boss_front_y'],c['bolt_boss_back_y']),c['bolt_circle_radius'],bolt_beta)
        revised=revised.fuse(boss)
        # The conical casting crosses a flat post-end plane near the outer edge.
        # Spotface that receiving region so the ring post meets a real planar seat.
        seat=positioned(cylinder(c['post_radius']+c['post_seat_gap'],ring_high,c['bolt_boss_front_y']),c['bolt_circle_radius'],bolt_beta)
        revised=revised.cut(seat)
        hole=positioned(cylinder(c['bolt_diameter']/2+c['pin_hole_gap'],ring_low-1,c['bolt_boss_back_y']+1),c['bolt_circle_radius'],bolt_beta)
        pin_ring=pin_ring.cut(hole);revised=revised.cut(hole)
        stations.append(dict(index=n,planet_angle_rad=beta,bolt_angle_rad=bolt_beta))
    shapes['pin_ring']=pin_ring.removeSplitter();revised=revised.removeSplitter()
    for key,shape in dict(shapes,carrier=revised).items():
        assert shape.isValid() and len(shape.Solids)==1,key
    return shapes,revised,dict(ring_faces_y_mm=[ring_low,ring_high],pin_boss_front_y_mm=boss_front,
        pin_fastening=pin_hw,bolt_fastening=bolt_hw,plug_base_y_mm=base,
        steel_faces_y_mm=[ring_high,boss_front],stations=stations,
        source_controlled_plug_diameter_mm=c['plug_diameter'],gear_bore_radius_mm=c['gear_bore_radius'])
