"""M399/M398 formed straps and M365 clip; shared MX61/MX60/M400 hardware.

Work in retained brake coordinates. Analytic planar/arcuate profiles retain
constant stock away from the explicitly mitered top-stop foot transition.
"""
import math
import FreeCAD as App
import Part
from transmission_high_brake_support_parts import datum,parts as receiving_parts
from transmission_high_brake_stop_parts import frame
V=App.Vector
Y=V(0,1,0)


def radial(angle):
    a=math.radians(angle);return V(math.cos(a),0,math.sin(a))


def arc(center,radius,start,end):
    return Part.Arc(center+radial(start)*radius,center+radial((start+end)/2)*radius,center+radial(end)*radius).toShape()


def plate(edges,width):
    s=Part.Face(Part.Wire(edges)).extrude(Y*width);s.translate(-Y*width/2);return Part.makeCompound([s])


def top_shape(c,rc):
    o,t,n,_=datum(rc,'top');s=c['top_stock'];low=c['back_stock'];middle=o+n*(low+s/2)
    radius=middle.z;inner=radius-s/2;outer=radius+s/2;end=c['top_arc_end_angle_deg'];far=c['foot_end']
    # Intersections of horizontal and inclined stock surfaces form a miter.
    upper_t=(outer-o.z-n.z*(low+s))/t.z;lower_t=(inner-o.z-n.z*low)/t.z
    a=o+t*far+n*(low+s);b=o+t*upper_t+n*(low+s);d=o+t*lower_t+n*low;e=o+t*far+n*low
    out_start=V(0,0,outer);in_start=V(0,0,inner);po=radial(end)*outer;pi=radial(end)*inner
    forward=V(math.sin(math.radians(end)),0,-math.cos(math.radians(end)));normal=radial(end);length=c['tongue_length']
    edges=[Part.makeLine(a,b),Part.makeLine(b,out_start),arc(V(),outer,90,end),Part.makeLine(po,po+forward*length),Part.makeLine(po+forward*length,pi+forward*length),Part.makeLine(pi+forward*length,pi),arc(V(),inner,end,90),Part.makeLine(in_start,d),Part.makeLine(d,e),Part.makeLine(e,a)]
    return plate(edges,c['strap_width']),radial(end)*radius,forward,normal


def back_shape(c,rc,toe):
    o,t,n,_=datum(rc,'top');h=c['back_stock']/2;start=o+n*h;far=start+t*c['foot_end'];R=c['back_fold_radius'];r=c['back_heel_radius']
    first_start=45.;first_end=first_start-c['back_fold_angle_deg'];C1=start-n*R
    p1=C1+radial(first_end)*R;E=V(math.sin(math.radians(first_end)),0,-math.cos(math.radians(first_end)));N=V(-E.z,0,E.x)
    p2=p1+E*c['back_straight_length'];C2=p2+N*r;second_start=math.degrees(math.atan2(-N.z,-N.x));second_end=second_start+c['back_heel_angle_deg']
    p3=C2+radial(second_end)*r;F=V(-math.sin(math.radians(second_end)),0,math.cos(math.radians(second_end)));N3=V(-F.z,0,F.x);p4=p3+F*toe
    edges=[Part.makeLine(far+n*h,start+n*h),arc(C1,R+h,first_start,first_end),Part.makeLine(p1+N*h,p2+N*h),arc(C2,r-h,second_start,second_end),Part.makeLine(p3+N3*h,p4+N3*h),Part.makeLine(p4+N3*h,p4-N3*h),Part.makeLine(p4-N3*h,p3-N3*h),arc(C2,r+h,second_end,second_start),Part.makeLine(p2-N*h,p1-N*h),arc(C1,R-h,first_end,first_start),Part.makeLine(start-n*h,far-n*h),Part.makeLine(far-n*h,far+n*h)]
    return plate(edges,c['strap_width']),dict(fold_center=list(C1),fold_end=list(p1),heel_center=list(C2),heel_end=list(p3),toe_direction=list(F),toe_end=list(p4),toe_length_mm=toe)


def parts(c,rc,case_before_receivers,shared,targets):
    newrc=dict(rc,top_bolt_stations=c['top_bolt_stations'])
    rebuilt,receiver_details,_=receiving_parts(newrc,case_before_receivers)
    shapes={'case':rebuilt['case'],'mount_screw':shared['mount_screw'].copy(),'lock_plate':shared['lock_plate'].copy(),'stop_screw':shared['stop_screw'].copy(),'stop_nut':shared['stop_nut'].copy()}
    target=Part.makeCompound(targets);top,tongue,forward,normal=top_shape(c,newrc)
    # Keep source-led bends/straight section fixed; solve only the inward toe
    # extension against the actual retained band envelope.
    low,high=.01,20.
    assert not back_shape(c,newrc,low)[0].common(target).Solids,'Back-stop body already intersects the band before its toe.'
    assert back_shape(c,newrc,high)[0].common(target).Solids,'Toe range never reaches the band.'
    for _ in range(25):
        mid=(low+high)/2
        if back_shape(c,newrc,mid)[0].common(target).Solids:high=mid
        else:low=mid
    back,back_details=back_shape(c,newrc,low-c['back_tip_gap']);back_details['first_contact_toe_mm']=low
    clipframe=frame(tongue+forward*c['clip_station'],forward,normal)
    width=c['strap_width'];stock=c['clip_stock'];gap=c['clip_gap'];half=c['clip_length']/2;bottom=-c['top_stock']/2;ceiling=c['top_stock']/2+gap;outertop=ceiling+stock
    clip=Part.makeBox(2*half,width+2*(gap+stock),outertop-bottom+stock,V(-half,-width/2-gap-stock,bottom-stock))
    channel=Part.makeBox(2*half+2,width+2*gap,ceiling-bottom,V(-half-1,-width/2-gap,bottom))
    clip=clip.cut(channel)
    screw_radius=shared['stop_screw_radius'];clip=clip.cut(Part.makeCylinder(screw_radius+c['clip_bore_gap'],outertop-bottom+2*stock,V(0,0,bottom-stock-1)))
    hole=Part.makeCylinder(c['tongue_bore_radius'],40,V(0,0,-20));hole.Placement=clipframe;top=top.cut(hole)
    # Both drilled straps share the relocated upper axes and existing60mm MX61.
    holes=[];mounts=receiver_details['mounts']['top']['bolt_seat_frames']
    for f in mounts:
        s=Part.makeCylinder(rc['mount_bore_radius'],c['back_stock']+c['top_stock']+2,V(0,0,-1));s.Placement=App.Placement(App.Matrix(*f));holes.append(s)
    top=top.cut(Part.makeCompound(holes));back=back.cut(Part.makeCompound(holes))
    oldo,oldt,oldn,oldseat=datum(rc,'bottom');first=rc['bottom_bolt_stations'][0]
    oldplateframe=frame(oldo+oldt*first+oldn*(oldseat+rc['bracket_stock']),oldt,oldn)
    newplateframe=App.Placement(App.Matrix(*mounts[0]));newplateframe.Base+=newplateframe.Rotation.multVec(V(0,0,c['back_stock']+c['top_stock']))
    lockframe=newplateframe.multiply(oldplateframe.inverse())
    # M400's saved definition has its flat tip at local Z=0 and shank behind it.
    q=clipframe.Base
    def tool(advance):return Part.makeCylinder(screw_radius,advance+60,q+normal*60,-normal)
    low,high=0.,80.;assert not tool(low).common(target).Solids and tool(high).common(target).Solids
    for _ in range(30):
        mid=(low+high)/2
        if tool(mid).common(target).Solids:high=mid
        else:low=mid
    tip_advance=low-c['stop_tip_gap'];screwframe=frame(q-normal*tip_advance,forward,-normal);nutframe=clipframe.multiply(App.Placement(V(0,0,outertop),App.Rotation()))
    shapes.update(top_stop=top,back_stop=back,clip=clip)
    for name,s in shapes.items():assert s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.Placement.isIdentity(),(name,s.isValid(),len(s.Solids),s.Placement)
    revision=[]
    for stations in [rc['top_bolt_stations'],c['top_bolt_stations']]:
        o,t,n,seat=datum(rc,'top');depth=rc['mount_screw_length']-rc['bracket_stock']-rc['lock_plate_stock']+rc['blind_gap']
        for sign in [-1,1]:
            for u in stations:
                f=frame(o+t*u+n*seat+Y*(sign*rc['brake_station']),t,n);hole=Part.makeCylinder(rc['mount_bore_radius'],depth+1,V(0,0,-depth));hole.Placement=f;revision.append(hole)
    return shapes,dict(receiver_controls=newrc,back=back_details,clip_frame=list(clipframe.toMatrix().A),clip_outer_top_mm=outertop,lock_frame=list(lockframe.toMatrix().A),mount_seat_frames=mounts,upper_clamped_stock_mm=c['back_stock']+c['top_stock']+rc['lock_plate_stock'],mount_engagement_mm=rc['mount_screw_length']-c['back_stock']-c['top_stock']-rc['lock_plate_stock'],stop_screw_frame=list(screwframe.toMatrix().A),stop_nut_frame=list(nutframe.toMatrix().A),stop_first_contact_advance_mm=low,stop_tip_advance_mm=tip_advance,tongue_frame=list(frame(tongue,forward,normal).toMatrix().A),limits=['Upper hole pitch revised to reuse handbook MX61 common plate; pitch remains an unprinted estimate.','M399 arc/miter, M398 bends, transverse stock and M365 enclosing clip with pierced tongue are reconstruction hypotheses.','Existing MX60 and M400/nut shapes reused; positive engagement is a geometric check, not structural qualification.','Toe and set-screw positions follow retained band envelopes; operating state and full service procedure remain unqualified.']),dict(upper_hole_revision=Part.makeCompound(revision))
