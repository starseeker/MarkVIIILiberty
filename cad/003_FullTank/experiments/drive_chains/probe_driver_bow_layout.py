"""Probe full-stock driver height feasibility against the saved corrected shell."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_layout_trial_parts import layout

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
parent=Saved(C/'driver_redo01/operating_integrated01')
bow=H/'bow_reconstruction_study/trial02';br=read(bow/'report.json');bn=bow/br['native_file'];assert sha(bn)==br['native_sha256']
doc=App.openDocument(str(bn));hull={}
for name,row in br['occurrences'].items():
    if row['candidate'] or name=='hull_floor_3':
        link=doc.getObject(name);s=link.LinkedObject.Shape.copy();s.Placement=link.LinkPlacement;hull[name]=s
App.closeDocument(doc.Name)
records=[]
for main_z in [900.,925.,950.,975.,1000.,1025.,1050.,1100.,1200.,1300.]:
    shapes,specs,properties,details=layout(parent,main_z)
    pairs=[];world={}
    for name,row in specs.items():
        s=shapes[row['definition']].copy();s.Placement=pose(row['frame']);world[name]=s
        for other,t in hull.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            common=s.common(t);volume=sum(abs(v.Volume) for v in common.Solids)
            pairs.append(dict(first=name,second=other,volume_mm3=volume,passed=volume<1e-5 and (common.isNull() or common.isValid())))
    handles={side:dict(bow_distance_mm=world[side+'DriverOperatingHandle'].distToShape(hull['hull_front_slope'])[0],
                       floor_distance_mm=min(world[side+'DriverOperatingHandle'].distToShape(hull[n])[0] for n in ['hull_floor_1','hull_floor_2'])) for side in ['Port','Starboard']}
    findings=[v for v in pairs if not v['passed']]
    records.append(dict(main_z_mm=main_z,layout=details,occurrences=len(specs),pairs=len(pairs),findings=findings,
                        tested_shell_clear=not findings,handles=handles))
    print('HEIGHT',main_z,'M576',details['M576_common_stock_mm'],'findings',len(findings),[(v['first'],v['second'],round(v['volume_mm3'],3)) for v in findings],flush=True)
# Current mounting contact points are audited against the replacement plates.
mounts=[]
for m in parent.report['details']['foundation']['mounts']:
    point=Part.Vertex(App.Vector(*m['floor_contact_world_mm']))
    distances={n:point.distToShape(hull[n])[0] for n in ['hull_floor_1','hull_floor_2']}
    mounts.append(dict(stem=m['stem'],old_contact_world_mm=m['floor_contact_world_mm'],distance_to_new_floor_mm=min(distances.values())))
write(out/'report.json',dict(parent_native_sha256=sha(parent.native),bow_native_sha256=sha(bn),
    worker_sha256=sha(Path(__file__)),parts_sha256=sha(H/'driver_layout_trial_parts.py'),records=records,current_mount_gaps=mounts,
    source_camera_refitted=False,geometry_integrated=False,
    scope='117 complete saved driver/rod/joint solids per height, with exact M574/short stock and one shared unprinted M576 length. No support/floor reconstruction or full internal/retained-context qualification. Height is a hypothesis, not a historical dimension.',
    source_inventory_correction='M575/M578/M573 rear rods are already present in the accepted native. The preceding next-action wording that called them missing is superseded; these saved rear constraints are retained.'))
