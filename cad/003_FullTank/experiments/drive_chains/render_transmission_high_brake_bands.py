"""Render the saved partial high-speed brake reconstruction without camera fitting."""
import argparse
from pathlib import Path
from types import SimpleNamespace
import sys
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
COLORS.update(HighBand=(.38,.54,.61),HighLining=(.70,.47,.25),Steel=(.58,.62,.68),Frame=(.62,.53,.40))
cache={};items={}
for row in m['occurrences']:
    owners=row['owners'];name=row['name']
    if not any(v in owners for v in ['TransmissionHighSpeedBrakes','TransmissionBrakeBands','TransmissionBrakeStops','TransmissionMountingFrame']) and not name.endswith('TransmissionCore_high_drum'):continue
    d=m['definitions'][row['definition']]
    if row['definition'] not in cache:
        assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[row['definition']]=SimpleNamespace(Shape=s)
    target=cache[row['definition']];s=target.Shape.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
    role='HighLining' if 'HighSpeedBrake' in name and name.endswith('Lining') else 'HighBand' if 'HighSpeedBrake' in name and name.endswith('Band') else 'Frame' if 'TransmissionMountingFrame' in owners else 'Steel'
    items[name]=dict(id=name,shape=s,target=target,definition=row['definition'],system=role,representation='assembly')
context=[v for v in items.values() if v['system']=='Frame']
shaded([v for v in items.values() if v['system']!='Frame'],out/'isometric.svg',(1,-.8,.55),'High-speed brake development | source-sized linings and partial backing blanks; fittings pending',context=context)
focus=[v for k,v in items.items() if k.startswith('PortHighSpeedBrake')]
shaded(focus,out/'high_brake_detail.svg',(1,-1,.3),'Long MX109 and short M364 | holes populated; ears, anchors and hardware pending')
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],renderer_sha256=sha(Path(__file__)),images={n+'.png':sha(out/(n+'.png')) for n in ['isometric','high_brake_detail']},camera_refit=False,historical_overlay=False,packet_complete=False))
print('Rendered partial high-speed bands and retained context',flush=True)
