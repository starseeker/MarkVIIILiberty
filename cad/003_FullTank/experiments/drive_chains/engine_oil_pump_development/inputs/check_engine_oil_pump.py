"""Independently inspect saved oil-pump hierarchy, material and bore networks."""
import argparse,itertools,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import sha,read,write
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'native_check.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    V=App.Vector;r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256'];doc=App.openDocument(str(native));c=r['controls'];d=r['datums'];checks=[];pairs=[]
    def check(name,passed,**kw):
        checks.append(dict(name=name,passed=bool(passed),**kw));write(out/'native_progress.json',dict(checks=checks,material_pairs=pairs));print(name,passed,flush=True)
    shapes={};defs={k:doc.getObject('Def_'+k).Shape for k in r['definition_order']}
    for k,s in defs.items():check('definition_'+k,s.isValid() and len(s.Solids)==1 and s.Volume>0,solids=len(s.Solids),faces=len(s.Faces),max_tolerance_mm=s.getTolerance(1))
    for row in r['occurrences']:
        link=doc.getObject(row['name']);parent=doc.getObject(row['assembly']);pl=parent.getGlobalPlacement().multiply(link.LinkPlacement);s=link.LinkedObject.Shape.copy();s.Placement=pl.multiply(s.Placement);shapes[row['name']]=s
        expected=App.Placement(V(*row['xyz']),App.Rotation(*row['rotation']));err=max((pl.multVec(v)-expected.multVec(v)).Length for v in [V(),V(13,0,0),V(0,17,5)])
        check('link_'+row['name'],link in parent.Group and link.LinkedObject.Name=='Def_'+row['key'] and err<1e-7,frame_error_mm=err)
    links=[o for o in doc.Objects if o.TypeId=='App::Link'];check('physical_inventory',len(links)==r['physical_count']==len(r['occurrences']),physical_count=len(links))
    for (an,s),(bn,t) in itertools.combinations(shapes.items(),2):
        if not s.BoundBox.intersect(t.BoundBox):continue
        vol=abs(s.common(t).Volume);pairs.append(dict(a=an,b=bn,overlap_mm3=vol,passed=vol<1e-5));write(out/'material_progress.json',pairs)
    check('physical_material',all(x['passed'] for x in pairs),tested_pairs=len(pairs),failures=[x for x in pairs if not x['passed']])
    def tube(points,radius):
        points=[V(*p) for p in points];pieces=[]
        for x,y in zip(points,points[1:]):
            delta=y-x;pieces.append(Part.makeCylinder(radius,delta.Length,x,delta/delta.Length))
        pieces += [Part.makeSphere(radius,point) for point in points[1:-1]]
        return pieces[0].multiFuse(pieces[1:])
    passages={k:tube(points,7. if k=='tank_supply' else c['port_radius']) for k,points in d['passages'].items()}
    allowed={frozenset(['pressure','relief']),frozenset(['common_return','crossover'])}
    for (an,s),(bn,t) in itertools.combinations(passages.items(),2):
        vol=abs(s.common(t).Volume);gap=s.distToShape(t)[0];joins=frozenset([an,bn]) in allowed
        check('passage_'+an+'_'+bn,vol>1 if joins else vol<1e-5 and gap>=c['passage_wall']-1e-6,overlap_mm3=vol,separation_mm=gap,intended_join=joins)
    for name,points in d['passages'].items():
        gauge=tube(points,6.9 if name=='tank_supply' else c['port_radius']-.1);vol=sum(abs(gauge.common(defs[k]).Volume) for k in ['lower_body','upper_body'])
        check('saved_void_'+name,vol<1e-5,casting_overlap_mm3=vol)
    axis=V(*d['drain_seat']);gauge=Part.makeCylinder(c['drain_diameter']/2,30,axis-V(0,0,1));vol=abs(gauge.common(defs['cover']).Volume);flags=[defs['cover'].isInside(axis+V(0,0,z),1e-7,True) for z in [1,4,7]]
    check('saved_drain_bore',vol<1e-5 and not any(flags),gauge_overlap_mm3=vol,axis_material_flags=flags)
    check('source_nominal_gear_fits',abs(c['gear_diametrical_clearance']-.004*25.4)<1e-10 and abs(c['gear_endplay']-.003*25.4)<1e-10)
    for level in ['lower','upper']:
        for index in range(9):
            pitch=360/c['gear_teeth'];angle=pitch*index/8;driver=defs[level+'_driving_gear'].copy();driver.rotate(V(),V(0,0,1),angle)
            for sign in ([-1,1] if level=='upper' else [-1]):
                mate=defs[level+'_idler_gear'].copy();mate.rotate(V(),V(0,0,1),pitch/2-angle);mate.translate(V(0,sign*d['gear_center_spacing'],0));vol=abs(driver.common(mate).Volume)
                check(f'mesh_{level}_{sign}_{index}',vol<1e-5,angle_deg=angle,overlap_mm3=vol)
    # The strainer is porous geometry, not an opaque cylindrical placeholder.
    for level in ['upper','lower']:
        side=defs[level+'_side_screen'];lo,hi=d['strainers']['baskets'][level]['side_span'];z=lo+(hi-lo)/c['screen_height_cells']/2;radius=c['filter_outer_radius']-c['filter_frame_stock'];gauge=Part.makeCylinder(.1,2,V(radius-1,0,z),V(1,0,0));vol=abs(gauge.common(side).Volume)
        check(level+'_screen_aperture',vol<1e-5,material_mm3=vol)
    check('source_assets',all(sha(ROOT/name)==value for name,value in r['source_assets'].items()))
    check('native_unchanged',sha(native)==r['native_sha256'])
    result=dict(passed=all(x['passed'] for x in checks),complete_pump=False,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),checks=checks,material_pairs=pairs,limitations=['Pump-to-crankcase and standard tank fit not yet checked','Hydraulic behavior and true screen mesh not simulated','External fittings, fasteners and lock wires remain pending'])
    write(out/'native_checks.json',result);assert result['passed']
finally:
    runtime.close()
