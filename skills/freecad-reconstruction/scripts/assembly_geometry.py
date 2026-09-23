"""Helpers for rigid App::Part ancestry and direct links to canonical definitions.

Run inside FreeCAD. Linked assemblies, scales and nonidentity definition frames
need a separately qualified traversal; these helpers deliberately reject them.
"""
import FreeCAD as App


def same_frame(a,b,tolerance=1e-8):
    return max(abs(x-y) for x,y in zip(a.toMatrix().A,b.toMatrix().A))<=tolerance


def global_placement(obj):
    result=App.Placement()
    seen=set()
    while obj is not None:
        key=(obj.Document.Name,obj.Name)
        if key in seen:raise ValueError('Cyclic geometric ancestry')
        seen.add(key)
        result=obj.Placement.multiply(result)
        obj=obj.getParentGeoFeatureGroup()
        if obj is not None and obj.TypeId!='App::Part':
            raise ValueError('Helper supports ordinary App::Part parents only')
    return result


def canonical_world_shape(link):
    if link.TypeId!='App::Link':raise ValueError('Expected a direct App::Link')
    if abs(link.Scale-1)>1e-12 or any(abs(v-1)>1e-12 for v in link.ScaleVector):
        raise ValueError('Scaled links require a different traversal')
    target=link.LinkedObject
    if target.TypeId=='App::Link' or not hasattr(target,'Shape') or target.TypeId=='App::Part':
        raise ValueError('Expected a direct shape definition, not a linked assembly')
    if not same_frame(global_placement(target),App.Placement()) or not same_frame(target.Shape.Placement,App.Placement()):
        raise ValueError('Definition and its library frame must be identity')
    shape=target.Shape.copy()
    shape.Placement=global_placement(link)
    return shape


def material_difference(reference,candidate):
    return dict(missing_mm3=abs(reference.cut(candidate).Volume),extra_mm3=abs(candidate.cut(reference).Volume))
