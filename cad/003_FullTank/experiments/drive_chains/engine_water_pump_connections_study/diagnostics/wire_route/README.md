# Valid solid with a self-crossing route

The first sweep passed simple topology, stock-volume and surrounding-part checks,
but its nonadjacent centreline strands came within 0.092mm for 1.2065mm stock.
That route is retained as a failing control. The corrected source-length path
separates the strands and uses a gentler bridge; the native assembly checks its
actual saved path, physical round stock, curvature, fit residuals and plug support.
Run replay.py through the headless launcher in a fresh directory to repeat the
sampled crossing-versus-corrected check. This is not a substitute for the full
assembly or STEP checks. The route and attachment remain historical estimates.
