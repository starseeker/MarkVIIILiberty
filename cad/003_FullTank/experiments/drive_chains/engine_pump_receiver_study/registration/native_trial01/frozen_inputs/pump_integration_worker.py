"""One-document extraction or one-definition comparison; process lifetime bounds memory."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('mode',choices=['extract','material'])
p.add_argument('--input',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();out=a.output.resolve();out.parent.mkdir(parents=True,exist_ok=True)
import FreeCAD as App
import Part

if a.mode=='extract':
    path=a.input.resolve();doc=App.openDocument(str(path));definitions={};rows=[]
    def matrix(pose):return list(pose.toMatrix().A)
    def walk(obj,parent,owners):
        if obj.TypeId=='App::Link':
            assert abs(obj.Scale-1)<1e-12 and all(abs(v-1)<1e-12 for v in obj.ScaleVector)
            target=obj.LinkedObject
            assert target.Document==doc and target.TypeId!='App::Part' and hasattr(target,'Shape')
            world=parent.multiply(obj.LinkPlacement).multiply(target.Shape.Placement)
            rows.append(dict(name=getattr(obj,'OccurrenceId',obj.Name),object=obj.Name,
                definition=target.Name,frame=matrix(world),owners=owners))
            if target.Name not in definitions:
                definitions[target.Name]=dict(frame=matrix(target.Shape.Placement),
                    properties={k:getattr(target,k) for k in ['DefinitionKey','SourceRecords','SourcePartMark']
                                if k in target.PropertiesList})
        else:
            assert obj.TypeId=='App::Part',obj.Name
            world=parent.multiply(obj.Placement)
            for child in obj.Group:walk(child,world,owners+[obj.Name])
    walk(doc.Root,App.Placement(),[])
    assemblies={obj.Name:dict(local=matrix(obj.Placement),world=matrix(obj.getGlobalPlacement()),
        children=[child.Name for child in obj.Group],
        proposed_engine_pose=json.loads(obj.ProposedEnginePlacementJSON) if 'ProposedEnginePlacementJSON' in obj.PropertiesList else None)
        for obj in doc.Objects if obj.TypeId=='App::Part'}
    with zipfile.ZipFile(path) as z:
        t=ET.fromstring(z.read('Document.xml'));files={o.get('name'):s.get('file')
            for o in t.findall('./ObjectData/Object') for s in o.findall('./Properties/Property[@name="Shape"]/Part')}
        for name,row in definitions.items():
            data=z.read(files[name]);digest=hashlib.sha256(data).hexdigest();f=out.parent/'breps'/(digest+'.brep')
            f.parent.mkdir(exist_ok=True);f.write_bytes(data)
            row.update(brep_sha256=digest,brep_path=str(f),archive_entry=files[name])
    write(out,dict(native_sha256=sha(path),extractor_sha256=sha(Path(__file__)),
        definitions=definitions,occurrences=rows,assemblies=assemblies))
    App.closeDocument(doc.Name);print('extracted',path.name,len(rows),flush=True)
else:
    request=read(a.input);one=Part.Shape();two=Part.Shape()
    for shape,key in [(one,'source'),(two,'candidate')]:
        f=Path(request[key+'_path']);assert sha(f)==request[key+'_sha256'];shape.read(str(f))
    ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(1e-4,max(1e-7,ta+tb))
    missing,added=one.cut(two),two.cut(one)
    fm,fa=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
    record=dict(source_sha256=request['source_sha256'],candidate_sha256=request['candidate_sha256'],
        definition=request['definition'],missing_mm3=missing.Volume,added_mm3=added.Volume,
        fuzzy_missing_faces=fm,fuzzy_added_faces=fa,source_tolerance_mm=ta,candidate_tolerance_mm=tb,
        passed=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and
        abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and
        ta<=1e-4 and tb<=max(ta,1e-7)+1e-10)
    record['worker_sha256']=sha(Path(__file__))
    write(out,record);print('material equivalence',record['definition'],record['passed'],flush=True)
