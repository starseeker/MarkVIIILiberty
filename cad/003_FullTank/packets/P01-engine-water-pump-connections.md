# P01 — Water-pump hose connections and drain lock

This follows the [passage correction](P01-engine-water-pump-passage.md).
The development assembly contains **2,247 physical occurrences**, including
77 pump constituents in 29 definitions. It remains separate from the standard
tank; the complete engine and its integration are unfinished.

## Source-driven geometry and ownership

The original handbook nomenclature on printed page 191 supplies dimensions that
were missing from the earlier pump dossier. Its two 12075 outlet connections are
explicitly cast with the body: **1-3/8 inch OD, 0.065 inch wall, 1-7/8 inch length**.
The 12081 inlet is cast with cover 12435: **2 inch OD, 0.065 inch wall, 1-7/8 inch length**.
These convert to 34.925/50.8 mm outside diameters, 1.651 mm wall and 47.625 mm tube stock.
The three hose ends now retain those values. Named connections are integral
features of their host castings, not additional overlapping pieces. Native
properties and the [identity review](../experiments/drive_chains/engine_water_pump_connections_study/identity_review.json)
record the mapping. The material/manufacturing interface within the casting is unknown.

Outlet attachment stations remain estimates: a 68 mm cast branch, including a 4 mm transition,
followed by the complete printed tube. The inlet elbow retains an estimated 3 mm
casting wall before the thinner straight hose end. Bead shapes, volute, clocking
and the inlet's spline meridian remain source-informed approximations.

HB 191 also explicitly lists **two 8213 packing pieces**. This supports the selected
two-box arrangement in HB 100 and LIB 28. Later SNL 160 lists three pieces, and the
HB 100 8-1/2 inch versus SNL 131 11-9/16 inch replacement stock lengths remain recorded.
The model represents compressed annular packing envelopes, not reconstructed rope
winding. HB 191's 1-1/4 inch cover studs differ from SNL's selected 1-3/16 inch studs;
its printed 3/4 inch nut conflicts with the 1/4 inch stud. Those originals are
retained rather than silently corrected or averaged.

## Drain lock and construction references

SNL 161 and 276 specify one LQ167A/L209 soft-iron No. 18 wire, 10 inches long, for plug LQ145A.
The No. 18 diameter is 1.2065 mm: HB 191 explicitly prints 0.0475 inch for another No. 18
wire. The distinct lower-drive wire's 6 inch length is **not** transferred. NBS
Circular 31, edition 2 (1914), Table IV independently corroborates the gauge conversion;
its web text was checked, but the PDF download failed and no local PDF is claimed.

HB plate 139 shows a doubled drain-to-cover-fastening wire. The selected cross-hole,
180-degree loop around cover stud 6, return bends and five-turn tail are estimated.
The complete saved centreline retains 254 mm stock with no hidden offcut; its solved
tail height follows the rest of the route. Native construction geometry retains
that centreline separately from the physical BOM and STEP solids. This is a
static reconstruction, without simulated tension or a verified installation procedure.

The first swept prototype was a valid solid but its route crossed itself. The
independent centreline check found only 0.092 mm separation between nonadjacent
strands, below the 1.2065 mm diameter. The accepted route uses a gentler bridge and
passes independent strand, curvature, plug-wall and surrounding-part checks.
Tangent circular-arc fits retain the estimated helix and cubic Bezier references;
the round stock is built from cylinders and torus segments. Held-out reference
samples differ by less than 0.001 mm. The solid also passes detailed Boolean
geometry checking. These numerical fit limits do not imply historical certainty.

A separate export diagnostic found that the isolated probe omitted STEP surface
curves. Both files reopened as valid solids, but the export without PCURVE gave an
incorrect full-volume difference. Exporting the identical native BRep with
`Part.setStaticValue('write.surfacecurve.mode',1)` preserves 1,438 PCURVE records and
passes both material directions with no remaining faces. The production builder
already used this setting. [The paired replay](../experiments/drive_chains/engine_water_pump_connections_study/diagnostics/step_surface_curves/README.md)
and the FreeCAD skill retain the lesson; no acceptance tolerance was relaxed.

The revised inlet cover initially passed the native checks and its installed STEP
comparison, but failed the definition-frame material comparison. Replacing the
quarter-circle pipe sweep with explicit torus segments retains the same elbow
radii and endpoints and passes the focused export check. The saved assembly is
then rebuilt and qualified in both frames. This changes the surface construction,
not the printed hose dimensions or intended elbow form.

## Qualification

The saved [native assembly](../experiments/drive_chains/engine_water_pump_connections_study/DrivetrainWithWaterPump.FCStd)
passes all **59 native checks and 481 affected material comparisons**,
including full standard context, parent preservation, nine gear-mesh samples and
eight rotor angles. All **108 STEP comparisons pass** across definitions, installed
pump parts and the case in both frames. The ten-control trial also passes all
59 native checks, 482 context pairs and 108 STEP comparisons.

Only the body, inlet cover and drilled drain plug change from the preceding pump
checkpoint; 842 other serialized shapes and 42,249 checked existing assembly
properties remain identical. The wire definition/feature and nonphysical path
add three serialized shapes. Fresh nominal reproduction matches all
851 shapes and 53,393 checked properties.

Six [native views](../experiments/drive_chains/engine_water_pump_connections_study/source_review/index.html)
were inspected against the cited originals. Two new progression images record
the revised hose ends and wire detail, bringing the total to 139. All 137 earlier
images and 20 standard natives retain their hashes. The source camera is
unregistered; detail cuts and exploded offsets affect display only.

From this checkpoint’s commit, regenerate into a fresh work directory with:

```sh
python3 cad/003_FullTank/experiments/drive_chains/engine_water_pump_build.py --output .work/water-pump-rebuild
python3 cad/003_FullTank/experiments/drive_chains/check_engine_water_pump.py --candidate .work/water-pump-rebuild --preservation --standard-context
python3 cad/003_FullTank/experiments/drive_chains/check_engine_water_pump_exchange.py --candidate .work/water-pump-rebuild
python3 cad/003_FullTank/experiments/drive_chains/render_engine_water_pump.py --candidate .work/water-pump-rebuild
```

The default output is `engine_water_pump_connections_study`. Inputs expose 154
controls with individual evidence labels, 123 source records, 10 source pages and
12 hashed local assets. Geometry changes require regeneration; the native custom
properties are not live feature expressions. Use this checkpoint's commit and
frozen inputs when future builders advance.

## Remaining work

LQ151A shim terminology, LQ154A gasket placement and the retainer marking alternative
remain documented. Newly reviewed HB 191 also lists a lower-drive retaining-screw
washer and separate 6 inch wire; that preceding subassembly needs reconciliation.
Its rear-screw entry prints 3/4-16 x 3-1/4 inches beside a 3/8 inch washer,
whereas SNL206:010 supplies the selected 3/8 x 3-1/4 inch lower-drive screw. Preserve this additional
source discrepancy until that assembly is reviewed.
Commercial bearing internals, cast profiles and source-camera registration remain
estimates. These checks do not certify hydraulic performance or service paths.
Oil-pump geometry, remaining engine systems, global inventory reconciliation,
combined qualification and standard-tank integration remain open. Poses remain
deferred until standard geometry is populated.
