"""Regenerate both fixtures: python3 freecad_python.py deliverables/build.py."""
import json
from pathlib import Path
import sys
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables'
sys.path.insert(0, str(ROOT / 'inputs/freecad_skill/scripts'))
from assembly_geometry import canonical_world_shape


def frame(data):
    return App.Placement(App.Vector(*data['translation']),
                         App.Rotation(App.Vector(*data['axis']), data['angle_degrees']))


def build(name, spec):
    doc = App.newDocument(name)
    definitions = doc.addObject('App::Part', 'Definitions')
    dimensions = [('Pin', 'pin_radius', 'pin_bore_radius', 'pin_length'),
                  ('Tube', 'tube_outer_radius', 'tube_inner_radius', 'tube_length'),
                  ('Bush', 'bush_outer_radius', 'bush_inner_radius', 'bush_length')]
    for part_name, outer, inner, length in dimensions:
        obj = doc.addObject('PartDesign::Feature', part_name)
        definitions.addObject(obj)
        for prop, key in [('OuterRadius', outer), ('InnerRadius', inner), ('Length', length)]:
            obj.addProperty('App::PropertyLength', prop, 'Fixture dimensions')
            setattr(obj, prop, spec[key])
        obj.addProperty('App::PropertyString', 'SourceKeys', 'Evidence')
        obj.SourceKeys = ', '.join((outer, inner, length))
        obj.addProperty('App::PropertyString', 'HistoricalStatus', 'Evidence')
        obj.HistoricalStatus = spec['historical_status']
        obj.Shape = Part.makeCylinder(spec[outer], spec[length], App.Vector(), App.Vector(1, 0, 0)).cut(
            Part.makeCylinder(spec[inner], spec[length], App.Vector(), App.Vector(1, 0, 0)))
        assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1
    assembly = doc.addObject('App::Part', 'Assembly')
    assembly.Placement = frame(spec['assembly_frame'])
    station = doc.addObject('App::Part', 'Station')
    assembly.addObject(station)
    station.Placement = frame(spec['station_frame'])
    occurrences = [('PinInstance', 'Pin', -spec['pin_length']/2),
                   ('TubeInstance', 'Tube', -spec['tube_length']/2),
                   ('BushLeft', 'Bush', -spec['tube_length']/2),
                   ('BushRight', 'Bush', spec['tube_length']/2-spec['bush_length'])]
    links = []
    for occurrence, definition, x in occurrences:
        link = doc.addObject('App::Link', occurrence)
        station.addObject(link)
        link.setLink(doc.getObject(definition))
        link.Placement = App.Placement(App.Vector(x, 0, 0), App.Rotation())
        link.Visibility = True
        links.append(link)
    definitions.Visibility = False
    assembly.Visibility = True
    station.Visibility = True
    doc.recompute()
    solids = [canonical_world_shape(link) for link in links]
    for i, shape in enumerate(solids):
        for other in solids[i+1:]:
            assert shape.common(other).Volume < 1e-7
    Part.makeCompound(solids).exportStep(str(OUT / (name + '.step')))
    doc.saveAs(str(OUT / (name + '.FCStd')))
    App.closeDocument(doc.Name)


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    for name, spec in json.loads((ROOT / 'inputs/stack_spec.json').read_text()).items():
        assert spec['units'] == 'mm'
        build(name, spec)
    print('Built nominal and variant')
