"""Source-owned crankshaft closures in the inherited engine-local frame.

Thread surfaces are nominal envelopes. Cap profiles, recess distribution and
unprinted hardware dimensions are explicit reconstruction assumptions.
"""
import math
import FreeCAD as App
import Part
from engine_crankshaft_parts import cyl, ring
from engine_crossmember_parts import box
from transmission_stud_parts import hex_x
from transmission_input_installation_parts import formed_pin

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def placed(shape, base=V(), rotation=None):
    result = shape.copy()
    result.Placement = App.Placement(base, rotation or App.Rotation()).multiply(result.Placement)
    return result


def parts(c, parent, original, progress=None):
    pc, cc, pd = parent['controls'], parent['case_controls'], parent['datums']
    shaft = original.copy()
    shapes, occurrences, assemblies, pairs, edit_zones = {}, [], [], [], []

    def audit(name, shape):
        assert shape.isValid() and len(shape.Solids) == 1, (name, shape.isValid(), len(shape.Solids))
        if progress:
            progress(name, shape)

    def add(key, name, group, xyz=V(), rotation=None):
        occurrences.append(dict(key=key, name='ShaftClosure_' + name, assembly=group,
                                xyz=list(xyz), rotation=list((rotation or App.Rotation()).Q)))

    radius = c['stud_diameter']/2
    large = c['large_gasket_stock']
    cap_stock = c['cap_stock']
    small = c['small_gasket_stock']
    gap = c['radial_fit_gap']
    # Canonical cap points inward along +X; X=0 is the shaft gasket seat.
    for name, bore in [('main', pc['main_hollow_radius']), ('pin', pc['pin_hollow_radius']),
                       ('gear', pc['main_hollow_radius'])]:
        ro = c[name + '_cap_radius']
        flange = cyl(ro, -large-cap_stock, -large)
        lip = cyl(bore-gap, -large, c['cap_lip'])
        shapes[name + '_cap'] = flange.fuse(lip).cut(cyl(radius+c['stud_bore_gap'], -large-cap_stock-1, c['cap_lip']+1))
        shapes[name + '_gasket'] = ring(ro, bore, -large, 0)
    shapes['small_gasket'] = ring(c['small_gasket_radius'], radius+c['stud_bore_gap'], 0, small)
    shapes['washer'] = ring(c['washer_radius'], radius+c['stud_bore_gap'], 0, c['washer_stock'])
    shapes['plain_nut'] = hex_x(c['nut_af'], 0, c['plain_nut_stock']).cut(cyl(radius+gap, -1, c['plain_nut_stock']+1))
    height = c['castle_nut_stock']; depth = c['castle_slot_depth']
    nut = hex_x(c['nut_af'], 0, height-depth).fuse(cyl(c['castle_radius'], height-depth, height))
    nut = nut.cut(cyl(radius+gap, -1, height+1))
    for angle in [0, 60, 120]:
        width = c['cotter_diameter'] + c['castle_slot_gap']
        tool = box(height-depth, height+1, -20, 20, -width/2, width/2)
        tool.rotate(V(), X, angle)
        nut = nut.cut(tool)
    shapes['castle_nut'] = nut
    pincontrols = dict(cotter_center_spacing=c['cotter_diameter']*.52, cotter_diameter=c['cotter_diameter'],
                       crown_radius=c['castle_radius'], cotter_head_gap=.15, cotter_exit_gap=.15,
                       cotter_bend_radius=.8, cotter_bend_angle=35, cotter_length=c['cotter_length'],
                       cotter_eye_radius=1.6, cotter_eye_rise=.7, cotter_eye_join_overlap=.02)
    shapes['cotter'], cotter = formed_pin(pincontrols)
    # Every source stud length constrains the complete cap/fastener stack.
    stack = 2*(large+cap_stock+small) + c['plain_nut_stock'] + c['washer_stock'] + height + 2*c['stud_end_exposure']
    journal_width = pc['main_bearing_short_length'] + pc['journal_endplay'] + 2*pc['web_stock']
    main_recess = (journal_width+stack-c['main_stud_length'])/2
    assert main_recess >= 0, 'Estimated cap stack cannot fit the source main stud length'
    flip = App.Rotation(Z, 180)

    def pair(name, family, left, right, center, roll=0, right_cap=None):
        nonlocal shaft
        right_cap = right_cap or family
        if family == 'pin':
            length = c['pin_stud_length']; r_recess = c['pin_rear_recess']
            l_recess = right-left+stack-length-r_recess
        elif family == 'main':
            length = c['main_stud_length']; l_recess = r_recess = main_recess
        else:
            l_recess, r_recess = main_recess, c['gear_recess']
            length = right-left-l_recess-r_recess+stack
        assert min(l_recess, r_recess) >= 0
        left_seat, right_seat = left+l_recess, right-r_recess
        orientation = App.Rotation(X, roll)
        group = 'EngineShaftClosure_' + name
        assemblies.append(dict(name=group, xyz=list(center), rotation=list(orientation.Q), family=family))
        left_cap = 'main' if family == 'gear' else family
        for side, seat, edge, kind, rot in [('Left', left_seat, left, left_cap, App.Rotation()),
                                           ('Right', right_seat, right, right_cap, flip)]:
            add(kind+'_cap', name+'_'+side+'Cap', group, V(seat,0,0), rot)
            add(kind+'_gasket', name+'_'+side+'Gasket', group, V(seat,0,0), rot)
            ro = c[kind+'_cap_radius']+gap
            tool = cyl(ro, edge-1, seat) if side == 'Left' else cyl(ro, seat, edge+1)
            tool = placed(tool, center, orientation)
            shaft = shaft.cut(tool); edit_zones.append(tool)
        face_left, face_right = left_seat-large-cap_stock, right_seat+large+cap_stock
        plain_start = face_left-small-c['plain_nut_stock']
        castle_start = face_right+small+c['washer_stock']
        start = plain_start-c['stud_end_exposure']
        end = start+length
        assert abs(end-(castle_start+height+c['stud_end_exposure'])) < 1e-7
        key = family+'_stud'
        cross = length-c['stud_end_exposure']-depth/2
        if key not in shapes:
            stud = cyl(radius, 0, length)
            stud = stud.cut(Part.makeCylinder(c['cotter_diameter']/2+.08, 2*radius+2, V(cross,-radius-1,0),Y))
            shapes[key] = stud
        add(key, name+'_Stud', group, V(start,0,0))
        add('small_gasket', name+'_LeftSeal', group, V(face_left-small,0,0))
        add('small_gasket', name+'_RightSeal', group, V(face_right,0,0))
        add('plain_nut', name+'_PlainNut', group, V(plain_start,0,0))
        add('washer', name+'_Washer', group, V(face_right+small,0,0))
        add('castle_nut', name+'_CastleNut', group, V(castle_start,0,0))
        add('cotter', name+'_Cotter', group, V(start+cross,0,0))
        pairs.append(dict(name=name, family=family, group=group, center=list(center), roll_deg=roll,
                          outer_faces=[left,right], seats=[left_seat,right_seat], recesses=[l_recess,r_recess],
                          stud_span=[start,end], source_stud_length=family!='gear', cotter_x=start+cross,
                          coarse_thread_span=[start,start+c['coarse_thread_length']],
                          fine_thread_span=[end-c['fine_thread_length'],end]))

    rows = pd['main_rows']; play = pc['journal_endplay']/2; web = pc['web_stock']
    for i in range(1, 6):
        pair('Main%d'%(i+1), 'main', rows[i]-pc['main_bearing_short_length']/2-play-web,
             rows[i]+pc['main_bearing_short_length']/2+play+web, V())
    for station in pd['crankpin_stations']:
        left, right = station['running_span']
        _, y, z = station['center']
        pair('Pin%d'%station['cylinder'], 'pin', left-web, right+web, V(0,y,z), -station['phase_deg'])
    pair('Gear', 'gear', rows[-1]-pc['main_bearing_short_length']/2-play-web,
         pd['gear_flange_span'][1], V(), right_cap='gear')
    audit('cap counterbores', shaft)

    # A blind inner nose termination accounts for the source's eleven ordinary
    # main caps, rather than introducing an unsupported twelfth cap.
    nose_inner_end = pd['crankpin_stations'][0]['running_span'][0]
    blind_start = nose_inner_end-c['nose_blind_stock']
    fill = cyl(pc['main_hollow_radius']+.1, blind_start, nose_inner_end)
    shaft = shaft.fuse(fill); edit_zones.append(fill)
    nose_tip = pd['taper']['rear']-pc['output_thread_length']
    transition = c['nose_bore_transition_start']; transition_end=transition+c['nose_bore_transition_length']
    fill = cyl(pc['main_hollow_radius']+.1, nose_tip, transition_end)
    shaft = shaft.fuse(fill); edit_zones.append(fill)
    shaft = shaft.cut(cyl(c['nose_bore_radius'], nose_tip-1, transition))
    shaft = shaft.cut(Part.makeCone(c['nose_bore_radius'], pc['main_hollow_radius'], transition_end-transition, V(transition,0,0), X))
    # Reopen the source cotter cross-hole and the blind retaining-screw receiver
    # where new internal stock has been added. External taper/key seats stay put.
    cp = pd['output_cotter_x']
    shaft = shaft.cut(Part.makeCylinder(pc['output_cotter_diameter']/2+.1, 2*pc['output_thread_radius']+2, V(cp,-pc['output_thread_radius']-1,0),Y))
    normal=V(*pd['key_screw_normal']);head=V(*pd['key_center'])
    shaft=shaft.cut(Part.makeCylinder(pc['key_screw_diameter']/2+.05, pc['key_screw_length']+.2,
                                    head-normal*(pc['key_screw_length']+.1),normal))
    nose_plug_start = cp+pc['output_cotter_diameter']/2+.1+c['nose_plug_after_cotter']
    shapes['nose_plug'] = cyl(c['nose_bore_radius'], 0, c['nose_plug_stock'])
    add('nose_plug','NosePlug','EngineShaftClosures',V(nose_plug_start,0,0))

    # The drilled web route needs an external machining entry. Close each entry
    # with one separately owned small plug; keep the inward oil transfer open.
    small_plug = cyl(c['small_plug_radius'], 0, c['small_plug_length'])
    small_plug = small_plug.cut(box(-1, 1, -c['small_plug_radius']-1,c['small_plug_radius']+1,-.6,.6))
    shapes['oil_plug'] = small_plug
    oil_entries=[]
    for i, passage in enumerate(p for p in pd['oil_passages'] if p['kind']=='rear_web'):
        start,end=V(*passage['start']),V(*passage['end']);axis=end-start;axis.normalize()
        reach=pc['stroke']/2+pc['web_pin_radius']
        access=Part.makeCylinder(pc['oil_drill_radius'],reach+1,start,axis)
        shaft=shaft.cut(access);edit_zones.append(access)
        face=start+axis*(reach-c['small_plug_recess'])
        receiver=Part.makeCylinder(c['small_plug_radius']+gap,c['small_plug_length']+c['small_plug_recess']+1,
                                   face+axis*(c['small_plug_recess']+1),-axis)
        shaft=shaft.cut(receiver);edit_zones.append(receiver)
        rotation=App.Rotation(X,-axis)
        add('oil_plug','OilPlug%d'%(6-i),'EngineShaftClosures',face,rotation)
        oil_entries.append(dict(cylinder=6-i,start=list(start),axis=list(axis),face=list(face),length=c['small_plug_length']))
    try:
        refined=shaft.copy().removeSplitter()
        if refined.isValid() and len(refined.Solids)==1:shaft=refined
    except Part.OCCError:
        pass
    shapes['shaft']=shaft
    for name, shape in shapes.items():audit(name,shape)
    assert len(occurrences)==139
    return shapes, occurrences, assemblies, dict(pairs=pairs, main_recess=main_recess, hardware_axial_stack=stack,
        nose_blind_span=[blind_start,nose_inner_end], nose_plug_span=[nose_plug_start,nose_plug_start+c['nose_plug_stock']],
        nose_transition_span=[transition,transition_end], oil_entries=oil_entries, cotter=cotter,
        fixed_estimates=dict(cotter_controls=pincontrols, small_plug_slot_width=1.2,small_plug_slot_depth=1.,cotter_hole_radial_gap=.08)), edit_zones
