"""Qualify the unintegrated adapter against the preserved native fixture."""
from pathlib import Path
import sys,subprocess,copy,math
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1];OUT=ROOT/'draft_check'
sys.path[:0]=[str(STAGE),str(ROOT)]
from lib.runtime import environment
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
import numpy as np
from lib.model import load
from lib.evidence import read,write,sha,fingerprint
from lib.roller_validation import bearing_face
from integration_draft.drive_mount_geometry import values,child_datum
from integration_draft.drive_mount_parts import build
lock=read(ROOT/'authored_input_fingerprint.json');assert fingerprint()==lock
native=ROOT/'build/DriveMountStudy.FCStd';assert sha(native)==read(ROOT/'build/report.json')['native_sha256']
fixture=App.openDocument(str(native));data=load()
controls=read(ROOT/'hypotheses.json')['values_mm']
controls.update(bearing_screw_head_af=31.75,bearing_screw_head_stock=12.7,
                locking_screw_head_af=22.225,locking_screw_head_stock=8.73125)
for key,value in controls.items():data['values']['drive_mount_'+key]=SimpleNamespace(value=value)
roles=list(read(ROOT/'source_rows.json'))
specs={'Shaft':dict(drive_mount_child='shaft'),'Key':dict(drive_mount_child='key'),
       'BackingPlate':dict(drive_mount_child='backing_plate'),'OilPlug':dict(drive_mount_child='oil_plug')}
for suffix,side in [('Inner',-1),('Outer',1)]:
    for prefix,role in [('Bearing','bearing'),('Nut','nut'),('LockingPlate','locking_plate'),('LockingScrew','locking_screw')]:
        specs[prefix+suffix]=dict(drive_mount_child=role,drive_mount_side=side)
for count,prefix,role in [(6,'BearingScrew','bearing_screw'),(6,'InnerRivet','inner_rivet'),(4,'BackingRivet','backing_rivet')]:
    for n in range(count):specs[prefix+str(n)]=dict(drive_mount_child=role,drive_mount_index=n)
assert len(specs)==28
original={link.Name:link for link in fixture.Fixture.Group};reports=[]
def bounds(s):
    b=s.optimalBoundingBox(False);return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
for trial,parameter,delta in [('nominal',None,0),('shaft_length','drive_mount_shaft_length',2),('frame_spacing','hull_frame_clear',10)]:
    candidate=copy.deepcopy(data)
    if parameter:candidate['values'][parameter]=SimpleNamespace(value=data['values'][parameter].value+delta)
    a=values(candidate);doc=App.newDocument('Draft_'+trial);targets={};transfer=[]
    for role in roles:
        target=build(doc,'Draft_'+role,{**a,'role':role});targets[role]=target
        assert target.Shape.isValid() and len(target.Shape.Solids)==1
        if trial=='nominal':
            expected=fixture.getObject('Def_'+role).Shape
            lost=expected.cut(target.Shape).Volume;added=target.Shape.cut(expected).Volume
            assert lost<1e-4 and added<1e-4,(role,lost,added)
            transfer.append(dict(role=role,lost_mm3=lost,added_mm3=added))
    items={}
    for name,link in original.items():
        role=link.LinkedObject.Name.removeprefix('Def_')
        shape=targets[role].Shape.copy() if role in targets else link.LinkedObject.Shape.copy()
        placement=link.Placement
        if name in specs:
            d=child_datum({**specs[name],'parent':'PortDrive_Unit000_Mounts'},candidate)
            placement=App.Placement(App.Vector(*d['translation']),App.Rotation(*d['rotation_deg']))
            if trial=='nominal':
                assert (placement.Base-link.Placement.Base).Length<1e-6,name
                assert placement.Rotation.isSame(link.Placement.Rotation,1e-7),name
        if trial=='frame_spacing' and name.startswith('Receiver'):
            # Receivers follow the independent shell spacing; thickness stays fixed.
            placement=App.Placement(App.Vector(0,-5 if name.endswith('Inner') else 5,0),App.Rotation()).multiply(placement)
        shape.Placement=placement.multiply(shape.Placement);items[name]=shape
    seats=[]
    for row in read(ROOT/'build/report.json')['bearing_faces']:
        gap,area=bearing_face(items[row['a']],items[row['b']])
        assert gap<1e-5 and area>1e-4,(trial,row,gap,area)
        seats.append(dict(a=row['a'],b=row['b'],gap_mm=gap,area_mm2=area))
    names=list(items);boxes=np.array([bounds(items[n]) for n in names]);tested=0;overlaps=[]
    for n,name in enumerate(names):
        b=boxes[n];near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
        for m in near:
            if m<=n:continue
            tested+=1;volume=items[name].common(items[names[m]]).Volume
            if volume>1e-5:overlaps.append(dict(a=name,b=names[m],volume_mm3=volume))
    assert not overlaps,(trial,overlaps)
    reports.append(dict(trial=trial,parameter=parameter,delta_mm=delta,transfer=transfer,
                        seats=seats,candidate_pairs=tested,overlaps=overlaps,passed=True))
    write(OUT/'report.json',dict(complete=False,trials=reports,authored_fingerprint=lock))
    App.closeDocument(doc.Name);print('DRAFT ADAPTER',trial,'passed',len(seats),'seats',tested,'pairs',flush=True)
write(OUT/'report.json',dict(complete=True,passed=True,trials=reports,authored_fingerprint=lock,
      script_sha256=sha(Path(__file__)),draft_sha256={p.name:sha(p) for p in (ROOT/'integration_draft').glob('*.py')},
      limitation='Draft adapter verified outside the delivered tank. Main registry, builders, source composition and full delivery still need integration.'))
assert fingerprint()==lock
App.closeDocument(fixture.Name)
