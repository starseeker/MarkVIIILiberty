"""Independent saved-material checks of corrected driver links and complete low-speed rods."""
import argparse,math,json
from pathlib import Path
from control_rebuild_io_v2 import *
from check_driver_foundation_interfaces import check_foundation
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);r=s.report;d=r['details'];c=d['controls'];parent=Saved((ROOT/r['parent_native']).parent);out=s.folder/'checks03';out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
checks=check_foundation(s,parent)
def ck(name,ok,**kw):
    checks.append(dict(name=name,passed=bool(ok),**kw));write(out/'progress.json',checks)
    if not ok:print('FAIL',name,kw,flush=True)
def vol(q):return sum(abs(v.Volume) for v in q.Solids)
def cyl(q,point,axis,radius):return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-point).cross(axis).Length<1e-6]
def span(f,point,axis):
    vals=[(v.Point-point).dot(axis) for v in f.Vertexes];return min(vals),max(vals)
def planes(q,point,axis):return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.Surface.Axis.cross(axis).Length<1e-7 and abs((f.CenterOfMass-point).dot(axis))<1e-6]
def bearing(q,t,point,axis):return sum(f.common(g).Area for f in planes(q,point,axis) for g in planes(t,point,axis))
ck('30 real additions, seven definitions and seven declared driver revisions',len(r['new_occurrences'])==30 and len(r['new_definitions'])==7 and len(r['changed_definitions'])==7 and len(s.rows)==94)
ck('Source M772 binding names actual catalogue row15',set(json.loads(s.manifest['definitions']['Def_DriverClutchLever_M772']['properties']['SourceRecords']))=={'SNL:116:015','HB:149'})
ck('Four source M784 occurrences share one definition',len(d['swings'])==4 and all(s.rows[v['occurrence']]['definition']=='Def_DriverSwingLink_M784' for v in d['swings'].values()))
shaft=s.world('DriverSwingShaft')
for branch,record in d['swings'].items():
    q=s.world(record['occurrence']);frame=pose(s.rows[record['occurrence']]['frame']);pivot=frame.Base;width=c['swing_journal_width'];core=Part.makeCylinder(12.7,width,pivot-Y*width/2,Y)
    fs=cyl(q,pivot,Y,12.85)
    ck(branch+' actual full journal and retained shaft stock',bool(fs) and all(abs(span(f,pivot,Y)[1]-span(f,pivot,Y)[0]-width)<1e-6 for f in fs) and vol(core.cut(shaft))<1e-5 and vol(q.common(shaft))<1e-5)
    ck(branch+' real radial oil passage into journal',vol(q.common(Part.makeCylinder(1.5,26,pivot,Z)))<1e-5 and bool(cyl(q,pivot,Z,1.5)))
    for end in ['front','rear']:
        point=V(*record[end+'_pin_world_mm']);fs=cyl(q,point,Y,6.5)
        ck(branch+' '+end+' uninterrupted receiver bore',len(fs)==1 and abs(fs[0].Area-2*math.pi*6.5*c['swing_web_stock'])<1e-5 and point.z<pivot.z)
        annulus=Part.makeCylinder(11,c['swing_web_stock'],point-Y*c['swing_web_stock']/2,Y).cut(Part.makeCylinder(6.5,c['swing_web_stock']+2,point-Y*(c['swing_web_stock']/2+1),Y))
        ck(branch+' '+end+' complete annular eye stock',vol(annulus.cut(q))<1e-5)
lever=s.world('DriverClutchOperatingLever');frame=pose(s.rows['DriverClutchOperatingLever']['frame']);pivot=frame.Base;bell=V(*d['clutch_bell_pin_world_mm']);main=s.world('DriverMainShaft');local=s.definition('Def_DriverClutchLever_M772');width=c['lever_boss_width']
caps=[f.Surface for f in local.Faces if isinstance(f.Surface,Part.Sphere) and abs(f.Surface.Radius-10.5)<1e-7]
reach=28.5*25.4
ck('M772 printed28-1/2in hand reach retained in actual solid',len(caps)==1 and abs(caps[0].Center.Length+caps[0].Radius-reach)<1e-7 and vol(local.cut(Part.makeSphere(reach)))<1e-5)
if caps:
    direction=caps[0].Center/caps[0].Center.Length
    ck('M772 real outward grip with retained radial reach',direction.y>0 and abs(direction.y*reach-c['lever_hand_outward_offset'])<1e-7 and bool(cyl(local,caps[0].Center,direction,10.5)))
ck('M772 printed5in bell reach reaches actual pin bore',abs((bell-pivot).Length-5*25.4)<1e-7 and len(cyl(lever,bell,Y,6.5))==1)
fs=cyl(lever,pivot,Y,38.3238/2)
ck('M772 true open journal and complete M782 stock',bool(fs) and vol(Part.makeCylinder(19.0119,width,pivot-Y*width/2,Y).cut(main))<1e-5 and vol(lever.common(main))<1e-5)
ck('M772 oil bore reaches the actual bearing opening',bool(cyl(local,V(),X,1.5)) and vol(local.common(Part.makeCylinder(1.5,32,V(),-X)))<1e-5)
for kind,record in d['rods'].items():
    name='DriverClutch'+kind+'Rod';rod=s.world(name);start=V(*record['stock_start_world_mm']);axis=V(*record['axis_world']);length=record['stock_length_mm'];core=Part.makeCylinder(9.525,length,start,axis)
    ck(kind+' complete full-diameter rod, no trimmed end stock',vol(core.cut(rod))<1e-5 and vol(rod.cut(core))<1e-5 and abs(rod.Volume-math.pi*9.525**2*length)<1e-5)
    if kind=='Short':ck('M789B source12-5/8in stock closes actual pins',abs(length-12.625*25.4)<1e-7 and abs(record['pin_span_mm']-371.475)<1e-7)
    else:ck('M576 is one complete rod with explicitly inferred family length',len(rod.Solids)==1 and s.manifest['definitions'][s.rows[name]['definition']]['properties']['SourcePartMark']=='M576',unprinted_stock_mm=length)
    for joint in record['endpoints']:
        stem=joint['stem'];receiver=s.world(joint['receiver']);fork=s.world(stem+'Fork');pin=s.world(stem+'Pin');nut=s.world(stem+'Nut');cotter=s.world(stem+'Cotter');jf=pose(s.rows[stem+'Fork']['frame']);point=jf.Base;axis=jf.Rotation.multVec(X);pinaxis=jf.Rotation.multVec(Y)
        fs=cyl(receiver,point,pinaxis,6.5)
        ck(stem+' actual coaxial receiver and correct M568C pin',len(fs)==1 and bool(cyl(pin,point,pinaxis,6.35)) and s.manifest['definitions'][s.rows[stem+'Pin']['definition']]['properties']['SourcePartMark']=='M568C')
        if fs:
            low,high=span(fs[0],point,pinaxis);ck(stem+' complete pin spans the receiving eye',vol(Part.makeCylinder(6.35,high-low,point+pinaxis*low,pinaxis).cut(pin))<1e-5)
        face=point+axis*44.45;area=bearing(fork,nut,face,axis)
        ck(stem+' true socket and nut bearing',abs(area-math.pi*(12.7**2-9.625**2))<1e-5,bearing_mm2=area)
        ck(stem+' full insertion and nut coverage',vol(Part.makeCylinder(9.525,38.1,face-axis*19.05,axis).cut(rod))<1e-4 and bool(cyl(fork,face,axis,9.625)))
        ck(stem+' all real joint materials clear',all(vol(q.common(t))<1e-5 for q,t in [(fork,receiver),(fork,pin),(fork,cotter),(pin,cotter),(nut,rod),(fork,rod),(pin,receiver)]))
        lifted=nut.copy();lifted.translate(axis*.2);ck(stem+' lifted nut loses seating',bearing(lifted,fork,face,axis)<1e-6)
        moved=pin.copy();moved.translate(X*3);ck(stem+' displaced pin intersects receiver',vol(moved.common(receiver))>1)
ck('Accepted intermediate clutch frame and material unchanged',s.rows['PortClutchIntermediateRocker']['frame']==parent.rows['PortClutchIntermediateRocker']['frame'] and s.rows['PortClutchIntermediateRocker']['definition'] not in r['changed_definitions'])
# Low-speed knees: three actual receiving eyes, source-counted washer and full pin.
expected_sources={'Def_DriverLowSuspension_M760':'SNL:119:033','Def_DriverLowConnecting_M762':'SNL:119:035','Def_DriverLowBrake_M763':'SNL:119:030','Def_DriverLowSuspensionPin_M761':'SNL:137:020','Def_DriverLowLinkWasher_SH220A':'SNL:272:001','Def_DriverLowSuspensionKeeper':'SNL:141:010','Def_DriverLowFrontRod_M574':'SNL:195:011'}
for key,source in expected_sources.items():ck(key+' actual source binding',source in json.loads(s.manifest['definitions'][key]['properties']['SourceRecords']))
ck('Two occurrences share each source low-speed part definition',all(sum(v['definition']==key for v in s.rows.values())==2 for key in expected_sources))
fd=d['foundation'];rear=V(*fd['shafts']['Swing']['center_world_mm'])
ck('Actual M763 receiver replaces the provisional low datum',(V(*d['low_speed']['Port']['rod_pin_world_mm'])-V(*fd['future_low_pin_world_mm'])).Length<1e-7)
landmarks=read(H/'transmission_controls_study/driver_redo01/low_source_landmarks01.json')
for key,offset in [('M784_short_pin',c['swing_front_eye']),('M784_long_pin',c['swing_rear_eye']),('M761_axis',c['low_knee_relative']),('M763_long_pin',c['low_rod_relative'])]:
    ck(key+' preserves reviewed eye identity within source pick allowance',(V(*offset)-V(*landmarks['inferred_offsets_from_M783_mm'][key])).Length<2.,construction_not_holdout=True)
for side,record in d['low_speed'].items():
    stem=side+'DriverLow';base=V(*record['base_world_mm']);knee=V(*record['knee_world_mm']);end=V(*record['rod_pin_world_mm']);susp=s.world(stem+'Suspension');conn=s.world(stem+'Connecting');brake=s.world(stem+'Brake');pin=s.world(stem+'Pin');washer=s.world(stem+'Washer');keeper=s.world(stem+'Keeper')
    fs=cyl(susp,base,Y,12.85)
    ck(stem+' actual M783 journal and complete retained shaft',len(fs)==1 and abs(fs[0].Area-2*math.pi*12.85*32)<1e-5 and vol(Part.makeCylinder(12.7,32,base-Y*16,Y).cut(s.world('DriverSwingShaft')))<1e-5 and vol(susp.common(s.world('DriverSwingShaft')))<1e-5)
    ck(stem+' drilled radial oil passage',bool(cyl(susp,base,Z,1.5)) and vol(susp.common(Part.makeCylinder(1.5,26,base,Z)))<1e-5)
    for name,q,width in [('M760',susp,16.),('M762',conn,10.),('M763',brake,12.7)]:
        fs=cyl(q,knee,Y,9.625)
        ck(stem+' '+name+' full common knee bore',len(fs)==1 and abs(fs[0].Area-2*math.pi*9.625*width)<1e-5)
    ck(stem+' full M761 pin through every eye and washer',bool(cyl(pin,knee,Y,9.525)) and vol(Part.makeCylinder(9.525,20.9-c['pin_head_seat_y'],knee+Y*c['pin_head_seat_y'],Y).cut(pin))<1e-5)
    ck(stem+' full estimated M761 stock length',abs(s.definition('Def_DriverLowSuspensionPin_M761').BoundBox.YMax-c['pin_head_seat_y']-57.15)<1e-7)
    head=knee+Y*c['pin_head_seat_y'];seat=knee+Y*c['washer_seat_y']
    head_area=bearing(pin,conn,head,Y);washer_area=bearing(washer,conn,seat,Y)
    ck(stem+' actual pin head bearing on M762',abs(head_area-math.pi*(14**2-9.625**2))<1e-5,bearing_mm2=head_area)
    ck(stem+' complete SH220A washer bearing on M762',abs(washer_area-math.pi*(15**2-9.625**2))<1e-5,bearing_mm2=washer_area)
    lifted=washer.copy();lifted.translate(Y*.2);ck(stem+' lifted washer loses bearing',bearing(lifted,conn,seat,Y)<1e-6)
    moved=pin.copy();moved.translate(X*3);ck(stem+' displaced suspension pin collides',vol(moved.common(susp))>1)
    point=knee+Y*c['pin_keeper_y'];ck(stem+' actual transverse M761 keeper drilling',bool(cyl(pin,point,X,2.5)) and vol(pin.common(Part.makeCylinder(2.5,21.05,point-X*10.525,X)))<1e-5)
    kc=c['low_keeper'];kd=d['low_parts']['keeper'];half=kc['cotter_center_spacing']/2;wire=(kc['cotter_diameter']-kc['cotter_center_spacing'])/2;head=-kc['crown_radius']-kc['cotter_head_gap'];bend=kc['crown_radius']+kc['cotter_exit_gap'];angle=math.radians(kc['cotter_bend_angle']);arc=kc['cotter_bend_radius']*angle;straight=bend-head;tail=31.75-straight-arc
    for sign in [-1,1]:
        start=point+X*head+Z*(sign*half);bend_end=point+X*(bend+kc['cotter_bend_radius']*math.sin(angle))+Z*(sign*(half+kc['cotter_bend_radius']*(1-math.cos(angle))));direction=X*math.cos(angle)+Z*(sign*math.sin(angle))
        ck(stem+' keeper full source leg '+str(sign),abs(kd['total_leg_centerline_mm']-31.75)<1e-7 and vol(Part.makeCylinder(wire,straight,start,X).cut(keeper))<1e-5 and vol(Part.makeCylinder(wire,tail,bend_end,direction).cut(keeper))<1e-5)
    ck(stem+' all knee materials clear',all(vol(q.common(t))<1e-5 for i,q in enumerate([susp,conn,brake,pin,washer,keeper]) for t in [susp,conn,brake,pin,washer,keeper][i+1:]))
    selector=V(*record['open_selector_connection_world_mm']);fs=cyl(conn,selector,Y,6.5)
    ck(stem+' actual open M762 front eye; selector connection unfinished',len(fs)==1 and abs(fs[0].Area-2*math.pi*6.5*10)<1e-5,unqualified_interface='No selector or front joint added in this increment')
    rod=s.world(stem+'Rod');start=V(*record['stock_start_world_mm']);axis=V(*record['axis_world']);length=49.5*25.4;core=Part.makeCylinder(9.525,length,start,axis)
    ck(stem+' complete printed M574 stock with true receiver closure',abs(record['stock_length_mm']-length)<1e-7 and abs(record['pin_span_mm']-length-50.8)<1e-7 and vol(core.cut(rod))<1e-5 and vol(rod.cut(core))<1e-5)
    for joint in record['endpoints']:
        js=joint['stem'];receiver=s.world(joint['receiver']);fork=s.world(js+'Fork');jp=s.world(js+'Pin');nut=s.world(js+'Nut');cotter=s.world(js+'Cotter');jf=pose(s.rows[js+'Fork']['frame']);point=jf.Base;axis=jf.Rotation.multVec(X);pinaxis=jf.Rotation.multVec(Y);fs=cyl(receiver,point,pinaxis,6.5)
        ck(js+' actual coaxial receiver and M568C pin',len(fs)==1 and bool(cyl(jp,point,pinaxis,6.35)) and s.manifest['definitions'][s.rows[js+'Pin']['definition']]['properties']['SourcePartMark']=='M568C')
        if fs:
            low,high=span(fs[0],point,pinaxis);ck(js+' complete receiver pin stock',vol(Part.makeCylinder(6.35,high-low,point+pinaxis*low,pinaxis).cut(jp))<1e-5)
        face=point+axis*44.45;area=bearing(fork,nut,face,axis)
        ck(js+' real socket and nut bearing',abs(area-math.pi*(12.7**2-9.625**2))<1e-5)
        ck(js+' complete rod insertion through nut',vol(Part.makeCylinder(9.525,38.1,face-axis*19.05,axis).cut(rod))<1e-4 and bool(cyl(fork,face,axis,9.625)))
        ck(js+' all complete joint materials clear',all(vol(q.common(t))<1e-5 for q,t in [(fork,receiver),(fork,jp),(fork,cotter),(jp,cotter),(nut,rod),(fork,rod),(jp,receiver)]))
        lifted=nut.copy();lifted.translate(axis*.2);ck(js+' lifted nut loses bearing',bearing(lifted,fork,face,axis)<1e-6)
    n=side+'LowIntermediateRocker';ck(side+' inherited low intermediate receiver preserved',s.rows[n]['frame']==parent.rows[n]['frame'] and s.rows[n]['definition'] not in r['changed_definitions'])
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),foundation_checker_sha256=sha(H/'check_driver_foundation_interfaces.py'),scope='Complete saved low-speed hanging linkage and M574 stock, corrected M784 eyes, real M761 retention and full inherited clutch chain. M762 front coupling, historical profiles/stack/pose, seat and other driver mechanisms remain unqualified.')
write(out/'independent_checks.json',result);print(len(checks),'checks;',result['passed'],flush=True)
for v in checks:
    if not v['passed']:print(v,flush=True)
assert result['passed']
