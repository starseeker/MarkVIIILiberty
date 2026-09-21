"""Two coupled drawing-scale scenarios; these are not manufacturing tolerances."""
import argparse,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_drive_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();base=a.candidate.resolve();out=base/'variants';out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves
    from lib.worker import check_build
    from clutch_drive_parts import build
    from air_pump_mount_parts import build as mounts
    from air_pressure_pump_parts import build as pump
    report=read(base/'report.json');native=base/'TransmissionWithClutchDrive.FCStd';native_hash=sha(native)
    assert native_hash==report['native_sha256']
    inp=read(HERE/'transmission_input_controls.json')
    cv=Part.Shape();cv.read(str(HERE/'air_pump_mount_build/inputs/parent_cover.brep'))
    hs=Part.Shape();hs.read(str(HERE/'air_pump_mount_build/inputs/parent_housing.brep'))
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document']);td.recompute()
    context=[i for i in leaves(td.Root) if i['representation']=='assembly'];scenarios=[]
    for radial,scale in [(-6,.85),(6,1.15)]:
        c=dict(report['controls']);pc=dict(report['pump_controls']);mc=dict(report['mount_controls'])
        for k in ['drum_radius','drum_inside','drum_groove_inside','box_neck_radius','box_outer_radius']:c[k]+=radial
        pc['pulley_radius']+=radial
        for k in ['shaft_length','shaft_radius','spline_radius','spline_root_radius','spline_width']:c[k]*=scale
        parts,occ,flange,d=build(c,pc,inp['stack'],inp['bearing'])
        mc['belt_drive_pitch_radius']=d['belt']['drive_pitch_radius'];mc['belt_pump_pitch_radius']=d['belt']['pump_pitch_radius']
        mp,mo,_,md=mounts(mc,pc,cv,hs);pp,_,_=pump(pc)
        doc=App.openDocument(str(native));doc.recompute()
        for key,s in parts.items():doc.getObject('Def_ClutchDrive_'+key).Tip.Shape=s
        for key,s in mp.items():doc.getObject('Def_PumpMount_'+key).Tip.Shape=s
        for row in mo:doc.getObject(row['name']).LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation())
        doc.AirPressurePump.Placement=App.Placement(App.Vector(*md['pump_origin']),App.Rotation())
        leaves0={i['id']:i for i in leaves(doc.Root)}
        leaves0['AirPump_pulley']['target'].Tip.Shape=pp['pulley']
        leaves0['InputHousing_coupling']['target'].Tip.Shape=flange
        doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
        affected=report['affected_ids'];physical=items+context
        boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
        pairs=[];seen=set()
        for n in affected:
            s=byid[n]['shape'];assert s.isValid() and len(s.Solids)==1,n
            b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for idx in near:
                other=physical[idx];pair=tuple(sorted([n,other['id']]))
                if n==other['id'] or pair in seen:continue
                seen.add(pair);v=s.common(other['shape']).Volume;pairs.append(dict(a=n,b=other['id'],intersection_mm3=v))
        contacts=[]
        def contact(a,b,want=0):
            value=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
            contacts.append(dict(a=a,b=b,gap_mm=value,expected_gap_mm=want,passed=abs(value-want)<1e-5))
        contact('ClutchDrive_belt','AirPump_pulley');contact('ClutchDrive_belt','ClutchDrive_drum')
        contact('ClutchDrive_drum','InputHousing_coupling')
        for n in [1,2]:
            contact('ClutchDrive_HalfCover'+str(n),'ClutchDrive_drum')
            contact('ClutchDrive_HalfCover'+str(n),'ClutchDrive_box')
        for row in md['datums']:
            prefix='PumpMount_'+row['side'];contact('AirPump_base',prefix+'_Bracket')
            for part in ['MX98_Nut','MX99_LowerWasher','MX99_UpperWasher']:contact(prefix+'_'+part,prefix+'_Bracket')
            for n in [1,2]:
                contact(prefix+f'_Base{n}_Bolt','AirPump_base')
                contact(prefix+f'_Base{n}_Washer',prefix+'_Bracket')
                contact(prefix+f'_Base{n}_Nut',prefix+f'_Base{n}_Washer')
        conflicts=[r for r in pairs if r['intersection_mm3']>1e-5]
        scenario=dict(radial_shift_mm=radial,shaft_dimension_factor=scale,pump_origin=md['pump_origin'],native_occurrences=len(items),
            material_pairs=len(pairs),overlaps=conflicts,contacts=contacts,passed=not conflicts and all(x['passed'] for x in contacts))
        write(out/('smaller.json' if radial<0 else 'larger.json'),dict(**scenario,pairs=pairs));scenarios.append(scenario)
        write(out/'progress.json',dict(completed=len(scenarios),scenarios=scenarios));print('Scenario',radial,'passed',scenario['passed'],'overlaps',json.dumps(conflicts),flush=True)
        App.closeDocument(doc.Name)
    assert sha(native)==native_hash
    result=dict(passed=all(s['passed'] for s in scenarios),scenarios=scenarios,native_sha256=native_hash,
        input_hashes={str(HERE.joinpath(n).relative_to(REPO)):sha(HERE/n) for n in ['clutch_drive_parts.py','air_pump_mount_parts.py','air_pressure_pump_parts.py']},
        checker_sha256=sha(Path(__file__)),standard_native_hashes=standard['native_hashes'],
        scope='Two sampled coupled radius/profile and shaft-size scenarios with full transmission and physical standard context. No exhaustive uncertainty or load qualification.')
    write(out/'report.json',result);sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
