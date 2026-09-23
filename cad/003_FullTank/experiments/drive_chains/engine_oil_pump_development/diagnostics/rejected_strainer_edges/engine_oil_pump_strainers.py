"""Separate strainer frames and porous screen approximations.

LIB29/30/33 and SNL plate33 support basket construction. Dimensions, four end
spokes and eight side posts are estimates. Gauze uses coarse square apertures:
individual woven wires, solder joints and actual filtration rating are unknown.
"""
import math
import FreeCAD as App
import Part
from engine_oil_pump_parts import V,Z,ring,cylinder,rev_z,hex_z,moved,united
from engine_crossmember_parts import box


def sector(inner,outer,a,b,low,high):
    def pt(r,theta):return V(r*math.cos(theta),r*math.sin(theta),low)
    a,b=math.radians(a),math.radians(b)
    edges=[Part.makeLine(pt(inner,a),pt(outer,a)),Part.Arc(pt(outer,a),pt(outer,(a+b)/2),pt(outer,b)).toShape(),Part.makeLine(pt(outer,b),pt(inner,b)),Part.Arc(pt(inner,b),pt(inner,(a+b)/2),pt(inner,a)).toShape()]
    return Part.Face(Part.Wire(edges)).extrude(Z*(high-low))


def side_gauze(ro,stock,low,high,count,rows,rib):
    shell=ring(ro,ro-stock,low,high);tools=[];step=(high-low)/rows
    width=2*ro*math.sin(math.pi/count)-rib
    for i in range(count):
        for j in range(rows):
            tools.append(moved(box(ro-stock-1,ro+1,-width/2,width/2,low+j*step+rib/2,low+(j+1)*step-rib/2),angle=360*i/count))
    return shell.cut(Part.makeCompound(tools))


def face_gauze(profile,outer,inner,pitch,rib):
    shell=rev_z(profile);tools=[];half=(pitch-rib)/2
    # Keep continuous inner/outer borders. Every aperture lies wholly inside
    # those borders, so the screen remains one connected manufactured piece.
    count=math.ceil(outer/pitch)
    for ix in range(-count,count+1):
        for iy in range(-count,count+1):
            x,y=ix*pitch,iy*pitch
            corners=[math.hypot(x+sx*half,y+sy*half) for sx in [-1,1] for sy in [-1,1]]
            closest=math.hypot(max(abs(x)-half,0),max(abs(y)-half,0))
            if max(corners)>outer-rib or closest<inner+rib:continue
            tools.append(box(x-half,x+half,y-half,y+half,-110,100))
    return shell.cut(Part.makeCompound(tools)),len(tools)


def extend(c,p,occ,groups,d,progress=None):
    def add(key,name):
        occ.append(dict(key=key,name='EngineOilPump_'+name,xyz=[0,0,0],rotation=list(App.Rotation().Q),assembly='EngineOilPumpStrainers'))
        if progress:progress(key,p[key])
    ro=c['filter_outer_radius'];stock=c['filter_frame_stock'];inside=ro-stock;mesh_stock=c['screen_stock'];mesh_r=inside-mesh_stock
    center=c['filter_center_land_radius'];hole=c['upper_boss_radius']+c['thread_gap'];post_count=c['filter_side_posts'];spokes=c['filter_end_spokes'];angle=c['filter_spoke_half_angle']
    descriptions={}
    for level in ['upper','lower']:
        if level=='upper':
            low=0.;high=c['upper_filter_top']-c['upper_filter_dome_depth'];top=c['upper_filter_top']
            profile=[(hole,top-stock),(center,top-stock),(ro,high-stock),(ro,high),(center,top),(hole,top)]
            f=lambda rr:top-stock if rr<=center else top-stock-(rr-center)*(top-high)/(ro-center)
            cap_profile=[(hole,f(hole)-mesh_stock),(mesh_r,f(mesh_r)-mesh_stock),(mesh_r,f(mesh_r)),(center,f(center)),(hole,f(hole))]
            mesh_inner=hole
        else:
            low=d['cover_top'];high=c['lower_filter_top'];z=d['cover_inner_center'];slope=c['cover_dish_depth']/ro
            profile=[(0,z),(ro,low),(ro,low+stock),(0,z+stock)]
            f=lambda rr:z+stock+slope*rr
            cap_profile=[(0,f(0)),(mesh_r,f(mesh_r)),(mesh_r,f(mesh_r)+mesh_stock),(0,f(0)+mesh_stock)]
            mesh_inner=0.
        end=rev_z(profile)
        for j in range(spokes):
            start=360*j/spokes+angle;endangle=360*(j+1)/spokes-angle
            end=end.cut(sector(center,ro-c['filter_rim_width'],start,endangle,-110,100))
        wall=ring(ro,inside,low,high)
        for j in range(post_count):
            start=360*j/post_count+c['filter_post_half_angle'];endangle=360*(j+1)/post_count-c['filter_post_half_angle']
            wall=wall.cut(sector(inside-1,ro+1,start,endangle,low+c['filter_rim_width'],high-c['filter_rim_width']))
        frame=end.fuse(wall);p[level+'_filter_frame']=frame;add(level+'_filter_frame',level.title()+'FilterFrame')
        p[level+'_side_screen']=side_gauze(inside,mesh_stock,low+stock/2,high-stock/2,c['screen_circumference_cells'],c['screen_height_cells'],c['screen_rib_width']);add(level+'_side_screen',level.title()+'SideScreen')
        p[level+'_end_screen'],holes=face_gauze(cap_profile,mesh_r,mesh_inner,c['screen_face_pitch'],c['screen_rib_width']);add(level+'_end_screen',level.title()+'EndScreen')
        descriptions[level]=dict(side_span=[low+stock/2,high-stock/2],end_apertures=holes,frame_estimate=dict(spokes=spokes,side_posts=post_count))
    # Two turned-up locking ears and an inner anti-rotation tongue are explicit
    # estimates of the source tab washer, not helical threads or a service pose.
    z=c['upper_filter_top'];t=c['screen_lock_stock'];af=c['screen_nut_af'];nh=c['screen_nut_height'];w=c['screen_lock_tab_width']
    p['screen_nut']=hex_z(af,z+t,z+t+nh).cut(cylinder(hole,z-1,z+t+nh+1));add('screen_nut','UpperScreenNut')
    lock=ring(af/2+t,hole,z,z+t)
    tabs=[box(sign*af/2 if sign>0 else -af/2-t,af/2+t if sign>0 else -af/2,-w/2,w/2,z,z+t+nh-.5) for sign in [-1,1]]
    key=box(c['upper_boss_radius']-.4,c['upper_boss_radius']+1,-w/3,w/3,z,z+t)
    lock=united([lock,key,*tabs]);p['screen_lock']=lock;add('screen_lock','UpperScreenNutLock')
    p['upper_body']=p['upper_body'].cut(box(c['upper_boss_radius']-.45,c['upper_boss_radius']+1.1,-w/3-.05,w/3+.05,z-.1,z+t+.1))
    d['strainers']=dict(representation='Separate open frames and coarse perforated BRep gauze; microscopic weave and actual mesh count unestablished',baskets=descriptions)
    d['missing']=['Fasteners, lock wires and mounting gasket','Case receiving revision and standard-context qualification','External connection configuration reconciliation']
