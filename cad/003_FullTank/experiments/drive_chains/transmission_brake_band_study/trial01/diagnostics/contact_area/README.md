# Cylindrical contact-area integration

Two complete track lining/drum contacts failed an equality of independently
integrated face areas: differences were 0.005319 and 0.003038 mm² out of
19,766.404 mm². Both analytic cylinder supports have zero axis/offset discrepancy;
face subtraction leaves no uncovered faces, and neither common-versus-original
difference contains faces. Translating the lining face 0.01 mm produces the
entire uncovered face, so the direct-coverage predicate rejects loss of contact.

The revised checker requires matching analytic supports, full axial containment,
and no uncovered face topology. It records the original and intersection area
estimates separately. No geometric tolerance or physical shape was changed.
All 154 revised native/context checks and 1,090 development material pairs pass.
The initial checker and failed report are retained here.
