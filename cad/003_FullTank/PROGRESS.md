# Full-tank implementation progress

Current user priority: **fully populate the standard assembled configuration,
including identifiable interiors, before implementing any pose variants**.
The pose research remains preparation for later work.
At each significant visual improvement, retain the standard isometric as the
next `cad/intermediate_snapshot_iso_NNN.png` and update
[the visual progression](../VISUAL_PROGRESSION.md). User-saved 001 and 002 are
preserved; 003 records the sponson shells, 004 the roof louvers and 005 the roller
stacks; 006 records the separate idler-wheel internals, 007 the shafts and adjusters,
008 the lower support runs, 009 the driving wheels, 010 their shafts and bearings,
and 011 the roller pinions. Transparent-hull companion views start at 011.

## 24 September 2026 — rear channel stock and local source registration

[The rear-channel study](experiments/drive_chains/transmission_controls_study/channel_stock01/README.md)
retains 45 source rows and confirms two original handbook/SNL quantity conflicts.
The intact rear side view supports a downward-open channel. A separate native
stock prototype uses a provisional 152.4 × 50.8 mm section, 2,200 mm span and
6.35 mm stock, seated on the measured floor at X = 2,400 mm. It has no mounting
holes, cleats or attached brackets yet and is **not integrated** into the tank.

Nominal and 0.5 mm thicker-stock trials each pass 13 native/interface checks,
three neighboring material pairs and two strict STEP comparisons. Fresh nominal
regeneration reproduces both archive BReps and stable definition/link properties.
The initial single-object STEP export lost its placement; an explicit task-local
export setting resolves the retained failure without geometry or tolerance changes.
That tested lesson is recorded in the FreeCAD reconstruction skill.

A fixed, conditional SNL6 side registration agrees with the outer drum silhouette
within 2.8 pixels but retains a 21.867-pixel high-speed control-bore discrepancy.
Those outer checks are correlated, and the drawing has rod-length breaks; no
historical perspective-camera calibration is claimed. The stock variation reuses
exactly the same registration. Next: cleat/fulcrum stations, floor bolts, channel
rivets, spring supports, and targeted lever/rod review. Current integrated counts
remain **3,173 occurrences /546 definitions /338 groups**; progression stays222.
The complete standard-tank goal remains active.

## 24 September 2026 — rear high-speed control joints

[The current native checkpoint](experiments/drive_chains/transmission_controls_study/us_nuts01/README.md)
populates two M569B forks, two M568A pins, two split pins and two plain nuts:
**3,173 physical occurrences /546 definitions /338 assembly groups**. Fork and
pin length datums remain explicit hypotheses. The shorter overall-fork-length
interpretation fails the chosen socket-engagement requirement with the retained
profile; it remains a recorded alternative, not a disproven historical design.

Nominal and thicker-ear trials pass42 saved checks,18 material comparisons and12
STEP comparisons each. Integration passes17 checks and preserves542 definitions.
A period-source check replaced the smaller reused nut with a separate classic
U.S. Standard envelope. That revision passes16 checks,6 material pairs,3 STEP
comparisons,8 updated variation checks and preservation of545 definitions
(526 exact /19 strict). All3,173 native links reopen after relocation; fresh
full builds reproduce shapes, frames, ownership and persistent properties.
Nut finish applicability and older clutch nut proportions remain open evidence.

Three new views bring progression to **222 images**, including the retained
small-nut trial and its source-led correction. Exact extracted-shape links avoid
about348MiB of duplicates across the two stages and their local reproductions.
The read-only control-checkpoint verifier checks current dependency hashes before
reusing receipts. Standard tank011 is unchanged. Next: M4128 rear control channel,
cleats, spring and lever supports, then full M575 and other control routes.

## 24 September 2026 — combined support qualification and control interfaces

The [combined support qualification](experiments/drive_chains/transmission_high_brake_support_study/integrated_upper01/combined_qualification/README.md)
passes all six pipeline stages. All 45 affected occurrences pass 431 material
comparisons and 59 combined STEP comparisons. Native relocation verifies every
installed link/frame; 38 scoped receipts and 528 inherited definition chains
support reuse. Standard-tank files and context remain current. The complete
HB133 overlay was inspected without a camera refit. Geometry and counts remain
**3,165 physical occurrences / 542 definitions / 336 assemblies**.

The [operating-control study](experiments/drive_chains/transmission_controls_study/README.md)
records 99 source rows, 34 identities and six measured brake-control interfaces.
The high-speed eye is 25.4 mm wide without a central slot; low/track eyes are
12.7 mm wide. Source fork/pin variants and inconsistent length/application
wording remain explicit. HB92/HB113/SNL6 contain rod-length breaks; HB104 is a
separate photograph suitable for later perspective investigation. Rear fork
joints and the M4128 channel/support layout precede full rod routes. The complete
tank goal remains active, with standard integration and poses still later.

## 24 September 2026 — high-speed upper stops and clips

The [upper-stop increment](experiments/drive_chains/transmission_high_brake_support_study/upper02/README.md)
adds sixteen occurrences, three definitions and four groups: **3,165 physical
occurrences / 542 definitions / 336 assemblies**. M399/M398 stops and M365 clips
reuse the existing MX60, MX61 and M400/nut definitions. The upper case hole pitch
changes locally from 65 to 60 mm to match the common MX61 plate. Stock, bends
and the hidden clip retention remain explicit reconstruction hypotheses.

Nominal and +1 mm M399 stock trials each pass 291 material pairs, 96 saved native
checks and 25 STEP comparisons. Integration passes 30 checks, preservation of
538 unchanged definitions (514 exact / 24 strict), 13 catalogue checks, retained
standard context and all six fresh-rebuild checks. The earlier receiver bracket
variation now also passes its 13 STEP checks. Default case-mass failures and the
qualified refined measurements are retained; geometry and limits are unchanged.

All six M400/nut pairs and eight of ten MX60 screws are located. The first upper
trial caught a screw contacting a thicker band end omitted from its adjustment
targets; the corrected setting includes that retained end without trimming it.
Three reviewed snapshots bring progression to **219**, including the assembled
160-occurrence brake pair. Source registration remains unchanged. Complete
support-packet pipeline qualification is next, followed by operating controls,
remaining interiors and standard integration. The full tank goal remains active.

## 24 September 2026 — high-speed anchor retention and bottom stops

The [bottom-stop increment](experiments/drive_chains/transmission_high_brake_support_study/bottom_stops03/README.md)
adds20 parts and eight assembly groups: **3,149 occurrences /539 definitions
/332 assemblies**. M363 pins/cotters, M366 stops, MX76/MX77 mounting hardware and
four M400/nut pairs are installed; M362 gains an estimated receiving shelf.
Printed cotter stock is retained. A rejected cast rib intersected a retained
lining-rivet tail; only the proposed rib was narrowed to provide clearance.

Nominal and1mm stop-stock variation pass75 native checks and30 STEP comparisons
each. The nominal trial also passes142 nearby pairs. Integration passes35 checks,
preservation of531 unchanged definitions (512 exact/19 strict),13 saved catalogue
checks, retained tank context and exact fresh nominal reproduction. The required
57.65mm pin withdrawal and25mm drift approach clear selected epicyclic neighbors;
larger assumed envelopes fail and remain documented. Full service work is open.

Three inspected views bring progression to **216 images**, preserving213 earlier
views. A tessellation-cache caller error in an unpublished preview was corrected;
native and STEP placements were unaffected. Source registration remains fixed.
M399/M398 top/back stops, M365 clips and remaining upper hardware are next.
Full support qualification and standard-tank integration remain pending;
the operating-mechanism checkpoint remains the last fully qualified parent.

## 24 September 2026 — high-speed receiving webs and anchor mounts

The [receiving candidate](experiments/drive_chains/transmission_high_brake_support_study/README.md)
adds eight physical bracket/locking-plate/mount-screw occurrences and revised
integral case receiving webs: **3,129 occurrences /532 definitions /324 assemblies**.
The fixed HB133 comparison was inspected; hidden sections and cast stock remain
explicit estimates. Two new images bring progression to **213**, preserving 211.

The prototype passes 22 checks including 226 nearby pairs, 28 additional saved
interface checks and 13 strict STEP comparisons. The integration passes 18
geometry/frame/hierarchy checks, preservation of all 528 unchanged definitions
(502 identical, 26 strict material comparisons), retained tank context and exact
fresh nominal reproduction. A 1 mm bracket-stock variation passes its native
checks. Tighter quadrature resolves a diagnosed case-mass convergence failure;
nine independent controls pass without changing geometry or tolerance limits.

This remains a development candidate: anchor pins/cotters, band stops and hardware,
parameter-variation STEP and full support-packet qualification are unfinished.
The last fully qualified parent remains the operating-mechanism checkpoint;
standard tank011 is unchanged and the complete tank goal remains active.

## 24 September 2026 — high-speed support evidence and receiving context

The [support study](experiments/drive_chains/transmission_high_brake_support_study/README.md)
records source counts, service connections, anchor cotter stock and nominal
hardware sizes. It preserves the handbook locking plates and later catalogue
lock washers as distinct configuration evidence. Eight MX60 screws are provisionally
located by the illustration; two of the catalogue total ten remain unallocated.

A read-only, native-bound section probe reuses the HB133 registration. At the
brake and bearing depths it exposes missing receiving material near the illustrated
support feet; the case-web/bracket depth hypothesis must be developed before
installation. Existing cotter and washer identities were audited for possible
reuse. No CAD geometry or progression image was added. The qualified parent
remains 3,121 occurrences /529 definitions /322 assemblies; the full goal is active.

## 24 September 2026 — high-speed operating mechanisms

The [mechanism checkpoint](experiments/drive_chains/transmission_high_brake_mechanism_study/trial01/README.md)
adds 30 parts: paired M355 lever members and joining rivets, four retained M356
pin joints, and both screw/spring/washer adjustment units. Development now has
**3,121 physical occurrences /529 definitions /322 assemblies**.

All 15 stages pass: 61 component checks, 98 development pairs, 519 preserved
definitions, 40 STEP comparisons, retained standard context, exact reproduction
and a 1 mm installed spring-height sensitivity. The curved profiles retain B-spline
boundaries. Hidden saddle/member sections and unprinted stock remain estimates;
failed pin envelopes and the circular-saddle tolerance diagnostic are retained.

Three inspected views bring progression to **211 images**, preserving all 208
previous views. The handbook registration is reused. Anchor supports, high-speed
stops and control rods remain; standard tank011 is unchanged and the full tank
goal remains active.

## 24 September 2026 — high-speed forward fittings and lining hardware

The [forward checkpoint](experiments/drive_chains/transmission_high_brake_front_study/trial01/README.md)
adds four end fittings, 12 steel rivets, 34 copper rivets and 2 brass screws. The
native development has **3,091 occurrences /519 definitions /314 assemblies**.
Source stock is retained. The inferred rear casing bridge now clears the rivet
tails, with bounded material preservation and remaining bridge stock verified.

All 16 stages pass: 104 component checks, 28 material/support checks,
504 development pairs,507 preserved definitions,71 STEP comparisons, retained
standard context, exact reproduction and a 1 mm fitting-stock variation. Full lining
support is checked with explicit countersink-pocket and axial-overhang exceptions.
Failed trials, the curved-face seam diagnostic and original source discrepancies
are retained. The fixed source registration is reused.

Four inspected views bring progression to **208 images**, preserving all 204 prior
images. Pins, levers, adjustment, anchor supports and high-speed stops remain;
standard tank011 is unchanged and the full tank goal remains active.

## 24 September 2026 — high-speed rear brake joints populated

The [rear joint checkpoint](experiments/drive_chains/transmission_high_brake_joint_study/trial01/README.md)
adds M361 anchor ends, 12 steel rivets and 12 coupling screws to the source-sized
high-speed linings/backings. M367 is represented by its component hierarchy.
The development native has **3,039 physical occurrences,
511 definitions and 306 assemblies**.

All 14 stages pass: 406 native checks, 240 development pairs,
504 preserved definitions, 41 STEP comparisons,
retained standard context, exact reproduction and actual anchor-stock sensitivity.
A rejected curved-band cut produced extra material despite passing validity;
reparameterizing the circular cutters resolves it without changing stock.
The anchor's numerical mass check uses verified, refined sections of the unchanged
solid. Failed controls remain available in the checkpoint diagnostics.

Three inspected views bring the progression to **204 images**, preserving all
201 earlier images. The source registration is unchanged and retains the visible
anchor-eye residual. Rear profiles and fastener details remain approximations;
forward fittings, lining fasteners, supports, levers, adjustment and stops are next.
Standard tank011 remains unchanged; the complete tank goal remains active.

## 24 September 2026 — preliminary high-speed brake bands

The [high-speed trial](experiments/drive_chains/transmission_high_brake_study/trial01/README.md)
adds eight lining/backing leaves: **3,013 physical occurrences, 508 definitions and
302 assemblies**. All 344 preliminary native checks and 106 development pairs
pass. The countersink opening direction and signed cone angle are checked after
correcting the initial checker convention; geometry was unchanged.

Original SNL119 supplies the long/short lining stock dimensions. Its continuous
MX109 plus M364 composition differs from HB's six-M364 arrangement; the trial
explicitly selects SNL. An estimated thick backing collided with the retained
case wall. The current thin backing estimate clears it; failed centered and
outboard-shift trials are preserved. No case or drum was revised.

Two inspected snapshots bring the progression to **201 images**, preserving all
199 previous images. This is partial geometry: end ears, anchors, lever/adjustment
pieces, stops and hardware remain. Full face coverage, material preservation,
STEP, rebuild and variation qualification also remain. The spacer checkpoint is
the latest locally qualified predecessor; standard tank011 remains unchanged.

## 24 September 2026 — four brake spring spacers populated

The [spacer checkpoint](experiments/drive_chains/transmission_brake_spacer_study/trial01/README.md)
adds four SH687A annuli and shortens the estimated spring while retaining other
mechanism geometry and frames. The development assembly now has **3,005 physical
occurrences, 504 definitions and 295 assemblies**.

All 13 deterministic stages pass: 321 native checks, 28 development pairs, 502
unchanged definitions, ten STEP comparisons, retained 5,316-component context,
exact fresh reproduction and coupled length/bore sensitivity. The published
manifest and BReps are independently bound to the saved native archive.

Source-supported identity/quantity are separated from estimated stock roles,
bore and swivel-side location. These are reviewed local approximations with
explicit reopening triggers; inherited brake-stop identity and service limits
remain. Three inspected views bring progression to **199 images**, preserving
all 196 earlier images. Standard tank011 remains unchanged.

Next: complete both high-speed brake assemblies. Original SNL composition confirms
both left and right members belong to each lever, joined by four rivets. Bands,
linings, anchors, adjustment pieces, stops and their hardware remain to build.
Then continue controls, frame/hull joints, engine/interior completion, inventory
reconciliation and full standard integration. Poses remain deferred.

## 24 September 2026 — deterministic reuse and source-camera workflow

Implemented the staged CAD runner and compact recovery pointer in
[CURRENT_WORK.json](CURRENT_WORK.json). The real brake-stop replay passes all 18
stages and exactly reproduces the prior trial04's 1,537 archived BReps and 139,961
persistent properties. After an explicit comparison-dependency correction,
17 stages reused and one reran; a subsequent invocation reused all 18 and read-only
freshness verification passed. See the [measured replay](../../benchmarks/cad_pipeline/20260924/README.md).
No model/effort downgrade or production promotion occurred.

Added immutable camera fitting and native-bound source rendering with separate
holdouts, reviewed refits and reciprocal perspective depth. A known-camera control
using real transmission geometry passes and reuses byte-identical renderings.
Historical plate79 still needs trusted landmark review; HB134/135 registration
and standard progression cameras remain unchanged. The
[decision ledger](decision_ledger.json) retains scoped approximations while keeping
identity and source gaps open. No new physical geometry or progression snapshot
is claimed for these tooling controls; total remains 196.

Returned to the standard-geometry queue: directly inspected original SNL218 and
HB101 for the four SH687A adjusting-spring spacers. The catalogue confirms quantity
and the literal stock notation; form, datum meaning and installed location need a
bounded source/interface packet before geometry is added.

## 24 September 2026 — brake-stop mounting and joint validation

The [trial04 revision](experiments/drive_chains/transmission_brake_stop_study/trial04/README.md)
repositions the previously estimated lower cap studs using relative handbook
picks and source-length hardware. Paired rounded bosses and connecting webs
replace the overly bulky trial03 casting. The native assembly remains at
3,001 physical occurrences, 503 definitions and 295 groups.

All 55 mounting and 71 joint/ownership checks pass. The 592 development pairs have
no detected interference, and the 76 affected components have no nearby retained
standard-tank pair. All 89 final STEP comparisons pass after exporting unchanged
components with separate representations. The initial flat-compound failure is
retained. All 490 unchanged definitions are preserved, and fresh reproduction
and a thickness/mounting-height variation pass. The candidate remains experimental
while historical mapping and installation/removal constraints remain open.
Four reviewed views bring the progression to 196 images; prior snapshots and
native baselines are preserved. Standard tank011 remains unchanged.

## 24 September 2026 — experimental brake-stop geometry populated

The [brake-stop packet](packets/P01-transmission-brake-stops.md) now contains a
44-component candidate: four lugs, twelve lug rivets, eight screws, eight nuts,
two bars, two brackets and eight bar rivets. Trial02 has **3,001 physical
occurrences, 503 definitions and 295 assemblies**. Four lower bands gain separate
drilled definitions, and two existing stud/nut/cotter sets advance by the estimated
mounting-tab stock. Upper backing definitions remain shared with the parent.

The saved-native diagnostic finds eleven valid closed solid definitions, 57
passing count/frame checks, no detected interference in 492 candidate pairs and
eighteen positive planar contacts. Trial01's ten interferences are retained.
Four inspected trial views bring the progression to **192 images**; all 188
previous images and 31 recorded native baselines are preserved.

**This is experimental, not a qualified development parent.** The shared
crossbar, M341/M342 versus MX95/MX96 identity and bearing-cap attachment remain
conditional. Under retained drawing registration the mounting nut projects
38–52 mm rearward and 29–39 mm high relative to manual source picks. Full
preservation, mounting/rivet checks, standard context, STEP, parameter and rebuild
qualification remain ahead. The accepted front-brake checkpoint `169c3da` and
standard tank011 remain unchanged. Four SH687A spring spacers identified in
SNL252 also remain to be reconstructed.

## 24 September 2026 — front brake adjustment mechanisms populated

The [front-brake trial](experiments/drive_chains/transmission_brake_front_study/trial01/README.md)
adds 100 physical parts: eight ears, eight pins and cotters, 56 steel rivets and
four sets of screw, spring, swivel, nut and lever. It contains **2,957 physical
occurrences, 492 definitions and 288 assemblies**. Eight backings gain front
attachment holes, and 24 lining rivets use longer stock. All inherited frames
remain fixed.

All **119 native checks and 996 development material pairs pass**. The retained
standard context has 5,316 occurrences and no nearby affected pair. All 482
unchanged definitions are preserved; a fresh rebuild reproduces 1,504 BReps and
137,434 persistent properties. A pivot-height/stand-off variation passes the
native checks and preserves all 482 unchanged nominal definitions.

All **142 STEP comparisons pass**. Five spring pairs required verified,
independently refined solid partitions for mass integration; the original
material, centroid and convergence thresholds are preserved. The other 137
passing pairs remain unchanged. The front-brake checkpoint is the new locally
qualified development parent; historical layout and service qualification remain
open.

Five new views bring the progression to **188 images**, preserving all 183 prior
images. Fixed-datum handbook overlays retain the forward/low pivot station
residuals; local joint fit does not establish historical accuracy. Hidden fork,
swivel and spring dimensions remain estimates. Stops, control rods, high-speed
brakes and broader engine/interior completion remain ahead; standard tank011
and the priority of geometry before poses are unchanged.

## 24 September 2026 — rear brake anchors and riveted feet populated

The [rear-anchor trial](experiments/drive_chains/transmission_brake_anchor_study/trial01/README.md)
adds eight rear brackets, four anchor pins, four springs, two spacers, four
retainer rivets and 60 steel rivets. Sixteen lining rivets use longer stock
through the feet. The development assembly now contains **2,857 physical
occurrences, 484 definitions and 276 assemblies**. Printed lining lengths and
hole pitches remain fixed; each lining group advances four degrees as the
estimated rear half-gap grows to five degrees.

All **106 native checks, 1,362 development material pairs and 342 STEP comparisons
pass**. The full retained standard context contains 5,316 occurrences and no
possible affected pair. All 472 unchanged inherited definitions are preserved:
453 exact BReps and 19 strict comparisons. Reproduction matches 1,478 BReps and
133,313 persistent properties. A thicker-foot/inset-lug parameter variation
passes the same native/context checks and retains all 472 unchanged nominal
BReps. Five inspected views give **183 progression images**, preserving 178 prior
images and 30 recorded native baselines.

Rejected layouts exposed real retainer and chain-case interference. The final
static joint fits; hidden lug/pin/spring sections and rivet forms remain named
estimates. Handbook coupling screws, additional MX49 rivet applications and the
source/model anchor-station residual remain unresolved. A false incomplete-seat
report was traced to omitted support patches; the corrected union-coverage
check retains negative controls and is documented in the FreeCAD skill.

Next: front ears/pins, adjusters, levers, stops, high-speed brake fittings and
support fastening; then remaining frame/hull joints, engine and tank interiors,
inventory reconciliation and standard integration. Standard tank011 remains
unchanged. Full-tank completion and pose work remain ahead.

## 24 September 2026 — brake suspension links and pivots populated

The [link study](experiments/drive_chains/transmission_brake_link_study/trial03/README.md)
adds four M337 links, four individual M339 pins and eight split pins. The
development model now has **2,775 physical occurrences, 474 definitions and
268 assemblies**. Six support pieces move to the inboard band sides, replacing
the earlier estimated centered placement; the frame and bands retain their
geometry. Cubic B-spline web profiles approximate the handbook link contour.
The earlier two-pin source count and hidden transverse arrangement remain
unresolved; lower anchors and foot fastening are not installed.

All **106 native/context checks, 92 development material pairs and 25 STEP
comparisons pass**. All 471 inherited definitions are preserved (448 exact,
23 strict material matches). Fresh reproduction matches 1,448 BReps and 129,795
persistent properties. A bow/clearance variation passes the same checks and
retains all 471 inherited nominal BReps. Four inspected images bring the visual
progression to **178**, preserving 174 prior images and 29 native baselines.

The rejected centered layout intersected the diaphragm. Inboard placement clears
it without changing the frame, while source overlays retain the drawing/model
registration residual. Next: rear anchor brackets/pins and riveted joints,
front ears, adjustment/control hardware and support fastening; then remaining
frame/hull joints and broader engine/interior coverage. Standard tank011 remains
unchanged; full-tank completion and poses remain ahead.

## 24 September 2026 — segmented transmission brake bands populated

The [brake-band trial](experiments/drive_chains/transmission_brake_band_study/trial01/README.md)
adds eight steel half-bands, 24 lining segments and 216 copper rivets. The
development assembly now has **2,759 physical occurrences, 471 definitions and
268 assemblies**. Printed handbook lining radii revise two provisional drum
friction lands while preserving their interiors, end interfaces and placements.
The earlier segmented arrangement is explicitly distinguished from later SNL
long strips. Steel stock, split geometry, rivet details and shoulder profiles
remain documented estimates; ears, anchors, linkage and fastening are unfinished.

All **154 native/context checks, 1,090 development material pairs and 259 STEP
comparisons pass**. The full retained standard context contains 5,316 occurrences
and no possible affected pair. All 464 unchanged definitions are preserved:
446 exact BReps and 18 strict comparisons. Fresh reproduction matches 1,439 BReps
and 129,129 persistent properties. A thicker-band/wider-seam variation passes the
same native/context checks and preserves all 466 inherited nominal definitions.

Default FreeCAD mass integration produced false centroid discrepancies on
perforated curved bands. Adaptive integration qualifies the unchanged STEP solids
with the original material and centroid limits; failed diagnostics are retained.
The reusable adapter and FreeCAD skill now document that finding. Four inspected
progression snapshots give **174 total**, preserving all 170 earlier images and
28 recorded native baselines.

Next: band end ears and anchors, M337 links, the unresolved M339 pin arrangement,
adjustment mechanism and support fastening; then remaining frame/hull attachments
and broader engine/interior coverage. Standard tank011 is unchanged; poses stay
deferred and the complete-tank goal remains unfinished.

## 24 September 2026 — brake suspension brackets and stops populated

The [brake suspension trial](experiments/drive_chains/transmission_brake_suspension_study/trial02/README.md)
adds four source-identified M338 brackets and two M385 stops. The development
model now has **2,511 physical occurrences, 466 definitions and 231 assemblies**.
All prior occurrence frames and all 464 inherited definitions are preserved.
The supports seat on the upper channel; their foot fastening, suspension links,
pins and brake bands remain incomplete.

All **53 native/context checks, 14 development material pairs and eight STEP
comparisons pass**. Standard-context filtering covers 5,316 retained physical
occurrences and finds no possible pair with these six supports. Preservation
uses 438 exact BReps and 26 strict material comparisons. Fresh reproduction
matches 1,424 BReps and 119,708 persistent properties. A wider-foot/thicker-lug/
lower-pin variation passes the same checks and preserves all inherited BReps.

The first channel-registered layout collided with the diaphragm and stops.
The revised bracket station follows the source pin-to-shaft separation; source
registration still disagrees by 9.576 mm longitudinally and 15.269 mm vertically.
Both the rejected trial and the visible source-overlay disagreement are retained.
Profiles, stock and hidden joints remain explicit estimates, not historical
qualification. Three inspected progression snapshots give **170 total**,
preserving all 167 prior images and 27 recorded native baselines.

Next: connected brake linkage/bands and support fastening, remaining 46 frame
rivets and return/upright joints, holding feet, packing and hull attachment;
then remaining engine/tank interiors and final integration. Standard tank011
remains unchanged and poses remain deferred.

The older coupled-pump render job has now completed successfully. Its renderer
was generating three views inside a 242-part loading loop. Moving rendering after
collection reduces 726 view renders to three; all three final PNGs are byte-identical
to the old terminal outputs. The [diagnostic record](experiments/drive_chains/engine_pump_receiver_study/assembly_trial02/diagnostics/render_loop/README.md)
retains both receipts and the old implementation. The FreeCAD runtime guidance
records the lesson. This fixes rendering overhead without promoting the old
pump registration or adding a progression milestone.

## 24 September 2026 — frame overlaps and first rivet group reconstructed

The [frame-joint trial](experiments/drive_chains/transmission_frame_joint_study/trial03/README.md)
adds **32 rivets**: 24 at gusset/channel joints and eight at diaphragm/upright
overlaps. Eight gussets acquire formed returns and the middle diaphragm acquires
overlapping seats. The printed rivet stock volume is retained through upsetting.
The development model has **2,505 physical occurrences, 464 definitions and 226
assemblies**. Prior occurrence frames and MX1 bearing-pad contacts remain fixed.

All **250 native checks, 238 development material pairs, one standard-context
pair and 55 STEP comparisons pass**. All 454 unchanged definitions match the
parent. Fresh reproduction matches 1,418 BReps and 119,075 persistent properties;
a return-height/hole-position variation passes the same native/context checks.
The rejected four-rivet corner layout and an interrupted preservation run remain
documented. Three inspected progression images give **167 total**, preserving
164 prior images and 26 recorded native baselines.

The source gives this rivet group's size and count; allocation, formed returns,
diaphragm overlap and head proportions remain explicit mechanical approximations.
The remaining 46 frame rivets, upright/return fastening, M338/M385 brake supports,
holding feet and complete hull attachment remain next. Standard tank011 is
unchanged; full engine/interior coverage and final integration remain unfinished.

## 24 September 2026 — twenty transmission bracket joints populated and checked

The [MX1 mounting trial](experiments/drive_chains/transmission_bracket_mount_study/trial01/README.md)
adds 80 bolt/nut/pin/washer occurrences, giving **2,473 physical occurrences,
463 definitions and 215 assemblies**. Four receiving definitions change; existing
occurrence frames stay fixed. All **257 native checks, 418 development material
pairs, one retained standard-context pair and 94 STEP comparisons pass**.
All 457 unchanged definitions match the parent. A variation of hole spacing and
bolt length passes the same native/context checks. Fresh reproduction matches
1,415 BReps and 117,408 stable properties; only 24 generated assembly UUIDs vary.

The handbook comparison now uses the apparent removed-unit orientation, with
the forward input axis upward. No physical pose changes. Casting silhouettes
and incomplete frame hardware remain visible discrepancies. The source gives
twenty joints, but the selected hole pattern, bolt length and inside-pad revision
remain explicit hypotheses. Three inspected progression images give **164 total**,
preserving all 161 prior images and 25 recorded native baselines.

The older preservation jobs have finished: all 461 following-frame definitions
and all 449 unchanged casing definitions pass. The initial bracket measurement,
Boolean and generated-UUID failures are retained with their diagnoses. Next:
holding interfaces, feet, frame hardware and casting-profile refinement, then
remaining engine and tank interiors. Standard tank011 remains unchanged; the
full model is incomplete and poses stay deferred.

## 23 September 2026 — constant-stock chain casings reconstructed

The [casing trial](experiments/drive_chains/engine_pump_receiver_study/registration/native_casing_trial01/README.md)
rebuilds twelve definitions and repositions 134 fasteners around the revised chain
route, preserving normal sheet thickness and the handbook's 6⅝ inch width.
All **326 local checks, 1,340 development material pairs, 27 standard-context
pairs and 169 STEP comparisons pass**. Both alternative source-axis stations pass
63 local regeneration checks. Fresh reproduction matches 1,409 BReps and 113,542
persistent properties. The hierarchy retains 2,393 physical occurrences.

Four views were inspected. Three new progression images give **161 total**,
preserving all 158 previous images and 24 recorded native files. The source
overlay retains visible shaft-height disagreement; historical station, fastener
schedule conflicts and complete mounting remain open. Sixteen save-normalized
definitions need strict preservation checks, alongside the running parent check.
The corrected packing-bore measurement and initial diagnostic are retained.

The installed FreeCAD 1.1.1/OCC 7.8.0 runtime was rechecked successfully on resume.
Next: transmission holding interfaces, feet, packing and hardware, followed by
remaining engine and tank interiors. Standard tank011 is unchanged; poses remain
deferred and the complete-tank goal is unfinished.

## 23 September 2026 — following-frame placement checked against the full standard context

The [following-frame trial](experiments/drive_chains/engine_pump_receiver_study/registration/native_following_frame_trial01/README.md)
retains the original transmission castings and moves the 15 frame occurrences
with the shaft. **53 native checks, 77 development material pairs and the sole
spatially possible frame/standard-tank pair pass.** Filtering covers all 5,326
physical standard occurrences. All **36 local STEP comparisons** pass, and fresh
reproduction matches 1,409 BReps and 113,542 persistent properties.

The source overlay improves relative channel-height agreement. This becomes the
preferred development placement, with attachment explicitly unfinished: the
channels remain 18.771 mm from the rear bulkhead and the lower channel 55.218 mm
above the floor. HB127 and SNL27/205 identify the missing holding interface and
separate bolt/screw hardware; they do not establish an arbitrary spacer thickness.
Feet, packing, complete fastening and constant-stock chain casings remain next.
A separate direct source-material comparison is running to close inherited
save-normalization gates; its final report is required before claiming that result.

Five views were inspected and three progression snapshots saved: **158 total**,
preserving all 155 earlier images and 24 recorded native files. Standard tank011
is unchanged. The full tank and its interior remain incomplete; poses are deferred.

## 23 September 2026 — transmission frame hypothesis checked against sources

The [fixed-frame trial](experiments/drive_chains/engine_pump_receiver_study/registration/native_frame_trial02/README.md)
rebuilds four bearing brackets and central case webs, resetting all sixteen MX5
joint constituents to the retained channels. **125 native checks, 279 material
pairs and 26 STEP comparisons pass.** Two local variations each pass 37 checks.
Fresh reproduction matches 1,409 archived BReps and 113,545 object properties.
The detached-boss attempt and corrected diameter measurement are retained.

The source overlay reopens frame placement: holding the frame fixed while raising
the shaft lowers its relative projections about 55.8 pixels, worsening SNL23
agreement. Compare a frame that follows the shaft against source sections and
hull attachments before choosing the station and rebuilding casings. Inner
packing/MX1 hardware, source ambiguities and strict preservation of save-normalized
definitions remain open. Local mechanical fit is not historical qualification.

Four views were inspected; three new progression images give **155 total**,
preserving all 152 prior images and 24 recorded native files. Standard tank011
remains unchanged at 5,326 physical occurrences. The full tank is incomplete.

## 23 September 2026 — coupled planetary phases and rebuilt engine supports

The [phase trial](experiments/drive_chains/engine_pump_receiver_study/registration/native_phase_trial01/README.md)
propagates the output-shaft alignment through both planetary stages using the
handbook's mechanical coupling. All nine criteria, twelve mesh checks and
832 affected material comparisons pass; 142 occurrences are rephased.

The subsequent [support trial](experiments/drive_chains/engine_pump_receiver_study/registration/native_support_trial01/README.md)
rebuilds three engine brackets between retained floor attachments and the trial
engine height. All four rail/bracket contacts are restored. **191 native checks,
102 affected material pairs and all 64 support STEP comparisons pass.** A fresh
build reproduces all 1,409 archived BReps and 113,542 persistent object properties.
Three directly inspected images bring the progression to **152**, preserving all
149 earlier images and 24 recorded native files. Standard tank011 is unchanged.

The source merged pump hierarchy has now passed its eight independent criteria,
including all 83 strict definition-material comparisons and all 2,393 occurrence
frames. Its legacy render job remains active; its intermediate images are not
accepted final reviews. The later registration trials still need strict checks
of their save-normalized definitions. Chain casings, transmission frame/bearing
seats, engine mounting holes and complete installation remain open. The chosen
mean-axis station remains provisional, with ±35.57 mm source-pick uncertainty.

## 23 September 2026 — resumed powertrain placement trial

The runtime and saved checkpoint were verified after resuming. A separate
[native registration diagnostic](experiments/drive_chains/engine_pump_receiver_study/registration/native_trial01/README.md)
retains all 2,393 development occurrences and installs the mean-axis hypothesis
for measurement only. Both chains pass all **886 nearby material comparisons**;
the saved oil-pump envelope clears the unchanged floor by **7.494 mm**.

The diagnostic exposes the next coupled changes: rephased shafts clash with
their internal planet-carrier disks by 2,038.844 mm³ per side, 128 chain/casing
pairs clash, and four engine rail/bracket contacts open by 51.369 mm. Internal
transmission phases, casings and supports require coordinated reconstruction.
The drawing's height uncertainty remains ±35.57 mm. Of 461 definitions, 401 retain
exact BRep bytes and 60 require material-preservation checks after saving.
Two diagnostic views were inspected; the standard tank and its 149-image visual
progression remain unchanged. The source-profile oil pump's full STEP validation
has now finished: **all 186 comparisons pass**. The merged-hierarchy material
validator remains active.

## 23 September 2026 — coupled pump receiver and datum study

The [coupled receiver](experiments/drive_chains/engine_pump_receiver_study/README.md)
now matches the smaller oil pump and printed 171.45 mm water-drive spacing.
Nominal and four-control variation pass **44 native checks, 77 case pairs and
22 cross-component pairs, plus both strict STEP frames**.
Fresh reproduction matches both shapes and 162 properties.
The first variation is retained as a rejected gasket-support test. Three local
views were inspected and two snapshots saved: **149 total**, preserving all
147 earlier images and standard native files.

A saved development hierarchy contains 2,393 physical occurrences. Independent
material/frame verification remains in progress; an interrupted checker is
replaced by workers that release memory between comparisons, retaining the same
acceptance expression and exact-pair evidence. The standard tank remains at
5,326 physical occurrences. The source-profile pump's full STEP check is also
still running.

The floor conflict remains unresolved. Three source-relative axis hypotheses
now satisfy the fixed-phase 50-link chain closure mathematically. The mean-axis
trial moves the powertrain +6.264 mm forward and +51.369 mm upward, leaving
7.494 mm under the pump. No hypothesis is installed; source registration,
supports, transmission, controls and actual chain/casing fits still need work.
The next oil-distribution inventory identifies 18 prospective constituents,
including one large and six small bearing-feed tubes, with two explicit source
conflicts. The full engine and tank remain unfinished.

## 23 September 2026 — source-constrained pump proportions

The [pump-layout study](experiments/drive_chains/engine_pump_layout_study/README.md)
applies HB printed68 Plate45's printed water-pump axis drop (171.45 mm) and oil
connection levels, with its **aviation mounting** applicability explicit. Local
image measurements reject the former oversized oil casing. The revised
146-component pump has a 144 mm body, 169 mm flange and shallower chamber with a
deeper bottom dish. **402 saved-native checks, 482 material pairs and seven
conditional source-envelope checks pass**. Fresh reproduction matches 81 BReps
and 7,376 properties. Rejected gallery/wall trials are retained. Pump STEP and
combined installation qualification remain pending.

The revised lower drive passes 37 component checks and all 27 strict STEP
comparisons; its obsolete case interfaces remain unqualified. Seven pump views
and a before/after handbook overlay were inspected. Two snapshots bring the
progression to **147**, preserving all prior images and standard native files.
Global engine/drivetrain height, receiving case, remaining wires/connections
and source refinements still need work. Standard tank011 remains unchanged at
5,326 physical occurrences; the full tank is incomplete.

## 23 September 2026 — oil-pump mounting and installation conflict

The [oil-pump checkpoint](packets/P01-engine-oil-pump.md) now has **146 physical
constituents in 40 definitions**. Ten source-length mounting stud/washer/nut/
cotter sets and gasket8348 add 41 pieces; the flange stack and rounded nose
support the source joint span and ten-hole pattern. Both nominal and eight-control
trial builds pass **402 native checks, 466 material pairs and 186 STEP
comparisons**. Fresh reproduction matches 81 BReps and 7,376 object properties.
Only the lower casting changes among prior components; 75 previous BReps and
1,049 checked frame/identity properties remain identical.

Seven source-review views were inspected. Two saved snapshots bring the
progression to **145**, preserving all earlier images and standard natives.
The original 35-part pump's full STEP check also finished: all 67 comparisons pass.

The first actual installation probe rejects the proposed pump position: **12
collisions in 54 nearby pairs**, with floor plate M1935 and the current crankcase.
A rigid 62.5165 mm raise would clear the floor envelope, but a trial with 1 mm
extra clearance then collides with the water drive and shaft coupling. Section
views and both failed trials are retained. Reconcile pump scale, lower-drive
spacing and engine/drivetrain registration against HB58/SNL14/SNL2 before
reconstructing the receiver and integrating the pump. Two wires, source profiles,
ports and external connections also remain open. Standard tank011 remains
unchanged at 5,326 physical occurrences; the full tank is incomplete.

## 23 September 2026 — oil-pump fastening sets and relief lock

The [oil-pump checkpoint](packets/P01-engine-oil-pump.md) now has **105 physical
constituents in 38 definitions**: all fourteen internal bolt sets and the
source-length cage-to-bolt wire are added. Underside access wells preserve the
strainer seat and at least 2.397 mm to the checked galleries. **266 saved-native
checks and 345 material comparisons pass**. Fresh reproduction matches 77 BReps
and 6,059 object properties; a four-control local wire probe passes its material,
stock and self-clearance checks. All 143 native/STEP pairs are qualified: 135
direct strict comparisons plus eight exact-pair reuses from completed screen
checks, with identity placement, unit scale and full coverage verified.
Six views were inspected; two snapshots bring the progression to 143, preserving
all prior images and standard natives. The folded-wire diagnostic also improves
the reusable FreeCAD guidance. Two wires, mounting components, source-profile and
port refinement, coupled full-pump qualification, crankcase fit and standard
integration remain open. The complete tank and pump remain unfinished.

## 23 September 2026 — oil-pump core, passages and strainers

The [oil-pump study](packets/P01-engine-oil-pump.md) now contains **35 physical
constituents in 32 definitions**: the five-gear core, castings and passages,
relief unit, bottom closure, two filter baskets with separate coarse open-gauze
representations, and screen nut/lock. The saved native passes **138 checks and
123 material comparisons**, including 27 gear-mesh samples. STEP comparisons
are still running; exported files alone are not qualified exchange results.
Five views were inspected and two snapshots saved, bringing the progression to
141 while preserving all previous images and standard natives. Printed mounting
stud dimensions expose a flange-stack revision still to be made. Fasteners,
lock wires, external fittings, parameter/reproduction trials, crankcase fit and
standard integration remain open. This separate study is not added to the
standard tank or prior drivetrain component count.

## 23 September 2026 — water-pump source connections and drain lock

The [new checkpoint](packets/P01-engine-water-pump-connections.md) applies HB191's
printed inlet/outlet tube stocks and integral ownership, and adds the source-length
No18 drain wire. The development assembly has **2,247 physical occurrences**:
77 pump constituents in 29 definitions. Nominal **59 native checks, 481
context pairs and 108 STEP comparisons pass**; the ten-control trial also passes
59/482/108. Fresh reproduction matches 851 BReps and
53,393 checked properties. Source quantities/alternatives and estimates
remain explicit. Six views were inspected; two snapshots bring the progression to
139, preserving all 137 earlier images and 20 standard natives. Oil pump,
remaining engine geometry and standard integration remain unfinished.

## 23 September 2026 — water-pump fluid passage corrected

The [passage correction](packets/P01-engine-water-pump-passage.md) removes drain-boss
material that entered the intended fluid cavity. The retained original trial
reproduces the outlet-gauge failure. Both corrected configurations pass without
changing gauges or tolerances: **39 native checks, 472 nominal / 473 trial context
pairs, and 106 STEP comparisons each**. The development assembly still contains
2,246 physical occurrences. Only the pump body changes; the other 846 serialized
shapes and 45,133 checked assembly properties match the previous checkpoint.
Fresh nominal reproduction matches all 848 shapes and those properties.
Five views and local before/after sections were inspected. All 137 progression
images and 20 standard natives are preserved. Drain lock wire, source conflicts,
remaining engine components and standard integration remain open.

## 23 September 2026 — water-pump mounting revision

The [mounting candidate](packets/P01-engine-water-pump-mounting.md) adds the four
source-length case stud/nut/washer/cotter sets and integral receiving pads. It
reconciles the flange stack, tangential outlets and drain seat in a 2,246-occurrence
development assembly: 76 pump constituents, one revised case and 2,169 preserved
parent components. **All 38 native checks and 472 affected material comparisons,
including standard context, pass.** All 106 nominal STEP comparisons pass. The six-control trial passes 37/38 native checks and all 473 local pairs, but
finds drain-boss interference with an outlet passage gauge; that correction is
next. Fresh nominal reproduction matches 848 shapes and 45,133 checked properties. Five views were inspected and two
snapshots saved (137 total). The standard tank remains unchanged.

## 23 September 2026 — water-pump development

The [water-pump candidate](experiments/drive_chains/engine_water_pump_study/DrivetrainWithWaterPump.FCStd)
adds 60 physical constituents in 24 definitions: geared shaft, radial bearing
internals, two packing/gland sets and spring, open impeller, pump body and
outlets, inlet cover, sealing layers, drain plug and eight cover stud sets.
The development document contains 2,230 occurrences and preserves all 2,170
inherited parts. **All 26 native checks and 202 material comparisons pass**,
including nine gear-mesh samples and eight complete-rotor rotation samples.

**82 of 84 STEP comparisons pass.** The pump body fails the unchanged native
kernel-tolerance limit in both coordinate frames; both exported body solids
are valid and have zero material differences. A separate spherical-pocket
parametrization fix resolved the bearing cage's STEP failure without changing
material. Frozen diagnostics retain both findings.

The [packet](packets/P01-engine-water-pump.md) documents remaining source conflicts
and the mounting constraint found in SNL239: the printed stud thread lengths
require revision of the estimated flange stack. Case receivers, mounting
hardware, drain lock wire, body precision, profile refinement, parameter trial,
fresh reproduction and standard integration remain open. Five views were rendered,
three final views directly inspected, and two progression images saved (135 total).
All prior images and standard native documents remain unchanged.

## 23 September 2026 — lower-drive receiving casting

The [receiving-case candidate](experiments/drive_chains/engine_lower_drive_installation/DrivetrainWithLowerDriveReceivers.FCStd)
revises one integral lower crankcase, preserving the other 2,169 physical
occurrences in the 2,170-occurrence development document. The cylindrical lug,
retaining-screw support, oil-access recess and both pump openings now have
explicit geometry. **25 independent checks, 261 affected material pairs
including standard tank context, and two casing STEP comparisons pass**. The
complete 16-piece removable unit clears a continuous downward envelope through
the casing. Actual saved-driver mesh/free-play checks, a seven-control coupled
trial and an independent fresh reproduction pass.

Six native views were compared with the source figures; two new progression
images bring the total to 133, preserving all 131 earlier images and 20 standard
native files. The [packet](packets/P01-engine-lower-drive-receivers.md) retains
estimated casting dimensions and the 184 mm pump-axis drop. Actual water/oil pumps,
receiving attachment features, source-profile refinement and standard integration
remain open. This is a verified geometry checkpoint, not a completed powerplant.

## 23 September 2026 — lower distribution component study

The [lower distribution study](experiments/drive_chains/engine_lower_drive_study/DrivetrainWithLowerDriveStudy.FCStd)
adds **17 physical constituents in ten definitions**, preserving all 2,153 parent
occurrences in a 2,170-occurrence development document. The integral 22/21-tooth
driver, two split bushes, two housing halves, dowel, two complete clamp sets and
retaining screw are represented. **37 component checks and 27 STEP comparisons
pass**. The 68 affected material pairs include **3 unresolved contacts with the
inherited lower casing**; installation and standard tank context are not qualified.
The [packet](packets/P01-engine-lower-distribution.md) records source-range bearing
fits, a native mating-gear experiment, source-led cup/access corrections and
estimated dimensions. Six revised native views were inspected. Two new study
images bring the progression to 131; all previous images and standard native
documents are unchanged. Pump-axis reconciliation, the casting lug and screw
support, oil-pump opening and full-unit withdrawal precede installation acceptance.

## 23 September 2026 — engine driving bevel and thrust-nut lock

The latest [engine driving-gear candidate](experiments/drive_chains/engine_gear_build/DrivetrainWithEngineGear.FCStd)
contains **2,153 physical components**: 22 new, two locally revised and 2,129
preserved parent occurrences. The main bevel has 33 spline-flanked teeth, an
integral estimated starting claw and splined hub, six complete bolt sets and one
provisional thin shim. The thrust nut has a radial lock screw and formed wire.
Nominal **93 independent checks, 428 affected material pairs including standard
context, and 33 native/STEP comparisons pass**. A coupled module/face/web trial
passes 93/428/33, including STEP. Six native views were inspected;
three new images bring the progression to 129. The [packet](packets/P01-engine-driving-gear.md)
retains the handbook bolt-grip conflict and unverified hub/locking details.
Mating gears, final backlash/shims/timing and the remaining engine systems are
pending. Combined qualification and standard integration remain open.

## 23 September 2026 — shaft closures and retaining sets

The [shaft-closure development candidate](experiments/drive_chains/engine_shaft_fittings_build/DrivetrainWithEngineShaftFittings.FCStd)
contains **2,131 physical components**: 139 new plugs, gaskets and retaining
constituents, one revised shaft and 1,991 preserved parent pieces. Nominal
**268 independent checks, 738 affected material pairs including standard context,
and 157 STEP comparisons pass**. Six continuous oil-route witnesses pass with
the stud sets installed. A coupled cap/gasket/nose-bore trial passes
268/738; trial STEP remains unchecked. Seven views were inspected;
three snapshots bring the progression to 126. The
[packet](packets/P01-engine-shaft-fittings.md) preserves catalogue conflicts and
inferred cap/nose geometry. Gear, shims, thrust lock and the remaining engine
systems are pending; combined qualification and standard integration remain open.

## 23 September 2026 — crankshaft and bearings

The [development assembly](experiments/drive_chains/engine_crankshaft_build/DrivetrainWithEngineCrankshaft.FCStd)
contains **1,992 physical occurrences**: 81 new, two revised cases and 1,909
preserved inherited pieces. Seven source-sized bearing pairs, fourteen dowels,
a hollow six-throw forging, double thrust internals and output retention are
represented. This is a development count including context, not an additive count
for the standard tank. Bearing quantity selection follows the individual SNL17
entries and LIB17, with contrary SNL58 wording retained.

Nominal 437 independent checks, 517 affected material pairs including standard
context and 101 STEP comparisons pass. A coupled parameter trial passes
437/517; variant STEP is not checked. Eight native views were inspected
against source figures. Three new images bring progression to 123; all 120 previous
images and 20 standard native files are unchanged. Standard geometry remains the
priority before poses. See the [packet](packets/P01-engine-crankshaft.md) for
approximations, rejected diagnostics and pending shaft plugs/gear, cylinders,
services, mounting reconciliation, combined qualification and integration.

## 23 September 2026 — clutch-stop anchor and operating linkage

The [development assembly](experiments/drive_chains/clutch_brake_linkage_build/TransmissionWithClutchBrake.FCStd)
contains **1,821 physical occurrences**: 35 new pieces, four revised receiving
parts and 1,782 preserved parent occurrences. The anchor, six rivets, mounting
hardware, spring-loaded eyebolt, stop rod and complete bell-crank pin assembly are
populated. The native band assembly owns its 26 catalogue children. Local counts
are not additive to the standard tank inventory.

All 112 independent checks, 273 affected material pairs including standard
context, and 64 STEP comparisons pass. A coupled dimensional trial passes 112
checks and 271 local pairs. Two final mounting overlaps were resolved by
finishing the estimated web at its mating plane and moving the carrier return
4mm outward. No source hardware size or numerical acceptance tolerance changed.
Six native views were inspected; three progression images bring the total to 111,
preserving all 108 earlier images.

The [packet](packets/I03-clutch-brake-linkage.md) retains the unproven mounting and
linkage arrangement, source-registration and complete-clutch-length questions.
Engine-frame/engine receivers and forward controls are next. Combined drivetrain
qualification and standard integration remain required. Standard tank011 and its
20 native documents are unchanged; the full-tank goal remains active and incomplete.

## 23 September 2026 — clutch supports and auxiliary controls

The [development assembly](experiments/drive_chains/clutch_support_build/TransmissionWithClutchSupports.FCStd)
contains **1,786 physical occurrences**: 27 new mechanism pieces, one replacement
floor context, two revised parent parts and 1,756 unchanged inherited occurrences.
It adds both supporting brackets and their eight cap screws, the cup setscrew,
auxiliary shaft/levers/keys/taper pins, and the rear rod with forks and pin assemblies.
The floor copy is replacement context and must not be duplicated at integration.

Full-source review corrected the control direction and withdrew the unsupported
main-shaft split-pin assignment. That pin belongs to the pending M4165 bell-crank
joint. The estimated bracket mounting uses underside screw heads, real floor
clearance holes and blind receiving bosses. Attachment to this floor remains a
historical hypothesis to revisit with the engine frame.

All 117 independent geometry checks, 88 affected material pairs including standard
context, and 46 STEP comparisons pass. A coupled dimensional trial passes 117 checks
and 78 local pairs. Five native views were inspected; three new progression images
bring the total to 108, preserving all 105 previous images. A retained split-pin
exchange failure and successful analytic replacement inform a focused FreeCAD skill
note. No acceptance tolerance was relaxed.

The [packet](packets/I03-clutch-supports.md) and its receipts preserve all source and
qualification limits. Full brake/forward controls, engine-frame receivers, overall
clutch length and source registration remain open. The candidate is unqualified;
standard tank011 and all 20 standard native documents remain unchanged. The full
tank goal is active and incomplete.

## 23 September 2026 — clutch release bearings, forks and shaft

The [development assembly](experiments/drive_chains/clutch_throwout_build/TransmissionWithClutchThrowout.FCStd)
contains **1,758 physical occurrences**, adding77 and preserving all1,681 parent
occurrences. It populates the two release bearings, pins and retaining hardware,
fork levers, main shaft, operating lever and three keys. The two catalogue
bearings contain54 estimated internal pieces; the77 additions represent25
catalogue-level installed items, not77 independently source-enumerated parts.

All90 independent checks,332 affected material pairs and93 STEP comparisons
pass. A coupled bearing-internal/shaft-height trial passes90 checks and368 local
pairs. Five native views were inspected; three new snapshots preserve all102
earlier images, bringing the progression to105.

The [packet](packets/I03-clutch-throwout.md) retains the unresolved overall clutch
length and source registration, and identifies all inferred dimensions. Supporting
brackets, retention, auxiliary controls and complete brake linkage remain required.
The shaft lies78.28mm above an existing floor plate; detailed frame support and
attachment are not yet established. The candidate remains unqualified and is not
integrated into standard tank011. The full-tank goal remains active and incomplete.

## 23 September 2026 — clutch-stop band development

The [development candidate](experiments/drive_chains/clutch_stop_band_build/TransmissionWithClutchStopBand.FCStd)
contains **1,681 physical occurrences**. It adds M4158 band, M4159 lining,
fourteen copper lining rivets and three button rivets at an inferred returned
pin eye. HB115's 9.25in stop-drum diameter replaces the former 9in estimate;
the belt, pump and supports update coherently. There are 85 affected parent
occurrences and 1,577 preserved ones.

All 119 independent checks, 472 affected interference pairs and 23 definition/
installed STEP comparisons pass. Two stock/gap/eye-size trials each pass the
119 independent checks and 111 local material pairs. These are development
checks; broader qualification and a fresh reproduction remain required.
Five native views were inspected. Three new progression images preserve all
99 previous images, bringing the total to 102.

The sharper original SNL2 drawing improves the throwout-shaft reading and exposes
an unresolved comparison with the inherited clutch proportions. The
[packet](packets/I03-clutch-stop-brake.md) and
[envelope review](experiments/drive_chains/clutch_envelope_review.json) retain
HB115's uninterpreted 19.875in complete-unit dimension and alternative endpoint
spans. Resolve the axial budget and shaft/bearing receivers before constructing
the anchor attachment. The current candidate is **not qualified or integrated**;
M4160, six anchor rivets and the full brake/throwout linkage remain required.

The qualified drum/flywheel checkpoint remains the accepted baseline. Standard
tank011 and its transparent-hull view are unchanged. Engine/crankshaft, remaining
interiors, complete coverage, integration and later poses remain full-goal work.

## 23 September 2026 — outer clutch drum and flywheel

The [latest isolated native assembly](experiments/drive_chains/clutch_drum_build/TransmissionWithClutchDrum.FCStd)
contains **1,662 physical occurrences**. Nine additions represent the outer drum,
flywheel, six drilled cap screws and their source-length 48in locking wire.
The existing 30in plunger wire turns inward to clear the dished flywheel;
1,652 other parent occurrences retain their geometry and placement.

All 270 independent checks, 262 affected interference pairs, five definition and
ten installed STEP comparisons pass. Two coupled stock/bend/tooth-count trials
each pass 68 checks and 262 pairs. A fresh build repeats the nominal geometry
and exchange checks. Six source/native views were inspected; four new progression
images preserve all 95 earlier snapshots.

The [packet](packets/I03-clutch-drum.md) records source conflicts, estimated tooth
form and mounting profiles, and the steeper modeled flywheel dish compared with
the handbook sketch. The complete crankshaft installation must revisit the dish
and hub interpretation. Clutch-stop brake, engine retention/starter, remaining
interiors, integration and coverage remain required. Standard tank011 and its
transparent-hull view are unchanged; the full goal remains active and incomplete.

## 22 September 2026 — plunger locking wire and head passages

The [latest isolated native assembly](experiments/drive_chains/clutch_retention_build/TransmissionWithClutchRetention.FCStd)
contains **1,653 physical occurrences**. One source-specified 30in SH861K wire now
passes through six real head bores in the existing shared plunger definition.
The other 1,646 parent occurrences retain their geometry and placement.

All 84 independent checks, 68 affected interference pairs, two definition and seven
installed STEP comparisons pass. Two wire/bore-size trials each pass 22 checks
and 68 pairs; a fresh build/check repeats the nominal result. Higher-accuracy OCC
integration resolves a default spline-volume measurement error without changing
the geometry or acceptance tolerance. Five views were inspected and three new
progression images are saved, preserving all 92 prior images.

The [packet](packets/I03-clutch-retention.md) documents estimated wire diameter,
route, twist and drilling. Next are the outer drum, flywheel/crankshaft interface
and clutch-stop brake, including a clearance check for the projecting wire tail.
Standard tank011 and its transparent-hull view remain unchanged. The complete-tank
goal remains active and incomplete.

## 22 September 2026 — clutch cone and spring sets

The [latest isolated native assembly](experiments/drive_chains/clutch_cone_build/TransmissionWithClutchCone.FCStd)
contains **1,652 physical occurrences**. This checkpoint adds nine reusable part
definitions and 71 occurrences, including the cone, lining, 49 rivets and six
spring-plunger sets. It refines one existing support and preserves the other
1,580 parent occurrences. These local counts are not additive to the standard
tank inventory; integration has not occurred.

All 462 independent checks, 326 affected interference pairs, ten definition and
72 installed STEP comparisons pass, together with two coupled parameter trials
and a fresh rebuild. Seven actual native/source images were reviewed; four new
progression snapshots are saved. The [packet](packets/I03-clutch-cone.md) records
conditional handbook dimensions, source conflicts and inferred profiles/finishing.
Independent through-hole checks rejected two Boolean defects that whole-part
interference and exchange checks alone had missed.

Next are the SH861K plunger locking wire and receiving holes, outer drum,
flywheel/crankshaft engagement, clutch-stop brake, and remaining drivetrain and
engine systems. Standard tank 011 and its transparent-hull view are unchanged.
The full-tank goal remains active and incomplete.

## 21 September 2026 — clutch-stop coupling and closed pump drive

The [combined native assembly](experiments/drive_chains/clutch_drive_build/TransmissionWithClutchDrive.FCStd)
now contains **1,520 physical components**. Thirty additions represent M855,
two M856 cover halves, M858, the SNL cardan shaft, eight bolt/nut/washer sets and
SH900G as a linked-belt assembly representation. The previous inferred six-hole
M246 flange now has the documented eight-bolt pattern. The closed belt raises
the pump and its dependent mounting stack by 0.797 mm. Another 1,406 parent
components remain unchanged.

All 474 affected material pairs, 148 independent interface checks, 22 detailed
STEP definition comparisons and 114 placed-solid exchange checks pass. Two
coupled radius/profile and shaft-size trials pass 450/474 pairs and 27 contacts
each. The [qualification](experiments/drive_chains/clutch_drive_build/qualification.json)
binds the checked native, exchange files, tooling and six inspected views.
It accepts the approximate installation for continued front-clutch construction.

[Source comparison](experiments/drive_chains/clutch_drive_build/source_review/index.html)
showed the first shaft head was too narrow; its section increased from 76 to
100 mm between the coarse HB/SNL proportions. The transverse form, cup profile,
sharp shoulder approximations and handbook-to-SNL shaft dimension transfer remain
explicit limitations. The belt's 108 scores do not establish a historical link
count; proprietary link inventory and the pitch-length convention remain open.

Three new [assembled](../intermediate_snapshot_iso_clutch_drive_001.png),
[exposed coupling](../intermediate_snapshot_iso_clutch_coupling_001.png) and
[section](../intermediate_snapshot_detail_clutch_drive_001.png) snapshots are saved.
All 20 standard native files and 66 prior progression PNGs are preserved.
Standard tank011 remains unchanged. Next are the front clutch coupling and
external spring, main compound clutch, brake band and pump air connections,
followed by remaining drivetrain supports, controls and standard integration.
The [packet](packets/I03-clutch-stop-drive.md) records the complete scope.

## 21 September 2026 — pump mounting reconstruction

The [combined native model](experiments/drive_chains/air_pump_mount_build/TransmissionWithAirPump.FCStd)
now has **1,490 physical leaves**. It incorporates the 51-piece pump and adds
32 mounting pieces: two handed brackets, two MX98 stud/nut/pin sets, two MX99
stud/three-nut/two-washer sets and four base bolt/nut/washer sets. Pump/base
hardware belongs to FuelPressure; transmission supports belong to Drivetrain.
The M264 cover and M250 housing gain integral blind receivers. The installed
pump feet are widened for bolt-head clearance. The other 1,405 transmission and
50 pump pieces retain their geometry.

All 529 affected material pairs, 93 independent interface/count checks,
16 detailed definition STEP comparisons and 85 placed-solid exchange checks
pass. Two coupled belt-reference scenarios rebuild the support height and stud
lengths; both pass 529 material pairs and 20 contacts. A global face-refinement
operation initially increased tolerance at the existing grease port. Retaining
the valid Boolean face divisions fixes this without relaxing exchange criteria.
The initial bracket/flange clashes and rejected refinement evidence are preserved.

The [qualification](experiments/drive_chains/air_pump_mount_build/qualification.json)
accepts this geometry for further clutch development. It does not establish the
historical support profile or final drive installation. Pump height375.005mm
above the input axis is derived from a54-inch belt and estimated pitch radii.
The new pulley planeX516 clears the input coupling; actual drive alignment remains
conditional. The [handbook comparison](experiments/drive_chains/air_pump_mount_build/source_review/source_comparison.png)
uses an opposite-side native isometric, with no source-image warping or claim
of matched scale. HB15 hides much of the support, so the tall webs and stepped
stud arrangement remain explicit hypotheses.

Three new [mounting](../intermediate_snapshot_iso_air_pump_mount_001.png),
[support](../intermediate_snapshot_iso_air_pump_supports_001.png) and
[section](../intermediate_snapshot_detail_air_pump_mount_001.png) snapshots are saved.
All 20 standard native files and 63 earlier PNGs remain byte unchanged.
Next are the clutch-stop drive, its belt and air connections, followed by standard
integration. The pump packet records this scope; standard tank011 remains current.

## 21 September 2026 — air-pressure pump core and internal mechanism

The [native pump](experiments/drive_chains/air_pressure_pump_build/AirPressurePump.FCStd)
now contains **51 physical pieces in 17 reusable definitions**: hollow base,
four cylinders and pistons, return springs, cam shaft, bushes, rounded triangular
bearing covers, V pulley and catalogue hardware. The [packet](packets/I05-air-pressure-pump.md)
records approximate dimensions and separates twelve pending base-fastener pieces
from the expanded 63-piece catalogue assembly.

All 139 local material pairs, 104 independent physical checks, 17 detailed definition
STEP comparisons, 51 placed STEP mass/centroid checks and two coupled dimension
trials pass. Checks include cam contact, hollow pistons, spring seating, shaft
axial stops, complete cover rims and an open vent path. Visual comparison led to
smaller triangular bearing covers; screw-head clearance and a missing shaft
locating shoulder were corrected. Explicit-accuracy mass integration resolved
default integration discrepancies without enlarging BRep tolerances.

Three preserved snapshots show the [assembled pump](../intermediate_snapshot_iso_air_pressure_pump_001.png),
[internal mechanism](../intermediate_snapshot_iso_air_pressure_pump_internals_001.png)
and [bank section](../intermediate_snapshot_detail_air_pressure_pump_section_001.png).
The fixed source overlay retains differences in foot ledges, cylinder reach,
pulley spacing and casting blends. Pump scale, hidden pressure passages and
historical key dimensions remain approximate or unresolved.

The proposed location above the transmission was raised 5mm after its pulley
intersected the M250 flange. Six candidate pairs against 6,733 current physical
context leaves are now clear. The placement study is separate from a qualified
installation. Next are MX100/MX101 brackets, MX98/MX99 attachments, base fasteners,
the clutch-stop drive pulley/belt and connected air ports/lines. The 1,407-leaf
transmission checkpoint and standard tank011 remain separate and unchanged.

## 21 September 2026 — mount approximation accepted; air-pressure pump prepared

The 1,407-solid MX5 checkpoint is now accepted for continued reconstruction with
its long casting bosses explicitly approximate. The
[disposition](experiments/drive_chains/transmission_case_mount_trial_build/source_profile_disposition.json)
retains the source-profile disagreement, conflicting stud lengths and inherited
frame offsets. Additional photographs expose outer supports and brakes but do
not establish the central boss depth. No CAD bytes or prior checks were changed;
the later qualification binds the existing evidence and this acceptance scope.
Historical fit and standard-tank integration remain unqualified.

The [air-pressure-pump packet](packets/I05-air-pressure-pump.md) separates the
four-cylinder fuel-pressure pump from the mechanical lubricator and B6205
input-bearing support. The inspected catalogue expands its core and base
attachments to 63 physical pieces. Its 54in link V belt, MX100/MX101 brackets,
M264-owned MX98 studs and M250-owned MX99 studs are separately identified.
This is source preparation; no new pump solids or standard-tank milestone are
claimed. The next work is calibrated approximate pump geometry and installation.

## 21 September 2026 — case mounting trial and source-profile discrepancy

The [MX5 mounting trial](experiments/drive_chains/transmission_case_mount_trial_build/MX5CaseMountTrial.FCStd)
contains 1,407 valid solids:16 new stud/nut/pin/washer occurrences, three revised
case/channel parts and 1,388 unchanged leaves. All 183 affected material pairs,
61 interfaces,84 independent witnesses,19 native/STEP comparisons and three
local parameter trials pass. A two-segment analytic bore resolved a small STEP
mass discrepancy in the bevel washers without manually enlarging tolerances.

The [source comparison](experiments/drive_chains/transmission_case_mount_trial_build/source_review/mounting_overlay.png)
shows that the inferred upper mounting boss extends beyond the visible wing.
The source stud lengths conflict, and the inherited frame also differs from the
upper source face. The [packet](packets/I03-case-mount-trial.md) records these
observations and the conditional allocation of four MX13 washers. At this initial
checkpoint it was **an experimental trial requiring a casting-profile disposition**;
the later acceptance is recorded above. Two trial snapshots are
preserved;20 standard CAD files and 58 earlier snapshots remain byte unchanged.

## 21 September 2026 — vertical reversing shaft and attachments

The [candidate](experiments/drive_chains/transmission_vertical_build/TransmissionVerticalCandidate.FCStd)
contains **1,391 valid solids**: 19 new, two revised and 1,370 unchanged. M305 shaft,
M303/M304 levers, two Woodruff keys, two M306 bearings and distinct MX11/MX12
attachment sets populate the rear control mechanism. M263 receives local
mounting lands; M302's provisional end hole becomes the lever's cross-socket.
Printed MX12 length is retained. No. C key size and blind-bearing construction
remain documented estimates.

All 148 affected material pairs, 21 native/STEP comparisons, 116 independent checks
and three local parameter trials pass. Sixty-three interfaces are freshly checked
and 641 retained against unchanged geometry. Qualification resolved nut/cotter
clearance, a mistaken reused-nut gap expectation and an upper-lever STEP issue;
a single revolved finger profile preserves the analytic form across export.
Seven inspected views include the fixed-scale SNL23 comparison and a bearing/key
section. Three new snapshots preserve the installed rear view and mechanism.
Twenty standard CAD files and 55 previous snapshots are byte unchanged.

The [packet](packets/I03-vertical-controls.md) records source identities,
assumptions and the remaining case-contour discrepancy. Next: four MX5 case
mounting studs, pump/support, brakes, oil circuits and long controls, then
frame/hull integration and remaining tank interiors. Standard tank011 still
contains provisional interior envelopes; no complete tank is claimed.

## 21 September 2026 — reversing fork, rod and detent

The [candidate](experiments/drive_chains/transmission_reversing_build/TransmissionReversingCandidate.FCStd)
contains **1,372 valid solids**: seven new, four revised and 1,361 unchanged.
M301 fork, retained M302 rod and M307–M309 detent populate the reversing
mechanism. The fork exposed an inherited groove obstruction and excessive
ring-dog reach; bounded revisions clear the continuous fork path while retaining
standard forward engagement. Case journal, detent and access receivers are added.

All 168 affected material pairs, 11 native/STEP comparisons, 63 independent checks
and three local parameter trials pass. Fifty interfaces are freshly checked
and 621 reused against unchanged geometry. The spring checks use ground end
faces, actual boundary samples and a 0.0001mm radial envelope allowance; rejected
conservative-bound and tangent-Boolean checks are retained. Native tolerances
are unchanged. Six inspected views led to a wider source-following upper arm.
Three new progression snapshots preserve the open assembly, mechanism and detent.
Twenty standard native files and 52 previous snapshots are byte unchanged.

The [packet](packets/I03-reversing-controls.md) records approximations and evidence.
Next: M303/M304 levers, M305 shaft, two M306 bearings and their distinct MX11/MX12
attachments, then remaining transmission and tank systems. The standard tank
still contains provisional interior envelopes; the full goal remains active.

## 21 September 2026 — central bevel-case joint

The [candidate](experiments/drive_chains/transmission_case_joint_build/TransmissionCaseJointCandidate.FCStd)
now contains **1,365 valid solids**: 44 new occurrences, two revised castings
and 1,319 unchanged parts. Fourteen MX8 bolt/nut/cotter sets and two M326 gaskets
populate the case split. Source counts are explicit; flange lands, bolt pattern,
gasket stock and fits remain documented estimates.

All 335 affected material pairs, 46 native/STEP comparisons and 200 independent
checks pass. Fifty-nine interfaces are freshly checked and 602 reused against
unchanged geometry. Three local parameter trials also pass. Qualification
resolved gasket/seat and cotter-eye interference, inconsistent overlapping
cutters, and a default mass-integration discrepancy; rejected evidence is kept.
Gasket backing is checked at 2,072 points per half against each casting, with
a displaced-cover negative. This sampled result is not a sealing qualification.

Six inspected views retain the SNL23 scale, showing the inferred joint and the
remaining casting/fastener-position differences. Three new progression images
preserve the overview, exposed joint and section. Twenty standard native files
and forty-nine earlier snapshots are unchanged. The
[packet](packets/I03-case-joint.md) records the evidence and numerical limits.
Reversing controls, case mounts, pump/support installation, brakes, lubrication
and standard integration remain ahead; the full-tank goal remains active.

## 21 September 2026 — paired brake-bearing supports

The [candidate](experiments/drive_chains/transmission_brake_bearing_build/TransmissionBrakeBearingCandidate.FCStd)
now contains **1,321 valid solids**: eighteen new occurrences, three revised and
1,300 unchanged. Two M265 bushes and M266 caps, two reused M300 dowels and four
MX14 stud/nut/cotter sets populate the joint. M263 gains connected rear saddles;
the M269 hub exteriors gain a common journal radius while retaining their
printed drum OD, splines and retaining-ring pockets. The shared-bush arrangement
and unshown casting shapes remain explicit hypotheses.

All153 affected pairs and21 raw/bounded STEP comparisons pass with zero material
difference. Thirty interfaces are freshly checked and584 retained against
unchanged geometry.109 independent checks and four local parameter trials pass.
A corrected annular installation witness replaces a false solid-bore check;
its failed predecessor is preserved. Both conflicting printed MX14 lengths fit
the inferred joint, so the source conflict remains unresolved.

Seven inspected views compare the actual saved section with SNL22. Three new
progression snapshots preserve the overview, focused section and fastener.
The [packet](packets/I03-brake-bearings.md) records the evidence and limitations.
Twenty standard native files and forty-six earlier snapshots are unchanged.
The full-tank goal remains active; pump/support installation, case fastening,
controls, brakes, lubrication and standard integration remain ahead.

## 21 September 2026 — input cover joint, grease feed and cotter repairs

The [qualified candidate](experiments/drive_chains/transmission_input_installation_build/TransmissionInputInstallationCandidate.FCStd)
contains **1,303 valid solids**: sixteen new occurrences, thirty-six revised,
and 1,251 retained unchanged. Four MX25 stud/nut/cotter sets attach the housing
through sixteen drilled shim leaves. A hollow grease cup, 45-degree elbow and
source-length nipple feed a bored housing/spacer passage.

Independent constituent checks found missing cotter legs that earlier solid
validity and STEP checks had not detected. Analytic eye/leg construction fixes
the four new pins and two prior definitions, affecting sixteen bearing-cap
pins and the input-shaft pin. The latter remains unspread. The workflow now
requires checks that constituent material survives Boolean unions.

All 653 affected material pairs, 52 raw/bounded STEP comparisons and 344
independent checks pass. Twenty-one interfaces are rechecked; 573 prior
results are retained against unchanged, hash-bound geometry. Four local feed
parameter trials also pass. A 1e-10 mm tolerance-reporting roundoff allowance
is documented separately from shape tolerances; the rejected receipt remains
preserved. All raw STEP material differences are zero.

Seven inspected views include SNL23's unchanged scale and explicit pin-repair
close-ups. The [packet](packets/I03-input-installation.md) records source count
and nut-size conflicts, inferred fitting placement, passage geometry and
rejected trials. Three new [progression images](../VISUAL_PROGRESSION.md)
show the cutaway, grease passage and fastener. Standard tank011, its twenty
native files and forty-three older snapshots remain unchanged. Pump/support
installation, brake bearings, case joints, controls and integration remain
open; this is progress toward the full tank, not a completed transmission.

## 21 September 2026 — input bearings, housing and coupling

The [new candidate](experiments/drive_chains/transmission_input_build/TransmissionInputCandidate.FCStd)
contains **1,287 valid single-solid occurrences**: 88 new input-assembly leaves,
two revised shaft/cover occurrences and 1,197 retained unchanged. Seventeen
definitions supply two opposed, internally decomposed Timken bearings, housing,
coupling, packing, gland, spacer, two shim packs and retaining/gland hardware.
All 749 affected material pairs, 578 interfaces and 90 native/STEP material
comparisons pass, without stored-tolerance inflation.
The independent checker passes 181 checks, including exact bearing envelopes,
cup insertion, cone passage over the shaft, preserved pinion flank geometry
and deliberate obstructed-entry/displaced-export failures.

Six inspected images include actual native sections over SNL Plates22 and23.
Printed bearing envelopes constrain the reconstruction; race/cage details,
fits and cast forms remain assumptions. Plate22's coupling is a detached
detail, correcting the earlier inference that the shaft extended too far.
M249 quantity and MX25 fastening conflicts remain explicit. The
[packet](packets/I03-input-assembly.md) records rejected cage/rib and
washer/spline interference, installation passages and the remaining work.
Standard tank011 and its opaque/transparent images remain unchanged; the
transmission candidate still awaits integration.
Three new [progression images](../VISUAL_PROGRESSION.md) preserve the input
assembly and bearing cutaways.

## 21 September 2026 — bevel drive and thrust bearings

The [new candidate](experiments/drive_chains/transmission_bevel_gear_build/TransmissionBevelGearCandidate.FCStd)
contains **1,199 valid single-solid occurrences**. Seventy new leaves populate
both bevel wheels and clutch rings, the central shifter and input pinion,
24 rivets, two shims and two decomposed thrust bearings. Thirteen earlier
support/shaft/case occurrences change; 1,116 are retained unchanged.

All 458 affected material pairs, 497 interfaces and 83 native/STEP
material comparisons pass. The 109 independent checks include actual tooth
counts, 26 sampled bevel-mesh positions, forward clutch engagement, printed
bearing envelopes, shaft passages, rivet-head capture and displaced STEP
negatives. Rejected missing-head rivets and a cage exchange-precision issue
are preserved with their corrections in the [packet](packets/I03-bevel-drive.md).

Seven inspected views compare the native bevel drive with SNL Plate22.
Printed 105 × 155 × 40 mm bearings constrain the revised support stack, reducing
the old 31.387 mm sleeve gap to 0.2 mm. The 32.113 mm source-registration conflict
remains explicit; tooth pressure angle, bearing internals, fits and many
profiles remain approximations. New cutaway snapshots preserve the visual
increment. Standard tank 011 and its opaque/transparent views remain unchanged.
Next populate the input bearings/housing/coupling, then remaining brake
bearings, fastening, controls, lubrication, mounting and standard integration.

## 20 September 2026 — bevel sleeve supports and shaft passages

The [new candidate](experiments/drive_chains/transmission_bevel_sleeve_build/TransmissionBevelSleeveCandidate.FCStd)
adds twelve sleeve, bush, oil-retainer, screw and dowel occurrences. Seven
existing shaft/case/cover/sun/bush occurrences are revised; 1,110 are unchanged.
The saved fixture contains **1,129 valid solids**. All 117 material pairs,
326 interfaces and nineteen native/STEP material comparisons pass.

Assembly checks exposed a defect that static clearance missed: the original
root-diameter bushes could not pass the shaft splines. Enlarged bevel and
small-sun journals, mating bores and a larger central clutch spline provide
shaft-only assembly passages. The independent checker passes 83 checks,
including continuous bush/gauge sweeps, actual native sections, local retention
and deliberate undersized-bore/displaced-export failures. Diameters and the
stepped-shaft interpretation remain assumptions.

Six inspected images include a [comparison with both axial registrations](experiments/drive_chains/transmission_bevel_sleeve_build/source_review/bevel_support_comparison.png).
The 32.113 mm datum conflict and 31.387 mm sleeve-end gap remain unresolved;
no complete axial stack is claimed. The [packet](packets/I03-bevel-sleeve-supports.md)
records source counts, rejected geometry and remaining bevel/input work.
New cutaways preserve this interior increment. Standard tank 011, both hull
views and all earlier snapshots remain intact. Brake cap/bush attachment,
bevel gears/clutch/shims, fastening, controls, lubrication and integration remain open.

## 20 September 2026 — small-sun retaining rings

The [new candidate](experiments/drive_chains/transmission_sun_retention_build/TransmissionSunRetentionCandidate.FCStd)
adds both M290 small-sun rings and revises the mating sun sleeves and brake
drums. It contains **1,117 valid solids**, with 1,111 previous occurrences
unchanged. Six M290 occurrences now reuse one definition, matching SNL165's
four shaft rings plus two pinion rings.

Complete groove collars, smooth shoulders and drum counterbores provide nominal
static retention. All 30 affected material pairs, 300 specified interfaces,
12 capture trials and six native/STEP comparisons pass. Independent checks
cover capture direction, actual native radii, source stations, definition reuse
and deliberately displaced exports. Four final views were inspected; the ring
split was moved out of the source section, with its angle recorded as assumed.

The [source comparison](experiments/drive_chains/transmission_sun_retention_build/source_review/sun_retention_comparison.png)
retains the existing calibration and exposes remaining hub/profile differences.
M265/M266 cap and bush ownership is still unresolved; this stage does not claim
to complete that bearing. The [packet](packets/I03-sun-retention.md) records the
limits and next work. Standard tank 011 and all earlier snapshots remain intact.

## 20 September 2026 — small planet supports and swept input disks

The [new transmission candidate](experiments/drive_chains/transmission_small_support_build/TransmissionSmallSupportCandidate.FCStd)
adds 56 small-planet support occurrences and revises 38 case, disk, ring and
rivet occurrences. It contains **1,115 valid solids**, with 1,021 earlier
occurrences unchanged. The pins, bushes, support rings, plugs and retaining
hardware are separate linked parts. The existing expansion-plug definition is
reused. The disk now has a cubic spline transition to its rim.

All 416 material pairs are clear; 296 interfaces, six gear meshes, ten tooth
counts and 94 native/STEP comparisons pass. Independent checks confirm 48 local
retention outcomes, 24 dimensions, six shared definitions, eight displaced STEP
failures, and the native spline/source stations. A bounded comparison handles
one cotter's coincident-face Boolean issue without changing stored tolerances.

The [source overlay](experiments/drive_chains/transmission_small_support_build/source_review/small_train_comparison.png)
shows the rivets at the source-derived axial station, correcting the earlier
15.022 mm discrepancy. The actual rivet clears the case by about 0.570 mm;
the previous concern about a necessary collision was too conservative. A flat
land beneath each head resolves the first swept-disk trial's small overlaps.
The planet-center discrepancy and source/profile uncertainties remain explicit
in the [work packet](packets/I03-small-planet-supports.md).

Seven views were inspected. New [combined cutaway](../intermediate_snapshot_iso_transmission_small_supports_001.png)
and [pin-section](../intermediate_snapshot_detail_transmission_small_pins_001.png)
snapshots preserve the improvement. Standard tank 011 and its transparent/opaque
views remain unchanged. Next are the sun/brake-bearing stack, retention and cap
dowels, followed by central bevel/input, remaining fastening, brakes, lubrication
and integration.

## 20 September 2026 — small planetary gears and riveted input disks

The [small-train candidate](experiments/drive_chains/transmission_small_build/TransmissionSmallCandidate.FCStd)
adds 46 occurrences: both small sun/planet/ring sets, sun sleeve bushes, input
disks and 32 separate rivets. The native fixture contains **1,059 valid solids**,
with one cross shaft revised to provide smooth sun-bush journals and 1,012
previous occurrences unchanged. All 166 material pairs are clear; 182 specified
interfaces, ten native tooth counts, six gear meshes and 47 STEP material
comparisons pass. Thirty independent local trials, eight native dimension checks
and seven intentional STEP-displacement checks also pass.

HB126's 30/78 teeth imply 24 small-planet teeth and reproduce the stated high
reduction. Its contradictory M276 disk tooth row remains documented. The first
trial exposed rivet-head collisions; explicit forward head recesses resolve
those without changing the printed rivet size. Cast lap, head form and fits
remain inferred.

Eight inspected images include the [original/native comparison](experiments/drive_chains/transmission_small_build/source_review/small_train_comparison.png).
It retains a 7.257 mm planet-center discrepancy and a 15.022 mm axial rivet-center
discrepancy. The source disk's swept outer transition is not yet represented by
the current flat-web approximation. The [work packet](packets/I03-small-planetary-gears.md)
keeps that refinement and the small pin/bush/ring support stacks open.

Preserved [combined cutaway](../intermediate_snapshot_iso_transmission_small_001.png)
and [small-gear oblique](../intermediate_snapshot_detail_transmission_small_001.png)
record this interior improvement. Standard tank milestone 011 and its opaque and
transparent views remain unchanged. Brake bearings, retention, central bevel/input,
case fastening, controls, mounting/lubrication and integration remain unfinished.

## 20 September 2026 — corrected ring-bolt source identity and seats

Tracing the original callout15 leader in SNL Plate22 and HB Plate73 corrected
the previous comparison: M318 is the inner bolt near source y355; the outer
bolt near y200 belongs to the case joint. The claimed 59.257 mm outward error
and proposed carrier-rim enlargement are withdrawn. The upper inner feature
is a ring bolt, so the earlier interpretation of two opposed planet pins is
also corrected. The old images and receipts remain preserved.

The [revised candidate](experiments/drive_chains/transmission_ring_support_build/TransmissionRingSupportCandidate.FCStd)
retains 1,013 valid solids, with 22 occurrences revised and 991 unchanged. The
M318 circle follows the conditional 148.771 mm source radius. Shorter bolts
seat in projecting ring bosses with open head counterbores; their nuts occupy
recessed carrier seats. Casting contours and access dimensions remain inferred.

All 166 material candidate pairs are clear, 108 retained interface checks pass,
and 22 changed solids preserve material through STEP. Fifty local access/stop
trials, six radius/diameter checks and five deliberately shifted STEP checks
pass. Seven images were inspected, including the
[corrected source comparison](experiments/drive_chains/transmission_ring_support_build/source_review/source_pin_comparison.png).
The [work packet](packets/I03-ring-bolt-station.md) records the correction and
remaining limits. Next populate the small planetary train and central bevel/input
assemblies. Case fastening, brakes, controls, mounting, lubrication and standard
tank integration remain incomplete.

## 20 September 2026 — large planet pins and recessed carrier seats

The subsequent ring-bolt revision above supersedes this checkpoint's M318
source comparison and geometry; its earlier artifacts remain preserved.

The [pin-support candidate](experiments/drive_chains/transmission_pin_build/TransmissionPinCandidate.FCStd)
adds 56 physical occurrences from ten source identities: bronze bushes, steel
sleeves, hollow pins, expansion plugs, pin rings, nuts, bolts and split pins.
It contains **1,013 valid solid components**, with two revised carriers and
955 earlier occurrences unchanged. All 332 material candidate pairs are clear;
108 specified contact/gap checks and 58 STEP material comparisons pass.

Source inspection corrected the preliminary M313 nut and half-inch plug
transcriptions. The large-bronze-bush model uses M282 from SNL43/HB122 while
retaining the conflicting SNL251/252 marks. Recessed nut seats now follow the
Plate22 axial pick. Their casting pockets and bearing shoulders remain inferred.

Fifty local retention trials, six pin/gear axis checks, four printed-size checks
and eleven deliberate export-displacement trials pass. STEP comparisons retain
small volume/center discrepancies while verifying that neither added nor missing
material exists and import has not enlarged numerical tolerances. These checks
establish the modeled static interfaces, not historical running fits.

The [pin-axis section](experiments/drive_chains/transmission_pin_build/source_review/pin_axis_section.png)
and [source comparison](experiments/drive_chains/transmission_pin_build/source_review/source_pin_comparison.png)
show the separate bearing stack and recessed retention. The approximately
11.5 mm planet-center discrepancy remains. The originally reported ring-bolt
discrepancy used the wrong source feature and is corrected above. The
[support packet](packets/I03-large-planet-supports.md) records those limits.

Standard milestone 011 remains unchanged. The carrier/ring and bolt-station
review is recorded in the subsequent revision above. The small planetary train,
bevel/input assemblies, brakes, controls, mounting and lubrication remain open.

## 20 September 2026 — large planetary gears and retention

The [large planetary candidate](experiments/drive_chains/transmission_planet_build/TransmissionPlanetCandidate.FCStd)
adds eighteen sun, planet, ring, gasket, washer and retaining-ring occurrences.
The native fixture now contains **957 valid solid components**, with five earlier
case/shaft occurrences revised and 934 unchanged. All 110 material candidate
pairs are clear; 24 specified interface checks, ten native tooth counts and six
planet-center/mesh checks pass. The 23 new/changed solids survive STEP roundtrip.

The large train uses HB126's 18/27/72 teeth and 4–5 DP. Cubic B-splines approximate
the involute flanks; pressure angle, root continuations, backlash and fits remain
documented assumptions. The printed ring dimensions require a larger local
M277 case bore and shoulder. New M255 end grooves receive the separate M256
clips; M288 washers fit between the carriers and existing bearing flanges.

Twenty-eight local trials pass their expected outcomes, including deliberately
misclocked planets and shifted retention parts. Seven inspected images include
the [SNL comparison](experiments/drive_chains/transmission_planet_build/source_review/source_detail.png).
The modeled sun differs visibly from the illustrated outline, and the gear face
station differs by 5.129 mm from the selected source picks. These disagreements
remain explicit; the checks establish nominal modeled fit, not historical fits
or full parameter/motion qualification.

Preserved [cutaway](../intermediate_snapshot_iso_transmission_cutaway_001.png) and
[gear-detail](../intermediate_snapshot_detail_transmission_gears_001.png) images
record this interior improvement. Standard milestone 011 and its opaque and
transparent views are unchanged. The [work packet](packets/I03-large-planetary-gears.md)
keeps large-planet pins/bushings, the small planetary train, central bevel drive,
brakes, controls, mounting and integration open.

## 20 September 2026 — central transmission cases and rotors

The [central transmission candidate](experiments/drive_chains/transmission_core_build/TransmissionCoreCandidate.FCStd)
adds eleven occurrences from seven source identities: M263/M264 case and cover,
one M255 cross shaft, and paired M278/M277 planetary case halves, M286 carriers
and M269 high-speed drums. The native fixture now reopens with **939 valid
single-solid leaves**, preserving all 928 earlier occurrence signatures. The
eleven new parts also survive STEP roundtrip with matching volumes and centers.

Thirty-three potentially contacting material pairs have no overlap. Nine
specified gaps/frame contacts pass; five further clearances are recorded as
diagnostics. Twelve local trials cover the inferred case lip and carrier hub,
with deliberate ring, phase and shaft-end failures detected. Both analytic
drum diameters match HB126's printed 381 mm. These checks do not qualify the
unbuilt gears, historical tolerances or a full parameter envelope.

Six actual rasters were inspected, including the
[horizontal source overlay](experiments/drive_chains/transmission_core_build/source_plate22_overlay.png)
and [case end-view overlay](experiments/drive_chains/transmission_core_build/source_review/source_plate23_overlay.png).
The [preserved transmission isometric](../intermediate_snapshot_iso_transmission_candidate_001.png)
records the visible improvement separately from the standard tank milestones.
The case uses explicit cubic B-spline outline poles, an axial extrusion and a
hollow cavity. Broad arrangement follows the sources; mounting-web contours,
cast transitions and gear seats remain partial. A 32 mm input-center discrepancy
and the printed-versus-scaled brake-diameter conflict remain explicit.

The [work packet](packets/I03-transmission-core.md) defines identities, evidence,
reproduction commands and remaining work. Populate carrier washers/retainers,
planetary and bevel gears, input bearings, brakes and controls next. Full frame
attachment, oil feeds and integration remain open; standard milestone 011 and
its opaque/transparent companions are unchanged.

## 20 September 2026 — transmission cap lubrication

The [lubrication candidate](experiments/drive_chains/transmission_oil_build/TransmissionOilCandidate.FCStd)
has 928 valid single-solid leaves. It adds twelve separate elbow/nut/sleeve
fittings and four porous wool envelopes, then drills the four caps and front
linings. The other 904 occurrences retain their geometry. All 104 material
candidate pairs have no overlap, four fitting/passage checks pass, and 24
new/changed solids survive STEP reopening. Existing bearing/hinge gaps and all
sixteen stud seats remain intact.

Original SNL261/262 establishes the feed tubes' ¼-inch outside diameter;
SNL56/274 specifies two ounces of wool per cup. The CAD uses one material
envelope per cup, with no claim to reproduce fibers, density or permeability.
It conforms to the hinge-lug intrusions found during the local fit check.
Each geometric passage connects the fitting inlet through the porous cup region
to the sleeve running interface; undrilled caps, undrilled linings and solid
elbows correctly obstruct it.

Twelve local gallery trials have the expected outcomes: ten nominal/height/bore
cases pass the connection and 1-mm wall checks; two deliberately lowered
drillings miss the reservoir and are rejected. This does not establish the
historical route or qualify the full assembly's uncertain parameter ranges.

The [fitting section](experiments/drive_chains/transmission_oil_build/oil_fitting_section.png),
[bearing section](experiments/drive_chains/transmission_oil_build/bearing_oil_section.png)
and [handbook comparison](experiments/drive_chains/transmission_oil_build/source_review/source_oil_detail.png)
were inspected. Fitting dimensions, inlet placement and gallery route remain
inferred. Rounded casting transitions and the source's upper opening remain
unfinished. Full armored lines, lubricator, sealing and oil-flow performance
are not represented by these local fit checks. Frame mounting and the central
transmission remain ahead of integration; standard milestone 011 is unchanged.

## 20 September 2026 — transmission cap fastening

The [fastened transmission candidate](experiments/drive_chains/transmission_stud_clearance_build/TransmissionStudCandidate.FCStd)
contains 912 valid single-solid leaves. It adds sixteen source-length studs,
sixteen castle nuts and sixteen formed split pins, with revised blind receiving
bosses and nut seats on eight existing castings. The other 856 occurrences
retain their geometry. All sixteen fastening checks and four retained
bearing/hinge checks pass; 262 material candidate pairs have no overlap.
The 56 new/changed solids also survive STEP reopening.

The first trial's two cotter-eye/casing collisions are preserved. Mirroring the
port split pins clears those collisions without changing the source dimensions.
The [handbook comparison](experiments/drive_chains/transmission_stud_clearance_build/source_review/source_fastener_detail.png)
shows the added fastening and the remaining differences in the casting, cup and
lubrication. Threads use smooth envelopes; thread retention and load capacity
are unqualified. Both tested upper/lower allocations of the two inner stud
lengths clear, so historical corner placement remains unresolved.

Original SNL56/67/86/126 now records the next oil-fitting inventory, including an
unresolved sleeve/collet identity. Oil fittings/passages, frame attachment and
the central transmission remain open. This is isolated candidate geometry;
standard milestone 011 and its opaque and transparent views remain unchanged.

## 20 September 2026 — closed oil-cover hinges

The [latest transmission candidate](experiments/drive_chains/transmission_lid_clearance_build/TransmissionLidCandidate.FCStd)
has 864 valid single-solid leaves. Four steel pins use the SNL's printed
3/16-inch diameter and 2½-inch length; integral knuckles are added to the four
caps and covers. The other 852 earlier occurrences retain their geometry.
Thirty new/changed material pairs have no overlap, and four hinge checks pass:
0.15-mm bore clearance, receiving-wall interference under a diagnostic shift,
and preserved cap split/lining seats. Twelve new/changed solids pass STEP reopening.
The first hinge trial's four cup-rim collisions are retained separately.

The [source comparison](experiments/drive_chains/transmission_lid_clearance_build/hinge_review/source_hinge_detail.png)
shows the handbook's rear hinge and the closed native cover. Knuckle form and
placement remain inferred; the source's rounded casting, cap nuts, oil fittings
and wool filling are still incomplete. Pin axial retention and lid motion are
unqualified. All standard covers stay closed.

The pin check exposed an understated triangulation-cached bounding box. Printed
diameter now uses the analytic cylinder, and collision filtering removes display
mesh caches. An independent frame recheck with those bounds again finds no
overlap among 126 pairs. Original SNL241/124 also supplies the next cap hardware
set: eight MX9, four MX10, four MX36 studs, sixteen castle nuts and sixteen split
pins. Their printed lengths must constrain the unfinished casting bosses.

## 20 September 2026 — transmission frame and revised support webs

The isolated [frame candidate](experiments/drive_chains/transmission_frame_clearance_build/TransmissionFrameCandidate.FCStd)
now contains 860 valid single-solid leaves: fifteen new channel, diaphragm, angle
and gusset occurrences, plus revised webs on four existing bearing brackets.
The other 841 occurrences retain their earlier geometry. Nineteen new/changed
solids survive STEP reopening. At nominal dimensions, 126 material candidate
pairs have no overlap and all 34 contact/gap checks pass. The first frame trial,
with nineteen overlaps, is retained separately.

The [frame/support view](experiments/drive_chains/transmission_frame_clearance_build/frame_supports.png)
and four other native/source views were inspected. Channels follow conditional
Plate 2 picks; bracket vertical webs and separated mounting pads are inferred.
The Plate 22 comparison explicitly distinguishes a section from a projection.
The outer bracket/casing gap is only 0.236 mm. Nearby assumed profiles collide,
so the sensitivity checks **do not qualify the uncertainty envelope**. The inner
pads still have a 5.806 mm attachment gap; its receiver/packing is unresolved.
SNL lists six main fiber packers, while the handbook lists eight; neither source
establishes that these fill the bracket gap.

Frame fasteners, hull attachment, brake suspension and the central bevel case
remain absent. Bearing cap hardware and lubrication details are next. This is
partial candidate geometry, not a promoted standard milestone; standard 011 and
both of its isometric views remain unchanged.

## 20 September 2026 — fixed transmission bearing trial

The isolated fixture now has 845 valid native solids. Twelve new catalogue
occurrences represent the four bracket/cap pairs and four oil-box lids; eight
additional regions represent poured babbitt, with no invented catalogue mark.
All 825 inherited occurrence signatures remain unchanged. The new twenty solids
survive STEP export/reimport. Four local bearing/lining, split-joint, axial
capture and lid-clearance checks pass.

The full candidate remains **unaccepted**: each outer bracket intersects the
chain-case sheet and one wall-angle rivet. The seventy-pair material check finds
four overlaps. Two earlier lid-seat failures are retained; the latest flat seat
and edge clearance fix those local issues. Six native rasters, including the
[source overlay](experiments/drive_chains/transmission_support_clearance_build/source_support_overlay.png)
and [interference detail](experiments/drive_chains/transmission_support_clearance_build/support_interference.png),
were inspected. The bracket vertical profiles and frame attachment need revision.

Original SNL96/97 and HB/SNL side sections now support the next frame study.
Build the top/bottom channels, angles and gussets to constrain the support/casing
interface; preserve the source-supported aft-facing bracket orientation. Cap
hardware, lubrication details, foot-count conflicts and full integration remain
open. Standard milestone 011 and its opaque/transparent snapshots are unchanged.

## 20 September 2026 — experimental chains, casing shells and fastening

The isolated chain work now includes separate bars, bushes, pins and cotters,
both sprockets, M1590 casing bodies, M1591 caps and M1592 wall attachments.
The wall-joint fixture has 567 physical leaves; its two angles, 22 wall rivets
and 34 casing rivets pass 697 material candidate pairs, 56 receiving bores and
56 seating checks. Existing hull checks also pass.

The cap-joint fixture adds 94 leaves: eight side cleats, four roof cleats,
four packing strips, 36 rivets and fourteen separate bolt/nut/lock-washer sets.
All 661 reopened leaves are valid single solids. Its 914 new/changed material
candidate pairs, 50 receiving bores, 50 seating checks and fourteen simplified
retention checks pass. A rejected roof-rivet pattern with four bolt/nut clashes
is preserved alongside the revised candidate and inspected detail rasters.

Original HB185 subsequently corrected the M1584 packing location: strips now
sit under the body side-cleat feet. The corrected candidate retains all passing
fit checks and adds four packing-contact checks. The trim fixture adds eight
register plates, eight beading strips and 72 rivets, for 749 valid native solids.
Its 1,088 material pairs, 72 bores, 72 seats, eight register laps and 40 flush-head
checks pass. Actual exterior, inner-face and countersunk-rivet section views
have been inspected. The HB/SNL beading identity and quantity conflicts remain
explicit alongside the inferred sections and installation details.

Four M1587/M1588 supports, 28 rivets and eight assumed three-part hull fastening
sets now connect the casings to four drilled inner/outer wing plates. The latest
fixture has 809 valid solids and passes 920 material pairs, 36 bores, 36 seats,
four support contacts, eight retention checks and the existing hull validator.
Native ownership auditing counts 300 casing occurrences, including 42 named
components across all twelve selected SNL casing marks. Bracket profiles and
hull bolt allocation remain inferred; the source quantity conflicts are open.

Earlier failed tooth reliefs, wall interferences and casing-corner clashes are
preserved. The latest inferred wall openings clear the actual casing section
by at least 2.304985 mm. Native half-sections and joint details have been
inspected; a faulty earlier section preview is explicitly rejected and replaced.
The 50-pitch chain interpretation, case stock/contours, cap seam and wall-angle
form remain documented approximations. Catalogue chain quantities and several
casing fastener schedules still conflict.

These parts are **not promoted to the standard model**. Source reconciliation,
transmission interfaces and full-model checks remain before
integration and parameter qualification. See the
[chain/casing packet](packets/R02-drive-chains.md) and
[native support detail](experiments/drive_chains/casing_support_build/casing_support_detail.png).

The latest isolated detail candidate forms all 100 chain cotters and adds 400
inferred oil passages across 200 bar occurrences. It retains 809 valid native
solids and passes 274 new material pairs, 100 cotter capture checks, 100 pin
retention checks, 400 oil paths and 200 orientation checks, with negative
controls. The original lubrication instructions support the features, but hole
dimensions and tail bends remain assumptions. Five actual rasters were inspected,
including clearer bar-aligned sections. Static retention and open passages are
checked; strength, lubrication performance and running engagement are not.

Two M289 transmission output shafts and two M292 brake drums now extend the
isolated fixture to 813 physical leaves. Source identity is distinct from the
central M255 cross shaft. A native section overlay against SNL Plate22 was
inspected; adjoining proportions use the printed four-inch sprocket hub as a
conditional scale. Shaft splines and drum/web sections remain inferred. Four
static spline fits and two hub seats pass. The first installation exposed two
23,938.321999 mm³ drum/casing clashes, preserved with exact inputs and renders.

A revised small-end casing narrows locally to 132 mm while retaining the
168.275 mm maximum width and the rear attachment region. All 764 changed/new
material pairs, eight sheet-thickness witnesses and both chain/drum clearance
checks pass. The taper and its location are explicit assumptions. Bearings,
shaft retaining rings, brake bands, planet-disk connections and full-model
integration remain open; neither candidate changes the delivered standard tank.

The latest output-shaft candidate adds twelve sleeve/dowel/ring parts, for 825
valid native solids. Four inner/outer sleeves, four bronze dowels and four
retaining rings match their selected SNL allocations. Inferred shaft grooves
and dowel pockets remove material only. All 26 changed/new material pairs,
four journal gaps, four dowel capture checks and four bidirectional ring capture
checks pass. An independent reopen confirms that all four existing spline
interfaces retain their original engagement geometry and passing fits.

Three native rasters, including the axial section and fixed source overlay,
were inspected. SNL309's poured-babbitt note is now recorded; the separate shaft
sleeves must not be confused with the future fixed lining. The handbook/SNL
bearing-material descriptions and the two-versus-four support-foot count remain
open. Fixed castings/caps, oil fittings, channels and the complete axial stack
are next. This candidate remains outside the delivered standard tank.

## 20 September 2026 — standard roller-pinion milestone 011

Both 98-part pinion installations are now in the main standard assembly: 252
shared definitions and 5,341 leaves, comprising 5,326 physical components and
15 layout occurrences. Physical geometry represents 216 source identities;
all physical definitions still have partial coverage.

The private origin passed all 29 qualification stages, 17 parameter trials and
37 record/renderer tests. Its original report/checkpoint bindings remain intact.
The exact authored geometry and all 20 native files were transferred to the main
build directory. A fresh FreeCAD check verified all dependencies there, all
252 definitions, 5,341 placements and the original geometry signatures. Only the
build report's top-document path changed; the full trial suite was not repeated
at the new path. The [transfer receipt](releases/011-roller-pinions-transfer.json)
records that distinction. The 754-file source lock also passed.

Preserved [isometric011](../intermediate_snapshot_iso_011.png),
[pinion/wheel detail](../intermediate_snapshot_detail_pinions_011.png) and
[shaft/support detail](../intermediate_snapshot_detail_pinion_mounts_011.png).
All three actual rasters were freshly inspected, and the earlier nine native/source
review artifacts retain their original hashes. The prior 18 progression images
remain unchanged. A new [transparent-hull view](../intermediate_snapshot_iso_transparent_011.png)
uses 18% armor opacity to expose enclosed geometry while retaining opaque running
gear and interior components. Interior layout envelopes remain provisional.
The complete native/STEP/view/report delivery is preserved in
`.work/deliveries/011-roller-pinions.zip`, with a
[versioned release record](releases/011-roller-pinions.json).

The first integrated candidate exposed four fuel-backplate overlaps that were
absent from the isolated fixture. A separate inferred longitudinal control now
moves the continuous backplate and its roof/floor ends aft, retaining its
printed 16 mm thickness. The saved three-plate candidate passes 510 pinion
material candidates, 102 bearing faces, 32 receiving bores and 40 clearances;
both backplate/bearing gaps are 26.0295 mm. HB27 supports the continuous plate
topology, but does not measure its station. The approximation remains explicit.

The 37-tooth alternative has 12 overlaps with the current fixed pinion station
and phase. This rejects that particular geometric combination; it does not
resolve the conflicting historical tooth counts. See the
[integration preflight](experiments/roller_pinions/integrated_preflight/README.md).
The next [chain packet](packets/R02-drive-chains.md) preserves a separate
conflict between the handbook's 50 pitches and the SNL's 25 bushes/pins per chain.
Separate chain and casing fixtures now exist; they have not been promoted to
the standard assembly.

Main mounting-stage validation has completed using durable checkpoints, as
recorded below. Generated records and ongoing experiments live in the project
workspace. Local commits are authorized by the user; the private pinion branch
includes the current qualification runner and source comparison work.

## 20 September 2026 — partial driving shafts and bearing attachments

Added 56 physical shaft, key, nut, plug, bearing and attachment occurrences.
Both source-defined driving-shaft assemblies now contain all seven SNL leaves;
the 23 bearing/attachment leaves per side remain separately owned. Ten new
native definitions reuse the common M1477 nuts, M1409 bushes and Q52C plug.
The standard tank now has 242 definitions and 5,145 leaves: 5,130 physical
solids, thirteen layout solids and two wires, covering 207 physical source
identities. All physical definitions remain partial reconstructions.

The original SNL189 bearing-joint rows, supported by SNL169/178 angle allocations,
correct the earlier inner-panel geometry mapping: M1977 receives the rear drive
bearing, while M1978 belongs forward at the roller pinion. Source identities were
preserved. Twelve rear panels now follow the documented level skirt-border
hypothesis and own the bearing-barrel and attachment bores. Exact historical
seams and casting outlines remain inferred.

Nominal native checks pass 82 bearing/attachment seats, 32 full hull receiving
cylinders, four shaft/bush clearances, shaft/key dimensions, oil-passage witnesses
and rivet-stock volumes. All 604 idler/drive wheel-and-mount occurrences clear
2,042 material candidate pairs. The shared Q52C plug has 12 mm insertion and
an inferred 0.2 mm radial gap; its tiny square-head contact is not treated as a
bolt shoulder. A deliberately shifted plug fails the insertion check. Threads,
sealing, retention strength, exact cast profiles, extra M1552 plate-only rivets,
historical fit and continuous engagement remain unqualified.

Thirty-five record/renderer tests pass. The complete delivered native shapes,
rigid placements, both STEP round trips, relocated links, independent rebuild,
unchanged cache and all fifteen parameter trials pass. The two new trials vary
shaft length and frame spacing; 46 fittings follow shaft-length changes while
independent wheels and hull faces stay fixed. The spacing trial also rechecks
existing hull, roller, idler and lower-support interfaces. Source verification
covers 749 files and the unchanged survey database.

Preserved [isometric010](../intermediate_snapshot_iso_010.png), a
[complete mounting-stage wheel view](../intermediate_snapshot_detail_drive_010.png)
and [shaft/support detail](../intermediate_snapshot_detail_drive_mounts_010.png).
Prior snapshots remain byte-identical. The reviewed source comparisons retain
all profile and interface limitations. Snapshot009 and its preserved wheel detail retain their original hashes.
The former temporary delivery archive was lost in an environment restart;
ongoing work and validation receipts now live in the project directory.

The next running-gear work is the source-counted roller pinions and chain drive,
followed by remaining exterior structure, fittings and identifiable interiors.
The isolated pinion integration has passed a focused installed geometry check
after an explicitly inferred fuel-backplate correction; its full qualification
remains separate from this delivery.
The complete-tank goal remains open, with standard geometry ahead of poses.

## 20 September 2026 — partial driving wheels and common wheel interfaces

Replaced the two drive-wheel envelopes with two 119-part source wheel assemblies
and two bushes per shaft: 242 new physical occurrences. The complete native
assembly now has 232 definitions and 5,089 leaves: 5,074 physical solids,
13 layout solids and two reference wires. Physical definitions remain partial,
covering 197 source identities. See [the drive-wheel packet](packets/R02-drive-wheels.md).

All four idler/drive wheels reuse the same native disks, bosses, diaphragms,
bushes and rivet definitions. Independent shared radii replace the former
idler-derived disk/rivet geometry. The nested lands and flatter diaphragm
troughs follow the inspected HB125 section; exact profiles, X/Y distinctions,
local rivet-head overhang and structural adequacy remain unresolved.

The four M1401 rims preserve the handbook's 39.237-inch OD, 32.75-inch ID and
2-inch width. The ID-to-bore interpretation, tooth reliefs and 3 mm crest rounding
are provisional. The nominal 35-tooth hypothesis follows HB130/HB133, while
HB119's 9:37 statement remains contradictory. A 37-tooth parameter trial passes
the implemented static geometry checks; neither count is historically definitive.

A saved-native placement check caught staggered tooth phases in the first build.
The corrected opposed rims have coincident groove axes in the XZ projection.
Both sides retain about 15.95 mm nearest track-bush clearance. No axis or source
calibration was moved to conceal that gap, and continuous engagement remains false.

Nominal wheel checks pass 1,876 material candidate pairs with zero overlaps,
24 sampled rivets with two bearing heads each, eight rim/disk seats and native
paired-rim alignment. The five remaining shaft-BOM leaves per drive side are
explicitly omitted. Shafts, keys, end nuts, oil plugs, bearings, locking plates,
roller pinions and chain still require integration.

Saved-native validity/placement, both STEP round trips, relocated dependencies,
independent rebuild/cache reuse and all thirteen parameter trials pass. The
new trials change the common disk radius and drive tooth count; the idler-OD
trial confirms that common disks and drive installations stay independent.
Thirty-three record/renderer tests pass. Native generation took
67.78 s; independent/cached rebuilds took
102.36 / 46.75 s.
The source lock verifies 740 files and the unchanged survey.

Preserved [isometric 009](../intermediate_snapshot_iso_009.png) and a
[drive-wheel detail](../intermediate_snapshot_detail_drive_009.png). Earlier
snapshots remain byte-identical. Eight final rasters were inspected, including
the shared idler sections and lower-support bank.

The next-stage [shaft/mount fixture](experiments/drive_mounts/README.md) remains
separate from this delivery. Its isolated and installed contacts pass; the
source-correct receiver reconstruction and mounting builders still require
integration and full delivery qualification. The
standard tank, remaining exterior systems and identifiable interiors remain
in progress; historical-fit and complete-tank verification remain false.

## 20 September 2026 — partial lower support runs and attachments

Integrated all 34 catalogue-counted lower support angles and 76 short attachment
bolts. Eighteen new definitions add 110 physical occurrences beneath separate
inner/outer run containers. The complete native assembly now has 232 definitions
and 4,849 leaves: 4,832 physical solids, 15 layout solids and two reference wires.
All 220 physical definitions remain partial, covering 196 source identities.
See [the lower-support packet](packets/R02-lower-supports.md).

Complete front roller units follow the three inclined pairs of support seats.
The inner No.5 pieces retain their printed 168.275 and 822.325 mm lengths. Cubic
transitions join the inferred level seats on runs 4 and 8. Reflected construction
variants retain their shared source identities; historical interchangeability,
exact curved sections and removable retention remain unresolved.

Receiving-bore checks exposed missing material at the first front bolt in the
old coarse hull trace. Reviewed SNL Plate 2 picks now follow the front lower
skirt border, retaining the old trace and unchanged source calibration. The
middle/rear outline and connecting transition remain approximate. A separately
documented 6 mm nose setback clears four track-rivet heads.

Nominal checks pass 826 material candidates,
424 pin/washer/bolt bearing faces, 34 angle/hull contacts and 76 receiving bores
through the 10 mm modeled skirt. Per-run bolt allocations independently match
SNL31. Native receiving surfaces qualify geometric contact, not threads or
structural capacity. Thirty record/renderer tests pass.

Saved-native validity/placement, both STEP round trips, relocated links,
independent rebuild/cache reuse and all eleven parameter trials pass. Native
generation took 40.87 s; independent/cached rebuilds took
59.92 / 42.20 s.
The source lock verifies 733 files and the unchanged survey.

Preserved [isometric 008](../intermediate_snapshot_iso_008.png) and an
[installed front support detail](../intermediate_snapshot_detail_supports_008.png).
Earlier snapshots remain byte-identical. Drive assemblies, remaining support
retention and hull fittings, and identifiable exterior/interior systems remain
in progress. Complete-tank and historical-fit verification remain false.

Next-stage geometry preparation is recorded in the separate
[drive-wheel study](experiments/drive_rims/README.md). Its shared-part candidate
clears 1,626 material pairs at the four installation axes; source conflicts,
shaft/support completion and integration remain open.

## 20 September 2026 — complete lower-support installation experiment

A separate [native experiment](experiments/lower_supports/README.md) now contains
all 34 catalogue-counted lower support angles and 76 attachment bolts. Its
[source comparison](experiments/lower_supports/comparison.html) includes the
inspected SNL longitudinal section, handbook transverse section, and three
native renders. This experiment preceded the integrated receiving-bore check
above; its original contact checks did not establish a receiving wall for every
bolt. Snapshots 001–007 remain unchanged.

The experiment resolves the previous 2 mm skirt/support gap, rotates the complete
front six roller units per side into their inclined support frames, and tests
an inner No.5 split with M2176 carrying Lower12 and M2175 carrying Lower13–15.
The printed lengths remain 168.275 and 822.325 mm. Runs 4 and 8 use explicit
inferred cubic transitions between horizontal bearing seats. The source
allocation of the final two rear rollers remains uncertain.

After correcting the provisional bolt positions, all 1,502 material candidates
have zero overlap above the declared numerical threshold. The 348 pin/washer
seats, 76 bolt-head seats and all 34 angle/hull interfaces have nonzero native
bearing area. A fresh headless reopen confirms 110 new single solids, all
424 pin/washer/bolt seats, and the four printed inner-support lengths. Tests
displacing a pin and bolt head by 0.2 mm correctly lose their bearing faces.

The source scan distinguishes this short-bolt row from following rows that
explicitly include nuts and washers. Tapped attachment is an inferred working
interpretation. HB144's removable retention plates are still unidentified;
their omission remains explicit. Next integrate accepted support geometry into
the typed model, retain these open historical issues, qualify parameter changes
and the complete delivery, then advance the visual milestone if warranted.

## 20 September 2026 — partial idler shafts and adjustment hardware

Added 64 physical occurrences from eleven new definitions, reusing Q52C plugs.
Both nine-part shaft assemblies now reconcile completely with the source BOM;
four brackets, reinforcement plates, guards, main screws, washers and copper
plugs, sixteen cap screws and ten identified outer-plate rivets complete this
partial installation subset. The idler family has 306 leaves. The complete
native assembly contains 214 definitions and 4,739 leaves: 4,722 physical solids,
15 layout solids and two reference wires. All 202 physical definitions remain
partial, covering 181 source identities. See [the mounting packet](packets/R02-idler-mounts.md).

The HB87 section interpretation now nests the disks on inboard rim lands and
uses a flatter diaphragm trough. Fixed bracket frames follow the independently
picked 13.282573-degree screw axis. The wheel/shaft moves 4.068608 mm rearward
along it (X −3.959768, Z −0.934778 mm), preserving the source datum. The foremost
roller retains its explicit 45 mm rearward correction and 8.838 mm excess beyond
the initial pick allowance. Four native rim/bushing gaps are 0.5 mm; the four
foremost-roller gaps are 1.201933 mm. No historical travel or continuous
engagement is claimed.

Nominal checks pass 888 internal and 200 external candidate material pairs with
zero overlap, 64 new mounting bearing faces, four curved copper/screw contacts,
0.04445 mm bush/shaft running gaps, and the existing wheel rivet seats/stock
checks. Deliberate 0.2 mm nut and copper displacements are rejected. Twenty-six
record/renderer tests pass. Native generation took 46.99 s.
Full saved-native validity/placement, both STEP round trips, relocated external
links, independent rebuild/cache reuse and all ten parameter trials pass,
including the new +2 mm shaft-length trial. Independent/cached native rebuilds
took 49.55 / 38.70 s.

Eight inspected rasters are hash-recorded. Preserved [isometric 007](../intermediate_snapshot_iso_007.png),
a [complete idler close-up](../intermediate_snapshot_detail_idler_007.png) and
[adjustment hardware detail](../intermediate_snapshot_detail_adjuster_007.png).
Snapshots 001–006 and their earlier detail remain unchanged. The source lock
verifies 729 files and the unchanged survey. Exact cast/guard profiles,
inner plate retention, threads, lower supports, drive assemblies and remaining
exterior/interior systems stay open. Complete-tank and historical-fit verification
remain false.

## 20 September 2026 — partial front idler wheels

Added 242 partial physical components from nine native definitions: each front
idler has two rims, two disks, one boss, five X and one Y diaphragm, 108 rivets
and two bushes. The two layout annuli are removed. Native geometry now has
203 definitions and 4,675 leaves: 4,658 physical solids, 15 layout solids and
two reference wires. All 191 physical definitions remain partial, covering
170 source identities. See [the idler-wheel packet](packets/R02-idler-wheels.md).

The nominal full build passes its implemented checks; native generation took
37.90 s with existing valid library caches available. Idler validation checks
716 internal and 162 external candidate material pairs with zero overlap,
four 0.5 mm rim/bushing gaps and four 1.686894 mm foremost-roller gaps.
Twenty-five record/renderer tests pass. Printed dimensions, source counts,
rivet stock volumes and 24 representative head-bearing faces pass. The shaft
assembly explicitly accounts for seven missing leaves per wheel and is marked
incomplete; shared whole-vehicle totals are not claimed fully populated.

The narrow-rim/bushing contact interpretation remains provisional. Idlers move
3.862354 mm rearward at fixed source Z. The foremost lower roller moves 45 mm
rearward, 8.838 mm beyond its initial horizontal pick allowance; its independent
source point stays unchanged. Native source-comparison views were inspected.
The diaphragm's rounded waist differs from the drawing's flatter trough; shape
refinement and X/Y distinction remain open. Shafts, tensioners, guards, lower
supports, drive assemblies and other tank systems remain unfinished.

Full saved-native qualification passes: 203 valid definitions and 4,675 rigid
placements, both STEP round trips, relocated dependencies, independent rebuild,
cache reuse and all nine parameter trials including idler diameter. Independent
and cached native rebuilds took 53.01 / 42.09 s.
Preserved the inspected standard isometric as [snapshot 006](../intermediate_snapshot_iso_006.png)
and a [wheel close-up](../intermediate_snapshot_detail_idler_006.png); 001–005 remain unchanged.
The final audit confirms 20 native hashes, 127 delivery hashes, six reviewed
rasters, unchanged snapshots 001–005 and exact copies for both new images.
The source lock verifies 727 files and the unchanged survey. Whole-tank and
historical-fit verification remain false.

## 20 September 2026 — upper support interface

Added four partial M2092 upper roller support angles, from the HB221 whole-tank
quantity. Original scan MarkVIII111 confirms the identity/count and joins the
source lock. HB141 and the transverse sections prompted correction of the shared
pin-end flats to face upward beneath the angle toe, and a taller clamp/flange
seat. All inferred stock, dimensions and drilling remain explicit. See
[the upper-support packet](packets/R02-upper-supports.md).

The current native build has 195 definitions and 4,435 leaves: 4,416 physical
solids, 17 layout solids and two reference wires. All 182 physical definitions
remain partial, covering 161 source identities. Native generation took 43.15 s.
Nominal roller fit passes 230 internal and 620 external candidate pairs with
zero overlap. Four toe/pin seats and eight washer/flange seats have zero gap,
with respective native contact areas about 328.818 and 365.772 mm². A deliberately
displaced pin is rejected by the contact measurement. The two outer supports
meet shell side plates; the two inner supports sit 1 mm from the provisional
roof-relief edge and still require attachment construction. No load-path or
structural qualification is claimed.

The raised clamp initially intersected the rear roof. A local parameter-driven
access relief now clears the upper angles and their clamps. Its boundary and
SH294A covers remain unresolved. Twenty-two record/renderer tests pass. Full
saved-native, both STEP round trips, relocated links, independent rebuild/cache
and all eight parameter trials pass. Independent/cached native rebuilds took
51.24 / 40.50 s. The final audit confirms 20 native and 117 delivery hashes,
724 locked sources, six reviewed raster hashes and unchanged snapshots 001–005.
The survey hash remains unchanged. Full-tank and historical-fit verification
remain false.

Snapshots 001–005 remain preserved. This is primarily a local interface
correction; the next numbered isometric is reserved for a significant visual
population stage. The comparison bundle adds an upper transverse section.
[Idler preparation](packets/R02-idler-research.md) records shared wheel counts,
printed controls and alternative native rail/bushing contact probes. A narrow
rim at the channel center can clear the bars and approach a bushing with a
3.862 mm rearward shift; a rail-contact arrangement instead needs 29.380 mm.
These remain alternatives for source review; no idler geometry or placement
has yet been changed.

## 20 September 2026 — lower and upper roller stacks

Added 1,224 physical components from 13 native definitions at 60 stations:
30 plain lower, 28 spring lower and two distinct upper stacks. The upper shared
parts retain their handbook quantity scope separately from the 58 SNL lower
stations. Upper M1410 and lower Q52C plugs remain separate source identities.
The standard assembly now has 194 definitions and 4,431 leaves: 4,412 physical
solids, 17 layout solids and two reference wires. All 181 physical definitions
remain partial, covering 160 source identities. See [R02](packets/R02.md).

Native geometry includes curved revolved roller profiles, grooved hollow tubes,
bushes, oil-drilled/flatted pins, stock-length split rings, dished plates,
three-coil springs and separate staples/nuts/washers/plugs. The spring's printed
outside-diameter conflict is retained; the working inside-diameter interpretation
is explicit. The plate contour, curves, fits and fastener details remain
approximate. Long supports, upper covers, drive/idler and adjustment assemblies
remain unfinished.

The upper station was corrected to the rear roof bend after HB144's engine-room
access description was checked against SNL2. Its source pick is (1025,248), with
±12 pixel uncertainty. The earlier forward trial and associated roof slots were
removed. All source station X positions remain fixed; installed Z follows the
native track rail envelope, with offsets from −49.976 to +62.501 mm. The upper
offset is −31.957 mm. Eight lower station offsets exceed the stated ±6-pixel
vertical pick allowance (±35.570 mm); this remains a historical placement issue.
Source calibration was not refitted.

Nominal integrated checks pass 214 internal and 616 external candidate material
pairs with zero overlap, against all 3,188 other physical components. Six
representative stack/hand combinations are checked directly and 54 repetitions
are proved equivalent by native definitions and relative placements. All 120
rollers have a 0.5 mm minimum gap to the actual native track rails, within
numerical tolerance. This static clearance does not establish loaded contact,
continuous rolling or the missing support interfaces. Twenty-one record/renderer
tests pass. Contact and dimension checks use OCC bounds without display
triangulation, after display-mesh bounds were found to underestimate curved parts.

The corrected full build passes its geometry checks; native generation took
48.41 s. Preserved the inspected standard isometric as
[snapshot 005](../intermediate_snapshot_iso_005.png), with 001–004 unchanged.
Saved-native validity/placements, both STEP round trips, relocated dependencies,
independent rebuild, cache reuse and all seven parameter trials now pass. The
trials cover track pitch, upper width, hull spacing, sponson roof thickness,
roller diameter, louver thickness and fuel spacing. Clean/cached native rebuilds
took 45.92 / 44.33 s, excluding the other qualification work.
An initial +0.5 mm pitch trial exposed a small upper staple-leg/roof overlap.
The local rear-roof clearance feature corrected it; the saved pitch variant now
passes 214 internal and 616 external roller candidate pairs with zero overlap.
All nominal volume/bounds signatures and reviewed raster hashes are unchanged.
Authored fingerprints, 20 native-file hashes and 115 delivery-file hashes match.
The source lock verifies 723 files, with the frozen survey unchanged.
The source-comparison bundle now includes lower/upper oblique stacks, a spring
stack section, both roller banks and installed rail views alongside HB88/89 and
SNL29. The simplified spring plate's tapered web and flat outer flange visibly
differ from the more continuously formed source contour and remain documented.
Poses remain deferred until the standard geometry is fully populated.

## 20 September 2026 — standard roof louvers and guarded frames

Added 82 physical louver components from 19 native definitions and 18 source
identities. These comprise 34 inlet/28 outlet bent blades, separate side/end
frames and guards, retainers, covers and packing plates. The later SNL blade
counts are a provisional configuration choice; conflicting HB34/29 and 39/29
counts remain recorded. All new definitions retain partial coverage. See
[the implementation packet](packets/X01-louvers.md).

The blades have native sketch/pad geometry with true circular bends, 6 mm normal
stock and a provisional 12.7 mm inside radius. Mapping the 63.5 mm outside width
to a sideways chevron's roof-normal height is explicit. SNL4 supports lengthwise
orientation, while section interpretation, pitches, guard assignment and frame
contours remain unresolved. The two roof datums follow H01's 11.504461-degree
slope; projected aperture lengths and true blade lengths remain distinct.
M997's shared distance-piece fit is not established by the unequal derived
pitches, so spacing/support hardware remains unpopulated rather than disguised
as completed geometry.

Nominal integrated checks pass 194 candidate material pairs, including 11
external pairs, with zero overlap. All 3,106 previously modeled physical
components are in contact scope. Source counts, both curved blade sections,
60 empty-passage probes and four guard heights pass. The standalone native
delivery passes STEP round trips, relocated links, independent reopened rebuild,
cache reuse and a +0.5 mm blade-thickness trial. Rebuild/cache times are
1.13 / 0.98 s. Eighteen record/renderer tests pass. The full native build took
32.83 s. Full saved-native qualification also passes all 181 definitions and
3,207 installed placements, both STEP round trips, relocated dependencies,
independent reopened rebuild, cache reuse and all six parameter trials (track
pitch, upper width, hull spacing, sponson roof, louver thickness and fuel spacing).
The changed-pitch track clears the louvers across 194 candidate pairs as well.
Independent full native rebuild/cache times are 32.38 / 28.04 s, excluding
exports/rendering and other qualification work. Authored fingerprints, all
20 full-build native hashes and 99 delivery-file hashes match. The separate
CoolingVentilation delivery's three native and 43 delivery-file hashes match.

The integrated assembly now has 181 definitions and 3,207 leaves: 3,188 physical
solids, 17 layout solids and two reference wires. All 168 physical definitions
remain partial, covering 147 source identities. Inspected the integrated
isometric/top and separate louver oblique/top/section views against SNL4/7.
Guard heights follow HB41; the remaining rear deflector and attachment hardware
are visibly absent. Preserved the significant roof-detail change as
[snapshot 004](../intermediate_snapshot_iso_004.png), leaving 001–003 intact.
The source lock verifies 717 files, including the five original louver
quantity/dimension scans; the frozen survey hash is unchanged.

Next standard work includes running-gear roller/support population, remaining
hull structure, louver support hardware/rear deflector, sponson fittings and
interior machinery. [Roller preparation](packets/R02-rollers-research.md) records
the lower/upper quantity scopes, inspected transverse sections and a confirmed
printed spring/tube diameter conflict before the next geometry pass.
Full-tank and historical-fit verification remain false;
poses remain deferred.

## 19–20 September 2026 — standard sponson plate shells

Replaced the two sponson layout blocks with 39 individual native plate solids
across 38 SNL identities. Both standard outboard shells now have roofs, separate
inner/sloping floor pieces, wings, side/back plates and top/bottom shield infills.
They are hollow and have the source's distinct handed opening arrangement: seven
peep openings and five ordinary pistol openings. Rotating shields/mounts, hinges,
supports, roof details, furnishings and fittings remain unpopulated.

HB35 armor thickness and HB9 overall width control the plate stock and outward
envelope. Current H01 aperture bounds provide X/Z installation, with an explicit
1 mm clearance. Taper, floor rake, seams and shield infill shapes remain inferred.
M2764 follows the later SNL right-side assignment provisionally against HB227's
port grouping, confirmed by inspection of the original sources. The floor
thickness scope and M2382/M2832 roller-bracket identity conflict remain recorded.
See [the sponson packet](packets/S01-sponsons.md).

The integrated assembly now has 162 definitions and 3,125 leaves: 3,106 physical
solids, 17 layout solids and two reference wires. All 149 physical definitions
remain partial and cover 129 source identities. Nominal sponson source quantities,
97 candidate material pairs, six hollow probes, twelve required/four absent
opening probes and twelve normal-thickness samples pass. All 3,067 other physical
components are included in the integrated contact scope; their bounding boxes
do not intersect the sponson plates at the current installation clearance.

The standalone 39-solid sponson delivery passes native validity/placements, STEP
round trip, relocation, independent reopened rebuild, cache reuse and a +1 mm
roof trial. The roof grows inward, adjoining walls shorten, the crown stays fixed
and the floors remain unchanged. Clean/cached builds took 3.42 / 1.91 s. Seventeen
record/renderer tests pass. Full saved-native qualification also passes: all 162
definitions and 3,125 placements, both STEP round trips, relocated dependencies,
independent reopened rebuild, cache reuse and the track-pitch, upper-width,
hull-spacing, sponson-roof and fuel-spacing trials. The independent full native
rebuild took 31.88 s and the cached build 26.32 s, excluding export/rendering and
other qualification work. Authored fingerprints, 20 full-build native hashes and
89 delivery-file hashes match; the separate Sponsons delivery's three native and
42 delivery-file hashes also match.

Inspected integrated isometric/side views and both sponson exterior views, interior
and underside against SNL7/1 and HB1. The open mount bays expose the remaining
interior layout blocks. Saved the significant visual change as
[snapshot 003](../intermediate_snapshot_iso_003.png), preserving both earlier
snapshots. The source lock verifies 712 files; the frozen survey hash is unchanged.

Next standard work includes roof louvers/guards, sponson fittings/supports,
wheel/roller support, remaining hull structure and complete interior machinery.
[Louver preparation](packets/X01-louvers-research.md) records competing blade and
distance-piece quantities before choosing the repeated component arrangement.
The complete model and historical fit remain unverified; poses stay deferred.

## 19 September 2026 — main hull plate population

Added 77 individual standard hull plate solids across 63 SNL identities,
replacing the central-hull and two track-frame reference solids. The physical
set includes outer side panels, front/rear inner walls, all four inner/outer
skirt runs, eight numbered floor pieces and the fuel floor, roof sections,
sloping front/back closures, split closed side-door leaves and engine side/roof
service leaves. Sponson and louver apertures are open for their actual components.
The plates remain partial, with polygonal source contours and inferred seams.

HB141's 565.15 mm lower shell gap, HB9's 527.05 mm flat-floor clearance and HB11's
engine-room stations control the new shell. The gap is provisionally centered on
the printed track centers. Broad central floors and narrower front/fuel portions
replace the former single narrow envelope. SNL1/7 and HB6 support the topology;
exact transverse transitions and several local roof joints remain unresolved.
HB39/HB43 side-door scope is provisional, with a retained 32.925 mm opening-width
residual. See [H01](packets/H01.md) for the complete source/assumption record.

Initial floor/skirt and front-roof overlaps were corrected by explicit joint
trims. The standalone 103-solid HullStructure assembly (77 hull + 26 upper)
passes source quantities, shape/placement checks, plate contacts, six cavity
probes, lower spacing, floor clearance, louver apertures, native relocation,
STEP round trip, independent rebuild and parameter propagation. A +10 mm shell
gap moves facing plates oppositely by 5 mm, widens the broad floors and narrows
the front floor while preserving the upper enclosures.

The first full integration found 80 contacts between roof pieces and upper-run
track hardware around units 41–44. A bounded smooth upper-route correction now
precedes chord closure: 60 mm peak, X = 4,200 mm, sigma 800 mm. It preserves the
printed count/pitch and fixed image calibration. The delivered native assembly
checks 1,135 candidate hull material pairs, including 868 hull/track pairs,
without material overlap. Track self-contact checks also pass all 1,958 selected
pairs. The +0.5 mm pitch trial remains closed and passes 1,111 hull contact pairs.
The source-construction residual becomes 191.722 mm RMS / 300.847 mm maximum;
static bends become −0.615433° to 28.186605°. Wheel/rail contact and historical
route fit remain open. Sixteen record/renderer tests pass.

Full saved-native qualification passes: 124 valid definitions and all 3,088
installed placements, both STEP round trips, relocated dependencies, independent
reopened rebuild, unchanged cache reuse, track-pitch, upper-width, shell-gap and
fuel-spacing trials. The independent native rebuild took 31.34 s and cached
build 27.03 s; these exclude export/rendering and the other qualification checks.
The standalone HullStructure rebuild/cache times were 6.97 / 4.02 s. Authored
fingerprints, 20 full-build native hashes and 79 delivery-file hashes match;
the separate HullStructure delivery's 52 files also match. The source lock
verifies 709 files and the frozen survey hash is unchanged.

The integrated count is 124 definitions and 3,088 leaves: 3,067 physical
components, 19 layout solids and two reference wires. All 110 physical definitions
remain partial; repeated track components dominate the instance count.
Inspected the isometric, fixed SNL2 overlay, hull oblique, right side and underside
against SNL1/7. The user-saved isometric snapshot 002 already preserves this stage;
the [visual review](VISUAL_REVIEW.md) records the inspected hashes and limitations.

Remaining work includes
curved contours, main beams/angles, bulkheads, roof strips, mud chutes, fittings,
sponsons, running gear support and the full interior equipment scope. All work
continues in the standard configuration; poses remain deferred. The next primary
geometry pass is both sponsons: [source preparation](packets/S01-sponson-research.md)
maps the plate candidates and retains two newly identified source conflicts.
Complete-tank and historical-fit verification remain false.

## 19 September 2026 — standard upper plate shells

Replaced the main enclosure, driver enclosure and lookout layout blocks with 26
individual native plate/closed-leaf solids representing 21 SNL identities. The
integrated standard assembly now has 49 definitions and 3,014 leaves: 2,990
physical component instances, 22 layout solids and two reference wires. The new
plates are partial reconstructions, not finished coverage. The three upper
interiors are hollow; no pose variants were added.

HB35 printed dimensions and armor thicknesses control the shells. The main
base center uses the existing SNL2 trace, while its printed length exceeds that
trace by 370.510 mm and its printed height is 86.538 mm lower. The fixed overlay
retains that disagreement. HB39 clear roof opening and HB43 closed leaf sizes
are kept separately. Undimensioned opening stations, plan chamfers, rake, joints
and roof forming are explicit approximations. The initial handed side-hole
ordering was corrected during HB43 rechecking and is now validated.

All 26 native parts are valid single solids. Independent SNL counts agree;
56 candidate plate contact pairs have no material overlap, three interior
probes are empty, and five armor-thickness samples match. Upper armor and each
track loop have 31.75 mm transverse bounding separation. Fourteen record/renderer
tests pass. The refreshed HullStructure subsystem also passes STEP round trips,
relocation, independent reopened rebuild, cache reuse and a +10 mm main-width
trial: opposed leaves move 5 mm, roof halves widen, and the driver/lookout stay
unchanged. Full integrated qualification passes as well: all 49 native definitions
and 3,014 actual placements, both STEP round trips (22 layout and 2,990 physical
solids), relocated dependencies, clean independent reopened rebuild, cache reuse,
track-pitch, upper-width and fuel-spacing trials. The independent full native
rebuild took 26.27 s and the cached build 23.73 s.
These checks qualify this increment; complete-tank verification remains false.

Inspected the integrated isometric, fixed SNL2 overlay and upper rear view against
HB30 and SNL7; earlier front/underside views show the open interiors. The roof
bend is still faceted, and angles, covers, hinges, rivets and fittings are absent.
The native full build took 26.01 s, excluding the remaining validation/rendering.
The source lock now verifies 708 files; the frozen survey hash is unchanged.

See [S01](packets/S01.md) and [visual review](VISUAL_REVIEW.md). S01 remains active:
upper fittings and detailed sponsons are still required. Next standard-geometry
work also includes the lower hull shell/frames, wheels and roller supports, then
remaining machinery and crew equipment. Complete-tank verification remains false.

## 19 September 2026 — two closed 78-unit tracks

The native hierarchy now contains two complete-count static track loops: 156
shoe/link units and 2,964 physical components from seven reusable definitions.
Together with the installation layout, the assembly has 26 definitions and
2,991 leaves (2,989 solids and two reference wires). The full tank remains
incomplete; repeated track hardware does not conceal the missing unique systems.

Printed count and pin pitch control the route. Every shared pin and both closing
joints agree within 0.000001 mm, and the nominal track self-interference check
passes 1,958 spatially selected exact contact pairs. Reuse of the port result is
conditional on proving the starboard track is its rigid transverse translation.
The actual static bends range from −0.009908° to 28.176469°. Wheel engagement,
roller support contact and continuous track motion remain unqualified.

The source image calibration is unchanged. Closing the rounded/inset construction
requires a 1.0580907513 scale and 57.6927 mm ground translation, both reported
explicitly. Its 188.648 mm RMS pin displacement is relative to the unscaled
construction curve, not a direct source-silhouette error. The SNL idler-axis pick
was corrected from (163,350) to (194,339). HB Plates 83, 86 and 87 were inspected;
the source lock now covers 705 files with the frozen survey hash unchanged.

Whole-vehicle and close views were regenerated and inspected against SNL2 and
HB84. The broad outline is recognizable, while wheel gaps, unfinished hull and
coarse equipment envelopes remain visible. Preview rendering now reuses a
definition's mesh across its occurrences and uses a small compiled depth-buffer
renderer. One full-track isometric took about five seconds in a direct benchmark.
Whole-vehicle views omit small track hardware for legibility; native geometry,
component STEP and close views retain it.

Thirteen record/renderer tests pass. Native placement validation now compares
rigid transforms directly and validates each reusable shape once. This avoids a
measured 0.000036 mm bounding-box variation for Boolean-identical rotated split
pins, while retaining explicit translation/rotation checks on every occurrence.
Full qualification now passes native validity/placements, both STEP round trips
(25 layout and 2,964 component solids), relocated native dependencies, a clean
independent rebuild, unchanged cache reuse, +0.5 mm track-pitch propagation and
+10 mm fuel-spacing propagation. Rebuild and variant checks reopen the saved
native files; the pitch check verifies all 2,991 actual installed placements.
The independent native rebuild took 25.55 s and the cached build 24.40 s. These
timings exclude preview generation, STEP qualification and the rest of validation.

See [R03](packets/R03.md) and the appended
[visual review](VISUAL_REVIEW.md) for construction, inspected artifacts and open
interfaces. R01 and R03 remain active. Next work is wheel/support engagement,
source-qualified hull panels and frames, then the remaining exterior/interior
component families and selected static hatch, sponson and service poses.
[Pose preparation](packets/P02-research.md) now identifies the handed roof-hatch
leaves, upper/lower side-door pieces and removable engine-access plates; pose
angles and clearances remain dependent on their physical hinges and interfaces.


## 19 September 2026 — first physical track components

Added seven native component definitions and six 19-part shoe/link units: 114
physical component instances, in three-unit trial segments on each side. The
whole native assembly now has 26 definitions and 141 leaves (139 solids and two
reference wires). The 19 original layout definitions remain provisional; the
seven new component definitions are partial, with documented forming/forging
assumptions. The full tank objective remains active and incomplete.

The pressed shoe includes a constrained longitudinal section, overlap lip,
rounded plan corners, a closed quartic NURBS center pressing and eight rivet
bores. The source hierarchy contains four handed bars, two bushes, two connecting
pins, two split pins and eight button rivets per shoe. Source composition is read
independently from SNL217/120/143 and checked against the authored templates.

Nominal straight-segment checks found and corrected a 0.4 mm lap-sign error in
adjacent link eyes. The corrected 114 components have no material overlaps in
316 candidate pairs. Sampled joint bends are clear at -5, 0, 10, 20, 30 and 35
degrees. At -10 degrees the overlapping plates contact (about 282 mm³); full
route angles and intermediate bends remain unqualified. A volume-inconsistent
flush-rivet trial was replaced with an explicit two-button approximation. The
provisional foot thickness now follows stock-volume conservation; the historical
underside form remains unverified.

Close native views were inspected against HB Plate84 and SNL Plate26. They
capture the paired channels, head count, overlap and central pressing, while
forged transitions and the pressing contour require further refinement. No
perspective image fit is used. The handbook road-wheel tooth/pitch statements
also conflict and must be resolved for wheel engagement and full track closure.

Template placements retain parameter expressions through nested datums. Physical
component STEP and coverage are separated from the original layout. See
[the R01 packet](packets/R01.md) for source identities, geometric assumptions,
interfaces and remaining acceptance work. Current generated validation reports
record the exact checked input version; earlier reports are invalidated on change.

The final full-build validation passed native solid validity, named placements,
both STEP round trips (25 layout solids and 114 component solids), native
relocation, independent rebuild, unchanged cache reuse, +0.5 mm track-pitch
propagation and +10 mm fuel-spacing propagation. Ten data-invariant tests pass.
The source lock verified 702 files and the unchanged frozen survey hash.
The measured independent native rebuild took 3.35 s and the cached native build
2.16 s; shaded preview generation is substantially slower and is not included in
those native-build timings. The complete-tank acceptance flag remains false.

Next: reconcile the track fastener/pressing interfaces, solve wheel engagement
and the constant-pitch tracks, and replace hull envelopes with identified plate
and frame parts. Complete interior systems, hardware and selected service poses
remain in the unchanged full-tank queue.


## 19 September 2026 — inventory and initial installation layout

The active objective remains the complete FreeCAD tank reconstruction, including
all identifiable components/interiors, documented approximations, selected poses
and visual validation against handbook/SNL figures. This iteration makes concrete
progress toward that result; no complete-tank milestone is claimed.

### Implemented

- Read-only survey access, a searchable 5,482-record production-triage ledger,
  retained quantity/variant/issue assertions, and per-part source dossiers.
- Thirteen explicit initial production decisions: six inclusions and seven
  exclusions. Others remain candidates or unresolved, not automatically accepted.
- Typed parameter arithmetic, source/applicability fields, bounded assumptions,
  named datums, rigid transforms and occurrence/definition identity checks.
- Native component-family libraries, external subsystem documents and a top-level
  linked FreeCAD assembly. The port/starboard running-gear groups exercise nested
  placements, and the sponson/clutch frames exercise nonzero rotations.
- An initial installation model with 19 definitions, 27 layout occurrences,
  25 closed solids and two reference track-path wires. The engine, transmission,
  fuel tanks, cooling, battery, crew/stowage, upper structures and sponsons have
  bounded layout representations. None is counted as a finished component model.
- Source-locked SNL/handbook comparison pages generated from installed native
  geometry. The SNL overlay uses a fixed pixel-to-model transform; the independent
  handbook cutaway is shown without claiming a metric calibration.
- STEP layout export, native relocation, source checks and meaningful data/geometry
  validation. Generated reports distinguish implemented checks from remaining
  tank-completion gates.

### Evidence and visual findings

The SNL longitudinal section and the rotated HB Plate 2 share the broad compartment
and machinery arrangement. Tracing SNL outlines gives useful construction
references, but coincidence with those same traced outlines is not independent
validation.

HB p. 35 supports separate driver-enclosure and lookout dimensions. The pilot's
use of the main-enclosure width for the lookout was a simplification; the new
layout separates these widths. The main-enclosure length/height and curved
transitions still need reconciliation between printed dimensions and figures.

HB pp. 97–98 locate the horizontal radiator aft of the engine on the port side and
describe removing the fan spindle through the hull side. The first centered,
full-width radiator envelope and longitudinal fan axis were inconsistent with
those descriptions. They have been corrected to port placement and a transverse
axis. The fan's exact longitudinal/vertical station remains an unresolved
installation reservation. HB Plates 35–36 and SNL Plate 24 were inspected; those
figures support the arrangement study without supplying an exact mounting frame.

HB pp. 30–32 place three fuel tanks side by side behind the engine compartment.
That arrangement is provisionally transferred to the selected production
50-gallon tanks. The approximate shells do not establish capacity or the correct
gallon convention. No later Zenith carburetor is silently substituted for the
production Ball and Ball unit.

The source overlay deliberately retains the coarse idler rim, approximate upper
profiles and equipment envelopes. It exposes missing detail and uncertain
placement rather than hiding them with image fitting.

The implemented pipeline checks pass, including native/STEP relocation,
independent rebuild, cache reuse and a 10 mm fuel-tank-spacing perturbation.
Eight data-invariant tests pass, and the unchanged foundation regression passes.
Four equipment-envelope intersections remain explicit review issues. See
[VISUAL_REVIEW.md](VISUAL_REVIEW.md); these technical successes do not establish
physical fit or component completeness.

### Remaining workflow gates

| Packet | Current state | Work still required |
|---|---|---|
| F01 | Initial ledger and decisions implemented | Resolve identity/configuration candidates and quantity scopes progressively; settle the selected loadout and retain unknown commercial inventory. |
| F02 | Typed records and named-frame placement implemented | Add explicit mating/fit contracts, representation alternatives and stronger feature-level uncertainty/ownership records. |
| F03 | Modular native build, cache, exports and checks implemented | Qualify representation switching and growing repeated assemblies; keep full physical-fit checks separate from layout checks. |
| E01 | First controlling-source review underway | Continue production equipment, ring/SH642B, wheel/contact and sponson-interface decisions. No archival drawing retrieval is claimed. |
| L01 | Initial longitudinal skeleton and transverse width controls | Refine transverse sections, mounting planes and independent envelope checks. |
| L02 | Major installation layout started | Complete starter/generator, ventilation/duct, exterior equipment, controls and roller-station reservations; resolve critical envelope conflicts. |
| M2–M4 | Not complete | Full plate/frame parts, running gear and track closure, all selected interiors, hardware/routes, static poses and release qualification. |

### Next implementation sequence

Use the working pipeline to finish the missing L01/L02 installation references,
then replace layout masses with source-qualified hull/upper/sponson panels and a
complete representative track/roller family. Inspect the source sections while
building those parts. Resolve track stations and constant-pitch loop closure
before reporting a complete exterior. Continue the complete component inventory
through the internal-system packets; do not substitute the layout for the final
requested model.
