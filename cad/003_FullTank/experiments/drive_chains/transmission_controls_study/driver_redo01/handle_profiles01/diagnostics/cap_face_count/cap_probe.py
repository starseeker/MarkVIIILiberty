import sys
from pathlib import Path
h=Path('/home/cyapp/MarkVIIILiberty/cad/003_FullTank/experiments/drive_chains');sys.path.insert(0,str(h))
from control_rebuild_io_v2 import *
s=Saved(h/'transmission_controls_study/driver_redo01/handle_profiles01/overall_control')
for side in ['Port','Starboard']:
 q=s.definition(s.rows[side+'DriverOperatingHandle']['definition']);print(side,[(list(f.Surface.Center),f.Surface.Radius,f.ParameterRange) for f in q.Faces if isinstance(f.Surface,Part.Sphere)],flush=True)
