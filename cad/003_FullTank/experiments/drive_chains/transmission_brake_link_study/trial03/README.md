# Brake suspension links and retained pivots — 24 September 2026

`PowertrainWithBrakeLinks.FCStd` adds four M337 suspension links, four M339 pivot
pins and eight split pins. The development assembly has **2,775 physical
occurrences, 474 definitions and 268 assemblies**. Three definitions are new;
all 471 inherited definitions retain their material. Four M338 brackets and two
M385 stops move to the inboard sides of their brake bands. All other inherited
occurrence frames and every owning assembly relationship are retained.
Standard tank011 is unchanged. Lower anchor fittings and support fastening
remain missing; this is not a complete brake installation.

## Source interpretation and shape

HB207 and SNL119 give four M337 links. Four separate M339 pins follow the explicit
SNL137 application: two low-speed and two track. HB207 and SNL251 instead list
two pins; applicability of the selected arrangement to the first-100 production
configuration remains unresolved. The later detailed entry is the chosen
reconstruction hypothesis, not proof of a production revision. Two quarter-inch
by 1½-inch split pins retain each pivot, giving eight installed occurrences.

HB134/135 depict a narrow link with its web set aft of the eye-to-eye chord.
Two cubic polynomial B-spline edges approximate this side profile: degree 3,
knots [0,1], endpoint multiplicities [4,4], unit weights and a 14 mm bow control.
The centerline control points are saved in `report.json`; each side is offset
by half the 19.05 mm web width, then extruded. The round eyes and pivot bores
remain analytic. This is an estimated contour, not a recovered factory curve.
The transverse taper, upper clevis, stock and pin fits are also estimates.
Dimensions change by regenerating the builder; native metadata is not a live
parametric dependency graph.

The first candidate centered each link on its band and put the entire lower eye
outside a future anchor-foot radius. Both low-speed links intersected the middle
diaphragm by 3,184.144419 mm³. Moving the link to the outboard side instead collided
with the chain cases, chains and gussets. The selected inboard layout places
lower straps 1.5 mm beside the steel band edges and lower eyes 2 mm forward of
the retained diaphragm. No frame cutout was introduced. No transverse source
section independently proves this layout; the earlier support packet explicitly
left axial centering provisional.

Low-speed support groups move 58.65 mm toward the vehicle center and track
support groups move 45.95 mm inward. Upper pivot X/Z stations stay fixed. The
lower pin centers are at X1504.346071, Z900.602941 mm, with link center distance
252.413774 mm. Their Y positions are ±476.745714 mm for low-speed and
±724.214286 mm for track. The 24 mm pivot shafts, 24.3 mm bores, 53.7 mm pivot
length, 6.35 mm cheeks and 12.7 mm lower stock are documented approximations.
Split-pin straight and splayed legs retain the selected nominal stock length;
paired round sections and eye joins do not claim exact original stock volume.

## Validation

All **106 saved-geometry checks** pass, including full bores and straight cotter
legs, source identities, fork clearances, retention witnesses, composed frames,
all six moved support seats, lower-eye/frame clearance and band-side spacing.
Filled bores, cut cotter legs and displaced support seats are rejected.
All **92 nearby development material pairs** pass. The complete retained standard
context contains 5,316 physical occurrences and yields zero possible affected
pairs. Context acceptance covers 16 added and six repositioned occurrences.

All **25 strict STEP comparisons** pass: three new definitions and 22 affected
installed components, with validity, tolerance, centroid and both material
directions checked. `BrakeLinksDefinitions.step` and `BrakeLinksInstallation.step`
are scoped exchanges; they are not full-tank exports.

All **471 inherited definitions** are preserved: 448 exact BReps and 23 strict
material comparisons. Fresh regeneration reproduces all 1,448 archived BReps,
9,937 object types and 129,795 persistent properties exactly. Increasing web bow
by 1 mm, frame clearance by 0.5 mm and band-side clearance by 0.5 mm passes the
same 106 checks and 92 development comparisons, with all 471 inherited nominal
BReps unchanged. Separate variation STEP qualification is not claimed.

The initial checker incorrectly counted trimmed cylinder faces as separate
cotter legs. The corrected check groups the two cylinder axes and independently
proves both complete leg solids, with cut-leg negative controls. A later checker
used an arbitrary cylinder surface origin as the eye's axial center; the saved
bore-face limits supply that center instead. A local variable collision also
interrupted one check. Failed reports/code are retained; none justified relaxing
an acceptance tolerance or altering the split-pin geometry.

## Visual review and continuation

The [isometric](isometric.png), [link detail](link_detail.png),
[low-speed overlay](lowspeed_source_overlay.png) and
[track overlay](track_source_overlay.png) were inspected directly. Original
channel registration is retained. The modeled shaft is still offset from the
pictured shaft; the lower eye appears forward and below the pictured anchor
under that registration. The bowed web improves the side silhouette, while
hidden sections and anchor details remain approximate. Four milestone copies
bring the progression to **178 images**, preserving all 174 earlier images and
29 recorded native baselines.

Continue with M348/M353 lower anchor pins, rear band brackets and their retained
joints, front ears, adjusters, controls and support-foot fasteners. Adding riveted
feet must account for existing lining-rivet tails and grip lengths. Then finish
frame/hull fastening and broader engine/interior coverage before standard-tank
integration and poses. Accepted local tests do not settle historical uncertainty.

## Rebuild

Run the scripts in `cad/003_FullTank/experiments/drive_chains/` through
`skills/freecad-reconstruction/scripts/freecad_headless.py`, with absolute file
arguments and fresh output/work directories:

1. `build_transmission_brake_links.py --source <brake-band-trial01> --output <fresh>`
2. `pump_integration_worker.py extract --input <fresh>/PowertrainWithBrakeLinks.FCStd --output <fresh>/isolated/manifest.json`
3. `check_transmission_brake_links.py --candidate <fresh> --standard-manifest <standard-context-manifest>`
4. `exchange_transmission_brake_links.py --candidate <fresh>`
5. `render_transmission_brake_links.py --candidate <fresh>`

Use ordinary Python for `check_transmission_brake_link_preservation.py --candidate
<fresh>` and `check_powertrain_frame_reproduction.py --candidate <first>
--reproduction <second>` after a second build/extraction. Source, controls,
generators, validators, reports and variant definitions are retained. Full
reproduction/variation natives and earlier diagnostic natives remain in the local
work directories; their reports and relevant definitions are versioned.
