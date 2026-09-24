"""Measure the saved front-brake stack before introducing the missing spacers."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();base=a.candidate.resolve();report=read(base/'report.json');manifest=read(base/'isolated/manifest.json')
assert sha(base/report['native_file'])==report['native_sha256']==manifest['native_sha256']
rows={v['name']:v for v in manifest['occurrences']};cache={}
def shape(name):
 row=rows[name];d=manifest['definitions'][row['definition']]
 if row['definition'] not in cache:
  assert sha(Path(d['brep_path']))==d['brep_sha256']
  s=Part.Shape();s.read(d['brep_path']);assert s.isValid() and len(s.Solids)==1;cache[row['definition']]=s
 s=cache[row['definition']].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));return s
stacks=[]
for hand in ['Port','Starboard']:
 for role in ['LowSpeed','Track']:
  prefix=hand+role+'Brake';screw=shape(prefix+'AdjustingScrew');axis=screw.Placement
  parts={};local_shapes={}
  for suffix in ['AdjustingScrew','AdjustingSpring','Swivel','AdjustingNut']:
   name=prefix+suffix;world=shape(name);local=world.copy();local.Placement=axis.inverse().multiply(world.Placement)
   local_shapes[suffix]=local
   box=local.optimalBoundingBox(False,False)
   parts[suffix]=dict(occurrence=name,definition=rows[name]['definition'],frame=rows[name]['frame'],
       axis_bounds_mm=[box.XMin,box.YMin,box.ZMin,box.XMax,box.YMax,box.ZMax],volume_mm3=world.Volume)
  spring=parts['AdjustingSpring']['axis_bounds_mm']
  radius=max(abs(spring[i]) for i in [0,1,3,4])
  seat=local_shapes['Swivel'].common(Part.makeCylinder(radius,500,App.Vector(0,0,-100)))
  assert seat.isValid() and not seat.isNull()
  swivel=seat.optimalBoundingBox(False,False)
  stacks.append(dict(id=prefix,parts=parts,spring_axial_length_mm=spring[5]-spring[2],
      swivel_seat_search_radius_mm=radius,spring_to_swivel_seat_axial_gap_mm=swivel.ZMin-spring[5]))
write(a.output,dict(native_sha256=manifest['native_sha256'],inspector_sha256=sha(Path(__file__)),stacks=stacks,
    existing_adjusting_spring_count=len(stacks),catalogued_spacer_quantity=4,
    standard_modified=False,geometry_added=False,
    interpretation='Saved spring reaches the existing swivel seat; a spacer cannot simply be added to this occupied stack. Its location and any change to estimated spring/shoulder geometry require a reviewed hypothesis.',
    limitation='Optimal bounds without triangulation or added shape tolerance, and swivel clipped to the spring-radius cylinder, identify occupied axial intervals; they do not alone prove annular seat contact or establish the printed stock dimensions datum.'))
print(json.dumps([dict(id=s['id'],spring_length_mm=s['spring_axial_length_mm'],swivel_gap_mm=s['spring_to_swivel_seat_axial_gap_mm']) for s in stacks],indent=2))
