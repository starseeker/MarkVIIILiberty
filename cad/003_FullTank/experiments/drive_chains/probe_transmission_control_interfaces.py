"""Locate saved brake control bores and neighboring structure before routing rods."""
import argparse,sys
from pathlib import Path
from types import SimpleNamespace
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
from lib.visual_review import shaded
from lib.cad_build import COLORS
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
parent=H/'transmission_high_brake_support_study/integrated_upper01';r=read(parent/'report.json');m=read(parent/'isolated/manifest.json');q=read(parent/'qualification.json');native=parent/r['native_file'];assert q['local_static_checks_passed'] and sha(native)==q['native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};names=[h+suffix for h in ['Port','Starboard'] for suffix in ['HighSpeedBrakeLeverLeft','HighSpeedBrakeLeverRight','LowSpeedBrakeLever','TrackBrakeLever']];validate_native_bindings(dict(native_file=str(native),render_occurrences=names,landmarks=[]),m);cache={}
def world(name):
 row=rows[name];key=row['definition']
 if key not in cache:
  d=m['definitions'][key];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[key]=s
 s=cache[key].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));return s
interfaces=[];checks=[];items=[];COLORS.update(Control=(.75,.47,.22),Brake=(.47,.57,.61),Structure=(.52,.54,.51))
for hand in ['Port','Starboard']:
 for kind,radius,suffixes in [('HighSpeed',8.0875,['HighSpeedBrakeLeverLeft','HighSpeedBrakeLeverRight']),('LowSpeed',6.5,['LowSpeedBrakeLever']),('Track',6.5,['TrackBrakeLever'])]:
  faces=[]
  for suffix in suffixes:
   name=hand+suffix;s=world(name);row=rows[name];items.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=cache[row['definition']]),definition=row['definition'],system='Control',representation='assembly'))
   for f in s.Faces:
    if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and abs(abs(f.Surface.Axis.y)-1)<1e-7:faces.append((name,f))
  assert faces;lowest=min(f.Surface.Center.z for _,f in faces);selected=[(n,f) for n,f in faces if abs(f.Surface.Center.z-lowest)<1e-6]
  xs=[f.Surface.Center.x for _,f in selected];ys=[v.Point.y for _,f in selected for v in f.Vertexes];assert max(xs)-min(xs)<1e-6
  center=[sum(xs)/len(xs),(min(ys)+max(ys))/2,lowest];intervals=[]
  for name,f in selected:
   y=[v.Point.y for v in f.Vertexes];intervals.append(dict(occurrence=name,range_y_mm=[min(y),max(y)]))
  intervals.sort(key=lambda v:v['range_y_mm'][0]);gap=intervals[-1]['range_y_mm'][0]-intervals[0]['range_y_mm'][1] if len(intervals)>1 else None
  interfaces.append(dict(id=hand+kind+'BrakeControl',center_world_mm=center,pin_axis_world=[0,1,0],bore_diameter_mm=2*radius,outer_width_mm=max(ys)-min(ys),inter_member_gap_mm=gap,bearing_intervals=intervals,selection='Lowest transverse cylinder with the currently modeled control-bore radius; visual/source identity must be reviewed before mating.'))
  checks.append(dict(name=hand+kind+' saved control bore',passed=len(selected)==len(suffixes) and max(ys)>min(ys)))
contextnames=[n for n in rows if n in ['CenterTransmissionCore_bevel_case','PortTransmissionCore_plain_case','StarboardTransmissionCore_plain_case'] or n.endswith('TransmissionCore_high_drum') or n.endswith('TransmissionCore_low_drum') or 'TransmissionFrame' in n and any(x in n for x in ['Channel','channel'])]
context=[]
for name in contextnames:
 row=rows[name];s=world(name);context.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=cache[row['definition']]),definition=row['definition'],system='Structure',representation='assembly'))
shaded(items,out/'control_interfaces_isometric.svg',(1,-1,.45),'Existing brake control bores | receiving interfaces for the next linkage packet',context=context)
write(out/'report.json',dict(passed=all(v['passed'] for v in checks),checks=checks,interfaces=interfaces,source_native_sha256=sha(native),source_manifest_sha256=sha(parent/'isolated/manifest.json'),source_qualification_sha256=sha(parent/'qualification.json'),probe_sha256=sha(Path(__file__)),retained_context=contextnames,geometry_modified=False,limits=['These are measured current CAD interfaces, not independent historical dimensions.','Full rod routes, mounting stations and pin/clevis selection remain unresolved.','High-speed transverse gap and lower/track lever widths must govern any proposed mating hardware.']))
print('Located six saved brake-control interfaces',interfaces,flush=True)
