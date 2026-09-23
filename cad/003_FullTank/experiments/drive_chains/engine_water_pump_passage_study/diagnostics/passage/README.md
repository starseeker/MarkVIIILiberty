# Drain-stock interference and correction

The retained prior nominal and trial body BReps both intersect intended fluid
volume near the drain. Only the prior trial intersects the smaller 5 mm-radius
outlet centerline gauge. Both corrected bodies clear the complete local fluid
region and both centerline gauges. No material is added or removed outside the
intended fluid volume within the drain-stock region.

original_probe.py records the initial live-document experiment. replay_passage.py
uses the frozen builder inputs and retained prior bodies, so it does not require
the old trial's .work native document. Run it through the project's headless
FreeCAD launcher with a fresh work directory. replay_checks.json records its run.

previous.png and corrected.png use the same display-only X=153..153.5 mm slab
and orthographic camera around the lower chamber and drain. They illustrate an
internal casting correction; the historical cavity profile remains estimated.
This is not a new full-tank isometric milestone. All 137 earlier progression images
are preserved. Full saved-assembly and STEP acceptance is recorded at the parent
candidate and in ../parameter_trial.
