"""Separate air-pump solids; source arrangement with explicit inferred dimensions.

Local X is the shaft axis, Y port, Z up. Cylinder parts are made along local Z
and installed at +/-45deg about X. The static cam/piston contact is derived from
the support plane of each eccentric circle, not guessed from their bounding boxes.
"""
import math
import FreeCAD as App
import Part


def cyl(r, z0, z1):
    return Part.makeCylinder(r, z1-z0, App.Vector(0,0,z0))


def xc(r, x0, x1, y=0, z=0):
    return Part.makeCylinder(r,x1-x0,App.Vector(x0,y,z),App.Vector(1,0,0))


def box(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,App.Vector(x0,y0,z0))


def hexagon(af,z0,z1):
    r=af/math.sqrt(3)
    pts=[App.Vector(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3),z0) for i in range(6)]
    return Part.Face(Part.makePolygon(pts+pts[:1])).extrude(App.Vector(0,0,z1-z0))


def moved(s, xyz=(0,0,0), rot=None):
    t=s.copy();t.Placement=App.Placement(App.Vector(*xyz),rot or App.Rotation()).multiply(t.Placement)
    return t


def fused(shapes):
    return shapes[0].multiFuse(shapes[1:]) if len(shapes)>1 else shapes[0].copy()


def bolt(diameter,length,af,height):
    return cyl(diameter/2,-length,0).fuse(hexagon(af,0,height)).removeSplitter()


def spring(height,c):
    wire=c['spring_wire_radius'];radius=c['spring_mean_radius']
    pitch=(height-2*wire)/c['spring_turns']
    helix=Part.makeHelix(pitch,height-2*wire+pitch/2,radius)
    path=Part.Wire(helix.Edges)
    tangent=App.Vector(0,radius,pitch/(2*math.pi))
    section=Part.Wire([Part.makeCircle(wire,App.Vector(radius,0,0),tangent)])
    result=path.makePipeShell([section],True,True)
    result.translate(App.Vector(0,0,wire-pitch/4))
    return result.common(cyl(radius+wire+1,0,height)),pitch


def build(c):
    h=c['body_length']/2;seat=c['bank_seat'];roof=seat*math.sqrt(2)
    floor=c['base_floor'];gap=c['receiver_gap'];r=c['journal_radius']
    parts={};occ=[];notes={};tools=[];base_blank=[]
    def add(name,key,xyz=(0,0,0),rot=None,parent='Core'):
        occ.append(dict(name=name,key=key,xyz=list(xyz),rotation=list((rot or App.Rotation()).Q),parent=parent))
    # Pentagonal casting, feet and a continuous crank/cam cavity.
    yz=[(-roof,floor),(roof,floor),(roof,0),(0,roof),(-roof,0)]
    pts=[App.Vector(-h,y,z) for y,z in yz]
    base=Part.Face(Part.makePolygon(pts+pts[:1])).extrude(App.Vector(2*h,0,0))
    for sign in [-1,1]:
        base_blank.append(box(-h,h,sign*roof-c['foot_extension'] if sign<0 else roof-1,
            sign*roof+1 if sign<0 else roof+c['foot_extension'],floor,floor+c['foot_stock']))
    base=base.multiFuse(base_blank)
    tools.append(xc(c['shaft_cavity_radius'],-h-1,h+1))
    for x in [-c['foot_hole_x'],c['foot_hole_x']]:
        for y in [-c['foot_hole_y'],c['foot_hole_y']]:
            tools.append(moved(cyl(9.525/2+gap,floor-1,floor+c['foot_stock']+1),(x,y,0)))
    # Rear/front bearing plates share a local Z definition, outward normal.
    axes=c['bearing_bolt_axes_yz'];vertices=[App.Vector(y,z,0) for y,z in axes]
    plate=Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(App.Vector(0,0,c['cover_stock']))
    plate=fused([plate,cyl(30,0,c['cover_stock'])]+
                [moved(cyl(10,0,c['cover_stock']),(y,z,0)) for y,z in axes])
    holes=[cyl(c['bush_radius']+gap,-1,c['cover_stock']+1)]
    holes += [moved(cyl(c['bearing_bolt_diameter']/2+gap,-1,c['cover_stock']+1),(y,z,0)) for y,z in axes]
    parts['bearing']=plate.cut(Part.makeCompound(holes)).removeSplitter()
    parts['bush']=cyl(c['bush_radius'],c['cover_stock']-c['bush_length'],c['cover_stock']).fuse(
        cyl(c['bush_flange_radius'],c['cover_stock'],c['cover_stock']+c['bush_flange_stock'])).cut(
        cyl(r+c['journal_gap'],-c['bush_length'],c['cover_stock']+c['bush_flange_stock']+1)).removeSplitter()
    parts['bearing_screw']=bolt(c['bearing_bolt_diameter'],c['bearing_bolt_length'],
        c['bearing_bolt_head_af'],c['bearing_bolt_head_height'])
    for sign,label in [(-1,'Rear'),(1,'Front')]:
        # local X->globalY,localY->globalZ,localZ->globalX for front.
        rot=App.Rotation(App.Vector(1,1,1),120)
        if sign<0:rot=App.Rotation(App.Vector(0,0,1),180).multiply(rot)
        p=App.Placement(App.Vector(sign*h,0,0),rot)
        add(label+'Bearing','bearing',list(p.Base),rot,'Bearings')
        add(label+'Bush','bush',list(p.Base),rot,'Bearings')
        for i,(y,z) in enumerate(axes):
            point=p.multVec(App.Vector(y,z,c['cover_stock']))
            add(label+'BearingScrew'+str(i+1),'bearing_screw',list(point),rot,'Bearings')
            tool=moved(cyl(c['bearing_bolt_diameter']/2+gap,
                c['cover_stock']-c['bearing_bolt_length']-.2,1),(y,z,0))
            tools.append(moved(tool,list(p.Base),rot))
    # Common cylinder and flange. Local axial coordinates are radial from shaft.
    f=c['cylinder_flange_stock'];offset=c['cylinder_bolt_offset']
    fp=[App.Vector(-23,0,seat),App.Vector(0,-offset-7,seat),
        App.Vector(23,0,seat),App.Vector(0,offset+7,seat)]
    flange=Part.Face(Part.makePolygon(fp+[fp[0]])).extrude(App.Vector(0,0,f))
    flange=flange.fuse(cyl(c['cylinder_radius'],seat,seat+f))
    for t in [-offset,offset]:flange=flange.fuse(moved(cyl(7,seat,seat+f),(0,t,0)))
    body=flange.fuse(cyl(c['cylinder_radius'],seat, c['cylinder_barrel_top']))
    body=body.fuse(Part.makeCone(c['cylinder_radius'],12,c['cylinder_top']-c['cylinder_barrel_top'],
        App.Vector(0,0,c['cylinder_barrel_top'])))
    body=body.cut(cyl(c['cylinder_bore_radius'],seat-1,c['cylinder_barrel_top']))
    body=body.cut(cyl(c['displacement_thread_radius']+gap,c['cylinder_barrel_top']-1,c['cylinder_top']+1))
    for t in [-offset,offset]:
        body=body.cut(moved(cyl(c['cylinder_bolt_diameter']/2+gap,seat-1,seat+f+1),(0,t,0)))
    parts['cylinder']=body.removeSplitter()
    parts['cylinder_screw']=bolt(c['cylinder_bolt_diameter'],c['cylinder_bolt_length'],
        c['cylinder_bolt_head_af'],c['cylinder_bolt_head_height'])
    parts['check_nut']=hexagon(c['check_nut_af'],c['cylinder_top'],c['cylinder_top']+c['check_nut_height']).cut(
        cyl(c['displacement_thread_radius']+gap,c['cylinder_top']-1,c['cylinder_top']+c['check_nut_height']+1)).removeSplitter()
    plug=cyl(c['displacement_stem_radius'],c['displacement_bottom'],c['cylinder_barrel_top'])
    plug=plug.fuse(cyl(c['displacement_thread_radius'],c['cylinder_barrel_top'],c['displacement_head_start']))
    parts['displacement_plug']=plug.fuse(hexagon(c['displacement_head_af'],c['displacement_head_start'],
        c['displacement_head_start']+c['displacement_head_height'])).removeSplitter()
    piston=cyl(c['piston_stem_radius'],0,c['piston_cone_start'])
    piston=piston.fuse(Part.makeCone(c['piston_stem_radius'],c['piston_radius'],
        c['piston_cup_start']-c['piston_cone_start'],App.Vector(0,0,c['piston_cone_start'])))
    piston=piston.fuse(cyl(c['piston_radius'],c['piston_cup_start'],c['piston_height']))
    parts['piston']=piston.cut(cyl(c['piston_inside_radius'],c['piston_cup_start']+c['piston_floor_stock'],c['piston_height']+1)).removeSplitter()
    shaft=xc(r,-h-c['cover_stock']-.5,c['pulley_hub_end'])
    shaft=shaft.fuse(xc(c['shaft_thread_radius'],c['pulley_hub_end'],c['shaft_thread_end']))
    shaft=shaft.fuse(xc(10,c['pulley_hub_start']-1,c['pulley_hub_start']))
    banks=[]
    for station,x in enumerate(c['station_x']):
        eccentric=(1 if station==0 else -1)*c['cam_eccentricity']
        shaft=shaft.fuse(xc(c['cam_radius'],x-c['cam_width']/2,x+c['cam_width']/2,eccentric,0))
        for sign,label in [(1,'Port'),(-1,'Starboard')]:
            name=label+str(station+1);rot=App.Rotation(App.Vector(1,0,0),-sign*45)
            n=rot.multVec(App.Vector(0,0,1));contact=c['cam_radius']+n.y*eccentric
            spring_bottom=contact+c['piston_cup_start']+c['piston_floor_stock']
            key='spring_high' if sign*eccentric>0 else 'spring_low'
            if key not in parts:parts[key],pitch=spring(c['spring_top']-spring_bottom,c)
            for k in ['cylinder','check_nut','displacement_plug']:
                add(name+'_'+k,k,(x,0,0),rot,name)
            add(name+'_piston','piston',list(App.Vector(x,0,0)+n*contact),rot,name)
            add(name+'_spring',key,list(App.Vector(x,0,0)+n*spring_bottom),rot,name)
            tools.append(moved(cyl(c['cylinder_bore_radius'],24,seat+1),(x,0,0),rot))
            for i,t in enumerate([-offset,offset]):
                p=App.Placement(App.Vector(x,0,0),rot).multVec(App.Vector(0,t,seat+f))
                add(name+'_screw'+str(i+1),'cylinder_screw',list(p),rot,name)
                hole=moved(cyl(c['cylinder_bolt_diameter']/2+gap,seat+f-c['cylinder_bolt_length']-.2,seat+1),(0,t,0))
                tools.append(moved(hole,(x,0,0),rot))
            banks.append(dict(name=name,x=x,normal=list(n),eccentric_y=eccentric,
                cam_contact_radial=contact,spring_bottom=spring_bottom,spring_top=c['spring_top']))
    # Recessed V pulley. V angle is transferred from belt, flange/web form inferred.
    mid=(c['pulley_rim_start']+c['pulley_rim_end'])/2
    bottom_width=c['pulley_groove_width']-2*c['pulley_groove_depth']*math.tan(math.radians(c['pulley_groove_angle']/2))
    assert bottom_width>0
    rr=c['pulley_radius'];root=rr-c['pulley_groove_depth']
    profile=[(c['pulley_rim_start'],rr),(mid-c['pulley_groove_width']/2,rr),
        (mid-bottom_width/2,root),(mid+bottom_width/2,root),
        (mid+c['pulley_groove_width']/2,rr),(c['pulley_rim_end'],rr),
        (c['pulley_rim_end'],root-5),(c['pulley_rim_start'],root-5)]
    pts=[App.Vector(x,rad,0) for x,rad in profile]
    pulley=Part.Face(Part.makePolygon(pts+pts[:1])).revolve(App.Vector(),App.Vector(1,0,0),360)
    pulley=pulley.fuse(xc(root-4,mid-c['pulley_web_stock']/2,mid+c['pulley_web_stock']/2))
    pulley=pulley.fuse(xc(c['pulley_hub_radius'],c['pulley_hub_start'],c['pulley_hub_end']))
    pulley=pulley.cut(xc(r+gap,c['pulley_hub_start']-1,c['pulley_hub_end']+1))
    # Semicircular key, flat face at key_top. Fit sockets are bounded separately.
    kr=c['key_radius'];kw=c['key_width'];kx=c['key_station_x'];top=c['key_top'];kg=c['key_gap']
    key=Part.makeCylinder(kr,kw,App.Vector(kx,-kw/2,top),App.Vector(0,1,0))
    parts['key']=key.common(box(kx-kr-1,kx+kr+1,-kw,kw,top-kr-1,top))
    keytool=Part.makeCylinder(kr+kg,kw+2*kg,App.Vector(kx,-kw/2-kg,top),App.Vector(0,1,0))
    keytool=keytool.common(box(kx-kr-1,kx+kr+1,-kw,kw,top-kr-1,top+kg))
    shaft=shaft.cut(keytool)
    pulley=pulley.cut(box(kx-kr-kg,kx+kr+kg,-kw/2-kg,kw/2+kg,0,top+kg))
    parts['shaft']=shaft.removeSplitter();parts['pulley']=pulley.removeSplitter()
    xrot=App.Rotation(App.Vector(0,1,0),90)
    parts['shaft_nut']=moved(hexagon(c['shaft_nut_af'],0,c['shaft_nut_height']).cut(
        cyl(c['shaft_thread_radius']+gap,-1,c['shaft_nut_height']+1)),(c['pulley_hub_end'],0,0),xrot)
    # Seven separately placed closure plugs; hidden pressure drillings deferred.
    pr=c['plug_shank_radius'];embed=c['plug_embed'];sq=c['plug_square']/2
    parts['pipe_plug']=cyl(pr,-embed,0).fuse(box(-sq,sq,-sq,sq,0,c['plug_head_height'])).removeSplitter()
    plug_positions=[]
    for x in c['oil_plug_x']:plug_positions.append(('Oil'+str(int(x)),[x,0,roof],App.Rotation(),True))
    for sign in [-1,1]:
        for i,(y,z) in enumerate(c['end_plug_yz']):
            plug_positions.append(('End'+str(sign)+'_'+str(i),[sign*h,y,z],App.Rotation(App.Vector(0,1,0),sign*90),False))
    plug_positions.append(('Drain',[0,0,floor],App.Rotation(App.Vector(1,0,0),180),False))
    for name,xyz,rot,open_oil in plug_positions:
        add(name+'_plug','pipe_plug',xyz,rot,'Closures')
        tools.append(moved(cyl(pr+gap,-embed-.2,1),xyz,rot))
        if open_oil:tools.append(moved(cyl(2.5,-70,-embed),xyz,rot))
    # Vented air-hole cover at roof center, inferred stem and side openings.
    vent=cyl(c['vent_stem_radius'],-6,4).fuse(cyl(c['vent_head_radius'],4,c['vent_height']))
    vent=vent.cut(cyl(1.5,-7,3))
    vent=vent.cut(Part.makeCylinder(1,12,App.Vector(-6,0,2),App.Vector(1,0,0)))
    parts['air_cover']=vent.removeSplitter()
    tools.append(moved(cyl(c['vent_stem_radius']+gap,roof-6.2,roof+1)))
    tools.append(cyl(1.5,25,roof-6))
    # Connected cutters are fused before subtracting from the casting.
    parts['base']=base.cut(fused(tools)).removeSplitter()
    for key in ['base','shaft','pulley','shaft_nut','key']:add(key,key,parent='Core')
    add('AirHoleCover','air_cover',(0,0,roof),parent='Closures')
    for key,shape in parts.items():
        assert shape.isValid() and len(shape.Solids)==1,(key,shape.isValid(),len(shape.Solids))
    notes.update(banks=banks,roof_height=roof,base_mounting_plane=floor,
        pulley_belt_plane_x=mid,pulley_groove_root_radius=root,
        pulley_groove_bottom_width=bottom_width,physical_occurrences=len(occ),
        mounting_hardware_deferred=12,installed_supports_complete=False,
        historical_dimensions_qualified=False)
    assert len(occ)==51
    return parts,occ,notes
