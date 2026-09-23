# Coupled parameter trial

Ten controls vary together: packing length, spring length, shim thickness, rear
body flange, mounting angle, outlet angle, cast branch length and derived tip,
wire joint station and bridge handle. Printed hose stock, wire length/diameter,
stud dimensions and all acceptance thresholds remain unchanged. The exact
nominal/trial values are in controls.json/trial_changes. Both saved-artifact and
STEP checks include the revised case and full standard context.

The trial's large native/STEP artifacts remain in .work/engine-water-pump-lock/variant;
these receipts retain their hashes. Recreate with the checkpoint builder using
--controls pointing to controls.json here and --output to a fresh directory.
