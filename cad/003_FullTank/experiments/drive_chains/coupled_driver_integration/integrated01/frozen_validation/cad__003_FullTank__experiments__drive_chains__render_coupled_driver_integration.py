"""Render the saved full development with duplicate-free standard tank context."""
import argparse, shutil
from pathlib import Path
from types import SimpleNamespace
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,read,write,sha,pose
from lib.visual_review import shaded,COLORS
from lib.camera_review import validate_native_bindings
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate)
for f in ['independent_checks.json','definition_preservation_checks.json']:
    q=read(s.folder/f);assert q['passed'] and q['native_sha256']==sha(s.native)
out=s.folder/'visual01';out.mkdir(exist_ok=False)
standardpath=H/'transmission_brake_front_study/trial01/standard_context_manifest.json';standard=read(standardpath)
assert all(sha(ROOT/f)==h for f,h in standard['native_files'].items())
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
COLORS.update(StationSeat=(.38,.25,.16),StationSupport=(.61,.46,.28),StationControls=(.36,.48,.67),StationHardware=(.55,.57,.58),StationClutch=(.76,.50,.24),StationEngine=(.43,.60,.52),StationTransmission=(.57,.62,.69),StationHull=(.53,.61,.49))
records={n:(r,s.manifest,'development') for n,r in s.rows.items()}
for r in standard['occurrences']:
    if r['representation']=='assembly' and r['name'] not in records and r['name'] not in {'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}:records[r['name']]=(r,standard,'standard')
cache={};items={}
def item(name):
    if name in items:return items[name]
    row,m,origin=records[name];d=m['definitions'][row['definition']];key=origin+':'+row['definition']
    if key not in cache:
        assert sha(d['brep_path'])==d['brep_sha256'];shape=Part.Shape();shape.read(d['brep_path']);assert shape.Placement.isIdentity();cache[key]=SimpleNamespace(Shape=shape)
    target=cache[key];shape=target.Shape.copy();shape.Placement=pose(row['frame'])
    system=row.get('system','StationHardware')
    if name in ['DriverSeatCushion','DriverSeatBackPadding']:system='StationSeat'
    elif 'DriverSeat' in name or 'SupportPlate' in name:system='StationSupport'
    elif 'Driver' in name or any(x in name for x in ['Rod','Control','Swing']):system='StationControls'
    elif name.startswith('Engine'):system='StationEngine'
    elif 'Transmission' in name or 'Clutch' in name:system='StationTransmission'
    elif name.startswith(('hull_','upper_')):system='StationHull'
    assert system in COLORS,system
    items[name]=dict(id=name,definition=key,shape=shape,target=target,representation='assembly',system=system)
    return items[name]
# Display plates as outlines for interior visibility. This does not alter material.
outline={n for n in records if n.startswith(('hull_','upper_'))}
views={}
for kind,names,title in [('development',list(s.rows),'Integrated development | coupled bow, driver controls and supported seat'),('isometric',list(records),'Standard tank context | integrated driver station; hull panels in outline')]:
    solids=[item(n) for n in names if n not in outline];context=[item(n) for n in names if n in outline]
    shaded(solids,out/(kind+'.svg'),(.8,-1,.9),title,context=context,canvas=(2200,1500))
    views[kind]=dict(physical_occurrences=names,shaded=[v['id'] for v in solids],outlined=[v['id'] for v in context],direction=[.8,-1,.9])
    print('Rendered',kind,len(names),'parts',flush=True)
prototype=ROOT/s.report['prototype'];pr=read(prototype/'report.json');source=read(prototype/'visual01/render_receipt.json');review=read(prototype/'visual01/visual_review.json')
assert source['native_sha256']==review['native_sha256']==pr['native_sha256'] and review['disposition']=='reviewed_local_approximation'
transferred={}
for name,d in source['images'].items():
    path=prototype/'visual01'/name;assert sha(path)==d
    target='station_'+name;shutil.copy2(path,out/target);transferred[target]=dict(source=str(path.relative_to(ROOT)),sha256=d)
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),renderer_sha256=sha(Path(__file__)),manifest_sha256=sha(s.folder/'isolated/manifest.json'),standard_manifest_sha256=sha(standardpath),
    input_hashes={str(H.parents[1]/'lib'/f):sha(H.parents[1]/'lib'/f) for f in ['visual_review.py','raster.py','raster.c','cad_build.py']},views=views,standard_replaced_occurrences=s.report['standard_replaced_occurrences'],
    source_camera_refitted=False,transferred_views=transferred,prototype_render_receipt_sha256=sha(prototype/'visual01/render_receipt.json'),strict_transfer_sha256=sha(s.folder/'independent_checks.json'),images={f.name:sha(f) for f in out.glob('*.png')},scope='Two newly rendered saved full unions; four inspected prototype views reused through strict material/frame transfer. Hull/upper panels displayed as outlines for visibility; no physical cuts or changes.'))
