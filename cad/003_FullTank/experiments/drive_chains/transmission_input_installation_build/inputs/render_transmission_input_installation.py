"""Render saved installation, feed cutaway and unchanged SNL23 registration."""
import argparse,base64
from pathlib import Path
import subprocess,sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_input_installation_build');p.add_argument('--worker',action='store_true')
args=p.parse_args();stage=args.stage.resolve();candidate=args.candidate.resolve();out=candidate/'source_review';sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,REPO
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(candidate),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part,fitz
    from lib.cad_build import leaves,COLORS
    from lib.visual_review import shaded
    report=read(candidate/'report.json');native=candidate/'TransmissionInputInstallationCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};origin=App.Vector(*report['shaft_axis_world_mm'])
    COLORS.update(InputCase=(.43,.55,.43),InputBearing=(.68,.67,.58),InputCage=(.74,.53,.24),InputShaft=(.34,.56,.7),
        InputSeal=(.35,.32,.25),InputHardware=(.71,.34,.23),InputGrease=(.79,.62,.27))
    def role(n):
        if n.startswith('InputInstallation_') and any(k in n for k in ['nipple','elbow','cup_']):return 'InputGrease'
        if n.startswith('InputBearing'):return 'InputCage' if n.endswith('cage') else 'InputBearing'
        if n.endswith(('shaft','pinion','coupling')) or 'wheel' in n:return 'InputShaft'
        if any(k in n.lower() for k in ['nut','bolt','stud','shim','cotter','washer']):return 'InputHardware'
        if n.endswith(('felt','disk')):return 'InputSeal'
        return 'InputCase'
    def draw(names,cut,name,title,direction=(1,-1,1.1)):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].cut(cut) if cut is not None else i['shape']
            if s.isNull() or not s.Solids:continue
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['definition']+'_view_'+n,system=role(n)))
        shaded(selected,out/(name+'.svg'),direction,title)
    names=[n for n in byid if n.startswith(('Input','CenterBevelDrive_pinion'))]+['CenterTransmissionCore_bevel_cover']
    draw(names,None,'installation_overview','Input installation | four MX25 sets and grease feed; source conflicts and inferred fitting placement retained',direction=(1,1,1.1))
    cut=Part.makeBox(700,160,180,origin+App.Vector(0,-160,0))
    draw(names,cut,'installation_cutaway','Input installation cutaway | opposed bearings and drilled spacer; housing quadrant removed for inspection')
    grease_names=['InputHousing_housing','InputHousing_spacer']+[n for n in report['new_ids'] if 'mount_' not in n]
    cut=Part.makeBox(600,600,600,origin+App.Vector(279,-300,-300))
    draw(grease_names,cut,'grease_section','Grease feed section | hollow cup,45-degree elbow,nipple and bored M250/M249; route inferred',direction=(1,.25,.2))
    draw(['InputInstallation_'+k+'0' for k in ['mount_stud','mount_nut','mount_cotter']],None,
        'cover_fastener','MX25 joint hardware | printed half-inch x2-17/32 stud; corrected nut size and formed3/32 x1 split pin')
    draw([report['repaired_prior_cotter_ids'][0]],None,'repaired_cap_cotter',
        'Bearing-cap split pin repair | both formed legs retained; source1/8 x1-3/8 inches',direction=(1,-1,.5))
    draw(['InputHousing_cotter'],None,'repaired_input_cotter',
        'Input-shaft split pin repair | both source3/16 x2-1/2 inch legs retained; ends remain unspread',direction=(1,1,.5))
    cal=read(ROOT/'transmission_input_calibration.json');src=REPO/cal['image'];assert sha(src)==cal['image_sha256']
    plane=Part.makePlane(1400,1000,origin+App.Vector(-500,0,-500),App.Vector(0,1,0))
    colors=dict(InputCase='#247443',InputBearing='#7a43a3',InputCage='#ae711a',InputShaft='#167b9b',InputSeal='#573b27',InputHardware='#cb3924',InputGrease='#c89113')
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1094" height="1040">','<rect width="1094" height="1040" fill="#f7f5ee"/>',
        f'<image width="1094" height="921" href="data:image/png;base64,{base64.b64encode(src.read_bytes()).decode()}" opacity=".65"/>']
    for n in names:
        for edge in byid[n]['shape'].section(plane).Edges:
            pts=[f'{cal["origin_px"][0]-(v.x-origin.x)/cal["mm_per_pixel"]:.3f},{cal["origin_px"][1]-(v.z-origin.z)/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.15)]
            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[role(n)]}" stroke-width=".9"/>')
    svg += ['<text x="20" y="949" font-family="sans-serif" font-size="18">Plate23 | unchanged cup-OD registration; actual saved axial sections.</text>',
        '<text x="20" y="978" font-family="sans-serif" font-size="17">Cover fastener pattern inferred. Off-plane grease feed is not located by this source section.</text>',
        '<text x="20" y="1007" font-family="sans-serif" font-size="17">Bearing-width and pinion-profile differences remain unresolved; no scan stretching.</text></svg>']
    path=out/'installation_plate23_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    rasters={p.name:sha(p) for p in out.glob('*.png')}
    write(out/'render_receipt.json',dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),
        source_sha256={str(src.relative_to(REPO)):sha(src)},calibration_sha256=sha(ROOT/'transmission_input_calibration.json'),rasters=rasters,
        native_placements_changed=False,source_warping=False,limitations=cal['limits']))
    # Keep the builder's report immutable so independent receipts remain bound.
    assert sha(native)==report['native_sha256'];print('Rendered seven input-installation images; native unchanged.',flush=True)
finally:runtime.close()
