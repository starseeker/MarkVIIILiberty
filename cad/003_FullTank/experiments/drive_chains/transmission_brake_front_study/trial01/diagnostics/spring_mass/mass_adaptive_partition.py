"""Try adaptive subdivision without changing the integration tolerances."""
from pathlib import Path
import json,sys,math
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty');STAGE=ROOT/'cad/003_FullTank';sys.path.insert(0,str(STAGE))
from lib.mass_properties import AdaptiveMass
mass=AdaptiveMass(Path('runtime-mass'));results={}
for name in ['spring_native','spring_step']:
    s=Part.Shape();s.read(str(ROOT/'.work/transmission-brake-front/mass-gk-probe'/(name+'.brep')))
    b=s.BoundBox;memo={};attempts=[]
    def interval(lo,hi,depth):
        piece=s.common(Part.makeBox(b.XLength+2,b.YLength+2,hi-lo,App.Vector(b.XMin-1,b.YMin-1,lo)))
        measured=mass.measure(piece);attempts.append(dict(interval=[lo,hi],depth=depth,measure=measured))
        if measured['converged']:return [(lo,hi,piece,measured)]
        assert depth<8,(name,lo,hi,measured)
        mid=(lo+hi)/2
        return interval(lo,mid,depth+1)+interval(mid,hi,depth+1)
    leaves=[]
    for i in range(4):leaves+=interval(b.ZMin+b.ZLength*i/4,b.ZMin+b.ZLength*(i+1)/4,0)
    refined=[]
    for lo,hi,_,_ in leaves:
        mid=(lo+hi)/2;refined+=interval(lo,mid,1)+interval(mid,hi,1)
    reports=[]
    for level,items in [('initial',leaves),('refined',refined)]:
        shapes=[v[2] for v in items];union=shapes[0].multiFuse(shapes[1:]);missing=s.cut(union);added=union.cut(s)
        coarse=sum(v[3]['results'][0]['volume'] for v in items);volume=sum(v[3]['volume_mm3'] for v in items)
        centroid=[sum(v[3]['volume_mm3']*v[3]['centroid_mm'][i] for v in items)/volume for i in range(3)]
        overlap=max(abs(a[2].common(b[2]).Volume) for a,b in zip(items,items[1:]))
        record=dict(level=level,count=len(items),volume_mm3=volume,centroid_mm=centroid,
            integration_volume_delta_mm3=abs(coarse-volume),max_adjacent_overlap_mm3=overlap,
            missing_faces=len(missing.Faces),added_faces=len(added.Faces),missing_mm3=missing.Volume,added_mm3=added.Volume,
            pieces=[dict(interval=[v[0],v[1]],measure=v[3]) for v in items])
        reports.append(record);print(name,level,len(items),volume,centroid,flush=True)
    delta=abs(reports[0]['volume_mm3']-reports[1]['volume_mm3']);dc=math.dist(reports[0]['centroid_mm'],reports[1]['centroid_mm'])
    results[name]=dict(partitions=reports,refinement_volume_delta_mm3=delta,refinement_centroid_delta_mm=dc,attempts=attempts)
    Path('report.json').write_text(json.dumps(results,indent=2)+'\n');print(name,'refinement delta',delta,dc,flush=True)
