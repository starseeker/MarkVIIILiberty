# Coupled driver station integrated — 27 September 2026

The [saved development assembly](integrated01/PowertrainControlRebuild.FCStd)
now contains the reviewed bow, driver controls and supported seat in the retained
powertrain hierarchy: **3,712 physical occurrences, 689 definitions and 456
assembly groups**. Standard tank011 itself remains unchanged.

- [Whole tank context, hull outlined](integrated01/visual01/isometric.png).
- [Complete development assembly](integrated01/visual01/development.png).
- [Driver station](integrated01/visual01/station_isometric.png).
- [Exposed support connections](integrated01/visual01/station_connections.png).
- [Fixed source section](integrated01/visual01/station_source_section.png).
- [Conditional clutch profile](integrated01/visual01/station_clutch_source_comparison.png).

Relative to operating_integrated01, the union adds **92 seat/support parts** and
**38 bow/enclosure context panels**, with 54 new definitions. It revises 17 existing
definitions and 226 occurrence frames. The other 618 definitions and every
inherited occurrence owner and assembly frame are preserved. New bow and seat
groups retain separate structure, attachments, stays and floor mounts. All uses
of each changed shared definition are covered by the reviewed prototype.

Intermediate trial copies had omitted reconstruction-status and regeneration
notes. The integration plan restores full native metadata from the original bow,
seat and support packets, then overlays later reviewed revisions. In particular,
the corrected SH289E bearing bore note supersedes the earlier seat estimate.
Eight current rod centerlines and ten seat construction sections are retained in
nonphysical groups outside the assembly/BOM; all 13 inherited guides survive.

The independent checks verify the actual saved document, its relocated internal
links, all composed frames, group membership, full metadata and persistent parent
properties. There are **743 canonical material comparisons**, including 55 strict
comparisons where BRep serialization differs. Reviewed definition material plus
identical installed frames transfers the existing 1,174-pair full-context audit
without adding mating exemptions. The 8,987-part context contains one replacement
for each matching standard bow/floor occurrence. Local stock/contact, variation
and strict delta STEP qualifications remain bound to their original artifacts;
this integration does not claim a new whole-tank STEP export.

A fresh full rebuild reproduces **2,135 archived BReps and 184,974 persistent
properties**. The first exact-byte guide checks flagged native location records
and vertex-coordinate bookkeeping. Complete world-space analytic/B-spline
signatures, trim intervals, vertices and topology match within 1e-9 mm; translated,
altered-pole and clipped-interval negative controls fail. No geometry was changed
to resolve that diagnostic. Both initial failures and the resolution are retained
in [the diagnostic record](integrated01/diagnostics/guide_serialization01/README.md).
The resulting integration has 108 passing checks and 31 passing guide comparisons.

Two newly inspected overview images and four previously inspected local/source
views bring accepted visual progression to **314 images**. No source camera was
refitted. Tentative shaft identities, handle length datum, delayed-set M772 profile,
seat curves, plate margins and angle/bolt patterns remain explicit approximations.
SH291C/D/F fittings remain unresolved; foot/reverse controls are the next packet.
No historical pose, force, motion or service qualification is implied.

Verify the frozen checkpoint with:

```sh
python3 cad/003_FullTank/experiments/drive_chains/verify_control_rebuild_checkpoint.py \
  --candidate cad/003_FullTank/experiments/drive_chains/coupled_driver_integration/integrated01
```

Rebuild with `integrate_coupled_driver_station.py --plan PLAN --output NEW_PATH`
through the qualified headless launcher, using absolute paths and the saved
`plan01/plan.json`. Extract with `pump_integration_worker.py extract`. The first
integration checker preserves the exact-byte diagnostic; the guide-geometry
checker and V2 aggregation resolve it without rerunning unaffected solid checks.
The qualification receipt binds the source chains, workers, native files, views,
standard archive and fresh reproduction.
