"""Qualify the new evaluator with known-good CAD and intentionally bad artifacts."""
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad_packets'))
from common import sha,write
from validators.shadow import evaluate,placement,world_shape

HERE=Path(__file__).resolve().parent
FIX=HERE/'fixtures'
OUT=HERE/'results/qualification'


def export(doc,links,path):
    import Part
    doc.recompute();doc.saveAs(str(path.with_suffix('.FCStd')))
    Part.makeCompound([world_shape(o) for o in links]).exportStep(str(path.with_suffix('.step')))


def good_stack(out):
    import FreeCAD as A
    import Part
    for name,p in json.loads((FIX/'stack_spec.json').read_text()).items():
        doc=A.newDocument('ReferenceStack')
        defs=doc.addObject('App::Part','Definitions');asm=doc.addObject('App::Part','Assembly')
        station=doc.addObject('App::Part','Station');asm.addObject(station)
        asm.Placement=placement(p['assembly_frame'],A);station.Placement=placement(p['station_frame'],A)
        rows=[('Pin','pin_radius','pin_bore_radius','pin_length'),('Tube','tube_outer_radius','tube_inner_radius','tube_length'),
              ('Bush','bush_outer_radius','bush_inner_radius','bush_length')]
        for title,outer,inner,length in rows:
            obj=doc.addObject('PartDesign::Feature',title);defs.addObject(obj)
            obj.Shape=Part.makeCylinder(p[outer],p[length],A.Vector(),A.Vector(1,0,0)).cut(
                Part.makeCylinder(p[inner],p[length]+2,A.Vector(-1,0,0),A.Vector(1,0,0)))
        positions={'PinInstance':('Pin',-p['pin_length']/2),'TubeInstance':('Tube',-p['tube_length']/2),
                   'BushLeft':('Bush',-p['tube_length']/2),'BushRight':('Bush',p['tube_length']/2-p['bush_length'])}
        links=[]
        for n,(target,x) in positions.items():
            o=doc.addObject('App::Link',n);station.addObject(o);o.setLink(doc.getObject(target))
            o.Placement.Base=A.Vector(x,0,0);links.append(o)
        export(doc,links,out/name);A.closeDocument(doc.Name)


def good_mount(out):
    import FreeCAD as A
    doc=A.openDocument(str(FIX/'broken_mount.FCStd'))
    p=json.loads((FIX/'mount_spec.json').read_text())
    for name,index in [('BoltLeft1',1),('BoltRight2',2)]:
        x,y=p['holes'][index];doc.getObject(name).Placement=A.Placement(A.Vector(x,y,0),A.Rotation())
    export(doc,[o for o in doc.Objects if o.TypeId=='App::Link'],out/'fixed')
    write(out/'diagnosis.json',dict(changed_objects=['BoltLeft1','BoltRight2'],cause='Two global placements were assigned as local placements, applying the parent frame twice.'))
    A.closeDocument(doc.Name)


def main():
    import FreeCAD as A
    import Part
    OUT.mkdir(parents=True,exist_ok=True)
    tests={}
    for name,builder in [('stack',good_stack),('mount',good_mount)]:
        folder=OUT/name;folder.mkdir(exist_ok=True);builder(folder)
        tests[name+'_reference']=evaluate(name,FIX,folder)
        if not tests[name+'_reference']['passed']:
            write(OUT/'self_test.json',tests);raise AssertionError(tests[name+'_reference'])
    for label,objname in [('omitted_parent_frame','Assembly'),('moved_bush','BushRight')]:
        folder=OUT/label;shutil.copytree(OUT/'stack',folder,dirs_exist_ok=True)
        doc=A.openDocument(str(folder/'nominal.FCStd'))
        if objname=='Assembly':doc.getObject(objname).Placement=A.Placement()
        else:doc.getObject(objname).Placement.Base.x+=1
        doc.recompute();doc.save();A.closeDocument(doc.Name)
        tests[label]=evaluate('stack',FIX,folder);assert not tests[label]['passed'],label
    folder=OUT/'unfixed_mount';shutil.copytree(OUT/'mount',folder,dirs_exist_ok=True)
    shutil.copyfile(FIX/'broken_mount.FCStd',folder/'fixed.FCStd')
    tests['unfixed_mount']=evaluate('mount',FIX,folder);assert not tests['unfixed_mount']['passed']
    p=dict(printed_spring_od_in=3.937,assumed_wire_diameter_in=1.0,printed_tube_od_in=3.812,
           literal_spring_id_mm=49.1998,tube_od_mm=96.8248,literal_radial_clearance_mm=-23.8125,
           alternative_spring_id_mm=99.9998,alternative_spring_od_mm=150.7998,alternative_radial_clearance_mm=1.5875,
           spring_mark='M1336',tube_mark='M1333',decision_status='needs_source_review',memo_supported=False,
           historical_dimensions_proven=False,source_wording='outside diameter',
           missing_evidence='A contemporaneous erratum or a provenance-qualified measurement of an original spring.')
    folder=OUT/'spring';folder.mkdir(exist_ok=True);write(folder/'assessment.json',p)
    tests['spring_reference']=evaluate('spring',FIX,folder);assert tests['spring_reference']['passed']
    folder=OUT/'unsupported_source_correction';folder.mkdir(exist_ok=True)
    write(folder/'assessment.json',dict(p,source_wording='inside diameter',historical_dimensions_proven=True,memo_supported=True,decision_status='accepted'))
    tests['unsupported_source_correction']=evaluate('spring',FIX,folder);assert not tests['unsupported_source_correction']['passed']
    write(OUT/'self_test.json',dict(passed=True,tests=tests,validator_sha256=sha(ROOT/'tools/cad_packets/validators/shadow.py'),
                                   runtime=dict(freecad=A.Version(),occ=Part.OCC_VERSION)))
    print('PASS: three references and four rejection controls; FreeCAD '+'.'.join(A.Version()[:3]))


if __name__=='__main__':main()
