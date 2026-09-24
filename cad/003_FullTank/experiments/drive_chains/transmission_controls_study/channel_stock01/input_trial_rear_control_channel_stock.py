"""Save an isolated channel stock trial; never promote an unfinished mount."""
import argparse
import json
from pathlib import Path
import shutil
import sys

H=Path(__file__).resolve().parent
sys.path[:0]=[str(H),str(H.parents[1])]
import FreeCAD as App
from lib.evidence import read, write, sha
from rear_control_channel_stock import channel

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args(); out=a.output.resolve(); assert not out.exists();out.mkdir(parents=True)
c=read(a.controls);d=c['dimensions_mm']
doc=App.newDocument('RearControlChannelStock')
root=doc.addObject('App::Part','Root');root.Label='Rear control channel | unfinished stock study'
defs=doc.addObject('App::DocumentObjectGroup','Definitions')
body=doc.addObject('PartDesign::Feature','Def_RearControlChannelStock');defs.addObject(body)
body.Label='M4128 | downward-open channel stock hypothesis'
body.Shape=channel(d['width'],d['height'],d['stock'],d['length'])
for key,value in d.items():
    body.addProperty('App::PropertyLength',key.capitalize(),'Reconstruction');setattr(body,key.capitalize(),value)
for key,value in dict(PieceMark='M4128',SourceRecords=json.dumps(['SNL:63:010','HB:nomenclature:190:059']),
                      GeometryStatus='unfinished_stock_hypothesis',UpdateMode='Regenerate with trial_rear_control_channel_stock.py; metadata fields are not live constraints',
                      Approximation=json.dumps(c['limits'])).items():
    body.addProperty('App::PropertyString',key,'Evidence');setattr(body,key,value)
link=doc.addObject('App::Link','RearControlChannelStock');link.setLink(body);root.addObject(link)
link.Placement=App.Placement(App.Vector(*c['placement_world_mm']),App.Rotation())
doc.recompute(); assert body.Shape.isValid() and len(body.Shape.Solids)==1
native=out/'RearControlChannelStock.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
inputs=[a.controls.resolve(),Path(__file__),H/'rear_control_channel_stock.py']
for path in inputs:shutil.copy2(path,out/('input_'+path.name))
write(out/'report.json',dict(native_file=native.name,native_sha256=sha(native),controls=c,
    input_hashes={path.name:sha(path) for path in inputs},
    definition_count=1,physical_occurrences=1,integrated_into_parent=False,
    historical_geometry_qualified=False,installation_qualified=False,
    scope='U-section stock only. No mounting holes, cleats, rivets, spring supports or fulcrums yet.'))
print('Saved isolated M4128 stock trial',str(native),flush=True)
