# Upper stops and clips — standard static reconstruction

M399 top stops, M398 back stops and M365 clips now have saved part definitions.
The [development assembly](../integrated_upper01/PowertrainWithHighBrakeUpperStops.FCStd)
adds sixteen physical occurrences, three definitions and four assembly groups:
**3,165 occurrences / 542 definitions / 336 assemblies**. The original bottom-stop
candidate remains available. Complete support-packet qualification and standard
tank promotion are separate work.

The [assembled brake isometric](../integrated_upper01/high_brake_assembly_isometric.png)
shows all 160 brake occurrences with the drums in outline. The
[upper-stop detail](upper_stop_detail.png) isolates the new parts. Both use saved
native definitions and actual composed placements.

## Evidence and reconstruction decisions

The [HB133 overlay](upper_stop_source.png) retains the existing image, center,
scale and axis conventions. Its main top-strap profile follows the illustration;
back-stop bends, bolt heads and clip retain visible residual differences. The
source uses local depth and sectional conventions. This comparison does not
recover hidden widths or establish a photographic camera, and it is not an
independent dimensional test of geometry inferred from that same drawing.

The handbook labels both upper and lower common locking plates MX61. The model
therefore reuses the actual saved lower plate definition, including its formed
tabs and 60 mm hole pitch. The earlier estimated upper pitch was 65 mm. Moving
both upper stations 2.5 mm toward their unchanged midpoint permits that reuse.
Both directions of case material change are confined to the old/new drill
envelopes; the surrounding case, lower receivers and bearing interfaces remain.
This shared-pitch interpretation is a hypothesis, not a printed dimension.

The upper stack is M398 at 3.175 mm, M399 at 6.35 mm and MX61 at 1.5875 mm.
The existing MX60 envelope has 11.1125 mm engagement, with positive blind-hole
back stock. Top/back straps use analytic lines and circular bends; the top foot
has an explicit miter into its horizontal section. M365 encloses the tongue,
with a bearing floor and a bore through the tongue for the M400 screw. These
hidden forms and stock values are named approximations. Threads remain nominal
envelopes and bores; geometric engagement does not establish strength.

M400 screws and their nuts also reuse the saved lower definitions. All six
catalogue M400/nut pairs are now located. Eight of ten catalogue MX60 screws are
located; the final two locations remain unresolved. No extra screw is invented
to close the catalogue count. The selected handbook locking plates remain an
alternative to the later SNL individual lock washers.

## Checks and retained failures

- [Prototype material checks](report.json): all 291 selected full-solid pairs
  pass, including the changed case and retained powertrain context. Both case
  material deltas stay within the declared upper drill envelopes.
- [Saved native checks](independent_checks.json): 96 pass, including actual
  coaxial bores, positive stack bearing, blind stock, full nut engagement,
  clip/tongue retention and overtravel negative controls.
- [STEP exchange](exchange_checks.json): all eight definitions and seventeen
  installed solids pass the existing material, tolerance, centroid and mass
  convergence criteria. The large receiving case uses the previously qualified
  refined quadrature, with failed default measurements retained. Geometry and
  acceptance limits are unchanged.
- [Thicker-strap variation](../upper_variation01/report.json): increasing M399
  stock by 1 mm regenerates its profile, clip channel, mounting stack and stop
  setting; 291 material pairs, 96 native checks and 25 STEP comparisons pass.

The retained [first trial](../upper01/report.json) found 863.687601 mm³ of screw
interference per side with the thicker front band end. The initial adjustment
solver had only included the thin bands and rear anchor. Adding the retained
front ends to its actual contact targets corrected the setting. No neighbor was
trimmed, and the source registration was unchanged.

Complete removal/tool paths, operating controls, structural qualification and
exact manufactured forms remain open. The minimum anchor-pin service probe from
the lower increment remains a scoped result, not a complete service procedure.

The [integrated checks](../integrated_upper01/independent_checks.json) pass all
30 transfers/hierarchy tests. All 538 unchanged inherited definitions are
preserved (514 exact BReps and 24 strict material comparisons); all 13 catalogue
checks pass. Seventeen affected occurrences clear 5,316 retained standard-tank
occurrences. A fresh rebuild reproduces all six compared data sets, including
1,658 archive BReps and 150,278 persistent properties. The
[checkpoint receipt](../integrated_upper01/development_checkpoint.json) binds
these results without promoting the full support packet.
