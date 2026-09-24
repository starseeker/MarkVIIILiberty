"""Render the assembled high-speed brakes from saved definitions and composed frames."""
import argparse,sys
from pathlib import Path
from types import SimpleNamespace
H=Path(__file__).resolve().parent;STAGE=H.parents[1];sys.path.insert(0,str(STAGE))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
from lib.visual_review import shaded
from lib.cad_build import COLORS
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
rows=[v for v in m['occurrences'] if 'HighSpeedBrake' in v['name']];validate_native_bindings(dict(native_file=str(native),render_occurrences=[v['name'] for v in rows],landmarks=[]),m)
COLORS.update(Band=(.50,.54,.55),Lining=(.35,.32,.27),Hardware=(.69,.70,.69),Support=(.65,.48,.30),Lever=(.44,.55,.59),Drum=(.51,.61,.68));cache={}
def shape(row):
 key=row['definition']
 if key not in cache:
  d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);assert s.Placement.isIdentity();cache[key]=s
 s=cache[key].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));return s
items=[]
for row in rows:
 n=row['name'];s=shape(row);system='Support' if any(x in n for x in ['Stop','Clip','AnchorBracket']) else 'Lining' if 'Lining' in n and 'Rivet' not in n else 'Band' if any(x in n for x in ['Band','FrontEnd','AnchorEnd']) else 'Lever' if 'Lever' in n and 'Rivet' not in n else 'Hardware'
 items.append(dict(id=n,shape=s,target=SimpleNamespace(Shape=cache[row['definition']]),definition=row['definition'],system=system,representation='assembly'))
context=[]
for row in m['occurrences']:
 if row['name'] not in ['PortTransmissionCore_high_drum','StarboardTransmissionCore_high_drum']:continue
 s=shape(row);context.append(dict(id=row['name'],shape=s,target=SimpleNamespace(Shape=cache[row['definition']]),definition=row['definition'],system='Drum',representation='assembly'))
shaded(items,out/'high_brake_assembly_isometric.svg',(1,-1,.45),'High-speed brakes | bands, operating mechanisms, supports and stops',context=context)
shaded([v for v in items if v['id'].startswith('Port')],out/'high_brake_assembly_detail.svg',(.6,-1,.35),'Port high-speed brake | assembled static reconstruction',context=[v for v in context if v['id'].startswith('Port')])
write(out/'assembly_render_receipt.json',dict(native_sha256=sha(native),manifest_sha256=sha(out/'isolated/manifest.json'),renderer_sha256=sha(Path(__file__)),render_occurrences=[v['name'] for v in rows],images={n:sha(out/n) for n in ['high_brake_assembly_isometric.png','high_brake_assembly_detail.png']},source_camera_refit=False,scope='Saved high-speed brake occurrences; high drums in outline for visibility. This review selection does not replace the full powertrain or standard tank.',historical_geometry_qualified=False))
print('Rendered',len(rows),'assembled brake occurrences',flush=True)
