"""Measure angular free play from native gear contact and localize casing conflict."""
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace
import FreeCAD as App
import Part

REPO = Path('/home/cyapp/MarkVIIILiberty')
HELPERS = REPO / 'cad/003_FullTank/experiments/drive_chains'
sys.path[:0] = [str(HELPERS), str(HELPERS.parents[1])]
from detail_render import shaded_detail
from lib.cad_build import COLORS

OUT = Path(__file__).resolve().parent / 'mesh_probe'
r = json.loads((OUT/'result.json').read_text())
V = App.Vector
o = V(*r['gear_apex'])
def read(name):
    s = Part.Shape(); s.read(str(OUT/(name+'.brep'))); return s
main, pinion, case = (read(n) for n in ['saved_main', 'half_tooth', 'EngineCase_lower'])
checks=[]
for n in range(9):
    theta = n*360/33/8
    a, b = main.copy(), pinion.copy()
    a.rotate(o, V(1,0,0), theta); b.rotate(o, V(0,0,1), -1.5*theta)
    checks.append(dict(main_deg=theta, overlap_mm3=a.common(b).Volume,
                       separation_mm=a.distToShape(b)[0]))
    print('rotation',json.dumps(checks[-1]),flush=True)

contact = []
for sign in [-1,1]:
    lo, hi = 0, 1
    for n in range(13):
        mid = (lo+hi)/2
        b = pinion.copy(); b.rotate(o,V(0,0,1),sign*mid)
        gap = main.distToShape(b)[0]
        if gap <= 1e-6: hi = mid
        else: lo = mid
    contact.append(dict(sign=sign, free_angle_deg=lo, contact_angle_deg=hi,
                        bracket_width_deg=hi-lo))
    print('contact',json.dumps(contact[-1]),flush=True)
pitch = r['pinion_tooth']['pitch_radius_mm']
angle=sum(c['contact_angle_deg'] for c in contact)
outer = math.radians(angle)*pitch
middle = outer*(1-r['pinion_tooth']['face_width_mm']/(2*r['pinion_tooth']['cone_distance_mm']))
inner = outer*(1-r['pinion_tooth']['face_width_mm']/r['pinion_tooth']['cone_distance_mm'])
common=pinion.common(case); bb=common.BoundBox
envelope=dict(x=[bb.XMin,bb.XMax],y=[bb.YMin,bb.YMax],z=[bb.ZMin,bb.ZMax])
result=dict(rotation_samples=checks, native_contact_brackets=contact,
            outer_pitch_circumferential_backlash_mm=outer,
            midface_pitch_circumferential_backlash_mm=middle,
            inner_pitch_circumferential_backlash_mm=inner,
            contact_distance_threshold_mm=1e-6,
            source_cold_backlash_range_mm=[.127,.254],
            source_measurement_station_unspecified=True,
            case_interference_mm3=common.Volume, case_interference_bounds_mm=envelope,
            scope='Native kinematic and clearance experiment, not manufacturing qualification.')
(OUT/'backlash.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
COLORS.update(Main=(.65,.70,.73),Pinion=(.73,.62,.40),Case=(.54,.63,.63),Conflict=(.85,.2,.2))
def item(s,key):
    return dict(shape=s,target=SimpleNamespace(Shape=s),definition=key,system=key,representation='assembly')
shaded_detail([item(main,'Main'),item(pinion,'Pinion')],OUT/'mesh.svg',(.8,1,.5),
              'Lower distribution drive | saved 33-tooth bevel and experimental 22-tooth mate',deflection=.05)
cut=Part.makeBox(160,95,200,o+V(-100,0,-170))
caseview=case.common(cut)
shaded_detail([item(main,'Main'),item(pinion,'Pinion'),item(caseview,'Case'),item(common,'Conflict')],
              OUT/'case_section.svg',(.1,-1,.05),'Lower distribution drive | provisional casing conflict shown red',deflection=.05)
