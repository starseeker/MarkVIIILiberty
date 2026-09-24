# Brake suspension brackets and stops — 24 September 2026

`PowertrainWithBrakeSuspension.FCStd` adds **four M338 suspension brackets and two
M385 stops** to the qualified frame-joint assembly. The development model now
contains **2,511 physical occurrences, 466 definitions and 231 assemblies**.
All inherited shapes, occurrence frames and assembly ownership are retained.
The parts are seated for geometric development; their fastening and connected
brake linkage remain incomplete. Standard tank011 is unchanged.

## Evidence and approximation

SNL96 lists four M338 brackets and two M385 stops; HB207 independently lists four
brackets. HB134/135 and SNL32 show the upper brake suspension supported below the
top channel. HB135 labels the long M385 stop behind the suspension link. Assigning
one stop to each track brake is an inference from that view and the source count.

The M338 side profile is registered from HB134 to the retained channel depth and
web separation. Its top foot and bored lug use analytic planes and cylinders;
the rounded lower end is inferred behind the overlying link head. Transverse
width, lug thickness, bore size, clearance and hidden construction are estimated.
The four occurrences share one definition. Both M385 occurrences share an
estimated L-section definition whose height follows the HB135 frame registration.
No bend radius, mounting holes or rivet allocation is claimed from these figures.

The chosen nominal bracket has a 93.607 mm by 60 mm foot, 8.373 mm foot thickness,
12.7 mm lug stock and a 24 mm intended pin diameter with 0.15 mm radial geometric
allowance. Pin drop below the upper channel is 66.341 mm. The stop is 201.893 mm
long, 40 mm wide and 6.35 mm thick, with a 23 mm upper toe. These values are
reconstruction controls, not recovered production dimensions or tolerances.

Each bracket is centered transversely on the saved cylindrical friction face:
the low-speed pair at Y = ±535.396 mm and track pair at Y = ±770.164 mm. Axial
centering remains provisional until the suspension links and complete band
stacks are constructed. The existing shaft phase is not used to rotate a fixed
bracket; all supports remain fixed in the vehicle frame.

## Registration conflict and rejected trial

The HB134 registration predicts a shaft center 9.576 mm aft and 15.269 mm above
the saved model center. A local ellipse fit confirms that the manual source
shaft-center pick is within its four-pixel allowance; the discrepancy is not
resolved by moving that pick. Both registration scales remain conditional.

The first layout used the channel datum for bracket X. It produced 3,287.684 mm³
of interference at each low-speed bracket/diaphragm and 701.214 mm³ at each
track bracket/stop. Those failures remain in `../trial01/`.

The current layout derives X from the source pin-to-shaft separation and the
retained shaft. The four brackets move forward by 9.575922 mm; the frame, stops
and all inherited occurrences stay fixed. The recorded source overlays still
use the channel registration, so the displaced pin outline remains visible.
This is a mechanically fitting alternative, not proof of the historical station.
No Boolean tolerance was relaxed and no intersecting material was discarded.

## Saved-artifact checks

All **53 independent checks pass**: counts, source identities, composed frames,
ownership, single-solid validity, stock volume, full open pin bores, complete
channel bearing faces and rotating-drum envelopes. Filled-bore and lifted-seat
negative controls are included. Each M338 foot bears over 5,616.410 mm² and each
M385 toe over 920 mm². The nearest drum-envelope clearance is 77.746 mm.

All **14 nearby development material pairs pass**. Filtering against the full
5,316 retained standard-tank occurrences finds no possible bounding-box pair
with these six parts; this is not a full-tank interference qualification.

`BrakeSuspensionDefinitions.step` and `BrakeSuspensionInstallation.step` pass all
**eight strict round-trip comparisons**: two definitions and six installed
occurrences, including material in both directions, topology, centroid and
unchanged maximum tolerance. All **464 inherited definitions** match the parent:
438 exact BReps and 26 strict material comparisons.

A fresh nominal rebuild reproduces all **1,424 archived BReps, 9,260 object types
and 119,708 persistent properties**, as well as the complete hierarchy and frames.
New group UUIDs are deterministic; no property exclusion is used. The existing
generic reproduction checker labels its report a transmission-support rebuild.

The isometric, underside detail and both source overlays were inspected directly.
Their open bores and separate stops are visible. The overlays retain pin-position
disagreement and cannot resolve the transverse stock or hidden mounting holes.
Display cropping and wireframe context do not change native geometry.

The parameter variation adds 1 mm to lug thickness, 4 mm to foot width and 3 mm
to pin drop. It passes the same 53 checks and 14 development material pairs;
standard-context filtering again finds no possible pair. All 464 inherited BRep
hashes exactly match the nominal candidate. No separate variation STEP or
historical qualification is claimed. Its controls, new shapes and reports are
retained under `parameter_trial`; the full variation and reproduction natives
remain in `.work/transmission-brake-suspension/`.

Three progression images bring the collection to **170**, preserving all 167
previous images and 27 recorded native baselines by hash. The prior rejected
layout remains documented rather than being counted as an accepted stage.

## Rebuild and next work

Use the skill's headless launcher with absolute input/output paths and a fresh
output directory. Scripts are in `cad/003_FullTank/experiments/drive_chains/`:

1. `build_transmission_brake_suspension.py --source <frame-joint-trial03> --output <fresh>`
2. `pump_integration_worker.py extract --input <fresh>/PowertrainWithBrakeSuspension.FCStd --output <fresh>/isolated/manifest.json`
3. `check_transmission_brake_suspension.py --candidate <fresh> --standard-manifest <retained-standard-manifest.json>`
4. `exchange_transmission_brake_suspension.py --candidate <fresh>`
5. `render_transmission_brake_suspension.py --candidate <fresh>`

Use ordinary Python for `check_transmission_brake_suspension_preservation.py`
and the existing `check_powertrain_frame_reproduction.py` after independently
building and extracting another nominal candidate. The stored standard manifest
can be taken from the parent frame-joint trial. Extracted BRep paths are local
cache paths; regenerate the extraction when relocating a checkout. Dimensions
update by regenerating the scripts, not by editing inert native metadata.

Continue the M337 suspension links, M339 pins and low-speed/track brake-band
interfaces, then resolve the support feet and remaining frame rivet allocation
together. The remaining 46 source frame rivets, return/upright fastening,
holding feet, packing identities and hull attachment are still open. Full engine
and tank interiors, inventory reconciliation and final integration remain
required; pose variants remain deferred.
