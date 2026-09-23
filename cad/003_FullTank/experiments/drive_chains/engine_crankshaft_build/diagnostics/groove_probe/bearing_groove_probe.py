from pathlib import Path
import sys,json,math
import FreeCAD as App,Part
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains';sys.path[:0]=[str(h),str(root/'cad/003_FullTank')]
from engine_crankshaft_parts import half,ring,polygon
from engine_crossmember_parts import box
V=App.Vector;X,Y,Z=V(1,0,0),V(0,1,0),V(0,0,1)
c=json.loads((h/'engine_crankshaft_controls.json').read_text())['controls'];cc=json.loads((h/'engine_case_controls.json').read_text())['controls']
long=115;short=49;outer=cc['crankshaft_diameter']/2+cc['main_bearing_shell_stock'];inner=c['journal_diameter']/2+c['bearing_diametral_clearance']/2
out=root/'.work/engine-crankshaft/groove_probe';out.mkdir(exist_ok=True)
for label,length in [('long',long),('short',short)]:
    for sign,word in [(1,'upper'),(-1,'lower')]:
        shell=half(ring(outer,inner,0,length),sign)
        print('STEP',label,word,'shell=half(ring(outer,inner,0,length),sign)',shell.isValid(),len(shell.Solids),flush=True)
        feeds=[length*.25,length*.75] if label=='long' else [length*.5]
        for x in feeds:
            # LIB31 has localized crossed oil channels, not a complete
            # circumferential groove on the running face. LIB11 shows a
            # localized elongated pocket on the ordinary lower shell.
            # Clip rounded planar slot tools to a constant-depth annular
            # layer so the groove depth follows the cylindrical surface.
            w=c['bearing_oil_groove_width'];depth=c['bearing_oil_groove_depth']
            layer=ring(inner+depth,inner-.2,0,length)
            span=length*(.2 if label=='long' else .4)
            width=w if label=='long' else 2*w
            for angle in ([-45,45] if label=='long' else [90]):
                theta=math.radians(angle);u=V(math.cos(theta),math.sin(theta),0);normal=V(-u.y,u.x,0)
                center=V(x,0,-outer-1);a=center-u*(span-width)/2;b=center+u*(span-width)/2
                mask=polygon([a-normal*width/2,b-normal*width/2,b+normal*width/2,a+normal*width/2],Z*(2*outer+2))
                for end in [a,b]:mask=mask.fuse(Part.makeCylinder(width/2,2*outer+2,end,Z))
                shell=shell.cut(layer.common(mask))
                print('STEP',label,word,'shell=shell.cut(layer.common(mask))',shell.isValid(),len(shell.Solids),flush=True)
            shell=shell.cut(Part.makeCylinder(c['bearing_oil_feed_radius'],outer+2,V(x,0,0),Z*sign))
            print('STEP',label,word,"shell=shell.cut(Part.makeCylinder(c['bearing_oil_feed_radius'],outer+2,V(x,0,0),",shell.isValid(),len(shell.Solids),flush=True)
        # Dowel remains recessed below the running surface; its hole is
        # visible through the liner, as shown in the front-bearing figure.
        dx=length*.5 if label=='long' else length*.72
        shell=shell.cut(Part.makeCylinder(c['dowel_diameter']/2+c['dowel_clearance'],outer+2,V(dx,0,0),Z*sign))
        print('STEP',label,word,"shell=shell.cut(Part.makeCylinder(c['dowel_diameter']/2+c['dowel_clearance'],out",shell.isValid(),len(shell.Solids),flush=True)
        for x in [length*(i+1)/(int(length/10)+1) for i in range(int(length/10))]:
            shell=shell.cut(ring(inner+c['bearing_oil_groove_depth'],inner-.1,x-1,x+1).common(box(-1,length+1,-outer-1,outer+1,-2,2)))
            print('STEP',label,word,"shell=shell.cut(ring(inner+c['bearing_oil_groove_depth'],inner-.1,x-1,x+1).commo",shell.isValid(),len(shell.Solids),flush=True)
        print('BEFORE_REFINE',label,word,shell.isValid(),len(shell.Solids),flush=True)
        shell.exportBrep(str(out/(label+'_'+word+'_raw.brep')))
        refined=shell.removeSplitter()
        print('AFTER_REFINE',label,word,refined.isValid(),len(refined.Solids),flush=True)
        refined.exportBrep(str(out/(label+'_'+word+'_refined.brep')))
