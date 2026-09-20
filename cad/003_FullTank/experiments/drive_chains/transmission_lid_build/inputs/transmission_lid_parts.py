"""Integral oil-box hinge knuckles and the separate printed-size steel pin.

Closed standard configuration only. Unmeasured hinge geometry is kept explicit;
this does not qualify cover motion or the undocumented pin retention method.
"""
import FreeCAD as App
import Part

from transmission_support_parts import box


def cylinder_y(radius, y0, y1, x, z):
    return Part.makeCylinder(radius, y1-y0, App.Vector(x,y0,z), App.Vector(0,1,0))


def hinge(old_cap, old_lid, dimensions, support, controls):
    c=controls; d=dimensions
    x=c['axis_from_cup_back']; z=c['axis_above_lid']
    radius=c['knuckle_radius']; half=c['lid_knuckle_half_length']
    gap=c['axial_knuckle_gap']; length=c['cap_knuckle_length']
    outer=half+gap+length; pin_radius=c['pin_diameter']/2
    bore=pin_radius+c['pin_radial_gap']
    # Work in the existing common cover datum: cup back, center, closed underside.
    lid_blank=old_lid.fuse(cylinder_y(radius,-half,half,x,z))
    windows=[]; ears=[]
    for y0,y1 in [(-outer,-half-gap),(half+gap,outer)]:
        windows.append(box(x-radius-gap,x+radius+gap,y0-gap,y1+gap,-2,z+radius+1))
        pedestal=box(x-radius,x+radius,y0,y1,-support['lid_gap']-c['pedestal_embed'],z)
        ears.append(pedestal.fuse(cylinder_y(radius,y0,y1,x,z)))
    lid_blank=lid_blank.cut(Part.makeCompound(windows)).removeSplitter()
    bore_tool=cylinder_y(bore,-outer-2,outer+2,x,z)
    lid=lid_blank.cut(bore_tool).removeSplitter()
    # Integral cast lugs use the same datum, transformed into the cap definition.
    datum=App.Vector(d['cup_back_x_mm'],0,d['cup_top_z_mm']+support['lid_gap'])
    added=Part.makeCompound(ears);added.translate(datum)
    cap_blank=old_cap.multiFuse(added.Solids).removeSplitter()
    cap_bore=bore_tool.copy();cap_bore.translate(datum)
    cap=cap_blank.cut(cap_bore).removeSplitter()
    pin=cylinder_y(pin_radius,-c['pin_length']/2,c['pin_length']/2,0,0)
    for name,shape in [('cap',cap),('lid',lid),('pin',pin)]:
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid hinged '+name)
    return dict(cap=cap,lid=lid,pin=pin),dict(
        hinge_axis_in_cap_mm=[datum.x+x,0,datum.z+z],
        hinge_axis_in_lid_mm=[x,0,z],
        cap_knuckle_limits_y_mm=[[-outer,-half-gap],[half+gap,outer]],
        lid_knuckle_limits_y_mm=[-half,half],
        pin_end_projection_mm=c['pin_length']/2-outer,
        pin_radius_mm=pin_radius,bore_radius_mm=bore),dict(cap=cap_blank,lid=lid_blank)
