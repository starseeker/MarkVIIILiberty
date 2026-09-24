"""Source-length oil-pump body and cover bolt sets; thread envelopes estimated."""
import math
import FreeCAD as App
import Part
from engine_water_pump_parts import castle,cotter
from transmission_stud_parts import hex_x
V=App.Vector;X=V(1,0,0);Y=V(0,1,0)


def extend(c,p,occ,groups,d):
    def cyl(r,a,b):return Part.makeCylinder(r,b-a,V(a,0,0),X)
    def add(key,name,x,y,z):
        # Local shaft +X runs downwards from the head bearing face.
        occ.append(dict(key=key,name='EngineOilPump_'+name,xyz=[x,y,z],rotation=list(App.Rotation(Y,90).Q),assembly='EngineOilPumpFasteners'))
    radius=c['bolt_diameter']/2;gap=c['bolt_hole_gap'];ws=c['washer_stock'];ns=c['fastener_nut_stock'];depth=c['fastener_castle_depth'];pd=c['fastener_cotter_diameter']
    p['fastener_washer']=cyl(c['fastener_washer_radius'],0,ws).cut(cyl(radius+gap,-1,ws+1))
    p['fastener_nut']=castle(radius,c['fastener_nut_af'],ns,c['fastener_crown_radius'],depth,pd,gap)
    p['fastener_cotter'],pin_datums=cotter(pd,c['fastener_cotter_length'],c['fastener_crown_radius'])
    joints={}
    for name,centers in [('upper',d['upper_bolt_centers']),('cover',d['cover_bolt_centers'])]:
        grip=c[name+'_bolt_head_nut_span'];length=c[name+'_bolt_length'];pin=grip+ns-depth/2
        shaft=cyl(radius,0,length);shaft=shaft.cut(Part.makeCylinder(pd/2+.08,4*c['fastener_crown_radius'],V(pin,-2*c['fastener_crown_radius'],0),Y))
        key=name+'_body_bolt';p[key]=hex_x(c['fastener_head_af'],-c['fastener_head_stock'],0).fuse(shaft)
        head_z=c['upper_body_flange_stock']+ws if name=='upper' else c['lower_body_bottom']+c['bottom_flange_stock']+ws
        nut_z=head_z-grip
        if name=='upper':body_bottom=-(grip-2*ws-c['upper_body_flange_stock'])
        else:body_bottom=d['cover_top']-c['cover_stock']
        assert abs(nut_z-(body_bottom-ws))<1e-8,(name,nut_z,body_bottom)
        assert length>pin+pd/2 and pin>grip,(name,length,pin)
        for index,(x,y) in enumerate(centers,1):
            prefix=name.title()+'Joint'+str(index)
            add(key,prefix+'Bolt',x,y,head_z)
            add('fastener_washer',prefix+'HeadWasher',x,y,head_z)
            add('fastener_washer',prefix+'NutWasher',x,y,head_z-grip+ws)
            add('fastener_nut',prefix+'Nut',x,y,nut_z)
            if name!='upper' or index!=c['upper_wire_locked_bolt']:
                add('fastener_cotter',prefix+'Cotter',x,y,head_z-pin)
            if name=='cover':
                # Shallow relief at the body's outer wall retains the printed
                # joint stack and gives the washer/head a complete flat seat.
                clearance=max(c['fastener_washer_radius'],c['fastener_head_af']/math.sqrt(3))+c['fastener_head_clearance_gap']
                seat=head_z-ws;tool=Part.makeCylinder(clearance,ws+c['fastener_head_stock']+.5,V(x,y,seat),V(0,0,1))
                p['lower_body']=p['lower_body'].cut(tool)
            else:
                tool=Part.makeCylinder(radius+gap,length+2,V(x,y,head_z-length-1),V(0,0,1))
                p['lower_body']=p['lower_body'].cut(tool);p['upper_body']=p['upper_body'].cut(tool)
        joints[name]=dict(count=len(centers),head_bearing_z=head_z,nut_bearing_z=nut_z,head_to_nut_span_mm=grip,bolt_length_mm=length,cotter_station_from_head_mm=pin,centers=centers)
    d['fastener_joints']=joints;d['fastener_cotter']=pin_datums
    d['missing']=['Three source lock wires and mounting gasket/fasteners','Case receiving revision and standard-context qualification','External connection configuration reconciliation']
