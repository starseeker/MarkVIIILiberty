"""Couple floor-relative source hypotheses to a closed, fixed-phase drive chain.

This calculation changes no CAD. It establishes candidate stations for subsequent
case/support/control and actual-solid chain checks, not an accepted installation.
"""
import json
import math
from pathlib import Path

from scipy.optimize import brentq
from installed_pitch_route_probe import closed_route,angle_error
from pitch_route_probe import PITCH,BIG,SMALL,LARGE_TEETH,SMALL_TEETH

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=HERE/'engine_pump_receiver_study/registration';OUT.mkdir(parents=True,exist_ok=True)

def read(p):return json.loads(p.read_text())
def sha(p):
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()

paths=dict(route=HERE/'installed_pitch_route_report.json',
    source=HERE/'engine_pump_layout_study/source_constraints.json',
    receiver=HERE/'engine_pump_receiver_study/trial02/independent_checks.json',
    assembly=HERE/'engine_pump_receiver_study/assembly_trial02/report.json')
r,s,local,assembly=[read(paths[k]) for k in ['route','source','receiver','assembly']]
big=r['roller_pinion_axis_xz_mm'];old=r['candidate_transmission_axis_xz_mm']
phase=math.radians(r['roller_pinion_phase_deg']);count=r['pitch_count']
assert count==50 and r['pitch_mm']==PITCH and r['large_teeth']==LARGE_TEETH and r['small_teeth']==SMALL_TEETH
assert abs(old[1]-assembly['engine_origin'][2])<1e-7

def solve_direction(beta):
    angles=[(math.pi/2-phase-2*math.pi*n/LARGE_TEETH-beta)%(2*math.pi) for n in range(LARGE_TEETH)]
    first=min(a for a in angles if math.pi/2<=a<=math.pi)
    distance=brentq(lambda c:closed_route(c,first,count)[0],BIG+SMALL,count*PITCH,xtol=1e-9)
    return distance,first

def candidate(target_z):
    beta=brentq(lambda a:big[1]+solve_direction(a)[0]*math.sin(a)-target_z,-.25,-.02,xtol=1e-12)
    distance,first=solve_direction(beta);residual,points=closed_route(distance,first,count)
    def world(p):
        x,z=p;return [big[0]+x*math.cos(beta)-z*math.sin(beta),big[1]+x*math.sin(beta)+z*math.cos(beta)]
    station=world((distance,0));vertices=[world(p) for p in points]
    large=[math.atan2(z,x)+beta for x,z in points[:-1] if abs(math.hypot(x,z)-BIG)<1e-7]
    small=[math.atan2(z,x-distance)+beta for x,z in points[:-1] if abs(math.hypot(x-distance,z)-SMALL)<1e-7]
    pitch=max(abs(math.dist(a,b)-PITCH) for a,b in zip(vertices,vertices[1:]))
    large_error=max(angle_error(a,math.pi/2-phase,LARGE_TEETH) for a in large)
    small_error=max(angle_error(a,small[0],SMALL_TEETH) for a in small)
    closing=math.dist(vertices[0],vertices[-1])
    passed=abs(station[1]-target_z)<1e-7 and pitch<1e-7 and closing<1e-7 and large_error<1e-9 and small_error<1e-9
    # Hold X fixed while lifting the transmission: closure must be recomputed.
    wrong_beta=math.atan2(target_z-big[1],old[0]-big[0]);wrong_distance=math.dist(big,(old[0],target_z))
    _,wrong_first=solve_direction(wrong_beta)
    wrong_residual,wrong_points=closed_route(wrong_distance,wrong_first,count)
    return dict(mathematical_checks_passed=passed,transmission_axis_xz_mm=station,
        rigid_powertrain_translation_mm=[station[0]-old[0],0,station[1]-old[1]],
        engine_origin_candidate_mm=[assembly['engine_origin'][0]+station[0]-old[0],0,station[1]],
        center_distance_mm=distance,axis_angle_deg=math.degrees(beta),
        fixed_roller_pinion_axis_xz_mm=big,fixed_roller_pinion_phase_deg=r['roller_pinion_phase_deg'],
        small_pinion_phase_deg=math.degrees(math.pi/2-small[0])%(360/SMALL_TEETH),
        maximum_pitch_error_mm=pitch,closure_error_mm=closing,
        maximum_large_phase_error_rad=large_error,maximum_small_phase_error_rad=small_error,
        large_contact_vertices=len(large),small_contact_vertices=len(small),
        inherited_floor_envelope_gap_mm=local['inherited_floor_envelope_gap_mm'],
        proposed_floor_envelope_gap_mm=local['inherited_floor_envelope_gap_mm']+station[1]-old[1],
        vertical_only_negative_control=dict(closure_residual_mm=wrong_residual,
            closing_error_mm=math.dist(wrong_points[0],wrong_points[-1]),
            rejected=abs(wrong_residual)>1e-7),
        vertices_world_xz_mm=vertices[:-1])

scale=s['snl2_vertical_scale_mm_per_px'];picks=s['snl2_picks']
engine_hypothesis=next(a['engine_axis_world_z_mm'] for a in s['layout_alternatives'] if a['name']=='floor_referenced_SNL2_hypothesis')
floor_top=engine_hypothesis-(picks['floor_line'][1]-picks['engine_axis'][1])*scale
levels={key:floor_top+(picks['floor_line'][1]-picks[key][1])*scale for key in ['engine_axis','transmission_axis']}
levels['common_horizontal_axis_mean']=(levels['engine_axis']+levels['transmission_axis'])/2
rows={key:candidate(z) for key,z in levels.items()}
for row in rows.values():assert row['mathematical_checks_passed'] and row['vertical_only_negative_control']['rejected']
result=dict(status='source_and_chain_constrained_station_candidates_not_installed',
    input_hashes={str(p.relative_to(ROOT)):sha(p) for p in paths.values()},script_sha256=sha(Path(__file__)),
    candidates=rows,floor_top_world_z_mm=floor_top,
    source_axis_difference_mm=levels['engine_axis']-levels['transmission_axis'],
    pixel_only_height_bound_mm=s['floor_referenced_axis_pick_bound_mm'],
    source_review='SNL Plate2 original full section and local registered crop directly inspected 23 September 2026.',
    datum_history=['Existing849.2335mm height comes from a50-pitch chain closure along a provisional drawing-derived direction.',
        'It is not a printed engine height. The floor was separately placed using the printed20.75in ground clearance.',
        'The source engine and transmission center picks differ by2pixels; a common horizontal axis is an explicit hypothesis.',
        'All candidates retain the installed fixed-axis roller-pinion position and17.21degree phase,50pitches of76.2mm,and23/12teeth.'],
    required_geometry_work=['Regenerate every chain occurrence, small sprocket phase and both casings for the selected station.',
        'Move engine, clutch and transmission together only after resolving their support and control interfaces.',
        'Reconstruct engine supports and transmission frame/bearing receivers against unchanged hull/floor.',
        'Check actual gear/chain material, mounting hardware, floor and surrounding equipment; mathematical closure is insufficient.',
        'Compare saved native overall and section silhouettes against SNL2 and handbook views before promotion.'],
    selected_candidate=None,standard_assembly_modified=False,installation_qualified=False)
(OUT/'station_candidates.json').write_text(json.dumps(result,indent=2)+'\n')
for key,row in rows.items():
    print(key,{k:row[k] for k in ['transmission_axis_xz_mm','rigid_powertrain_translation_mm','proposed_floor_envelope_gap_mm','vertical_only_negative_control']})
