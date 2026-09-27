# Front clutch reconstruction — retained trials

The accepted selection is `linkage06`, with `linkage_variation06` and a fresh
`linkage_reproduction06`. Integration/qualification is recorded separately in
`linkage_integrated01`; earlier trials below are retained diagnostics.

| Trial | Disposition |
|---|---|
| linkage01 | Rejected:16mm M772 stock overlaps the unchanged13.2mm M569C fork gap by1742.23mm³. Catalogue row017 was also wrong; actual M772 row is116:015. |
| linkage02 | Fork clash removed by estimated12.7mm lever stock. Checker falsely compared native JSON-string SourceRecords to a list. Plan review found that a flat hand omitted the outward inclination. |
| linkage03 | Outward hand, solid M784 web, printed reaches and all local/context/STEP checks pass. The assumed140-degree projected hand/bell angle leaves an approximately58px fore-aft hand-tip discrepancy. Superseded after source review. The checker's missing import and original partial result are retained under diagnostics. |
| linkage04 | Source-informed122-degree angle preserves all real bell/rod pins and printed stock, but intersects actual hull_front_slope by14975.15mm³. Rejected; no STEP acceptance. |
| linkage05 |124-degree angle reduces plan-tip discrepancy to5.62px, but still intersects the nose by3673.49mm³. Nominal and thicker-link variants both reject it. Fresh reproduction is retained as unused preparation. |
| linkage06 |126-degree angle gives47.8465-degree hand elevation,13.5145mm nominal nose clearance and11.4791px plan-tip discrepancy. Nominal and13mm-web variants pass251 local checks,168 context pairs with no exemptions and69 STEP comparisons each. Fresh prototype reproduction passes. |

The [bounded angle probe](linkage_handle_angle_probe01.json) tests124–128 degrees
without moving the actual bell pin or driver foundation.125 degrees clears by
only1.8015mm;126 degrees is the selected provisional static compromise. These are
estimates of an unprinted lever form, not implemented operating poses. The source
registration is unchanged throughout. The discrepancy is diagnosed against the
physical nose; a camera refit would conceal the unresolved source/placement issue.

For future similarly bounded shape decisions, run the small receiving-interface
probe before rebuilding an entire prototype at every parameter value. The chosen
candidate still requires full saved-native/interface/context/STEP checks,
reproduction and explicit source review. A quick probe is not acceptance evidence
for the complete installed assembly.

All trials retain the four M784 source count and one shared definition. The chosen
three-eye form, depth, journal and web section are interpretations of overlapping
assembled figures. M772 retains the printed28½-inch radial hand reach and5-inch
bell reach; M789B retains12⅝-inch stock plus complete unchanged fork sockets.
M576 length is inferred, and its other four applications must be reconciled.

Absolute driver station and the source-like hand pose remain coupled to the
unfinished low-speed receivers and seat support. Later changes must preserve
printed rod/lever lengths and real joint stock. Review stronger source evidence
before fixing the station or claiming historical exactness.
