"""Audit the refined wheel hypothesis at all four standard installation axes."""
from pathlib import Path
import sys,subprocess
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
OUT=ROOT/'installed_fit_build'
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)

import FreeCAD as App
import numpy as np
from lib.evidence import read,write,sha,fingerprint
from lib.model import load
from lib.cad_build import leaves,frame
from lib.visual_review import shaded

lock=fingerprint()
assert lock==read(ROOT/'authored_input_fingerprint.json'),'Archived study inputs changed; review and explicitly rebase before regeneration'
data=load()
reference=ROOT/'reference_native';manifest=read(ROOT/'reference_native_manifest.json')
for relative,digest in manifest['files'].items():assert sha(reference/relative)==digest
base=App.openDocument(str(reference/'MarkVIII.FCStd'));original=leaves(base.Root)
path=ROOT/'common_fit_refined_build/CommonWheelInterfaceStudy.FCStd'
qualification=read(path.parent/'report.json')
assert sha(path)==qualification['native_sha256']
assert all(not r['overlaps'] for r in qualification['fixture_checks'])
fixture=App.openDocument(str(path));replacements=[]
for hand in ['port','starboard']:
    for kind in ['idler','drive']:
        group=fixture.getObject(kind.title()+'Fixture');placement=frame(hand+'_'+kind,data)
        for link in group.Group:
            target=link.LinkedObject;shape=target.Shape.copy()
            shape.Placement=placement.multiply(link.Placement).multiply(target.Shape.Placement)
            replacements.append(dict(id='Candidate_'+hand+'_'+link.Name,definition='candidate_'+target.Name,
                shape=shape,target=target,system='RunningGear',representation='assembly',hand=hand,kind=kind))
assert len(replacements)==484
removed=[i for i in original if i['definition'].startswith('wheel_')]
assert len(removed)==242
remaining=[i for i in original if not i['definition'].startswith('wheel_') and i['definition']!='drive_wheel']
physical=[i for i in remaining if i['representation']=='assembly']+replacements
def bounds(shape):
    b=shape.optimalBoundingBox(False)
    return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
boxes=np.array([bounds(i['shape']) for i in physical]);selected={i['id'] for i in replacements}
tested=0;overlaps=[]
for a in replacements:
    b=bounds(a['shape'])
    near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
    for index in near:
        other=physical[index]
        if other['id'] in selected and other['id']<=a['id']:continue
        tested+=1;volume=a['shape'].common(other['shape']).Volume
        if volume>1e-5:overlaps.append(dict(a=a['id'],b=other['id'],volume_mm3=volume))
    if tested and tested%100==0:print('MATERIAL CANDIDATES',tested,flush=True,file=sys.stderr)

doc=App.newDocument('InstalledWheelHypothesis');root=doc.addObject('App::Part','FourWheels')
for hand in ['port','starboard']:
    for kind in ['idler','drive']:
        group=doc.addObject('App::Part',hand.title()+kind.title());root.addObject(group)
        for item in replacements:
            if item['hand']!=hand or item['kind']!=kind:continue
            feature=doc.addObject('PartDesign::Feature',item['id']);feature.Shape=item['shape'];group.addObject(feature)
            feature.addProperty('App::PropertyString','Hypothesis');feature.Hypothesis='Unintegrated shared wheel interface study'
doc.recompute();native=OUT/'InstalledWheelHypothesis.FCStd';doc.saveAs(str(native))
visible=[i for i in remaining+replacements if i['definition'] not in
         {'central_hull','track_frame','track_path','track_pin','track_bushing','track_cotter','track_rivet'}]
shaded(visible,OUT/'candidate_standard.svg',(1,1,.6),'Wheel interface hypothesis | full context | not an integrated delivery')
drive=[i for i in replacements if i['hand']=='port' and i['kind']=='drive']
shaded(drive,OUT/'drive_detail.svg',(1,1,.6),'Drive-wheel hypothesis at recorded axis | shaft and supports absent')
assert fingerprint()==lock
write(OUT/'report.json',dict(complete=True,integrated=False,authored_fingerprint=lock,
    executed_script_sha256=sha(Path(__file__)),fixture_sha256=sha(path),native_sha256=sha(native),
    replaced_idler_components=len(removed),candidate_wheel_components=len(replacements),
    total_physical_components_in_audit=len(physical),material_candidate_pairs=tested,overlaps=overlaps,
    static_clearance_checks_passed=not overlaps,historical_profile_qualified=False,
    drive_shafts_and_supports_present=False,continuous_engagement_qualified=False,
    limitations=['This four-wheel file omits the context shown in candidate_standard.png; keep the source fixture and reference baseline for reproduction.',
                 'The 35-tooth hypothesis is only a working branch of an unresolved source conflict.',
                 'Native material clearance is not proof of motion, retention, or load transmission.']))
for name in list(App.listDocuments()):App.closeDocument(name)
print('INSTALLED WHEEL STUDY COMPLETE',tested,'pairs;',len(overlaps),'overlaps',flush=True,file=sys.stderr)
