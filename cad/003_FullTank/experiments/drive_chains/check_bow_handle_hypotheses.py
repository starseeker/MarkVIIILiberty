"""Retest the four saved full handle profiles against all 40 proposed plates."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import *

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--bow',type=Path,required=True)
a=p.parse_args();folder=a.bow.resolve();r=read(folder/'report.json')
native=folder/r['native_file'];assert sha(native)==r['native_sha256']
doc=App.openDocument(str(native));hull={}
for name,row in r['occurrences'].items():
    if not row['candidate']:continue
    link=doc.getObject(name);s=link.LinkedObject.Shape.copy();s.Placement=link.LinkPlacement;hull[name]=s
App.closeDocument(doc.Name)
out=folder/'handle_recheck01';out.mkdir(exist_ok=False)
root=H/'transmission_controls_study/driver_redo01/handle_profiles01'
results={};inputs={};normal=None
front=hull['hull_front_slope'];face=max(front.Faces,key=lambda f:f.Area)
normal=face.normalAt(0,0)
if normal.x>0:normal=-normal
for key in ['overall_control','pivot_reach','functional_current','functional_source']:
    saved=Saved(root/key)
    old=read(root/key/'profile_checks02/report.json')
    assert old['native_sha256']==sha(saved.native)
    inputs[str(saved.native.relative_to(ROOT))]=sha(saved.native)
    inputs[str((root/key/'profile_checks02/report.json').relative_to(ROOT))]=sha(root/key/'profile_checks02/report.json')
    pairs=[];sides={}
    for side in ['Port','Starboard']:
        name=side+'DriverOperatingHandle';one=saved.world(name)
        for plate,two in hull.items():
            if not one.BoundBox.intersect(two.BoundBox):continue
            common=one.common(two);volume=sum(abs(s.Volume) for s in common.Solids)
            pairs.append(dict(handle=name,plate=plate,common_mm3=volume,
                              passed=volume<1e-5 and (common.isNull() or common.isValid())))
        pole=App.Vector(*old['records'][side]['actual_tip_world_mm'])
        sides[side]=dict(pole_world_mm=list(pole),pole_signed_interior_plane_mm=(pole-face.CenterOfMass).dot(normal),
                         unchanged_source_plan_discrepancy_px=old['records'][side]['plan_residual_px'],
                         unchanged_source_side_discrepancy_px=old['records'][side]['side_residual_px'],
                         complete_handle_to_wall_distance_mm=one.distToShape(front)[0])
    results[key]=dict(native_sha256=sha(saved.native),pairs=pairs,sides=sides,passed=all(q['passed'] for q in pairs))
    print(key,results[key]['passed'],pairs,flush=True)
write(out/'report.json',dict(bow_native_sha256=sha(native),worker_sha256=sha(Path(__file__)),input_hashes=inputs,
    profile_results=results,source_camera_refitted=False,geometry_changed=False,integration_accepted=False,
    scope='Only the proposed shell changes from the earlier full-profile study; all four complete saved handle solids and their original frames are retained. Test each against all40 replacement plates. Prior unchanged-context findings and source discrepancies remain applicable.',
    next_action='Reconcile absolute driver shaft/seat/support datums and the depicted control state with the source views and full connecting-rod lengths. Do not accept a shell penetration, shorten the handle to clear it, or refit the camera to suppress it.'))
