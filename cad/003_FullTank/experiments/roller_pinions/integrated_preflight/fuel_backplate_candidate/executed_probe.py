"""Rebuild only the three owned fuel-enclosure plates; check their real neighbors."""
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent;STAGE=ROOT/'cad/003_FullTank';OUT=ROOT/'runs/fuel_backplate_candidate'
sys.path.insert(0,str(STAGE))
from lib import runtime
from lib.evidence import fingerprint,sha,write
if '--worker' not in sys.argv:
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(OUT),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    from lib.model import load,geometry_arguments
    from lib.cad_build import leaves,part,frame
    from lib.hull_validation import validate as validate_hull
    from lib.pinion_validation import validate as validate_pinions
    from lib.visual_review import shaded
    lock=fingerprint();data=load();doc=App.openDocument(str(STAGE/'build/native/MarkVIII.FCStd'))
    doc.recompute();items=leaves(doc.Root);definitions={'hull_fuel_back','hull_floor_fuel','hull_roof_fuel'}
    candidate=App.newDocument('FuelBackplateCandidate');old={};native=OUT/'FuelBackplateCandidate.FCStd'
    for key in sorted(definitions):
        definition=data['definitions'][key]
        part(candidate,key,definition,geometry_arguments(definition,data))
    candidate.recompute();candidate.saveAs(str(native));App.closeDocument(candidate.Name)
    candidate=App.openDocument(str(native));candidate.recompute()
    nodes={i['id']:i for i in data['occurrences']}
    for i in items:
        if i['definition'] not in definitions:continue
        old[i['id']]=i['shape']
        i['target']=candidate.getObject('Def_'+i['definition']);i['shape']=i['target'].Shape.copy()
        i['shape'].Placement=frame(nodes[i['id']]['frame'],data).multiply(i['shape'].Placement)
        assert i['shape'].isValid()
    print('Checking all hull/track and new pinion interfaces after the three-plate change',flush=True)
    hull=validate_hull(data,items,OUT);pinions=validate_pinions(data,items,OUT)
    byid={i['id']:i for i in items};wall=byid['hull_fuel_back']['shape']
    gap=[dict(id=i['id'],gap_mm=wall.distToShape(i['shape'])[0]) for i in items
         if i['id'].startswith(('PortPinion_','StarboardPinion_')) and i['definition']=='pinion_inner_bearing']
    view=[i for i in items if i['definition'] in definitions or i['id'] in {'hull_port_inner_rear_end','hull_port_inner_fuel_side'} or i['id'].startswith('PortPinion_')]
    for name,direction in [('oblique',(1,1,.65)),('plan',(0,0,1))]:
        shaded(view,OUT/(name+'.svg'),direction,'Pinion / fuel compartment | inferred backplate station candidate')
    write(OUT/'report.json',dict(passed=True,authored_fingerprint=lock,native_sha256=sha(native),
        changed_definitions=sorted(definitions),hull=hull,pinions=pinions,backplate_bearing_clearances=gap,
        plate_station_pixel=1642,old_plate_station_pixel=1630,historical_fit_qualified=False,visual_review_status='pending'))
    shutil.copy2(__file__,OUT/'executed_probe.py');assert fingerprint()==lock
finally:
    runtime.close()
