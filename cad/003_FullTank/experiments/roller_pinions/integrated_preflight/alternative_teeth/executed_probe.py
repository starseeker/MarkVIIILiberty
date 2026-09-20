"""Measure the historical37-tooth alternative against the current pinion fixture."""
from pathlib import Path
import copy
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent;STAGE=ROOT/'cad/003_FullTank'
OUT=ROOT/'runs/alternative_teeth';SOURCE=STAGE/'experiments/roller_pinions/installation_build/PairedPinionDriveStudy.FCStd'
sys.path.insert(0,str(STAGE))
from lib import runtime
from lib.evidence import fingerprint,sha,write,read
if '--worker' not in sys.argv:
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(OUT),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    from lib.model import load,geometry_arguments
    from lib.parameters import resolve
    from lib.cad_build import part
    lock=fingerprint();data=load();data['parameters']['drive_teeth']['value']=37
    data['values']=resolve(data['parameters'])
    expected=read(SOURCE.parent/'report.json')['native_sha256'];assert sha(SOURCE)==expected
    fixture=App.openDocument(str(SOURCE));fixture.recompute()
    candidate=App.newDocument('Alternative37Teeth');definition=data['definitions']['drive_rim']
    target=part(candidate,'drive_rim',definition,geometry_arguments(definition,data));candidate.recompute()
    path=OUT/'Alternative37Teeth.FCStd';candidate.saveAs(str(path));App.closeDocument(candidate.Name)
    candidate=App.openDocument(str(path));candidate.recompute();target=candidate.getObject('Def_drive_rim')
    pairs=[];overlaps=[];rings=0
    for link in fixture.Objects:
        if link.TypeId!='App::Link' or link.LinkedObject.Name!='Def_Drive_drive_rim':continue
        rings+=1;ring=target.Shape.copy();ring.Placement=link.Placement.multiply(ring.Placement)
        hand='Port' if link.Name.startswith('Port') else 'Starboard'
        for other in fixture.Objects:
            if other.TypeId!='App::Link' or not other.Name.startswith(hand+'Pinion_'):continue
            shape=other.LinkedObject.Shape.copy();shape.Placement=other.Placement.multiply(shape.Placement)
            if not ring.BoundBox.intersect(shape.BoundBox):continue
            volume=ring.common(shape).Volume;row=dict(ring=link.Name,pinion_part=other.Name,volume_mm3=volume)
            pairs.append(row)
            if volume>1e-5:overlaps.append(row)
    assert rings==4
    write(OUT/'report.json',dict(measurement_completed=True,alternative_teeth=37,rings=rings,
        pinion_phase_deg=17.21,candidates=len(pairs),overlaps=overlaps,
        current_static_installation_clear=not overlaps,source_conflict_resolved=False,
        inference='This tests only the current fixed station and phase, not every possible37-tooth reconstruction.',
        authored_fingerprint=lock,fixture_sha256=expected,candidate_sha256=sha(path)))
    shutil.copy2(__file__,OUT/'executed_probe.py');assert fingerprint()==lock
    print('37-tooth alternative:',len(overlaps),'overlaps',flush=True)
finally:
    runtime.close()
