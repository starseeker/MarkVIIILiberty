"""Preflight the two new mounted-shaft trials before promotion to the main delivery."""
from pathlib import Path
import sys,subprocess,copy,time,shutil
STAGE=Path('/tmp/drive-mount-integration-repo/cad/003_FullTank');OUT=STAGE/'mount_trial_preflight'
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
from lib import runtime
App,Gui=runtime.start_gui()
from lib.evidence import read,write,sha,fingerprint
from lib.model import load
from lib.parameters import resolve
from lib.cad_build import build,leaves,shape_signature
from lib.worker import check_build,reopen_saved,same_shape
from lib.wheel_validation import validate as validate_wheels
from lib.hull_validation import validate as validate_hull
from lib.roller_validation import validate as validate_rollers
from lib.lower_support_validation import validate as validate_lower_supports
try:
 lock=fingerprint();nominal=check_build(STAGE/'build');baseline=nominal['geometry'];data=load();reports=[]
 write(OUT/'report.json',dict(complete=False,authored_fingerprint=lock,trials=[]))
 for parameter,delta,trial in [('drive_mount_shaft_length',2,'drive_shaft_length_change'),('hull_frame_clear',10,'drive_frame_spacing_change')]:
  assert fingerprint()==lock;start=time.monotonic();print('START',trial,flush=True)
  changed=copy.deepcopy(data);changed['parameters'][parameter]['value']+=delta
  if parameter=='hull_frame_clear':changed['parameters'][parameter]['bounds'][1]+=delta
  changed['values']=resolve(changed['parameters']);folder=OUT/trial
  # Cache reuse is allowed here; the main release still tests an independent build.
  for rel in ['cache','native/library']:
   shutil.copytree(STAGE/'build'/rel,folder/rel,dirs_exist_ok=True)
  doc,stats=build(changed,folder);doc=reopen_saved(doc);items=leaves(doc.Root)
  checks=validate_wheels(changed,items,folder);altered={i['id']:shape_signature(i['shape']) for i in items};ids=[]
  if parameter=='drive_mount_shaft_length':
   affected={'drive_shaft','drive_key','idler_nut','roller_plug','drive_inner_bearing','drive_outer_bearing','drive_locking_plate','drive_locking_screw','drive_bearing_screw','drive_inner_rivet'}
   for item in items:
    k=item['id'];different=not same_shape(baseline[k],altered[k]);wanted=k.startswith(('PortDrive_','StarboardDrive_')) and item['definition'] in affected
    if different!=wanted:raise ValueError('Unexpected shaft-length propagation: '+k)
    if different:ids.append(k)
   assert len(ids)==46
   dependencies={'fixed_hull_faces_and_wheels':True,'shaft_end_fittings_follow':True}
  else:
   dependencies={'hull':validate_hull(changed,items,folder),'rollers':validate_rollers(changed,items,folder),'lower_supports':validate_lower_supports(changed,items,folder)}
   for item in items:
    k=item['id'];different=not same_shape(baseline[k],altered[k])
    if item['definition'] in {'drive_shaft','drive_key'} or '_ShaftAssembly_Nut' in k and 'Drive_' in k:
     if different:raise ValueError('Frame spacing moved a fixed drive-shaft end fitting: '+k)
    if different:ids.append(k)
   assert ids
  reports.append(dict(trial=trial,parameter=parameter,delta_mm=delta,affected_occurrences=ids,reopened_contacts=checks,dependencies=dependencies,seconds=time.monotonic()-start,passed=True))
  write(OUT/'report.json',dict(complete=False,authored_fingerprint=lock,trials=reports));print('PASS',trial,len(ids),'affected',flush=True)
 assert fingerprint()==lock
 write(OUT/'report.json',dict(complete=True,passed=True,authored_fingerprint=lock,trials=reports,script_sha256=sha(__file__)))
 shutil.copy2(__file__,OUT/'executed_check.py');print('MOUNT TRIAL PREFLIGHT PASS',flush=True)
finally:runtime.close()
