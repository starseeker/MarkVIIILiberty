"""Independent saved-shape witnesses for the HB196/199 mounting joint."""
import math
import FreeCAD as App
import Part
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)


def check_mounting(doc,r,defs,shapes,passages,check):
    c,d=r['controls'],r['datums'];m=d['mounting'];group=doc.getObject('EngineOilPumpMounting')
    rows=[o for o in r['occurrences'] if o['assembly']==group.Name]
    expected={'mount_stud':10,'mount_gasket':1,'fastener_washer':10,'fastener_nut':10,'fastener_cotter':10}
    for key,count in expected.items():
        actual=sum(row['key']==key for row in rows)
        check('mount_inventory_'+key,actual==count,actual=actual,expected=count)
    check('mount_source_identities',doc.Def_mount_stud.SourcePartMark=='132' and doc.Def_mount_gasket.SourcePartMark=='8348')
    stud=defs['mount_stud'];gasket=shapes['EngineOilPump_MountGasket'];body=defs['lower_body']
    check('HB196_actual_stud_stock_length',abs(stud.BoundBox.XLength-1.4375*25.4)<1e-7,actual_mm=stud.BoundBox.XLength)
    check('HB196_actual_stud_diameter',any(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-.125*25.4)<1e-8 for f in stud.Faces))
    face=gasket.BoundBox.ZMax;positions=[]
    for i in range(1,11):
        prefix='EngineOilPump_MountJoint'+str(i);slink=doc.getObject(prefix+'Stud');nlink=doc.getObject(prefix+'Nut');wlink=doc.getObject(prefix+'Washer');clink=doc.getObject(prefix+'Cotter')
        base=slink.LinkPlacement.Base;positions.append([base.x,base.y]);nut_z=nlink.LinkPlacement.Base.z
        check('HB196_mount_joint_span_'+str(i),abs(face-nut_z-.4375*25.4)<1e-8,actual_mm=face-nut_z)
        washer=shapes[prefix+'Washer'];nut=shapes[prefix+'Nut'];actual=shapes[prefix+'Stud']
        check('mount_washer_nut_seating_'+str(i),abs(washer.BoundBox.ZMin-nut.BoundBox.ZMax)<1e-7)
        check('mount_source_bindings_'+str(i),slink.SourceRecords==['HB:nomenclature:196:052'] and wlink.SourceRecords==['HB:nomenclature:199:003'] and nlink.SourceRecords==['HB:nomenclature:199:015'] and clink.SourceRecords==['HB:nomenclature:199:005'])
        low=actual.BoundBox.ZMin;thread_high=low+c['mount_stud_outer_thread']
        check('mount_selected_nominal_thread_engagement_'+str(i),nut.BoundBox.ZMin>low and nut.BoundBox.ZMax<=thread_high+1e-7 and abs(actual.BoundBox.ZMax-face-c['mount_stud_embed'])<1e-7,outer_thread_span_z=[low,thread_high],nut_span_z=[nut.BoundBox.ZMin,nut.BoundBox.ZMax],case_engagement_mm=actual.BoundBox.ZMax-face,thread_ends_are_transferred_inference=True)
        radial=V(base.x,base.y,0);radial.normalize();tangent=clink.LinkPlacement.Rotation.multVec(Y)
        check('mount_cotter_axis_tangent_'+str(i),abs(radial.dot(tangent))<1e-8)
        # Entire washer footprint must bear on real flange stock, including nose.
        z=washer.BoundBox.ZMax
        footprint=Part.makeCylinder(c['fastener_washer_radius'],.05,V(base.x,base.y,z)).cut(Part.makeCylinder(c['mount_hole_radius'],.07,V(base.x,base.y,z-.01)))
        missing=abs(footprint.cut(body).Volume)
        check('mount_washer_full_bearing_land_'+str(i),missing<1e-5,missing_mm3=missing)
        hole=Part.makeCylinder(.03125*25.4,20,V(base.x,base.y,clink.LinkPlacement.Base.z)-tangent*10,tangent)
        check('mount_stud_cotter_bore_'+str(i),abs(hole.common(actual).Volume)<1e-5)
        # Nine local body-wall sectors, away from the two intentional ports.
        if i!=6:
            outer=c['lower_body_radius']-c['lower_body_wall']+3.;inner=outer-2.5
            low_z=m['nut_seat_relief_low_z'];height=-c['mount_flange_stock']-low_z
            wall=Part.makeCylinder(outer,height,V(0,0,low_z),Z,10).cut(Part.makeCylinder(inner,height+2,V(0,0,low_z-1)))
            wall.rotate(V(),Z,math.degrees(math.atan2(base.y,base.x))-5)
            missing=abs(wall.cut(body).Volume)
            check('mount_nut_seat_retains_local_wall_'+str(i),missing<1e-5,missing_mm3=missing,witness_radial_stock_mm=2.5)
    circular=[p for p in positions if abs(math.hypot(*p)-c['mount_stud_radius'])<1e-7]
    nose=[p for p in positions if abs(p[0]-c['mount_nose_stud_x'])<1e-7 and abs(p[1])<1e-7]
    check('LIB28_nine_circle_one_nose',len(circular)==9 and len(nose)==1,positions=positions)
    for name,x,y in [('pressure',c['pressure_port_x'],c['pressure_port_y']),('front_sump',c['return_inlet_port_x'],c['return_inlet_port_y'])]:
        gauge=Part.makeCylinder(c['port_radius'],face+2,V(x,y,-1),Z)
        overlap=abs(gasket.common(gauge).Volume)
        check('HB110_gasket_leaves_'+name+'_port_open',overlap<1e-5,material_mm3=overlap)
    opening=Part.makeCylinder(c['mount_opening_radius']-.001,face+2,V(0,0,-1),Z)
    check('mount_gasket_central_opening',abs(opening.common(gasket).Volume)<1e-5)
    check('mount_nose_is_rounded',any(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-c['mount_nose_tip_radius'])<1e-7 for f in gasket.Faces))
    check('receiver_qualification_remains_explicit',m['case_fit_qualified'] is False)
