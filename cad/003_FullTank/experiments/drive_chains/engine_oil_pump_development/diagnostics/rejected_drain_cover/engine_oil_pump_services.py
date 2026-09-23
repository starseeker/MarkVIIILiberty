"""Oil-pump passages, pressure relief and bottom closure; estimated routing."""
import math
import FreeCAD as App
import Part
from engine_oil_pump_parts import V,X,Y,Z,cylinder,ring,united,moved,rod,channel,hex_z,rev_z
from engine_crossmember_parts import box

def extend(c,p,occ,groups,d):
    def add(key,name,xyz=(0,0,0),rotation=None,group='EngineOilPumpRelief'):
        occ.append(dict(key=key,name='EngineOilPump_'+name,xyz=list(xyz),rotation=list((rotation or App.Rotation()).Q),assembly=group))
    lo,up=p['lower_body'],p['upper_body'];floor=d['gear_cavity_floor'];roof=d['gear_cavity_roof'];space=d['gear_center_spacing'];r=c['port_radius'];stock=r+c['passage_wall']
    # A continuous ceiling seats the lower strainer's open rim, preventing an
    # unfiltered route around its upper edge. The upper gear case remains separate.
    lo=lo.fuse(cylinder(c['lower_body_radius']-c['lower_body_wall']+.5,c['lower_filter_top'],floor-c['body_gear_bottom_stock']+.5))
    x,y=c['relief_x'],c['relief_y'];seat_top=floor-2.;seat_bottom=seat_top-c['relief_seat_stock'];cage_top=seat_bottom-c['thread_gap'];valve_bottom=seat_bottom-c['relief_head_stock']
    cage_bottom=valve_bottom-c['relief_spring_length']-c['relief_shim_stock']-c['relief_cage_floor_stock']
    lo=lo.fuse(cylinder(c['relief_radius']+c['relief_cage_wall']+1,cage_top-8,seat_top+1,x,y))
    # Source function graph: lower filtered supply -> pressure pair -> manifold
    # and relief; front-sump return -> one upper pair; upper strainer -> the other;
    # both upper deliveries -> common return. Routes avoid the central shaft.
    pressure=[(12,-space/2,-9),(44,-space/2,-9),(44,-64,-9),(-60,-64,-9),(c['pressure_port_x'],c['pressure_port_y'],-9),(c['pressure_port_x'],c['pressure_port_y'],1)]
    front=[(c['return_inlet_port_x'],c['return_inlet_port_y'],1),(c['return_inlet_port_x'],c['return_inlet_port_y'],-22),(-40,28,-22),(30,28,-22),(30,space/2,-22),(30,space/2,14),(13,space/2,14)]
    supply=[(-30,-space/2,-40),(-30,-space/2,-9),(-13,-space/2,-9)]
    outlet=[(-13,space/2,14),(-30,space/2,14),(-30,space/2,-9),(-38,40,-9),(-38,c['lower_body_radius']+4,-9)]
    bypass=[(12,-space/2,-9),(x,y,-9),(x,y,seat_top+1)]
    level=d['upper_body_top']+c['crossover_lift'];cross=[(13,-space/2,14),(13,-space/2,level),(30,-space/2,level),(30,space/2,level),(-13,space/2,level),(-13,space/2,14)]
    paths=dict(pressure=pressure,front_sump=front,filtered_supply=supply,common_return=outlet,relief=bypass,crossover=cross)
    for name in ['pressure','front_sump','filtered_supply','common_return','relief']:
        # Machining tools extend 1 mm beyond the mounting face; casting stock
        # stops on that face. Otherwise two detached annuli become false parts
        # of the upper body at the crankcase manifold ports.
        stock_points=list(paths[name])
        if name=='pressure':stock_points[-1]=(c['pressure_port_x'],c['pressure_port_y'],0)
        if name=='front_sump':stock_points[0]=(c['return_inlet_port_x'],c['return_inlet_port_y'],0)
        outer=channel(stock_points,stock);lo=lo.fuse(outer.common(box(-150,150,-150,150,-100,0)))
        if name in ['front_sump','common_return']:
            up=up.fuse(outer.common(box(-150,150,-150,150,0,100)))
    # Roof cross-over with two machining closures, shown as a raised cast passage.
    up=up.fuse(channel(cross,stock));accesses=[[(13,-space/2,level),(45,-space/2,level)],[(-13,space/2,level),(-45,space/2,level)]]
    for points in accesses:up=up.fuse(channel(points,stock))
    for points in paths.values():
        tool=channel(points,r);lo=lo.cut(tool);up=up.cut(tool)
    for points in accesses:up=up.cut(channel(points,r))
    # Rear-sump filtered inlet through the upper housing side; it opens inside
    # the upper strainer and stops at the appropriate inter-gear pocket.
    rear=[(-44,-space/2,14),(-13,-space/2,14)];up=up.cut(channel(rear,r));paths['rear_sump']=rear
    # Supply connection into the exterior of the lower strainer.
    inlet=[(0,-c['lower_body_radius']-5,-44),(0,-c['lower_body_radius']+c['lower_body_wall']+2,-44)]
    lo=lo.fuse(channel(inlet,10.));lo=lo.cut(channel(inlet,7.));paths['tank_supply']=inlet
    # Keep the known chamber envelopes clear after casting additions.
    tip_lower=d['gear_profiles']['lower']['tip_radius_mm'];tip_upper=d['gear_profiles']['upper']['tip_radius_mm'];clearance=c['gear_diametrical_clearance']/2
    lo=lo.cut(united([cylinder(tip_lower+clearance,floor,1,0,yy) for yy in [-space,0]]))
    up=up.cut(united([cylinder(tip_upper+clearance,c['partition_stock'],roof,0,yy) for yy in [-space,0,space]]))
    up=up.cut(united([cylinder(tip_lower+3,0,c['partition_stock'],0,yy) for yy in [-space,0]]))
    lo=lo.cut(cylinder(c['lower_bush_radius']+c['bush_cast_gap'],c['lower_bush_bottom']-.1,c['lower_bush_top']))
    lo=lo.cut(cylinder(c['shaft_core_radius']+.1,c['lower_bush_bottom']-2,1))
    up=up.cut(cylinder(c['upper_bush_radius']+c['bush_cast_gap'],c['upper_bush_bottom'],c['upper_bush_top']+1))
    # Source mushroom valve, seat and threaded cage with drain windows.
    lo=lo.cut(cylinder(c['relief_radius']+c['thread_gap'],cage_bottom-1,seat_bottom,x,y))
    lo=lo.cut(cylinder(c['relief_seat_radius']+c['thread_gap'],seat_bottom,seat_top,x,y))
    lo=lo.cut(cylinder(c['relief_throat_radius'],seat_top-.1,-8,x,y))
    p['relief_seat']=ring(c['relief_seat_radius'],c['relief_throat_radius'],seat_bottom,seat_top)
    add('relief_seat','ReliefSeat',(x,y,0))
    p['relief_valve']=cylinder(c['relief_head_radius'],valve_bottom,seat_bottom).fuse(cylinder(c['relief_stem_radius'],valve_bottom-c['relief_valve_stem_length'],valve_bottom+.1))
    add('relief_valve','ReliefValve',(x,y,0))
    cage=ring(c['relief_radius'],c['relief_radius']-c['relief_cage_wall'],cage_bottom,cage_top)
    cage=cage.fuse(hex_z(c['relief_cage_hex_af'],cage_bottom,cage_bottom+c['relief_cage_floor_stock'])).cut(cylinder(c['relief_stem_radius']+.1,cage_bottom-1,cage_bottom+c['relief_cage_floor_stock']+.1))
    # Broad drain windows below the threaded portion leave three structural legs.
    for a in [0,120,240]:cage=cage.cut(moved(box(0,c['relief_radius']+2,-5,5,cage_bottom+4,cage_top-8),angle=a))
    p['relief_cage']=cage;add('relief_cage','ReliefCage',(x,y,0))
    shim_bottom=cage_bottom+c['relief_cage_floor_stock'];p['relief_shim']=ring(8.,c['relief_stem_radius']+.15,shim_bottom,shim_bottom+c['relief_shim_stock']);add('relief_shim','ReliefShim',(x,y,0))
    spring_low=shim_bottom+c['relief_shim_stock'];height=valve_bottom-spring_low;assert abs(height-c['relief_spring_length'])<1e-6,(height,c['relief_spring_length'])
    wr=c['relief_spring_wire_radius'];pitch=(height-2*wr)/c['relief_spring_turns'];helix=Part.makeHelix(pitch,height-2*wr+pitch/2,c['relief_spring_radius']);path=Part.Wire(helix.Edges)
    section=Part.Wire([Part.makeCircle(wr,V(c['relief_spring_radius'],0,0),V(0,c['relief_spring_radius'],pitch/(2*math.pi)))])
    spring=path.makePipeShell([section],True,True);spring.translate(V(0,0,wr-pitch/4));spring=spring.common(cylinder(c['relief_spring_radius']+wr+1,0,height));p['relief_spring']=spring;add('relief_spring','ReliefSpring',(x,y,spring_low))
    # Machining plugs close the two roof passages. Cylindrical thread envelopes.
    p['upper_plug']=cylinder(c['upper_plug_radius'],0,c['upper_plug_length'])
    for i,(sign,yy) in enumerate([(1,-space/2),(-1,space/2)],1):
        start=sign*(45-c['upper_plug_length']);tool=rod((start,yy,level),(sign*46,yy,level),c['upper_plug_radius']+c['upper_plug_gap']);up=up.cut(tool)
        add('upper_plug','UpperPassagePlug'+str(i),(start,yy,level),App.Rotation(Z,X*sign),groups[1])
    # A low side access plug is separate from the cover drain.
    p['body_plug']=cylinder(c['body_plug_radius'],0,c['body_plug_length']);plug_y=-(c['lower_body_radius']+2);plug_z=-20.;lo=lo.fuse(rod((0,plug_y,plug_z),(0,plug_y+c['body_plug_length']+3,plug_z),c['body_plug_radius']+3))
    lo=lo.cut(rod((0,plug_y-1,plug_z),(0,plug_y+c['body_plug_length']+4,plug_z),c['body_plug_radius']+c['thread_gap']))
    add('body_plug','LowerBodyPlug',(0,plug_y,plug_z),App.Rotation(Z,Y),groups[0])
    top=c['lower_body_bottom']-c['cover_gasket_stock'];fr=c['mount_flange_radius'];inner=c['filter_outer_radius'];dish=c['cover_dish_depth'];thick=c['cover_stock']
    cover=rev_z([(0,top-dish-thick),(inner,top-thick),(fr,top-thick),(fr,top),(inner,top),(0,top-dish)])
    dx=c['drain_x'];seat_z=top-dish-thick-c['drain_boss_drop'];cover=cover.fuse(cylinder(c['drain_diameter']/2+6,seat_z,top,dx,0))
    cavity=rev_z([(0,top-dish),(inner,top),(fr,top),(fr,top+5),(0,top+5)]);cover=cover.cut(cavity)
    cover=cover.cut(cylinder(c['drain_diameter']/2+c['thread_gap'],seat_z-1,top+1,dx,0))
    gasket=ring(fr,c['lower_body_radius']-c['lower_body_wall'],top,c['lower_body_bottom'])
    centers=[]
    for i in range(c['mount_count']):
        a=2*math.pi*i/c['mount_count'];xx,yy=c['mount_stud_radius']*math.cos(a),c['mount_stud_radius']*math.sin(a)
        centers.append((xx,yy));tool=cylinder(c['mount_hole_radius'],top-thick-1,c['lower_body_bottom']+c['bottom_flange_stock']+1,xx,yy);cover=cover.cut(tool);gasket=gasket.cut(tool);lo=lo.cut(tool)
    p['cover']=cover;p['cover_gasket']=gasket;add('cover','BottomCover',group=groups[0]);add('cover_gasket','CoverGasket',group=groups[0])
    p['drain_plug']=hex_z(c['drain_head_af'],-c['drain_head_stock'],0).fuse(cylinder(c['drain_diameter']/2,0,c['drain_thread_length']))
    p['drain_gasket']=ring(c['drain_diameter']/2+4,c['drain_diameter']/2+c['thread_gap'],0,c['drain_gasket_stock'])
    add('drain_plug','DrainPlug',(dx,0,seat_z-c['drain_gasket_stock']),group=groups[0]);add('drain_gasket','DrainGasket',(dx,0,seat_z-c['drain_gasket_stock']),group=groups[0])
    p['lower_body']=lo;p['upper_body']=up
    d.update(passages=paths,cover_bolt_centers=centers,cover_top=top,cover_inner_center=top-dish,drain_seat=[dx,0,seat_z],relief_seat=[x,y,seat_top],relief_spring_span=[spring_low,valve_bottom],relief_cage_span=[cage_bottom,cage_top],crossover_height=level)
    d['missing']=['Strainer frames and gauze','Upper screen nut and lock','Fasteners, lock wires and mounting gasket','Case receiving revision and standard-context qualification','External connection configuration reconciliation']
