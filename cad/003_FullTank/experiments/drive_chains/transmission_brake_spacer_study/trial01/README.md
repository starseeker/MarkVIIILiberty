# Brake adjusting-spring spacer development checkpoint

Four SH687A annuli and shorter installed springs populate the retained adjustment
mechanisms. [PowertrainWithBrakeSpacers.FCStd](PowertrainWithBrakeSpacers.FCStd)
contains **3,005 physical occurrences, 504 definitions and 295 assemblies**.
The two new/revised definitions and eight affected instances also have named
component STEP exports. Standard tank011 remains unchanged.

The 25.4 mm OD × 31.75 mm length × 13 mm bore and swivel-side position are
explicit approximations. SNL218/252 support identity, quantity and literal stock
notation; HB156 describes the spring stack without identifying the spacer.
The earlier estimated spring is shortened to keep screw/shoulder/swivel frames
fixed. Inherited brake-stop identity and transverse-layout limits remain open.

[Qualification](qualification.json) records passing results for 321 native checks,
28 development pairs, 502 preserved definitions, ten STEP comparisons, retained
standard context, exact fresh reproduction and length/bore sensitivity. The
[visual review](visual_review.json) retains the source-registration discrepancies.
These checks establish local static consistency; they do not establish historical
accuracy, strength or service removal.

All 13 stages of `tools/cad_pipeline/plans/brake_spacer_development.json` passed
in run `brake_spacer02`; read-only freshness verification also passed. The native
file hash is `9abdab05d466d51744002cce3dc442e27c1f02dd6266724821ca1f02f4e9b937`.
[Publication checks](publication_checks.json) verify every definition against its
native archive and prove that only BRep paths changed in the published manifest.
473 inherited payloads are reused from committed evidence; 31 new or normalized
payloads are copied here. Original receipt-bound manifest bytes are retained as
`pipeline_manifest.json`. Runtime files remain in `.work/cad-pipeline/brake_spacer02`.

[Parameter evidence](parameter_evidence/variation.json) preserves the actual
changed BReps and checker receipt. Its full varied native stays in the recorded
working path; it can be regenerated with the pipeline plan and parameter controls.

The [isometric](isometric.png), [detail](spacer_detail.png) and
[fixed-channel source overlay](spacer_source_overlay.png) are copied into the
visual progression. All 196 previous images remain unchanged: 199 total.
