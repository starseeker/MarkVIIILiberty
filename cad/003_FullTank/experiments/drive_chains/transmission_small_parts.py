"""Small epicyclic gears, splined input disk, sleeve bush and riveted ring.

Printed tooth counts control pitch geometry; cast sections and fits are explicit
approximations. All shapes use the existing port transverse shaft coordinates.
"""
import math
import FreeCAD as App
import Part
from transmission_core_parts import cylinder,spline_envelope
from transmission_planet_parts import gear_outline,extrude


def small_parts(c,core,cal,output_y,old_shaft):
    axial=lambda pixel:output_y+(cal['sprocket_center_x_px']-pixel)*cal['mm_per_pixel']
    low,high=map(axial,c['gear_face_picks_px'][::-1])
    rp={k:c['teeth_'+k]*25.4/(2*c['pitch_numerator']) for k in ['sun','planet','ring']}
    assert c['teeth_ring']==c['teeth_sun']+2*c['teeth_planet']
    assert (c['teeth_ring']+c['teeth_sun'])%c['planets_per_side']==0
    add=25.4/c['pitch_denominator'];ded=1.25*add
    faces={};profiles={}
    for key in ['sun','planet','ring']:
        internal=key=='ring'
        faces[key],profiles[key]=gear_outline(c['teeth_'+key],rp[key],rp[key]-add if internal else rp[key]-ded,
            rp[key]+ded if internal else rp[key]+add,c['pressure_angle'],
            -c['tooth_thinning'] if internal else c['tooth_thinning'],c['flank_samples'])
    # Even small planets present a root at both radial ends when the sun's
    # tooth faces them. Half a ring-void pitch puts a ring tooth in that root.
    faces['ring'].rotate(App.Vector(),App.Vector(0,1,0),-180/c['teeth_ring'])
    end=axial(c['disk_outer_face_px']);web=end-c['disk_web_stock']
    grip=c['rivet_raw_length']-c['rivet_upset_allowance'];start=end-grip
    radius=c['rivet_diameter']/2;h=c['rivet_head_height']
    a=math.sqrt((6*radius*radius*c['rivet_upset_allowance']/h-h*h)/3)
    ring=cylinder(c['ring_outer_radius'],low,web).cut(extrude(faces['ring'],low-1,high))
    ring=ring.cut(cylinder(c['ring_attachment_inner_radius'],high,web+1))
    flange=cylinder(c['ring_attachment_outer_radius'],start,web).cut(cylinder(c['ring_attachment_inner_radius'],start-1,web+1))
    ring=ring.fuse(flange)
    disk=cylinder(c['ring_attachment_outer_radius'],web,end).fuse(
        cylinder(c['disk_hub_radius'],web-c['disk_hub_extension'],end+c['disk_hub_extension']))
    disk=disk.cut(spline_envelope(core['cross_shaft_root_radius']+c['spline_radial_gap'],
        core['cross_shaft_tip_radius']+c['spline_radial_gap'],core['cross_shaft_spline_width']+2*c['spline_side_gap'],
        core['splines'],web-c['disk_hub_extension']-1,end+c['disk_hub_extension']+1))
    for n in range(c['rivet_count_per_side']):
        theta=2*math.pi*n/c['rivet_count_per_side']
        hole=cylinder(c['rivet_diameter']/2+c['rivet_hole_gap'],start-1,end+1)
        hole.translate(App.Vector(c['rivet_circle_radius']*math.cos(theta),0,c['rivet_circle_radius']*math.sin(theta)))
        ring=ring.cut(hole);disk=disk.cut(hole)
        access=cylinder(a+c['rivet_head_access_gap'],low-1,start)
        access.translate(App.Vector(c['rivet_circle_radius']*math.cos(theta),0,c['rivet_circle_radius']*math.sin(theta)))
        ring=ring.cut(access)
    # Nominal rivet length describes the blank, not the installed grip. The
    # spherical tail cap uses exactly the volume of the assigned upset length.
    sphere_radius=(a*a+h*h)/(2*h)
    def cap(face,sign):
        center=face-sign*(sphere_radius-h)
        sphere=Part.makeSphere(sphere_radius,App.Vector(0,center,0))
        return sphere.common(cylinder(a+1,min(face,face+sign*h),max(face,face+sign*h)))
    rivet=cylinder(radius,start,end).fuse(cap(start,-1)).fuse(cap(end,1)).removeSplitter()
    sleeve_low=axial(c['sun_sleeve_inner_end_px'])
    sleeve=spline_envelope(core['high_drum_bore_radius']-c['spline_radial_gap'],
        core['high_drum_spline_tip_radius']-c['spline_radial_gap'],core['high_drum_spline_width']-2*c['spline_side_gap'],
        core['splines'],sleeve_low,high)
    sun=extrude(faces['sun'],low,high).fuse(sleeve)
    sun=sun.cut(cylinder(c['sun_bush_outer_radius']+c['sun_bush_outer_gap'],sleeve_low-1,high+1)).removeSplitter()
    bush=cylinder(c['sun_bush_outer_radius'],sleeve_low,high).cut(cylinder(c['sun_bush_inner_radius'],sleeve_low-1,high+1)).removeSplitter()
    planet=extrude(faces['planet'],low,high).cut(cylinder(c['planet_bore_radius'],low-1,high+1)).removeSplitter()
    # The freely rotating sleeved sun requires a bearing journal on the shaft.
    # Retain the inherited root radius and remove only spline crests here.
    journal_low=sleeve_low-c['shaft_journal_end_gap'];journal_high=high+c['shaft_journal_end_gap']
    shaft=old_shaft.copy()
    for sign in [1,-1]:
        lo,hi=sorted([sign*journal_low,sign*journal_high])
        cutter=cylinder(80,lo,hi).cut(cylinder(c['shaft_journal_radius'],lo-1,hi+1))
        shaft=shaft.cut(cutter)
    shapes=dict(sun=sun,sun_bush=bush,planet=planet,ring=ring.removeSplitter(),disk=disk.removeSplitter(),rivet=rivet)
    shaft=shaft.removeSplitter()
    for name,s in dict(shapes,cross_shaft=shaft).items():assert s.isValid() and len(s.Solids)==1,name
    return shapes,shaft,dict(tooth_profiles=profiles,gear_band_y_mm=[low,high],planet_center_radius_mm=rp['sun']+rp['planet'],
        ring_void_phase_deg=180/c['teeth_ring'],planet_phase_deg=180/c['teeth_planet'],
        disk_web_y_mm=[web,end],disk_hub_y_mm=[web-c['disk_hub_extension'],end+c['disk_hub_extension']],
        rivet_grip_y_mm=[start,end],rivet_grip_mm=grip,rivet_head_base_radius_mm=a,rivet_head_height_mm=h,
        rivet_access_radius_mm=a+c['rivet_head_access_gap'],
        rivet_blank_shank_volume_mm3=math.pi*radius*radius*c['rivet_raw_length'],
        rivet_formed_shank_and_tail_volume_mm3=math.pi*radius*radius*grip+cap(end,1).Volume,
        sun_bush_y_mm=[sleeve_low,high],shaft_journal_y_mm=[journal_low,journal_high],
        small_carrier_per_input=c['teeth_ring']/(c['teeth_sun']+c['teeth_ring']),
        high_ratio=90/(18+72*c['teeth_ring']/(c['teeth_sun']+c['teeth_ring'])),
        source_planet_axis_pick_y_px=739,source_planet_center_residual_mm=rp['sun']+rp['planet']-(739-cal['shaft_axis_y_px'])*cal['mm_per_pixel'])
