"""Partial channel/diaphragm frame and frame-constrained bearing brackets."""
import FreeCAD as App
import Part

from transmission_support_parts import box


def xy_plate(points,z0,z1):
    vertices=[App.Vector(x,y,z0) for x,y in points]
    return Part.Face(Part.makePolygon(vertices+vertices[:1])).extrude(App.Vector(0,0,z1-z0))


def xz_plate(points,y0,y1):
    vertices=[App.Vector(x,y0,z) for x,z in points]
    return Part.Face(Part.makePolygon(vertices+vertices[:1])).extrude(App.Vector(0,y1-y0,0))


def frame_parts(c,inner_y,outer_y):
    depth=c['channel_depth'];height=c['channel_height'];stock=c['channel_stock'];half=c['channel_half_span']
    profile=[(-depth,0),(0,0),(0,height),(-stock,height),(-stock,stock),
             (-depth+stock,stock),(-depth+stock,height),(-depth,height)]
    shapes={'top_channel':xz_plate(profile,-half,half),
            'bottom_channel':xz_plate([(x,-z) for x,z in profile],-half,half)}
    rear=-depth+stock;front=-stock;t=c['angle_stock'];g=c['gusset_stock']
    low=c['bottom_web_z']+g;high=c['top_web_z']-g
    for side,sign in [('left',1),('right',-1)]:
        # Both legs occupy the channel interior; mirror transverse orientation.
        points=[(rear,0),(rear+c['angle_leg_x'],0),(rear+c['angle_leg_x'],-sign*t),
                (rear+t,-sign*t),(rear+t,-sign*c['angle_leg_y']),(rear,-sign*c['angle_leg_y'])]
        shapes['inner_angle_'+side]=xy_plate(points,0,high-low)
    shapes['outer_angle']=shapes['inner_angle_left'].copy()
    diaphragm_half=inner_y-c['angle_leg_y']
    shapes['middle_diaphragm']=box(rear,rear+c['diaphragm_stock'],-diaphragm_half,diaphragm_half,0,high-low)
    for role in ['inner','outer']:
        for side,sign in [('left',1),('right',-1)]:
            shapes[role+'_gusset_'+side]=xy_plate([(rear,0),(front,0),(rear,-sign*c['gusset_width'])],-g,0)
    placements={
        'TopChannel':('top_channel',App.Placement(App.Vector(c['frame_front_x'],0,c['top_web_z']),App.Rotation())),
        'BottomChannel':('bottom_channel',App.Placement(App.Vector(c['frame_front_x'],0,c['bottom_web_z']),App.Rotation())),
        'MiddleDiaphragm':('middle_diaphragm',App.Placement(App.Vector(c['frame_front_x'],0,low),App.Rotation()))}
    flip=App.Rotation(App.Vector(1,0,0),180)
    for side,sign in [('left',1),('right',-1)]:
        for role,station in [('inner',inner_y),('outer',outer_y)]:
            key='outer_angle' if role=='outer' else 'inner_angle_'+side
            rotated=role=='outer' and side=='right'
            placements[side.title()+role.title()+'Angle']=(key,App.Placement(
                App.Vector(c['frame_front_x'],sign*station,high if rotated else low),flip if rotated else App.Rotation()))
            for end,z in [('Top',c['top_web_z']),('Bottom',c['bottom_web_z'])]:
                reversed_end=end=='Bottom'
                key_side=('right' if side=='left' else 'left') if reversed_end else side
                key=role+'_gusset_'+key_side
                placements[side.title()+role.title()+end+'Gusset']=(key,App.Placement(
                    App.Vector(c['frame_front_x'],sign*station,z),flip if reversed_end else App.Rotation()))
    for name,shape in shapes.items():
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid frame member '+name)
    return shapes,placements,dict(channel_front_x_mm=c['frame_front_x'],channel_rear_x_mm=c['frame_front_x']-depth,
                                 middle_diaphragm_half_width_mm=diaphragm_half,angle_limits_z_mm=[low,high],
                                 gusset_count=8)


def revised_bracket(old,role,c,support,dimensions,shaft_center):
    d=dimensions[role];radius=support[role+'_cast_radius'];rear=d['foot_aft_x_mm'];front=d['foot_front_x_mm']
    low=c['bottom_web_z']-shaft_center.z-c['channel_height']
    high=c['top_web_z']-shaft_center.z+c['channel_height']
    lower_web=c['bottom_web_z']-shaft_center.z;upper_web=c['top_web_z']-shaft_center.z
    # Preserve the complete saddle, its bore, cap joint, and receiving holes.
    retained=old.common(box(-radius-8,300,-300,300,-200,200))
    width=d['foot_width_mm'];web=support['web_stock']
    pads=[box(rear,front,-width/2,width/2,low,lower_web),
          box(rear,front,-width/2,width/2,upper_web,high)]
    outline=[(rear,low),(front,low),(-radius+10,-support['bracket_height']/2),
             (-radius+10,support['bracket_height']/2),(front,high),(rear,high)]
    body=retained.multiFuse(pads+[xz_plate(outline,-web/2,web/2)])
    if role=='outer':
        b=old.BoundBox
        # The completed old candidate exposes the source-derived rear stem bounds.
        stem=old.common(box(b.XMin-1,rear-.01,-300,300,-200,200))
        sb=stem.BoundBox
        stem=box(sb.XMin+c['rear_stem_end_inset'],rear+1,sb.YMin,sb.YMax,
                 -support['rear_stem_height']/2,support['rear_stem_height']/2)
        edges=[e for e in stem.Edges if e.BoundBox.ZLength>support['rear_stem_height']-.01]
        stem=stem.makeFillet(c['rear_stem_round_radius'],edges)
        body=body.fuse(stem)
    result=body.removeSplitter()
    if not result.isValid() or len(result.Solids)!=1:raise ValueError('Invalid revised '+role+' bracket')
    witness=box(-radius+12,300,-300,300,-200,200)
    retained_difference=result.common(witness).cut(old).Volume+old.common(witness).cut(result).Volume
    return result,dict(retained_saddle_difference_mm3=retained_difference,
                       lower_pad_limits_z_mm=[low,lower_web],upper_pad_limits_z_mm=[upper_web,high],
                       required_inner_packing_gap_mm=shaft_center.x+rear-c['frame_front_x'])
