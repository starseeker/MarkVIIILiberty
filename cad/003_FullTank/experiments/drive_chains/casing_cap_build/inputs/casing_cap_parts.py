"""Inferred cap cleats and source-allocated fastening envelopes.

Coordinates follow the existing casing fixture, with transverse center Y=0.
The three side bolts and one roof bolt per face pair give seven sets per cap.
"""
import math
import FreeCAD as App
import Part
from lib.idler_parts import hex_y
from casing_mount_parts import cutter


def block(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1-x0, y1-y0, z1-z0, App.Vector(x0, y0, z0))


def xz_prism(points, y0, width):
    vertices = [App.Vector(x, y0, z) for x, z in points]
    return Part.Face(Part.makePolygon(vertices+vertices[:1])).extrude(App.Vector(0, width, 0))


def cap_joint(a, casing, route, shell):
    big, small = route['roller_pinion_axis_xz_mm'], route['candidate_transmission_axis_xz_mm']
    radii = shell['dimensions']['outside_contour_radii_mm']
    dx, dz = small[0]-big[0], small[1]-big[1]
    distance = math.hypot(dx, dz)
    q = (radii[0]-radii[1])/distance
    v = math.sqrt(1-q*q)
    nx, nz = q*dx/distance-v*dz/distance, q*dz/distance+v*dx/distance
    roof = lambda x: big[1]+(radii[0]-nx*(x-big[0]))/nz
    sx, sz = [shell['dimensions'][k] for k in ['cap_seam_x_mm', 'cap_seam_z_mm']]
    g, t, width, reach = casing['cap_split_gap'], a['cleat_stock'], a['foot_width'], a['flange_reach']
    half = casing['outside_width']/2
    z0 = sz+a['side_end_margin']
    z1 = roof(sx+g/2+width)-a['side_end_margin']
    assert z1-z0 > 4*a['rivet_end_margin']
    parts, rivets, bolts = {}, [], []

    def add(name, mark, shape):
        parts[name] = dict(mark=mark, shape=shape.removeSplitter())

    for sign, face in [(-1, 'Inner'), (1, 'Outer')]:
        for direction, owner in [(1, 'Body'), (-1, 'Cap')]:
            x0, x1 = sorted([sx+direction*g/2, sx+direction*(g/2+width)])
            f0, f1 = sorted([sx+direction*g/2, sx+direction*(g/2+t)])
            y0, y1 = sorted([sign*half, sign*(half+t)])
            fy0, fy1 = sorted([sign*half, sign*(half+reach)])
            name = owner+face+'Cleat'
            add(name, 'M1583', block(x0,x1,y0,y1,z0,z1).fuse(block(f0,f1,fy0,fy1,z0,z1)))
            x = sx+direction*(g/2+t+(width-t)/2)
            grip = casing['sheet_stock']+t
            for n, z in enumerate([z0+a['rivet_end_margin'], (z0+z1)/2+a['rivet_stagger'], z1-a['rivet_end_margin']]):
                rivets.append(dict(name=name+'Rivet%02d'%n, owner=owner, cleat=name,
                    length_role='short' if owner=='Body' else 'long', grip=grip,
                    center=[x,sign*(half+(t-casing['sheet_stock'])/2),z], axis=[0,sign,0]))
        py0, py1 = sorted([sign*(half+t), sign*(half+reach)])
        packer = face+'Packing'
        add(packer, 'M1584', block(sx-g/2,sx+g/2,py0,py1,z0,z1))
        for n,z in enumerate([z0+a['bolt_end_margin'],(z0+z1)/2,z1-a['bolt_end_margin']]):
            bolts.append(dict(name=face+'BoltSet%02d'%n, center=[sx,sign*(half+a['bolt_face_offset']),z],
                              axis=[1,0,0],grip=2*t+g,body='Body'+face+'Cleat',cap='Cap'+face+'Cleat',packing=packer))

    roof_half = half-a['roof_side_inset']
    top = roof(sx)+reach
    for direction,owner in [(1,'Body'),(-1,'Cap')]:
        x0,x1 = sorted([sx+direction*g/2, sx+direction*(g/2+width)])
        f0,f1 = sorted([sx,sx+direction*t])
        foot = xz_prism([(x0,roof(x0)),(x1,roof(x1)),(x1,roof(x1)+t/nz),(x0,roof(x0)+t/nz)],-roof_half,2*roof_half)
        flange = xz_prism([(f0,roof(f0)),(f1,roof(f1)),(f1,top),(f0,top)],-roof_half,2*roof_half)
        name = owner+'RoofCleat'
        add(name,'M1593',foot.fuse(flange))
        x = sx+direction*(g/2+t+(width-t)/2)
        offset = (t-casing['sheet_stock'])/2
        for n,y in enumerate([-roof_half+a['roof_rivet_end_margin'],0,roof_half-a['roof_rivet_end_margin']]):
            rivets.append(dict(name=name+'Rivet%02d'%n,owner=owner,cleat=name,length_role='short',
                               grip=casing['sheet_stock']+t,center=[x+nx*offset,y,roof(x)+nz*offset],axis=[nx,0,nz]))
    bolts.append(dict(name='RoofBoltSet00',center=[sx,0,roof(sx)+a['bolt_face_offset']],axis=[1,0,0],
                      grip=2*t,body='BodyRoofCleat',cap='CapRoofCleat',packing=None))
    for station in rivets:
        name = station['cleat']
        parts[name]['shape'] = parts[name]['shape'].cut(cutter(station,a['rivet_diameter']+a['hole_diameter_clearance']))
    for station in bolts:
        tool = cutter(station,a['bolt_diameter']+a['hole_diameter_clearance'])
        for name in [station['body'],station['cap'],station['packing']]:
            if name: parts[name]['shape'] = parts[name]['shape'].cut(tool)
    for name,part in parts.items():
        part['shape'] = part['shape'].removeSplitter()
        if not part['shape'].isValid() or len(part['shape'].Solids)!=1:
            raise ValueError('Invalid/disconnected cap joint '+name)
    assert len(parts)==8 and len(rivets)==18 and len(bolts)==7
    return parts,dict(rivets=rivets,bolts=bolts),dict(seam_x_mm=sx,side_bottom_z_mm=z0,side_top_z_mm=z1,
                roof_normal=[nx,0,nz],side_grip_mm=2*t+g,roof_grip_mm=2*t)


def fasteners(a):
    """Canonical local-Y fasteners; bolt head bears at Y=0, nut/washer at Y=0."""
    diameter, length = a['bolt_diameter'], a['bolt_length']
    bolt = Part.makeCylinder(diameter/2,length,App.Vector(0,-length,0),App.Vector(0,1,0))
    bolt = bolt.fuse(hex_y(a['hex_across_flats'],0,a['bolt_head_stock'])).removeSplitter()
    nut = hex_y(a['hex_across_flats'],0,a['nut_stock']).cut(Part.makeCylinder(
        (diameter+a['thread_envelope_diameter_clearance'])/2,a['nut_stock']+2,App.Vector(0,-1,0),App.Vector(0,1,0)))
    washer = Part.makeCylinder(a['washer_od']/2,a['washer_stock'],App.Vector(),App.Vector(0,1,0))
    washer = washer.cut(Part.makeCylinder((diameter+a['hole_diameter_clearance'])/2,a['washer_stock']+2,
                                          App.Vector(0,-1,0),App.Vector(0,1,0)))
    washer = washer.cut(block(0,a['washer_od'],-1,a['washer_stock']+1,-a['washer_split']/2,a['washer_split']/2))
    shapes = dict(bolt=bolt,nut=nut.removeSplitter(),washer=washer.removeSplitter())
    for name,shape in shapes.items():
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid fastener '+name)
    return shapes
