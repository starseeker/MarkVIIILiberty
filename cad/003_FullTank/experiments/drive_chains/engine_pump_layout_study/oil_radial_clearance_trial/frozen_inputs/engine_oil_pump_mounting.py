"""HB196/199 pump-to-case joint, with LIB28's nine-circle-plus-nose pattern.

Stud length and case-to-nut span follow HB196. SNL237's longer stud is retained
as a source alternative; transferring its thread-end lengths is an explicit
inference. The receiver casting is qualified separately, not supplied here.
"""
import math
import FreeCAD as App
import Part
from engine_oil_pump_parts import V,X,Y,Z,cylinder,mount_outline


def extend(c,p,occ,groups,d):
    group='EngineOilPumpMounting';groups.append(group)
    face=c['mount_gasket_stock'];flange=c['mount_flange_stock'];washer=c['washer_stock']
    span=c['mount_case_nut_span'];nut=c['fastener_nut_stock'];depth=c['fastener_castle_depth']
    assert abs(face+flange+washer-span)<1e-8
    bearing=face-span;pin=span+nut-depth/2
    embed=c['mount_stud_embed'];length=c['mount_stud_length'];end=length-embed
    assert span>=end-c['mount_stud_outer_thread']-1e-8
    assert span+nut<end and pin+c['fastener_cotter_diameter']/2<end
    radius=c['bolt_diameter']/2
    shaft=Part.makeCylinder(radius,length,V(-embed,0,0),X)
    shaft=shaft.cut(Part.makeCylinder(c['fastener_cotter_diameter']/2+.08,20,V(pin,-10,0),Y))
    p['mount_stud']=shaft
    gasket=mount_outline(c,0,face).cut(cylinder(c['mount_opening_radius'],-1,face+1))
    for x,y in [(c['pressure_port_x'],c['pressure_port_y']),(c['return_inlet_port_x'],c['return_inlet_port_y'])]:
        gasket=gasket.cut(cylinder(c['port_radius']+c['mount_gasket_port_gap'],-1,face+1,x,y))
    centers=[];low=-flange-washer-nut-c['mount_nut_seat_gap']
    relief=max(c['fastener_washer_radius'],c['fastener_nut_af']/math.sqrt(3))+c['mount_nut_seat_gap']
    for index in range(c['mount_count']):
        angle=360*index/c['mount_count'];theta=math.radians(angle)
        x,y=c['mount_stud_radius']*math.cos(theta),c['mount_stud_radius']*math.sin(theta)
        if index==c['mount_count']//2:x,y=c['mount_nose_stud_x'],0.
        centers.append([x,y]);hole=cylinder(c['mount_hole_radius'],low-1,face+1,x,y)
        p['lower_body']=p['lower_body'].cut(hole);gasket=gasket.cut(hole)
        # Nut/washer relief at the outside of the body; cotter axis is tangent
        # to the bolt circle, keeping both legs outside the cylindrical wall.
        p['lower_body']=p['lower_body'].cut(cylinder(relief,low,-flange,x,y))
        rotation=App.Rotation(Z,angle).multiply(App.Rotation(Y,90))
        for key,suffix,z,source in [('mount_stud','Stud',face,'HB:nomenclature:196:052'),
                ('fastener_washer','Washer',-flange,'HB:nomenclature:199:003'),
                ('fastener_nut','Nut',bearing,'HB:nomenclature:199:015'),
                ('fastener_cotter','Cotter',face-pin,'HB:nomenclature:199:005')]:
            occ.append(dict(key=key,name='EngineOilPump_MountJoint'+str(index+1)+suffix,
                xyz=[x,y,z],rotation=list(rotation.Q),assembly=group,source_records=[source]))
    p['mount_gasket']=gasket
    occ.append(dict(key='mount_gasket',name='EngineOilPump_MountGasket',xyz=[0,0,0],rotation=list(App.Rotation().Q),assembly=group,source_records=['HB:nomenclature:199:004']))
    d['mounting']=dict(centers=centers,case_face_z=face,pump_face_z=0.,nut_bearing_z=bearing,
        stud_span_z=[face-end,face+embed],case_engagement_mm=embed,
        inner_thread_span_z=[face,face+embed],outer_thread_span_z=[face-end,face-end+c['mount_stud_outer_thread']],
        cotter_z=face-pin,head_to_nut_span_mm=span,flange_stock_mm=flange,
        nut_seat_relief_radius_mm=relief,nut_seat_relief_low_z=low,case_opening_radius_mm=c['mount_opening_radius'],
        pattern='Nine equally spaced circular stations plus the forward station moved to the nose; LIB28',
        selected_stud='HB196 132: 1/4-28 x 1-7/16in; SNL237 1-9/16in retained as alternative',
        thread_end_lengths='Transferred from SNL237; compatibility inference for shorter HB stock, not printed HB end lengths',
        case_fit_qualified=False)
    d['missing']=['Two remaining source lock wires','Receiving case, stud engagement and standard-context qualification',
        'External connections and source-profile/port refinement']
