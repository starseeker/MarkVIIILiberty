import json
from pathlib import Path
import FreeCAD as App,Part
w=Path('/home/cyapp/MarkVIIILiberty/.work/engine-crankshaft');results=[]
for mode in ['direct','copy']:
 original=Part.Shape();original.read(str(w/'groove_probe/long_upper_raw.brep'))
 before=original.isValid();candidate=original.copy() if mode=='copy' else original
 refined=candidate.removeSplitter()
 results.append(dict(mode=mode,original_valid_before=before,original_valid_after=original.isValid(),candidate_valid_after=candidate.isValid(),refined_valid=refined.isValid()))
 print(json.dumps(results[-1]),flush=True)
(w/'unification_copy_probe.json').write_text(json.dumps(dict(freecad=App.Version(),occ=Part.OCC_VERSION,results=results),indent=2)+'\n')
