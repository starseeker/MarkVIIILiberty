"""Read-only coupled source-layout trial, including real pump/drive BReps.

Keep the estimated oil-pump shape unchanged to expose the consequences of the
new printed levels separately from the necessary radial reconstruction. The
floor-relative engine elevation is only a hypothesis: no global drivetrain or
receiving case is rebuilt or approved by this diagnostic.
"""
import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
import FreeCAD as App
import Part
from lib.cad_build import leaves,COLORS
from lib.evidence import read,write,sha
from detail_render import shaded_detail

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=HERE/'engine_pump_layout_study')
p.add_argument('--render',action='store_true')
a=p.parse_args();out=a.candidate.resolve();out.mkdir(parents=True,exist_ok=True)
source=read(out/'source_constraints.json')
oil_dir=HERE/'engine_oil_pump_mounting_study'
water_dir=HERE/'engine_water_pump_connections_study'
driver_dir=out/'lower_drive_trial'
orr,wrr,drr=[read(q/'report.json') for q in [oil_dir,water_dir,driver_dir]]
natives=[oil_dir/orr['native_file'],water_dir/wrr['native_file'],driver_dir/'DrivetrainWithLowerDriveStudy.FCStd']
for path,r in zip(natives,[orr,wrr,drr]):assert sha(path)==r['native_sha256'],path
oil_doc,water_doc,driver_doc=[App.openDocument(str(q)) for q in natives]
try:
    inverse=water_doc.TankLibertyEngine.getGlobalPlacement().inverse()
    driver_inverse=driver_doc.TankLibertyEngine.getGlobalPlacement().inverse()
    oil_pose=App.Placement(App.Vector(orr['controls']['pump_axis_x'],0,
        source['oil_mount_from_ports']['selected_for_diagnostic_z_mm']),App.Rotation())
    shapes={};roles={}
    def store(name,shape,pose,role):
        s=shape.copy();s.Placement=pose.multiply(s.Placement);shapes[name]=s;roles[name]=role
    for row in orr['occurrences']:
        obj=oil_doc.getObject(row['name'])
        pose=oil_pose.multiply(oil_doc.getObject(row['assembly']).getGlobalPlacement()).multiply(obj.LinkPlacement)
        store(row['name'],obj.LinkedObject.Shape,pose,'LayoutOil')
    water_raise=wrr['controls'].get('pump_axis_drop',184)-171.45 if 'pump_axis_drop' in wrr['controls'] else -wrr['pump_axis_z']-171.45
    # Water-pump pose changes with the common drive apex; internal geometry is
    # preserved. Its obsolete receiving pads are intentionally NOT relocated.
    for row in leaves(water_doc.Root):
        name=row['id']
        if name.startswith('EngineWaterPump_'):
            pose=App.Placement(App.Vector(0,0,water_raise),App.Rotation()).multiply(inverse)
            store(name,row['shape'],pose,'LayoutWater')
        elif name=='EngineCase_lower':store(name,row['shape'],inverse,'LayoutCase')
        elif name=='hull_floor_5':store(name,row['shape'],inverse,'LayoutFloor')
    for row in leaves(driver_doc.Root):
        if row['id'].startswith('EngineLowerDrive_'):
            store(row['id'],row['shape'],driver_inverse,'LayoutDrive')
    oil_names=[r['name'] for r in orr['occurrences']]
    drive_names=[n for n in shapes if roles[n] in ['LayoutWater','LayoutDrive']]
    def overlap(s,t):
        return abs(s.common(t).Volume) if s.BoundBox.intersect(t.BoundBox) else 0.
    # All oil constituents against all revised moving-drive/pump constituents;
    # bbox screening discards only demonstrably separated pairs.
    pairs=[]
    for name in oil_names:
        for other in drive_names:
            if not shapes[name].BoundBox.intersect(shapes[other].BoundBox):continue
            v=overlap(shapes[name],shapes[other])
            pairs.append(dict(a=name,b=other,overlap_mm3=v,clear=v<1e-5))
            write(out/'coupled_layout_progress.json',dict(completed=len(pairs),pairs=pairs))
    case_pairs=[]
    case=shapes['EngineCase_lower']
    for name in oil_names:
        if not shapes[name].BoundBox.intersect(case.BoundBox):continue
        v=overlap(shapes[name],case)
        case_pairs.append(dict(a=name,b='EngineCase_lower',overlap_mm3=v,clear=v<1e-5))
    floor=shapes['hull_floor_5'];floors=[]
    for alternative in source['layout_alternatives']:
        shift=alternative['engine_axis_world_z_mm']-wrr['engine_origin'][2]
        f=floor.copy();f.translate(App.Vector(0,0,-shift))
        near=[dict(a=name,overlap_mm3=overlap(shapes[name],f)) for name in oil_names
              if shapes[name].BoundBox.intersect(f.BoundBox)]
        gap=min(shapes[n].BoundBox.ZMin for n in oil_names)-f.BoundBox.ZMax
        floors.append(dict(name=alternative['name'],floor_top_engine_z_mm=f.BoundBox.ZMax,
            envelope_gap_mm=gap,material_pairs=near,collisions=[r for r in near if r['overlap_mm3']>=1e-5]))
    result=dict(status='Coupled source layout diagnostic; receiving case and global installation unqualified',
        source_constraints_sha256=sha(out/'source_constraints.json'),checker_sha256=sha(Path(__file__)),
        native_inputs={str(p):sha(p) for p in natives},oil_occurrences=len(oil_names),
        water_and_lower_drive_occurrences=len(drive_names),water_raise_mm=water_raise,
        oil_pose=list(oil_pose.toMatrix().A),pump_to_drive_pairs=pairs,
        pump_to_drive_collisions=[r for r in pairs if not r['clear']],
        obsolete_case_pairs=case_pairs,obsolete_case_collisions=[r for r in case_pairs if not r['clear']],
        floor_hypotheses=floors,
        source_documents_unchanged=all(sha(path)==r['native_sha256'] for path,r in zip(natives,[orr,wrr,drr])),
        standard_assembly_modified=False,installation_qualified=False,
        limitations=['Oil-pump radial geometry remains the prior oversized study.',
            'Only oil-pump interactions are checked here. Revised drive against stale case/water mounts and complete tank is not qualified.',
            'Floor-relative engine elevation remains hypothetical; clutch, supports, controls and chain geometry need coordinated registration.',
            'Receiving case shown unchanged to expose the remaining conflicts; stud seating is not established.'])
    write(out/'coupled_layout_checks.json',result)
    if a.render:
        COLORS.update(LayoutCase=(.60,.65,.63),LayoutWater=(.42,.66,.76),
            LayoutOil=(.80,.66,.42),LayoutFloor=(.77,.36,.35),LayoutDrive=(.59,.61,.67))
        # Common engine frame, so the alternative engine-height hypotheses are
        # represented by moving only the display floor, never physical source files.
        cut=Part.makeBox(480,145,530,App.Vector(1010,0,-420))
        for index,floor_trial in enumerate(floors):
            items=[]
            for name,s in shapes.items():
                displayed=s.copy()
                if name=='hull_floor_5':displayed.translate(App.Vector(0,0,floor_trial['floor_top_engine_z_mm']-floor.BoundBox.ZMax))
                if not displayed.BoundBox.intersect(cut.BoundBox):continue
                displayed=displayed.common(cut)
                if not displayed.Solids:continue
                items.append(dict(shape=displayed,target=SimpleNamespace(Shape=displayed),
                    definition=name,system=roles[name],representation='assembly'))
            title=('Source pump levels | inherited floor datum' if index==0 else
                   'Source pump levels | hypothetical floor-relative engine datum')
            shaded_detail(items,out/('layout_'+floor_trial['name']+'.svg'),(0,-1,0),title,.08)
        write(out/'coupled_render_receipt.json',dict(checks_sha256=sha(out/'coupled_layout_checks.json'),
            renderer_sha256=sha(Path(__file__)),images={f.name:sha(f) for f in out.glob('layout_*.png')},
            display_cut=dict(x=[1010,1490],y=[0,145],z=[-420,110]),installation_qualified=False))
    print(dict(pump_drive_collisions=len(result['pump_to_drive_collisions']),
               stale_case_collisions=len(result['obsolete_case_collisions']),
               floor_gaps=[r['envelope_gap_mm'] for r in floors]),flush=True)
finally:
    for doc in [oil_doc,water_doc,driver_doc]:App.closeDocument(doc.Name)
