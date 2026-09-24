"""Render the local pump context from verified saved-native geometry and frames."""
import argparse
from pathlib import Path
import sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--output',type=Path,help='Separate review output directory; defaults to candidate')
a=p.parse_args();candidate=a.candidate.resolve();out=(a.output or candidate).resolve();out.mkdir(parents=True,exist_ok=True)
r=read(candidate/'report.json');native=candidate/r['native_file']
assert sha(native)==r['native_sha256']
m=read(candidate/'isolated/candidate/manifest.json');assert m['native_sha256']==sha(native)
import FreeCAD as App
import Part
from lib.cad_build import COLORS
from detail_render import shaded_detail
V=App.Vector;engine=App.Placement(App.Matrix(*m['assemblies']['TankLibertyEngine']['world']))
current={}
for row in m['occurrences']:
    name=row['name']
    if not name.startswith(('EngineOilPump_','EngineWaterPump_','EngineLowerDrive_')) and name not in ['EngineCase_lower','hull_floor_5']:continue
    d=m['definitions'][row['definition']];path=Path(d['brep_path']);assert sha(path)==d['brep_sha256']
    shape=Part.Shape();shape.read(str(path));shape.Placement=App.Placement(App.Matrix(*row['frame']))
    current[name]=dict(shape=shape)
# Build the complete display set once, then render each view once.
inverse=engine.inverse();display={};roles={}
for name,row in current.items():
    role=('PumpOil' if name.startswith('EngineOilPump_') else 'PumpWater' if name.startswith('EngineWaterPump_')
          else 'PumpDrive' if name.startswith('EngineLowerDrive_') else 'PumpCase' if name=='EngineCase_lower'
          else 'PumpFloor' if name=='hull_floor_5' else None)
    if role is None:continue
    s=row['shape'].copy();s.Placement=inverse.multiply(s.Placement);display[name]=s;roles[name]=role
COLORS.update(PumpCase=(.60,.65,.63),PumpOil=(.80,.66,.42),PumpWater=(.42,.66,.76),
              PumpDrive=(.59,.61,.67),PumpFloor=(.77,.36,.35))
for name,direction in [('isometric',(.7,-1,.6)),('section',(0,-1,0)),('floor_context',(0,-1,0))]:
    items=[];cut=Part.makeBox(480,145,530,V(1010,0,-420))
    for ident,s in display.items():
        if roles[ident]=='PumpFloor' and name!='floor_context':continue
        if name=='isometric':
            shown=s.common(Part.makeBox(330,220,415,V(1060,-110,-400))) if roles[ident]=='PumpCase' else s.copy()
        else:shown=s.common(cut)
        if not shown.Solids:continue
        items.append(dict(shape=shown,target=SimpleNamespace(Shape=shown),definition=ident,
            system=roles[ident],representation='assembly'))
    shaded_detail(items,out/(name+'.svg'),direction,'Saved coupled pump hierarchy | '+name,.08)
write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
    images={name+'.png':sha(out/(name+'.png')) for name in ['isometric','section','floor_context']},source='Actual2393-occurrence saved native; only local affected components displayed',
    display_only_sections=True,installation_qualified=False))
