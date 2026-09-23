# Initial STEP export discrepancy

The initial export/check ended with five failures: the bevel-washer definition
and its four installed occurrences. Boolean cuts returned no missing/added
material, but explicit OCC integration differed by approximately0.001182mm3.
The native washer agreed with the closed-form wedge-minus-bore integral.

Adaptive Gauss and Gauss-Kronrod integration, with requested accuracy from1e-10
to1e-14, converged to the same discrepant STEP result. Simply tightening numerical
integration did not correct it. Export tests isolated `write.surfacecurve.mode`:
mode0 reproduced the discrepancy; mode1 retained the surface trimming curves and
matched both native and analytical mass/centroid. No BRep tolerance was inflated.

The final exporter explicitly sets mode1, preserves the saved native document,
and writes a separate export receipt. All83 final exchange comparisons pass,
including closed-form checks for all five washer shapes. These retained initial
STEP files/receipts are diagnostics, not the accepted exchange artifacts.
The original helper scripts used temporary experiment paths; their exact logs
are retained here. The first diagnostic attempt imported Part before FreeCAD and
terminated; the retained corrected diagnostic initializes FreeCAD first.
