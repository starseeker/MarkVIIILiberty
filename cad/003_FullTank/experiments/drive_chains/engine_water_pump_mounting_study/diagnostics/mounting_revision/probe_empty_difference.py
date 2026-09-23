import json
from pathlib import Path
import FreeCAD as App,Part
one=Part.makeBox(10,10,10);two=Part.makeBox(12,12,12,App.Vector(-1,-1,-1));difference=one.cut(two)
r=dict(freecad=App.Version(),occ=Part.OCC_VERSION,is_null=difference.isNull(),solids=len(difference.Solids),faces=len(difference.Faces),volume_mm3=difference.Volume)
try:
 result=difference.cut(Part.makeBox(30,30,30,App.Vector(-10,-10,-10)))
 r['second_cut']='returned';r['second_cut_volume_mm3']=result.Volume
except (ValueError,Part.OCCError) as e:r['second_cut']='raised';r['error']=str(e)
r['guarded_outside_volume_mm3']=0. if not difference.Solids else abs(difference.cut(Part.makeBox(30,30,30)).Volume)
r['passed']=not difference.Solids and not difference.Faces and abs(difference.Volume)<1e-12 and r['guarded_outside_volume_mm3']==0
Path('empty_difference.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));assert r['passed']
