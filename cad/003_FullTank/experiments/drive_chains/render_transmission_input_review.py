"""Render the actual saved input assembly and unwarped SNL section comparisons."""
import argparse,base64
from pathlib import Path
import subprocess,sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_input_build');p.add_argument('--worker',action='store_true')
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
    from transmission_input_parts import box
    report=read(candidate/'report.json');native=candidate/'TransmissionInputCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};origin=App.Vector(*report['shaft_axis_world_mm'])
    COLORS.update(InputCase=(.43,.55,.43),InputBearing=(.68,.67,.58),InputCage=(.74,.53,.24),InputShaft=(.34,.56,.7),InputSeal=(.35,.32,.25),InputHardware=(.71,.34,.23))
    def role(n):
        if n.startswith('InputBearing'):return 'InputCage' if n.endswith('cage') else 'InputBearing'
        if n.endswith(('shaft','pinion','coupling')) or 'wheel' in n:return 'InputShaft'
        if any(k in n for k in ['nut','bolt','shim','cotter','washer']):return 'InputHardware'
        if n.endswith(('felt','disk')):return 'InputSeal'
        return 'InputCase'
    def draw(names,crop,name,title,direction=(1,-1,1.1)):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].common(crop) if crop is not None else i['shape']
            if s.isNull() or not s.Solids:continue
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['definition']+'_view_'+n,system=role(n)))
        shaded(selected,out/(name+'.svg'),direction,title)
    names=report['new_ids']+report['changed_ids']
    crop=box(origin.x+150,origin.x+510,-130,130,origin.z-140,origin.z)
    draw(names,crop,'input_section','Input assembly cutaway | opposed Timken bearings, shims, housing, coupling and packing; dimensions partly inferred')
    draw([n for n in names if n not in ['InputHousing_housing','InputHousing_gland','CenterTransmissionCore_bevel_cover']],None,
        'input_exposed','Input assembly inspection | housing/gland hidden; actual native placements, bearing internals inferred')
    draw([n for n in names if n.startswith('InputBearing1')],box(origin.x+290,origin.x+360,-80,80,origin.z-80,origin.z),
        'input_bearing_section','Timken6454/6420 section | printed bore69.85, OD149.225, cone54.229, cup44.45mm; internals inferred')
    central=[i['id'] for i in items if i['id'].startswith(('PortBevel','StarboardBevel','PortThrust','StarboardThrust','CenterBevel','CenterTransmissionCore','Input'))]
    draw(central,box(origin.x-300,origin.x+520,-230,230,origin.z-280,origin.z),'input_bevel_cutaway',
        'Bevel drive and input assembly | source-counted parts; controls, support joints, pump and lubrication still pending')
    cal=read(ROOT/'transmission_input_calibration.json');src=REPO/cal['image'];assert sha(src)==cal['image_sha256']
    plane=Part.makePlane(1400,1000,App.Vector(origin.x-500,0,origin.z-500),App.Vector(0,1,0))
    colors=dict(InputCase='#247443',InputBearing='#7a43a3',InputCage='#ae711a',InputShaft='#167b9b',InputSeal='#573b27',InputHardware='#cb3924')
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1094" height="1040">','<rect width="1094" height="1040" fill="#f7f5ee"/>',
        f'<image width="1094" height="921" href="data:image/png;base64,{base64.b64encode(src.read_bytes()).decode()}" opacity=".65"/>']
    for n in names:
        for edge in byid[n]['shape'].section(plane).Edges:
            pts=[f'{cal["origin_px"][0]-(v.x-origin.x)/cal["mm_per_pixel"]:.3f},{cal["origin_px"][1]-(v.z-origin.z)/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.15)]
            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[role(n)]}" stroke-width=".9"/>')
    svg += ['<text x="20" y="949" font-family="sans-serif" font-size="18">Plate23 | actual native axial sections; cup OD calibration, no raster stretching.</text>',
        '<text x="20" y="978" font-family="sans-serif" font-size="17">Green casting, purple races/rollers, amber cage, blue shaft/coupling, red hardware/shims.</text>',
        '<text x="20" y="1007" font-family="sans-serif" font-size="17">Horizontal bearing-width checks disagree with radial scale; contours and placement remain approximate.</text></svg>']
    path=out/'input_plate23_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    # Independent Plate22 comparison retains its pre-existing hub-based scale.
    other=read(ROOT/'transmission_output_calibration.json');src2=REPO/other['image'];assert sha(src2)==other['image_sha256']
    plane2=Part.makePlane(3000,3000,App.Vector(origin.x-1500,-1500,origin.z),App.Vector(0,0,1))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1330">','<rect width="1724" height="1330" fill="#f7f5ee"/>',
        f'<image width="1724" height="1147" href="data:image/png;base64,{base64.b64encode(src2.read_bytes()).decode()}" opacity=".65"/>']
    for n in names:
        for edge in byid[n]['shape'].section(plane2).Edges:
            pts=[f'{1534-v.y/other["mm_per_pixel"]:.3f},{other["shaft_axis_y_px"]+(v.x-origin.x)/other["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.15)]
            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[role(n)]}" stroke-width=".9"/>')
    svg += ['<text x="25" y="1270" font-family="sans-serif" font-size="21">Plate22 | coupling is a detached detail at lower left of input bearings; main section omits its installed extension.</text>',
        '<text x="25" y="1304" font-family="sans-serif" font-size="21">Hub-based scale retained. Bearing/spacer proportions disagree with Plate23; differences remain visible.</text></svg>']
    path=out/'input_plate22_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    rasters={p.name:sha(p) for p in out.glob('*.png')}
    report.update(rendering_complete=True,output_raster_hashes=rasters);write(candidate/'report.json',report)
    write(out/'render_receipt.json',dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),
        source_sha256={str(src.relative_to(REPO)):sha(src),str(src2.relative_to(REPO)):sha(src2)},calibration_sha256=sha(ROOT/'transmission_input_calibration.json'),rasters=rasters,
        native_placements_changed=False,source_warping=False,limitations=cal['limits']))
    assert sha(native)==report['native_sha256'];print('Rendered six input-assembly images; native unchanged.',flush=True)
finally:runtime.close()
