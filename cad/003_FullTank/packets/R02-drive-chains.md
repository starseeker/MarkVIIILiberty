# R02 — drive chains and casings, research preparation

Standard installed geometry follows completion of the roller-pinion integration.
No drive-chain component geometry has been promoted by this packet.

## Source controls and unresolved counts

Original SNL61 and SNL135 were inspected on 20 September 2026; records and
reviewed-file hashes are preserved in `experiments/drive_chains`.
SNL61 lists two complete chains. Each chain lists 25 SH40AD bushes,
25 SH40AE pin assemblies, 25 SH40AC inner bars and 25 SH40AB outer bars.
SNL135 nests one pin and one 3/8 × 1-3/4 inch split pin per pin assembly and
lists 50 pin assemblies for the vehicle.

HB132 specifies a three-inch pitch and 50 pitches per chain. A conventional
50-pitch chain needs 50 articulation axes, so the apparent factor-of-two
conflict requires an explicit interpretation of the supplied bars/bushes/pins.
Do not double catalogue quantities, call the records reconciled, or create
overlapping duplicate solids to satisfy both statements.

HB132 gives outside-bar spacing 2-7/8 inches and inside spacing 1-9/16 inches;
bar stock is respectively 1/2 and 5/8 inch. Pin diameter 1-7/32 inch and
reamed hole 1.231 inch imply 0.01225 inch diametral clearance, although the
same paragraph states 0.005 inch. Preserve this separate dimensional conflict.

The M291 transmission pinion has a printed four-inch overall axial width,
1-1/2 inch tooth width, ten shaft splines and 11.592-inch pitch control.
With three-inch pitch, 12 teeth give an 11.591110-inch pitch diameter. This
supports a 12-tooth hypothesis; it does not establish the detailed tooth or
spline profile. The installed roller pinion carries 23 central teeth.

HB134 describes a 6-5/8 inch wide casing following the chain contour, with a
separate removable cap at the roller-pinion end. It requires oil holes on top
and cotters facing outboard to clear the epicyclic gusset. Those are standard
installation constraints even while poses remain deferred.

## Geometry work to follow

1. Compare SNL Plate25 and HB81/82 chain illustrations with the original chain
   inventory. Record which unresolved quantity interpretation is modeled.
2. Establish the transmission-pinion axis against the provisional transmission
   datum and the now explicit roller-pinion station; retain source picks and
   any geometric closure correction separately.
3. Solve a discrete closed pitch polygon for the selected standard chain,
   then model separate bars, bushes, pins and cotters with source identities.
   Check all joints and both handed installations, including the outboard
   cotter orientation. A static closure does not qualify running engagement.
4. Populate the body/cap, cleats, strips, supports and fasteners from their
   nested SNL55/60/61 records. Provide explicit service clearances without
   introducing posed variants.
5. Review native sections and the installed drivetrain against HB81 and SNL25;
   retain significant isometrics after promotion and completed validation.

## Discrete pitch-route preflight

`experiments/drive_chains/pitch_route_probe.py` constructs a provisional external
route around the 12/23-tooth pitch circles and steps along it by exact 76.2 mm
chords. The 50-pitch case closes at a center distance of 1,230.966743 mm; maximum
chord error is below 1e-9 mm. Its phase begins at the large-circle tangent and
is not yet aligned to the installed casting's teeth.

The literal 25-articulation interpretation does not bracket a closed route with
separate pitch circles in this model. This reinforces the need to clarify the
SNL's supplied-unit counts; it does not resolve their meaning. Neither result
changes the provisional transmission datum or creates installed components.
The next native study must check tooth phase, bar/bush sections and all physical
interfaces before adopting a chain route.
