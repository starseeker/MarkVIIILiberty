"""Small reconstruction helpers; geometry and acceptance stay in stage workers."""
from pathlib import Path
import sys
import uuid

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
C = H/'transmission_controls_study'
sys.path.insert(0,str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.cad_build import metadata


def pose(frame):
    return App.Placement(App.Matrix(*frame))


class Saved:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.report = read(self.folder/'report.json')
        self.manifest = read(self.folder/'isolated/manifest.json')
        self.native = self.folder/self.report['native_file']
        assert sha(self.native)==self.report['native_sha256']==self.manifest['native_sha256']
        self.rows = {r['name']:r for r in self.manifest['occurrences']}
        self.cache = {}

    def definition(self, key):
        if key not in self.cache:
            d=self.manifest['definitions'][key]
            assert sha(d['brep_path'])==d['brep_sha256']
            s=Part.Shape();s.read(d['brep_path'])
            assert s.Placement.isIdentity()
            self.cache[key]=s
        return self.cache[key].copy()

    def world(self,name):
        r=self.rows[name];s=self.definition(r['definition'])
        s.Placement=pose(r['frame'])
        return s


def trial(out, parent, shapes, specs, properties, details, inputs, curves=None):
    """Save a self-contained prototype. Caller supplies reviewed source metadata.

    Nothing is accepted by saving. Existing output directories are refused.
    Receiver shapes/frames come directly from the hash-bound parent.
    """
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    doc=App.newDocument('ControlRebuildTrial')
    root=doc.addObject('App::Part','Root')
    library=doc.addObject('App::Part','Definitions')
    groups={};bodies={}
    for key,s in shapes.items():
        assert s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed(),key
        assert s.getTolerance(1)<=1e-4,(key,s.getTolerance(1))
        body=doc.addObject('PartDesign::Body',key);library.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=s
        metadata(body,**properties[key])
        bodies[key]=body
    for name,spec in specs.items():
        owner=spec['owner'] if spec['role']!='receiver' else 'Receivers'
        if owner not in groups:
            group=doc.addObject('App::Part',owner);root.addObject(group)
            groups[owner]=group
        link=doc.addObject('App::Link',name);groups[owner].addObject(link)
        link.setLink(bodies[spec['definition']]);link.LinkPlacement=pose(spec['frame'])
        metadata(link,OccurrenceId=name,Coverage='reconstruction_trial',
                 SourceRecords=properties[spec['definition']].get('SourceRecords',[]))
    if curves:
        analysis=doc.addObject('App::DocumentObjectGroup','NonphysicalCenterlines')
        for name,s in curves.items():
            obj=doc.addObject('PartDesign::Feature',name+'WirePath');obj.Shape=s
            analysis.addObject(obj);obj.Visibility=False
            s.exportBrep(str(out/(name+'_centerline.brep')))
    for obj in doc.Objects:
        if obj.TypeId=='App::Part':obj.Uid=str(uuid.uuid5(uuid.NAMESPACE_URL,'markviii:control-redo:'+obj.Name))
    library.Visibility=False;doc.recompute()
    native=out/'ControlRebuildTrial.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    hashes={str(Path(f).resolve().relative_to(ROOT)):sha(f) for f in inputs}
    write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),
         parent_native=str(parent.native.relative_to(ROOT)),parent_native_sha256=sha(parent.native),
         parent_manifest_sha256=sha(parent.folder/'isolated/manifest.json'),
         input_hashes=hashes,specs=specs,details=details,
         new_occurrences=[n for n,s in specs.items() if s['role']!='receiver'],
         new_definitions=sorted(set(shapes)-set(parent.manifest['definitions'])),
         changed_definitions=[],prototype_physical_occurrences=len(specs),
         prototype_definition_count=len(shapes),geometry_integrated=False,
         historical_geometry_qualified=False,installation_qualified=False))
    return native
