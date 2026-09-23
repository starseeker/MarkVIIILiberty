"""Static three-point engine suspension; source identities, estimated cast forms.

Each structural definition uses its crossmember X station, rail Y center where
applicable, and floor top as local origin. Rails use their aft end and lower face.
Hardware is axial +Z with its head seat at zero. Occurrences are in tank axes.
"""
import math
import FreeCAD as App
import Part
from engine_crossmember_parts import box,xz_plate

V=App.Vector;Z=V(0,0,1)


def yz_plate(points,x0,x1):
    v=[V(x0,y,z) for y,z in points]
    return Part.Face(Part.makePolygon(v+v[:1])).extrude(V(x1-x0,0,0))


def hexagon(af,z0,z1):
    radius=af/math.sqrt(3)
    v=[V(radius*math.cos(i*math.pi/3),radius*math.sin(i*math.pi/3),z0) for i in range(6)]
    return Part.Face(Part.makePolygon(v+v[:1])).extrude(V(0,0,z1-z0))


def hardware(diameter,length,c):
    r=diameter/2;af=c['hex_across_flats_ratio']*diameter
    head_h=c['head_height_ratio']*diameter;nut_h=c['nut_height_ratio']*diameter;lock_h=c['lock_stock_ratio']*diameter
    bolt=hexagon(af,-head_h,0).fuse(Part.makeCylinder(r,length)).removeSplitter()
    nut=hexagon(af,0,nut_h).cut(Part.makeCylinder(r+c['thread_radial_allowance'],nut_h+2,V(0,0,-1))).removeSplitter()
    ro=c['lock_outer_radius_ratio']*diameter
    lock=Part.makeCylinder(ro,lock_h).cut(Part.makeCylinder(r+c['hole_radial_allowance'],lock_h+2,V(0,0,-1)))
    lock=lock.cut(box(0,ro+1,-c['lock_split_width']/2,c['lock_split_width']/2,-1,lock_h+1)).removeSplitter()
    return bolt,nut,lock,dict(diameter=diameter,length=length,head_height=head_h,nut_height=nut_h,lock_stock=lock_h,head_af=af)


def parts(c,cc,axis_z,originals):
    floor=cc['floor_top'];h=cc['channel_height'];d=cc['channel_depth']/2;cw=cc['channel_web'];cf=cc['channel_flange'];cs=cc['cleat_stock']
    ry=c['rail_half_spacing'];rw=c['rail_width'];rh=c['rail_height'];rf=c['rail_flange'];web=c['rail_web']
    top=axis_z+c['engine_mount_z_offset_from_crankshaft'];bottom=top-rh;local_bottom=bottom-floor
    stock=c['packing_stock'];base_z=h+stock;base_top=base_z+c['rear_base_stock'];pad_bottom=local_bottom-c['rear_top_pad_stock']
    slope=math.tan(math.radians(c['rear_channel_upper_taper_deg']))
    defs={};occ=[];joints=[];datums=dict(engine_mount_z=top,rail_bottom_z=bottom,rail_inner_gap=2*ry-rw,
        engine_interface_conditional=True,bracket_profiles_estimated=True)
    # Rear upper flange receives M190 washers. Preserve lower flange and old holes.
    rear=originals['EngineFrame_RearChannel'].copy()
    taper=xz_plate([(-d,h-cf),(d-cw,h-cf-slope*(2*d-cw)),(d-cw,h-cf)],-cc['channel_half_span'],cc['channel_half_span'])
    rear=rear.fuse(taper).removeSplitter()
    cleat=originals['EngineFrame_FrontCleat'].copy()
    hub_bottom=h+stock;hub_top=hub_bottom+c['front_hub_height'];pivot_z=(hub_bottom+hub_top)/2
    cleat=cleat.fuse(box(d,d+cs,-cc['cleat_half_width'],cc['cleat_half_width'],h,hub_top)).removeSplitter()
    revisions={'EngineFrame_RearChannel':rear,'EngineFrame_FrontCleat':cleat}
    # Rails use the conditional17in engine bolt-row spacing. Engine bores deferred.
    for side,sign in [('left',1),('right',-1)]:
        points=[(-rw/2,0),(rw/2,0),(rw/2,rh),(-rw/2,rh),(-rw/2,rh-rf),(rw/2-web,rh-rf),(rw/2-web,rf),(-rw/2,rf)]
        defs[side+'_rail']=yz_plate([(sign*y,z) for y,z in points],0,c['rail_front_x']-c['rail_rear_x'])
    rear_bracket=box(c['rear_base_x_min'],c['rear_base_x_max'],-c['rear_base_half_width'],c['rear_base_half_width'],base_z,base_top)
    rear_bracket=rear_bracket.fuse(box(-c['rear_top_pad_length']/2,c['rear_top_pad_length']/2,-rw/2,rw/2,pad_bottom,local_bottom))
    t=c['rear_web_stock']
    rear_bracket=rear_bracket.fuse(yz_plate([(-24,base_top),(24,base_top),(22,pad_bottom),(-22,pad_bottom)],-t/2,t/2))
    for sy in [-c['rear_rib_y'],c['rear_rib_y']]:
        rear_bracket=rear_bracket.fuse(xz_plate([(-20,base_top),(20,base_top),(c['rear_top_pad_length']/2,pad_bottom),(-c['rear_top_pad_length']/2,pad_bottom)],sy-t/2,sy+t/2))
    defs['left_bracket']=rear_bracket.removeSplitter();defs['right_bracket']=defs['left_bracket'].copy()
    defs['rear_packing']=box(c['rear_base_x_min'],c['rear_base_x_max'],-c['rear_base_half_width'],c['rear_base_half_width'],h,h+stock)
    front_x0=d+cs;front_x1=front_x0+c['front_hub_x_stock'];hh=c['front_hub_half_width']
    front=box(front_x0,front_x1,-hh,hh,hub_bottom,hub_top)
    for sign in [-1,1]:
        outline=[(hh,hub_top),(ry-rw/2,local_bottom),(ry+rw/2,local_bottom),
                 (ry+rw/2,local_bottom-c['front_pad_stock']),(ry-rw/2,local_bottom-c['front_arm_depth']),
                 (hh,hub_top-c['front_arm_depth'])]
        front=front.fuse(yz_plate([(sign*y,z) for y,z in outline],front_x0,front_x1))
        front=front.fuse(box(c['front_pad_x']-c['front_pad_length']/2,c['front_pad_x']+c['front_pad_length']/2,
                            sign*ry-rw/2,sign*ry+rw/2,local_bottom-c['front_pad_stock'],local_bottom))
        front=front.fuse(Part.makeCylinder(c['front_cap_boss_radius'],c['front_cap_boss_depth'],
                         V(c['front_pad_x']+c['front_cap_x_offset'],sign*ry,local_bottom-c['front_cap_boss_depth'])))
    defs['front_bracket']=front.removeSplitter()
    defs['front_packing']=box(front_x0,front_x1,-hh,hh,h,h+stock)
    half=c['bevel_washer_side']/2;center=c['bevel_washer_center_stock']
    defs['bevel_washer']=xz_plate([(-half,0),(half,0),(half,center-slope*half),(-half,center+slope*half)],-half,half)
    defs['bevel_washer']=defs['bevel_washer'].cut(Part.makeCylinder(c['rear_bolt_diameter']/2+c['hole_radial_allowance'],30,V(0,0,-1))).removeSplitter()
    hardware_data={}
    for key,diam,length in [('half',c['half_bolt_diameter'],c['half_bolt_length']),('rear',c['rear_bolt_diameter'],c['rear_bolt_length']),('pivot',c['pivot_bolt_diameter'],c['pivot_bolt_length'])]:
        bolt,nut,lock,hd=hardware(diam,length,c);defs[key+'_bolt']=bolt;defs[key+'_nut']=nut;defs[key+'_lock']=lock;hardware_data[key]=hd
    defs['cap']=hardware(c['cap_diameter'],c['cap_length'],c)[0]
    def install(key,name,base,assembly,axis=Z):
        rot=App.Rotation(Z,axis);occ.append(dict(key=key,name='EngineSuspension_'+name,xyz=list(base),rotation=list(rot.Q),assembly=assembly))
    positions={}
    def structural(key,name,base,assembly):
        positions[key]=V(*base);install(key,name,V(*base),assembly)
    for side,sign in [('left',1),('right',-1)]:
        structural(side+'_rail',side.title()+'Rail',[c['rail_rear_x'],sign*ry,bottom],'LongitudinalSupports')
        structural(side+'_bracket',side.title()+'Bracket',[cc['rear_x'],sign*ry,floor],side.title()+'RearSuspension')
        install('rear_packing',side.title()+'Packing',V(cc['rear_x'],sign*ry,floor),side.title()+'RearSuspension')
    structural('front_bracket','FrontBracket',[cc['front_x'],0,floor],'FrontSuspension')
    structural('front_packing','FrontPacking',[cc['front_x'],0,floor],'FrontSuspension')
    receiver_positions={'EngineFrame_RearChannel':V(cc['rear_x'],0,floor),'EngineFrame_FrontCleat':V(cc['front_x'],0,floor),**positions}
    def cut(key,base,axis,length,radius,offset=None):
        tool=Part.makeCylinder(radius,length+2,base-axis,axis)
        tool.translate(-(offset if offset is not None else receiver_positions[key]))
        target=revisions if key in revisions else defs;target[key]=target[key].cut(tool).removeSplitter()
    def bolt_set(key,name,base,axis,grip,receivers,assembly):
        hd=hardware_data[key];diam=hd['diameter']
        for receiver,offset in receivers:cut(receiver,base,axis,grip,diam/2+c['hole_radial_allowance'],offset)
        install(key+'_bolt',name+'Bolt',base,assembly,axis)
        install(key+'_lock',name+'Lock',base+axis*grip,assembly,axis)
        install(key+'_nut',name+'Nut',base+axis*(grip+hd['lock_stock']),assembly,axis)
        joints.append(dict(name=name,hardware=key,base=list(base),axis=list(axis),grip=grip,
                           receiver_keys=[r[0] for r in receivers],thread_protrusion=hd['length']-grip-hd['lock_stock']-hd['nut_height']))
    # Rear supports: four top bolts, two base bolts and bevel seats per side.
    bx=c['rear_base_bolt_x'];underside=h-cf-slope*(bx+d);washer_bottom=underside-center
    for side,sign in [('left',1),('right',-1)]:
        sy=sign*ry;group=side.title()+'RearSuspension'
        for i,x in enumerate(c['rear_rail_bolt_x'],1):
            bolt_set('half',side.title()+'Rail%d'%i,V(cc['rear_x']+x,sy,floor+pad_bottom),Z,c['rear_top_pad_stock']+rf,
                     [(side+'_bracket',None),(side+'_rail',None)],group)
        for i,dy in enumerate(c['rear_base_bolt_y'],1):
            base=V(cc['rear_x']+bx,sy+dy,floor+base_top)
            install('bevel_washer',side.title()+'Bevel%d'%i,V(base.x,base.y,floor+washer_bottom),group)
            bolt_set('rear',side.title()+'Base%d'%i,base,-Z,base_top-washer_bottom,
                     [(side+'_bracket',None),('rear_packing',V(cc['rear_x'],sy,floor)),('EngineFrame_RearChannel',None)],group)
    # Front yoke: source count retained; mixed bolt/cap allocation is a hypothesis.
    for side,sign in [('left',1),('right',-1)]:
        x=c['front_pad_x']+c['front_bolt_x_offset'];y=sign*ry
        bolt_set('half',side.title()+'FrontRail',V(cc['front_x']+x,y,bottom-c['front_pad_stock']),Z,c['front_pad_stock']+rf,
                 [('front_bracket',None),(side+'_rail',None)],'FrontSuspension')
        cx=c['front_pad_x']+c['front_cap_x_offset'];lock_h=hardware_data['half']['lock_stock']
        base=V(cc['front_x']+cx,y,bottom+rf+lock_h)
        install('cap',side.title()+'Cap',base,'FrontSuspension',-Z)
        install('half_lock',side.title()+'CapLock',base,'FrontSuspension',-Z)
        cut(side+'_rail',base,-Z,rf+lock_h,c['cap_diameter']/2+c['hole_radial_allowance'])
        # Nominal blind thread envelope from rail seat into thick casting boss.
        engagement=c['cap_length']-rf-lock_h
        thread_start=V(base.x,base.y,bottom)
        cutter=Part.makeCylinder(c['cap_diameter']/2+c['thread_radial_allowance'],engagement+c['cap_blind_extra_depth']+1,thread_start+Z,-Z)
        cutter.translate(-positions['front_bracket']);defs['front_bracket']=defs['front_bracket'].cut(cutter).removeSplitter()
        joints.append(dict(name=side.title()+'Cap',hardware='cap',base=list(base),axis=[0,0,-1],
                           grip=rf+lock_h,thread_engagement=engagement,blind_floor=c['front_cap_boss_depth']-engagement-c['cap_blind_extra_depth'],receiver_keys=['front_bracket',side+'_rail']))
    pivot=V(cc['front_x']+d,0,floor+pivot_z)
    bolt_set('pivot','FrontPivot',pivot,V(1,0,0),cs+c['front_hub_x_stock'],
             [('EngineFrame_FrontCleat',None),('front_bracket',None)],'FrontSuspension')
    for key,s in {**defs,**revisions}.items():assert s.isValid() and len(s.Solids)==1,key
    assert len(occ)==61
    datums.update(joints=joints,hardware=hardware_data,receiver_positions={k:list(v) for k,v in receiver_positions.items()},
                  rear_channel_upper_taper=slope,rear_washer_bottom_world_z=floor+washer_bottom,
                  rear_base_top_world_z=floor+base_top,front_pivot=list(pivot),front_hub_bottom_world_z=floor+hub_bottom,
                  cap_boss_bottom_world_z=bottom-c['front_cap_boss_depth'],catalogue_support_children=72,
                  aviation_reference_hole_count_per_side=7,tank_bolt_set_count_per_rail=6,engine_holes_drilled=False)
    return defs,occ,revisions,datums
