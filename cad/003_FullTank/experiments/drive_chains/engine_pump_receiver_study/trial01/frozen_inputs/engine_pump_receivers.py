"""Coupled pump receiver, reconstructed from the pre-receiver lower casing.

Coordinates are engine-local millimetres. Printed pump fastener stock is retained;
casting stock, smooth blind holes and passage geometry remain approximations.
The two open oil sockets do not qualify the missing manifold tube circuit.
"""
import FreeCAD as App
import Part
from engine_lower_drive_receivers import revise as lower_receiver
from engine_oil_pump_parts import mount_outline, cylinder
from engine_water_pump_mounting import revise_case as water_mount

V=App.Vector


def revise(original, controls, oil, drive, water, progress):
    c=controls['receiver'];oc=oil['controls'];mount=oil['datums']['mounting']
    s,lower_datums=lower_receiver(original,c,drive['datums'],drive['main_apex'],
                                 drive['controls'],progress)
    x,z=oc['pump_axis_x'],oc['pump_mount_z']
    face=z+mount['case_face_z']
    assert abs(face-c['oil_mount_z'])<1e-8
    assert abs(x-c['oil_center_x'])<1e-8
    # Match the actual pump's complete circular-and-nose gasket footprint.
    pad=mount_outline(oc,face,face+controls['oil_nose_pad_stock'])
    pad.translate(V(x,0,0));s=s.fuse(pad)
    # Recut the full opening through the added plate as well as the old well.
    s=s.cut(cylinder(c['oil_open_radius'],face-1,c['oil_well_top_z']+1,x))
    progress('oil_nose_and_opening',s)
    holes=[]
    for dx,y in mount['centers']:
        hole=cylinder(oc['bolt_diameter']/2+controls['oil_stud_radial_clearance'],
            face-1,face+mount['case_engagement_mm']+controls['oil_stud_blind_extra'],x+dx,y)
        holes.append(hole)
    s=s.cut(Part.makeCompound(holes))
    # These are separate pressure/front-sump receiving sockets. Their upstream
    # tubes are absent, so open passages alone do not establish a fluid circuit.
    ports=[]
    for key in ['pressure','return_inlet']:
        px,py=x+oc[key+'_port_x'],oc[key+'_port_y']
        s=s.cut(cylinder(oc['port_radius'],face-1,controls['oil_port_top_z']+1,px,py))
        ports.append(dict(name=key,axis=[px,py],radius_mm=oc['port_radius'],
                          open_span_z_mm=[face,controls['oil_port_top_z']]))
    progress('oil_studs_and_sockets',s)
    water_frame=App.Placement(V(drive['main_apex'],0,-drive['controls']['pump_axis_drop']),App.Rotation())
    s,water_datums=water_mount(s,water['controls'],water_frame,water['datums']['mounting'])
    progress('water_mounting_pads',s)
    assert s.isValid() and len(s.Solids)==1
    return s,dict(lower=lower_datums,water=water_datums,oil=dict(
        axis=[x,0],case_face_z=face,stud_centers=[[x+dx,y] for dx,y in mount['centers']],
        stud_engagement_mm=mount['case_engagement_mm'],ports=ports,
        manifold_tubes_modeled=False,hydraulic_circuit_qualified=False))
