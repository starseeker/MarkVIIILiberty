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
HB130 explicitly specifies 12 driving-sprocket teeth in both its outline table
and its prose. The original scan was inspected on 20 September 2026. With
three-inch pitch, 12 teeth give an 11.591110-inch pitch diameter, consistent
with the rounded printed control. The tooth count is directly documented;
the detailed tooth and spline profiles remain inferred. The installed roller
pinion carries 23 central teeth.

The same HB130 outline gives a two-inch chain roller diameter and a maximum
chain width of 4-9/16 inches. These constrain the upcoming native chain study;
they do not reconcile the SNL's quantities or prove that a supplied bushing
and a finished roller are separate parts.

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

## Installed phase and drawing comparison

The second calculation, `installed_pitch_route_probe.py`, retains the existing
17.21-degree roller-pinion phase and aligns the chain joints to its relief
centers. Fifty exact 76.2 mm chords close at a center distance of
1,230.854801 mm. Twelve vertices occupy the large pitch circle and six occupy
the small circle; their phase errors are below 1e-9 radians. The inferred
small-sprocket phase is 17.983209 degrees. No native datum is changed.

The resulting candidate transmission axis is 134.927 mm from the earlier
provisional layout point. On the unchanged SNL Plate2 calibration it projects
to pixel (1412.157, 451.749), close to the visible shaft center. The earlier
point was (1390, 455). The interactive
[source overlay](../experiments/drive_chains/route_comparison.html) was rendered
and inspected: the lower chain run broadly follows the illustration, and the
upper run crosses details hidden by the original casing/section. This is a
visual comparison made after the mathematical prediction, not an independent
metric acceptance. The casing, transmission geometry, physical tooth fit and
catalogue quantity conflict still need checking.

## Native roller-envelope clearance diagnostic

`roller_clearance_probe.py` creates and reopens an isolated casting with fifty
diagnostic annuli on the candidate route. Their 25.4 mm outer radius comes from
HB130; their 39.6875 mm axial length covers only the inner-bar gap. These are
diagnostic envelopes, not inventory-counted chain parts.

The existing 22.525 mm circular relief produces 16 roller/casting overlaps,
with a largest volume of 10,181.857 mm³. A 25.65 mm relief candidate reduces
this to three overlaps, with a largest volume of 990.215 mm³ near the entry
and exit transitions. Both reopened native models and their elevation rasters
are retained in `experiments/drive_chains/roller_clearance_build`; both rasters
were inspected. Neither case qualifies chain engagement. The result shows that
the tooth flank/transition shape needs work in addition to the root radius.
The currently running pinion qualification still covers its installed wheel,
shaft and hull interfaces; the chain interface remains explicitly incomplete.
