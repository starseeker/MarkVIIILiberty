# Rear high-speed control joints

The current [native assembly](PowertrainWithUSControlNuts.FCStd) contains3,173
physical occurrences,546 definitions and338 assembly groups. Two M569B forks,
two M568A pins, two split pins and two plain U.S. Standard nuts populate the rear
high-speed brake connections. The fork/pin/cotter definitions are shared between
sides; the larger nut has its own reusable definition. Existing geometry is
preserved. This is a locally checked static reconstruction, not a complete rod
assembly or a historically proven manufacturing model.

The [qualification](qualification.json) binds native, STEP, source, preservation
and fresh-build evidence. The initial joint work passes42 saved checks,18 material
pairs,12 STEP comparisons, and a+0.5mm ear-stock variation. Its integration passes
17 checks and preserves542 inherited definitions. A later nut revision follows
the catalogue's U.S. Standard wording; see the [source review](../us_standard_nut_review.json)
and [period table](https://www.gutenberg.org/files/23319/23319-h/23319-h.htm).
The table describes forged/unfinished nuts, so applicability of its outside
profile remains an interpretation. No blanket revision of older hardware is made.

The new nut checks cover source dimensions, all-link native relocation, source
identity, actual fork seating, material interference and the thicker-ear
variation. Both final installed nuts and their shared definition pass strict
STEP round trips. The full assembly reproduces its native shapes, frames,
hierarchy and persistent properties in a fresh build. The earlier successful
small-nut model is retained in integrated01 as a superseded geometry hypothesis.

The [assembled brake view](high_brake_assembly_isometric.png) shows168 brake
occurrences with drums in outline. Standard tank011 remains unchanged. The
[main packet](../README.md) records fork/pin datum alternatives, projection limits
and the next work: M4128 rear channel, spring/bracket stations and complete rods.

Generation is two explicit steps: build_transmission_control_joints.py adds the
qualified fork/pin/cotter prototype, then revise_transmission_control_nuts.py
assigns the source-led nut definition. Earlier native inputs and validation
scripts are frozen or hash-bound. Source dimensions, fit allowances and hidden
profiles remain separate. Reproduce with the repository headless launcher and
absolute input/output arguments. Do not replace the standard assembly until
its broader integration gates pass.
