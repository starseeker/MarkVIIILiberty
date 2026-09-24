"""Prototype material check against every retained development occurrence.

This is an exploratory layout check, not saved-native assembly qualification.
"""
import argparse
from pathlib import Path
import sys
import numpy as np
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty')
H=ROOT/'cad/003_FullTank/experiments/drive_chains'
sys.path[:0]=[str(H),str(H.parents[1])]
from lib.evidence import read,write,sha
from transmission_brake_front_layout import layout
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--probe',type=Path,required=True)
p.add_argument('--controls',type=Path,default=H/'transmission_brake_front_study/controls.json')
a=p.parse_args();probe=a.probe.resolve();out=Path.cwd()
parent=H/'transmission_brake_anchor_study/trial01'
m=read(parent/'isolated/manifest.json');r=read(probe/'report.json');d=r['dimensions'];c=read(a.controls)['controls']
assert sha(parent/'PowertrainWithBrakeAnchors.FCStd')==m['native_sha256']
new,revised,groups=layout(d,c,m);rows={v['name']:v for v in m['occurrences']}
definitions=dict(m['definitions'])
for role in ['pin','screw','swivel','nut','lever','spring','low_ear','track_ear','low_band','track_band']:
    key=('Def_BrakeBand_' if role.endswith('_band') else 'Def_BrakeFront_')+role
    path=probe/(role+'.brep');definitions[key]=dict(brep_path=str(path),brep_sha256=sha(path))
allrows={**rows,**revised,**new};cache={};shapes={}
for name,row in allrows.items():
    key=row['definition']
    if key not in cache:
        f=Path(definitions[key]['brep_path']);assert sha(f)==definitions[key]['brep_sha256']
        s=Part.Shape();s.read(str(f));cache[key]=s
    s=cache[key].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));shapes[name]=s
affected=sorted(set(new)|set(revised))
write(out/'layout.json',dict(parent_native_sha256=m['native_sha256'],probe_report_sha256=sha(probe/'report.json'),
    controls_sha256=sha(a.controls),layout_script_sha256=sha(H/'transmission_brake_front_layout.py'),
    definitions=definitions,occurrences=list(allrows.values()),affected_occurrences=affected,
    new_occurrences=new,revised_occurrences=revised,new_assemblies=groups,
    historical_geometry_qualified=False,installation_qualified=False))
def bounds(s):
    b=s.copy().cleaned().BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
names=sorted(shapes);boxes=np.array([bounds(shapes[n]) for n in names]);seen=set();checks=[]
for n in affected:
    one=shapes[n];bb=np.array(bounds(one))
    indices=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
    for i in indices:
        other=names[i];pair=tuple(sorted([n,other]))
        if n==other or pair in seen:continue
        seen.add(pair);common=one.common(shapes[other]);v=common.Volume
        checks.append(dict(first=n,second=other,volume_mm3=v,passed=abs(v)<1e-5))
    write(out/'progress.json',dict(last_occurrence=n,pairs=len(checks),failed=[v for v in checks if not v['passed']]))
    print(n,len(checks),'pairs',flush=True)
failed=[v for v in checks if not v['passed']]
write(out/'report.json',dict(passed=not failed,checks=checks,failed=failed,layout_sha256=sha(out/'layout.json'),
    new_count=len(new),revised_count=len(revised),affected_count=len(affected),total_occurrences=len(allrows),
    scope='All new and revised prototype occurrences against all retained development geometry; standard tank and saved-native hierarchy not yet checked.'))
print('Finished',len(checks),'pairs;',len(failed),'failures',failed,flush=True)
