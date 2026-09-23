"""Render saved gear, joint sections and thrust lock with original source context."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent; STAGE = HERE.parents[1]; ROOT = STAGE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
from lib import runtime
from lib.evidence import read, write, sha
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, default=HERE/'engine_gear_build')
p.add_argument('--worker', action='store_true')
a = p.parse_args(); base = a.candidate.resolve(); out = base/'source_review'; out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable, __file__, '--candidate', str(base), '--worker'],
            env=runtime.environment(out), stdout=log, stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App
    import Part
    from lib.cad_build import leaves, COLORS
    from detail_render import shaded_detail
    V = App.Vector
    native = base/'DrivetrainWithEngineGear.FCStd'; r = read(base/'report.json')
    assert sha(native) == r['native_sha256']
    doc = App.openDocument(str(native)); byid = {i['id']: i for i in leaves(doc.Root)}
    origin = doc.TankLibertyEngine.Placement.Base
    COLORS.update(Casting=(.62,.68,.67), Shaft=(.44,.49,.53), Bearing=(.77,.67,.41),
        Gear=(.69,.72,.74), Shim=(.78,.51,.27), Hardware=(.53,.61,.68), Wire=(.84,.63,.30), Context=(.43,.54,.60))
    names = []
    def draw(selected, name, title, direction, clip=None):
        items=[]
        for n in selected:
            row=byid[n]; s=row['shape'].copy()
            if clip is not None: s=s.common(clip)
            if s.isNull() or not s.Solids: continue
            color='Context'
            if n.startswith('EngineCase_'): color='Casting'
            elif n=='EngineCrank_Forging': color='Shaft'
            elif n.startswith('EngineCrank_'): color='Bearing'
            elif n=='EngineGear_DrivingBevel': color='Gear'
            elif n=='EngineGear_ThinShim': color='Shim'
            elif n.endswith('Wire') or 'Cotter' in n: color='Wire'
            elif n.startswith(('EngineGear_', 'ShaftClosure_')): color='Hardware'
            items.append(dict(row, shape=s, target=SimpleNamespace(Shape=s), definition=n, system=color))
        shaded_detail(items, out/(name+'.svg'), direction, title, deflection=.04)
        names.append(name); print('Rendered',name,flush=True)
    crank=[n for n in byid if n.startswith(('EngineCrank_','ShaftClosure_','EngineGear_'))]
    frame=[n for n in byid if n.startswith(('EngineFrame_','EngineSuspension_'))]
    draw(crank+frame+['EngineCase_lower'],'isometric',
        'Engine development | driving bevel and thrust lock installed; upper case hidden for review',(.45,.6,1))
    joint=[n for n in r['new_ids'] if not 'ThrustLock' in n]+['EngineCrank_Forging']
    joint += [n for n in byid if n.startswith('ShaftClosure_Gear_')]
    end=r['parent_datums']['gear_flange_span'][1]
    window=Part.makeBox(125,180,180,origin+V(end-45,-90,-90))
    draw(joint,'gear_joint','33-tooth bevel | integral claw and internal spline counts are estimates',(1,.65,.5),window)
    draw(joint,'gear_end','Gear end | six bolt sets, one provisional thin shim, broad claw rim guided by figure86',(1,0,0),window)
    section=Part.makeBox(125,90,180,origin+V(end-45,0,-90))
    draw(joint,'gear_section','Gear joint section | source-length bolts, estimated installed grip and hub profile',(.1,-1,.2),section)
    locking=['EngineCrank_Forging','EngineCrank_ThrustNut','EngineGear_ThrustLockScrew','EngineGear_ThrustLockWire']
    window=Part.makeBox(30,94,94,origin+V(20,-47,-47))
    draw(locking,'thrust_lock','Thrust nut lock | estimated open wire passes screw and anchors in a nut slot',(-1,.6,.8),window)
    section=Part.makeBox(18,94,94,origin+V(r['controls']['lock_station'],-47,-47))
    draw(locking,'thrust_lock_section','Thrust lock section | radial blind receiver, screw cross-hole and slotted nut',(-1,0,0),section)
    sources=ROOT/'references/1918-09_12_Cylinder_Liberty_Aero_Engine/Liberty_Project/assets'
    comparisons=''; hashes={}
    for figure,view in [(86,'gear_joint'),(22,'gear_joint'),(93,'gear_end'),(107,'isometric')]:
        path=sources/('figure_%03d_original.png'%figure); hashes[str(path.relative_to(ROOT))]=sha(path)
        comparisons+='<h2>Liberty figure '+str(figure)+' / '+view+'</h2><div class="comparison"><img src="'+os.path.relpath(path,out)+'"><img src="'+view+'.png"></div>'
    for page in [23,99,202,212,217]:
        path=ROOT/('references/1928-03-30_SNL_G13/SNL_G13_Project/sources/p%03d.jpg'%page)
        hashes[str(path.relative_to(ROOT))]=sha(path)
        comparisons+='<p><a href="'+os.path.relpath(path,out)+'">Original SNL page '+str(page)+'</a></p>'
    for n in [48,100]:
        path=ROOT/('references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII%03d.jpg'%n)
        hashes[str(path.relative_to(ROOT))]=sha(path)
        comparisons+='<p><a href="'+os.path.relpath(path,out)+'">Original handbook scan '+str(n)+'</a></p>'
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Liberty driving gear</title><style>body{font:18px system-ui;margin:24px;background:#f6f4ed}img{max-width:100%}.comparison{display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:16px}</style><h1>Liberty driving gear development</h1><p>Source identities, counts and conditional dimensions are retained separately from estimated profiles. HB199 printed3/32in grip conflicts with the installed stack and has not been silently corrected. Claw/spline counts and lock-wire route remain unverified estimates. Mating pinions, final shim stack and backlash remain pending. Cameras are not registered; display cuts do not alter the saved physical model.</p>'+comparisons+''.join('<h2>'+n+'</h2><img src="'+n+'.png">' for n in names))
    write(out/'render_receipt.json',dict(native_sha256=sha(native),renderer_sha256=sha(Path(__file__)),
        images={n+'.png':sha(out/(n+'.png')) for n in names},source_assets=hashes,model_modified=False,source_camera_fit=False))
finally:
    runtime.close()
