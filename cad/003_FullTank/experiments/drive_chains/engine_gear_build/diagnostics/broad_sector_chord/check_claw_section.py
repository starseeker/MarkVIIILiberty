from pathlib import Path
import json
import FreeCAD as App, Part
root=Path('/home/cyapp/MarkVIIILiberty');b=root/'cad/003_FullTank/experiments/drive_chains/engine_gear_build'
r=json.loads((b/'report.json').read_text());c=r['controls'];doc=App.openDocument(str(b/'DrivetrainWithEngineGear.FCStd'))
x=c['shim_stock']+c['web_stock']+c['hub_length']+c['claw_stock']/2
s=doc.Def_EngineGear_gear.Shape.common(Part.makeBox(.1,100,100,App.Vector(x-.05,-50,-50)))
d=dict(expected_claw_sections=2,actual_claw_sections=len(s.Solids),native_sha256=r['native_sha256'],cause='Triangular sector at150degrees has a chord inside the centre bore; use an exact arc sector for the broader rim.')
(root/'.work/engine-gear/claw_section_diagnostic.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d));App.closeDocument(doc.Name)
