# Repeated pump rendering — 24 September 2026

The old renderer generated all three views inside its selected-occurrence loading
loop. The saved model contains 242 selected occurrences, so it issued 726 view
renders, repeatedly replacing incomplete intermediate images. Its final render
receipt and successful terminal result are retained here; intermediate images
were not accepted as completed reviews.

The revised renderer collects the same 242 shapes first and produces each of
the three views once. A separate `--output` path preserves the old outputs during
verification. Its receipt names only the three intended PNGs, rather than any
unrelated image in the output folder.

The revised process returned exit 0. **All three final PNGs are byte-identical**
to the old process's terminal outputs. The native model is unchanged. This is a
render-control-flow correction, not acceptance or promotion of the obsolete
pump-registration geometry. No new progression milestone is recorded for it.

`before_renderer.py` and `before_receipt.json` retain the old implementation and
final image hashes. `after_receipt.json`, `terminal_status.json` and
`comparison.json` record the successful replacement. The regenerated images stay
in `.work/pump-render-loop/result/`; the original terminal images remain beside
the candidate native. Run the current `render_engine_pumps_integration.py`
through the headless launcher with `--candidate <assembly_trial02>` and
`--output <fresh-directory>` to reproduce the corrected path. Do not rerun the
old repeated-render implementation just to reproduce the final images.
