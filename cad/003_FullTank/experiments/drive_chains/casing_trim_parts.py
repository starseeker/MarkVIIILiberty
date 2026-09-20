"""Inferred lap registers and straight beading on the casing's horizontal seam."""
import math
import FreeCAD as App
import Part
from scipy.optimize import brentq
from lib.idler_parts import rounded_xz
from lib.roller_parts import revolution
from casing_mount_parts import cutter


def beading(x0, length, outer_y, z0, height, stock, sign):
    """Round-ended flat strip, tangent to the inside sheet face."""
    r = stock/2
    cy = outer_y-sign*r
    shape = Part.makeBox(length,stock,height-stock,App.Vector(x0,min(outer_y,outer_y-sign*stock),z0+r))
    caps = [Part.makeCylinder(r,length,App.Vector(x0,cy,z),App.Vector(1,0,0)) for z in [z0+r,z0+height-r]]
    return shape.multiFuse(caps).removeSplitter()


def trim(a, casing, route, shell):
    big = route['roller_pinion_axis_xz_mm']
    sx,sz = [shell['dimensions'][k] for k in ['cap_seam_x_mm','cap_seam_z_mm']]
    half, gap = casing['outside_width']/2, casing['cap_split_gap']
    hub = 85+casing['hub_gap']  # The prior shell was qualified around this retained hub.
    parts, stations = {}, []
    for sign,face in [(-1,'Right'),(1,'Left')]:
        y0,y1 = sorted([sign*half,sign*(half+a['register_stock'])])
        for owner,direction in [('Body',-1),('Cap',1)]:
            x0 = big[0]+hub+a['register_hub_margin'] if owner=='Body' else big[0]-hub-a['register_hub_margin']-a['register_length']
            z0,z1 = sorted([sz+direction*a['register_fixed_depth'],sz-direction*a['register_lap']])
            name = owner+face+'Register'
            mark = 'M1581' if owner=='Body' else ('M1594A' if sign<0 else 'M1594B')
            shape = rounded_xz(x0,x0+a['register_length'],z0,z1,y0,y1,a['register_corner'])
            parts[name] = dict(shape=shape,mark=mark,owner=owner,role='register')
            grip = casing['sheet_stock']+a['register_stock']
            for n in range(4):
                x = x0+a['register_rivet_end']+n*(a['register_length']-2*a['register_rivet_end'])/3
                stations.append(dict(name=name+'Rivet%02d'%n,part=name,owner=owner,role='register',grip=grip,
                    center=[x,sign*(half+(a['register_stock']-casing['sheet_stock'])/2),sz+direction*a['register_rivet_offset']],axis=[0,sign,0]))
        for owner,direction in [('Body',-1),('Cap',1)]:
            x0 = (big[0]+hub+sx)/2-a['beading_length']/2
            z0 = sz+gap/2 if owner=='Cap' else sz-gap/2-a['beading_width']
            inner = sign*(half-casing['sheet_stock'])
            name = owner+face+'Beading'
            shape = beading(x0,a['beading_length'],inner,z0,a['beading_width'],a['beading_stock'],sign)
            parts[name] = dict(shape=shape,mark='M1585',owner=owner,role='beading')
            grip = casing['sheet_stock']+a['beading_stock']
            for n in range(5):
                x = x0+a['beading_rivet_end']+n*(a['beading_length']-2*a['beading_rivet_end'])/4
                stations.append(dict(name=name+'Rivet%02d'%n,part=name,owner=owner,role='beading',grip=grip,
                    center=[x,sign*(half-grip/2),z0+a['beading_width']/2],axis=[0,sign,0]))
    for s in stations:
        parts[s['part']]['shape'] = parts[s['part']]['shape'].cut(drill(s,a))
    for key,part in parts.items():
        part['shape'] = part['shape'].removeSplitter()
        if not part['shape'].isValid() or len(part['shape'].Solids)!=1:raise ValueError('Invalid trim part '+key)
    assert len(parts)==8 and len(stations)==36
    return parts,stations


def drill(s,a):
    diameter = a[s['role']+'_rivet_diameter']
    shape = cutter(s,diameter+a['hole_diameter_clearance'])
    if s['role']=='beading':
        r,R = diameter/2,diameter*a['countersunk_head_radius_ratio']
        height = (R-r)/math.tan(math.radians(a['countersunk_angle_deg']/2))
        center,axis = App.Vector(*s['center']),App.Vector(*s['axis'])
        shape = shape.fuse(Part.makeCone(r,R,height,center+axis*(s['grip']/2-height),axis))
    return shape


def countersunk_rivet(doc,name,a,grip):
    """Overall stock length includes the inferred cone; conserve material at upset."""
    d,stock = a['beading_rivet_diameter'],a['beading_rivet_length']
    r,R = d/2,d*a['countersunk_head_radius_ratio']
    head = (R-r)/math.tan(math.radians(a['countersunk_angle_deg']/2))
    assert head<grip<stock
    base = d*a['upset_radius_ratio']
    capvol = lambda h:math.pi*h*(3*base*base+h*h)/6
    excess = math.pi*r*r*(stock-grip)
    upset = brentq(lambda h:capvol(h)-excess,1e-6,stock)
    sphere = (base*base+upset*upset)/(2*upset)
    middle = math.sqrt(sphere*sphere-(sphere-upset/2)**2)
    v = lambda radius,y:App.Vector(radius,y,0)
    points = [(0,grip/2),(R,grip/2),(r,grip/2-head),(r,-grip/2),(base,-grip/2)]
    curves = [Part.LineSegment(v(*p),v(*q)) for p,q in zip(points[:-1],points[1:])]
    curves += [Part.Arc(v(base,-grip/2),v(middle,-grip/2-upset/2),v(0,-grip/2-upset)),
               Part.LineSegment(v(0,-grip/2-upset),v(0,grip/2))]
    body = revolution(doc,name,curves)
    expected = math.pi*head*(R*R+R*r+r*r)/3+math.pi*r*r*(stock-head)
    assert abs(body.Shape.Volume-expected)<1e-4
    for key,value in [('SourceStockLength',stock),('InstalledGrip',grip),('HeadHeight',head),('UpsetHeight',upset)]:
        body.addProperty('App::PropertyLength',key,'Reconstruction');setattr(body,key,value)
    body.addProperty('App::PropertyString','StockInterpretation','Reconstruction')
    body.StockInterpretation='Overall nominal stock length includes countersunk head; explicit reconstruction interpretation'
    return body
