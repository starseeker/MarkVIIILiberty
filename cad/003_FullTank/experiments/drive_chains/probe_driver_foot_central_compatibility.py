"""Compare two unintegrated foot-control hypotheses and the rigid-transform repair."""
from types import SimpleNamespace
from control_rebuild_io_v2 import *
from lib.visual_review import shaded
from lib.cad_build import COLORS
N=H/'driver_foot_reverse_study';central=Saved(N/'central03');profile=Saved(N/'profile03');old=Saved(N/'central02')
out=N/'central_compatibility01';out.mkdir(exist_ok=False)
assert central.report['parent_native_sha256']==profile.report['parent_native_sha256']==old.report['parent_native_sha256']
def volume(q):return sum(abs(s.Volume) for s in q.Solids)
pairs=[]
for name in profile.report['new_occurrences']:
    p=profile.world(name)
    for other in central.report['new_occurrences']:
        q=central.world(other)
        overlap=p.common(q);v=volume(overlap)
        pairs.append(dict(profile=name,central=other,intersection_mm3=v,minimum_distance_mm=p.distToShape(q)[0],intersects=v>1e-5))
before=old.world('DriverBrakePedal');after=central.world('DriverBrakePedal')
repair=dict(old_native_sha256=sha(old.native),missing_mm3=volume(before.cut(after)),added_mm3=volume(after.cut(before)),
    old_surface_types=sorted({type(f.Surface).__name__ for f in before.Faces}),new_surface_types=sorted({type(f.Surface).__name__ for f in after.Faces}))
COLORS.update(CentralStudy=(.63,.42,.22),ProfileStudy=(.32,.54,.68),Shafts=(.45,.48,.51))
items=[]
for source,names,system in [(central,list(central.rows),'CentralStudy'),(profile,profile.report['new_occurrences'],'ProfileStudy')]:
    for name in names:
        key=source.rows[name]['definition']
        items.append(dict(id=name,definition=key,shape=source.world(name),target=SimpleNamespace(Shape=source.definition(key)),system='Shafts' if name.endswith('Shaft') else system,representation='assembly'))
shaded(items,out/'combined_hypotheses.svg',(-1,-1,.7),'Unintegrated foot-control studies | brown central group; blue M769 hypothesis | output links incomplete')
result=dict(central_native_sha256=sha(central.native),profile_native_sha256=sha(profile.native),worker_sha256=sha(Path(__file__)),pairs=pairs,
    findings=[p for p in pairs if p['intersects']],rigid_representation_repair=repair,
    geometry_integrated=False,mechanism_connectivity_qualified=False,
    scope='All twenty cross-study material pairs; minimum distances do not establish intended joints. Analytic rigid-placement repair compared with preceding spline-converted pedal.',
    images={'combined_hypotheses.png':sha(out/'combined_hypotheses.png')})
write(out/'report.json',result);print('Cross-study pairs',len(pairs),'intersections',len(result['findings']),'repair',repair,flush=True)
