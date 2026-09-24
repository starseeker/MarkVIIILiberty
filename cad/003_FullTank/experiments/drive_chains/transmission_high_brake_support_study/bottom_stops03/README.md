# Anchor retention and bottom stops

This increment adds two physical M363 pins and their source-sized cotters,
two M366 bottom stops, two MX77 locking plates, four MX76 mounting screws,
and four M400 set screws with four separate nuts. The integrated development
[native file](../integrated_bottom01/PowertrainWithHighBrakeBottomStops.FCStd)
has **3,149 physical occurrences /539 definitions /332 assemblies**. The eight
new groups include the catalogue pin and screw/nut assemblies; those aggregate
identities are not counted as additional physical parts.

The retained M362 fork gains a lower mounting shelf with two transverse receiving
pads and connecting ribs. HB154 expressly attaches the bottom stop to this bracket.
The transverse bolt pitch, cast section and shelf form remain estimates. The first
15.875 mm branch intersected an existing lining-rivet tail by 21.223617 mm³ on each
side. The proposed branch was narrowed to 9.525 mm; the printed rivet stock and
retained bracket material remain intact. The failed trial and its collision
diagnostic are retained in `../bottom_stops01`.

SNL137:004 supplies the cotter's 3/16 × 2-inch stock. Existing cotters with the same
catalogue identity were formed around 17.5 mm nut crowns. This joint surrounds
a 7.9375 mm pin radius, so it uses a separate installed form of that identity,
with the existing analytic cylinder/torus construction. Two round legs and
overlapping eye leads approximate a manufactured split pin. Each under-eye
developed leg is 50.8 mm; the historical length datum and exact stock volume are
not claimed. Pin dimensions and outboard head side are estimates.

The MX76 nominal half-inch size follows the catalogue washer application;
M400's nominal 3/8-inch size follows its listed nut. Unprinted screw lengths,
head forms, plate thickness and the 0.25 mm stop approach allowance are explicit
controls in [stop_controls.json](../stop_controls.json). Threads use nominal
envelopes. HB133's common MX77 plate remains distinct from the later SNL lock-washer
alternative. Each M400 position is adjusted against the actual retained band/eye
material without changing the camera, drum or band geometry.

The fixed [HB133 comparison](bottom_stop_source.png) led to shorter stop ends and
revised screw stations after `bottom_stops02`. The current strip and mounting
region agree more closely with the illustration. Screw adjustment, cast silhouette,
pin head form and hidden depth still have residuals and uncertain interpretation.
The image is a sectional illustration with local depth conventions, not a recovered
photographic perspective. The saved registration remains unchanged.

| Evidence | Result |
|---|---|
| [Prototype material](report.json) | Retained M362 material preserved, additions bounded to proposed stock, all 142 nearby material pairs pass. |
| [Saved interfaces](independent_checks.json) | All 75 checks pass: actual pin/bore axes, head and cotter retention, source cotter envelope/developed lengths, positive mounting contacts, blind passages/back stock, and bounded stop approach. |
| [STEP](exchange_checks.json) | All 30 strict definition/installed comparisons pass with unchanged material, tolerance and mass-convergence criteria. |
| [1 mm stock variation](../bottom_variation01/independent_checks.json) | All 75 checks and [30 STEP comparisons](../bottom_variation01/exchange_checks.json) pass. Locking plate, mounting heads, receiving depths and jam nuts follow the thicker M366 stock. |
| [Integration](../integrated_bottom01/independent_checks.json) | All 35 checks pass for actual saved counts, hierarchy, inherited frames and material/pose transfer from the prototype. |
| [Preservation](../integrated_bottom01/definition_preservation_checks.json) | All 531 unchanged inherited definitions compared independently; the changed M362 and seven new definitions are covered by the prototype transfer. |
| [Tank context](../integrated_bottom01/standard_context_checks.json) | All 22 affected occurrences lie clear of the conservative bounds of 5,316 retained tank occurrences. Zero nearby material pairs; no Boolean comparison was required. |
| [Fresh nominal build](../integrated_bottom01/reproduction_checks.json) | All six comparisons pass, including all 1,649 archive BReps and 149,329 persistent properties. |

## Service limits

The initial [service probe](pin_service_probe.json) fails for an 80 mm withdrawal
envelope and 100 mm straight drift approach: they encounter the outer plain case
and central bevel case. These lengths were diagnostic assumptions, not source
requirements. The [minimum-travel probe](service_minimum/pin_service_probe.json)
passes all 12 nearby pairs for a 57.65 mm withdrawal (the full 57.15 mm pin length
plus 0.5 mm clearance) and a 25 mm drift approach.

Both probes remove the cotter and bottom-stop assembly first and consider selected
epicyclic/frame/brake material after removal of the gear unit from the tank, as the
handbook states. They do not verify tool handling, straightening the cotter, gear
extraction or the complete service sequence. The failed larger envelopes remain
useful constraints; they are not silently relabeled as passing.

## Preview correction

The original `bottom_stop_isometric.png` is a rejected preview. Its caller shared
a tessellation key while supplying different world-posed targets, causing repeated
parts to be drawn at the first instance's location. Native geometry, source overlay
and all STEP occurrences were correctly placed. The separate saved-native renderer
now supplies one identity-frame target per shared definition and composes each
occurrence's placement. Use the inspected
[corrected isometric](bottom_stop_isometric_reviewed.png) and
[detail](bottom_stop_detail.png). The [diagnostic](diagnostics/render_cache.json)
retains both implementations and image hashes; no CAD or camera fit changed.

Top/back stops M399/M398, clips M365, their upper mounting hardware and remaining
two M400/nut pairs are next. Full support-packet qualification, inherited receiver
variation STEP, control rods and standard-tank promotion remain open. The last
fully qualified parent is still the operating-mechanism checkpoint; tank011
and all previous progression images remain unchanged.
