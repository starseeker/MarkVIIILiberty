# S01 — standard sponson plate shells

Status: active, partial plate population. Both sponsons remain in the standard
outboard position. No pose variants are implemented. This record follows the
[source preparation](S01-sponson-research.md) and supplements [S01](S01.md).

## Native component scope

Thirty-nine individual native plate solids replace two layout occurrences of the
old sponson block. They represent the 38 listed marks in the source preparation
table, with M2738 used once per side. The hierarchy is Sponsons / SponsonPort or
SponsonStarboard / individual plate links. Definitions use local coordinates:
X is negative aft from the front aperture edge, Y is explicitly handed outward,
and Z is up. Both child installation datums remain unrotated.

Each native body has a constrained planar source-section sketch, a pad and a
scripted opening/joint-trim feature. Regeneration uses the authored data and
builders; manual upstream pad edits do not automatically regenerate the Boolean
trims. All definitions remain `assembly / partial`.

The plate scope includes upright wings, sides and back pieces; roof; inner floor;
two lower sloping pieces; and separate top/bottom shield infill segments. The
front/outboard bay is deliberately open for the separate rotating shield and
mount. The horizontal infill interpretation is provisional. Neither the bay nor
its strips are a reconstructed working gun mount.

## Controls and inferred geometry

HB35 controls side armor 12 mm, roof 6 mm, floor 8 mm and shield infills 8 mm.
The separately printed forward 12 mm / aft 6 mm floor values are provisionally
assigned to M2740B/A and M2749/M2741 respectively. This thickness-scope mapping
remains unresolved, even though normal thickness is checked on the native parts.

The current H01 aperture bounds supply longitudinal length and height, with a
1 mm nominal clearance at each end and in the vertical direction. The inboard
plane is 1 mm outside the hull wall. This yields plate-frame length
1,685.558 mm, height 1,005.806 mm and outward depth 650.575 mm. The outer faces
meet the handbook's 3,657.6 mm whole-vehicle width. Interpreting that width as the
sponson shell envelope is an explicit installation assumption.

The plan is a six-vertex faceted reconstruction informed by SNL7, not a measured
orthographic trace. In aft/outward coordinates (u,v), normalized by length L and
depth D, its perimeter is (0,0), (0,0.32D), (0.22L,D), (0.80L,D),
(L,0.48D), (L,0). The inboard face stays open. The inner floor extends to 0.25D;
the lower skin then rises 200 mm toward the outside. Its forward/aft seam is
at 0.62L. Front hinge and wing strips divide at 0.10D; the outboard gun bay ends
at 0.52L. Back side and inner return divide at 0.14D. These fractions are all
reconstruction choices and remain visible in the builder.

The open bay begins 320 mm above the datum and ends 110 mm below the crown.
Shield infill strips extend 65 mm inward. The side and front bands end against
those strips. Joint ownership is explicit: floors, roof, walls, then infills.
Butt/miter cuts remove positive-volume intersections; shapes with more than
40 percent stock removal are rejected. This guard does not establish historical
joint design. Angles, laps, straps, fasteners and exact formed contours remain
separate work.

HB43 and SNL cover allocations give seven peep openings and five ordinary pistol
openings across the two shells. Their sizes provisionally reuse the earlier
107.95 × 25.4 mm and 88.9 × 63.5 mm opening controls; centers use 0.74H and 0.49H.
They are placed in the explicitly identified handed wings, sides and backplates.
Special revolver assemblies, port covers and periscope/roof details are pending.

## Source conflicts retained

M2764 is assigned to the right upper intermediate infill following SNL154:003.
The left upper front infill spans two of the three reconstructed strip segments.
HB227 instead groups M2764 with the port parts. This is a provisional preference
for the later SNL in the working configuration, not proof of a historical change.
Both source assignments remain recorded.

The original HB227 scan was also inspected on the right half of
`references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII114.jpg`.
It confirms both the port grouping and the M2832 roller-bracket spelling, against
the SNL's M2382. Its SHA-256 is
`f6575962d2d527c7d73dfc8e8f842e83e5b3c6cc671dde853779cea73c886e96`.
This supplemental scan inspection confirms the locked restored handbook text;
the raw scan hash is recorded here separately from the build's source lock.
No disputed roller bracket geometry is assigned in this increment.

## Verification and remaining components

Source quantities are independently read from 38 SNL records, including source
identity ownership. Removing one handed roof is rejected by the record test.
The native validator checks exact material intersections among sponson plates and
all other modeled physical components, whole-vehicle width, six hollow/entry
probes, twelve required opening probes, four checks for absent mirrored openings,
and twelve normal-thickness samples. The standalone assembly passes 97 candidate
material pairs with zero overlap.

Standalone native validity/placement, STEP round trip, relocated links, independent
reopened rebuild and cache reuse pass. A +1 mm roof-thickness trial thickens
inward, holds the crown fixed, shortens the adjoining side plates and leaves the
floors unchanged; nominal and changed shells both pass the plate checks.
The clean/cached standalone builds took 3.42 / 1.91 seconds, excluding the other
qualification work. Seventeen record/renderer tests pass. Integrated qualification
also passes native shapes and all 3,125 placements, both STEP round trips,
relocation, independent reopened rebuild, cache reuse and all five parameter
trials. Nominal and changed-pitch tracks clear the sponson shells. The full native
rebuild/cache times were 31.88 / 26.32 seconds. The generated full-tank reports
retain the checks and their limits; complete-tank and historical-fit verification
remain false.

Remaining work includes curved/recessed shield interfaces, actual rotating
shields and mount representations, hinges and rear attachment, curved floor
rails and support rollers/brackets, angles and butt straps, roof/periscope
pressings and covers, viewing/pistol covers, seats, stowage, fittings and
fasteners. Hollow shells and correct subset counts do not close those components.
