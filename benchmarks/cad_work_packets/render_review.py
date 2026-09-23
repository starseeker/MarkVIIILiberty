"""Render saved candidate BRep data for review, without executing its builder."""
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad_packets'))
sys.path.insert(0,str(ROOT/'cad/003_FullTank'))
from validators.shadow import global_frame,world_shape
from lib.visual_review import shaded
import FreeCAD as A
import Part


def render(run):
    folder=ROOT/'benchmarks/cad_work_packets/results'/run
    artifact=folder/'artifacts/deliverables'
    out=folder/'review_views';out.mkdir(exist_ok=True)
    for path in sorted(artifact.glob('*.FCStd')):
        doc=A.openDocument(str(path))
        try:
            links=[o for o in doc.Objects if o.TypeId=='App::Link']
            for section in ([False,True] if doc.getObject('Station') else [False]):
                items=[]
                if section:
                    cut=Part.makeBox(1000,200,200,A.Vector(-500,-100,0))
                    cut.Placement=doc.getObject('Station').getGlobalPlacement()
                for i,link in enumerate(links):
                    s=world_shape(link)
                    if section:s=s.cut(cut)
                    color='Powerplant' if link.LinkedObject.Name in ['Pin','Bolt'] else 'FuelPressure' if link.LinkedObject.Name=='Bush' else 'HullStructure'
                    items.append(dict(shape=s,target=SimpleNamespace(Shape=s),definition=link.Name,system=color,representation='assembly'))
                suffix='_section' if section else '_isometric'
                direction=(1,1,.65)
                up_direction=(0,0,1)
                if section:
                    vec=doc.getObject('Station').getGlobalPlacement().Rotation.multVec(A.Vector(1,-1,1))
                    direction=tuple(vec)
                    up_direction=tuple(doc.getObject('Station').getGlobalPlacement().Rotation.multVec(A.Vector(0,0,1)))
                shaded(items,out/(path.stem+suffix+'.png'),direction,
                       run+' / '+path.stem+(' / cut section' if section else ' / installed solids'),
                       up_direction=up_direction,canvas=(1200,650))
        finally:A.closeDocument(doc.Name)


if __name__=='__main__':
    for run in sys.argv[1:]:render(run)
