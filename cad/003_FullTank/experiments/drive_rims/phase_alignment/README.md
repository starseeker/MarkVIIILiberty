# Paired driving-rim phase regression

The first integrated wheel build flipped the inner ring about X. With an odd
number of teeth, this staggered its tooth reliefs by half a pitch. Axial reversal
about Z preserves the +Z relief phase, as required for the paired track channels.

The native checker rejects both the saved original staggering and a deliberate
one-degree error after correction. Both corrected sides pass by comparing the
actual cylindrical relief axes in XZ. The inspected `aligned.png` shows the
corrected ring relationship. Exact historical tooth profile and engagement remain
unqualified. The original native dependencies and result hashes are retained.

`executed_phase_check.py` records the exact executed diagnostic, including its
original temporary paths. It is an execution record, not a current launcher.
The permanent checker is `lib/wheel_validation.py:paired_rim_alignment`; current
build and parameter trials call it against their own saved native installations.
