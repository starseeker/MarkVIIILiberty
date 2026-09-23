"""Exercise real FreeCAD transforms/exchange and unsupported-case rejection."""
import json
from pathlib import Path
import tempfile

import FreeCAD as App
import Part
from assembly_geometry import canonical_world_shape,global_placement,material_difference,same_frame


def main():
    checks={}
    doc=App.newDocument('SkillQualification')
    library=doc.addObject('App::Part','Definitions')
    definition=doc.addObject('PartDesign::Feature','Sleeve');library.addObject(definition)
    definition.Shape=Part.makeCylinder(12,40).cut(Part.makeCylinder(8,42,App.Vector(0,0,-1)))
    outer=doc.addObject('App::Part','Outer');inner=doc.addObject('App::Part','Inner');outer.addObject(inner)
    outer.Placement=App.Placement(App.Vector(40,-60,120),App.Rotation(App.Vector(1,2,3),33))
    inner.Placement=App.Placement(App.Vector(10,30,-20),App.Rotation(App.Vector(0,1,0),-72))
    link=doc.addObject('App::Link','SleeveInstance');inner.addObject(link);link.setLink(definition)
    library.Visibility=False;link.Visibility=True
    link.Placement=App.Placement(App.Vector(5,-8,12),App.Rotation(App.Vector(1,0,0),16));doc.recompute()
    shape=canonical_world_shape(link)
    point=App.Vector(10,0,20)
    expected=outer.Placement.multVec(inner.Placement.multVec(link.Placement.multVec(point)))
    checks['composed_material_point']=shape.isInside(expected,1e-7,False)
    center=outer.Placement.multVec(inner.Placement.multVec(link.Placement.multVec(App.Vector(0,0,20))))
    checks['bore_void']=not shape.isInside(center,1e-7,False)
    checks['part_api_agrees']=same_frame(global_placement(inner),inner.getGlobalPlacement())
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
        folder=Path(folder);shape.exportStep(str(folder/'sleeve.step'))
        loaded=Part.Shape();loaded.read(str(folder/'sleeve.step'))
        checks['step_material']=loaded.isValid() and len(loaded.Solids)==1 and max(material_difference(shape,loaded).values())<1e-5
        doc.saveAs(str(folder/'test.FCStd'));App.closeDocument(doc.Name)
        doc=App.openDocument(str(folder/'test.FCStd'));link=doc.getObject('SleeveInstance')
        checks['headless_visibility_reopens']=not doc.getObject('Definitions').Visibility and link.Visibility
        checks['native_reopen']=max(material_difference(shape,canonical_world_shape(link)).values())<1e-5
        link.Scale=2
        try:canonical_world_shape(link);checks['reject_scale']=False
        except ValueError:checks['reject_scale']=True
        link.Scale=1;doc.getObject('Definitions').Placement.Base.x=1
        try:canonical_world_shape(link);checks['reject_definition_frame']=False
        except ValueError:checks['reject_definition_frame']=True
        doc.getObject('Definitions').Placement=App.Placement();link.setLink(doc.getObject('Definitions'))
        try:canonical_world_shape(link);checks['reject_assembly_link']=False
        except ValueError:checks['reject_assembly_link']=True
        App.closeDocument(doc.Name)
    print(json.dumps(dict(passed=all(checks.values()),checks=checks,freecad=App.Version(),occ=Part.OCC_VERSION),indent=2))
    assert all(checks.values()),checks


if __name__=='__main__':main()
