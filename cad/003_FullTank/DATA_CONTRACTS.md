# Current authored-record contracts

This describes the implemented F02 subset. The Python validation is in
lib/model.py and lib/parameters.py.

## Evidence and configuration

`configuration.json` holds the selected production baseline and explicit decisions
keyed by stable survey ID. Decisions retain source-record IDs, rationale and an
installed count where actually established. All other inventory rows remain
triage candidates. Source assertions are never summed into a vehicle BOM.

`model.json` records model revision, configuration, output units, scope limitations
and additive source locks. The inherited foundation lock verifies the frozen
survey and previously consumed sources. A changed hash stops the build.

Evidence locators use `record:`, `page:`, `calibration:` and `issue:`. The loader
checks source IDs/pages against the frozen database. Unknown or excluded survey
identities cannot silently enter a definition.

## Parameters

Each parameter records unit, value or expression, bounds in the declared unit,
evidence basis, applicability, references and interpretation. Units currently
supported are mm, in, deg, count, scalar, mm2 and mm3. Lengths resolve to mm.
Arithmetic tracks length and angle dimensions; addition requires matching
dimensions. Unknown names, cycles, executable expressions, nonfinite values,
fractional counts and blocked/out-of-bounds parameters fail.

Literal geometry coordinates use the units declared by their field. A parameter
expression must have the correct dimensions for that field. Bounds remain
reconstruction bounds; they are not machining tolerances.

## Frames and occurrences

Datums have a parent datum, translation and yaw/pitch/roll in degrees. A datum may
derive X/Z from a named conditional-metric calibration and image pixel, with Y
specified independently. Visual-only references cannot produce metric geometry.
The world frame is X forward, Y port, Z up, at ground level under the rear drive
axis.

An occurrence has a unique ID, owning parent, definition or group, and named
frame. Its frame resolves in the global datum hierarchy; the builder computes the
parent-relative placement for the native assembly. Defining a child in a world
datum and defining it relative to its mounting datum have different propagation
semantics. Use parented datums for interfaces that must move together; the current
source-traced installation frames predominantly refer to world.

Each definition has builder arguments, survey mappings, owning subsystem,
representation, coverage status, evidence and notes. Layout envelopes and finished
components are distinct. Current profile builders store longitudinal coordinates
in the model frame and reuse those profiles across transverse placements. As
parts become manufactured-component models, give each a local origin and
interface frame; do not rely on a generated face number for installation.

Assembly templates in `assemblies.json` contain physical leaf definitions and
nested assemblies. Identified track assemblies retain one reviewed survey
identity; convenience channel groups do not invent source identities. The
templates are independently compared against the frozen SNL composed-of edges.

`patterns.json` instantiates repeated templates under named installation frames.
Generated IDs include pattern, unit index and child path. Child translations and
pattern-step expressions remain symbolic until frame evaluation, so changing
pitch moves the nested pins and repeated units as well as rebuilding their parts.
Changing a pattern count requires reloading/expanding the authored records.
Parameter-perturbation validation checks the installed result independently.

A `closed_track` pattern resolves its generated `track_unit_index` datums through
`lib/track_path.py`. The solver uses the printed count and rigid chord pitch,
records its rounding/scale/ground adjustment and leaves the source-image
calibration fixed. Its reported pin-path residual is displacement from the
unscaled, rounded and inset construction curve, **not** distance to the scanned
outer silhouette. Closed pins do not establish wheel engagement or support fit.

A `roller_bank` pattern chooses plain, spring or upper templates from
`roller_stations.json`. Each generated `roller_station` datum retains its SNL2
source pixel, kind and picking uncertainty. `roller_geometry.stations` preserves
source X independently, applies any explicit `x_adjustment_parameter`, and computes installed Z from the native track's pin-segment capsule
envelope, fixed roller diameter and declared rail allowance. It reports source X/Z and both installation offsets separately. Lower00 uses a declared −45 mm X correction for idler clearance; its excess over the initial pick allowance remains documented. Track pitch and roller diameter changes
therefore move stations and the corresponding H01 shaft/roof openings; they do
not alter the source calibration. The source-station array and pattern count must
agree. Port pin/plug assemblies face outward; the distinct upper wheels are
mirrored within their own transverse stack.

`roller_component` definitions resolve native revolved sections, curved shoulder
profiles, helical springs and separate machined/fastener features. The
`roller_source_rows.json` role map identifies source records. Lower SNL totals
include the spring base assemblies and are checked separately from the two HB
upper stacks. HB237 supplies per-upper-stack quantities; M1410 remains a separate
plug identity from lower Q52C. Identified lower nested assemblies are also checked
against frozen SNL composition edges during model loading.

The roller validator checks six kind/hand template installations directly and
requires identical native definitions and relative transforms before reusing
those internal-contact results across repetitions. It still checks every external
and inter-station bounding-box candidate with exact BRep intersection, and all
120 roller-to-rail distances. Bounds explicitly disable display triangulation,
which can underestimate curved extents. Static clearance and stock-volume checks
do not qualify historical fits, absent support angles, spring loads or motion.

## Build and review artifacts

Louver installation datums carry `louver_bank` and optionally `blade_index` or
`packing_index`. Their resolver shares the H01 roof slope and aperture stations.
Blade definitions use true sloping length; their source count and exact section
bounds determine transverse pitch with an explicit edge allowance. The native
builder preserves a curved sketch/pad, including concentric circular bends.
`louver_source_rows.json` independently checks SNL identities and vehicle counts;
HB quantity alternatives remain issues. This partial subset does not establish
shared-spacer topology, attachment fit or completed cooling-system coverage.

The native document hierarchy is top-level assembly → linked subsystem document
→ optional groups → links to component-family libraries. Relative dependency paths
must survive relocation. Per-library caches include resolved geometry inputs,
definition metadata, CAD implementation hashes and runtime versions. The build
report locks all authored data/code and generated native files.
The input fingerprint includes the renderer's C source as well as Python and
authored JSON. The compiled library is a generated runtime cache.

Rendering tessellates native geometry for preview only. The SNL overlay projects
native edges through the recorded calibration without refitting. Comparison
findings are authored separately from generated images, so a geometric change
does not automatically count as a reviewed visual match.
The renderer tessellates each reusable native definition once and applies each
occurrence's rigid placement. Whole-vehicle preview filtering never changes the
physical native/STEP inventory.

Native placement validation compares translation and the three rotated unit
axes against independently resolved authored datums. It allows 0.000001 mm
translation and 0.00000001 basis-vector error, reporting the actual maxima.
Geometry validity is checked once per reused definition; rigid placements
preserve topology. STEP geometry uses separate volume/bounds checks. Starting a
new build removes stale exports and qualification reports so earlier results
cannot be mistaken for the current geometry.

Explicit fit/mate contracts, multiple selectable detail representations and final
physical BOM/clearance gates remain implementation work.

## Upper plate geometry

`upper_*` builders create individual native plate bodies with constrained section
sketches, pads and scripted BRep opening/joint trims. Their local coordinates use
the enclosing assembly datum: main shell base center, driver's rear base edge,
and lookout base center. Opposite hands can share a source identity while having
different reusable definition keys; quantity reconciliation counts identities
across those keys. No enclosure-sized solid is retained for the replaced shells.

HB35 dimensions and the fixed SNL2 calibration have independent roles. The main
shell size follows the print; its base center follows the trace. The difference
is computed and reported by `upper_validation`, never removed by image fitting.
Source-backed values can still be provisionally transferred to the production
configuration. `partial` coverage records missing fittings and uncertain forms.

`upper_validation` independently reads quantities for 21 SNL marks, checks their
26 installed plate occurrences, verifies HB43's distinct handed opening order,
tests candidate physical intersections and samples empty interior volumes and
armor thicknesses. A width-change qualification reopens a separately saved native
subsystem and verifies opposed flap shifts, wider roof halves and unchanged
lookout/driver geometry. These checks establish current CAD consistency, not
historical fit, complete upper-assembly composition or manufacturing readiness.

## Main hull plates

`hull_plate` definitions use a named role, handedness and (for floors) numbered
index. `hull_geometry.arguments` resolves the typed dimensional values and fixed
SNL2 calibration without loading FreeCAD. `hull_parts` builds a constrained
section/pad and explicit BRep trims. Role-specific seam picks and joint decisions
are preserved in code and H01; these parts remain partial while unlocated edge
forms and components are unresolved. The source quantity contract lives separately
in `data/hull_source_rows.json` and is included in the authored-input fingerprint.

All hull plate coordinates reference `hull_shell`, the established drive-axis X /
ground-Z frame. Their transverse face coordinates derive from track centers,
HB141 shell gap and local thickness. Broad floors extend to outer walls; forward
and fuel portions use the inner walls. Inner skirts continue under the broad
floor; they are not full-height walls through occupied compartments. Lower gap
and plate thickness remain independent controls.

The hull validator checks source-row ownership/quantities, candidate material
intersections within the hull and against upper/track components, sampled empty
cavities, the floor underside and sloped louver apertures. Its contact scope is
reported explicitly: a standalone HullStructure run cannot prove track clearance.
The whole-tank build supplies the physical track leaves for that check. It does
not treat unmodeled pieces, layout overlaps or mating gaps as completed interfaces.

The artificial +10 mm shell-gap test widens only its copied input bound. Both
facing planes must move by 5 mm in opposite directions, broad/narrow floor widths
must respond oppositely, and the independent upper enclosures remain unchanged.
The resulting native files are reopened before comparison. Historical printed
dimensions and source locks are unchanged by qualification trials.

## Standard sponson plate shells

`sponson_plate` resolves a role and explicit hand through `sponson_geometry`.
Its local frame is the front/bottom aperture corner, offset by the nominal
installation clearance. Local negative X points aft; Y is explicitly signed for
the hand. No mirrored assembly rotation or alternate pose is used. Overall shell
width follows `vehicle_width`; current aperture dimensions follow the unchanged
SNL2 calibration and hull transverse planes.

`sponson_parts` records the inferred plan fractions, floor rake and joint
ownership. All 39 bodies have one closed solid, native sketch/pad stock and BRep
trim features. Thirty-eight source-row quantity contracts are kept independently
in `data/sponson_source_rows.json`. Neither source quantities nor the stock-removal
guard proves historical contour or completeness. The M2764 hand and floor
thickness-scope decisions remain explicit issues.

The validator checks required and absent handed openings, normal thickness,
empty interiors, width and candidate contacts against all other modeled physical
leaves supplied to it. Standalone contact scope is explicitly empty outside the
sponson set. Roof-thickness qualification saves and reopens a separate subsystem,
requiring inward growth, fixed crown, shortened walls and unchanged floors.

Upper support angles remain inside the upper roller template. M2092 quantity four is checked against HB221 whole-vehicle nomenclature, independently of HB237 per-assembly roller quantities and SNL lower totals. `bearing_face` measures coplanar face intersections because OCC solid intersections discard zero-volume mating faces. Pin/toe and washer/flange contacts require both zero gap and nonzero area. Nearest-hull distances do not qualify an attachment. The support-stock trial preserves outside bounds and unrelated parts while increasing stock material.


## Idler wheels and explicit partial assemblies

`wheel_component` definitions use documented printed controls and inferred
profiles. `idler_station` datums retain the SNL2 source point while resolving a
local static displacement along the independently picked screw axis against the reconstructed track bushings. This numerical
fit is neither a historical travel range nor continuous engagement qualification.
`wheel_child` datums derive paired rim/disk/bush locations, diaphragm orientations
and rivet placements at evaluation time, so diameter and joint-stock parameters
propagate through both geometry and nested links.

Identified assembly templates normally reconcile every leaf with the frozen SNL
BOM. A deliberately incomplete template must declare `composition_status: partial`
and positive integer `omitted_source_counts`; modeled plus omitted identities
must equal the complete source composition. The report preserves modeled and
omitted counts and explicitly marks `complete: false`. The idler shaft now accounts for all nine source leaves. A negative test removes
the shaft and requires an explicit partial/omitted record before accepting that
template. The rotating-wheel template independently accounts for 119 leaves.

Wheel validation checks both installed hands, all broad-phase candidate material
pairs, native rim/bushing and foremost-roller distances, controlled dimensions,
source-stock rivet volumes and representative head-to-joint face contacts.
The full qualification includes an idler diameter perturbation and checks its
placement dependency during the existing track-pitch trial. Source alias candidates
remain explicit and do not create duplicate physical occurrences or rewrite survey
identities. X/Y diaphragms keep distinct definitions despite their unresolved
geometric difference.


## Idler adjustment installation

`idler_component` and `idler_child` expose the fixed bracket frame and moving
shaft frame separately. `idler_geometry.axis` uses two retained SNL2 picks;
`wheel_geometry.station` solves only translation along that axis. Wheel radial
orientation stays vertical, while the shaft and support local X axes follow the
inclined adjustment line. Source datums are not refitted to the track.

The `idler_source_rows` manifest scopes separately catalogued adjuster hardware;
whole-vehicle counts are checked against source quantities, and ten outer-plate
rivets are checked against the two explicit five-rivet applications. Shared Q52C
parts are counted by installation ID, not by their `roller_plug` definition name.
The same rule scopes wheel definitions for future reuse in the drive assemblies.

`idler_parts.hull_tools` owns the fixed neck/head windows and fastening bores.
`idler_validation` measures bearing faces and curved copper/screw contact using
actual installed native shapes. The +2 mm shaft-length trial requires the oil
plugs to move 1 mm outward at each end and locking screws to lengthen; the
brackets, wheel and unrelated components must remain unchanged. These tests do
not qualify missing inner attachments, threads, adjustment travel or load paths.

## Lower support runs and hull receivers

`lower_support_runs` defines station ownership, handed source marks, installation
scope and attachment count. `lower_support_source_rows` retains the fourteen
angle identities and one bolt identity. Whole-vehicle quantities and each
angle's bolt allocation are checked against the frozen source records.
Reflected construction variants can share a source identity without asserting
historical interchangeability. Their occurrences live under `PortLowerSupports`
and `StarboardLowerSupports`, outside the existing roller-stack count scope.

Named run datums follow installed roller stations. The first three runs rotate
the complete paired roller frames. The two printed inner No.5 lengths remain
fixed when track pitch changes. Separate `lower_support_thickness` owns lower
stock; it does not inherit the upper support's stock parameter. Bolt seats and
receiving hull holes follow the same datum calculation. Original source picks
remain independent of installed geometry.

The receiving plane uses `hull_frame_clear/2 + hull_skirt_thickness`. Each
attachment requires native bolt-head/angle contact and cylindrical hull contact
equivalent to at least the full skirt thickness. An angle touching a hull plate
elsewhere on its length cannot substitute for a bolt's receiving wall. These
checks establish contact geometry only; threads and structural capacity remain
unqualified. Analytic planes are retained for bearing-face checks; reflected
variants use explicit extrusion direction rather than a general geometry
transform that converts planes into spline surfaces.

The initial SNL hull polygon is retained as `hull_initial_layout`. Reviewed
front-border pixels, their uncertainty and the inferred middle transition are
recorded separately. `hull_nose_clearance_setback` changes only the installed
foremost vertex; it does not change the pixel pick or calibration.
