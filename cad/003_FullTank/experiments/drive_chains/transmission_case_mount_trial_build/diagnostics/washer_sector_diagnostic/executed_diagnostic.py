import sys,subprocess,math
from pathlib import Path
REPO=Path(__file__).resolve().parents[2];STAGE=REPO/'cad/003_FullTank';ROOT=STAGE/'experiments/drive_chains'
sys.path[:0]=[str(STAGE),str(ROOT)]
from lib import runtime
from lib.evidence import write
out=Path(__file__).parent/'washer_sector_diagnostic';out.mkdir(exist_ok=True)
if '--worker' not in sys.argv:
    with (out/'run.log').open('w') as f:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out),stdout=f,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from transmission_frame_parts import xz_plate
    from transmission_stud_parts import cylinder_x
    from case_joint_mass import calculator
    mass=calculator(out/'runtime/mass');rows=[];radius=9.675;slope=4/42;t=4+slope*17
    expected=(34*30-math.pi*radius**2)*t
    wedge=xz_plate([(0,-15),(t-slope*15,-15),(t+slope*15,15),(0,15)],-17,17)
    clip=xz_plate([(t-slope*40,-40),(20,-40),(20,40),(t+slope*40,40)],-40,40)
    for method in ['sector180_keep','sector180_refine','sector180_overlap','split_body_keep','split_body_refine']:
        cutter=cylinder_x(radius,-1,12)
        if method.startswith('sector'):
            aa=Part.makeCylinder(radius,13,App.Vector(-1,0,0),App.Vector(1,0,0),181 if 'overlap' in method else 180)
            bb=aa.copy();bb.rotate(App.Vector(),App.Vector(1,0,0),180)
            s=wedge.cut(aa).cut(bb)
        else:
            half=Part.makeBox(20,20,30,App.Vector(-2,0,-15))
            s=wedge.common(half).cut(cutter).fuse(wedge.cut(half).cut(cutter))
        if 'refine' in method:s=s.removeSplitter()
        s.translate(App.Vector(1582.0817913541819,118,1192.8698292220113))
        path=out/(method+'.step');s.exportStep(str(path));back=Part.Shape();back.read(str(path))
        mn,ms=mass(s,method+'_native'),mass(back,method+'_step');dv=abs(mn['volume_mm3']-ms['volume_mm3'])
        dc=(App.Vector(*mn['center_mm'])-App.Vector(*ms['center_mm'])).Length
        rows.append(dict(method=method,valid=s.isValid() and back.isValid(),native_volume=mn['volume_mm3'],step_volume=ms['volume_mm3'],
            expected_volume=expected,native_analytic_error=mn['volume_mm3']-expected,step_analytic_error=ms['volume_mm3']-expected,
            mass_difference=dv,center_difference=dc,native_tolerance=s.getTolerance(1),step_tolerance=back.getTolerance(1),
            raw_missing=s.cut(back).Volume,raw_added=back.cut(s).Volume,
            native_curve_types=[type(e.Curve).__name__ for e in s.Edges],step_curve_types=[type(e.Curve).__name__ for e in back.Edges]))
        write(out/'report.json',dict(rows=rows));print(method,dv,dc,flush=True)
finally:runtime.close()
