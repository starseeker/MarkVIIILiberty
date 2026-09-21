import sys,subprocess,math
from pathlib import Path
REPO=Path(__file__).resolve().parents[2];STAGE=REPO/'cad/003_FullTank';ROOT=STAGE/'experiments/drive_chains'
sys.path[:0]=[str(STAGE),str(ROOT)]
from lib import runtime
from lib.evidence import write
out=Path(__file__).parent/'washer_diagnostic';out.mkdir(exist_ok=True)
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
    for method in ['cut0','cut90','cut180','cut270','drill_then_slope','drill_then_slope90','half_cylinders','common_prism']:
        cutter=cylinder_x(radius,-1,12)
        if method.startswith('cut'):
            cutter.rotate(App.Vector(),App.Vector(1,0,0),float(method[3:]));s=wedge.cut(cutter)
        elif method.startswith('drill_then_slope'):
            if method.endswith('90'):cutter.rotate(App.Vector(),App.Vector(1,0,0),90)
            s=Part.makeBox(12,34,30,App.Vector(0,-17,-15)).cut(cutter).cut(clip)
        elif method=='half_cylinders':
            half=Part.makeBox(20,20,30,App.Vector(-2,0,-15));a=cutter.common(half);b=cutter.cut(half)
            s=wedge.cut(a).cut(b)
        else:s=Part.makeBox(12,34,30,App.Vector(0,-17,-15)).cut(cutter).common(wedge)
        s=s.removeSplitter();s.translate(App.Vector(1582.0817913541819,118,1192.8698292220113))
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
