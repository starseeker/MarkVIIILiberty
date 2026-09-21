"""Front coupling and seven-turn spring; source-linked static approximations."""
import math
import FreeCAD as App
import Part
from air_pressure_pump_parts import box,xc,cyl,hexagon,bolt,moved
from transmission_input_parts import spline


def spring(c):
    turns=c['spring_turns'];end=c['spring_end_turns'];r=c['spring_wire_radius']
    mean=c['spring_inside_radius']+r;rear=c['spring_rear_seat'];height=c['spring_length']
    blend=c['spring_transition_turns'];end_pitch=c['spring_end_pitch']
    offset=(1-c['spring_end_grind_fraction'])*r;rise=height-2*offset
    area=turns-2*end-blend
    free_pitch=end_pitch+(rise-end_pitch*turns)/area
    assert free_pitch>end_pitch>2*r and area>0
    def integral(u):
        if u<=end:return 0
        if u<end+blend:
            t=(u-end)/blend;return blend*(t**3-.5*t**4)
        if u<=turns-end-blend:return blend/2+u-end-blend
        if u<turns-end:
            t=(u-(turns-end-blend))/blend
            return turns-2*end-1.5*blend+blend*(t-t**3+.5*t**4)
        return area
    pts=[];count=turns*c['spring_samples_per_turn']
    for n in range(count+1):
        u=n/c['spring_samples_per_turn'];angle=2*math.pi*u
        x=rear+offset+end_pitch*u+(free_pitch-end_pitch)*integral(u)
        pts.append(App.Vector(x,mean*math.cos(angle),mean*math.sin(angle)))
    path=Part.BSplineCurve();path.interpolate(pts)
    wire=Part.Wire([path.toShape()]);normal=path.tangent(path.FirstParameter)[0]
    profile=Part.Wire([Part.makeCircle(r,pts[0],normal)])
    shape=wire.makePipeShell([profile],True,True)
    # Ground ends are cuts of one continuous wire; no invented cap solids.
    shape=shape.common(xc(mean+r+1,rear,rear+height))
    detail=dict(turns=turns,free_turns=turns-2*end,end_turns_each=end,
        selected_inside_radius=c['spring_inside_radius'],mean_radius=mean,wire_radius=r,
        end_pitch=end_pitch,free_pitch=free_pitch,centerline_rise=rise,
        seats=[rear,rear+height],sample_count=len(pts),ground_depth=r-offset)
    return shape,wire,detail


def blend_shaft(old,dc,c):
    shaft=old.copy();head_end=dc['head_end'];tip=dc['head_start']+dc['shaft_length']
    spline_start=tip-dc['spline_length'];edges=[]
    for edge in shaft.Edges:
        curve=edge.Curve
        if hasattr(curve,'Radius') and abs(curve.Radius-dc['shaft_radius'])<1e-5:
            if any(abs(edge.CenterOfMass.x-x)<1e-5 for x in [head_end,spline_start]):edges.append(edge)
    assert len(edges)==2,('shaft shoulder circles',len(edges))
    return shaft.makeFillet(c['shaft_shoulder_fillet'],edges)


def build(c,dc,old_shaft,old_box):
    parts={};occ=[];rear=c['spring_rear_seat'];front=rear+c['spring_length'];end=front+c['coupling_flange_stock']
    collar=xc(c['clamp_hub_radius'],c['clamp_rear'],rear)
    collar=collar.fuse(xc(c['clamp_flange_radius'],c['clamp_plate_start'],rear))
    for sign in [-1,1]:
        y=sign*c['clamp_bolt_y'];x=c['clamp_bolt_x']
        collar=collar.fuse(box(x-c['clamp_lug_half_x'],x+c['clamp_lug_half_x'],
            y-c['clamp_lug_half_y'],y+c['clamp_lug_half_y'],-c['clamp_seat_z'],c['clamp_seat_z']))
        hole=moved(cyl(c['bolt_diameter']/2+c['bolt_hole_gap'],-c['clamp_seat_z']-1,c['clamp_seat_z']+1),(x,y,0))
        collar=collar.cut(hole)
    collar=collar.cut(xc(dc['shaft_radius'],c['clamp_rear']-1,rear+1))
    parts['half_flange']=collar.common(box(c['clamp_rear']-1,rear+1,-100,100,c['clamp_split_gap']/2,100)).removeSplitter()
    parts['bolt']=bolt(c['bolt_diameter'],c['bolt_length'],c['bolt_head_af'],c['bolt_head_height'])
    parts['nut']=hexagon(c['nut_af'],0,c['nut_height']).cut(cyl(c['bolt_diameter']/2+c['nut_gap'],-1,c['nut_height']+1)).removeSplitter()
    parts['washer']=cyl(c['washer_outer_radius'],0,c['washer_stock']).cut(cyl(c['washer_bore_radius'],-1,c['washer_stock']+1))
    parts['washer']=parts['washer'].cut(box(0,c['washer_outer_radius']+1,-c['washer_split']/2,c['washer_split']/2,-1,c['washer_stock']+1)).removeSplitter()
    coupling=xc(c['coupling_body_radius'],c['coupling_rear'],end).fuse(xc(c['coupling_flange_radius'],front,end)).removeSplitter()
    edge=[e for e in coupling.Edges if hasattr(e.Curve,'Radius') and abs(e.Curve.Radius-c['coupling_body_radius'])<1e-6 and abs(e.CenterOfMass.x-front)<1e-6]
    assert len(edge)==1
    coupling=coupling.makeFillet(c['coupling_flange_fillet'],edge)
    gap=c['coupling_spline_gap']
    coupling=coupling.cut(spline(dc['spline_root_radius']+gap,dc['spline_radius']+gap,
        dc['spline_width']+2*gap,dc['spline_count'],c['coupling_rear']-1,end+1))
    for n in range(c['collar_bolt_count']):
        theta=2*math.pi*n/c['collar_bolt_count'];rad=c['collar_bolt_circle']
        coupling=coupling.cut(xc(c['collar_bolt_hole_radius'],front-1,end+1,rad*math.cos(theta),rad*math.sin(theta)))
    parts['coupling']=coupling.removeSplitter()
    parts['spring'],spine,sd=spring(c)
    shaft=blend_shaft(old_shaft,dc,c)
    relief=xc(dc['shaft_radius']+c['shaft_shoulder_fillet']+dc['receiver_gap'],
        dc['head_end']-c['box_relief_extra'],dc['head_end']+c['shaft_shoulder_fillet']+c['box_relief_extra'])
    receiver=old_box.cut(relief).removeSplitter()
    def add(name,key,xyz=(0,0,0),angle=0):occ.append(dict(name='FrontClutch_'+name,key=key,xyz=list(xyz),angle=angle))
    add('UpperFlange','half_flange');add('LowerFlange','half_flange',angle=180)
    add('Coupling','coupling');add('Spring','spring')
    for n,sign in enumerate([-1,1],1):
        x=c['clamp_bolt_x'];y=sign*c['clamp_bolt_y'];z=c['clamp_seat_z']
        add(f'Set{n}_Bolt','bolt',(x,y,z))
        add(f'Set{n}_Washer','washer',(x,y,-z-c['washer_stock']))
        add(f'Set{n}_Nut','nut',(x,y,-z-c['washer_stock']-c['nut_height']))
    revised=dict(shaft=shaft,box=receiver)
    for key,s in {**parts,**revised}.items():
        assert s.isValid() and len(s.Solids)==1,(key,s.isValid(),len(s.Solids))
    return parts,occ,revised,dict(spring=sd,coupling_flange_start=front,coupling_front=end,
        bolt_protrusion=c['bolt_length']-2*c['clamp_seat_z']-c['washer_stock']-c['nut_height'],
        shoulder_fillet=c['shaft_shoulder_fillet'],clutch_collar_joint_complete=False),spine
