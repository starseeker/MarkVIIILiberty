"""Estimated transverse engine supports with source-allocated physical rivets.

Definition coordinates: channel center X=0, floor top Z=0, Y across tank.
Rivets: shaft along +Z, factory head seat at Z=0; shaped tail at grip.
All occurrences are returned in the tank frame (+X forward, +Y port, +Z up).
"""
import math
import FreeCAD as App
import Part

V=App.Vector
Z=V(0,0,1)


def box(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))


def xz_plate(points,y0,y1):
    v=[V(x,y0,z) for x,z in points]
    return Part.Face(Part.makePolygon(v+v[:1])).extrude(V(0,y1-y0,0))


def cap(radius,height):
    """Spherical cap above Z=0, with given base radius and axial height."""
    sphere_radius=(radius*radius+height*height)/(2*height)
    sphere=Part.makeSphere(sphere_radius,V(0,0,height-sphere_radius))
    return sphere.common(box(-radius-1,radius+1,-radius-1,radius+1,0,height+1))


def rivet(diameter,length,grip,c):
    """Retain blank-shank volume when estimating an upset spherical tail."""
    assert 0<grip<length
    radius=diameter/2;tail_radius=diameter*c['formed_radius_ratio']
    excess=math.pi*radius**2*(length-grip)
    lo,hi=0.0001,2*diameter
    for _ in range(70):
        h=(lo+hi)/2
        if math.pi*h*(3*tail_radius**2+h*h)/6<excess:lo=h
        else:hi=h
    tail_h=(lo+hi)/2
    head=cap(diameter*c['head_radius_ratio'],diameter*c['head_height_ratio'])
    head.rotate(V(),V(1,0,0),180)
    tail=cap(tail_radius,tail_h);tail.translate(V(0,0,grip))
    shape=Part.makeCylinder(radius,grip).multiFuse([head,tail]).removeSplitter()
    return shape,dict(diameter=diameter,blank_length=length,grip=grip,tail_height=tail_h,
                     head_radius=diameter*c['head_radius_ratio'],head_height=diameter*c['head_height_ratio'])


def parts(c):
    h=c['channel_height'];half=c['channel_half_span'];d=c['channel_depth']/2
    t=c['channel_flange'];w=c['channel_web'];s=c['gusset_stock'];cs=c['cleat_stock']
    channel=xz_plate([(-d,0),(d,0),(d,h),(-d,h),(-d,h-t),(d-w,h-t),(d-w,t),(-d,t)],-half,half)
    cleat=box(d,d+cs,-c['cleat_half_width'],c['cleat_half_width'],c['cleat_bottom'],h)
    cleat=cleat.fuse(box(d,d+c['cleat_overhang'],-c['cleat_half_width'],c['cleat_half_width'],h-cs,h)).removeSplitter()
    ghalf=c['gusset_half_width'];end=d+c['gusset_length']
    gusset=box(d,d+s,-ghalf,ghalf,0,h).fuse(box(d,end,-ghalf,ghalf,0,s))
    gusset=gusset.fuse(xz_plate([(d+s,s),(end,s),(d+s,h)],-s/2,s/2)).removeSplitter()
    shapes={'front_channel':channel.copy(),'rear_channel':channel.copy(),'cleat':cleat,'left_gusset':gusset.copy(),'right_gusset':gusset.copy()}
    occ=[];joints=[];forming={};holes=[]
    def install(key,name,xyz,assembly,rotation=None):
        rot=rotation or App.Rotation()
        occ.append(dict(key=key,name='EngineFrame_'+name,xyz=list(xyz),rotation=list(rot.Q),assembly=assembly))
    for which in ['front','rear']:
        install(which+'_channel',which.title()+'Channel',[c[which+'_x'],0,c['floor_top']],which.title()+'Crossmember')
    install('cleat','FrontCleat',[c['front_x'],0,c['floor_top']],'FrontCrossmember')
    for side,sign in [('left',1),('right',-1)]:
        install(side+'_gusset',side.title()+'Gusset',[c['rear_x'],sign*c['gusset_y'],c['floor_top']],'RearCrossmember')
    def joint(key,name,diameter,length,grip,local_base,axis,receivers,assembly,station,yoffset=0):
        if key not in shapes:shapes[key],forming[key]=rivet(diameter,length,grip,c)
        base=V(*local_base);direction=V(*axis)
        tool=Part.makeCylinder(diameter/2+c['hole_radial_allowance'],grip+2,base-direction,direction)
        for receiver,offset in receivers:
            cutter=tool.copy();cutter.translate(-V(*offset));shapes[receiver]=shapes[receiver].cut(cutter).removeSplitter()
        world=base+V(station,yoffset,c['floor_top']);rotation=App.Rotation(Z,direction)
        install(key,name,list(world),assembly,rotation)
        joints.append(dict(name='EngineFrame_'+name,key=key,base=list(world),axis=axis,grip=grip,
                           receivers=[r[0] for r in receivers],diameter=diameter,blank_length=length))
    # Two original nested front-channel rivets; four original nested rear rivets.
    for i,y in enumerate([-c['cleat_rivet_y'],c['cleat_rivet_y']],1):
        joint('front_rivet','FrontWebRivet%d'%i,c['front_rivet_diameter'],c['front_rivet_blank_length'],w+cs,
              [d-w,y,c['cleat_rivet_z']],[1,0,0],[('front_channel',[0,0,0]),('cleat',[0,0,0])],'FrontCrossmember',c['front_x'])
    for side,sign in [('left',1),('right',-1)]:
        sy=sign*c['gusset_y']
        for i,dy in enumerate([-c['gusset_rivet_y'],c['gusset_rivet_y']],1):
            joint('rear_rivet',side.title()+'WebRivet%d'%i,c['rear_rivet_diameter'],c['rear_rivet_blank_length'],w+s,
                  [d-w,sy+dy,c['gusset_web_rivet_z']],[1,0,0],[('rear_channel',[0,0,0]),(side+'_gusset',[0,sy,0])],
                  'RearCrossmember',c['rear_x'])
    # Additional SNL175 joints: 5 per channel and 2 per gusset, with real floor holes.
    for which,floor in [('front','hull_floor_6'),('rear','hull_floor_7')]:
        for i,y in enumerate(c['channel_floor_rivet_y'],1):
            x=c['channel_floor_rivet_x']
            joint('channel_floor_rivet',which.title()+'FloorRivet%d'%i,c['floor_rivet_diameter'],c['floor_rivet_blank_length'],c['floor_stock']+t,
                  [x,y,-c['floor_stock']],[0,0,1],[(which+'_channel',[0,0,0])],'FloorAttachments',c[which+'_x'])
            joints[-1]['floor']=floor;holes.append(joints[-1])
    for side,sign in [('left',1),('right',-1)]:
        sy=sign*c['gusset_y']
        for i,dy in enumerate([-c['gusset_rivet_y'],c['gusset_rivet_y']],1):
            joint('gusset_floor_rivet',side.title()+'FloorRivet%d'%i,c['floor_rivet_diameter'],c['floor_rivet_blank_length'],c['floor_stock']+s,
                  [c['gusset_floor_rivet_x'],sy+dy,-c['floor_stock']],[0,0,1],[(side+'_gusset',[0,sy,0])],'FloorAttachments',c['rear_x'])
            joints[-1]['floor']='hull_floor_7';holes.append(joints[-1])
    for key,shape in shapes.items():
        assert shape.isValid() and len(shape.Solids)==1,key
    assert len(occ)==25
    return shapes,occ,dict(joints=joints,floor_holes=holes,rivet_forming=forming)
