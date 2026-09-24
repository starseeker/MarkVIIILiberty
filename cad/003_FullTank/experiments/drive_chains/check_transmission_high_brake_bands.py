"""Independent saved-artifact checks for partial high-speed brake bands."""
import argparse,math
from pathlib import Path
import sys
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
source=ROOT/r['source_native'];old=read(source.parent/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256'] and sha(source)==r['source_native_sha256']==old['native_sha256']
c=r['controls'];rows={v['name']:v for v in m['occurrences']};prior={v['name']:v for v in old['occurrences']}
checks=[];cache={};world={};V=App.Vector
def ck(name,passed,**details):checks.append(dict(name=name,passed=bool(passed),**details))
for key,d in m['definitions'].items():
    assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[key]=s
for name,row in rows.items():
    s=cache[row['definition']].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));world[name]=s
new={hand+'HighSpeedBrake'+role+leaf for hand in ['Port','Starboard'] for role in ['Long','Short'] for leaf in ['Band','Lining']}
ck('Eight added leaves, four definitions, seven owned assemblies',set(rows)-set(prior)==new and len(rows)==len(prior)+8 and len(m['definitions'])==len(old['definitions'])+4 and len(m['assemblies'])==len(old['assemblies'])+7)
ck('Every inherited occurrence preserves definition, frame and owners',all(v['definition']==prior[n]['definition'] and v['owners']==prior[n]['owners'] and max(abs(x-y) for x,y in zip(v['frame'],prior[n]['frame']))<1e-7 for n,v in rows.items() if n in prior))
for name,g in old['assemblies'].items():
    extra=['TransmissionHighSpeedBrakes'] if name=='Root' else ['Def_HighBrake_'+role+'_'+leaf for role in ['long','short'] for leaf in ['band','lining']] if name=='Definitions' else []
    now=m['assemblies'][name]
    ck('Retained assembly '+name,sorted(now['children'])==sorted(g['children']+extra) and max(abs(x-y) for x,y in zip(now['world'],g['world']))<1e-7)
neutral=c['inner_radius']+c['lining_stock']/2
for role,holes_expected in [('long',12),('short',6)]:
    for leaf in ['lining','band']:
        key='Def_HighBrake_'+role+'_'+leaf;s=cache[key]
        ck(key+' valid closed identity solid',s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.Placement.isIdentity() and s.getTolerance(1)<1e-4)
        b=s.optimalBoundingBox(False,False);ck(key+' actual source axial width',abs(b.YLength-47.625)<1e-5,width_mm=b.YLength)
    lining=cache['Def_HighBrake_'+role+'_lining'];band=cache['Def_HighBrake_'+role+'_band']
    ro=c['inner_radius']+c['lining_stock']
    # The uninterrupted circular edge at an axial side measures the actual sweep.
    arcs=[e for e in lining.Edges if isinstance(e.Curve,Part.Circle) and abs(e.Curve.Radius-ro)<1e-6 and abs(e.Curve.Center.y+c['width']/2)<1e-6]
    flat=sum(e.Length/ro*neutral for e in arcs)
    required=695.325 if role=='long' else 346.075
    ck(role+' source flat length from saved circular edge',abs(flat-required)<1e-4,measured_mm=flat)
    cylinders=[f for f in lining.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-7.14375/2)<1e-6]
    ck(role+' source hole count/diameter',len(cylinders)==holes_expected,actual_count=len(cylinders))
    cones=[f for f in lining.Faces if isinstance(f.Surface,Part.Cone)]
    # OCCT uses a signed cone half-angle: radius decreases along our outward axis.
    ck(role+' source countersink angle and opening direction',len(cones)==holes_expected and all(abs(math.degrees(f.Surface.SemiAngle)+35)<1e-6 and f.Surface.Axis.dot(V(f.Surface.Center.x,0,f.Surface.Center.z).normalize())>.999999 for f in cones),signed_half_angles_deg=[math.degrees(f.Surface.SemiAngle) for f in cones])
    for group in range(2 if role=='long' else 1):
        for n in range(6):
            along=group*(695.325-346.075)+38.1+n*53.975;theta=along/neutral
            direction=V(math.cos(theta),0,math.sin(theta));y=(-1 if n%2==0 else 1)*(47.625/2-12.7)
            origin=direction*(190.5-1)+V(0,y,0)
            witness=Part.makeCylinder(3.45,8.35,origin,direction)
            ck(role+f' hole {group}:{n} independent through void',abs(lining.common(witness).Volume)<1e-5)
    env=Part.makeCylinder(ro+c['steel_stock'],c['width'],V(0,-c['width']/2,0),V(0,1,0))
    inner=Part.makeCylinder(ro,c['width'],V(0,-c['width']/2,0),V(0,1,0))
    ck(role+' band stock remains in its annular envelope',abs(band.cut(env).Volume)<1e-5 and abs(band.common(inner).Volume)<1e-5)
coverage=[]
for hand,sign in [('Port',1),('Starboard',-1)]:
    drum=world[hand+'TransmissionCore_high_drum'];face=next(f for f in drum.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-190.5)<1e-6)
    db=face.optimalBoundingBox(False,False)
    for role in ['Long','Short']:
        lining=world[hand+'HighSpeedBrake'+role+'Lining'];band=world[hand+'HighSpeedBrake'+role+'Band']
        lb=lining.optimalBoundingBox(False,False)
        width=max(0,min(db.YMax,lb.YMax)-max(db.YMin,lb.YMin))
        distance=lining.distToShape(drum)[0]
        ck(hand+role+' cylindrical contact and retained axial overlap',distance<1e-5 and width/47.625>.97 and lining.common(drum).Volume<1e-5,axial_overlap_mm=width,coverage_fraction=width/47.625)
        ck(hand+role+' lining meets separate backing',lining.distToShape(band)[0]<1e-5 and abs(lining.common(band).Volume)<1e-5)
        coverage.append(dict(hand=hand,role=role,axial_overlap_fraction=width/47.625,inner_edge_overhang_mm=max(0,db.YMin-lb.YMin),outer_edge_overhang_mm=max(0,lb.YMax-db.YMax)))
        row=rows[hand+'HighSpeedBrake'+role+'Lining'];expected=['Root','TransmissionHighSpeedBrakes',hand+'HighSpeedBrake',hand+'HighSpeedBrake'+role+'Assembly']
        ck(hand+role+' hierarchy owners',row['owners']==expected and rows[hand+'HighSpeedBrake'+role+'Band']['owners']==expected)
pairs=set();collisions=[];invalid=[]
for name in new:
    for other,s in world.items():
        if name!=other and world[name].BoundBox.intersect(s.BoundBox):pairs.add(tuple(sorted([name,other])))
for left,right in sorted(pairs):
    common=world[left].common(world[right]);volume=sum(abs(v.Volume) for v in common.Solids)
    if not common.isValid():invalid.append([left,right])
    if volume>1e-5:collisions.append(dict(left=left,right=right,volume_mm3=volume))
ck('No development material interference or invalid intersections',not collisions and not invalid,pairs=len(pairs),collisions=collisions,invalid=invalid)
result=dict(passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],checker_sha256=sha(Path(__file__)),checks=checks,development_pairs=len(pairs),axial_coverage=coverage,
    scope='Preliminary saved stock, holes, frames, contact distance/axial overlap and development interference. Full face coverage, hardware, preservation, STEP, reproduction, variation and historical/source qualification pending.',packet_complete=False,installation_qualified=False,standard_modified=False)
write(out/'independent_checks.json',result)
print('Checks',len(checks),'pairs',len(pairs),'passed',result['passed'],flush=True)
for v in checks:
    if not v['passed']:print(v,flush=True)
assert result['passed']
