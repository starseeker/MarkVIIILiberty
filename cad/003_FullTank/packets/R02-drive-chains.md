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

## Separate chain fixture and installed check

The tangent-flank study retains the source roller diameter, tooth count, pitch,
casting diameter and tooth width. A 25.65 mm root seat with repeated 20-degree
straight tangent flanks has 0.25 mm minimum static roller clearance. The profile
is an explicit reconstruction, not a source drawing or a running-mesh validation.

The native single-chain fixture now contains 250 chain components and two
sprockets. It follows the documented HB interpretation: 25 inner bar pairs,
25 outer bar pairs, 50 bushings, 50 pins and 50 cotters. Its 443 candidate pairs
have no overlap after saving and reopening; the pin/bush radial clearance is
0.155575 mm. Source-sized bushings serve as the wear rollers without inventing
another part identity. Cotters remain unsplayed, oil holes unlocated, and small
sprocket hub/spline dimensions inferred. The SNL quantity conflict stays open.

Both handed installations were then tested against the tank's physical solids.
The 504 candidate leaves replace the two previous castings in that comparison.
All 18 overlaps among 886 internal and 260 external candidate pairs are with
the unperforated M2003 engine-room back plate. The failed native model, report
and inspected rasters are preserved; no chain has been promoted to the standard
assembly and no transmission datum has been changed.

Original SNL60 identifies M1592 as the casing's hull-back-plate angle. Original
SNL170 explicitly connects it to M2003 with 1/2 × 1-1/2 inch rivets, allocation
(11). Together with HB134's 6-5/8 inch casing width and back-plate fastening,
this supports testing casing passages through the wall. A separate candidate
retains its documented station, full outer bounds and stock. The opening shape,
corner radius, sheet thickness and installation clearances are inferred and
recorded independently in `casing_passage_controls.json`. Casing bodies, caps,
angles and their fasteners still need reconstruction before integration.

The isolated passage candidate passed after saving and reopening: 505 leaves,
904 internal and 255 external candidate pairs, zero overlap. All 18 formerly
overlapping chain components clear the revised wall, with a minimum measured
gap of 19.446583 mm. The retained hull validator checks 77 plates, 1,037
candidate material pairs and six compartment probes without failure.

Each inferred opening is 172.275 mm wide and 492.142731 mm high, with an 8 mm
corner radius. The precise height comes from the selected route and assumed
envelopes; it does not indicate historical measurement accuracy. The actual
oblique, wall elevation and standard isometric were inspected and their hashes
recorded. The model remains an isolated candidate: casing bodies, supports,
fastening and full drivetrain fit are not yet qualified.

## Casing shells and wall attachments

Separate source-identified M1590 bodies and M1591 removable caps now exist as
isolated native solids. Their 168.275 mm outside width follows HB134. The 3 mm
sheet stock, two-circle/tangent contour, 12 mm radial allowance, hub passages
and upper rear cap seam are explicit reconstruction assumptions. The cap's
half-bore is open to its lower edge, consistent with removing it before the
roller pinion; neither its exact split nor a service motion is qualified.

The first shell installation found two 21.609290 mm³ overlaps at the rounded
corners of the chain-only wall openings. That failure and its exact inputs
remain preserved. Openings derived from the actual casing section across the
wall thickness now measure 176.275 × 497.795324 mm with 8 mm corners. This
revised candidate passes 638 casing-related material pairs and the existing
hull checks, with 2.304985 mm minimum wall clearance, 2 mm hub clearance and
a 1 mm cap/body gap. The earlier chain-only opening candidate is superseded
for casing fit, not silently overwritten. The corrected native half-section
and installed views were inspected.

The next fixture adds two inferred M1592 flanged collars with 11 wall rivets
and 17 casing rivets each. SNL170 directly identifies the wall joint and
1/2 × 1-1/2 inch stock; SNL167 identifies the casing joint and 5/16 × 3/4 inch
stock. Angle form, 6 mm section, flange/leg dimensions and hole coordinates
are inferred. Rivet heads use the existing stock-conserving reconstruction.
All 567 saved/reopened fixture leaves are valid single solids. The 58 new
mounting parts and three drilled receivers pass 697 material candidate pairs,
56 receiving-bore checks and 56 two-receiver seating checks. The existing hull
validator also passes. Actual attachment rasters and their hashes are retained.

Original SNL31 allocates 14 bolt/nut/lock-washer sets to the two cap/body joints;
seven per cap is the working interpretation of its total. Original SNL167's
global and joint rivet counts conflict with the nested SNL55/60/61 quantities.
`casing_joint_review.json` preserves both. The 17 M1592 casing rivets are supported
by the joint row and fit within the body's 26 short-rivet allocation. Remaining
joint schedules need an explicit selected interpretation before population.

The cap-joint fixture now adds eight M1583 side cleats, four M1593 roof cleats,
four M1584 packing strips, 36 cleat rivets and fourteen three-part detachable
fastener sets. Original SNL128 and SNL270 identify the plain half-inch nut and
lock washer and explicitly include the half-inch by one-inch bolt among their
uses. Their general catalogue totals are not used as cap quantities.

The angles, five-mm stock, packing location and seven-bolt pattern per cap are
inferred. Side cleats face across the one-mm shell gap, with a packing strip;
roof flanges meet at the seam and their feet follow the sloping shell. Each
body receives nine short cleat rivets, which together with its seventeen wall-
angle rivets fills the nested body allocation of twenty-six. Each cap receives
three short roof-cleat and six long side-cleat rivets. Eight long cap rivets
remain provisionally allocated to register plates; the independent short-rivet
joint entry for those plates remains a conflict. Body long-rivet allocations
also remain unresolved. The selected schedule is explicit in the cap controls.

The first 661-leaf cap fixture found four intersections between the middle
cap-roof rivet and the adjacent bolt/nut, despite passing its bore and seating
checks. That candidate and its exact inputs remain preserved. Moving the
undimensioned middle roof-rivet station 24 mm transversely clears those parts.
The revised native fixture passes 914 new/changed material candidate pairs,
50 receiving bores, 50 joint-seating checks and fourteen simplified retention
checks. All leaves remain valid single solids after reopening. Actual whole-
casing and joint-detail rasters were inspected and bound to the report hashes.
Bolt protrusion is 1.9 mm at side joints and 2.9 mm at the roof; these values
depend on assumed nut/washer/cleat stock. Threads, spring action, clamp loads,
historical fit and removal motion are not qualified.

## Packing correction, register plates and beading

Inspection of original HB185 identifies M1584 as packing **under** the angle
cleats. This supersedes the earlier between-flange hypothesis. The corrected
candidate puts a one-mm strip beneath each body side-cleat foot, with both
side and roof flanges meeting directly. Side rivet grip increases to nine mm;
both side and roof bolt grips are ten mm, giving 2.9 mm inferred protrusion.
Its 661 leaves pass the same 914 material pairs, 50 bores, 50 seats and fourteen
retention checks, plus four explicit strip-to-cleat/sheet contact checks.
The previous source interpretation and its native results remain preserved.

The next fixture adds four M1581 body register plates, two M1594A and two M1594B
cap register plates, eight M1585 bead strips and their 72 rivets. Each inferred
register laps the other sheet across a horizontal cap seam. Equal-length inner
bead strips reinforce the forward horizontal seam segments, with five flush
countersunk rivets each. Sections, precise locations and hole patterns are
approximations, not independently established by a detailed source drawing.

All 749 saved/reopened leaves are valid single solids. The 88 added components
and drilled sheets pass 1,088 material candidate pairs, 72 receiving bores,
72 two-receiver seating checks, eight register-lap contacts and 40 flush-head
checks. Countersunk heads use an inferred 90-degree cone; their nominal length
is interpreted as including the head, and formed tails conserve the resulting
stock volume. Exterior, inner-face and actual transverse-section rasters were
inspected and their hashes retained.

Original HB185 separately names M1586 cap beading and gives quantities that
differ from the SNL nested body/cap lists. The selected candidate follows the
SNL's eight M1585 strips, without silently merging or superimposing M1586.
SNL191 assigns five countersunk rivets per bead; its global total leaves only
twenty after other listed allocations, whereas the nested casing lists require
forty. Both conflicts are explicit in `casing_trim_sources.json`. The passing
native geometry does not resolve the historical inventory.

## Support brackets and selected casing inventory

The support candidate adds two M1587 and two M1588 brackets connecting casing
sides to the adjacent M1978 inner and M1976 outer wing plates. Its Z-section,
six-mm stock, station and hole patterns are inferred. Receiver planes come from
the retained native hull geometry. Seven case rivets per bracket follow the
direct SNL167 joint allocations, selecting 22 long body rivets including the
register plates, despite the nested body list's sixteen.

Two half-inch by 1-1/2 inch bolt/nut/lock-washer sets per bracket are an explicit
mounting hypothesis. SNL31:007 documents that standard type for other equipment;
it does **not** establish these casing joint allocations. The native definitions
record that distinction. The selected eighteen-mm grip leaves 7.6 mm nominal
bolt protrusion; threads, joint loads and tool access are not qualified.

The 809-leaf saved/reopened support fixture contains 56 added support/hardware
parts and four replacement drilled hull plates. All 920 new/changed material
pairs, 36 bores, 36 fastening seats, four bracket-to-case/hull contact checks
and eight simplified retention checks pass. Hull changes only remove material
and preserve outer bounds; the existing validator passes 77 plates and 1,037
material candidate pairs. Actual exterior and installation-crop rasters were
inspected and checksum-bound to the native model and report.

An independent saved-native ownership audit counts 300 selected casing
occurrences: 42 named components spanning all twelve selected SNL casing marks,
192 rivets and 22 three-part detachable fastener sets. This is the current
reconstruction schedule, **not a reconciled historical BOM**. The audit retains
the long/short/countersunk rivet conflicts, assumed support bolts, and HB M1586
alternative. The selected named-component counts match their source entries.

Next: reconcile and disposition source conflicts, add formed chain retention
and lubrication details, connect the transmission shaft, then integrate and
qualify the complete chain/casing installation under parameter changes. These
fixtures do not alter the standard model.
