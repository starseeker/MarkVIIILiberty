"""Rebuild the support stack for two coupled belt-reference assumptions."""
import argparse,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'air_pump_mount_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();candidate=a.candidate.resolve();out=candidate/'variants';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(candidate),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves
    from air_pump_mount_parts import build
    r=read(candidate/'report.json');native=candidate/'TransmissionWithAirPump.FCStd';assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();origin=doc.TransmissionCore.Placement.Base
    rows=leaves(doc.Root);old={}
    for i in rows:
        s=i['shape'].copy();s.translate(-origin);old[i['id']]=s
    cover=Part.Shape();cover.read(str(candidate/'inputs/parent_cover.brep'))
    house=Part.Shape();house.read(str(candidate/'inputs/parent_housing.brep'))
    old_pump=App.Vector(*r['details']['pump_origin']);variants=[]
    for radial_shift in [-r['controls']['belt_reference_radius_uncertainty'],r['controls']['belt_reference_radius_uncertainty']]:
        c=dict(r['controls']);c['belt_pump_pitch_radius']+=radial_shift;c['belt_drive_pitch_radius']+=radial_shift
        parts,occ,revised,d=build(c,r['pump_controls'],cover,house)
        allshapes={n:s.copy() for n,s in old.items() if n not in r['new_ids']+r['changed_ids']}
        allshapes['CenterTransmissionCore_bevel_cover']=revised['cover'];allshapes['InputHousing_housing']=revised['housing']
        for row in occ:
            s=parts[row['key']].copy();s.translate(App.Vector(*row['xyz']));allshapes[row['name']]=s
        for n in r['new_ids']:
            if n.startswith('AirPump_'):
                s=old[n].copy();s.translate(App.Vector(*d['pump_origin'])-old_pump);allshapes[n]=s
        pairs=[];seen=set();names=list(allshapes)
        boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [s.copy().cleaned().BoundBox for s in allshapes.values()]])
        for n in r['new_ids']+r['changed_ids']:
            s=allshapes[n];assert s.isValid() and len(s.Solids)==1,n
            b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for j in near:
                other=names[j];pair=tuple(sorted([n,other]))
                if n==other or pair in seen:continue
                seen.add(pair);v=s.common(allshapes[other]).Volume
                pairs.append(dict(a=n,b=other,intersection_mm3=v))
            write(out/'progress.json',dict(radial_shift=radial_shift,last=n,pairs=len(pairs)))
        contacts=[]
        for side in ['Port','Starboard']:
            prefix='PumpMount_'+side
            for a,b in [(prefix+'_Bracket','AirPump_base'),(prefix+'_Bracket','CenterTransmissionCore_bevel_cover'),
                        (prefix+'_MX99_LowerWasher',prefix+'_Bracket'),(prefix+'_MX99_UpperWasher',prefix+'_Bracket'),
                        (prefix+'_MX99_SmallNut',prefix+'_MX99_UpperWasher'),(prefix+'_MX102_JamNut','InputHousing_housing')]:
                gap=allshapes[a].distToShape(allshapes[b])[0]
                contacts.append(dict(a=a,b=b,gap_mm=gap,passed=gap<1e-5))
            for n in [1,2]:
                for a,b in [(prefix+f'_Base{n}_Bolt','AirPump_base'),(prefix+f'_Base{n}_Washer',prefix+'_Bracket')]:
                    gap=allshapes[a].distToShape(allshapes[b])[0]
                    contacts.append(dict(a=a,b=b,gap_mm=gap,passed=gap<1e-5))
        bad=[p for p in pairs if p['intersection_mm3']>1e-5]
        trial=dict(radial_shift=radial_shift,center_height_mm=d['pump_origin'][2],physical_count=len(allshapes),
            checked_pairs=len(pairs),conflicts=bad,contacts=contacts,passed=not bad and all(r['passed'] for r in contacts))
        variants.append(trial);write(out/'report.json',dict(passed=all(v['passed'] for v in variants),variants=variants,
            native_sha256=sha(native),checker_sha256=sha(Path(__file__)),parts_sha256=sha(HERE/'air_pump_mount_parts.py'),
            scope='Two coupled pitch-radius changes; rebuilt supports and stud lengths with unchanged pump core; affected pairs against1490-piece transmission/pump context. Does not prove arbitrary uncertainty domain or historical belt fit.'))
        print('Variant',radial_shift,'height',d['pump_origin'][2],'pairs',len(pairs),'conflicts',bad,flush=True)
    assert all(v['passed'] for v in variants)
finally:runtime.close()
