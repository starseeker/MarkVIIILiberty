# I03 — input cover fasteners and grease feed

This increment extends the [input assembly](I03-input-assembly.md) with four
MX25 stud/nut/cotter sets and the M250 grease-cup installation. It also drills
the corresponding receivers in M264, M250 and all sixteen M254 shim leaves,
and opens a feed through M250 and the M249 spacer into the bearing cavity.
It remains an isolated transmission candidate pending tank integration.

## Source decisions

The [source register](../experiments/drive_chains/transmission_input_installation_sources.json)
retains the literal SNL records and their conflicts. Original SNL77 lists four
MX25 assemblies in the owning M264 cover assembly. SNL240 also gives four in
the catalogue quantity, but its usage note allocates two to M250/M264. This
reconstruction selects four, with an inferred cardinal pattern on the existing
96 mm radius. Neither the section drawing nor this choice resolves the
contradictory usage note.

SNL240 specifies a half-inch stud, 2-17/32 inches long, with one inch of
U.S. Standard thread and 7/8 inch of SAE thread. These convert to diameter
12.7 mm, length 64.29375 mm and thread intervals of 25.4 and 22.225 mm.
The nested nut is printed as one inch; the generic SNL124 nut allocation
instead assigns a three-quarter-inch nut to MX25. Both conflict with the
stud. The modeled half-inch nut is an explicit mechanical interpretation.
Its source record and conflict are retained, but it does **not** claim to
fulfil either conflicting catalogue nut identity. Nut flats, height, slots
and thread clearance are inferred.

Each set includes the printed 3/32 × 1 inch split pin. Its two round-wire
legs are formed outward, preserving a 25.4 mm centreline length under the eye.
The eye and wire section are approximations; exact stock volume, period
manufacture, loads and removal by straightening are not qualified.

SNL78 identifies one No.4 × half-inch grease cup, SNL85 one Q51QD half-inch
beaded 45-degree elbow, and SNL124 one half-inch × 1-3/4 inch close nipple,
all explicitly allocated to M250. The nipple retains the printed 44.45 mm
length. The source does not provide a complete No.4 cup drawing: its hollow
body and screw cap are an inferred two-solid decomposition of **one**
commercial item, with the catalogue identity on the assembly container.

Two modern manufacturer documents support limited dimensional transfers:

- [Wheatland standard-pipe brochure](https://www.wheatland.com/wp-content/uploads/2017/12/Standard-Pipe-Brochure-2.pdf),
  page5: nominal half-inch pipe OD0.840 inch and Schedule40 ID0.622 inch
  give 21.336 and 15.7988 mm. The historical wall schedule is unproven.
- [Anvil Fig1102 submittal](https://www.asc-es.com/resources-and-downloads/1102-45-elbow-submittal),
  page3: the half-inch 45-degree elbow has centre-to-face dimension C=7/8 inch,
  or 22.225 mm. The adjacent A/J table belongs to the 90-degree street elbow
  and is not used. The historic Q51QD casting profile remains inferred.

The downloaded PDFs are retained with hashes. These transfers do not claim
modern construction or ratings for the historical parts.

## Geometry and remaining uncertainty

The [controls](../experiments/drive_chains/transmission_input_installation_controls.json)
separate printed values, transfers and assumptions. The stud starts at
X219.6 mm and ends at X283.89375 mm. Its SAE interval starts at X261.66875,
just before the nut seat at X262.0. The blind receivers are deepened to
X219.4 so the nominal nut base lies within that threaded interval. Threads
are smooth clearance envelopes; the model does not simulate thread contact.
Nut-clearance recesses of 12 mm radius run from X262 to X277 in the housing
barrel. Cotter axes follow the tangent at each stud position, keeping their
eyes and formed tails clear of the barrel. These are inferred joint details.

The grease feed is at X279.0 mm, between the cup backs, 45 degrees above
port. The nipple enters radially and the elbow turns the cup upright.
This location avoids the cardinal stud pattern and opens into the M249
spacer. It is a reconstruction assumption, not a position measured from
SNL Plate23: the fittings lie outside that section plane. The No.4 cup is
44 mm in body diameter with a 48 mm cap; those dimensions are also inferred.

An 8 mm drilled passage continues from the nipple receiver through the spacer
to the open cavity between the opposed cone small ends. This is a connected
geometric route, not a grease-flow calculation or a sealing qualification.
The M249 one-versus-two quantity conflict remains unresolved.

## Qualification

The [combined qualification](../experiments/drive_chains/transmission_input_installation_build/qualification.json)
passes for the [saved candidate](../experiments/drive_chains/transmission_input_installation_build/TransmissionInputInstallationCandidate.FCStd):
**1,303 valid single-solid occurrences**, sixteen new and thirty-six revised,
with 1,251 earlier occurrences retained unchanged. Seven new definitions supply
the added hardware and fittings; two earlier cotter definitions are repaired.
All 653 affected material pairs and 52 raw/bounded STEP comparisons pass with
zero material difference. Twenty-one interfaces are checked in this increment;
573 earlier interface results are retained against unchanged geometry and the
hash-bound parent report.

The [independent checker](../experiments/drive_chains/transmission_input_installation_build/interface_checks.json)
passes 344 checks. These include printed fastener dimensions, thread intervals,
nut seats, both cotter legs/tails, straight-withdrawal obstruction, protected
casting material and a connected grease gauge: diameter2 mm along the main
feed, with diameter1 mm branches passing beneath the cage lips toward both
cone small ends. Deliberately closed housing/spacer passages and a plugged
elbow are detected. This qualifies geometric continuity, not lubricant flow.
Four [local parameter trials](../experiments/drive_chains/transmission_input_installation_build/sensitivity_checks.json)
vary port station and passage diameter using the actual prior housing/spacer;
each checks six affected parts and the radial passage. They are not full-tank
perturbation runs.

All seven final rasters were [visually inspected](../experiments/drive_chains/transmission_input_installation_build/visual_review.json),
including the unchanged SNL23 registration and both repaired pin forms.
Three new progression snapshots preserve the installation cutaway, grease
section and MX25 joint. Twenty standard native files and forty-three earlier
snapshots remain byte-identical. The builder report is an immutable generation
receipt; the combined qualification records completed rendering and review.

An initial construction attempt was rejected before saving a candidate because
the elbow turned the cup horizontal. Reversing the bend in its local plane
restores the intended upright cup. Its exact initial inputs and failure log
remain in the candidate's rejected-trial archive.

The next complete trial found nut/barrel intersections of 0.555–30.596 mm³,
two inward-pointing cotter clashes of 6.785 and 10.059 mm³, and an elbow-bead
intersection of 18.544 mm³ with the housing flange. The nut reliefs and
tangential cotter orientations address the hardware clashes. Moving the
inferred port from X276.5 to X279.0 clears the elbow bead from the flange.
The rejected reports and exact inputs remain preserved.

The swept-torus construction in that trial also failed the two-way STEP
material comparison. Isolated tests reproduced the failure on a single
cotter leg despite matching volume and topology counts. Replacing pipe-shell
arcs with equivalent analytic cylinder/torus segments passed that local
comparison. The candidate uses the analytic construction for both cotter
legs and the elbow; the small-pin check also requires both legs and their
formed tails to remain present after fusion and native reopening.

A stricter independent check then found that the many-piece eye fusion had
dropped one complete leg despite returning a valid single solid. A semicircular
analytic eye with overlapping lead junctions retains both legs; explicit leg
gauges and minimum stock-volume checks now guard that requirement. A focused
audit found the same defect in the older bearing-cap and input-shaft cotter
definitions. This increment repairs those two definitions, affecting sixteen
cap pins and one input-shaft pin, while retaining their source dimensions and
placements. The input-shaft pin still has unspread legs.

The final input-pin STEP comparison had zero raw and bounded material
difference, but the reported maximum tolerance changed from
7.925414398e-6 to 7.925427862e-6 mm. The earlier relative-only guard rejected
that 1.35e-11 mm drift. The validator now declares a separate absolute
1e-10 mm reporting-roundoff allowance; it does not alter either shape's
stored tolerance. The 1e-4 mm native ceiling and bounded material comparison
remain. A negative check rejects a 1e-7 mm increase. The rejected tolerance
receipt is retained so this qualification change is reviewable.

## Reproduce and continue

```sh
python3 cad/003_FullTank/experiments/drive_chains/transmission_input_installation_probe.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_transmission_input_installation.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/check_input_feed_variants.py --stage cad/003_FullTank
python3 cad/003_FullTank/experiments/drive_chains/render_transmission_input_installation.py --stage cad/003_FullTank
```

The builder accepts `--output`; the checker and renderer accept `--candidate`.
The independent rendering receipt binds an immutable builder report.

Input pump attachments, B6205/A7679/A7680/A7682 support components and their
installation remain open. The brake-bearing bushing is **M265**, and its cap
is **M266**. The later MX14 cap-stud work must retain another source conflict:
SNL59's assembly list gives 1-9/16 inches while SNL240 gives 1-11/16 inches.
Case fastening, controls, complete lubrication/mounting and tank integration
remain ahead. This increment is not a completed transmission or full tank.
