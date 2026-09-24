"""Record printed engine constraints and conditional image measurements.

This is a source/layout study, not permission to rescale source-sized hardware
or move the accepted drivetrain. Pixel intervals are picking bounds, not a
claim about the original drawing's manufacturing accuracy.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'engine_pump_layout_study')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(out/'runtime/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from PIL import Image

    hb = 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/'
    snl = 'references/1928-03-30_SNL_G13/SNL_G13_Project/'
    paths = [hb+'original_scans/MarkVIII035.jpg', hb+'original_scans/MarkVIII030.jpg',
             hb+'Handbook_Project/assets/plate45.png', hb+'Handbook_Project/assets/plate40.png',
             snl+'sources/p286.jpg', snl+'assets/p277_foldout-geometry.png',
             'references/1918-09_12_Cylinder_Liberty_Aero_Engine/Liberty_Project/assets/figure_028_original.png']
    printed = {
        'water_axis_drop': dict(inches=6+3/4, printed_mm=171.5, feature='crankshaft to water-pump axis'),
        'left_connection_drop': dict(inches=10+45/64, printed_mm=271.9, feature='left oil-connection center in source view'),
        'right_connection_drop': dict(inches=12+5/64, printed_mm=306.8, feature='right oil-connection center in source view'),
        'connection_half_span': dict(inches=5+1/8, printed_mm=130.2, feature='oil-unit centerline to each connection end'),
        'camshaft_rise': dict(inches=23+5/32, printed_mm=588.2, feature='crankshaft to visible camshaft axis'),
    }
    for row in printed.values():
        row.update(exact_inch_conversion_mm=row['inches']*25.4,
                   locator='HB printed page68, Plate45; original scan MarkVIII035.jpg',
                   applicability='Caption: DIMENSIONS FRONT ELEVATION (AVIATION MOUNTING). Conditional tank transfer.')
    picks = dict(crank_y=1057, water_y=1287, left_connection_y=1417,
                 right_connection_y=1463, cam_y=293, oil_mount_y=1399,
                 drain_tip_y=1533, connection_end_x=[474,810], flange_x=[532,750],
                 body_x=[546,732], point_bound_px=3)
    sy = printed['right_connection_drop']['exact_inch_conversion_mm']/(picks['right_connection_y']-picks['crank_y'])
    sx = 2*printed['connection_half_span']['exact_inch_conversion_mm']/(810-474)
    checks=[]
    for name, point in [('water_axis_drop','water_y'),('left_connection_drop','left_connection_y'),('camshaft_rise','cam_y')]:
        measured=abs(picks[point]-picks['crank_y'])*sy
        exact=printed[name]['exact_inch_conversion_mm']
        checks.append(dict(name=name, measured_mm=measured, printed_inches_mm=exact,
                           residual_mm=measured-exact, nominal_pick_bound_mm=6*sy,
                           within_nominal_pick_bound=abs(measured-exact)<=6*sy))
    # Separate horizontal calibration; never apply the vertical scale to width.
    widths={}
    for name in ['flange','body']:
        span=picks[name+'_x'][1]-picks[name+'_x'][0]
        widths[name]=dict(diameter_mm=span*sx,
            pixel_only_interval_mm=[(span-6)*260.35/(336+6),(span+6)*260.35/(336-6)],
            interpretation='Image-scaled envelope, not a printed part diameter; projection/drawing errors are additional.')
    pump=json.loads((HERE/'engine_oil_pump_mounting_study/report.json').read_text())
    context=json.loads((HERE/'engine_oil_pump_mounting_study/diagnostics/current_context/source_constraints.json').read_text())
    return_local=pump['datums']['passages']['common_return'][-1][2]
    supply_local=pump['datums']['passages']['tank_supply'][0][2]
    return_mount=-printed['left_connection_drop']['exact_inch_conversion_mm']-return_local
    supply_mount=-printed['right_connection_drop']['exact_inch_conversion_mm']-supply_local
    # Keep the two independent inferred planes; do not conceal their 0.075mm
    # disagreement by silently averaging or call this an explicit mount dimension.
    mount=return_mount
    facts=context['facts']
    cal=json.loads((ROOT/'cad/003_FullTank/data/calibrations.json').read_text())['snl_2']
    scale=3124.2/(cal['axes']['z']['pixels'][1]-cal['axes']['z']['pixels'][0])
    snl_picks=dict(engine_axis=[1260,449], transmission_axis=[1413,451], floor_line=[1150,512], bound_px=3)
    floor_top=facts['floor_underside_mm']+facts['floor_stock_mm']
    engine_z=floor_top+(512-449)*scale
    bottom=context['facts']['proposed_pump_mount_local_z_mm']
    bounds=json.loads((HERE/'engine_oil_pump_mounting_study/diagnostics/current_context/context_probe.json').read_text())['engine_frame_bounds']
    pump_low=min(v['zmin'] for k,v in bounds.items() if k.startswith('EngineOilPump_'))-bottom
    alternatives=[]
    for name,axis in [('inherited_drivetrain',facts['engine_origin_z_mm']),('floor_referenced_SNL2_hypothesis',engine_z)]:
        alternatives.append(dict(name=name,engine_axis_world_z_mm=axis,pump_mount_engine_z_mm=mount,
            pump_bottom_engine_z_mm=mount+pump_low, floor_top_engine_z_mm=floor_top-axis,
            full_pump_envelope_floor_gap_mm=axis+mount+pump_low-floor_top,
            registration_selected=False))
    report=dict(status='Source reconciliation and conditional layout hypotheses; installation unqualified',
        source_hashes={p:digest(ROOT/p) for p in paths}, printed=printed,
        hb45_picks=picks, hb45_local_scales_mm_per_px=dict(horizontal=sx,vertical=sy),
        held_out_vertical_checks=checks, widths=widths,
        interpretation=['Camshaft held-out dimension fails the local pump-region scale: no globally accurate HB45 scale claimed.',
            'HB58 Plate40 and SNL Plate14 were inspected as qualitative crosschecks; no new metric picks are adopted from them.',
            'The left higher connection is provisionally associated with common return, and the lower right with tank supply; source-view orientation must be reconciled before final fittings.',
            'Floor-referenced SNL2 registration is a separate hypothesis. It cannot independently settle the absolute engine elevation or the correct interpretation of the floor line.',
            'An engine elevation change must also reconcile clutch/transmission axes, supports, control linkages and output chains; a whole-assembly translation is not an accepted repair.'],
        oil_mount_from_ports=dict(common_return_based_z_mm=return_mount,tank_supply_based_z_mm=supply_mount,
            discrepancy_mm=abs(return_mount-supply_mount), selected_for_diagnostic_z_mm=mount,
            basis='Conditional printed connection levels minus current estimated local passages; NOT a printed mounting plane.'),
        snl2_picks=snl_picks,snl2_vertical_scale_mm_per_px=scale,
        floor_referenced_axis_pick_bound_mm=6*scale,
        floor_referenced_engine_shift_mm=engine_z-facts['engine_origin_z_mm'],
        layout_alternatives=alternatives,
        recommended_geometry_trials=dict(water_axis_drop_mm=171.45,oil_flange_radius_mm=84.5,
            oil_body_radius_mm=72.0,gear_module_estimate_mm=2.0,
            caution='Radial controls are starting estimates for a coupled pump reconstruction; retain printed fastener stock/fits and independently qualify all passages and hardware.'),
        native_inputs_unchanged=True,standard_assembly_modified=False,installation_qualified=False,
        script_sha256=digest(Path(__file__)))
    (out/'source_constraints.json').write_text(json.dumps(report,indent=2)+'\n')

    im=Image.open(ROOT/(hb+'Handbook_Project/assets/plate45.png')).convert('RGB')
    fig,ax=plt.subplots(figsize=(9,8))
    ax.imshow(im);ax.set_xlim(425,1150);ax.set_ylim(1585,990)
    for y,label in [(1057,'Crank datum'),(1287,'6 3/4 in = 171.45 mm'),(1417,'10 45/64 in = 271.859 mm'),(1463,'12 5/64 in = 306.784 mm')]:
        ax.axhline(y,color='#176499',lw=1);ax.text(820,y-5,label,color='#0b426b',fontsize=10)
    for key,y in [('flange',1486),('body',1440)]:
        x1,x2=picks[key+'_x'];ax.plot([x1,x2],[y,y],color='#ba391b',lw=2)
        ax.text(430,y+23,f'{key}: {widths[key]["diameter_mm"]:.1f} mm estimated',color='#9c2511',fontsize=10)
    ax.set_title('HB p68 Plate45: aviation mounting; local image measurements')
    ax.set_xlabel('Original asset pixel X');ax.set_ylabel('Original asset pixel Y')
    fig.tight_layout();fig.savefig(out/'hb45_constraints.png',dpi=150);plt.close(fig)
    im=Image.open(ROOT/(snl+'assets/p277_foldout-geometry.png'))
    fig,ax=plt.subplots(figsize=(14,5));ax.imshow(im);ax.set_xlim(995,1485);ax.set_ylim(525,420)
    for name,(x,y) in [(k,v) for k,v in snl_picks.items() if isinstance(v,list)]:
        ax.plot(x,y,'o',color='#b22817');ax.annotate(f'{name}: ({x}, {y})',(x,y),xytext=(0,20 if name!='floor_line' else -25),textcoords='offset points',ha='center',color='#8e2315',bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
    ax.set_yticks(range(420,526,10));ax.grid(alpha=.3)
    ax.set_title('SNL Plate2: floor-relative registration trial; each pick bounded +/-3 pixels')
    fig.tight_layout();fig.savefig(out/'snl2_registration.png',dpi=150);plt.close(fig)
    (out/'source_review_receipt.json').write_text(json.dumps(dict(
        source_constraints_sha256=digest(out/'source_constraints.json'),
        images={p.name:digest(p) for p in [out/'hb45_constraints.png',out/'snl2_registration.png']},
        image_method='Source images plotted with coordinate annotations; original source files unchanged'),indent=2)+'\n')
    print(json.dumps(dict(widths=widths,port_mounts=report['oil_mount_from_ports'],layouts=alternatives),indent=2))


if __name__=='__main__':
    main()
