# Low-selector topology, trials and remaining interfaces

The new source review replaces the earlier provisional curved M762. Following
HB113's leaders shows that the bowed outline below the main shaft belongs to the
M765 foot-brake bridle. M762 runs diagonally between the upper M790 joint and the
rear M761 knee. The [source close-up](selector_source_views01/hb113_joint_detail.png)
and [recorded pick](selector_landmarks01.json) retain the evidence. The preceding
low02 files and qualification remain unchanged as historical CAD evidence; their
M762 topology and unfinished lower front point are superseded.

The selected SNL convention is M756 left/port, M757 right/starboard. HB190 reverses
these names. The two geometries have inward-facing selector jaws; this naming
choice does not establish an undocumented manufacturing revision. HB93 is a
pictorial shape reference, not an orthographic dimensional drawing. No camera was
refitted to obtain agreement. The existing SNL6 and HB113 local registrations are
reused; the upper-joint pick is construction evidence, not a holdout.

| Trial | Disposition |
| --- | --- |
| selector01 | Rejected before native saving: the reused strut helper returns a web centered on local Y=0, while the M762 eyes are at Y=-16.35. Explicitly translating the web into the eye plane restores one connected solid. Failed helper and log retained in selector_diagnostics01/untranslated_web. |
| selector02 | Intermediate nominal build, not accepted. The common web parameter also controlled the bell-eye web. Before testing the thicker variant, bell-eye stock was fixed to its independent 12.7 mm interface dimension. The exact earlier helper is frozen in selector_diagnostics01/nominal_before_stock_split. |
| selector03 | Nominal 12.7 mm upper web; complete diagonal link, selector jaws, pins and cotters. Local, context, exchange and fresh-prototype checks pass. |
| selector_variation03 | 13 mm upper web with unchanged bearing and bell-eye interfaces; the same checks pass without relaxed limits. |
| selector_reproduction03 | Fresh nominal prototype reproduces actual BReps, all occurrence frames and stable persistent properties. |

Only the shared M762 definition changes. Its citations are narrowed to the actual
SNL row and HB113 detail supporting this revision; identity is unchanged. All
existing world frames, shaft stations, M761 knee stacks, SH220A washers, clutch
geometry and complete M574 rods remain fixed. Six new components are the two
handed selectors and two M790 pin/cotter sets. The third source M790 application
remains unbuilt and must be located during foot-brake reconstruction; it is not
counted here.

Dimensions and axial stack remain reconstruction estimates. M762 has 10 mm stock,
28 mm web width, 50 mm eye OD and 19.25 mm bores. The selected upper connection is
90 mm aft and 92 mm above the main shaft. M790 uses estimated 19.05 mm diameter,
31.75 mm under-head length and a real transverse cotter bore. Both keepers retain
the source 3/16 × 1¼ inch stock. Selector journal width, profiles, gate dimensions,
oil holes and static inclination are unprinted approximations.

Next complete the high-speed selectors and their M789A short connections, then
reconcile their M576 long rods with the same part's other applications. SNL194
lists three M789A assemblies, each with 10⅝ inch stock: the reverse short
connection is also required. Continue the operating handles/fulcrums, gates and
stops, brake interconnection, spring anchors, axial spacing, reverse controls and
complete seat support. Neither this static fit nor source-pick agreement proves
historical pose, hand clearance or motion.
