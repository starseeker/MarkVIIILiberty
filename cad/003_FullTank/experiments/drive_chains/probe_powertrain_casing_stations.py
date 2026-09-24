"""Check local casing regeneration at the two separately solved source-axis alternatives."""
import argparse
import copy
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
STAGE=HERE.parents[1]
ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json')
assert sha(out/r['native_file'])==r['native_sha256']
stations_path=HERE/'engine_pump_receiver_study/registration/station_candidates.json'
stations=read(stations_path)

import FreeCAD as App
import Part
from powertrain_casing_registration_parts import reconstruct
from casing_mount_parts import cutter
V=App.Vector
path=out/'baseline_shapes/standard_bulkhead.brep'
assert sha(path)==r['baseline_brep_hashes'][path.name]
wall=Part.Shape();wall.read(str(path))
results={}
for key in ['transmission_axis','engine_axis']:
    selected=stations['candidates'][key];assert selected['mathematical_checks_passed']
    route=copy.deepcopy(r['revised_route'])
    route['candidate_transmission_axis_xz_mm']=selected['transmission_axis_xz_mm']
    shapes,poses,trim,details=reconstruct(r['controls'],route,wall,r['centers'],r['support_joints'],r['big_hub_radius_mm'],r['small_hub_radius_mm'])
    checks=[]
    def ck(name,passed,**detail):checks.append(dict(name=name,passed=bool(passed),**detail))
    for name,s in shapes.items():
        ck(name+' topology and kernel tolerance',s.isValid() and len(s.Solids)==1 and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
    body,cap=shapes['Def_Casing_body'],shapes['Def_Casing_cap']
    c=r['controls']['casing'];cp=r['controls']['cap'];wc=r['controls']['mount']
    ck('cap/body split',abs(body.distToShape(cap)[0]-c['cap_split_gap'])<1e-6)
    for s in details['cap_stations']['rivets']:
        receivers=[shapes['Def_CapJoint'+s['cleat']],body if s['owner']=='Body' else cap]
        if s.get('packing'):receivers.append(shapes['Def_CapJoint'+s['packing']])
        tool=cutter(s,cp['rivet_diameter']+cp['hole_diameter_clearance'])
        residual=sum(one.common(tool).Volume for one in receivers)
        ck(s['name']+' complete bores',abs(residual)<1e-5,remaining_mm3=residual)
    for role in ['case','wall']:
        for index,s in enumerate(details['wall_stations'][role]):
            tool=cutter(s,wc[role+'_rivet_diameter']+wc['hole_diameter_clearance'])
            residual=shapes['Def_CasingWallAngle'].common(tool).Volume
            if role=='case':residual+=body.common(tool).Volume
            else:
                tool.translate(V(0,r['centers']['Port'],0))
                residual+=shapes['Def_hull_engine_back'].common(tool).Volume
            ck(role+' rivet '+str(index)+' complete bores',abs(residual)<1e-5,remaining_mm3=residual)
    ck('134 joint frames regenerated',len(poses)==134)
    ck('Taper retains normal sheet stock',all(v['passed'] for v in details['taper_report']['sheet_thickness_checks']))
    big=route['roller_pinion_axis_xz_mm'];small=route['candidate_transmission_axis_xz_mm']
    radii=[route['pitch_mm']/(2*math.sin(math.pi/route[k]))+c['chain_radial_envelope']+c['radial_gap']+c['sheet_stock'] for k in ['large_teeth','small_teeth']]
    dx,dz=small[0]-big[0],small[1]-big[1];d=math.hypot(dx,dz);q=(radii[0]-radii[1])/d
    for sign in [1,-1]:
        nx,nz=q*dx/d-sign*math.sqrt(1-q*q)*dz/d,q*dz/d+sign*math.sqrt(1-q*q)*dx/d
        x=1200;z=big[1]+(radii[0]-nx*(x-big[0]))/nz
        point,normal=V(x,0,z),V(nx,0,nz)
        lengths=[edge.Length for edge in body.common(Part.makeLine(point+normal,point-normal*(c['sheet_stock']+1))).Edges]
        ck('Normal shell stock '+str(sign),len(lengths)==1 and abs(lengths[0]-c['sheet_stock'])<1e-6,lengths_mm=lengths)
    folder=out/'parameter_trials'/key;folder.mkdir(parents=True,exist_ok=True)
    for name,shape in shapes.items():shape.exportBrep(str(folder/(name+'.brep')))
    record=dict(passed=all(v['passed'] for v in checks),checks=checks,axis_xz_mm=small,
                dimensions=details,poses={name:list(p.toMatrix().A) for name,p in poses.items()},
                brep_hashes={f.name:sha(f) for f in folder.glob('*.brep')})
    write(folder/'checks.json',record);results[key]=record
    print(key,len(checks),'local checks',record['passed'],flush=True)
write(out/'parameter_checks.json',dict(passed=all(v['passed'] for v in results.values()),
    native_sha256=r['native_sha256'],probe_sha256=sha(Path(__file__)),builder_report_sha256=sha(out/'report.json'),
    stations_sha256=sha(stations_path),variants=results,
    scope='Local casing stock, opening and joint regeneration at the two solved alternative source-axis stations. No variant whole-assembly collision, chain-route, exchange or historical qualification.',
    installation_qualified=False))
assert all(v['passed'] for v in results.values())
