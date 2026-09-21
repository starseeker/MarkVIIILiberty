"""Swept small input disk and riveted ring at the Plate22 axial station."""
import math
import FreeCAD as App
import Part
from transmission_core_parts import cylinder,spline_envelope
from transmission_planet_parts import gear_outline,extrude


def swept_disk_parts(c,controls,core,cal,output_y,gear,old_rivet):
    low,high=gear['gear_band_y_mm'];web,end=gear['disk_web_y_mm']
    target=output_y+(cal['sprocket_center_x_px']-controls['rivet_center_x_px'])*cal['mm_per_pixel']
    shift=target-old_rivet.Solids[0].CenterOfMass.y
    new_web=web+shift;new_end=end+shift;start=new_end-gear['rivet_grip_mm']
    r0=controls['transition_start_radius'];r1=controls['transition_end_radius'];R=c['ring_attachment_outer_radius']
    assert r1 < c['rivet_circle_radius']-gear['rivet_head_base_radius_mm'], 'Rivet heads require a flat disk seat'
    # Two translated cubic curves retain constant axial stock and horizontal
    # end tangents. Their poles are explicit reconstruction parameters.
    poles=[(r0,web),(r0+(r1-r0)/3,web),(r1-(r1-r0)/3,new_web),(r1,new_web)]
    def curve(points):
        b=Part.BSplineCurve();b.buildFromPolesMultsKnots([App.Vector(r,y,0) for r,y in points],[4,4],[0,1],False,3)
        return b.toShape()
    # Explicit vectors avoid positional ambiguity at the radial/Y profile.
    def edge(a,b):return Part.makeLine(App.Vector(a[0],a[1],0),App.Vector(b[0],b[1],0))
    upper=[(r,y+c['disk_web_stock']) for r,y in poles]
    edges=[edge((0,web),(r0,web)),curve(poles),edge((r1,new_web),(R,new_web)),
        edge((R,new_web),(R,new_end)),edge((R,new_end),(r1,new_end)),curve(upper[::-1]),
        edge((r0,end),(0,end)),edge((0,end),(0,web))]
    disk=Part.Face(Part.Wire(edges)).revolve(App.Vector(),App.Vector(0,1,0),360)
    disk=disk.fuse(cylinder(c['disk_hub_radius'],web-c['disk_hub_extension'],end+c['disk_hub_extension']))
    disk=disk.cut(spline_envelope(core['cross_shaft_root_radius']+c['spline_radial_gap'],core['cross_shaft_tip_radius']+c['spline_radial_gap'],
        core['cross_shaft_spline_width']+2*c['spline_side_gap'],core['splines'],web-c['disk_hub_extension']-1,end+c['disk_hub_extension']+1))
    rp=c['teeth_ring']*25.4/(2*c['pitch_numerator']);add=25.4/c['pitch_denominator']
    face,profile=gear_outline(c['teeth_ring'],rp,rp-add,rp+1.25*add,c['pressure_angle'],-c['tooth_thinning'],c['flank_samples'])
    face.rotate(App.Vector(),App.Vector(0,1,0),-180/c['teeth_ring'])
    ring=cylinder(c['ring_outer_radius'],low,new_web).cut(extrude(face,low-1,high))
    ring=ring.cut(cylinder(c['ring_attachment_inner_radius'],high,new_web+1))
    flange=cylinder(R,start,new_web).cut(cylinder(c['ring_attachment_inner_radius'],start-1,new_web+1))
    ring=ring.fuse(flange)
    for n in range(c['rivet_count_per_side']):
        beta=2*math.pi*n/c['rivet_count_per_side'];offset=App.Vector(c['rivet_circle_radius']*math.cos(beta),0,c['rivet_circle_radius']*math.sin(beta))
        hole=cylinder(c['rivet_diameter']/2+c['rivet_hole_gap'],start-1,new_end+1);hole.translate(offset)
        access=cylinder(gear['rivet_access_radius_mm'],low-1,start);access.translate(offset)
        disk=disk.cut(hole);ring=ring.cut(hole).cut(access)
    rivet=old_rivet.copy();rivet.translate(App.Vector(0,shift,0))
    result=dict(disk=disk.removeSplitter(),ring=ring.removeSplitter(),rivet=rivet)
    for key,s in result.items():assert s.isValid() and len(s.Solids)==1,key
    return result,dict(axial_rivet_shift_mm=shift,target_rivet_center_y_mm=target,rivet_source_x_px=controls['rivet_center_x_px'],
        inner_web_y_mm=[web,end],rim_web_y_mm=[new_web,new_end],rivet_grip_y_mm=[start,new_end],
        transition_poles_radius_y_mm=poles,transition_degree=3,transition_knots=[0,1],transition_multiplicities=[4,4],
        axial_web_stock_mm=c['disk_web_stock'],ring_tooth_profile=profile,
        source_note='Rivet center follows approximate Plate22x1065; spline transition poles and radial stations are inferred. Rivet blank, head volume, hub and gear teeth retain inherited dimensions.')
