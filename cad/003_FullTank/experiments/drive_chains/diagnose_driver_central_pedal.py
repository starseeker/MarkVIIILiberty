"""Retain diagnostics for rigid surface conversion and endpoint witnesses."""
from collections import Counter
import math
from control_rebuild_io_v2 import *
N=H/'driver_foot_reverse_study';s=Saved(N/'central02');d=s.report['details'];c=d['controls']
out=N/'central_diagnostics01';out.mkdir(exist_ok=False)
V=App.Vector;Y=V(0,1,0);Z=V(0,0,1)
q=s.definition('Def_DriverBrakePedal_M764A');rot=App.Rotation(Y,c['pedal_long_axis_deg'])
result=dict(native_sha256=sha(s.native),worker_sha256=sha(Path(__file__)),surface_types=dict(Counter(type(f.Surface).__name__ for f in q.Faces)),transform_shape_doc=Part.Shape.transformShape.__doc__)
back=q.transformGeometry(rot.toMatrix())
result['inverse_geometry_transform']=dict(bounds=[back.BoundBox.XMin,back.BoundBox.XMax],vertices=[min(v.Point.x for v in back.Vertexes),max(v.Point.x for v in back.Vertexes)])
box=Part.makeBox(10,20,30);m=App.Rotation(Y,20).toMatrix();cases={}
for copy in [False,True]:
    a=box.copy();a.transformShape(m,False,copy)
    cases[str(copy)]=dict(identity=a.Placement.isIdentity(),surfaces=dict(Counter(type(f.Surface).__name__ for f in a.Faces)),volume=a.Volume)
result['transform_shape_probe']=cases
cp=s.definition('Def_DriverBrakeBridleCotter');conf=d['rear_hardware_controls']['cotter'];head=-conf['crown_radius']-conf['cotter_head_gap'];bend=conf['crown_radius']+conf['cotter_exit_gap'];r=conf['cotter_bend_radius'];ang=math.radians(conf['cotter_bend_angle']);half=conf['cotter_center_spacing']/2
tail=38.1-(bend-head)-r*ang;rz=App.Rotation(Z,-90);rows=[]
for sign in [-1,1]:
    start=V(0,head,sign*half);corner=V(0,bend+r*math.sin(ang),sign*(half+r*(1-math.cos(ang))));end=corner+V(0,math.cos(ang),sign*math.sin(ang))*tail
    points=[('start',start),('start_interior',start+Y*.2),('bend',V(0,bend,sign*half)),('arc_end',corner),('end',end),('end_interior',end-V(0,math.cos(ang),sign*math.sin(ang))*.2)]
    for name,point in points:
        w=Part.makeSphere(.15,rz.multVec(point));rows.append(dict(sign=sign,station=name,point=list(rz.multVec(point)),missing_mm3=sum(abs(x.Volume) for x in w.cut(cp).Solids)))
result['cotter_witnesses']=rows
write(out/'report.json',result);print(result,flush=True)
