"""Separate driving-shaft and bearing solids from the inspected native fixture."""
import math
import FreeCAD as App
import Part
from lib.track_parts import cylinder_y,feature
from lib.idler_parts import block,hex_y
from lib.roller_parts import revolution,lines
from lib.wheel_parts import button_rivet
from .drive_mount_geometry import bearing_points,backing_points


def annulus(ro,ri,y0,y1):
    return cylinder_y(ro,y1-y0,y=(y0+y1)/2).cut(cylinder_y(ri,y1-y0+2,y=(y0+y1)/2))


def drill(shape,points,diameter):
    return shape.cut(Part.makeCompound([cylinder_y(diameter/2,1000,x=x,z=z) for x,z in points]))


def keytool(a,z0,z1):
    return block(-a['key_width']/2,a['key_width']/2,a['key_start'],a['key_end'],z0,z1)


def build(doc,name,a):
    role=a['role'];r=a['shaft_diameter']/2;j=a['journal_diameter']/2
    if role=='shaft':
        end=a['end'];s=a['shoulder']
        body=revolution(doc,name,lines([(0,-end),(j,-end),(j,-s),(r,-s),
                                      (r,s),(j,s),(j,end),(0,end)]))
        shape=body.Shape.cut(keytool(a,a['key_bottom'],r+1))
        shape=shape.cut(cylinder_y(a['roller_oil_bore']/2,end+1,y=(end+1)/2))
        shape=shape.cut(Part.makeCylinder(a['radial_oil_bore']/2,r+1,App.Vector(),App.Vector(0,0,1)))
        feature(body,'KeywayAndOilDrilling',shape.removeSplitter());return body
    if role=='inner_rivet':
        return button_rivet(doc,name,a['bearing_screw_diameter'],a['inner_rivet_length'],
                            a['flange_stock']+a['hull_side_thickness'])
    if role=='backing_rivet':
        return button_rivet(doc,name,a['backing_rivet_diameter'],a['backing_rivet_length'],
                            a['backing_stock']+a['hull_side_thickness'])
    if role in {'inner_bearing','outer_bearing'}:
        shape=annulus(a['barrel_radius'],j+a['journal_running_gap'],a['shoulder'],a['face'])
        shape=shape.fuse(annulus(a['flange_radius'],j+a['journal_running_gap'],a['outside'],a['face']))
        shape=drill(shape,bearing_points(a),a['bearing_screw_diameter']+a['fastener_hole_clearance'])
        shape=shape.cut(cylinder_y(a['locking_screw_diameter']/2,2*a['locking_screw_length'],
                                  x=a['locking_screw_x'],y=a['face'],z=a['lock_center']))
        if role=='outer_bearing':shape=shape.cut(keytool(a,0,a['key_top']))
    elif role=='key':shape=keytool(a,a['key_bottom'],a['key_top'])
    elif role=='backing_plate':
        shape=annulus(a['backing_radius'],a['barrel_radius'],a['shell']-a['backing_stock'],a['shell'])
        shape=drill(shape,bearing_points(a),a['bearing_screw_diameter']+a['fastener_hole_clearance'])
        shape=drill(shape,backing_points(a),a['backing_rivet_diameter']+a['fastener_hole_clearance'])
    elif role=='locking_plate':
        shape=block(a['locking_plate_x0'],a['locking_plate_x1'],0,a['locking_stock'],
                    a['lock_z']-a['locking_plate_width'],a['lock_z'])
        shape=shape.cut(cylinder_y((a['locking_screw_diameter']+a['fastener_hole_clearance'])/2,1000,
                                  x=a['locking_screw_x'],z=a['lock_center']))
        shape=drill(shape,bearing_points(a),2*(a['bearing_screw_head_af']/math.sqrt(3)+a['locking_head_clearance']))
    elif role in {'bearing_screw','locking_screw'}:
        length=a[role+'_length'];head=a[role+'_head_stock']
        shape=cylinder_y(a[role+'_diameter']/2,length,y=-length/2)
        shape=shape.fuse(hex_y(a[role+'_head_af'],0,head))
    else:raise ValueError('Unknown drive mounting component '+role)
    shape=shape.removeSplitter()
    if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid/disconnected drive mount '+role)
    body=doc.addObject('PartDesign::Body',name)
    feature(body,'Reconstructed'+role.title().replace('_',''),shape);return body


def hull_tools(clearance,outer_side,hand):
    a=clearance['values'];result=[]
    for center in [clearance['stations']['port' if hand==1 else 'starboard']]:
        # The holes traverse Y and are symmetric in XZ; handed rigid frames
        # therefore generate the same set at both sides of each drive axis.
        for points,d in [(bearing_points(a),a['bearing_screw_diameter']+a['fastener_hole_clearance'])]+(
                [(backing_points(a),a['backing_rivet_diameter']+a['fastener_hole_clearance'])] if outer_side else []):
            for x,z in points:result.append(cylinder_y(d/2,6000,x=center[0]+x,z=center[2]+z))
        result.append(cylinder_y(a['barrel_radius'],6000,x=center[0],z=center[2]))
    return result
