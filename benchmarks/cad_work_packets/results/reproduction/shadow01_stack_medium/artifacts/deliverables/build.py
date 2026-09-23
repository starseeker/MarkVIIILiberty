"""Run from the workspace: python3 freecad_python.py deliverables/build.py.
Regenerates both cases from the immutable supplied JSON; no external dependencies.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import os
import sys
import FreeCAD as App
import Part
import FreeCADGui as Gui

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables'
SPEC_PATH = ROOT / 'inputs/stack_spec.json'
EPS_LENGTH = 1e-7  # computational check threshold, not a design tolerance (mm)
EPS_VOLUME = 1e-5  # computational check threshold (mm^3)


def close(a, b, eps=EPS_LENGTH):
    assert abs(a-b) <= eps, (a, b, eps)


def frame(data):
    return App.Placement(App.Vector(*data['translation']),
                         App.Rotation(App.Vector(*data['axis']), data['angle_degrees']))


def identity(p):
    close(p.Base.Length, 0)
    close(p.Rotation.Angle, 0)


def hollow(outer, inner, length):
    origin, axis = App.Vector(0, 0, 0), App.Vector(1, 0, 0)
    return Part.makeCylinder(outer, length, origin, axis).cut(
        Part.makeCylinder(inner, length, origin, axis)).Solids[0]


def volume(outer, inner, length):
    return math.pi * (outer**2-inner**2) * length


def make_definition(doc, group, name, outer, inner, length, color):
    obj = doc.addObject('PartDesign::Feature', name)
    group.addObject(obj)
    for prop, val in [('OuterRadius', outer), ('InnerRadius', inner), ('Length', length)]:
        obj.addProperty('App::PropertyLength', prop, 'Fixture dimensions')
        setattr(obj, prop, val)
        obj.setEditorMode(prop, 1)
    obj.Shape = hollow(obj.OuterRadius.Value, obj.InnerRadius.Value, obj.Length.Value)
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.LineColor = (0.12, 0.12, 0.12)
    obj.ViewObject.Deviation = 0.05
    return obj


def inspect(doc, spec):
    defs, assembly, station = doc.Definitions, doc.Assembly, doc.Station
    assert defs.TypeId == assembly.TypeId == station.TypeId == 'App::Part'
    identity(defs.Placement)
    assert {o.Name for o in defs.Group} == {'Pin', 'Tube', 'Bush'}
    assert list(assembly.Group) == [station]
    assert not defs.Visibility
    for obj in defs.Group:
        identity(obj.Placement)
        s = obj.Shape
        assert s.isValid() and len(s.Solids) == 1
        close(s.BoundBox.XMin, 0)
        close(s.BoundBox.XMax, obj.Length.Value)
        close(s.Volume, volume(obj.OuterRadius.Value, obj.InnerRadius.Value, obj.Length.Value), EPS_VOLUME)
        # A through bore must leave no material on the entire local axis.
        axis = Part.makeLine(App.Vector(0,0,0), App.Vector(obj.Length.Value,0,0))
        assert s.common(axis).Length < EPS_LENGTH
        assert sum(isinstance(f.Surface, Part.Cylinder) for f in s.Faces) == 2
    names = ['PinInstance', 'TubeInstance', 'BushLeft', 'BushRight']
    assert {o.Name for o in station.Group} == set(names)
    assert len([o for o in doc.Objects if o.TypeId == 'App::Link']) == 4
    starts = [-spec['pin_length']/2, -spec['tube_length']/2,
              -spec['tube_length']/2, spec['tube_length']/2-spec['bush_length']]
    targets = [doc.Pin, doc.Tube, doc.Bush, doc.Bush]
    world_frame = frame(spec['assembly_frame']).multiply(frame(spec['station_frame']))
    close((station.getGlobalPlacement().Base-world_frame.Base).Length, 0)
    close((station.getGlobalPlacement().Rotation.inverted()*world_frame.Rotation).Angle, 0)
    worlds = []
    for name, start, target in zip(names, starts, targets):
        link = doc.getObject(name)
        assert link.TypeId == 'App::Link' and link.LinkedObject == target
        close((link.LinkPlacement.Base-App.Vector(start,0,0)).Length, 0)
        close(link.LinkPlacement.Rotation.Angle, 0)
        solid = target.Shape.copy()
        solid.Placement = station.getGlobalPlacement().multiply(link.LinkPlacement).multiply(target.Shape.Placement)
        assert solid.isValid() and len(solid.Solids) == 1
        expected_center = world_frame.multVec(App.Vector(start+target.Length.Value/2,0,0))
        close((solid.CenterOfMass-expected_center).Length, 0)
        worlds.append(solid)
    pairs = []
    for i, j in itertools.combinations(range(4), 2):
        overlap = worlds[i].common(worlds[j]).Volume
        assert overlap < EPS_VOLUME
        pairs.append({'pair': [names[i], names[j]], 'overlap_mm3': overlap,
                      'distance_mm': worlds[i].distToShape(worlds[j])[0]})
    close(worlds[0].distToShape(worlds[2])[0], spec['bush_inner_radius']-spec['pin_radius'])
    close(worlds[1].distToShape(worlds[2])[0], spec['tube_inner_radius']-spec['bush_outer_radius'])
    return worlds, pairs


def build(name, spec):
    assert spec['units'] == 'mm'
    assert 0 < spec['pin_bore_radius'] < spec['pin_radius'] < spec['bush_inner_radius'] < spec['bush_outer_radius'] < spec['tube_inner_radius'] < spec['tube_outer_radius']
    assert 2*spec['bush_length'] < spec['tube_length'] < spec['pin_length']
    doc = App.newDocument(name)
    defs = doc.addObject('App::Part', 'Definitions')
    defs.addProperty('App::PropertyString', 'HistoricalStatus', 'Source').HistoricalStatus = spec['historical_status']
    defs.addProperty('App::PropertyString', 'SourceSHA256', 'Source').SourceSHA256 = hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest()
    for key, value in spec.items():
        if isinstance(value, (float, int)):
            defs.addProperty('App::PropertyLength', key, 'Source dimensions')
            setattr(defs, key, value)
            defs.setEditorMode(key, 1)
    pin = make_definition(doc, defs, 'Pin', spec['pin_radius'], spec['pin_bore_radius'], spec['pin_length'], (0.74,0.76,0.80))
    tube = make_definition(doc, defs, 'Tube', spec['tube_outer_radius'], spec['tube_inner_radius'], spec['tube_length'], (0.40,0.56,0.69))
    bush = make_definition(doc, defs, 'Bush', spec['bush_outer_radius'], spec['bush_inner_radius'], spec['bush_length'], (0.80,0.63,0.28))
    assembly = doc.addObject('App::Part', 'Assembly')
    assembly.Placement = frame(spec['assembly_frame'])
    station = doc.addObject('App::Part', 'Station')
    assembly.addObject(station)
    station.Placement = frame(spec['station_frame'])
    for label, target, x in [('PinInstance', pin, -spec['pin_length']/2),
                              ('TubeInstance', tube, -spec['tube_length']/2),
                              ('BushLeft', bush, -spec['tube_length']/2),
                              ('BushRight', bush, spec['tube_length']/2-spec['bush_length'])]:
        link = doc.addObject('App::Link', label)
        station.addObject(link)
        link.setLink(target)
        link.LinkPlacement = App.Placement(App.Vector(x,0,0), App.Rotation())
        link.Visibility = True
    doc.recompute()
    defs.Visibility = False
    assembly.Visibility = station.Visibility = True
    Gui.activeDocument().activeView().viewAxonometric()
    from pivy import coin
    node = Gui.activeDocument().activeView().getCameraNode()
    center = station.getGlobalPlacement().Base
    offset = node.orientation.getValue().multVec(coin.SbVec3f(0, 0, 2*spec['pin_length']))
    node.position.setValue(center.x+offset[0], center.y+offset[1], center.z+offset[2])
    node.height.setValue(1.3*spec['pin_length'])
    node.nearDistance.setValue(spec['pin_length']*0.1)
    node.farDistance.setValue(spec['pin_length']*4)
    worlds, pairs = inspect(doc, spec)
    path = OUT / (name+'.FCStd')
    doc.recompute()
    doc.saveAs(str(path))
    compound = Part.makeCompound(worlds)
    assert len(compound.Solids) == 4 and compound.isValid()
    step_path = OUT / (name+'.step')
    compound.exportStep(str(step_path))
    reread = Part.Shape()
    reread.read(str(step_path))
    assert reread.isValid() and len(reread.Solids) == 4
    unmatched = list(reread.Solids)
    for expected in worlds:
        match = min(unmatched, key=lambda s: (s.CenterOfMass-expected.CenterOfMass).Length+abs(s.Volume-expected.Volume))
        close(match.Volume, expected.Volume, 1e-4)
        close((match.CenterOfMass-expected.CenterOfMass).Length, 0, 1e-6)
        close(match.common(expected).Volume, expected.Volume, 1e-4)
        unmatched.remove(match)
    App.closeDocument(doc.Name)
    reopened = App.openDocument(str(path))
    inspect(reopened, spec)
    App.closeDocument(reopened.Name)
    return {'status': 'passed', 'native_reopened': True, 'step_reread_solids': 4,
            'installed_volumes_mm3': [s.Volume for s in worlds],
            'installed_centers_mm': [list(s.CenterOfMass) for s in worlds],
            'pairs': pairs, 'pin_end_projection_mm': (spec['pin_length']-spec['tube_length'])/2,
            'bush_inner_end_gap_mm': spec['tube_length']-2*spec['bush_length']}


def main():
    OUT.mkdir(exist_ok=True)
    packet = json.loads((ROOT/'inputs/packet.json').read_text())
    expected_hash = next(item['sha256'] for item in packet['inputs'] if item['destination']=='stack_spec.json')
    assert hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest() == expected_hash
    specs = json.loads(SPEC_PATH.read_text())
    Gui.showMainWindow()
    # Saving a camera does not require an offscreen raster render.
    report = {'FreeCAD_version': App.Version(), 'source_sha256': expected_hash,
              'check_thresholds': {'length_mm': EPS_LENGTH, 'volume_mm3': EPS_VOLUME,
                                   'step_length_mm': 1e-6, 'step_volume_mm3': 1e-4},
              'scenarios': {name: build(name, specs[name]) for name in ['nominal','variant']}}
    (OUT/'checks.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: nominal and variant; native reopen, STEP round trip, hollows, links, frames, clearances and no overlaps.', flush=True)


if __name__ == '__main__':
    # This installed offscreen Qt build segfaults during interpreter GUI teardown.
    # All saves, round-trip checks and report writes complete before explicit exit.
    try:
        main()
    except BaseException:
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(1)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
