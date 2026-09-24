"""Handbook segmented brake linings, drilled half-bands and copper rivets.

Brake coordinates: origin on the drum axis at its friction-face axial center;
+X forward, +Y along the shaft, +Z upward. Segment definitions begin at +X and
advance toward +Z. Installed half-bands use rigid occurrences, never mirrored
solids. Printed flat lengths are preserved at the lining's middle radius.
"""
import math
import FreeCAD as App
import Part
from transmission_frame_joint_parts import cap

V=App.Vector


def point(radius,theta,y):return V(radius*math.cos(theta),y,radius*math.sin(theta))


def sector(inner,outer,start,end,width):
    y=-width/2
    def arc(radius,a,b):return Part.Arc(*[point(radius,v,y) for v in [a,(a+b)/2,b]]).toShape()
    edges=[arc(outer,start,end),Part.makeLine(point(outer,end,y),point(inner,end,y)),
           arc(inner,end,start),Part.makeLine(point(inner,start,y),point(outer,start,y))]
    return Part.Face(Part.Wire(edges)).extrude(V(0,width,0))


def rotate_theta(theta):return App.Rotation(V(0,1,0),-math.degrees(theta))


def copper_rivet(c):
    r=c['rivet_shank_diameter']/2;dr=c['hole_diameter']/2
    depth=c['lining_stock']-c['straight_lining_stock']-c['rivet_head_recess']
    headrad=dr+depth*math.tan(math.radians(c['countersink_angle_deg']/2))
    grip=c['lining_stock']+c['steel_stock']-c['tail_spotface_depth']-c['rivet_head_recess']
    under_head_grip=grip-depth
    assert depth>0 and 0<under_head_grip<c['rivet_stock_length']
    volume=math.pi*r*r*(c['rivet_stock_length']-under_head_grip)
    radius=c['rivet_tail_radius'];low,high=0,radius
    assert volume<2*math.pi*radius**3/3
    for _ in range(80):
        height=(low+high)/2
        if math.pi*height*(3*radius*radius+height*height)/6<volume:low=height
        else:high=height
    height=(low+high)/2
    head=Part.makeCone(headrad,dr,depth)
    shank=Part.makeCylinder(r,under_head_grip,V(0,0,depth))
    tail=cap(radius,height);tail.translate(V(0,0,grip))
    shape=head.multiFuse([shank,tail])
    assert shape.isValid() and len(shape.Solids)==1
    return shape,dict(head_depth_mm=depth,head_radius_mm=headrad,grip_mm=grip,
        under_head_grip_mm=under_head_grip,tail_height_mm=height,tail_volume_mm3=volume)


def parts(c):
    rivet,rd=copper_rivet(c);shapes={'copper_rivet':rivet};details={};curves={}
    for role in ['low','track']:
        v=c[role];ri=v['inner_radius'];ro=ri+c['lining_stock'];neutral=(ri+ro)/2
        sweep=v['segment_flat_length']/neutral
        total=(3*v['segment_flat_length']+2*c['segment_seam']+2*c['terminal_margin'])/neutral
        # An estimated one-degree gap at each side of the rear split leaves
        # room for the separately reconstructed anchor brackets and joining ends.
        end=math.pi-math.radians(c['rear_split_half_gap_deg'])+math.radians(c['opening_clock_deg']);start=end-total
        assert 0<start<end<2*math.pi and total<math.pi
        lining=sector(ri,ro,0,sweep,v['width'])
        band=sector(ro,ro+c['steel_stock'],start,end,v['width']+2*c['steel_side_overhang'])
        lining_tools=[];holes=[]
        for column in range(4):
            along=c['hole_end_margin']+column*v['hole_pitch'];theta=along/neutral
            offsets=[-v['width']/2+c['hole_edge_margin'],v['width']/2-c['hole_edge_margin']]
            if column==0:offsets.insert(1,0)
            for y in offsets:
                direction=point(1,theta,0);origin=point(ri+c['rivet_head_recess'],theta,y)
                rotation=App.Rotation(V(0,0,1),direction);pose=App.Placement(origin,rotation)
                drill=Part.makeCylinder(c['hole_diameter']/2,c['lining_stock']+10,V(0,0,-5))
                k=math.tan(math.radians(c['countersink_angle_deg']/2))
                cone=Part.makeCone(c['hole_diameter']/2+(rd['head_depth_mm']+5)*k,c['hole_diameter']/2,
                                   rd['head_depth_mm']+5,V(0,0,-5))
                tool=drill.fuse(cone);tool.Placement=pose;lining_tools.append(tool)
                holes.append(dict(column=column,along_mm=along,axial_mm=y,theta_rad=theta,
                    frame=list(pose.toMatrix().A)))
        assert len(holes)==9
        assert abs(v['segment_flat_length']-(2*c['hole_end_margin']+3*v['hole_pitch']))<1e-8
        lining=lining.cut(Part.makeCompound(lining_tools))
        segment_angles=[];band_tools=[];joints=[]
        for n in range(3):
            angle=start+(c['terminal_margin']+n*(v['segment_flat_length']+c['segment_seam']))/neutral
            segment_angles.append(angle);sp=App.Placement(V(),rotate_theta(angle))
            for index,h in enumerate(holes):
                pose=sp.multiply(App.Placement(App.Matrix(*h['frame'])))
                drill=Part.makeCylinder(c['rivet_shank_diameter']/2+c['steel_hole_clearance'],rd['grip_mm']+20,V(0,0,-5))
                spot=Part.makeCylinder(c['rivet_tail_radius']+.05,rd['tail_height_mm']+5,V(0,0,rd['grip_mm']))
                tool=drill.fuse(spot);tool.Placement=pose;band_tools.append(tool)
                joints.append(dict(segment=n+1,hole=index+1,frame=list(pose.toMatrix().A)))
        band=band.cut(Part.makeCompound(band_tools))
        for key,s in [('lining',lining),('band',band)]:
            assert s.isValid() and len(s.Solids)==1,(role,key,s.isValid(),len(s.Solids))
            shapes[role+'_'+key]=s
        curves[role]=Part.Arc(*[point(neutral,v,0) for v in [0,sweep/2,sweep]]).toShape()
        details[role]=dict(inner_radius_mm=ri,outer_radius_mm=ro,neutral_radius_mm=neutral,
            segment_sweep_rad=sweep,half_sweep_rad=total,half_start_rad=start,half_end_rad=end,
            segment_angles_rad=segment_angles,holes=holes,joints=joints,
            blank_lining_volume_mm3=v['width']*c['lining_stock']*v['segment_flat_length'])
    return shapes,dict(brakes=details,rivet=rd),curves


def revised_land(old,ri,width,c):
    """Raise only the external friction land; retain old interior/end material.

    Connecting conical shoulders are hypotheses. Zero-thickness annulus ends
    coincide with the previous outer cylinder. No existing solid is cut away.
    """
    faces=[f for f in old.Faces if isinstance(f.Surface,Part.Cylinder) and abs(abs(f.Surface.Axis.y)-1)<1e-7]
    face=max(faces,key=lambda f:(f.Surface.Radius,f.Area));b=face.BoundBox;radius=face.Surface.Radius
    center=(b.YMin+b.YMax)/2;half=width/2+c['land_axial_margin']
    lo,hi=b.YMin+c['protected_end_width'],b.YMax-c['protected_end_width']
    assert radius<ri and lo<center-half<center+half<hi
    # The old cylindrical face spans these stations; all added stock lies
    # outside it. Keep both end strips and every original drilled interface.
    profile=[(radius,lo),(ri,center-half),(ri,center+half),(radius,hi)]
    points=[V(rad,y,0) for rad,y in profile]
    addition=Part.Face(Part.makePolygon(points+points[:1])).revolve(V(),V(0,1,0),360)
    shape=old.fuse(addition)
    assert shape.isValid() and len(shape.Solids)==1
    return shape,addition,dict(old_radius_mm=radius,new_radius_mm=ri,old_axial_limits_mm=[b.YMin,b.YMax],
        axial_center_mm=center,contact_land_limits_mm=[center-half,center+half],addition_limits_mm=[lo,hi],
        added_volume_mm3=addition.Volume,profile_radial_axial_mm=profile)
