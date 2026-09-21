import sys,subprocess,json
from pathlib import Path
repo=Path(__file__).resolve().parents[2];stage=repo/'cad/003_FullTank';root=stage/'experiments/drive_chains';out=Path(__file__).parent
sys.path[:0]=[str(stage),str(root)]
from lib import runtime
if '--worker' not in sys.argv:
 with (out/'case_diagnostic.log').open('w') as f:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out),stdout=f,stderr=subprocess.STDOUT).returncode)
try:
 App,Gui=runtime.start_gui();import Part
 from lib.cad_build import leaves
 from lib.evidence import write
 doc=App.openDocument(str(root/'transmission_reversing_build/TransmissionReversingCandidate.FCStd'));doc.recompute()
 old={i['id']:i for i in leaves(doc.Root)}['CenterTransmissionCore_bevel_case']['target'].Shape
 new=Part.Shape();new.read(str(out/'case.brep'))
 result=dict(old=dict(volume=old.Volume,valid=old.isValid(),tol=old.getTolerance(1)),new=dict(volume=new.Volume,valid=new.isValid(),tol=new.getTolerance(1)),comparisons=[])
 for tol in [0,1e-7,1e-6,1e-5]:
  rm=old.cut(new,tol);add=new.cut(old,tol);common=old.common(new,tol)
  r=dict(tol=tol,removed=rm.Volume,added=add.Volume,common=common.Volume,rm_valid=rm.isValid(),add_valid=add.isValid(),rm_solids=len(rm.Solids),add_solids=len(add.Solids),conservation_error=new.Volume-old.Volume-add.Volume+rm.Volume)
  print(r,flush=True);result['comparisons'].append(r)
 write(out/'case_diagnostic.json',result)
finally:runtime.close()
