# Experimental brake-stop assembly — trial02

**Not accepted or STEP-qualified.** This candidate extends the qualified
front-brake checkpoint with 44 components. See the
[work packet](../../../../packets/P01-transmission-brake-stops.md) for sources,
assumptions, the mounting discrepancy and remaining acceptance work.

- [Native assembly](PowertrainWithBrakeStops.FCStd): 3,001 physical occurrences,
  503 definitions and 295 assembly containers.
- [Isometric](isometric.png), [support detail](support_detail.png),
  [HB134 overlay](lowspeed_source_overlay.png), [HB135 overlay](track_source_overlay.png).
- [Saved-native diagnostics](trial_diagnostics.json): eleven valid closed solid
  definitions, 57 passing count/frame checks, zero detected interferences in
  492 candidate pairs, and eighteen positive planar contacts.
- [Source comparison](source_comparison.json): the support mounting remains
  appreciably above and behind the source picks under the retained registration.

The 44 components are four lugs, twelve lug rivets, eight screws, eight nuts,
two bars, two brackets and eight bar rivets. Four lower bands use new drilled
definitions. Two existing stud/nut/cotter sets move forward by 6.35 mm.
No backing above the shaft is intentionally changed. The shared crossbar and
bearing-cap attachment are explicit hypotheses, not demonstrated factory details.

Trial01 remains a rejected fit experiment with ten recorded interferences.
Trial02 resolves those clashes through the estimated bracket-eye profile and
bar-rivet spacing. This does not qualify source identity, mount retention,
unaffected geometry, full standard context, STEP, rebuild or parameter behavior.

From the repository root, regenerate into a **new** output directory:

```bash
python3 skills/freecad-reconstruction/scripts/freecad_headless.py \
  --workdir .work/transmission-brake-stops \
  cad/003_FullTank/experiments/drive_chains/build_transmission_brake_stops.py \
  --output /absolute/path/to/new-trial
```

Then extract the saved document with `pump_integration_worker.py extract`, run
`inspect_transmission_brake_stop_trial.py --candidate /absolute/path/to/new-trial`
and `render_transmission_brake_stops.py` with the same argument through the
headless launcher. Run `compare_transmission_brake_stops.py` with system Python.
The builder freezes its selected inputs. Its current input freeze is narrower
than the final qualification receipt required for an accepted checkpoint.
