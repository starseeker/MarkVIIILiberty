"""Source-identified hull plates; plane seams and unmeasured details are partial."""
import math
import FreeCAD as App
import Part
from .upper_parts import box,prism,xz,xy,rect,cylinder,slot


def clip(poly,a,b,c):
    """Clip XZ coordinates to a*x+b*z+c >= 0, retaining boundary vertices."""
    result=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        dp=a*p[0]+b*p[1]+c;dq=a*q[0]+b*q[1]+c
        if dp>=-1e-8:result.append(p)
        if (dp>1e-8 and dq< -1e-8) or (dp< -1e-8 and dq>1e-8):
            t=dp/(dp-dq);result.append([p[i]+t*(q[i]-p[i]) for i in range(2)])
    cleaned=[]
    for p in result:
        if not cleaned or math.dist(p,cleaned[-1])>1e-7:cleaned.append(p)
    if len(cleaned)>1 and math.dist(cleaned[0],cleaned[-1])<1e-7:cleaned.pop()
    if len(cleaned)<3:raise ValueError('Hull plate mask has no area')
    return cleaned


def layout(a):
    v=a['values'];ox,oz=a['image_origin_xz'];sx,sz=a['pixel_scale_xz']
    X=lambda u:ox+u*sx;Z=lambda w:oz+w*sz
    inner=v['track_centers']/2-v['hull_frame_clear']/2
    outer=v['track_centers']/2+v['hull_frame_clear']/2
    body_inner=outer;front_inner=inner-v['hull_side_thickness']
    return v,X,Z,inner,outer,body_inner,front_inner


def strip(x0,z0,x1,z1,y0,y1,t,up=False):
    """Normal-thickness plate between vertical end planes (miter approximation)."""
    dz=t*math.hypot(x1-x0,z1-z0)/abs(x1-x0)
    if not up:dz=-dz
    return xz([(x0,z0),(x1,z1),(x1,z1+dz),(x0,z0+dz)],y0,y1-y0)


def stock(a):
    role=a['role'];h=a['hand'];v,X,Z,inner,outer,wide,narrow=layout(a)
    floor=v['hull_ground_clearance'];ft=v['hull_floor_thickness'];g=v['hull_door_gap']
    engine_back=v['hull_engine_back_x'];engine_front=engine_back+v['hull_engine_length']
    center=X(860);door_half=v['hull_door_leaf_width']/2
    sill=floor+v['hull_door_sill'];lower0=sill+g;lower1=lower0+v['hull_door_lower_height']
    upper0=lower1+g;upper1=upper0+v['hull_door_upper_height']
    upper_front=v['upper_base_x']+v['upper_length']/2
    upper_rear=v['upper_base_x']-v['upper_length']/2
    driver_front=upper_front+v['driver_length'];roof_z=v['upper_base_z']
    inlet_front=v['hull_inlet_front_x'];inlet_rear=inlet_front-v['hull_inlet_length']
    rear_inlet=inlet_rear-v['hull_roof_cross_strip'];outlet_front=rear_inlet-v['hull_engine_cover_length']
    outlet_rear=outlet_front-v['hull_outlet_length'];roof_front=inlet_front+v['hull_roof_cross_strip']
    engine_roof_z=lambda x:Z(335)+(x-engine_back)*(roof_z-Z(335))/(roof_front-engine_back)
    gas_rear=X(1630);gas_bottom=Z(476)
    tools=[]
    side_roles={'front_upper','front_lower','front_sponson','under_sponson_front','under_sponson_rear',
        'over_sponson','aft_sponson','door_aft_surround','door_header','door_sill','engine_side_1',
        'engine_side_2','engine_side_3','engine_access_leaf','rear_wing','rear_end','inner_front_upper',
        'inner_front_lower','inner_front_sponson','inner_fuel_side','inner_rear_end',
        'inner_skirt_front','inner_skirt_rear','outer_skirt_front','outer_skirt_rear','door_upper','door_lower'}
    if role in side_roles:
        inside=role.startswith('inner_');skirt='skirt' in role
        base_role=role.removeprefix('inner_')
        t=v['hull_skirt_thickness'] if skirt else v['hull_front_thickness'] if base_role in {'front_upper','front_lower','front_sponson'} else v['hull_side_thickness']
        # The inner roller-facing plane is independent of local armor thickness.
        y=inner-t if h==1 and inside else -inner if inside else outer if h==1 else -outer-t
        poly=a['outline']
        intervals={'front_upper':(X(400),X(90)),'front_lower':(X(400),X(90)),
            'front_sponson':(X(510),X(400)),'under_sponson_front':(X(650),X(510)),
            'under_sponson_rear':(X(790),X(650)),'over_sponson':(X(790),X(510)),
            'aft_sponson':(center+door_half+g,X(790)),
            'door_aft_surround':(engine_front,center-door_half-g),
            'door_header':(center-door_half-g,center+door_half+g),
            'door_sill':(center-door_half-g,center+door_half+g),
            'engine_side_1':(X(1150),engine_front),'engine_side_2':(X(1300),X(1150)),
            'engine_side_3':(engine_back,X(1300)),'rear_wing':(gas_rear,engine_back),
            'rear_end':(X(1800),gas_rear),'fuel_side':(gas_rear,engine_back)}
        if skirt:
            limits=(engine_front,X(90)) if role.endswith('front') else (X(1800),engine_front)
        elif role.startswith('door_') and role in {'door_upper','door_lower'}:
            limits=(center-door_half,center+door_half)
        elif role=='engine_access_leaf':
            limits=(X(1375)-v['hull_service_width']/2,X(1375)+v['hull_service_width']/2)
        else:limits=intervals[base_role]
        poly=clip(poly,1,0,-limits[0]);poly=clip(poly,-1,0,limits[1])
        if role=='door_upper':poly=clip(clip(poly,0,1,-upper0),0,-1,upper1)
        elif role=='door_lower':poly=clip(clip(poly,0,1,-lower0),0,-1,lower1)
        elif role=='door_header':poly=clip(poly,0,1,-upper1-g)
        elif role=='door_sill':poly=clip(poly,0,-1,sill)
        elif role=='engine_access_leaf':poly=clip(clip(poly,0,1,-(1000-v['hull_service_height']/2)),0,-1,1000+v['hull_service_height']/2)
        elif role.startswith('under_sponson'):poly=clip(poly,0,-1,Z(440))
        elif role=='over_sponson':poly=clip(poly,0,1,-Z(270))
        elif base_role in {'front_upper','front_lower'}:
            # The diagonal seam is inferred from the oblique seam topology.
            x0,z0=X(108),Z(340);x1,z1=X(400),Z(465)
            slope=(z1-z0)/(x1-x0)
            aa,bb,cc=-slope,1,slope*x0-z0
            if base_role=='front_lower':aa,bb,cc=-aa,-bb,-cc
            poly=clip(poly,aa,bb,cc)
        # Lower shell strip follows the source bottom, with a separately inferred upper edge.
        lower_line=[(X(u),Z(z)) for u,z in [(90,325),(151,350),(245,430),(400,495)]]
        lower_line += [(X(680),floor),(engine_back-v['hull_side_thickness'],floor),(X(1630),Z(500)),(X(1800),Z(430))]
        region=lower_line+[(X(1800),10000),(X(90),10000)] if skirt else lower_line+[(X(1800),-10000),(X(90),-10000)]
        tools.append(prism(*xz(region,-3000,6000)))
        if inside and base_role in {'front_upper','front_sponson'}:
            tools.append(box(upper_rear,driver_front,-3000,3000,roof_z-v['hull_roof_thickness'],10000))
        if base_role=='front_upper':
            from .idler_parts import hull_tools
            tools.extend(hull_tools(a['idler_clearance'],not inside))
        if base_role=='rear_end':tools.append(cylinder(v['hull_drive_bore']/2,(X(1715),0,Z(453)),(0,1,0),6000))
        if role=='front_sponson':tools.append(slot((X(461),0,Z(292)),v['hull_peep_length'],v['hull_peep_height']))
        if role=='engine_side_1':tools.append(slot((X(1050),0,Z(315)),v['hull_peep_length'],v['hull_peep_height']))
        if role=='engine_side_3':
            w=v['hull_service_width']/2+g;hh=v['hull_service_height']/2+g
            tools.append(box(X(1375)-w,X(1375)+w,-3000,3000,1000-hh,1000+hh))
        if role=='door_upper':
            tools.append(cylinder(v['hull_door_mount_diameter']/2,(center,0,upper0+v['hull_door_upper_height']*.63),(0,1,0),6000))
            tools.append(box(center-44.45,center+44.45,-3000,3000,upper0+120,upper0+183.5))
        return xz(poly,y,t),tools
    if role=='floor':
        index=int(a['index'])
        start,end=X(442),X(680)
        split=X(510);zstart=Z(421)
        zsplit=floor+(split-end)*(zstart-floor)/(start-end)
        stations=[(start,zstart,narrow),(split,zsplit,narrow),(end,floor,wide)]
        stations += [(end+(engine_back-end)*i/6,floor,wide) for i in range(1,7)]
        x0,z0,w0=stations[index-1];x1,z1,w1=stations[index]
        w=max(w0,w1)
        spec=strip(x0,z0,x1,z1,-w,w,ft,True)
        plan=prism(*xy([(x0,-w0),(x0,w0),(x1,w1),(x1,-w1)],-1000,5000))
        tools.append(prism(*spec).cut(plan))
        return spec,tools
    if role=='floor_fuel':return xy(rect(gas_rear+v['hull_back_thickness'],engine_back,-narrow,narrow),gas_bottom,ft),tools
    if role in {'engine_back','fuel_back'}:
        x=engine_back if role=='engine_back' else gas_rear
        width=wide if role=='engine_back' else narrow
        bottom=floor+ft if role=='engine_back' else gas_bottom+ft
        top=Z(335)-v['hull_roof_thickness']*2 if role=='engine_back' else Z(381)-v['hull_fuel_roof_thickness']*2
        t=v['hull_side_thickness'] if role=='engine_back' else v['hull_back_thickness']
        return ([(x,-width,bottom),(x,width,bottom),(x,width,top),(x,-width,top)],(t,0,0)),tools
    if role=='front_slope':
        spec=strip(X(442),Z(421),driver_front,roof_z,-narrow,narrow,v['hull_side_thickness'],True)
        tools.append(box(-10000,15000,-3000,3000,roof_z,10000))
        for hand in [-1,1]:
            roof_stock,_=stock({**a,'role':'roof_driver','hand':hand})
            tools.append(prism(*roof_stock))
        return spec,tools
    if role in {'roof_front','roof_driver'}:
        half=v['main_turret_width']/2-v['upper_wall'];driverhalf=v['driver_width']/2-v['driver_wall']
        if role=='roof_front':pts=[(upper_rear,half),(upper_front,half),(upper_front,narrow),(driver_front,narrow),(driver_front,wide),(upper_rear,wide)]
        else:pts=rect(upper_front,driver_front,driverhalf,narrow)
        pts=[(x,h*y) for x,y in pts]
        return xy(pts,roof_z,-v['hull_roof_thickness']),tools
    if role=='roof_aft_upper':return xy(rect(roof_front,upper_rear,-v['hull_louver_width']/2,v['hull_louver_width']/2),roof_z,-v['hull_roof_thickness']),tools
    if role in {'roof_before_inlet','roof_after_inlet','roof_engine_cover'}:
        limits={'roof_before_inlet':(inlet_front,roof_front),'roof_after_inlet':(rear_inlet,inlet_rear),'roof_engine_cover':(outlet_front,rear_inlet)}[role]
        x0,x1=limits;w=v['hull_louver_width']/2
        return strip(x0,engine_roof_z(x0),x1,engine_roof_z(x1),-w,w,v['hull_roof_thickness']),tools
    if role=='roof_track_rear':
        y0,y1=(v['hull_louver_width']/2,wide) if h==1 else (-wide,-v['hull_louver_width']/2)
        # A short level section joins the flat forward roof at the upper shell's rear.
        t=v['hull_roof_thickness'];dz=t*math.sqrt(1+((roof_z-Z(335))/(roof_front-engine_back))**2)
        slope=(roof_z-Z(335))/(roof_front-engine_back)
        inner_corner=roof_front+(dz-t)/slope
        pts=[(upper_rear,roof_z),(roof_front,roof_z),(engine_back,Z(335)),(engine_back,Z(335)-dz),(inner_corner,roof_z-t),(upper_rear,roof_z-t)]
        return xz(pts,y0,y1-y0),tools
    if role=='roof_fuel':
        t=v['hull_fuel_roof_thickness'];w=narrow
        # Folded central roof with vertical-miter ends; radius remains unlocated.
        dz1=t*math.sqrt(1+((roof_z-Z(335))/(roof_front-engine_back))**2)
        dz2=t*math.sqrt(1+((Z(335)-Z(381))/(engine_back-gas_rear))**2)
        s1=(roof_z-Z(335))/(roof_front-engine_back);s2=(Z(335)-Z(381))/(engine_back-gas_rear)
        dx=(dz1-dz2)/(s1-s2)
        pts=[(outlet_rear,engine_roof_z(outlet_rear)),(engine_back,Z(335)),(gas_rear,Z(381)),(gas_rear,Z(381)-dz2),(engine_back+dx,Z(335)+s1*dx-dz1),(outlet_rear,engine_roof_z(outlet_rear)-dz1)]
        spec=xz(pts,-w,2*w)
        # Rear track-roof panels own the shoulder strip forward of the engine backplate.
        tools.append(box(engine_back,15000,v['hull_louver_width']/2,3000,-1000,5000))
        tools.append(box(engine_back,15000,-3000,-v['hull_louver_width']/2,-1000,5000))
        return spec,tools
    raise ValueError('Unknown hull plate role: '+role)


def build(doc,name,a):
    from .cad_build import sketch_polygon,pad
    from .track_parts import feature
    (pts,vec),tools=stock(a)
    if a.get('lower_support_holes'):
        from .lower_support_parts import hull_tools
        tools.extend(hull_tools(a['lower_support_holes']))
    body=doc.addObject('PartDesign::Body',name)
    origin=App.Vector(*pts[0]);direction=App.Vector(*vec)
    placement=App.Placement(origin,App.Rotation(App.Vector(0,0,1),direction))
    inverse=placement.inverse();local=[inverse.multVec(App.Vector(*p)) for p in pts]
    if max(abs(p.z) for p in local)>1e-7:raise ValueError('Nonplanar hull plate stock: '+a['role'])
    sketch=sketch_polygon(body,'SourcePlateSection',[(p.x,p.y) for p in local],placement)
    solid=pad(body,sketch,direction.Length).Shape
    clearance=a.get('roller_clearance')
    if clearance:
        for st in clearance['stations']:
            tools.append(Part.makeCylinder(clearance['pin_radius'],6000,App.Vector(st['x'],-3000,st['z']),App.Vector(0,1,0)))
            if st['kind']=='upper':
                for hand in [-1,1]:
                    y=hand*a['values']['track_centers']/2
                    # Inferred local roof relief for the upper roller/tube,
                    # pending reconstruction of the separate SH294A covers.
                    for offset in [-clearance['wheel_offset'],clearance['wheel_offset']]:
                        tools.append(Part.makeCylinder(clearance['wheel_radius'],clearance['wheel_width'],
                            App.Vector(st['x'],y+offset-clearance['wheel_width']/2,st['z']),App.Vector(0,1,0)))
                    tools.append(Part.makeCylinder(clearance['tube_radius'],clearance['tube_length'],
                        App.Vector(st['x'],y-clearance['tube_length']/2,st['z']),App.Vector(0,1,0)))
                    for offset in [-clearance['ring_offset'],clearance['ring_offset']]:
                        tools.append(Part.makeCylinder(clearance['ring_radius'],clearance['ring_width'],
                            App.Vector(st['x'],y+offset-clearance['ring_width']/2,st['z']),App.Vector(0,1,0)))
                    if a['role']=='roof_track_rear':
                        # Provisional access relief around M2092 and its clamp.
                        # Exact cover/roof joints are still unlocated. Keep this
                        # local to the rear roof and dependent on the shaft.
                        for sign in [-1,1]:
                            ys=sorted([y+sign*(clearance['support_offset']-1),
                                       y+sign*(clearance['support_offset']+clearance['support_width']+1)])
                            half=clearance['support_length']/2+1
                            tools.append(box(st['x']-half,st['x']+half,*ys,
                                             st['z']+clearance['support_toe']-1,st['z']+clearance['clamp_top']+1))
                        # Local vertical-leg clearance under the upper cover.
                        # It also follows the station when track pitch changes.
                        for offset in [-clearance['clamp_offset'],clearance['clamp_offset']]:
                            for dx in [-clearance['clamp_leg_x'],clearance['clamp_leg_x']]:
                                tools.append(Part.makeCylinder(clearance['clamp_leg_radius'],clearance['clamp_top']+2,
                                    App.Vector(st['x']+dx,y+offset,st['z']-1)))
    for tool in tools:
        if tool.Solids and solid.BoundBox.intersect(tool.BoundBox):solid=solid.cut(tool)
    if tools:feature(body,'SeamsOpeningsAndJoints',solid.removeSplitter())
    return body
