"""Independent saved-material checks for high selectors and four complete rod connections."""
import argparse,math,json
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0)
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);r=s.report;d=r['details'];c=d['high_selector_controls'];parent=Saved((ROOT/r['parent_native']).parent);out=s.folder/'checks03';out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest);assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
checks=[]
def ck(name,ok,**kw):
    checks.append(dict(name=name,passed=bool(ok),**kw));write(out/'progress.json',checks)
    if not ok:print('FAIL',name,kw,flush=True)
def vol(q):return sum(abs(v.Volume) for v in q.Solids)
def same(q,t):return vol(q.cut(t))<1e-5 and vol(t.cut(q))<1e-5 and not q.cut(t,1e-4).Faces and not t.cut(q,1e-4).Faces
def cyl(q,p,axis,radius):return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-p).cross(axis).Length<1e-6]
def planes(q,p,axis):return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.Surface.Axis.cross(axis).Length<1e-7 and abs((f.CenterOfMass-p).dot(axis))<1e-6]
def bearing(q,t,p,axis):return sum(f.common(g).Area for f in planes(q,p,axis) for g in planes(t,p,axis))
def moved(q,v):t=q.copy();t.translate(v);return t
def block(a,b,halfwidth,stock):
    axis=b-a;axis.normalize();n=V(-axis.z,0,axis.x)*halfwidth;points=[a+n-Y*stock/2,b+n-Y*stock/2,b-n-Y*stock/2,a-n-Y*stock/2]
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(Y*stock)
ck('38 physical additions, three definitions, no inherited revisions',len(r['new_occurrences'])==38 and len(r['new_definitions'])==3 and not r['changed_definitions'] and len(s.rows)==140)
for key in s.manifest['definitions']:
    q=s.definition(key);ck(key+' canonical closed solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions']:ck(key+' inherited complete material preserved',same(q,parent.definition(key)))
for name,row in s.rows.items():
    ck(name+' saved world frame',max(abs(a-b) for a,b in zip(row['frame'],r['specs'][name]['frame']))<1e-7)
    if name in parent.rows:ck(name+' inherited definition and world frame',row['definition']==parent.rows[name]['definition'] and max(abs(a-b) for a,b in zip(row['frame'],parent.rows[name]['frame']))<1e-7)
ck('M789A literal source length binding',json.loads(s.manifest['definitions']['Def_DriverFrontShortRod_M789A']['properties']['SourceRecords'])==['SNL:194:028'])
ck('Three M576 applications share one preserved definition',all(s.rows[name]['definition']=='Def_DriverClutchFrontRod_M576' for name in ['DriverClutchFrontRod','PortDriverHighFrontRod','StarboardDriverHighFrontRod']))
layout=read(ROOT/c['layout']);coef=complex(*layout['registration']['complex_scale']);main=V(*d['foundation']['shafts']['Main']['center_world_mm']);source=layout['source_high_eye_px'];shaft=s.world('DriverMainShaft')
for side,sign,mark,rowid in [('Port',1,'M759','SNL:117:025'),('Starboard',-1,'M758','SNL:117:026')]:
    stem=side+'DriverHigh';record=d['high_controls'][side];pivot=V(*record['pivot_world_mm']);eye=V(*record['bell_pin_world_mm']);lever=s.world(stem+'Selector');entry=s.manifest['definitions'][s.rows[stem+'Selector']['definition']]
    ck(stem+' source handed identity',entry['properties']['SourcePartMark']==mark and rowid in json.loads(entry['properties']['SourceRecords']))
    fs=cyl(lever,pivot,Y,19.1619);ck(stem+' actual main-shaft journal and full stock span',bool(fs) and all(abs(max((v.Point-pivot).y for v in f.Vertexes)-min((v.Point-pivot).y for v in f.Vertexes)-24)<1e-6 for f in fs) and vol(Part.makeCylinder(19.0119,24,pivot-Y*12,Y).cut(shaft))<1e-5 and vol(lever.common(shaft))<1e-5)
    hub=Part.makeCylinder(32,24,pivot-Y*12,Y).cut(Part.makeCylinder(19.1619,26,pivot-Y*13,Y)).cut(Part.makeCylinder(1.5,34,pivot,-X));ck(stem+' full bearing stock and radial oil opening',vol(hub.cut(lever))<1e-5 and bool(cyl(lever,pivot,X,1.5)))
    fs=cyl(lever,eye,Y,6.5);ck(stem+' full lower receiving bore',len(fs)==1 and abs(fs[0].Area-2*math.pi*6.5*12.7)<1e-5)
    annulus=Part.makeCylinder(16,12.7,eye-Y*6.35,Y).cut(Part.makeCylinder(6.5,14.7,eye-Y*7.35,Y));ck(stem+' complete eye wall',vol(annulus.cut(lever))<1e-5)
    # Measure the saved bore position against the unchanged source construction pick.
    p=fs[0].Surface.Center;pixel=complex(315,322)+coef*complex(-(p.x-main.x),-(p.z-main.z));residual=abs(pixel-complex(*source))
    ck(stem+' source discrepancy explicitly retained, not hidden',abs(residual-layout['construction_discrepancy_px'])<1e-6 and residual>layout['source_pick_uncertainty_px'],residual_px=residual,historical_geometry_qualified=False)
    direct=V(*c['selector_gate_direction']);n=V(-direct.z,0,direct.x);y0,y1=sorted([sign*(c['selector_web_stock']/2+.5),sign*(c['selector_gate_outward_depth']-.5)]);middle=(y0+y1)/2
    gate=block(pivot+direct*153.2+Y*middle,pivot+direct*196.8+Y*middle,15.5,y1-y0);ck(stem+' actual open selector jaw',vol(gate.common(lever))<1e-5 and gate.Volume>20000)
    for a,b in [(140.5,152.2),(197.8,209.5)]:ck(stem+' full jaw lip '+str(a),vol(block(pivot+direct*a+Y*middle,pivot+direct*b+Y*middle,15.5,y1-y0).cut(lever))<1e-5)
    low=s.world(side+'DriverLowSelector');ck(stem+' paired selector stocks clear in chosen static pose',vol(lever.common(low))<1e-5 and lever.distToShape(low)[0]>.1,minimum_distance_mm=lever.distToShape(low)[0])
    for kind,v in record['rods'].items():
        rod=s.world(v['occurrence']);start=V(*v['stock_start_world_mm']);axis=V(*v['axis_world']);length=v['stock_length_mm'];core=Part.makeCylinder(9.525,length,start,axis)
        ck(stem+kind+' complete full-diameter rod stock',same(rod,core) and len(rod.Solids)==1)
        ck(stem+kind+' real pin-span closure',abs(v['pin_span_mm']-length-50.8)<1e-7)
        if kind=='Short':ck(stem+' exact printed10-5/8in M789A stock',abs(length-269.875)<1e-7)
        else:ck(stem+' exact shared M576 stock length',abs(length-d['rods']['Front']['stock_length_mm'])<1e-7 and s.rows[v['occurrence']]['definition']==s.rows['DriverClutchFrontRod']['definition'])
        for joint in v['endpoints']:
            js=joint['stem'];receiver=s.world(joint['receiver']);fork=s.world(js+'Fork');pin=s.world(js+'Pin');cotter=s.world(js+'Cotter');nut=s.world(js+'Nut');frame=pose(s.rows[js+'Fork']['frame']);point=frame.Base;rodaxis=frame.Rotation.multVec(X);pinaxis=frame.Rotation.multVec(Y)
            fs=cyl(receiver,point,pinaxis,6.5)
            ck(js+' actual coaxial receiving bore and source M568C pin',len(fs)==1 and bool(cyl(pin,point,pinaxis,6.35)) and s.manifest['definitions'][s.rows[js+'Pin']['definition']]['properties']['SourcePartMark']=='M568C')
            if fs:
                vals=[(vert.Point-point).dot(pinaxis) for vert in fs[0].Vertexes];lo,hi=min(vals),max(vals);ck(js+' complete pin spans receiving eye',vol(Part.makeCylinder(6.35,hi-lo,point+pinaxis*lo,pinaxis).cut(pin))<1e-5)
            # Reused complete pin/cotter definitions retain source stock; actual
            # installed materials and receiver axes must still fit this joint.
            for role in ['Fork','Pin','Cotter','Nut']:ck(js+role+' uses preserved physical definition',s.rows[js+role]['definition']==parent.rows['PortTrackBrakeJoint'+role]['definition'])
            face=point+rodaxis*44.45;area=bearing(fork,nut,face,rodaxis)
            ck(js+' full nut/socket bearing',abs(area-math.pi*(12.7**2-9.625**2))<1e-5,bearing_mm2=area)
            ck(js+' complete rod insertion and nut stock coverage',vol(Part.makeCylinder(9.525,38.1,face-rodaxis*19.05,rodaxis).cut(rod))<1e-4 and bool(cyl(fork,face,rodaxis,9.625)))
            ck(js+' all complete joint materials clear',all(vol(q.common(t))<1e-5 for q,t in [(fork,receiver),(fork,pin),(fork,cotter),(pin,cotter),(nut,rod),(fork,rod),(pin,receiver),(nut,pin),(nut,cotter)]))
            ck(js+' lifted nut loses seating',bearing(moved(nut,rodaxis*.2),fork,face,rodaxis)<1e-6)
            ck(js+' displaced pin intersects receiving eye',vol(moved(pin,X*3).common(receiver))>1)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(s.native),manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Actual saved selectors and complete rods/joints; printed stock, preserved shared definitions, source discrepancy and negative controls. No historical shape or motion qualification.')
write(out/'independent_checks.json',result);print('High controls',len(checks),'checks; passed',result['passed'],flush=True);assert result['passed']
