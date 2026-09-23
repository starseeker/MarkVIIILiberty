# Same elbow geometry, explicit quarter torus

The revised thin-wall inlet cover passed saved-native checks and installed STEP,
but its definition-frame STEP material comparison failed. Omitting optional
cleanup did not resolve it. Explicit quarter-torus primitives replace only the
circular elbow sweep, keeping its radii, endpoints and printed straight tube.
Both material differences between old/new natives are empty. Accurate integrated
volumes differ by about 2.42e-8mm3 and centroids by 2.93e-7mm, within the recorded
kernel precision. Do not infer a physical change from their less accurate default
Volume estimates. The new export passes strict comparison in the focused probe;
full definition/installed acceptance is recorded in the parent checkpoint.
Run replay.py via the project headless launcher in a fresh directory.
