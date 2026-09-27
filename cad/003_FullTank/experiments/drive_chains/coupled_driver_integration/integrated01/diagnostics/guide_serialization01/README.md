# Native curve serialization diagnostic

The initial checker required identical BRep bytes for copied guides. All 18 new
guides and two inherited guides serialized differently after a native save.
Physical material, hierarchy, metadata and fresh reproduction already passed.

The retained probe shows extra native Locations records and vertex-coordinate
bookkeeping while composed placements and lengths remain unchanged. The complete
curve checker compares all31 guides' world-space analytic definitions or full
B-spline poles/weights/knots, trim intervals, vertices, topology and tolerances.
All pass within1e-9mm. A0.01mm translation of every guide fails, as do an altered
spline pole and a changed trim interval. This is a geometric equivalence proof,
not acceptance based only on matching lengths or sparse sample points.

The native model was not edited. V2 combines the bound, passing physical checks
from the initial report with this complete curve audit. Original failed reports
and the inspection log remain here. The extra small diagnostic does not repeat
the already-completed solid comparisons.
