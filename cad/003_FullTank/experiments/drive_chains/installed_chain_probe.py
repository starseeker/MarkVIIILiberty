"""Install both handed chain candidates against the verified current tank solids.

Save only the new candidates; use the existing tank as read-only context. This
does not replace the delivered assembly or alter its authored parameters.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'installed_chain_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve()
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import fingerprint,read,write,sha
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),
            '--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import numpy as np
    from lib.cad_build import leaves,metadata
    from lib.worker import check_build
    from lib.visual_review import shaded
    lock=fingerprint();build=check_build(stage/'build')
    candidate_native=ROOT/'chain_candidate_build/DriveChainCandidate.FCStd'
    candidate_report=read(ROOT/'chain_candidate_build/report.json')
    assert candidate_report['passed'] and sha(candidate_native)==candidate_report['native_sha256']
    tank=App.openDocument(build['build']['top_document']);tank.recompute();original=leaves(tank.Root)
    source=App.openDocument(str(candidate_native));source.recompute();prototype=leaves(source.Root)
    doc=App.newDocument('InstalledChainsCandidate');library=doc.addObject('App::Part','Definitions')
    root=doc.addObject('App::Part','Root');metadata(root,PhysicalRelease=False,
        Scope='Two candidate chains and replacement pinion castings; existing tank is external read-only comparison context')
    definitions={}
    for item in prototype:
        key=item['definition']
        if key in definitions:continue
        body=doc.addObject('PartDesign::Body','Def_'+key);library.addObject(body)
        feature=body.newObject('PartDesign::Feature','ReconstructedSolid');feature.Shape=item['target'].Shape
        metadata(body,DefinitionId=key,Representation='assembly',Coverage='partial',SurveyIds=item['target'].SurveyIds)
        definitions[key]=body
    for hand in ['Port','Starboard']:
        group=doc.addObject('App::Part',hand+'Chain');root.addObject(group)
        for item in prototype:
            pose=item['shape'].Placement
            if hand=='Starboard':
                # Bars and bushes are symmetric about local Y. Headed pins,
                # cotters and sprockets instead use their local X symmetry,
                # retaining a proper rigid transform while reversing Y.
                rotation=pose.Rotation
                if item['definition'] not in {'inner_bar','outer_bar','bush'}:
                    rotation=rotation.multiply(App.Rotation(App.Vector(0,0,1),180))
                pose=App.Placement(App.Vector(pose.Base.x,-pose.Base.y,pose.Base.z),rotation)
            name=hand+'Chain_'+item['id'];obj=doc.addObject('App::Link',name);group.addObject(obj)
            obj.setLink(definitions[item['definition']]);obj.LinkPlacement=pose
            metadata(obj,OccurrenceId=name,Subsystem='Drivetrain')
    library.Visibility=False;doc.recompute();native=out/'InstalledChainsCandidate.FCStd';doc.saveAs(str(native))
    App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute();new=leaves(doc.Root)
    assert len(new)==504
    for item in new:
        if not item['shape'].isValid() or len(item['shape'].Solids)!=1:raise ValueError('Invalid installed chain solid '+item['id'])
    # Each revised casting replaces exactly one old casting for this comparison.
    replaced={'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
    assert {i['id'] for i in original if i['id'] in replaced}==replaced
    context=[i for i in original if i['id'] not in replaced]
    all_physical=[i for i in context if i['representation']=='assembly']+new
    boxes=np.array([[s.XMin,s.YMin,s.ZMin,s.XMax,s.YMax,s.ZMax] for s in [i['shape'].BoundBox for i in all_physical]])
    ids={i['id'] for i in new};internal=external=0;overlaps=[];neighbors=set()
    for first in new:
        box=first['shape'].BoundBox;b=np.array([box.XMin,box.YMin,box.ZMin,box.XMax,box.YMax,box.ZMax])
        near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
        for n in near:
            second=all_physical[n]
            if second['id'] in ids:
                if second['id']<=first['id']:continue
                internal+=1
            else:external+=1;neighbors.add(second['id'])
            volume=first['shape'].common(second['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=first['id'],b=second['id'],volume_mm3=volume))
    byid={i['id']:i for i in new}
    handed_gaps=[]
    for n in range(50):
        pair=[]
        for hand in ['Port','Starboard']:
            pin=byid[hand+'Chain_Joint%02d_Pin'%n]['shape'];bush=byid[hand+'Chain_Joint%02d_Bush'%n]['shape']
            pair.append(bush.distToShape(pin)[0])
        if abs(pair[0]-pair[1])>1e-6:raise ValueError('Handed joint gap changed')
        handed_gaps.append(dict(joint=n,port_gap_mm=pair[0],starboard_gap_mm=pair[1]))
    views=[i for i in context if i['id'] in neighbors]+new
    shaded(views,out/'neighbors_oblique.svg',(1,1,.65),'Both chain candidates and nearby installed parts | diagnostic fit')
    shaded([i for i in views if not i['id'].startswith('Starboard') and not i['id'].startswith('hull_starboard')],
           out/'port_elevation.svg',(0,1,0),'Port chain installation | exact native neighbors; approximation remains explicit')
    # This full view is diagnostic; it is not a promoted numbered milestone.
    shaded(context+new,out/'installed_isometric.svg',(1,1,.65),'Standard tank with experimental chain candidates | not promoted')
    assert fingerprint()==lock;check_build(stage/'build')
    write(out/'report.json',dict(complete=True,passed=not overlaps,new_native_occurrences=len(new),
        replaced_existing_occurrences=sorted(replaced),internal_candidate_pairs=internal,
        external_candidate_pairs=external,overlaps=overlaps,handed_joint_clearances=handed_gaps,
        native_sha256=sha(native),tank_native_hashes=build['native_hashes'],authored_fingerprint=lock,
        candidate_native_sha256=sha(candidate_native),script_sha256=sha(__file__),
        standard_assembly_modified=False,source_bom_reconciled=False,transmission_shaft_fit_qualified=False,
        chain_casing_and_mounts_populated=False,lubrication_qualified=False,formed_retention_qualified=False,
        historical_fit_qualified=False,visual_review_status='pending'))
    print('Installed chain candidates:',internal,'internal,',external,'external,',len(overlaps),'overlaps',flush=True)
    sys.exit(0 if not overlaps else 1)
finally:
    runtime.close()
