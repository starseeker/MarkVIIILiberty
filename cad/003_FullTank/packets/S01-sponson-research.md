# S01 — standard sponson geometry preparation

Research preparation, 19 September 2026. The subsequent
[39-plate implementation](S01-sponsons.md) replaces the layout envelopes in the
standard configuration. This record preserves its source preparation and open
questions; it is not a complete sponson BOM or pose implementation.

## Reviewed evidence

Read HB9, HB11–12, HB35–38, HB42–43 and HB227 from the immutable survey; inspected
SNL Plates 1, 7 and 10, original SNL table scans p040/p154, and HB Plate1.
SNL1 and HB1 show the same general right-side
arrangement and should not count as independent dimensional measurements. SNL7
shows the left armor assembly in perspective. SNL10 is a front photograph with
the sponsons obscured by the forward track structure; it supplies no reliable
sponson transverse scale.

HB35 prints side armor 12 mm, roof 6 mm, floor 8 mm, and top/bottom shield plates
8 mm. It separately lists forward floor plates 12 mm and aft floor plates 6 mm.
The latter scopes must be mapped to the actual plate identities before assigning
every lower piece one thickness. HB9's 3,657.6 mm overall width can constrain the
installed outer envelope, but does not establish the complete plan shape.

HB43 explicitly distinguishes the openings: both front wings and backplates have
peep/pistol openings; the port back wing has a peephole; the starboard side has a
peephole, while the port side has both peephole and pistol opening. SNL151:028
independently allocates four peep covers to the left sponson and three to the
right. SNL152:008 allocates three ordinary pistol covers left and two right, but
its total quantity is seven; HB227 distinguishes five ordinary and two special
revolver assemblies. Preserve that scope difference when adding covers.

## Source identity map for primary plates

The following are candidate physical leaves, from SNL153–154, excluding splash
pieces, butt straps, angles and roof pressings. They total 39 plate occurrences
across 38 listed marks if installed as listed; they are not a complete sponson BOM.

| Role | Port / left | Starboard / right |
|---|---|---|
| Back | M2738 | M2738 |
| Back side | M2750 | M2739 |
| Back wing | M2744 | M2742 |
| Floor | M2757B | M2757A |
| Front lower | M2733B | M2733A |
| Front upper | M2734B | M2734A |
| Front vertical | M2732A | M2732B |
| Front wing | M2745 | M2743 |
| Roof | M2756B | M2756A |
| Side | M2748 | M2737 |
| Side lower aft | M2747 | M2736 |
| Side upper | M2746 | M2735 |
| Sloping bottom | M2740B | M2740A |
| Sloping side | M2749 | M2741 |
| Shield bottom, front / middle / rear | M2766 / M2767 / M2768 | M2762 / M2760 / M2761 |
| Shield top, front / middle / rear | M2763 / unresolved / M2765 | M2759 / M2764 per SNL / M2758 |

**Identity conflict:** SNL154:003 calls M2764 a right top intermediate plate;
HB227 groups M2764 with the port shield pieces. The original SNL p154 scan
confirms the printed right-side assignment; this is not a survey transcription
error. The original HB227 right-hand scan in MarkVIII114.jpg also confirms the
port grouping. The current plate increment provisionally follows the SNL; an
assembly drawing is still needed to resolve the historical hand. Do not mirror all parts or
infer the hand from the A/B suffix: M2732A/B is opposite the other handed pairs.

## Installed support components

HB38 gives the support roller a 40 mm bore, 110 mm OD and 27 mm width. Its curved
rail is 19.05 mm wide × 101.6 mm high, centered on the forward hinge axis, with
three floor brackets. This supplies static installed geometry even while poses
remain deferred. Rail radius, angular extent, hinge centers and bracket shapes
are still unmeasured.

SNL251:002–015 gives one handed rail assembly per side: M1944B/A rail, M1946B/A
center cleat, M1945B/A inside cleat, one shared M1947 outside cleat per assembly,
and six button rivets per assembly. The source's '(2)' on M1947 is the vehicle
quantity, not two per rail. SNL106:020–022 gives four M2826 sponson hinge pieces
plus two each of M2828 and M2827 on the hull. SNL214:007 gives two M2833 shafts.
SNL40:027 calls the roller bracket M2382, while HB227 gives M2832. The original
SNL p040 scan confirms M2382. No matching issue/review-queue text was found in
the immutable survey. Retain both source spellings and resolve their identity
explicitly before selecting a mark.

## Current interfaces to replace the envelopes

The new main hull aperture is at X = 5,574.970–7,262.528 mm and
Z = 918.882–1,926.689 mm. Its source pixel bounds are columns 510–790 and rows
270–440 in SNL2. The ordinary outer wall face is |Y| = 1,177.225 mm; the printed
vehicle half-width is 1,828.8 mm. These are current reconstruction interfaces,
not newly recovered manufactured sponson dimensions. Retain their provenance and
allow the inferred aperture to change if better source evidence requires it.

Replace the old envelope datums together with the envelope definitions; their
2,200 × 1,250 × 1,100 mm block dimensions and old transverse placement are not
plate boundaries. Use a named forward attachment/hinge frame, a common installed
floor/roof frame, explicit handed leaves and hollow interior probes. Compare
actual native plate outlines against SNL7 and the right-side photograph, check
all sponson/hull/track material interfaces, and independently reconcile quantities
from the original source rows. Keep unmeasured contours and joints partial until
their assumptions are recorded and their geometry has been inspected.
