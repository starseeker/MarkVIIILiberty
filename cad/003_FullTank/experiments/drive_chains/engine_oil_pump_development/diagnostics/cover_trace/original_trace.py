from pathlib import Path
import sys,json
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(h))
import FreeCAD as App
import Part
from engine_oil_pump_parts import rev_z,cylinder
V=App.Vector;c=json.loads((h/'engine_oil_pump_controls.json').read_text())['controls'];out=Path.cwd();data=[]
top=c['lower_body_bottom']-c['cover_gasket_stock'];inner=c['filter_outer_radius'];fr=c['mount_flange_radius'];dish=c['cover_dish_depth'];thick=c['cover_stock'];dx=c['drain_x'];seat=top-dish-thick-c['drain_boss_drop']
hole=cylinder(c['drain_diameter']/2+c['thread_gap'],seat-1,top+1,dx,0)
def audit(name,s):
    data.append(dict(name=name,valid=s.isValid(),solids=len(s.Solids),volume=s.Volume,faces=len(s.Faces),drain_overlap=s.common(hole).Volume));s.exportBrep(str(out/(name+'.brep')))
    print(data[-1],flush=True)
    return s
blank=audit('blank',rev_z([(0,top-dish-thick),(inner,top-thick),(fr,top-thick),(fr,top),(inner,top),(0,top-dish)]))
boss=audit('boss',blank.fuse(cylinder(c['drain_diameter']/2+6,seat,top,dx,0)))
cavity=audit('cavity',rev_z([(0,top-dish),(inner,top),(fr,top),(fr,top+5),(0,top+5)]))
cleared=audit('cleared',boss.cut(cavity));drilled=audit('drilled',cleared.cut(hole));audit('drilled_without_cavity',boss.cut(hole))
altcavity=Part.makeCone(0,inner,dish,V(0,0,top-dish)).fuse(cylinder(fr,top,top+5))
alt=audit('alternate_cavity',altcavity);s=audit('alternate_cleared',boss.cut(altcavity));s=audit('alternate_drilled',s.cut(hole))
raw=Part.makeCone(0,inner,dish,V(0,0,top-dish-thick)).fuse(cylinder(fr,top-thick,top));audit('analytic_blank',raw)
s=audit('analytic_boss',raw.fuse(cylinder(c['drain_diameter']/2+6,seat,top,dx,0)));s=audit('analytic_clear',s.cut(altcavity));s=audit('analytic_drilled',s.cut(hole))
(out/'report.json').write_text(json.dumps(data,indent=2)+'\n')
