"""Exercise local casting/attachment regeneration at two nearby axis hypotheses.

These are parameter checks, not posed tanks or qualified alternative whole
powertrains. Chain closure and surrounding hardware are outside this local scope.
"""
import argparse
import copy
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
STAGE=HERE.parents[1]
ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json')
assert read(out/'independent_checks.json')['local_frame_checks_passed']
assert sha(out/r['native_file'])==r['native_sha256']
m=read(out/'isolated/manifest.json');assert m['native_sha256']==r['native_sha256']
rows={v['name']:v for v in m['occurrences']}
import FreeCAD as App
import Part
from transmission_frame_parts import revised_bracket
from powertrain_frame_registration_parts import bevel_case,replay_features
from transmission_case_mount_parts import case_mount_parts
V=App.Vector
def load(path):
 s=Part.Shape();s.read(str(path));return s
def base(name):
 path=out/'baseline_shapes'/(name+'.brep');assert sha(path)==r['baseline_brep_hashes'][path.name];return load(path)
def definition(name):
 d=m['definitions'][name];path=Path(d['brep_path']);assert sha(path)==d['brep_sha256'];return load(path)
def world(name):
 row=rows[name];s=definition(row['definition']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def placed(shape,origin):
 s=shape.copy();s.translate(origin);return s
def area(one,two,x):
 def faces(s):return [f for f in s.Faces if type(f.Surface).__name__=='Plane' and abs(f.BoundBox.XMin-x)<1e-7 and abs(f.BoundBox.XMax-x)<1e-7]
 return sum(a.common(b).Area for a in faces(one) for b in faces(two))
fc,sc,cc=r['frame_controls'],r['support_controls'],r['core_controls']
original_axis=V(*r['original_axis_mm']);nominal_axis=V(*r['shaft_axis_mm'])
mr=read(HERE/'transmission_case_mount_trial_build/report.json')
prepath=HERE/'transmission_case_mount_trial_build/inputs/parent_case.brep'
assert sha(prepath)==mr['parent_case_brep_sha256']
premount=load(prepath)
channels={k:definition(rows['TransmissionFrame_'+label+'Channel']['definition']) for k,label in [('top','Top'),('bottom','Bottom')]}
nut=definition(rows['CaseMount_UpperPort_nut']['definition'])
expected_areas={end:area(world('CenterTransmissionCore_bevel_case'),world('TransmissionFrame_'+end+'Channel'),fc['frame_front_x']) for end in ['Top','Bottom']}
trials=[]
for label,dx,dz in [('lower_aft',-2.,-10.),('upper_forward',2.,10.)]:
 dest=out/'parameter_trials'/label;dest.mkdir(parents=True,exist_ok=True)
 axis=nominal_axis+V(dx,0,dz);dims=copy.deepcopy(r['original_bracket_dimensions']);checks=[];shapes={}
 def ck(name,value,target=0,tol=1e-5):checks.append(dict(name=name,actual=value,expected=target,passed=abs(value-target)<tol))
 for role in ['inner','outer']:
  for key in ['foot_aft_x_mm','foot_front_x_mm']:dims[role][key]-=axis.x-original_axis.x
  revised,_=revised_bracket(base(role+'_minimal'),role,fc,sc,dims,axis)
  original=base(role+'_original_base');detailed=base(role+'_detailed_before')
  final,_=replay_features(original,revised,detailed);shapes[role]=final
  add,remove=detailed.cut(original),original.cut(detailed)
  ck(role+' later bosses retained',add.cut(final).Volume if add.Solids else 0)
  ck(role+' later bore voids retained',remove.common(final).Volume if remove.Solids else 0)
  occurrence=placed(final,axis+V(0,rows['PortFixedBearing_'+role+'_bracket']['frame'][7],0))
  gap=r['original_bracket_dimensions'][role]['foot_aft_x_mm']-r['original_bracket_dimensions']['outer']['foot_aft_x_mm']
  for end in ['Top','Bottom']:
   frame=world('TransmissionFrame_'+end+'Channel')
   ck(role+'/'+end+' frame gap',occurrence.distToShape(frame)[0],gap,1e-6)
   ck(role+'/'+end+' no overlap',occurrence.common(frame).Volume)
   aligned=occurrence.copy();aligned.translate(V(-gap,0,0))
   ck(role+'/'+end+' full pad facing',area(aligned,frame,fc['frame_front_x']),dims[role]['foot_width_mm']*fc['channel_height'],1e-3)
 frame=dict(rear=fc['frame_front_x']-axis.x,top=fc['top_web_z']-axis.z,bottom=fc['bottom_web_z']-axis.z,height=fc['channel_height'])
 raw,_=bevel_case(cc,frame)
 detailed,_=replay_features(base('case_raw_original_base'),raw,premount)
 mc=dict(r['mount_controls'],frame_front_x=frame['rear'],top_web_z=frame['top'],bottom_web_z=frame['bottom'])
 _,revised,installed,datums=case_mount_parts(mc,detailed,channels,nut,mr['pin_controls'])
 shapes['case']=revised['case'];case=placed(shapes['case'],axis)
 for end in ['Top','Bottom']:
  channel=world('TransmissionFrame_'+end+'Channel')
  ck('case/'+end+' seat gap',case.distToShape(channel)[0],0,1e-6)
  ck('case/'+end+' no overlap',case.common(channel).Volume)
  ck('case/'+end+' full seat facing',area(case,channel,fc['frame_front_x']),expected_areas[end],1e-3)
 for joint in datums['mounts']:
  channel=world('TransmissionFrame_'+('Top' if joint['channel']=='Upper' else 'Bottom')+'Channel')
  stud=placed(installed[joint['name']+'_stud'],axis)
  washer=placed(installed[joint['name']+'_washer'],axis)
  ck(joint['name']+' bore clearance',stud.distToShape(case)[0],.15,1e-6)
  ck(joint['name']+' channel clearance',stud.distToShape(channel)[0],.15,1e-6)
  ck(joint['name']+' washer seating',washer.distToShape(channel)[0],0,1e-6)
 for name,s in shapes.items():
  checks.append(dict(name=name+' valid single casting',passed=s.isValid() and len(s.Solids)==1 and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1)))
  s.exportBrep(str(dest/(name+'.brep')))
 record=dict(name=label,axis_mm=list(axis),delta_from_nominal_mm=[dx,0,dz],checks=checks,
             passed=all(v['passed'] for v in checks),shape_hashes={p.name:sha(p) for p in dest.glob('*.brep')})
 write(dest/'checks.json',record);trials.append(record);print(label,record['passed'],len(checks),flush=True)
write(out/'parameter_checks.json',dict(passed=all(v['passed'] for v in trials),native_sha256=r['native_sha256'],
    probe_sha256=sha(Path(__file__)),builder_report_sha256=sha(out/'report.json'),trials=trials,
    scope='Local web, bore and frame-seat regeneration at two X/Z variations; no full assembly, STEP or chain-route qualification.',
    full_context_qualified=False,historical_station_qualified=False))
assert all(v['passed'] for v in trials)
