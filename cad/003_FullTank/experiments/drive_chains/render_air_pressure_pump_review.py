"""Fixed source comparisons and a provisional pump/input-housing placement study."""
import argparse,base64,math,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=HERE/'air_pressure_pump_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.candidate.resolve();view=out/'source_review';view.mkdir(exist_ok=True)
if not a.worker:
    with (view/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],
            env=runtime.environment(view),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,fitz,numpy as np
    from lib.cad_build import leaves,COLORS
    from lib.visual_review import shaded
    from lib.worker import check_build
    report=read(out/'report.json');native=out/'AirPressurePump.FCStd';assert sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    src=REPO/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p279-geometry.png'
    scale=.47625;end_origin=[821,841];top_origin=[308,310]
    cal=dict(source=str(src.relative_to(REPO)),source_sha256=sha(src),mm_per_pixel=scale,
        end_origin_px=end_origin,top_origin_px=top_origin,source_warped=False,
        basis='Assumption-normalized visual comparison: assumed190.5mm pulley OD divided by approximately400px in the end view. Not independent dimensional calibration.',
        source_picks=dict(pulley_vertical_diameter_px=[645,1045],base_axial_ends_top_px=[156,458],
            bearing_width_end_px=[743,902],base_transverse_edges_top_px=[146,477]),
        limits=['Manual broad pixel picks; scan/aspect distortion retained.','Estimated absolute scale from HB115 shaft-end proportion remains unverified.','Side section is not used as a simple upright orthographic view of both inclined banks.'])
    write(view/'calibration.json',cal)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1115" height="1200">',
        '<text x="15" y="25" font-family="sans-serif" font-size="18">Air-pressure pump | fixed approximate-scale outline comparison</text>',
        '<text x="15" y="48" font-family="sans-serif" font-size="14">Green: modeled casting/parts; red: pulley circle. Assumed scale, not metrology.</text>',
        f'<image x="0" y="60" width="1115" height="1128" opacity=".68" href="data:image/png;base64,{base64.b64encode(src.read_bytes()).decode()}"/>']
    end_ids=['AirPump_base','AirPump_RearBearing','AirPump_RearBush','AirPump_AirHoleCover']
    end_ids += ['AirPump_RearBearingScrew'+str(i) for i in [1,2,3]]
    end_ids += ['AirPump_'+b+'1_'+k for b in ['Port','Starboard'] for k in ['cylinder','check_nut','displacement_plug','screw1','screw2']]
    top_ids=[i['id'] for i in items if i['definition'].removeprefix('air_pressure_pump_') not in ['piston','spring_high','spring_low','shaft','bush','key']]
    for names,origin,axes in [(end_ids,end_origin,'end'),(top_ids,top_origin,'top')]:
        for n in names:
            for edge in byid[n]['shape'].Edges:
                points=[]
                for v in edge.discretize(Deflection=.2):
                    u,w=(v.y,v.z) if axes=='end' else (v.x,v.y)
                    points.append(f'{origin[0]-u/scale:.2f},{origin[1]-w/scale+60:.2f}')
                svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#197a43" stroke-width=".8" opacity=".65"/>')
    svg.append(f'<circle cx="{end_origin[0]}" cy="{end_origin[1]+60}" r="{report["controls"]["pulley_radius"]/scale}" fill="none" stroke="#ae3022" stroke-width="1.5"/>')
    svg.append('</svg>');path=view/'source_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    # Inspect the proposed location without changing or resaving the transmission.
    parent=HERE/'transmission_case_mount_trial_build';q=read(parent/'qualification.json')
    trans=parent/'MX5CaseMountTrial.FCStd';assert q['passed'] and sha(trans)==q['native_sha256']
    td=App.openDocument(str(trans));td.recompute();context=leaves(td.Root)
    offset=td.TransmissionCore.Placement.Base+App.Vector(*report['controls']['inspection_position_core_xyz'])
    installed=[]
    for item in items:
        new=dict(item);shape=item['shape'].copy();shape.translate(offset)
        new.update(shape=shape,target=SimpleNamespace(Shape=shape),definition=item['id'])
        installed.append(new)
    COLORS['PumpContext']=(.74,.53,.26)
    shown=[dict(i,system='PumpContext') for i in installed]
    nearby=[i for i in context if i['id'].startswith(('InputHousing_','InputMount_','InputFeed_')) or i['id']=='CenterTransmissionCore_bevel_cover']
    shaded(shown+nearby,view/'installation_study.svg',(1,1,.5),
        'Air pump above transmission input | proposed position; mounts and belt absent')
    print('Source views saved; loading standard physical context.',flush=True)
    standard=check_build(STAGE/'build');tank=App.openDocument(standard['build']['top_document']);tank.recompute()
    surrounding=context+[i for i in leaves(tank.Root) if i['representation']=='assembly']
    boxes=[i['shape'].copy().cleaned().BoundBox for i in surrounding];pairs=[]
    print('Loaded',len(surrounding),'context leaves; checking proposed placement.',flush=True)
    for new in installed:
        b=new['shape'].copy().cleaned().BoundBox
        for other,ob in zip(surrounding,boxes):
            if not b.intersect(ob):continue
            v=new['shape'].common(other['shape']).Volume
            pairs.append(dict(pump=new['id'],context=other['id'],intersection_mm3=v))
        write(view/'placement_progress.json',dict(last_id=new['id'],checked_pairs=len(pairs),conflicts=[p for p in pairs if p['intersection_mm3']>1e-5]))
    conflicts=[p for p in pairs if p['intersection_mm3']>1e-5]
    write(view/'placement_study.json',dict(proposed_core_xyz=report['controls']['inspection_position_core_xyz'],
        proposed_world_xyz=list(offset),checked_pairs=len(pairs),conflicts=conflicts,pairs=pairs,
        passed_no_material_overlap=not conflicts,accepted_vehicle_placement=False,
        scope='Static proposed pump location against accepted transmission and current standard physical solids. Supports,clutch/drive pulley,belt,air lines and remaining interiors absent; clear space alone does not qualify installation.',
        pump_native_sha256=sha(native),transmission_native_sha256=sha(trans),standard_native_hashes=standard['native_hashes']))
    write(view/'render_receipt.json',dict(native_sha256=sha(native),source_sha256=sha(src),
        renderer_sha256=sha(Path(__file__)),calibration_sha256=sha(view/'calibration.json'),
        rasters={p.name:sha(p) for p in view.glob('*.png')}))
    assert sha(trans)==q['native_sha256'] and sha(native)==report['native_sha256']
    print('Source and placement views saved;',len(pairs),'context pairs, conflicts:',conflicts,flush=True)
finally:runtime.close()
