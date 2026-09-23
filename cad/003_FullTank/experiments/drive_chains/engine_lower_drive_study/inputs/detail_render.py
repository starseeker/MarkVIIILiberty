"""Refine native tessellation without changing the frozen standard renderer.

This adapter only affects display meshing. The existing renderer still verifies
its target-to-installed rigid transform and uses the native shape bounds.
"""
from types import SimpleNamespace
from lib.visual_review import shaded


class FineEdge:
    def __init__(self, edge, deflection):
        self.edge, self.deflection = edge, deflection

    def discretize(self, **kwargs):
        kwargs['Deflection'] = min(kwargs.get('Deflection', self.deflection), self.deflection)
        return self.edge.discretize(**kwargs)


class FineMesh:
    def __init__(self, shape, deflection):
        self.shape, self.deflection = shape, deflection
        self.Placement = shape.Placement
        self.Edges = [FineEdge(edge, deflection) for edge in shape.Edges]

    def tessellate(self, requested):
        return self.shape.tessellate(min(requested, self.deflection))


def shaded_detail(items, path, direction, title, deflection=.04):
    if not 0 < deflection <= .6:
        raise ValueError('Detail deflection must be positive and no coarser than 0.6 mm')
    refined=[dict(item,target=SimpleNamespace(Shape=FineMesh(item['target'].Shape,deflection))) for item in items]
    return shaded(refined,path,direction,title)
