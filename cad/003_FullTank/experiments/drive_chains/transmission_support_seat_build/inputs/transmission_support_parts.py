"""Fixed output-bearing castings and separate in-situ babbitt regions.

Local +X is forward, +Y shaft axis and +Z up. No rotating-shaft phase here.
All unprinted dimensions are explicit controls, not inferred manufacturing fits.
"""
import FreeCAD as App
import Part

from transmission_output_parts import cylinder


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1-x0, y1-y0, z1-z0, App.Vector(x0,y0,z0))


def parts(controls, picks, calibration, sleeves):
    c=controls; shapes={}; dimensions={}
    scale=calibration['mm_per_pixel']; axis=calibration['shaft_axis_y_px']
    for role in ['inner','outer']:
        sleeve=sleeves[role]
        length=sleeve['barrel_length_mm']-2*c['end_gap']
        bore=sleeve['barrel_radius_mm']+c['running_gap']
        socket=bore+c['lining_stock']; radius=c[role+'_cast_radius']
        rear,front=[(v-axis)*scale for v in picks[role]['foot_y_px']]
        foot_width=(picks[role]['foot_x_px'][1]-picks[role]['foot_x_px'][0])*scale
        half=c['bracket_height']/2
        halfspace={
            'back':box(-600,-c['split_gap'],-400,400,-400,400),
            'front':box(c['split_gap'],600,-400,400,-400,400)}
        annulus=cylinder(radius,-length/2,length/2)
        ear_y=length/2-c['stud_y_inset']; ear_z=radius-4
        ears=[]; holes=[]
        for y in [-ear_y,ear_y]:
            for z in [-ear_z,ear_z]:
                ears.append(Part.makeCylinder(c['ear_radius'],2*c['ear_x_extent'],
                            App.Vector(-c['ear_x_extent'],y,z),App.Vector(1,0,0)))
                holes.append(Part.makeCylinder(c['stud_diameter']/2+c['stud_hole_gap'],
                             2*c['ear_x_extent']+2,App.Vector(-c['ear_x_extent']-1,y,z),App.Vector(1,0,0)))
        blank=annulus.multiFuse(ears)
        bracket=blank.common(halfspace['back']).multiFuse([
            box(rear,front,-foot_width/2,foot_width/2,-half,half),
            box(front-1,-radius+12,-c['web_stock']/2,c['web_stock']/2,-half,half),
            box(-radius-8,-radius+12,-length/2,length/2,-half,half)])
        stem=None
        if role=='outer':
            start,end=[(v-axis)*scale for v in picks[role]['stem_y_px']]
            width=(picks[role]['stem_x_px'][1]-picks[role]['stem_x_px'][0])*scale
            stem=box(start,end+1,-width/2,width/2,-c['rear_stem_height']/2,c['rear_stem_height']/2)
            bracket=bracket.fuse(stem)
        cup_front=c[role+'_cup_front'];cup_back=cup_front-c['cup_length']
        cup=box(cup_back,cup_front,-c['cup_width']/2,c['cup_width']/2,-c['cup_height']/2,c['cup_height']/2)
        neck=box(radius-12,cup_back+10,-c['cup_width']/2,c['cup_width']/2,-c['cup_height']/2,c['cup_height']/2)
        cap=blank.common(halfspace['front']).multiFuse([cup,neck])
        cavity=box(cup_back+c['cup_stock'],cup_front-c['cup_stock'],
                   -c['cup_width']/2+c['cup_stock'],c['cup_width']/2-c['cup_stock'],
                   -c['cup_height']/2+c['cup_stock'],c['cup_height']/2+1)
        cap=cap.cut(cavity)
        # Form a flat lid seat where the cup merges into the curved cap.
        # Without this cut the common outside lid penetrates the cap's crown.
        lid_seat=box(cup_back-c['lid_overhang'],cup_front+c['lid_overhang'],
                     -c['cup_width']/2-c['lid_overhang'],c['cup_width']/2+c['lid_overhang'],
                     c['cup_height']/2,2*radius)
        cap=cap.cut(lid_seat)
        socket_tool=cylinder(socket,-length/2-1,length/2+1)
        hole_tool=Part.makeCompound(holes)
        shapes[role+'_bracket']=bracket.cut(socket_tool).cut(hole_tool).removeSplitter()
        shapes[role+'_cap']=cap.cut(socket_tool).cut(hole_tool).removeSplitter()
        lining=cylinder(socket,-length/2,length/2).cut(cylinder(bore,-length/2-1,length/2+1))
        for side in ['back','front']:
            shapes[role+'_lining_'+side]=lining.common(halfspace[side]).removeSplitter()
        # Common lid geometry has its origin at the cup back/top edge.
        dimensions[role]=dict(bore_radius_mm=bore,socket_radius_mm=socket,length_mm=length,
                             foot_aft_x_mm=rear,foot_front_x_mm=front,foot_width_mm=foot_width,
                             cup_back_x_mm=cup_back,cup_front_x_mm=cup_front,cup_top_z_mm=c['cup_height']/2,
                             stud_axes_yz_mm=[[y,z] for y in [-ear_y,ear_y] for z in [-ear_z,ear_z]])
    shapes['lid']=box(-c['lid_overhang'],c['cup_length']+c['lid_overhang'],
                      -c['cup_width']/2-c['lid_overhang'],c['cup_width']/2+c['lid_overhang'],0,c['lid_stock'])
    for name,shape in shapes.items():
        if not shape.isValid() or len(shape.Solids)!=1:
            raise ValueError('Invalid fixed bearing part: '+name)
    return shapes,dimensions
