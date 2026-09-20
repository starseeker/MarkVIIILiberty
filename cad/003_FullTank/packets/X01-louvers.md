# X01 — standard engine-roof louver population

Status: active, partial reconstruction, 20 September 2026. This is the exterior
louver subset of X01 and preparation for I04; neither packet is accepted or
complete. The user has prioritized standard geometry before pose work.
See [source preparation and original scan hashes](X01-louvers-research.md).

## Source identities and installed scope

The CoolingVentilation hierarchy now owns LouverInlet and LouverOutlet groups,
with 82 individual solid links from 19 native definitions and 18 survey identities.
Radiator and fan installation envelopes remain separate layout geometry.

| Component | Inlet | Outlet | Installed total |
|---|---|---|---|
| Bent blade | M987 × 34 | M994 × 28 | 62 |
| Tall side frame/guard | M983 port, M982 starboard | M2108 port, M990 starboard | 4 |
| Low port side plate | — | M989 | 1 |
| Front/rear end frame | M984 / M985 | M992 / M991 | 4 |
| Port cover strip | M986 | M993 | 2 |
| Front/rear retaining plate | M995A / printed `995B` | M988 × 2 | 4 |
| Packing plates | M1000 × 2 | M1000 × 2 | 4 |
| Port packing strip | M1005 | — | 1 |

The raw `995B` identity is preserved, with its survey ID, rather than inventing an
M995B record. M988 uses separate front/rear definitions with the same survey
identity; M1000 uses one reusable definition for all four placements. Source
quantities are independently read from the selected original SNL records through
`data/louver_source_rows.json`, including ownership checks against the survey.

Working blade counts follow SNL18:015–016. The handbook alternatives are retained:
HB40 34/29, HB233/235 39/29. M997's SNL allocation is 68 inlet/54 outlet, compared
with HB66/56. A common total of 122 does not resolve the distribution or topology.
Neither count conflict is silently corrected.

## Placement and editable geometry

The installation resolver shares H01's sloping engine-roof plane and aperture
stations. Its slope is 11.504461 degrees. Printed aperture lengths remain global
X projections: 655.955 / 955.675 mm. True roof-plane lengths are
669.403873 / 975.268954 mm. Each blade is set back 16 mm from both end planes,
giving true extrusion lengths 637.403873 / 943.268954 mm. The two bank datums use
an explicit 2 mm roof-normal installation gap. All parts remain in the standard
installed configuration.

SNL4's top-view photograph supports lengthwise blades repeated transversely.
It does not establish the section or bend-radius reference. The native section
is provisionally a sideways 90-degree chevron, with 6 mm normal armor stock,
12.7 mm inside bend radius and a 63.5 mm total roof-normal extent. These map
HB40's printed thickness, radius and outside width to an explicit interpretation.
The bend uses concentric exact circular arcs (outside radius 18.7 mm) tangent to
the straight legs. It is a sketch and pad, not a tessellated mesh. Changing the
authored thickness regenerates the arcs, tangent legs and repeated placements.

The blade group has 30 mm transverse edge allowance on both sides of the
946.15 mm aperture. Actual section bounds and source counts give pitches
25.997065 mm inlet and 31.774191 mm outlet. This unequal pitch is a reconstruction
result, not a printed dimension. The shared M997 distance-piece geometry and
contacts have not been reconciled with it. Empty spaces and visually plausible
blades do not prove the historical clamping or support arrangement.

The guards use HB41's 6 mm stock and 222.25 mm vertical projection above the
installed roof datum, excluding the 2 mm normal installation gap. Mapping that
height to M982/M983 and M990/M2108 is provisional. Outward top lips are 31.75 mm
wide, with square inner bends pending source detail. M989 remains a separate low
port outlet plate. Rear deflector channels are separate, unpopulated identities.

The following unprinted dimensions are explicit reconstruction choices, in the
bank's roof-plane coordinates:

- End frames are 6 mm thick and 90 mm high; the low M989 side plate is 90 mm high.
- Blade section lies between normal heights 20 and 83.5 mm.
- Retaining strips occupy 6–12 mm from each end, between heights 14 and 20 mm.
- Cover strips are 14 mm wide, 6 mm thick, 16 mm short of both ends, at height 92 mm.
- Four M1000 packing plates are 40 × 14 × 6 mm, at the cover-strip ends and height 86 mm.
- M1005 is a 14 mm wide, 2 mm thick strip at height 84 mm under the inlet cover.

These pieces have native sketches and pads. Exact attachment holes, tapers,
formed bends, screws, supports and joints remain unresolved. There is no claim
that the currently separate solids form a mechanically secured louver cassette.

## Verification and remaining work

The standalone nominal checks pass all 82 source component quantities, 183
candidate exact material intersections with zero overlap, both native blade
sections (normal stock, radii, width and true length), 60 local void probes and
four guard-projection checks. The void probes check geometric openings only.
They do not simulate airflow or qualify protection. The complete integrated
validator also considers every other reconstructed physical component; layout
envelopes remain excluded from claims of physical fit.

A record test rejects adding a 29th outlet blade to this SNL-based configuration.
The saved-native qualification includes STEP round trips, relocation, independent
reopened rebuild, unchanged cache reuse and a +0.5 mm blade-thickness trial.
These checks pass in both the standalone and integrated deliveries. The full
assembly passes all 181 definition shapes and 3,207 installed placements, six
parameter trials and 194 nominal louver contact pairs, including 11 external
pairs. Independent native rebuild/cache times are 1.13 / 0.98 s standalone and
32.38 / 28.04 s full, excluding other qualification work. Delivery hashes match
all 43 standalone and 99 full files. See PROGRESS and the generated reports.

Remaining louver components include M997 distance pieces, M998 end packings,
M996 saddles, M999 securing cleats, fishplates, clamps/set screws and other
fasteners. Rear channels M2110/M2111, M2109/M2112 packing and M2116 deflector need
their own rear-roof geometry. Radiator, fans/drives, ducts and connections remain
I04 work. Current blades, frames and packing shapes are all partial coverage;
complete-louver, full-tank and historical-fit verification remain false.
