import sys,json,math
from pathlib import Path
stage=Path('cad/003_FullTank').resolve();root=stage/'experiments/drive_chains';sys.path[:0]=[str(stage),str(root)]
from lib import runtime
from lib.evidence import read,write
App,Gui=runtime.start_gui()
try:
 import Part,numpy as np
 from lib.cad_build import leaves
 from transmission_bevel_gear_parts import toothed_blanks,support_stack,thrust_bearing,gear_joints
 c={k:v['value'] for k,v in read(root/'transmission_bevel_gear_controls.json')['controls'].items()}
 doc=App.openDocument(str(root/'transmission_bevel_sleeve_build/TransmissionBevelSleeveCandidate.FCStd'));doc.recompute();old={i['id']:i for i in leaves(doc.Root)}
 base=App.openDocument(str(root/'transmission_sun_retention_build/TransmissionSunRetentionCandidate.FCStd'));base.recompute();baseline={i['id']:i for i in leaves(base.Root)}
 support,sd=support_stack(c,read(root/'transmission_bevel_sleeve_build/report.json')['dimensions'],read(root/'transmission_core_controls.json')['controls'],
 old['CenterTransmissionCore_cross_shaft']['target'].Shape,baseline['CenterTransmissionCore_bevel_case']['target'].Shape,baseline['CenterTransmissionCore_bevel_cover']['target'].Shape,
 old['PortSmallPlanetTrain_sun']['target'].Shape.BoundBox.YMin,old['PortTransmissionCore_high_drum']['target'].Shape.BoundBox.YMin)
 blanks,teeth=toothed_blanks(c,sd);joints,jd=gear_joints(c,blanks['wheel'],support['sleeve'],sd);support['sleeve']=joints['sleeve']
 bearings,bd=thrust_bearing(c,sd['thrust_limits_y_mm'][0])
 shape={'shaft':support['shaft'],'case':support['case'],'cover':support['cover'],'pinion':blanks['pinion']}
 for hand,sign in [('Port',1),('Starboard',-1)]:
  local={k:v for k,v in support.items() if k not in ['shaft','case','cover']}
  local.update({k:joints[k] for k in ['wheel','clutch_ring']});local.update({'bearing_'+k:v for k,v in bearings.items()})
  for row in jd['rivet_occurrences']:
   s=joints[row['key']].copy();s.translate(App.Vector(*row['position_mm']));local[row['key']+'_'+str(row['index'])]=s
  for key in ['sun','sun_bush']:local['existing_'+key]=old[hand+'SmallPlanetTrain_'+key]['target'].Shape.copy()
  local['existing_drum']=old[hand+'TransmissionCore_high_drum']['target'].Shape.copy()
  for k,s in local.items():
   s=s.copy()
   if sign<0:s.rotate(App.Vector(),App.Vector(1,0,0),180)
   shape[hand+'_'+k]=s
 clutch=joints['clutch'].copy();clutch.translate(App.Vector(0,c['forward_clutch_y'],0));shape['clutch']=clutch
 pairs=[];overlaps=[];names=list(shape)
 for i,name in enumerate(names):
  a=shape[name]
  for other in names[i+1:]:
   b=shape[other]
   if not a.BoundBox.intersect(b.BoundBox):continue
   v=a.common(b).Volume
   pairs.append(dict(a=name,b=other,overlap_mm3=v))
   if v>1e-5:overlaps.append(pairs[-1])
  write(Path('.work/transmission-bevel-gear-study/local_progress.json'),dict(last=name,pairs=len(pairs),overlaps=overlaps))
 print('PAIRS',len(pairs),'OVERLAPS',json.dumps(overlaps),flush=True)
 for name,s in shape.items():s.exportBrep(str(Path('.work/transmission-bevel-gear-study/local_shapes')/(name+'.brep')))
 write(Path('.work/transmission-bevel-gear-study/local_assembly_report.json'),dict(support=sd,teeth=teeth,joints=jd,bearings=bd,material_candidate_pairs=len(pairs),overlaps=overlaps,passed=not overlaps))
finally:runtime.close()
