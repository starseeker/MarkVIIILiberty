"""Test material-equivalent housing construction before changing accepted inputs."""
import importlib.util
import json
import math
from pathlib import Path
import sys
import FreeCAD as App
import Part

ROOT=Path('/home/cyapp/MarkVIIILiberty');H=ROOT/'cad/003_FullTank/experiments/drive_chains'
W=Path(__file__).resolve().parent/'housing_step_trials';W.mkdir(exist_ok=True)
sys.path.insert(0,str(H))
source=(H/'engine_lower_drive_parts.py').read_text()
original=source[source.index('def rounded_window('):source.index('\n\ndef parts(')]
replacement='''def rounded_window(width,low,high,radius,reach):
    """One analytic prism from tangent lines and exact circular corner arcs."""
    w=width/2;r=radius;q=r/math.sqrt(2)
    def p(y,z):return V(-reach,y,z)
    edges=[Part.makeLine(p(-w+r,low),p(w-r,low)),
        Part.Arc(p(w-r,low),p(w-r+q,low+r-q),p(w,low+r)).toShape(),
        Part.makeLine(p(w,low+r),p(w,high-r)),
        Part.Arc(p(w,high-r),p(w-r+q,high-r+q),p(w-r,high)).toShape(),
        Part.makeLine(p(w-r,high),p(-w+r,high)),
        Part.Arc(p(-w+r,high),p(-w+r-q,high-r+q),p(-w,high-r)).toShape(),
        Part.makeLine(p(-w,high-r),p(-w,low+r)),
        Part.Arc(p(-w,low+r),p(-w+r-q,low+r-q),p(-w+r,low)).toShape()]
    return Part.Face(Part.Wire(edges)).extrude(V(2*reach,0,0))
'''
window_block="""    for a,b in [(hlo+c['housing_end_stock'],mid-c['center_bridge_stock']/2),
                (mid+c['center_bridge_stock']/2,hhi-c['housing_end_stock'])]:
        h=h.cut(rounded_window(2*c['window_half_width'],a,b,c['window_corner_radius'],50))
"""
versions={'arc_prism':source.replace(original,replacement)}
versions['arc_prism_windows_last']=versions['arc_prism'].replace(window_block,'').replace('    # Top radial oil entry',window_block+'    # Top radial oil entry')
current=App.openDocument(str(H/'engine_lower_drive_study/DrivetrainWithLowerDriveStudy.FCStd'))
c=json.loads((H/'engine_lower_drive_controls.json').read_text())['controls'];reports=[]
try:
    for name,code in versions.items():
        path=W/(name+'.py');path.write_text(code)
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        shapes,*_=module.parts(c)
        checks=[]
        for key in ['housing_flywheel','housing_distributor']:
            a=shapes[key];old=current.getObject('Def_EngineLowerDrive_'+key).Shape
            changes=dict(missing=old.cut(a).Volume,added=a.cut(old).Volume)
            a.exportBrep(str(W/(name+'_'+key+'.brep')))
            step=W/(name+'_'+key+'.step');Part.setStaticValue('write.surfacecurve.mode',1);a.exportStep(str(step))
            b=Part.Shape();b.read(str(step));ta,tb=a.getTolerance(1),b.getTolerance(1)
            fuzzy=min(1e-4,max(1e-7,ta+tb));missing=a.cut(b,fuzzy);added=b.cut(a,fuzzy)
            row=dict(part=key,valid=a.isValid() and b.isValid(),native_tolerance=ta,step_tolerance=tb,
                     missing_faces=len(missing.Faces),added_faces=len(added.Faces),native_changes_mm3=changes,
                     passes=b.isValid() and tb<=max(1e-7,ta)+1e-10 and not missing.Faces and not added.Faces and max(abs(v) for v in changes.values())<1e-5)
            checks.append(row);print(name,json.dumps(row),flush=True)
        reports.append(dict(trial=name,checks=checks));(W/'result.json').write_text(json.dumps(reports,indent=2)+'\n')
finally:App.closeDocument(current.Name)
