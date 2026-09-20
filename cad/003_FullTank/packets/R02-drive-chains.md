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

Next: reconcile and disposition source conflicts, connect the transmission
shaft, then integrate and
qualify the complete chain/casing installation under parameter changes. These
fixtures do not alter the standard model.

## Formed chain retention and link oil passages

Original HB24 directs lubrication through holes in the links, and HB134 requires
the holes on top and cotters outboard. Neither supplies hole size or count. The
selected candidate adds a 3.175 mm passage from the outward edge to each pin bore
in each bar. The upper straight run faces upward; the lower return follows the
rotating link orientation. This is an explicit continuous-loop interpretation.

The HB132 split pins retain their 44.45 mm nominal leg centerline length. Tails
bend beyond the pin surface with an inferred six-mm radius and 50-degree splay.
The two-round-leg section and eye remain proxies. Splaying their initially
overlapping sections increases modeled volume by 0.672616 mm³ per cotter;
exact material conservation and forming mechanics are not claimed.

`chain_detail_build/ChainDetailCandidate.FCStd` preserves 809 saved/reopened,
valid single-solid leaves. Its 100 changed cotters pass 274 new material
candidate pairs without overlap, 100 cotter capture checks and 100 pin retention
checks. Unformed cotters do not provide the same tail extraction stop. The 200
drilled bars pass 400 oil-to-journal path checks and 200 orientation checks; four
undrilled controls block the passages. These are static geometric tests.

Five native rasters were inspected and their hashes retained in the external
visual review. The joint overview section cuts obliquely across the oil holes,
so `inspect_chain_oil_sections.py` adds separate inner/outer bar-aligned sections
from the unchanged saved native file. They show the passages reaching the pin
clearance. Lubrication performance, strength, historical fit, source inventory
reconciliation and standard-model integration remain incomplete.

## Transmission output rotors and casing clearance

HB122 identifies M289 as the sprocket output shaft (callout 10), M292 as its track
brake drum (callout 7), and M291 as the chain sprocket (callout 6). SNL215:028 and
SNL83:036 each specify two installed pieces. M255 is a separate central cross
shaft; it is not the shaft carrying the chain sprocket. SNL165:013 separately
allocates four M290 retaining rings to M289 and two to M267.

`transmission_output_calibration.json` uses the M291 hub's printed 101.6 mm width
across pixels 292–432 in SNL Plate22. The separate 38.1 mm tooth-width check
measures 37.737 mm on that scale. Axial/radial scan distortion remains; the drum
extent midpoint is six pixels from the selected shaft axis. The roughly 589 mm
shaft length and 607 mm drum diameter are scaled estimates, not printed dimensions.
The existing approximate ten-groove sprocket bore is retained; the corresponding
shaft section, journals and drum casting transitions remain assumptions.

The first 813-leaf native fixture adds four rotor parts. All four spline
interfaces have 0.1 mm minimum flank gap and resist a two-degree virtual twist;
unsplined cores do not. Both drum/sprocket hubs meet axially. Forty material
candidate pairs reveal two drum/casing overlaps of 23,938.321999 mm³ each. The
failed installation, exact inputs and four inspected rasters—including the
native section over the unchanged source—remain preserved.

`casing_front_build` retains those rotors and narrows the casing symmetrically
between inferred stations X1450–1515 mm to 132 mm outside width. HB134's 168.275 mm
width is interpreted as the maximum, retained behind the taper. The three-mm
sheet uses a normal offset through the taper, and a 79 mm hub passage clears the
77 mm inferred brake hub. The rear region through X1440 mm has zero symmetric
material difference, preserving its existing attachments and drilled joints.

All 813 reopened solids remain valid. The 764 changed/new material pairs have no
overlap, eight normal sheet-thickness checks measure 3 mm, and minimum drum/case
and chain/sprocket/case distances are 2 mm on both sides. The actual oblique and
shaft-height section were inspected. This qualifies the selected static fit;
it does not establish the original casing contour. Shaft bearings, M290 rings,
axial capture, planet disks, brake bands and full-model qualification remain.


## Output bearing sleeves, dowels and shaft retention

Original SNL44 identifies two M296 inside bushes and two M299 outside bushes,
each with one M300 bronze dowel, 5/8 inch diameter by 1/2 inch long. Original
SNL165 allocates four M290 rings to the two output shafts. HB208 Plate123 places
M290 at both ends of the output shaft, corroborating two ring stations per side.
The candidate uses common C-ring geometry at those stations; its section, radial
gap, groove depth and fit remain assumptions.

`transmission_bush_build/TransmissionBushCandidate.FCStd` adds twelve physical
parts, for 825 saved/reopened valid single solids. Sleeve axial dimensions follow
the existing conditional Plate22 scale. Their radii, flanges and dowel drilling
remain inferred. The M289 shaft changes remove material only: two grooves and
two blind radial pockets per shaft. Sleeve holes open radially for dowel insertion.
All 811 other existing occurrences retain their original geometry signatures.

The native candidate passes 26 new/changed material pairs without overlap, four
0.1 mm sleeve/journal clearances, four dowel capture checks and four ring capture
checks. Dowels have 0.05 mm nominal radial clearance; a three-degree sleeve twist
or three-mm axial displacement meets the installed dowel. Ungrooved shafts reject
the rings, undrilled shafts reject the dowels, and omitting the dowel removes the
tested torque stop. Each ring has 0.15 mm minimum groove clearance and meets the
shaft walls under both one-mm axial displacement witnesses. These tests do not
qualify assembly procedures, load capacity or a continuous motion range.

An independent fresh-native check confirms zero material difference throughout
the four retained sprocket/drum engagement regions. All spline clearances and
twist-capture checks still pass. The entire axial stack is not yet qualified:
planet disks, washers, fixed supports and their receivers remain unpopulated.
Three actual rasters, including an axial section and source overlay, were inspected;
`visual_review.json` binds those images to the native and verification reports.

SNL309 note(gq) requires a poured babbitt lining in the fixed brackets/caps after
alignment. This supports treating the separately listed M296/M299 parts as
shaft-mounted sleeves; the selected radial dowel interface remains a hypothesis.
Do not mistake these sleeves for the still-missing fixed housing lining. Original
HB207 calls M296 outside, whereas SNL44 explicitly calls it inside; the candidate
follows SNL44 and the sectional placement while preserving that conflict.

The next fixed-support study must also disposition HB209's separately listed
M392/M393/M395/M396 brasses and M394/M397 shims against SNL309's poured material.
Original SNL42 implies four M391 foot assemblies in the two outside brackets,
while SNL95 and HB209 list two feet globally. Both counts are retained. SNL56's
four bearing caps each include an oil-box cover, sleeve, pipe elbow, elbow nut
and steel pin; its two ounces of wool per cap is a material quantity. The
[source research](../experiments/drive_chains/transmission_support_research.json)
records these inspected pages and avoids prematurely selecting overlapping
bearing parts or silently resolving the foot conflict.

The qualified standard tank remains milestone011. This installation fixture and
its passing checks do not yet add chain/transmission geometry to that delivery.

## Fixed bearing castings and frame-interface trial

`transmission_support_clearance_build/TransmissionSupportCandidate.FCStd` adds
two M293 inside brackets, two M297 outside brackets, two M294 inside caps, two
M298 outside caps, four M295 lids and eight poured babbitt half regions. The
twenty new solids give 845 valid single-solid leaves after save/reopen. All 825
prior occurrence signatures are unchanged. The eight in-situ regions have no
fabricated catalogue identity and do not duplicate HB209's unresolved brasses.

HB20/21 shows the cup openings facing upward on forward-facing caps. HB125/127,
HB204 and SNL Plates2/23 put the supporting frame aft of the transverse shaft.
Fixed bearing placements therefore keep +Z up and feet toward -X on both sides,
independent of the rotating shaft's phase. The Plate22 axial overlay retains the
existing four-inch hub calibration. Web and cup profiles remain simplified;
the provisional 170-mm bracket depth does not establish a frame connection.

Four local bearing checks pass: 0.15-mm sleeve/lining clearance, flange capture
under both one-mm axial witnesses, 0.1-mm cap split, contacting lining seats,
and 0.15-mm lid clearance. All twenty additions survive STEP export/reimport.
These are selected static interface checks, not a parameter or historical-fit
qualification. Studs, hinge pins, pipe fittings and oil passages remain pending.

The overall installation **does not pass**. Seventy new-material candidate pairs
expose four interferences: each outer bracket crosses the chain-case sheet by
17,983.219434 mm³ and one wall-angle rivet by 2.392474 mm³. Earlier lid/cap
intersections and touching seat edges are preserved in the first two native
trials. The latest flat seat and perimeter clearance correct those lid issues.
Six latest rasters were actually inspected, including a display of the common
material and a source overlay; `visual_review.json` binds them to the artifacts.

The next work is the transmission frame skeleton: separate M373/M374 channels,
M375 diaphragm, M376/M377/M378 angles and M380/M382/M383/M384 gussets. Original
SNL96/97 rows and inspected-file hashes are in `transmission_frame_research.json`.
Use those members and the source side sections to constrain bracket vertical
shape and casing clearance together. HB134 documents chain-link cutaways in
gussets and requires casing installation before the gear, but does not establish
a bearing-foot hole through the casing wall. Neither such a hole nor a smaller
source footprint is assumed merely to eliminate the current clashes.

### Transmission frame trial and bracket revision

`transmission_frame_clearance_build` now contains separate M373/M374 channels,
M375 diaphragm, M376/M377/M378 angles and M380/M382/M383/M384 gussets: fifteen
occurrences from ten shared definitions. Four existing bearing brackets have
tapered webs and upper/lower mounting pads; their bearing saddles are unchanged.
The native file reopens with 860 valid single-solid leaves and unchanged geometry
for the other 841 prior occurrences. Nineteen new/changed solids pass STEP reopening.

The initial frame intersects the floor, wall rivets and its own rear stems in
nineteen places. The revision moves the bottom web up three source pixels,
reduces channel depth from 160 to 148 mm within the rear-face pick allowance, and
moves outer angles to the frame ends. Now 126 new/changed material pairs have no
overlap; 34 frame/support contact or explicitly expected gap checks pass. All five
native/source rasters were inspected and their hashes recorded. Plate 22's broad
foot is interpreted as projected pads, not falsely shown as shaft-height material.
That interpretation, cast profiles and the middle diaphragm's form remain uncertain.

The nominal outer bracket/casing clearance is 0.236090 mm. Independent sensitivity
checks expose collisions at an 18-mm corner radius or with the 2.5-mm rear inset
removed. Restoring the original channel depth or lower-web pick also collides.
These expected failures demonstrate sensitivity; they do not qualify the uncertain
parameter ranges. Four saved bearing interfaces still pass. The inner pads' 5.806-mm
channel gap is unresolved. SNL131 identifies fiber packers M386/M387, but main
quantity six conflicts with HB209's eight, and receiver/thickness are unknown.

Frame attachment and central bevel case clearance remain incomplete. Finish cap
hardware and oil fittings, then reconstruct the central case and actual mounting
receivers before accepting the complete assembly. No new standard snapshot is
issued for these isolated partial candidates.

### Oil-cover hinge geometry

The closed standard candidate now includes four SNL56 steel pins (3/16 × 2½ in),
plus integral hinge knuckles on the existing M294/M298 caps and M295 covers.
Original HB20 Plate11 shows the rear hinge; segment lengths, radius and position
are estimates. The initial 4.5-mm axis height intersects each cup rim by
100.461820 mm³. Raising that inferred axis to 6 mm preserves the pin dimensions
and gives a clear joint. Both native trials and exact inputs are retained.

The revised `transmission_lid_clearance_build` reopens with 864 valid solids;
four pins are new, eight cap/cover occurrences change, and 852 prior occurrences
remain unchanged. Thirty material candidate pairs have no overlap. All four
hinges have 0.15-mm pin/bore and cap/lid clearance. One-mm radial shifts and
undrilled receivers correctly collide with the pins. Existing cap/lining seats
and 0.1-mm bracket splits remain intact. Twelve new/changed solids survive STEP
reopening. Pin axial retention and cover motion remain unqualified.

The close source/native comparison makes remaining differences visible: the cup
and cap cast transitions are still square/simplified, and cap nuts, oil inlet,
fittings and wool are missing. The handbook's lid is open; the native lid stays
closed, and these perspective images are not used as a dimensional registration.
The original large source comparison has SVG clipping defects; the separate
`hinge_review` images provide the corrected readable comparison.

An early pin-diameter assertion used a display-mesh bounding box that understated
the true cylinder. The revised verifier checks analytic radius, volume and clean
axial bounds. Collision filtering removes triangulation caches. An independent
cleaned-bounds check of the earlier frame/bracket candidate confirms 126 material
pairs with no overlap; its unqualified attachment and uncertainty remain unchanged.

Next fastening inventory is now source-bound in `transmission_stud_research.json`:
eight MX9 (3⅝ in), four MX10 (4⅞ in), four MX36 (5½ in), all
3/4-inch nominal diameter; each has one SAE castle nut and one 1/8 × 1⅜-inch split
pin. The nested bracket rows identify stud assemblies, while SNL241 identifies
the physical rods separately. Both inside stud lengths need a documented corner
allocation and suitable receiving bosses; do not shorten rods to fit provisional
ear depths. Thread forms, nut dimensions and detailed retention remain pending.

### Cap studs, castle nuts and split pins

`transmission_stud_clearance_build` adds 48 physical occurrences: eight MX9,
four MX10, four MX36, sixteen SAE castle nuts and sixteen split pins. Each
three-part fastener set belongs to a fixed bearing. Five shared definitions use
the physical SNL241 identities; assembly metadata preserves the nested stud-set
records. None of this hardware follows the output-shaft rotation.

The shortest printed stud, the stated 38.1-mm US thread end, a 2-mm assumed
thread recess and estimated nut stack derive a common cap seat at local X29.7
and stud tip at X51.925. The MX9/MX10/MX36 tails lie at X−40.15/−71.9/−87.775.
Integral rear bosses accommodate these full lengths; pilot bottoms have 0.3-mm
clearance and 4-mm estimated end stock. Existing cap ears are spotfaced to the
seat. The opposite SAE thread-end length is recorded as 28.575 mm. Actual
threads remain smooth envelopes with no flank or axial-thread retention claim.

The inferred nut has 28.575-mm flats, 19.05-mm height and six crown slots.
Split pins use the printed 3.175-mm nominal envelope and 34.925-mm leg length,
with the latter interpreted as the under-eye centerline length before bending.
Their twin round legs, approximate eyes and splayed tails are shape proxies;
they do not reproduce half-round stock or conserve exact original material
volume. The two port outer cotter eyes initially intersected the casing by
0.328169 mm³ each. Port pins now rotate 180 degrees about the stud axis, so eyes
point outboard on both hands. This direction is a clearance-based assumption.

The final native document has 912 valid single-solid leaves: 48 new hardware
occurrences, eight changed bracket/cap castings and 856 unchanged earlier
occurrences. The 56 new/changed solids survive STEP reopening. Cleaned BRep
bounds select 262 material pairs with no overlap. All sixteen fastening checks
pass: nut seat contact, 0.15-mm nut/stud and cotter/hole gaps, blind-end clearance
and at least 2-mm radial casting wall around the full US thread region.
Diagnostic stud shifts, undrilled studs, nut rotation and two-sided cotter
shifts produce expected interference. Four retained lining/split/cover/hinge
checks also pass. These checks establish the specified static geometry only.

The current inner allocation puts MX36 above MX10. The independent allocation
study reverses them, preserving four of each source length; its 41 material
pairs also clear. Geometric feasibility therefore does not establish historical
corner placement. Both candidates retain the source schedule and explicitly
unqualified thread, casting and frame assumptions.

Four native overview/detail rasters and three supplementary cap/source rasters
were inspected. HB20 Plate11 shows an open lid; the modeled standard lid remains
closed. The source comparison is unregistered perspective, not a dimensional
overlay. Cap-only views omit the bracket to expose the full rods; installed
views show their receiving bosses. Cast blends, rounded cup corners, the oil
inlet/fittings and wool are still missing. The first failed native, exact inputs,
reports and four rasters remain in `transmission_stud_build`.

### Oil-fitting source inventory

Original SNL56 lists one SH664A elbow, SH664B nut and SH664C sleeve per cap.
SNL86 identifies the elbow as Herring Motor Co. No.69F, and SNL126 identifies
the nut as No.61F; both standalone totals are four. The sleeve is No.60F.
SNL67 separately lists brass quarter-inch collet A16323, vehicle quantity
twelve, with M298 and SH664A among its applications. Its survey identity differs
from SH664C; their possible terminology overlap remains unresolved. Do not
silently merge them or stack both in the same receiving seat.

`transmission_oil_fitting_research.json` records those inspected rows and scan
hashes. The quarter-inch nominal label alone does not establish actual tube
diameter, bore, seat, taper or thread form. Reconstruct the inlet and oil routes
against section evidence, then complete frame receivers/fasteners and the
central transmission before integration. Standard milestone011 remains intact,
including both opaque and transparent isometric snapshots.
