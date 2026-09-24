# SH687A transmission brake adjusting-spring spacers

Source/interface preparation for four missing components; no new geometry yet.
Original SNL218 confirms SH687A, quantity four, and the literal notation
`W. I., 1″ x 1¼″`. SNL252's transcribed transmission composition also lists four.
The two printed numbers have not yet been assigned to diameter, length or nominal
stock size. HB101/134 show the screw/spring/swivel arrangement without a resolved
SH687A callout. [sources.json](sources.json) retains those distinctions.

The saved trial04 geometry contains four adjusting springs, each approximately
112.823802 mm long, ending at the swivel's central seat to numerical tolerance.
The independent [context audit](context.json) checks the actual saved BReps and
frames. There is no empty axial gap to populate by simply adding a spacer. A
reviewed spacer placement will require changing the currently estimated spring
and/or shoulder arrangement, followed by interface and parameter checks.

The first diagnostic used ordinary `BoundBox` values. On this trimmed B-spline
spring, those broad bounds overestimate the axial extent; the swivel's side
journals also extend below its central seat. The retained current measurement
uses `optimalBoundingBox(False, False)` and restricts the swivel search to the
spring-radius cylinder. It is an axial occupancy check, not proof of complete
annular contact. The initial broad-bounds diagnostic remains in
`.work/brake-spacer/initial_broad_bounds.json` and must not be interpreted as a
physical clash or spring length.

Next inspect the original composition/context and any additional adjuster views,
choose and document a defensible stock/placement hypothesis, then build the four
owned occurrences and revise affected estimated spring geometry. Use the staged
runner with explicitly declared dependencies. No source-camera refit or change to
the existing standard assembly is warranted by this inventory discovery.
