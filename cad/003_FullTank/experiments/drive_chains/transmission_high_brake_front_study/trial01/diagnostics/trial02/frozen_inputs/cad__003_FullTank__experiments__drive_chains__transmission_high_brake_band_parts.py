"""SNL long/short lining strips and partial steel backings, dimensions in mm.

Definitions start at +X and advance towards +Z about +Y. Printed flat lengths
apply to the lining middle radius. This is an explicit bending approximation.
These backing blanks do not yet contain their end attachments or steel rivets.
"""
import math
import FreeCAD as App
import Part
from transmission_brake_band_parts import sector,point,rotate_theta

V=App.Vector

def parts(c):
    ri=c['inner_radius'];ro=ri+c['lining_stock'];neutral=(ri+ro)/2
    hole_r=c['hole_diameter']/2;depth=c['lining_stock']-c['straight_bore_depth']
    slope=math.tan(math.radians(c['countersink_included_angle_deg']/2))
    assert depth>0 and c['long_flat_length']>2*c['short_flat_length']
    shapes={};details={}
    for role in ['long','short']:
        length=c[role+'_flat_length'];sweep=length/neutral
        lining=sector(ri,ro,0,sweep,c['width'])
        extra=c['steel_terminal_margin']/neutral
        band=sector(ro,ro+c['steel_stock'],-extra,sweep+extra,c['width'])
        groups=2 if role=='long' else 1
        group_shift=c['long_flat_length']-c['short_flat_length']
        holes=[];lining_tools=[];band_tools=[]
        for group in range(groups):
            for n in range(6):
                along=group*group_shift+c['end_margin']+n*c['hole_pitch']
                y=(-1 if n%2==0 else 1)*(c['width']/2-c['edge_margin'])
                theta=along/neutral
                pose=App.Placement(point(ri,theta,y),App.Rotation(V(0,0,1),point(1,theta,0)))
                drill=Part.makeCylinder(hole_r,c['lining_stock']+4,V(0,0,-2))
                sink=Part.makeCone(hole_r+(depth+2)*slope,hole_r,depth+2,V(0,0,-2))
                tool=drill.fuse(sink);tool.Placement=pose;lining_tools.append(tool)
                tool=Part.makeCylinder(c['steel_hole_radius'],c['lining_stock']+c['steel_stock']+4,V(0,0,-2))
                tool.Placement=pose;band_tools.append(tool)
                holes.append(dict(group=group,index=n,along_mm=along,axial_mm=y,theta_rad=theta,frame=list(pose.toMatrix().A)))
        lining=lining.cut(Part.makeCompound(lining_tools));band=band.cut(Part.makeCompound(band_tools))
        for key,shape in [(role+'_lining',lining),(role+'_band',band)]:
            assert shape.isValid() and len(shape.Solids)==1 and shape.Solids[0].isClosed(),key
            shapes[key]=shape
        details[role]=dict(flat_length_mm=length,sweep_rad=sweep,neutral_radius_mm=neutral,
            holes=holes,steel_extra_sweep_rad=extra,stock_volume_before_holes_mm3=length*c['width']*c['lining_stock'])
    # Keep a separate lining seam; steel blanks terminate face-to-face at it.
    seam=max(c['joint_lining_gap'],2*c['steel_terminal_margin'])/neutral
    joint=math.radians(c['joint_clock_deg'])
    details['placement_angles_rad']=dict(long=joint-seam/2-details['long']['sweep_rad'],short=joint+seam/2)
    details['lining_seam_mm']=seam*neutral
    return shapes,details
