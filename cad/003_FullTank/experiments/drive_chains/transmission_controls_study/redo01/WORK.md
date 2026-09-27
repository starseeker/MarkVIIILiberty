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
