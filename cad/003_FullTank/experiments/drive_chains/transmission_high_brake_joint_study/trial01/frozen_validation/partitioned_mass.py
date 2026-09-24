"""Strict mass integration by verified, adaptively refined solid partitions.

Use explicitly after diagnosing whole-face integration failure. This changes
only the measurement domain, never the supplied or exported CAD geometry.
Every piece must pass AdaptiveMass's original convergence requirements. Both
partitions must reproduce the original material, and their aggregate properties
must agree. A rigid measurement frame allows reuse of identical definitions.
"""
import copy
import math
from pathlib import Path
import tempfile

from .evidence import write,sha


class PartitionedMass:
    def __init__(self, mass, work):
        self.mass=mass;self.work=Path(work).resolve();self.work.mkdir(parents=True,exist_ok=True)
        self.cache={}
        self.provenance=dict(adapter_sha256=sha(Path(__file__)),mass_provenance=mass.provenance,
                             initial_intervals=4,max_subdivision_depth=8,refinement='Bisect every converged interval once, subdividing further if required.')

    @staticmethod
    def certificate(original, pieces):
        """The pieces must be in adjacent, ordered, nonoverlapping Z slabs."""
        union=pieces[0].multiFuse(pieces[1:])
        missing=original.cut(union);added=union.cut(original)
        overlaps=[abs(a.common(b).Volume) for a,b in zip(pieces,pieces[1:])]
        result=dict(missing_faces=len(missing.Faces),added_faces=len(added.Faces),
                    missing_mm3=missing.Volume,added_mm3=added.Volume,
                    max_adjacent_overlap_mm3=max(overlaps,default=0))
        result['passed']=not missing.Faces and not added.Faces and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and all(v<1e-5 for v in overlaps)
        return result

    def measure(self,shape,frame=None):
        import FreeCAD as App
        import Part
        assert shape.isValid() and len(shape.Solids)==1 and shape.Solids[0].isClosed()
        frame=frame or App.Placement();local=shape.copy()
        # Equality here is exact: a saved definition placed in this frame needs
        # no inverse-transform arithmetic to recover its original coordinates.
        if list(shape.Placement.toMatrix().A)==list(frame.toMatrix().A):local.Placement=App.Placement()
        else:local.Placement=frame.inverse().multiply(shape.Placement)
        with tempfile.TemporaryDirectory(dir=self.work) as name:
            path=Path(name)/'canonical.brep';local.exportBrep(str(path));key=sha(path)
        if key not in self.cache:
            box=local.BoundBox;attempts=[]
            def interval(lo,hi,depth):
                piece=local.common(Part.makeBox(box.XLength+2,box.YLength+2,hi-lo,App.Vector(box.XMin-1,box.YMin-1,lo)))
                assert piece.isValid() and len(piece.Solids)==1 and piece.getTolerance(1)<=1e-4
                measured=self.mass.measure(piece)
                attempts.append(dict(interval=[lo,hi],depth=depth,measure=measured))
                write(self.work/'progress.json',dict(canonical_brep_sha256=key,attempts=len(attempts),last_interval=[lo,hi],depth=depth,converged=measured['converged']))
                if measured['converged']:return [(lo,hi,piece,measured)]
                if depth>=8:raise ValueError('Partition did not reach the unchanged integration tolerances')
                mid=(lo+hi)/2
                return interval(lo,mid,depth+1)+interval(mid,hi,depth+1)
            leaves=[]
            for i in range(4):leaves+=interval(box.ZMin+box.ZLength*i/4,box.ZMin+box.ZLength*(i+1)/4,0)
            refined=[]
            for lo,hi,_,_ in leaves:
                mid=(lo+hi)/2;refined+=interval(lo,mid,1)+interval(mid,hi,1)
            reports=[]
            for label,items in [('initial',leaves),('refined',refined)]:
                for left,right in zip(items,items[1:]):assert left[1]==right[0]
                volume=sum(v[3]['volume_mm3'] for v in items)
                centroid=[sum(v[3]['volume_mm3']*v[3]['centroid_mm'][i] for v in items)/volume for i in range(3)]
                coarse_volume=sum(v[3]['results'][0]['volume'] for v in items)
                coarse_center=[sum(v[3]['results'][0]['volume']*v[3]['results'][0]['centroid'][i] for v in items)/coarse_volume for i in range(3)]
                integration_delta=sum(v[3]['volume_convergence_mm3'] for v in items)
                centroid_delta=math.dist(coarse_center,centroid)
                certificate=self.certificate(local,[v[2] for v in items])
                passed=certificate['passed'] and integration_delta<1e-5 and centroid_delta<1e-6
                reports.append(dict(label=label,count=len(items),volume_mm3=volume,centroid_mm=centroid,
                    integration_absolute_volume_delta_mm3=integration_delta,integration_centroid_delta_mm=centroid_delta,
                    material_certificate=certificate,passed=passed,pieces=[dict(interval=[v[0],v[1]],measure=v[3]) for v in items]))
            delta=abs(reports[0]['volume_mm3']-reports[1]['volume_mm3']);dc=math.dist(reports[0]['centroid_mm'],reports[1]['centroid_mm'])
            result=dict(method='Adaptive Gauss on verified, independently refined disjoint partitions',canonical_brep_sha256=key,
                provenance=self.provenance,partitions=reports,attempts=attempts,volume_convergence_mm3=delta,centroid_convergence_mm=dc,
                volume_mm3=reports[-1]['volume_mm3'],canonical_centroid_mm=reports[-1]['centroid_mm'],
                converged=all(v['passed'] for v in reports) and delta<1e-5 and dc<1e-6)
            self.cache[key]=result;write(self.work/(key+'.json'),result)
        result=copy.deepcopy(self.cache[key])
        result['centroid_mm']=list(frame.multVec(App.Vector(*result['canonical_centroid_mm'])))
        result['measurement_frame']=list(frame.toMatrix().A)
        return result
