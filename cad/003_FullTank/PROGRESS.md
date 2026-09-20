# Full-tank implementation progress

Current user priority: **fully populate the standard assembled configuration,
including identifiable interiors, before implementing any pose variants**.
The pose research remains preparation for later work.
At each significant visual improvement, retain the standard isometric as the
next `cad/intermediate_snapshot_iso_NNN.png` and update
[the visual progression](../VISUAL_PROGRESSION.md). User-saved 001 and 002 are
preserved; 003 records the sponson shells, 004 the roof louvers and 005 the roller
stacks; 006 records the separate idler-wheel internals, 007 the shafts and adjusters,
008 the lower support runs, 009 the driving wheels and 010 their shafts and bearings.

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
formed chain retention, lubrication and transmission interfaces remain before
integration and parameter qualification. See the
[chain/casing packet](packets/R02-drive-chains.md) and
[native support detail](experiments/drive_chains/casing_support_build/casing_support_detail.png).

## 20 September 2026 — experimental full-tank roller-pinion integration

An isolated source branch, `experiment/roller-pinions`, now builds both
98-part pinion installations in the complete standard assembly. It has 252
definitions and 5,341 leaves, including 5,326 physical components and 216
represented physical source identities. Nominal native checks and 37
record/renderer tests pass. The detailed source comparison views have been
inspected. This has **not** been promoted to the main delivery; its full
29-stage validation with 17 parameter trials remains in progress.

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
