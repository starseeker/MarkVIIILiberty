# High selectors and complete rod connections

The high01 nominal prototype adds M759 port and M758 starboard selectors, two
M789A short rods, two M576 long rods and eight complete clevis/pin/cotter/nut
joints. The 38 additions use three new definitions. Every inherited definition
and world frame remains fixed.

The [source review](high_source_review01.json) binds catalogue rows and directly
reviewed figures. SNL194 prints 10⅝ inches for M789A stock, with three installed
assemblies. Two are used here; the reverse short connection remains required.
SNL86 explicitly associates M569C forks with M789A. SNL117 and HB190 agree on the
high-selector handed names, unlike the preceding low-selector naming conflict.

The printed 269.875 mm stock plus the retained pair of 25.4 mm fork offsets
requires a 320.675 mm pin span. The HB113 lower main-side pin pick [321,391],
under the unchanged local registration, instead implies 351.381447 mm. The
selected lower eye is the nearest point to that pick satisfying the complete
stock constraint: **43.073828 mm aft and 160.345287 mm below the main shaft**.
See [layout calculation](high_layout01.json).

The **13.525126 px discrepancy exceeds the 4 px pick allowance**. It remains an
open source disagreement. Selector pose, the estimated two-shaft separation,
fork insertion/length interpretation, or the assembled illustration may need
revision. A collision-free assembly does not settle that question. Neither local
source registration is refitted. Native bore measurements reproduce the recorded
residual, and the source overlay states it explicitly.

Both high long connections have the same receiving span as the existing clutch
M576. They therefore reuse the exact same definition and complete 1296.850963 mm
inferred stock. Three of five M576 applications are now populated. The two foot
applications must confirm or reopen that shared family geometry.

Selector stock, journal, profile and gate remain estimates. The high jaws occupy
radii 140..210 mm with 41 mm outward lips; the retained low jaws occupy the higher
radial interval. Actual operating handles and their engagement remain unfinished.
Nominal 12.7 mm and variant 13 mm upper webs retain independent 12.7 mm bell-eye
stock and all mating interfaces. Each passes 432 local checks, 75 context pairs
without exemptions and 41 strict STEP comparisons. Fresh nominal rebuilding
reproduces saved materials, frames and stable properties.

The first section display accidentally omitted PortHighDriverSwingLink because
its name differs from the PortDriverHigh prefix. The renderer, receipt and image
are retained in high_diagnostics01/section_filter. Adding that existing receiver
to the display yields a complete linkage section; native geometry is unchanged.
All five final views have been inspected.

Next reconstruct the actual M746/M747 operating-lever fulcrums and M738A/M738B
37-inch operating handles, including their pivot hardware and real selector
engagement. Continue triggers, separate control gates/stops, brake interconnection,
spring anchors, axial spacing, reverse lever/rods and full seat support. The
remaining reverse M789A and M571 connection and two foot M576 applications remain
explicit open work. Static fit does not qualify motion, access or historical pose.
