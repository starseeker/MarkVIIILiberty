# Rejected trials and resolved numerical discrepancy

Initial assembly: six bearing contacts with nuts/pins. A radius14mm spotface
cleared four nuts but retained two small cotter contacts. Radius18mm clears the
formed pins while retaining the saved-CAD journal-support witness.

First native build: all148 affected material pairs were clear. Four expected
nut gaps incorrectly used0.15mm instead of the reused nut's0.10mm. The upper
lever's sphere/cylinder fusion also yielded a STEP tolerance increase and
centroid discrepancy despite zero Boolean differences. A single revolved
neck/ball profile preserves the same nominal geometry and exports cleanly.
The focused numerical diagnostic records its independent adaptive mass results.

The initial generator's case-difference diagnostic used its unrefined Boolean
intermediate and incorrectly returned almost the entire old case as removed.
Reopening the refined saved BRep gave local removal2804.773mm3. Generation no
longer reports that intermediate difference; the independent checker bounds the
saved case additions/removals spatially. Default volume integration itself has
small numerical variation; no native tolerances were enlarged to conceal it.

Exact first-native inputs and failed report are retained here. The first native
file remains in .work/transmission-vertical-controls-study/rejected_first_native;
the qualified candidate is separate. Initial trial scripts use their original
study-relative paths and are evidence snapshots, not entry-point commands here.
