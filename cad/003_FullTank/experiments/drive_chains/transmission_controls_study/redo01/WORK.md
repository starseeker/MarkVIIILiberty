# Remaining Gemini work — reconstruction in progress

User instruction, 26 September 2026: redo the work of `b19e16e5` correctly,
then resume the next step (driver/front controls). Starting accepted checkpoint:
`low_rods_integrated01`, native SHA-256
`9b36e8ca2124d0314825c66b905080f770a3d709a9503eb76a882147cd4e1f04`.
Original commit and `review/gemini-front-controls-20260926` remain untouched.

Sequence and acceptance:

1. M567 washers and M564 return springs: source counts, real seating/capture at
   both ends, continuous wire stock and surrounding material; nominal/variation.
2. M575 long high-speed rods, M563 springs and forward fittings: receiving bores,
   guide fit, spring seats and complete rod routes, including source identity.
3. M641/M640 center foot controls and M578 rear rods: support attachment, lever
   retention and correct M568C hardware, not substituted M568A definitions.
4. M638 shaft/M639 mounts/M640 levers: full mounting fastener grip and receivers,
   shaft/cotter retention and source applications.
5. M579 center foot rods and SH944 clutch links/M581 rear rod: correct joint
   axes, keyways, clamps, bearing seats, thread engagement and no pair exemptions.
6. Remaining forward connections: reconcile M573/M574/M576 applications and
   source lengths before routing; no extra rod segment merely to close a gap.
7. After the redo is qualified, resume driver/front controls from the preserved
   inventory, rebuilding the obstructed bores and floor-crossing layout.

At each accepted stage: reopen native; compare all affected material with retained
context without mating exemptions; preserve unrelated definitions/frames/metadata;
check native/STEP and a meaningful variation; inspect saved views with the fixed
source camera; record a new, uniquely named progression image. No historical
certainty is inferred from fit. Standard assembly promotion and poses stay deferred.

Current investigation: the old spring checks did not establish attachment at both
ends. M567 is source-described as a small brake-gear spring washer (SNL267), not
proven to be a spring anchor. A revised M564 hook hypothesis wraps around the
existing fork socket and is retained behind its jam nut; the other end passes
through the actual M4136 hole. This hypothesis must pass material, seating,
retention and source-view review before acceptance. The inferred end shape,
installed extension and free spring properties remain open.

Further source/connection issues to resolve in later stages:

- SNL193:037 lists five M576 front control rods, explicitly high-speed (2), foot
  brake (2), clutch (1). Do not count extra M576 segments between the rear rods
  and the intermediate shaft, then add five more driver rods.
- Eight M640 intermediate-shaft levers must account for high (2), low (2), foot
  (2), reverse (1), clutch (1), as inferred from the source arrangement. Gemini
  allocated two reverse rockers and no clutch rocker, leaving its clutch route
  ending at a nominal shaft station rather than a receiving lever. Reconcile the
  complete linkage graph against SNL6 before fixing these estimated stations.
- M563 compression-spring geometry needs a seat at both ends, not clearance
  gaps. Gemini's forward fitting packet says the spring is aft of M4135, but its
  rod/nut/forward-fork route requires review as a complete M575 part and linkage.
- M641/M639 mounting bolts must actually reach identified receiving material;
  mere absence of intersections does not establish a supported bracket.
- The original `exchange_rear_control_springs.py` accepts failed AdaptiveMass
  convergence when only successive numerical values agree. That bypass is not
  retained. Initial redo trials preserve Gauss/GK and partition failures while
  a restricted independent surface integration method is being checked.

Checkpoint completed: `springs_integrated01` (3,294 / 575 / 365), native
`e62ab97d8c480a780a87768816ec0140da2f7c363e369b519a1c2d7a8ab59f31`.
Nominal `springs03`, variation `springs_variation03`, exchange05 are authoritative.
First/second native and exchange attempts remain diagnostics. Measurement controls
surface_mass02 and surface_mass04 pass. Progression 258, standard unchanged.

Next dependency adjustment: center M641/M640 support and real floor-6 attachment
can proceed independently. Establish M638 near the driver from the printed M574
length before full M575/M573/M579/clutch routes; Gemini X3700 is contradicted by
its own X7280 driver layout and the source 49½-inch rod. See long_controls_sources.
Full withheld commit and front-controls continuation remain required.

Second accepted increment: `center_foot_integrated02` (3,324 / 580 / 372), native
`1ea80885fc1ded9484fcc267d43c41476264e2e3be5fd92a3198cc616a323668`.
Authoritative prototype `center_foot05`, variation `center_foot_variation05`,
source_review02, v3 geometry/checker, exchange01. Each: 115 local checks,
76 context pairs with no exemptions/findings, 37 strict STEP comparisons.
Full native: 57 transfer checks, 574 unchanged definitions preserved, one floor
revision limited to six declared holes, 1,772 archive BReps and 160,044 persistent
properties identical in a fresh reproduction. Four progression views added: 262.

The first four foot trials and integrated01 are rejected: closer HB92/SNL6 review
showed that M640 has both rod eyes on the same side of its pivot and M641 pivots
vertically. The equal opposite arms and transverse floor journal inherited from
Gemini were wrong, although center_foot04 passed mechanical checks. See
`center_foot_source_correction01.json`. Topology must be reviewed in at least two
relevant source projections before treating material tests as acceptance evidence.
Exact arm radii, cast form and neutral clocking remain approximations.

Next: M638/M639 supports and eight single-ended M640 receivers, constrained by
M574 front rod length and real support material; then complete rear routes and
clutch, followed by the preserved driver-controls continuation. Do not stop after
these two accepted increments: the user's complete withheld-commit redo remains active.

Third accepted increment: `intermediate_integrated01` (3,347 / 586 / 385), native
`6ea0cdc50a55cd8e86b8ab6bd49a54094b103d5bf17c7c7156f8125f8601d821`.
Nominal `intermediate02`, variation `intermediate_variation02`, builder v2,
source_review01. Each has 101 local checks, 53 context pairs and 29 STEP comparisons.
All 580 inherited definitions preserved; 43 full transfer checks; fresh build
reproduces 1,790 archive BReps and all 161,989 persistent properties. Four views
bring progression to266. Standard remains unchanged; floor3 added as revised
local development context with six holes, not duplicated vehicle material.

X5944.495797 follows printed M5741257.3 mm core plus two25.4 mm pin/socket offsets
against provisional driver [7220,+/-180,890]. M639 pedestals on two floor-supported
M3019 strips, with2-inch cap screws entering from below, are explicit estimates;
the real strip/casting/floor bearing and screw engagement now close mechanically.
Eight source applications have separate physical M640 receivers: reverse1,
clutch1, high2, low2, foot2. Axial rocker lanes await constraint by complete rods.

Next high-route study: `high_alignment01` tests horizontal rear forks and a port
guide shifted back into the rear-eye lane. Source SNL6/HB92 shows M563 seating
between the rear fork nut and fixed guide; the old spring ended on a bare rod bend.
This study uses explicitly nonphysical rod/spring envelopes, not accepted parts.
Port guide movement also restores its old channel holes and cuts real new holes.
Assess actual context before committing to complete rods/springs. Finish remaining
withheld redo and driver-controls continuation; do not stop at this checkpoint.

High-speed rebuild, 27 September: authoritative local prototypes are `high02`
and `high_variation_trial02`, generated by `trial_control_rebuild_high_v2.py`.
Both pass156 independent material/receiver checks and349 context pairs.
Strict exchanges: nominal `exchange04`, variation `exchange03`, using
`exchange_control_rebuild_high_v2.py` without its optional cache. Complete
M575 rods and ground-ended M563 coils have real socket engagement and both
spring bearing patches. Full native `high_integrated01` is being verified;
do not promote it until its qualification receipt exists.

Coupled corrections are explicit estimates, not recovered historical castings:
rear M355 pin uses the existing SNL6 pixel1490,908 as a construction constraint;
upper adjustment geometry remains unchanged. M569B printed1.5in is interpreted
as socket length. M4135 has an aft offset return to provide a bend corridor.
Clutch feet previously stood51.3694307mm above the floor; their old floor holes
also differed from cap axes by6.2642793mm. Revised lower casting/actual floor
holes preserve main/auxiliary journals and upper clutch connections. Raised
left bridge clears the rear control channel. High02 checks actual floor-hole
material restoration and all8 source-sized cap screws, not just nonintersection.

`high_alignment01`–`06`, `high01`, and variation_trial01 remain diagnostics.
First high02 STEP Gauss measurements failed convergence. `exchange02` fixed
measurement selection for plates/levers/ground coils but accidentally selected
lever integration for4 moved joining rivets. `exchange03` nominal attempted
BRep-pair cache reuse, which correctly refused mismatched serialization hashes.
Nominal04 and variation03 perform full strict comparisons with the correct
measurement selection; no predicate was relaxed. `TrimmedSurfaceMassV5`
extends the earlier surface quadrature to actual curved trimming boundaries,
including crossed surface knots. It passes35 analytic/NURBS/rigid-frame controls
in `diagnostics/trimmed_mass01`. V4 and the aborted slow partition attempt remain
diagnostic only. V5 is not a universal convergence guarantee (the lever uses GK).

Next after high_integrated01 qualification: complete M573 rear low-speed rods
from the actual free front eyes of M4133/M4134 to intermediate Low receivers;
complete M579 from the inner M641/M640 foot eyes to intermediate Foot receivers.
Use actual saved bores, not stale fulcrum_integrated01 interface coordinates.
The M579 route crosses low/high lanes in plan and must have verified vertical
separation. Then SH944/M581 and the remaining forward connections; finally
resume the preserved driver/front-controls inventory. The entire withheld redo
and driver continuation are still required; do not stop after this increment.

High checkpoint qualification completed: 1,072 bound dependencies; 87 installation
checks, 578 preserved inherited definitions, exact fresh rebuild. Four inspected
views bring progression to270. Commit this stage, then continue long rods.

Fifth accepted increment: long_rods_integrated01, native
`7b7efd440348db104f06456f4ed2ebc318c56d1b3f378fd584aa82f532325d96`,3395/593/403. Nominal long_rods03 and
variation_trial01, builderv3. 156 local checks each,240/239 context,51 STEP each.
All588 unchanged definitions preserved; fresh build1,811 BReps/165,031 properties.
Four views bring progression274. All ten M640 inner radii66.675, outer101.6 fixed;
rear forks yaw10deg inboard, low outer lanes+/-300 toX3160, foot transition endsX4700.
Source assumptions stay explicit. Updated front interfaces/driver datum in report.details.

Next SH944/M581: original Gemini wrongly equates SH944A with M4131 and cites
wrong SNL pages. Correct selected_rows: SH944A37:008, bolts31:009(half x1.75in)
and31:011(half x2.5in), SH944C/B119:025/026, keys115:013, shaft211:032,
M581193:007, SH953E87:001, M569C86:022. HB92/SNL6 source side shows both
clutch swing connections below their pivot; Gemini opposite-arm placement must
be re-evaluated. Original Woodruff key disk axis is parallel to shaft: redo as
axial/radial key segment with tangential thickness and true shaft/hub keyways.
Complete four bracket bolt/nut/lock mounts into actual EngineFrame_RearChannel.
Do not stop after this increment: whole withheld redo then driver continuation.

Clutch work in progress after d1612733: latest successful context-only trial is
clutch_swing05, builder trial_control_rebuild_clutch_swing_v4.py and parts_v2,
controls05/source_review03. 33 new occurrences, 8 new definitions; floor6 revised
only by four mounting bores. 35 prototype occurrences include floor and AuxLever1.
All171 context pairs clear. NOT yet locally/STEP/variation/source/render qualified.
No live tool session remains from these trials after session16977 exited0.

SH944 floor-mount hypothesis: base [3350,350,533.05], shaft[3350,350,715],
shaft120mm x25.4 alongY; cheekcentersY305/395, width10; arms short47.3 atY335,
long88.9 atY365, both down. Actual source hardware4 half x1.75in mounts and2
half x2.5in clamps; complete nuts/locks. Four floor holes real, no unlisted spacers.
Woodruff key arc lies axial/radial planeYZ, tangential6.35 thicknessX, diameter25.4,
height10.31 inferred (still needs dimensional review), projecting2.5 above shaft.
Two actual circular shaft pockets and straight hub keyways; all clearance .025.
Both links have split radial clamp at+X, boltaxisZ, full source63.5 shanks.

M581 rear joint at existing AuxLever1 eye[2354.944642,141,622.697294], SH953E/F
family, pitched30deg UP aboutY. New source3/4 USStd nut, not old smaller clutch nut.
Rear pin-to-face55, insertion19.05; forwardM569C/M568C at[3350,335,667.7], axis-X.
Rod path starts rear+axis35.95, continues to rear+axis170, cubic to[2700,335,710],
line[2830,335,710], cubic[3120,335,667.7], ends[3324.6,335,667.7]. Full retained
material clear, but source routing/station remains explicitly estimated.

Rejected trials01(engine-frame mountX3000/Y60/Z728):9 intersections;
02(floor mount, depressed route):5;03(upward route, early outboard bend):one
carrier overlap;04(190mm straight departure):one stop-rod overlap;05(170mm):clear.
ClutchBrake_Carrier boundsX2401.49..2505.49,Y69.28..237.7,Z655.6..743.87;
StopRodX2418.72..2629.94,Y118.45..149.55,Z721.08..751.08;
FlywheelX2674.69..2908.07,Y+/-251.6,Z649..1152. Source arrangement re-inspected;
SNL115/119 scans confirm2 No15 keys andone short/long link. ModernLawson3038
corroborates No15 one-inch diameter/quarter-inch thickness only; height unverified.
No manufacturing or historical-fit claim. Continue local checks/variation/render/
STEP/integration, then unresolved center-clutch route and forward/driver controls.

Source omission recovered: SNL192:020 SH229A center clutch rod93in. Full scan inspected. clutch_swing05 and unchecked integrated01 are not acceptable final station despite local clearance. v5 combines M581/SH944/SH229A, solves bracketX from complete2362.2mm stock, preserves all retained receivers. Source04 and controls06; no accepted checkpoint changed.

Sixth increment accepted:clutch_swing_integrated02 4fb23038e66070ff47f8c6813c64cd46f8972846237adfd67a0f991e24809ddc,3437/602/409. Complete SH944/M581/SH229A,142local/53STEP each,215nominal/214variation context;592preserveddefs,1838freshBReps/167273properties. v7controls08/source06,var05. Source93in determines bracketX; all original140withheld additions disposed in withheld_redo_completion.json. Redo functional scope complete. Continue driver draft, beginning source-bound M782 shaft and real mounting; future forward rods are separate continuation.

Driver continuation is active at ../driver_redo01/shaft01: five-part uninstalled M782/M313/keeper study;28local/9context/7STEP eachnominal+variation, freshreproduction and two reviewedviews. Full checkpointremainsclutch_swing_integrated02. NextrealM746/M747floor mounting andM783; reducedends andoutboardkeeperlayout provisional. No active worker after completion.
