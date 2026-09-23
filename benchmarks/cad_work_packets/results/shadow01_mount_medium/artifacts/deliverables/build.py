"""Reproduce with: python3 freecad_python.py deliverables/build.py"""
from pathlib import Path
import hashlib
import json
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'deliverables'
# Numerical comparison thresholds only, not manufacturing tolerances.
EPS = 1e-8

def same(a, b):
    return all(abs(x-y) < EPS for x,y in zip(a.toMatrix().A, b.toMatrix().A))

def frame(s):
    return App.Placement(App.Vector(*s['translation']),
                         App.Rotation(App.Vector(*s['axis']), s['angle_degrees']))

def structure(doc):
    return {o.Name: (o.TypeId, o.Label, sorted(p.Name for p in o.InList),
            [p.Name for p in o.Group] if hasattr(o, 'Group') else None,
            o.LinkedObject.Name if o.TypeId == 'App::Link' else None,
            o.LinkTransform if o.TypeId == 'App::Link' else None)
            for o in doc.Objects}

def placements(doc):
    return {o.Name: App.Placement(o.Placement) for o in doc.Objects if hasattr(o,'Placement')}

def main():
    packet = json.loads((ROOT/'inputs/packet.json').read_text())
    for entry in packet['inputs']:
        assert hashlib.sha256((ROOT/'inputs'/entry['destination']).read_bytes()).hexdigest() == entry['sha256']
    spec = json.loads((ROOT/'inputs/mount_spec.json').read_text())
    doc = App.openDocument(str(ROOT/'inputs/broken_mount.FCStd'))
    doc.recompute()
    before = structure(doc)
    old = placements(doc)
    shapes = {n: doc.getObject(n).Shape.exportBrepToString() for n in ('Plate','Bolt')}
    assert same(doc.Rig.Placement, frame(spec['rig_frame']))
    desired = {}
    sides = {}
    for side, s in spec['side_frames'].items():
        assert same(doc.getObject(side).Placement, frame(s))
        desired['Plate'+side] = App.Placement()
        sides['Plate'+side] = side
        for i, (x,y) in enumerate(spec['holes']):
            name = 'Bolt'+side+str(i)
            desired[name] = App.Placement(App.Vector(x,y,0),App.Rotation())
            sides[name] = side
    changed = []
    evidence = {}
    for name, local in desired.items():
        o = doc.getObject(name)
        assert o.TypeId == 'App::Link'
        assert o.LinkedObject.Name == ('Plate' if name.startswith('Plate') else 'Bolt')
        assert o in doc.getObject(sides[name]).Group
        if not same(o.Placement, local):
            parent = doc.Rig.Placement.multiply(doc.getObject(sides[name]).Placement)
            assert same(o.Placement, parent.multiply(local)), 'Unexpected defect; stop without guessing'
            evidence[name] = {'before_matrix': list(o.Placement.toMatrix().A),
                              'after_matrix': list(local.toMatrix().A),
                              'before_equals_expected_world_transform': True}
            o.LinkPlacement = local
            changed.append(name)
    doc.recompute()
    assert structure(doc) == before
    for name, p in old.items():
        assert same(doc.getObject(name).Placement, desired[name] if name in changed else p)
    for name, brep in shapes.items():
        assert doc.getObject(name).Shape.exportBrepToString() == brep
    world = []
    for name, local in desired.items():
        o = doc.getObject(name)
        assert same(o.Placement, local)
        shape = o.Shape.copy()  # already contains the occurrence-local placement
        parent = doc.Rig.Placement.multiply(doc.getObject(sides[name]).Placement)
        shape.Placement = parent.multiply(shape.Placement)
        assert shape.isValid() and len(shape.Solids) == 1
        world.extend(shape.Solids)
    compound = Part.makeCompound(world)
    assert len(compound.Solids) == 10 and compound.isValid()
    # Independently compare with FreeCAD's recursively composed native Rig shape.
    assert compound.cut(doc.Rig.Shape).Volume < 1e-6
    assert doc.Rig.Shape.cut(compound).Volume < 1e-6
    overlaps = [world[i].common(world[j]).Volume for i in range(10) for j in range(i)]
    assert max(overlaps) < 1e-6
    doc.saveAs(str(OUT/'fixed.FCStd'))
    compound.exportStep(str(OUT/'fixed.step'))
    imported = Part.Shape()
    imported.read(str(OUT/'fixed.step'))
    assert imported.isValid() and len(imported.Solids) == 10
    # Match every exported solid to one installed solid, including its world position.
    remaining = list(imported.Solids)
    for solid in world:
        matches = [s for s in remaining if (s.CenterOfMass-solid.CenterOfMass).Length < 1e-6
                   and abs(s.Volume-solid.Volume) < 1e-6]
        assert len(matches) == 1
        match = matches[0]
        assert solid.cut(match).Volume < 1e-6 and match.cut(solid).Volume < 1e-6
        remaining.remove(match)
    App.closeDocument(doc.Name)
    saved = App.openDocument(str(OUT/'fixed.FCStd'))
    saved.recompute()
    assert structure(saved) == before
    for name,p in old.items():
        assert same(saved.getObject(name).Placement, desired[name] if name in changed else p)
    for name,brep in shapes.items():
        original = Part.Shape()
        original.importBrepFromString(brep)
        restored = saved.getObject(name).Shape
        assert restored.isValid()
        assert (len(original.Faces), len(original.Edges), len(original.Vertexes)) == (len(restored.Faces), len(restored.Edges), len(restored.Vertexes))
        assert abs(original.Volume-restored.Volume) < 1e-6
        assert original.cut(restored).Volume < 1e-6 and restored.cut(original).Volume < 1e-6
    assert saved.Rig.Shape.isValid() and len(saved.Rig.Shape.Solids) == 10
    cause = ('World-space transforms were stored as side-local LinkPlacements on ' + ', '.join(changed)
             + '. Correct composition is T_world = T_Rig * T_side * T_occurrence. '
             'The defective values equal T_Rig * T_side * T_hole, so nesting applied the parent '
             'frames a second time. Restore only the offending local hole translations with identity rotation.')
    (OUT/'diagnosis.json').write_text(json.dumps({'changed_objects':changed,'cause':cause,
                                                 'evidence':evidence},indent=2)+'\n')
    report = {'passed':True,'freecad_version':App.Version(),'object_count':len(saved.Objects),
              'changed_objects':changed,'installed_solids':len(world),
              'step_solids':len(imported.Solids),'volume_mm3':compound.Volume,
              'maximum_pairwise_overlap_mm3':max(overlaps),
              'checks':['input SHA256','frame contract','object names/types/labels/hierarchy/link targets',
                        'all unchanged placements','exact in-memory definition BREP before/after; geometry/topology after reopen',
                        'all ten occurrence placements','native Rig vs composed world compound',
                        'solid validity','pairwise intersections','STEP roundtrip per-solid geometry and position',
                        'saved native reopen']}
    (OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
