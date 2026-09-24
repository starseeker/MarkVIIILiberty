"""Source-proportioned lower inside-bearing bosses for the stop mounting trial.

Only the old lower-boss region is replaced. Shaft/socket, oil connections,
upper cap, frame mounting pads and all their existing interfaces stay protected.
Long MX36 studs in the lower row and the hidden casting profile remain inferences.
"""
import FreeCAD as App
import Part
V=App.Vector


def box(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))


def plate(points,y0,y1):
    points=[V(x,y0,z) for x,z in points]
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,y1-y0,0))


def revise(c,stop,hardware,shapes,rows):
    center=V(*[rows['PortFixedBearing_inner_cap']['frame'][i] for i in [3,7,11]])
    old_nut=rows['PortFixedBearing_inner_Stud01_Nut']['frame']
    old_cotter=rows['PortFixedBearing_inner_Stud01_Cotter']['frame']
    old_stud=rows['PortFixedBearing_inner_Stud01_Stud']['frame']
    cap_seat=(hardware['MX36_length']-hardware['US_thread_length']-hardware['nut_height']
        -hardware['stud_end_projection']-stop['bracket_stock']-hardware['US_thread_recess']-c['split_half_gap'])
    z=c['lower_stud_z'];floor=z-c['lower_edge_margin'];cut_z=c['replacement_top_z']
    old=shapes['cap'];cylinders=[f.Surface for f in old.Faces if isinstance(f.Surface,Part.Cylinder)
        and abs(f.Surface.Axis.y)>.999 and abs(f.Surface.Center.x)<1e-7 and abs(f.Surface.Center.z)<1e-7]
    assert any(abs(s.Radius-c['socket_radius'])<1e-7 for s in cylinders)
    span=c['casting_half_width']
    region=box(c['replacement_rear_x'],200,-100,100,c['replacement_bottom_z'],cut_z)
    cap=old.cut(region)
    socket=Part.makeCylinder(c['socket_radius'],2*span+2,V(0,-span-1,0),V(0,1,0))
    annulus=Part.makeCylinder(c['outer_radius'],2*span,V(0,-span,0),V(0,1,0)).cut(socket)
    lower=box(-200,200,-100,100,c['replacement_bottom_z'],cut_z)
    cap_additions=[annulus.common(lower).common(box(c['split_half_gap'],200,-100,100,-300,300))]
    bracket=shapes['bracket'].cut(region)
    addition=plate([(c['lower_web_rear_x'],c['lower_web_rear_bottom_z']),
        (c['lower_web_rear_x'],c['lower_web_rear_top_z']),(-c['upper_web_join_x'],cut_z),
        (-c['split_half_gap'],cut_z),(-c['split_half_gap'],floor),
        (c['lower_web_knee_x'],floor)],-c['rear_web_stock']/2,c['rear_web_stock']/2)
    bracket_additions=[addition,annulus.common(lower).common(box(-200,-c['split_half_gap'],-100,100,-300,300))]
    tip=cap_seat+hardware['nut_height']+hardware['stud_end_projection']
    tail=tip-hardware['MX36_length']
    holes=[];boss_back=tail-c['blind_end_gap']-c['blind_end_stock']
    for index in ['01','03']:
        y=rows['PortFixedBearing_inner_Stud'+index+'_Stud']['frame'][7]-center.y
        # Two separate lower ears and neck webs, rather than a full-width block.
        # The branching and hidden rib sections are explicit casting estimates.
        cap_additions += [Part.makeCylinder(c['boss_radius'],cap_seat-c['split_half_gap'],
            V(c['split_half_gap'],y,z),V(1,0,0)),
            plate([(c['split_half_gap'],cut_z),(c['cap_upper_join_x'],cut_z),
                (cap_seat,z+c['lower_boss_height_above_axis']),(cap_seat,z),(c['split_half_gap'],z)],
                y-c['neck_width']/2,y+c['neck_width']/2)]
        bracket_additions += [Part.makeCylinder(c['boss_radius'],-c['split_half_gap']-boss_back,V(boss_back,y,z),V(1,0,0)),
            plate([(boss_back,cut_z),(-c['split_half_gap'],cut_z),(-c['split_half_gap'],z),(boss_back,z)],
                y-c['neck_width']/2,y+c['neck_width']/2)]
        holes.append(Part.makeCylinder(hardware['stud_diameter']/2+c['stud_bore_clearance'],
            cap_seat+1-tail+c['blind_end_gap'],V(tail-c['blind_end_gap'],y,z),V(1,0,0)))
    half_pitch=abs(rows['PortFixedBearing_inner_Stud01_Stud']['frame'][7]-center.y)
    bracket_additions.append(box(boss_back,boss_back+c['rear_rib_stock'],-half_pitch,half_pitch,
                                 z-c['rear_rib_half_height'],z+c['rear_rib_half_height']))
    cap=cap.multiFuse(cap_additions).cut(socket)
    bracket=bracket.multiFuse(bracket_additions).cut(socket)
    tool=Part.makeCompound(holes)
    cap=cap.cut(tool);bracket=bracket.cut(tool)
    changed={'Def_FixedBearing_inner_cap':cap,'Def_FixedBearing_inner_bracket':bracket}
    for key,s in changed.items():
        assert s.isValid() and len(s.Solids)==1 and s.Placement.isIdentity(),key
    revisions={}
    for hand in ['Port','Starboard']:
        base=rows[hand+'FixedBearing_inner_cap']['frame']
        for index in range(1,5):
            stem=hand+'FixedBearing_inner_Stud'+str(index).zfill(2)+'_'
            lower=index in [1,3];mark='MX36' if lower else 'MX10'
            old_frame=rows[stem+'Nut']['frame'];nut_x=base[3]+cap_seat if lower else old_frame[3]
            axis_z=base[11]+z if lower else old_frame[11]
            tip_x=nut_x+hardware['nut_height']+hardware['stud_end_projection']
            for suffix in ['Stud','Nut','Cotter']:
                row=dict(rows[stem+suffix]);f=list(row['frame'])
                f[3]=tip_x-hardware[mark+'_length'] if suffix=='Stud' else nut_x if suffix=='Nut' else nut_x+(old_cotter[3]-old_nut[3])
                f[11]=axis_z;row['frame']=f
                if suffix=='Stud':row['definition']='Def_TransmissionCap_'+mark
                revisions[stem+suffix]=row
        for role in ['cap','bracket']:
            name=hand+'FixedBearing_inner_'+role;revisions[name]=dict(rows[name])
    details=dict(lower_cap_seat_x_mm=cap_seat,lower_stud_z_mm=z,lower_unbracketed_stud_tail_x_mm=tail,
        mounted_coarse_thread_front_x_mm=tail+stop['bracket_stock']+hardware['US_thread_length'],
        source_count_allocation='Two MX36 lower and two MX10 upper per inside bearing; inferred allocation.',
        protected_socket_radius_mm=c['socket_radius'],replacement_region=dict(x_min=c['replacement_rear_x'],
        z_min=c['replacement_bottom_z'],z_max=cut_z),additional_lower_web_region=dict(x_min=c['lower_web_rear_x'],
        z_min=c['lower_web_rear_bottom_z'],z_max=cut_z),historical_geometry_qualified=False)
    return changed,revisions,details
