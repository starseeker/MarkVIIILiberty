"""Conditional high-speed anchor supports and integral case receiving webs.

Unprinted profiles and transverse depths are explicit reconstruction controls.
Brackets use brake-local XYZ; the revised case uses the retained central frame.
"""
import math
import FreeCAD as App
import Part
from transmission_frame_parts import xz_plate
from transmission_brake_anchor_parts import strip
from transmission_brake_stop_parts import hexagon
V=App.Vector


def datum(c,role):
    if role=='bottom':
        angle=math.radians(c['bottom_slope_deg'])
        return V(*c['anchor_center']),V(-math.cos(angle),0,-math.sin(angle)),V(math.sin(angle),0,-math.cos(angle)),c['bottom_seat_normal']
    angle=math.radians(c['top_slope_deg'])
    return V(*c['top_origin']),V(-math.cos(angle),0,math.sin(angle)),V(math.sin(angle),0,math.cos(angle)),0.


def tn_plate(origin,tangent,normal,points,y0,y1):
    points=[origin+tangent*t+normal*n for t,n in points]
    return xz_plate([(p.x,p.z) for p in points],y0,y1)


def parts(c,old_case):
    bracket_origin,t,n,seat=datum(c,'bottom')
    width=c['bracket_width'];stock=c['bracket_stock']
    start,end=c['bracket_foot_limits']
    bracket=tn_plate(bracket_origin,t,n,[(start,seat),(end,seat),(end,seat+stock),(start,seat+stock)],-width/2,width/2)
    gap=c['fork_gap'];outer=c['fork_outer_width']
    for y0,y1 in [(-outer/2,-gap/2),(gap/2,outer/2)]:
        eye=Part.makeCylinder(c['eye_radius'],y1-y0,bracket_origin+V(0,y0,0),V(0,1,0))
        web=strip(bracket_origin,bracket_origin+t*c['fork_web_reach'],c['fork_web_width'],y0,y1-y0)
        bracket=bracket.fuse(eye).fuse(web)
    # Trim the estimated cheek tails to the bracket's receiving plane. The
    # retained first trial left 709.947 mm3 per bracket below its flat seat.
    bracket=bracket.cut(tn_plate(bracket_origin,t,n,[(start,-100),(end+50,-100),(end+50,seat),(start,seat)],-width/2-1,width/2+1))
    # M361's wide rear band foot passes between the cheek noses. Preserve its
    # complete material and remove only the proposed bracket's inner corners.
    bracket=bracket.cut(Part.makeCylinder(c['band_clearance_radius'],width+2,V(0,-width/2-1,0),V(0,1,0)))
    bracket=bracket.cut(Part.makeCylinder(c['pin_bore_radius'],width+2,bracket_origin+V(0,-width/2-1,0),V(0,1,0)))
    new=dict(anchor_bracket=bracket)
    feet=[];ribs=[];ties=[];holes=[];mounts={}
    for role in ['top','bottom']:
        o,t,n,seat=datum(c,role)
        lo,hi=c[role+'_case_foot_limits']
        poses=[]
        for station in c[role+'_bolt_stations']:
            base=o+t*station+n*seat
            yaxis=n.cross(t)
            rotation=App.Rotation(App.Matrix(t.x,yaxis.x,n.x,0,t.y,yaxis.y,n.y,0,t.z,yaxis.z,n.z,0,0,0,0,1))
            pose=App.Placement(base,rotation)
            poses.append(list(pose.toMatrix().A))
        mounts[role]=dict(origin=list(o),tangent=list(t),normal=list(n),seat_normal_mm=seat,bolt_seat_frames=poses)
        for sign in [1,-1]:
            # Broad cast seats project from a thin bearing-side rib to the
            # brake plane. Their hidden transverse span is a named estimate.
            low=sign*(c['brake_station']-width/2);high=sign*(c['bearing_station']+c['web_stock']/2)
            foot=tn_plate(o,t,n,[(lo,seat-c['case_foot_stock']),(hi,seat-c['case_foot_stock']),(hi,seat),(lo,seat)],min(low,high),max(low,high))
            feet.append(foot)
            zsign=1 if role=='top' else -1
            root=V(c['rib_root_x'],0,zsign*c['rib_root_z'])
            tip=o+t*c[role+'_rib_station']+n*(seat-c['case_foot_stock']*.65)
            y=sign*c['bearing_station']
            ribs.append(strip(root,tip,c['rib_width'],y-c['web_stock']/2,c['web_stock']))
            # Tie into the existing case mounting bosses beyond the existing
            # stud bores; preserve the original frame-contact plane.
            z=c[role+'_frame_web_z']
            z0,z1=sorted([z,z+zsign*c['channel_height']])
            y0,y1=sorted([sign*c['tie_start_y'],sign*(c['bearing_station']+c['web_stock']/2)])
            ties.append(Part.makeBox(c['tie_depth'],y1-y0,z1-z0,V(c['frame_front_x'],y0,z0)))
            for f in poses:
                pose=App.Placement(App.Matrix(*f));pose.Base+=V(0,sign*c['brake_station'],0)
                # Case-local coordinates; rigid rotation is identical on both
                # hands because both brakes retain X forward and Z up.
                depth=c['mount_screw_length']-c['bracket_stock']-c['lock_plate_stock']+c['blind_gap']
                drill=Part.makeCylinder(c['mount_bore_radius'],depth+1,V(0,0,-depth));drill.Placement=pose
                holes.append(drill)
        if role=='bottom':
            tools=[]
            for f in poses:
                drill=Part.makeCylinder(c['mount_bore_radius'],stock+c['lock_plate_stock']+2,V(0,0,-1));drill.Placement=App.Placement(App.Matrix(*f));tools.append(drill)
            new['anchor_bracket']=new['anchor_bracket'].cut(Part.makeCompound(tools))
            # Common handbook locking strip with two inferred upturned tabs.
            # Tab interior faces meet opposite screw-head flats; bend radii
            # and exact original sheet profile remain unprinted.
            first,last=c[role+'_bolt_stations'];half=c['mount_head_af']/2
            w=half+c['lock_plate_stock'];base=seat+stock;top=base+c['lock_plate_stock']
            plate=tn_plate(o,t,n,[(first-c['lock_plate_end_margin'],base),(last+c['lock_plate_end_margin'],base),
                (last+c['lock_plate_end_margin'],top),(first-c['lock_plate_end_margin'],top)],-w,w)
            for sign,station in [(1,first),(-1,last)]:
                y0,y1=sorted([sign*half,sign*w])
                tab=tn_plate(o,t,n,[(station-c['lock_tab_half_length'],top-.1),(station+c['lock_tab_half_length'],top-.1),
                    (station+c['lock_tab_half_length'],top+c['lock_tab_height']),(station-c['lock_tab_half_length'],top+c['lock_tab_height'])],y0,y1)
                plate=plate.fuse(tab)
            new['anchor_lock_plate']=plate.cut(Part.makeCompound(tools))
    addition=Part.makeCompound(feet+ribs+ties)
    case=old_case.multiFuse(feet+ribs+ties).cut(Part.makeCompound(holes))
    new['case']=case
    # One inferred MX60 envelope can be shared by top and bottom mountings.
    new['mount_screw']=Part.makeCylinder(c['mount_screw_diameter']/2,c['mount_screw_length'],V(0,0,-c['mount_screw_length'])).fuse(hexagon(c['mount_head_af'],c['mount_head_stock']))
    for name,s in new.items():
        if not s.isValid() or len(s.Solids)!=1 or not s.Solids[0].isClosed():
            raise ValueError((name,s.isValid(),len(s.Solids)))
    return new,dict(mounts=mounts,anchor_center_brake_mm=c['anchor_center'],
        case_foot_count=len(feet),case_rib_count=len(ribs),case_tie_count=len(ties),
        limitations=['Unprinted receiver and bracket sections are conditional estimates.',
            'Integral case side ribs and transverse receiving seats are a reconstruction hypothesis.',
            'Mounting threads use nominal envelopes and clearance bores.',
            'Common locking strip and formed tabs are an HB133-led estimate; exact bend radii and production variant unresolved.',
            'This initial scope precedes the anchor pin and stop members.']),dict(addition_envelope=addition,receiving_holes=Part.makeCompound(holes))
