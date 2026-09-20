"""Inferred M1592 flanged collar, with source-counted wall/case rivet stations."""
import math
import FreeCAD as App
import Part
from casing_parts import capsule


def round_rectangle(x0, depth, y0, y1, z0, z1, radius):
    pieces = [Part.makeBox(depth, y1-y0-2*radius, z1-z0, App.Vector(x0,y0+radius,z0)),
              Part.makeBox(depth, y1-y0, z1-z0-2*radius, App.Vector(x0,y0,z0+radius))]
    for y in [y0+radius,y1-radius]:
        for z in [z0+radius,z1-radius]:
            pieces.append(Part.makeCylinder(radius,depth,App.Vector(x0,y,z),App.Vector(1,0,0)))
    return pieces[0].multiFuse(pieces[1:]).removeSplitter()


def joint(a, casing, route, shell_report, wall_bounds):
    stock, margin, length = a['angle_stock'], a['flange_margin'], a['collar_length']
    wall_x, wall_stock = wall_bounds.XMin, wall_bounds.XLength
    opening = shell_report['wall_opening_changes'][0]
    width, z0, z1, radius = [opening[k] for k in ['width_mm','bottom_z_mm','top_z_mm','corner_radius_mm']]
    flange = round_rectangle(wall_x-stock,stock,-width/2-margin,width/2+margin,z0-margin,z1+margin,radius+margin)
    flange = flange.cut(round_rectangle(wall_x-stock-1,stock+2,-width/2,width/2,z0,z1,radius))
    radii = shell_report['dimensions']['outside_contour_radii_mm']
    big, small = route['roller_pinion_axis_xz_mm'], route['candidate_transmission_axis_xz_mm']
    gap = a['collar_case_gap']
    outer = capsule(big,small,[r+gap+stock for r in radii],casing['outside_width']+2*(gap+stock))
    inner = capsule(big,small,[r+gap for r in radii],casing['outside_width']+2*gap)
    clip = Part.makeBox(length,6000,6000,App.Vector(wall_x-stock-length,-3000,-1000))
    collar = outer.cut(inner).common(clip)
    angle = flange.fuse(collar).removeSplitter()
    if not angle.isValid() or len(angle.Solids)!=1:
        raise ValueError('M1592 inferred flange/collar is disconnected or invalid')
    wall_points = []
    for sign in [-1,1]:
        for n in range(4):
            wall_points.append((sign*(width/2+margin/2),z0+50+n*(z1-z0-100)/3))
    wall_points += [(-width/4,z0-margin/2),(width/4,z0-margin/2),(0,z1+margin/2)]
    wall_grip = wall_stock + stock
    wall_stations = [dict(center=[wall_x+(wall_stock-stock)/2,y,z],axis=[1,0,0],grip=wall_grip)
                     for y,z in wall_points]
    x = wall_x-stock-length/2
    case_grip = casing['sheet_stock']+gap+stock
    mid_y = casing['outside_width']/2+(gap+stock-casing['sheet_stock'])/2
    stations=[]
    for sign in [-1,1]:
        for n in range(8):
            stations.append(dict(center=[x,sign*mid_y,z0+45+n*(z1-z0-90)/7],axis=[0,sign,0],grip=case_grip))
    dx,dz=small[0]-big[0],small[1]-big[1];distance=math.hypot(dx,dz)
    q=(radii[0]-radii[1])/distance;t=math.sqrt(1-q*q)
    nx,nz=q*dx/distance-t*dz/distance,q*dz/distance+t*dx/distance
    top_z=big[1]+(radii[0]-nx*(x-big[0]))/nz
    offset=(gap+stock-casing['sheet_stock'])/2
    stations.append(dict(center=[x+nx*offset,0,top_z+nz*offset],axis=[nx,0,nz],grip=case_grip))
    assert len(wall_stations)==11 and len(stations)==17
    return angle,dict(wall=wall_stations,case=stations)


def cutter(station,diameter):
    center,axis=App.Vector(*station['center']),App.Vector(*station['axis'])
    return Part.makeCylinder(diameter/2,station['grip']+2,
                             center-axis*(station['grip']/2+1),axis)
