"""Estimated support side plates on the two real forward floor planes."""
import math
from control_rebuild_io_v2 import App, Part
from bow_reconstruction_parts import intersection, line_offset, section

V=App.Vector;Y=V(0,1,0)


def floor_profile(bow):
    inner=bow['joint_datums']['inner']
    points=sorted([inner[k] for k in ['bow_lower','floor_bend','floor_seam','floor_end']])
    def at(x):
        for a,b in zip(points,points[1:]):
            if a[0]-1e-6<=x<=b[0]+1e-6:
                slope=(b[1]-a[1])/(b[0]-a[0]);n=V(-slope,0,1);n.normalize()
                return a[1]+slope*(x-a[0]),n
        raise ValueError('Mount is outside the reconstructed floor: '+str(x))
    return points,at


def support(bow, controls, main, rear, hand):
    points,at=floor_profile(bow)
    base=V(rear.x,0,at(rear.x)[0]);sep=main.x-rear.x;t=controls['plate_stock']
    outer=controls['nut_seat_y'];inside=outer-t
    a,b=rear.x-70,main.x-25
    bottom=[[a,at(a)[0]]]+[p for p in points if a<p[0]<b]+[[b,at(b)[0]]]
    offsets=[line_offset(p,q,t,[0,1]) for p,q in zip(bottom,bottom[1:])]
    upper=[intersection(offsets[0],([a,0],[a,1]))]
    upper += [intersection(p,q) for p,q in zip(offsets,offsets[1:])]
    upper += [intersection(offsets[-1],([b,0],[b,1]))]
    local=lambda p:[p[0]-base.x,p[1]-base.z]
    footpoly=[local(p) for p in bottom+list(reversed(upper))]
    yy=sorted([hand*inside,hand*(outer+55)])
    foot=section(footpoly,*yy)
    bottom_web=[[x-base.x,z-base.z-.3] for x,z in upper]
    profile=bottom_web+[[sep+20,main.z-base.z-15],[sep,main.z-base.z],
                        [0,rear.z-base.z],[-35,rear.z-base.z-15],[-70,rear.z-base.z-40]]
    web=section(profile,*sorted([hand*inside,hand*outer]))
    q=foot.fuse(web)
    for x,z,radius in [(0,rear.z-base.z,24),(sep,main.z-base.z,31)]:
        q=q.fuse(Part.makeCylinder(radius,t,V(x,hand*inside,z),Y*hand))
    for x,z,radius in [(0,rear.z-base.z,12.15),(sep,main.z-base.z,14.15)]:
        q=q.cut(Part.makeCylinder(radius,t+2,V(x,hand*(inside-1),z),Y*hand))
    mounts=[]
    for x in [rear.x-40,rear.x-10,main.x-80,main.x-50]:
        z,n=at(x);p=V(x,hand*(outer+27.5),z);local_point=p-base
        q=q.cut(Part.makeCylinder(6.5,t+2,local_point-n,n))
        mounts.append(dict(contact_world_mm=list(p),normal_world=list(n),
                           floor='hull_floor_2' if x<bow['joint_datums']['inner']['floor_seam'][0] else 'hull_floor_1'))
    return q.removeSplitter(),App.Placement(base,App.Rotation()),mounts,dict(
        floor_contact_section_world=bottom,upper_foot_section_world=upper,stock_mm=t,
        canonical_origin_world_mm=list(base),main_shaft_local_mm=[sep,0,main.z-base.z],
        swing_shaft_local_mm=[0,0,rear.z-base.z],
        approximation='Folded foot and vertical side web on the inferred floor. Sharp bends and unprinted outline remain provisional.')
