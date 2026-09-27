# Driver foot and reverse controls — source review underway

Continue from the qualified [coupled station](../coupled_driver_integration/README.md).
This packet begins the next geometry work with **44 selected catalogue rows**,
their complete enclosing pages, 31 source views and nine actual retained native
interface frames. It does not add or qualify physical geometry yet.

The directly inspected original pages establish several construction constraints:

- HB148 describes neutral-selective braking through the speed-selector linkage.
  M771 connecting members must connect the pedal mechanism to those selectors;
  two independent permanent pedal-to-rod drives would omit the described function.
- SNL71 lists eight M771 members, one M764A pedal, one M765 bridle, one M766
  distance piece, two M769 links, one M770 suspension link, one M795 sleeve,
  SH98B/SH98C clips and SH98D spring. Exact joint topology remains to be traced.
- SNL193 has five M576 applications: high speed two, foot brake two, clutch one.
  Three already exist in the parent. The two foot applications must use the
  shared unprinted stock length, currently1298.281517mm, or revise the whole
  family through a documented coupled solve.
- SNL86 lists two SH946F fork ends, one for each of two M576 rods. Its M569C row
  assigns two ends to each of only three M576 rods. Assigning F to the foot pair
  follows the application inventory and existing high/clutch construction;
  the row does not explicitly say “foot.” Do not add an unlisted second M569C
  to each foot rod before resolving its connection to M769.
- SNL23 gives M767 with an M7687/8-inch crown nut and a3/16×1-1/2-inch cotter.
  The adjacent M776 handle-bolt assembly instead uses a1-inch cotter. M767 bolt
  length is not printed there. SNL136 assigns M568A to M771 and prints1-5/8inch;
  the older front-control composed-of list says1-7/8inch. Retain the existing
  specific-part-row interpretation and the source conflict.
- HB150 prints reverse hand reach27.968in (710.3872mm), bell arm6in (152.4mm)
  and reverse rod52in (1320.8mm), made from extra-strong nominal3/4-inch pipe.
  The rod length datum and front/center/rear attribution require reconciliation;
  nominal pipe size is not its outside diameter. SNL195 separates M571 front and
  M566 center, with M570 forks and pipe-lock nuts.
- Original SNL118 actually prints **M177** for the reverse operating lever,
  drawing214. This is not merely a transcription error. Existing figure-family
  M777 interpretation must remain an explicit identity discrepancy; do not
  silently alter the source record. Its composed-of row also lists the trigger,
  spring, guide, pawl, pins and two5/16×1-3/4-inch rivets.

[The source review](source_review.json) records inspected images and open issues.
The first evidence pass used the broad prefix SH98, which also selected unrelated
SH980/SH981/SH984 entries. `evidence02` uses token boundaries and explicit SH98B/C/D;
`evidence01` is retained as superseded search provenance, not the construction list.

Next trace the local foot-brake connectivity and source picks on SNL6/HB113,
using the saved local registrations and actual shaft/selector receiver geometry.
Build the bridle/suspension and M771 chain as one connected static prototype;
then close the two M576 rods with the correct ends. Review all printed stock,
contact, holes, full-context interference and exchange before integrating.
The reverse lever/quadrant and complete M571 route follow. Keep current M574 and
SH229A printed stock intact. Whole-length fitting across broken schematic rods,
or a perspective fit to these schematic views, would not supply valid dimensions.
