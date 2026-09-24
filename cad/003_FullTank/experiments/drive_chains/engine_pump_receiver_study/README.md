# Coupled pump receiver and powertrain registration

23 September 2026. The **local receiving case is qualified**; the complete tank
installation remains unfinished. The standard tank011 native files are unchanged.
The [support and planetary checkpoint](registration/native_support_trial01/README.md)
retains 2,393 development occurrences and resolves the local carrier alignment
and engine rail/bracket gaps. Casings, transmission supports and station
qualification remain open. The subsequent
[fixed-frame trial](registration/native_frame_trial02/README.md) closes local
transmission support/MX5 interfaces but worsens channel-height agreement in its
source overlay. Compare a frame that follows the shaft before choosing the
installation. The progression now contains 155 images; the standard tank is unchanged.

`trial02/PumpReceiver.FCStd` reconstructs the receiver from the pre-receiver
lower crankcase, using the source-profile oil pump and the 171.45 mm lower-drive
spacing. It provides the complete circular/nose mounting land, ten blind stud
receivers, two separate oil sockets, water-pump pads and a recut retaining-screw
bore with a blind head recess. Casting stock, fits and exact cast profiles remain
documented estimates. Open sockets are not a finished oil circuit.

**44 saved-native checks, 77 case pairs, 22 cross-component pairs and both strict
STEP comparisons pass.** A fresh rebuild reproduces both serialized shapes,
20 object types and 162 checked properties, excluding new UUIDs. The three local
views were directly inspected. Isometric and section snapshots bring the visual
progression to 149, preserving all 147 earlier images and standard native files.

## Retained failures and source corrections

The oblique LIB96 image does not establish an offset between the oil-pump and
lower-drive axes. LIB28 plan and LIB107 section support their common splined axis;
the previous offset inference is retracted as a dimensional constraint.

`trial01` failed one case contact: the newly fused water pads refilled the lower
driver's screw bore/head region. `trial02` recuts the bore after the additions and
adds a short recess, retaining 10.0737 mm to the water joint plane. The printed
retaining screw dimensions are unchanged.

An initial whole-shim witness included the center opening and four stud-hole
clearances. The earlier qualified case and both new trials lack the same
40.94477 mm³ in those clearances. The corrected check excludes only those five
defined allowances. A negative control extending the head recess through the
bearing face loses 22.61508 mm³ of required land and is correctly rejected.

The first four-control `parameter_trial` enlarges the oil-stud bore clearance to
0.08 mm and fails the unchanged full-gasket support check by 0.408721 mm³. All
other 43 checks and all contact pairs pass. `parameter_trial02` instead uses
0.025 mm clearance, with 16 mm nose stock and 0.75 mm head-recess allowances.
It passes the same 44 checks, 77 case pairs, 22 cross-component pairs and both
strict STEP frames. The failed first variation remains.

## Merged hierarchy

`assembly_trial02/DrivetrainWithBothPumps.FCStd` contains **2,393 physical
occurrences**, including 146 oil-pump constituents in 40 definitions. These are
development assembly counts, not additions to the standard tank count.
Its independent verification now passes all eight criteria, all 83 strict
definition-material comparisons and every source-derived occurrence frame.
The earlier byte-equality
assertion in `assembly_trial01` was too strict for native save normalization;
archive internals have not been rewritten to force matching hashes.

The first material verifier terminated with tool exit247 after 42 passing
definition pairs; its cause is not established. The isolated checker extracts
one native document at a time without copying all occurrence shapes, then runs
each remaining material comparison in its own process. It retains the original
material/tolerance acceptance expression. The 42 completed comparisons can be
reused only for their exact source/candidate BRep hashes; all source-derived
occurrence coverage and composed frames are checked independently again.

The current driver is `check_engine_pumps_isolated.py`; the earlier monolithic
checker and its output are retained under `assembly_trial02/diagnostics/process247`.
The source-profile pump's separate 186-pair STEP check subsequently completed;
all 186 comparisons pass. The merged-hierarchy driver is still producing its
legacy render views; intermediate outputs are not accepted final visual reviews.
Its completed `independent_checks.json` records the successful geometry checks.

## Global registration

The inherited engine axis is Z849.233510 mm; it derives from a 50-pitch chain
closure along an initially estimated direction, not a printed engine height.
The floor separately follows the printed 20.75 inch ground clearance. The
selected pump extends **43.875865 mm below the current floor envelope**.

The [station study](registration/station_candidates.json) solves three
floor-relative SNL2 hypotheses while retaining the fixed roller-pinion axis and
17.21° phase, 50 pitches of 76.2 mm, and 23/12 teeth. All three mathematical
closure/phase checks pass. A vertical-only shift fails closure by 11–14 mm.

| Axis interpretation | Transmission X / Z, mm | Powertrain shift X / Z, mm | Pump-floor gap, mm |
|---|---|---|---|
| Engine pick | 1832.082 / 906.531 | +6.852 / +57.298 | 13.422 |
| Transmission pick | 1830.879 / 894.675 | +5.649 / +45.441 | 1.565 |
| Common horizontal mean | 1831.495 / 900.603 | +6.264 / +51.369 | 7.494 |

No candidate is accepted for installation. The source picks alone carry a ±35.57 mm
height bound. The [comparison](registration/registration_comparison.png) shows
why local floor registration cannot replace the whole-vehicle transform: it
aligns the transmission candidate but shifts the fixed final-drive projection.
Drawing accuracy and floor-line interpretation remain explicit uncertainties.

A subsequent [saved placement diagnostic](registration/native_trial01/README.md)
instantiates the common-axis hypothesis for measurement. Both chains pass 886
material comparisons, but obsolete casings interfere, support contacts separate,
and the new output-shaft phases require internal carrier/planet changes. This
trial remains unqualified and the standard tank is unchanged. The subsequent
[coupled phase trial](registration/native_phase_trial01/README.md) resolves the
carrier/spline mismatch while preserving tooth meshes. The
[support trial](registration/native_support_trial01/README.md) rebuilds three
brackets to restore rail contact while retaining floor receivers and hardware.

Next, compare fixed and shaft-following frame placements against the source and
hull/floor attachments. Locally seated brackets alone do not settle this choice.
Then rebuild constant-stock chain casings and check controls and surrounding hull
interfaces together. Complete outstanding definition-preservation checks before
promotion. Preserve the printed floor clearance and keep historical station
acceptance separate from mechanical fit.

## Reproduce

Run from the repository root; replace output paths to retain existing evidence.

```sh
python3 cad/003_FullTank/experiments/drive_chains/engine_pump_receiver_build.py --output .work/receiver-rebuild
python3 cad/003_FullTank/experiments/drive_chains/check_engine_pump_receiver.py --candidate .work/receiver-rebuild --render
python3 cad/003_FullTank/experiments/drive_chains/check_engine_pump_receiver_exchange.py --candidate .work/receiver-rebuild
python3 cad/003_FullTank/experiments/drive_chains/engine_pumps_integrate.py --receiver .work/receiver-rebuild --output .work/pumps-integrated
python3 cad/003_FullTank/experiments/drive_chains/check_engine_pumps_isolated.py --candidate .work/pumps-integrated --render
python3 cad/003_FullTank/experiments/drive_chains/probe_powertrain_registration.py
python3 cad/003_FullTank/experiments/drive_chains/render_powertrain_registration.py
```

The oil-manifold source supplement identifies 18 prospective constituents,
including one large and six small bearing-feed tubes. Plug allocation and the
special drain-plug identity need reconciliation before that circuit is qualified.
