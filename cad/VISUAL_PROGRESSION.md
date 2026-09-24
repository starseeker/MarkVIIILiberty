# Mark VIII visual progression

The 23 September coupled-receiver checkpoint adds an
[isometric](intermediate_snapshot_iso_engine_coupled_pumps_001.png) and
[section](intermediate_snapshot_detail_engine_coupled_pumps_001.png).
The receiving case passes 44 local checks, 77 case-contact comparisons,
22 cross-component comparisons, both STEP frames and a fresh rebuild. These views
combine the saved case with actual source pump/drive geometry; verification of
the merged 2,393-component native is still running. Global floor registration and
the oil manifold circuit remain unresolved. All 147 earlier images and the
standard native files are preserved, giving **149 total**. Standard tank011
remains unchanged. See the [receiver study](003_FullTank/experiments/drive_chains/engine_pump_receiver_study/README.md).

| New image | SHA256 |
|---|---|
| intermediate_snapshot_iso_engine_coupled_pumps_001.png | `62736de4754fb934db11ff681f38048ce3f183a1e30293e68bc5c3e455ce2aec` |
| intermediate_snapshot_detail_engine_coupled_pumps_001.png | `23e385b2317bb15770adeb912ae691e6f6954612a949520d5cce91834cc3686b` |

The 23 September source-profile revision adds an
[isometric](intermediate_snapshot_iso_engine_oil_pump_source_001.png) and
[handbook overlay](intermediate_snapshot_detail_engine_oil_pump_source_overlay_001.png).
The isolated 146-part pump has a smaller casing and revised bottom profile,
following conditional HB45 measurements. All 402 native checks, 482 material
pairs and seven source-envelope checks pass; fresh reproduction matches.
STEP qualification is pending. All 145 previous snapshots remain unchanged,
giving **147 total**. The overlay shows actual CAD outlines (old red, revised
blue); its local scales and proposed mounting level remain conditional.
The old crankcase receiver and engine-to-floor registration still need revision.
Standard tank011 is unchanged. See the
[source and layout study](003_FullTank/experiments/drive_chains/engine_pump_layout_study/README.md).

| New image | SHA256 |
|---|---|
| Source-profile isometric | `61c6c88743ae04602a4a24cd44d953797b2eda0ae1d4f3f13898e6e6ab3d1c6a` |
| Handbook overlay | `e62d87ade49b21ecd7d541801f70b337a3c86899663b27819fad75800fa58dd5` |

The 23 September oil-pump mounting checkpoint adds an
[isometric](intermediate_snapshot_iso_engine_oil_pump_mounting_001.png) and
[mounting plan](intermediate_snapshot_detail_engine_oil_pump_mounting_001.png).
Ten stud/washer/nut/cotter sets and a gasket bring the isolated pump to 146
components. Both nominal and eight-control trial builds pass 402 native checks,
466 material comparisons and 186 STEP pairs. All 143 previous snapshots remain
unchanged, giving **145 total**. The first installation trial finds floor and
crankcase interference; its rejected section views are retained in the
[work packet](003_FullTank/packets/P01-engine-oil-pump.md), rather than presented
as an accepted installation. Standard tank011 remains unchanged.

| New image | SHA256 |
|---|---|
| Mounting isometric | `9f2d01938c586dd5b93d8c0fca4f9645bf6c40974207845d044bfb9b83e6b453` |
| Mounting plan | `5476ce5b4d03e961429931d95a2ddd13dedf5c4b8b85bab879b75e3a90191fd1` |

The earlier hardware and relief-lock checkpoint preserves a new
[isometric](intermediate_snapshot_iso_engine_oil_pump_hardware_001.png) and
[underside detail](intermediate_snapshot_detail_engine_oil_pump_relief_lock_001.png).
The separate pump now contains 105 constituents, including fourteen bolt sets
and the cage-to-bolt lock wire. All 141 earlier images are unchanged: **143 total**.
Two wires, mounting, connections and source-profile refinement remain pending;
standard tank 011 is unchanged. The detail omits the cover and lower strainer
for inspection; it does not change the physical assembly or implement a pose.

Isometric SHA-256: `8b2e80d8d39d061acffc4dd438aa05343f93c49a1a5f1a1bde7310233b355f93`.
Underside SHA-256: `799bafc01dedc7e08785011d376d505f89ee0b8fd8978472a8482ff9f193c990`.

The 23 September oil-pump development adds a preserved
[isometric](intermediate_snapshot_iso_engine_oil_pump_development_001.png) and
[cutaway](intermediate_snapshot_detail_engine_oil_pump_cutaway_001.png).
The separate 35-component study includes five gears, two castings, the pressure
relief internals, both strainer baskets and their open screen approximations.
Fastening sets, lock wires, external fittings and crankcase installation remain
pending; this does not advance the standard tank to milestone 012.
All 139 earlier progression images remain unchanged; the total is now 141.
See the [oil-pump packet](003_FullTank/packets/P01-engine-oil-pump.md).

Isometric SHA-256: `aa2bece0e8e38b15f3aab96ee5be6dd4b9e92c3e233b1edb42a795be86583fcf`.
Cutaway SHA-256: `a0a798100fe57a6bfc25acc73f8fa47671095c16278f40105585d18d90a9816c`.

Preserved standard isometric renderings, requested by the user on 19 September
2026. Add the next unused `intermediate_snapshot_iso_NNN.png` when the assembled
model reaches a significant visual improvement. Copy the rendered image without
modification, retain the camera/style where practical, and preserve earlier
snapshots. These are in-progress reconstructions; an image is not a completeness
or historical-accuracy certification.

| Snapshot | Recorded date | Milestone | SHA-256 |
|---|---|---|---|
| [001](intermediate_snapshot_iso_001.png) | 2026-09-19 | User-saved upper plate stage: both closed tracks, 26 upper plates, remaining major systems as layout geometry. | c68365214418aca1b9c8dae4ffc355e9871d955b6bb6c57d57dbe9a03266f31f |
| [002](intermediate_snapshot_iso_002.png) | 2026-09-19 | User-saved main hull stage: 77 individual hull plates added; revised upper track clearance. Sponsons and interior machinery remain provisional. | 319098de4921f8e801cffaf1895aa0092a2e7445fbe80f91fa93d73a28ac60dd |
| [003](intermediate_snapshot_iso_003.png) | 2026-09-19 | Individual sponson shells: 39 plates replace the two envelopes, with hollow interiors, handed openings and tapered lower plates. Mounts, supports and fittings remain pending. | 172008f6c40ce8e1c944c9aae3d3cff3300b5cef77106167ad6900203fbacbbd |
| [004](intermediate_snapshot_iso_004.png) | 2026-09-20 | Roof louvers: 62 curved blades plus separate guarded frames, covers, retainers and packing plates (82 components). Spacing/support hardware and rear deflector remain pending. | aee4cf8abdc73d6e7685c62665c730b496726d7c4f67ecaf342d208bb30f8cf6 |
| [005](intermediate_snapshot_iso_005.png) | 2026-09-20 | 60 roller stacks: 58 lower and two rear upper stations, 1,224 components. Visible lower roller/clamp detail; long supports, upper covers and drive/idler assemblies remain pending. | 494ec7acb1b08eb732de906249f96ede93f0d9dca7ab097bd531e4ca440c4701 |
| [006](intermediate_snapshot_iso_006.png) | 2026-09-20 | Front idler internals: 242 rim/disk/boss/diaphragm/rivet/bushing parts replace two wheel envelopes. Enclosed detail is visible through the lower nose openings; shafts and tensioners remain pending. | e375e9e2aad2f6a449a3191e5ce42c73d53a5e250c62217847381dea2b52c7d6 |
| [007](intermediate_snapshot_iso_007.png) | 2026-09-20 | Idler shafts and adjusters: 64 additional parts, four visible brackets and owned hull openings; nested wheel disks and flatter diaphragm troughs. Profiles, inner retention and threads remain partial. | c9f03efc751c3d84b504946ece85c731757ad76dc88d167c42ce3716d7f98073 |
| [008](intermediate_snapshot_iso_008.png) | 2026-09-20 | 34 lower support angles and 76 bolts, inclined front roller units, revised front skirt border and bounded nose clearance. Contours, tapped receivers and removable retention remain partial. | 123536379dc393e79d8572a9d0f1c578c231b0462666c03ebcbb369ef6aa7558 |
| [009](intermediate_snapshot_iso_009.png) | 2026-09-20 | 242 driving-wheel/bush parts replace two envelopes; aligned toothed rims and revised common idler/drive internals. The 35/37 tooth conflict, shafts, bearings and engagement remain open. | 040eea4a40408f37e55b384c9c4160289dee173f48ec181c9aba6dea333a89d6 |
| [010](intermediate_snapshot_iso_010.png) | 2026-09-20 | 56 driving-shaft/bearing/attachment parts; source-correct inner receivers and revised rear skirt border. Exact casting profiles, threads, sealing, additional backing-plate rivets and engagement remain open. | 7544be5660dde9e57c1386175eefb367ed12d062a66afe1c8ffd5e866913fbbe |
| [011](intermediate_snapshot_iso_011.png) | 2026-09-20 | 196 roller-pinion, shaft and support parts; inferred fuel-backplate station. 5,326 physical components in the standard assembly. Static fit checked; tooth count, cast profiles, retention and engagement remain partial. | fd1ee7b817ca0729c9cee1de4fa4a0080dbe9554e8a18edfaeef672b0d462f21 |

The initial two images were user-saved and matched against the rendering history.
Snapshots 003–011 are byte-for-byte copies of the inspected standard isometric
at the sponson-shell, louver, roller, idler, lower-support, drive-wheel, driving-shaft and roller-pinion milestones. Preserve them through later rebuilds. Use the next unused
number for the next significant visual improvement; never replace an earlier image.

The idler stage also preserves an unmodified [wheel close-up](intermediate_snapshot_detail_idler_006.png),
showing construction largely hidden by the hull in the standard view.
SHA-256: `4579c66d788ca9bbe532992b05639c7f4cc76690884d70db317fe256d00237ec`.

The adjustment stage preserves an [idler close-up](intermediate_snapshot_detail_idler_007.png)
and [mounting detail](intermediate_snapshot_detail_adjuster_007.png).
`intermediate_snapshot_detail_idler_007.png` SHA-256: `357c8b77fc3a2e8bd3ee84ec0aec51802c7c4ead6d99e43f4bc28400bd05b5a5`.
`intermediate_snapshot_detail_adjuster_007.png` SHA-256: `10a8bffb339466f2cb7cc630bd1490791a9e51e660c37490912ba5116c48a234`.

[Open the interactive comparison](visual_progression.html) to select two saved milestones and move a divider between them.

The lower-support stage preserves an [installed front detail](intermediate_snapshot_detail_supports_008.png),
using a hull section crop to expose the assembled supports. This is a diagnostic view, not a pose variant.
SHA-256: `a075f2aab36ae0256702529358e43ca696f9d884b24f56a951eac2c3da8be710`.

The driving-wheel stage preserves a [drive-wheel close-up](intermediate_snapshot_detail_drive_009.png),
showing the paired aligned toothed rings and source-common internal parts.
SHA-256: `d150f4d4e33294c392aadb085cfb3e14a146debc0e2f456d50c17c45dcb3be1d`.

The driving-shaft stage preserves a [wheel close-up](intermediate_snapshot_detail_drive_010.png)
and [shaft/support detail](intermediate_snapshot_detail_drive_mounts_010.png).
`intermediate_snapshot_detail_drive_010.png` SHA-256: `81c3b41b5aabe69e3a997df99fc67f4ee199c908e2bb2cdfae7341ecc2b95cdc`.
`intermediate_snapshot_detail_drive_mounts_010.png` SHA-256: `84d734370c5bd753c85f3d37e5714926b714e0632ab6d1ed23eb7af756321244`.

The pinion stage preserves a [pinion/wheel close-up](intermediate_snapshot_detail_pinions_011.png)
and [shaft/support detail](intermediate_snapshot_detail_pinion_mounts_011.png).
`intermediate_snapshot_detail_pinions_011.png` SHA-256: `eaab45d3888028d024db63a1491aec464a4cc5985ea80d4b47481a58914aea6a`.
`intermediate_snapshot_detail_pinion_mounts_011.png` SHA-256: `19fbb47c92d28b031e6838159a35a30a713dc7ffc9d8a6eef92f79e6abc51cfc`.

The [transparent-hull isometric011](intermediate_snapshot_iso_transparent_011.png)
uses 18% opacity for hull and sponson armor, with opaque running gear and interior
components. This exposes enclosed detail while keeping the standard assembled
geometry unchanged. Colored interior layout envelopes remain provisional.
The interactive viewer offers opaque and transparent hull display; older stages
retain their original images. Future milestones should preserve both versions.
SHA-256: `97f19ad3b616f3c5ed191a0cc1398c13f19ddfa89d1b31ada49f1b46c167605d`.

The [transmission candidate isometric](intermediate_snapshot_iso_transmission_candidate_001.png)
preserves the first central-case stage separately from standard tank milestones
(20 September 2026). It shows the reconstructed frame/output train with eleven
new bevel-case, cross-shaft, planetary-case, carrier and high-speed drum parts.
This isolated fixture has 939 solids; gear internals, brake bands and integration
remain unfinished. It is not standard milestone 012.
SHA-256: `b7b37e5d9d767742fca1b85e459b622a4de379647ae72b1f87c46dd5d7a07b0e`.

The subsequent isolated [transmission cutaway](intermediate_snapshot_iso_transmission_cutaway_001.png)
and [large-gear detail](intermediate_snapshot_detail_transmission_gears_001.png)
show the eighteen added gear, gasket and retention occurrences (20 September
2026). Both large planetary trains are populated in the 957-solid fixture;
pin supports, the small train, bevel gears and integration remain open. These
inspection images supplement the standard history and are not milestone 012.

`intermediate_snapshot_iso_transmission_cutaway_001.png` SHA-256:
`1ad1be8ec500935ad12d45b40b03eaf62b78a98d7647df5ac899ba88f05396dd`.
`intermediate_snapshot_detail_transmission_gears_001.png` SHA-256:
`55e1003638315b0ae9424d71d242c51853e3eefd7640c2fff35674813730657b`.

The isolated [supported-planet isometric](intermediate_snapshot_iso_transmission_supports_001.png)
and [pin-axis section](intermediate_snapshot_detail_transmission_pins_001.png)
record 56 added pin, bearing, ring and retention occurrences (20 September 2026).
The fixture contains 1,013 solids with recessed carrier nuts. The source
pin-center discrepancy remains unresolved; the ring-bolt comparison is corrected
in the subsequent revision below. These partial reconstruction views do not
advance the standard tank to milestone 012.

`intermediate_snapshot_iso_transmission_supports_001.png` SHA-256:
`6781fd0f8ad0f1170c215034b886143c56a3bdbc0b419a65217996ccb2d09edc`.
`intermediate_snapshot_detail_transmission_pins_001.png` SHA-256:
`0bd2205f7576cc7db237e4441fb2f6a3bcbc53bf50b4d4e6323daeefee76a00a`.

The revised [support isometric](intermediate_snapshot_iso_transmission_supports_002.png)
and [ring-bolt section](intermediate_snapshot_detail_transmission_ring_bolts_001.png)
record the corrected M318 installation (20 September 2026). Callout15 identifies
the inner ring bolt; the previous outer-bolt comparison used a case-joint bolt
and is superseded. Twenty-two occurrences change; the fixture still has 1,013
solids. The carrier-face view exposes the revised recessed nuts. All earlier
images remain preserved, and standard tank milestone 011 is unchanged.

`intermediate_snapshot_iso_transmission_supports_002.png` SHA-256:
`e0e34faf4f9c1e19182d5d5c3363dc26304cd1aa2c2970a7e1630690d7a5adcb`.
`intermediate_snapshot_detail_transmission_ring_bolts_001.png` SHA-256:
`4832942123168e19b3096c72a30fbb32ffc92284bc506035afac1772f340119c`.

The [combined planetary cutaway](intermediate_snapshot_iso_transmission_small_001.png)
and [small-train oblique](intermediate_snapshot_detail_transmission_small_001.png)
record 46 added small-gear, bush, disk/ring and rivet occurrences (20 September
2026). The isolated fixture contains 1,059 solids. Source planet-center and rivet
axial discrepancies remain documented; small supports and full-tank integration
are unfinished. Standard milestone 011 and all earlier images remain unchanged.

`intermediate_snapshot_iso_transmission_small_001.png` SHA-256:
`8087bc84fe79bed20684e63d1fee3d2e66a8cfc76f1efe2f88195641bfc5195f`.
`intermediate_snapshot_detail_transmission_small_001.png` SHA-256:
`263623a1d20c510169004966f381afe2aec7c911d11765c364f4e8bed1958cb8`.

The [small-support cutaway](intermediate_snapshot_iso_transmission_small_supports_001.png)
and [small pin section](intermediate_snapshot_detail_transmission_small_pins_001.png)
record 56 additional support occurrences and 38 revised case/disk/ring/rivet
occurrences (20 September 2026). The 1,115-solid fixture has both planetary
support stacks. A cubic swept input disk brings the rivet center to its source
station; the planet-center and exact-profile uncertainties remain. This is an
isolated transmission checkpoint, not standard tank milestone 012. All prior
snapshots, including transparent/opaque 011, remain preserved.

`intermediate_snapshot_iso_transmission_small_supports_001.png` SHA-256:
`75adb4749160b51952aafecd8491f27f604733f484da95f159216cd1c4e8197b`.

`intermediate_snapshot_detail_transmission_small_pins_001.png` SHA-256:
`77794f427b6d298ccd037b8daa18c35fc8667357363cae0b1703ca939776b109`.

The [sun-retention cutaway](intermediate_snapshot_iso_transmission_retention_001.png)
and [sleeve/drum section](intermediate_snapshot_detail_transmission_sun_retention_001.png)
record the two small-sun M290 rings and four revised sleeve/drum occurrences
(20 September 2026). Six M290 rings now share one definition in the 1,117-solid
fixture. The close view exposes the groove collar, shoulder and counterbore;
fits and split angle remain inferred. Brake bearings and standard integration
remain open. Standard milestone 011 and all previous views are preserved.

`intermediate_snapshot_iso_transmission_retention_001.png` SHA-256:
`9f72097204650212350519d3a5b490d9dd4c2c3e34bcc62e43da3011e9431de7`.

`intermediate_snapshot_detail_transmission_sun_retention_001.png` SHA-256:
`39e5c9b60ed47b93d0783d0b82b60f495076693c1e70c99c1018839aec73c59e`.

The [bevel-support cutaway](intermediate_snapshot_iso_transmission_bevel_supports_001.png)
and [central bearing section](intermediate_snapshot_detail_transmission_bevel_supports_001.png)
record twelve new sleeve, bush, oil-retainer, screw and dowel occurrences
(20 September 2026). The 1,129-solid fixture has seven revised shaft/case/cover/
sun/bush occurrences. Enlarged journals correct an assembly-passage defect;
the source datum conflict and unqualified axial stack remain documented in
[the packet](003_FullTank/packets/I03-bevel-sleeve-supports.md). This isolated
interior checkpoint retains standard milestone011 and both hull display views.

`intermediate_snapshot_iso_transmission_bevel_supports_001.png` SHA-256:
`f37e14a5193883e73843f3f8a5e9c80a1cae161c70eca74f5492d4f2701ff1e6`.

`intermediate_snapshot_detail_transmission_bevel_supports_001.png` SHA-256:
`981f6e83a1be155cd158eb620c2e2bbe4cd6569f4bd8aedd8664a73cd7669c27`.

The bevel-drive increment (21 September 2026) preserves the
[transmission cutaway](intermediate_snapshot_iso_transmission_bevel_001.png),
[central section](intermediate_snapshot_detail_transmission_bevel_001.png) and
[exposed gear mesh](intermediate_snapshot_iso_bevel_mesh_001.png). These show the
1,199-leaf isolated candidate with 46/14-tooth bevel gears, four-dog clutch,
rivets and decomposed thrust bearings. Source-datum disagreement and inferred
internal profiles remain explicit; input bearings and complete transmission
integration are pending. Standard 011 and both hull views are preserved.
`intermediate_snapshot_iso_transmission_bevel_001.png` SHA-256: `d3de93d41d3b1c6c573a2065976cd45942672483c02e3e9f21a841400c442f4d`.
`intermediate_snapshot_detail_transmission_bevel_001.png` SHA-256: `44d41a1ae1fd598ea4ec737c0ef1cb302a6a10825735154e08da84ff234e3faa`.
`intermediate_snapshot_iso_bevel_mesh_001.png` SHA-256: `c035c19d179c974176e054a7c2468bd77f3d34069d33b90931cd604fffae4f8a`.

## Input bearing/housing/coupling increment — 21 September 2026

The isolated transmission now contains 1,287 valid solids, including 88 new
input-assembly occurrences. Preserve the [central cutaway](intermediate_snapshot_iso_transmission_input_001.png),
[input section](intermediate_snapshot_detail_transmission_input_001.png) and
[bearing section](intermediate_snapshot_detail_input_bearing_001.png). The
[packet](003_FullTank/packets/I03-input-assembly.md) records printed bearing
envelopes, inferred internals, corrected assembly passages and comparisons
with SNL Plates22/23. Source quantity/profile conflicts remain explicit.
Standard tank011 and its opaque/transparent companions are unchanged; these
are candidate interior improvements awaiting integration.

`intermediate_snapshot_iso_transmission_input_001.png` SHA-256: `f9b08bb95d3a00b0251b195aa768bc9c086ac7c8efb4971ad31b376a174c325d`.
`intermediate_snapshot_detail_transmission_input_001.png` SHA-256: `c707a4245ad11927cd4eda61113298ef133ca189bf4bd7daab4a5ff4c6b38742`.
`intermediate_snapshot_detail_input_bearing_001.png` SHA-256: `fed23cf8801f77bf4f86426e370fd4b4d502fa75e51963060e89bbd0cfabcc12`.

## Input installation and cotter repair — 21 September 2026

The [installation cutaway](intermediate_snapshot_iso_transmission_input_installation_001.png),
[grease-feed section](intermediate_snapshot_detail_input_grease_001.png) and
[MX25 joint](intermediate_snapshot_detail_input_fasteners_001.png) preserve the
1,303-solid candidate's new cover fasteners and bored grease feed. Seventeen
older cotter occurrences also regain a leg lost during fusion. The
[packet](003_FullTank/packets/I03-input-installation.md) retains the count/nut
conflicts, inferred fitting location and source-scale differences. Standard011
and its opaque/transparent companions remain unchanged pending integration.

`intermediate_snapshot_iso_transmission_input_installation_001.png` SHA-256: `3b34fbc4f4b016a700e5dc6c6cadf6bd9c32baf2cbc6ad961f01be482541b598`.
`intermediate_snapshot_detail_input_grease_001.png` SHA-256: `33d728238967fd9a8f345f5852c52029ffc181c9bc432437492b14fd5a5a0168`.
`intermediate_snapshot_detail_input_fasteners_001.png` SHA-256: `40352b6e7562621f3620a08cc7958093cea8207f840dcf65f8604260b2c50521`.

## Brake-bearing supports — 21 September 2026

The [support overview](intermediate_snapshot_iso_transmission_brake_bearings_001.png),
[focused bearing section](intermediate_snapshot_detail_brake_bearing_001.png) and
[MX14 fastener](intermediate_snapshot_detail_brake_bearing_fasteners_001.png)
preserve the1,321-solid candidate. Two bushes/caps and their hardware close the
previously missing joint; shared-journal architecture and casting form remain
explicit hypotheses. The [packet](003_FullTank/packets/I03-brake-bearings.md)
records the qualification and SNL22 differences. Standard011 and all46 earlier
snapshots remain unchanged; this candidate awaits tank integration.

`intermediate_snapshot_iso_transmission_brake_bearings_001.png` SHA-256: `70f3c796161bd02b9303459774555bb18bc46b83a392ef7adcd150d0a71fd141`.
`intermediate_snapshot_detail_brake_bearing_001.png` SHA-256: `58af613065c4f081c53f8ce2a806735728b0e30b63fe491a6b4074d577a28b39`.
`intermediate_snapshot_detail_brake_bearing_fasteners_001.png` SHA-256: `3f5c9b9ef288cf8dade590dbd5a562af1cdc70f5b6ce6e010eb5976c1c28316b`.

The central case joint (21 September 2026) preserves a
[case overview](intermediate_snapshot_iso_transmission_case_joint_001.png),
[cover-hidden isometric](intermediate_snapshot_iso_transmission_case_joint_open_001.png)
and [joint section](intermediate_snapshot_detail_case_joint_001.png).
Fourteen MX8 bolt/nut/pin sets and two M326 gaskets bring the isolated transmission
to 1,365 valid solids. Source counts are retained; the transverse bolt pattern,
flange detail and gasket stock remain inferred. Six inspected views include the
unchanged SNL23 calibration and record casting/fastener-position differences.
These are inspection views of an incomplete transmission, not standard tank012.
All twenty standard native files and forty-nine previous images are preserved.

`intermediate_snapshot_iso_transmission_case_joint_001.png` SHA-256:
`6fff221141049d24c103c58bf4b5cb5d1b4698da917a5a470f4b0ef187213c9a`.

`intermediate_snapshot_iso_transmission_case_joint_open_001.png` SHA-256:
`9b29aa0a5026b73b7a335e811eede16fac16ff91779762753a7feec084559257`.

`intermediate_snapshot_detail_case_joint_001.png` SHA-256:
`7e28b922c9c227a9bee20515918447cdc8167d269678ed059da8247fa33fd69c`.

The reversing-controls stage preserves the [open isometric](intermediate_snapshot_iso_transmission_reversing_001.png),
[fork/rod mechanism](intermediate_snapshot_iso_transmission_reversing_mechanism_001.png)
and [detent section](intermediate_snapshot_detail_reversing_detent_001.png)
(21 September2026). Seven added leaves bring the isolated candidate to1,372
solids. The continuous clutch groove and paired ring tips are corrected to clear
the fork; its upper arm is refined against the fixed-scale SNL23 image. The
section exposes the plunger, spring and hollow cap. Vertical linkage, mounting,
other transmission equipment and standard integration remain pending. Earlier
snapshots and the opaque/transparent standard011 are unchanged.

`intermediate_snapshot_iso_transmission_reversing_001.png` SHA-256: `812d2afbf7e6bd348a5c31d67daf12ce65b7b0d06a83e8fae9352d95d9088e35`.

`intermediate_snapshot_iso_transmission_reversing_mechanism_001.png` SHA-256: `5bc51d7bacc3d363401451114422a4859790486ac3601925654c33d432866527`.

`intermediate_snapshot_detail_reversing_detent_001.png` SHA-256: `e8d8d00ced715037b428f1e407711571dd67f02e2929fc687a7fecd88bbb80be`.

## 21 September 2026 — vertical reversing controls

The [installed rear view](intermediate_snapshot_iso_transmission_vertical_001.png),
[exposed mechanism](intermediate_snapshot_iso_transmission_vertical_mechanism_001.png)
and [bearing/key section](intermediate_snapshot_detail_vertical_bearing_001.png)
preserve the addition of M303–M306, two Woodruff keys and separate MX11/MX12
attachment sets. The isolated transmission now has 1,391 valid solids. Seven
native/source views were inspected; all148 affected material pairs, 21 STEP
comparisons, 116 independent checks and three parameter trials pass. No. C key
size, bearing construction and unshown profiles remain estimates. Standard tank 011
and its opaque/transparent companions are unchanged; this is not tank012.

| Snapshot | SHA-256 |
|---|---|
| `intermediate_snapshot_iso_transmission_vertical_001.png` | `146ef0a60a06c36710cbbb368960d5d467574233ef5424947cb4b3cbd9c688b3` |
| `intermediate_snapshot_iso_transmission_vertical_mechanism_001.png` | `88e32e7750322ac0cb801336a8afb62eec0ee3ae54984b2bb68273aab4a5b163` |
| `intermediate_snapshot_detail_vertical_bearing_001.png` | `6de767825b1795b553fb4938632944674849b32fd2968c7f2d87fb7595368a8f` |

The [MX5 mounting trial](intermediate_snapshot_iso_transmission_case_mount_trial_001.png)
and [joint section](intermediate_snapshot_detail_case_mount_trial_001.png) record
four added stud/nut/pin/bevel-washer sets (21 September2026). The experimental
fixture has 1,407 solids and passes its mechanical/STEP checks. Its long upper
casting bosses project beyond the visible source wing; the discrepancy remains
explicit. A subsequent source review accepted these exact CAD bytes for continued
reconstruction with the bosses documented as approximate. The original trial
images are retained; historical fit is unqualified and this is not tank012.

`intermediate_snapshot_iso_transmission_case_mount_trial_001.png` SHA-256:
`8a6eb8f5b18ef5ebce27be48a719c0c13d59ff42e881f735b076da60f5192da1`.
`intermediate_snapshot_detail_case_mount_trial_001.png` SHA-256:
`08b9ea2cff91d0f7d4009e9e656940fcd0d8d250964026aa233553c6cc2e7c0e`.

## 21 September 2026 — air-pressure pump core

The [assembled pump](intermediate_snapshot_iso_air_pressure_pump_001.png),
[internal mechanism](intermediate_snapshot_iso_air_pressure_pump_internals_001.png)
and [transverse bank section](intermediate_snapshot_detail_air_pressure_pump_section_001.png)
preserve 51 new physical pieces in an isolated native assembly. Four cylinders,
hollow pistons, return springs, cam shaft, separate bearing bushes and a V pulley
are visible. Bearing covers were refined against the source; axial shaft location,
screw-head clearance and vent continuity are checked. Dimensions and internal
details remain documented approximations. Supports, mounting hardware, drive belt
and air lines remain unfinished. Standard tank011 and its transparent companion
are unchanged; these component views are not tank012.

| Snapshot | SHA-256 |
|---|---|
| `intermediate_snapshot_iso_air_pressure_pump_001.png` | `8e1f96d2219290554a68721ec4c631f27dd0663f74ce7325630d5547b7a9a4be` |
| `intermediate_snapshot_iso_air_pressure_pump_internals_001.png` | `20ce493ae617c82b5c40959afbf63e1c923493dd6ba90b5bb5625a686508212f` |
| `intermediate_snapshot_detail_air_pressure_pump_section_001.png` | `68aa7a24ab5b74a6a487c75129aa8f81e414829ca3e6a45ad4a7d5577ee906ff` |

## 21 September 2026 — pump mounting and conditional drive datum

The [mounted pump](intermediate_snapshot_iso_air_pump_mount_001.png),
[exposed supports](intermediate_snapshot_iso_air_pump_supports_001.png) and
[attachment section](intermediate_snapshot_detail_air_pump_mount_001.png) preserve
32 new bracket/stud/base-fastener pieces. The combined transmission/pump document
has1,490 physical leaves with separate FuelPressure and Drivetrain ownership.
The pump is now attached to modeled receiving bosses, with widened feet for
bolt-head clearance. This remains a mounting hypothesis: the54-inch belt study
uses estimated driver and pitch radii, and HB15 obscures much of the support.
Clutch drive, air lines and standard integration remain unfinished. Tank011 and
its opaque/transparent views remain unchanged.

| Image | SHA-256 |
|---|---|
| `intermediate_snapshot_iso_air_pump_mount_001.png` | `a7ccb6ca51d0aed647a0fc0a36c8e5065ab383dfbde34a9bfe748f724eda4263` |
| `intermediate_snapshot_iso_air_pump_supports_001.png` | `0c56002de284cf08abee08af76ccb1626d8567192be711c4547964f386128b93` |
| `intermediate_snapshot_detail_air_pump_mount_001.png` | `4d3aafe9f78a889d017317ca0bb57884ed1eac12413460a2939814a9b6960623` |

The clutch-stop drive stage (21 September 2026) preserves the [assembled drive](intermediate_snapshot_iso_clutch_drive_001.png),
[exposed coupling and shaft](intermediate_snapshot_iso_clutch_coupling_001.png),
and [centre section](intermediate_snapshot_detail_clutch_drive_001.png).
The combined transmission/pump candidate contains 1,520 physical leaves after
adding the coupling box, two half covers, stop drum, shaft, eight fastening sets
and linked-belt representation. Source comparison widened the estimated head
from 76 to 100 mm. The exact transverse form, shaft identity transfer, casting
profiles and proprietary belt-link inventory remain approximate or unresolved.
Main clutch, air circuit and standard integration are unfinished; standard tank
011 and both of its hull display views remain unchanged.

`intermediate_snapshot_iso_clutch_drive_001.png` SHA-256: `4c70d49360b03d0993c313d1f4dd16f2fce28e8d8243d0a14bdc054d93ae1b75`.
`intermediate_snapshot_iso_clutch_coupling_001.png` SHA-256: `a30548fdd71165bbd1f9f1737fd072d990add6006e590e2da2a893b481a77617`.
`intermediate_snapshot_detail_clutch_drive_001.png` SHA-256: `5b3aa2a1331a69e7dce40ca1bcc012cb4d0bea63f234eba34ec93f662c9b0d29`.

The front-clutch stage (21 September 2026) adds the SH945A coupling, two SH849A
half flanges, seven-turn SH849B spring and two bolt/nut/washer sets. The combined
transmission/pump candidate has1,530 physical pieces, with blended cardan shoulders
and a relieved receiving passage. Spring diameter convention, coupling dimension
transfer and collar profiles remain documented approximations. The main clutch
and standard integration are unfinished; standard tank011 remains preserved.

[intermediate_snapshot_iso_front_clutch_001.png](intermediate_snapshot_iso_front_clutch_001.png) · SHA-256 `76aab7188d7154b33d5b3fb8171a67099a934eec6535659431be006d148faff5`.

[intermediate_snapshot_iso_front_clutch_mechanism_001.png](intermediate_snapshot_iso_front_clutch_mechanism_001.png) · SHA-256 `67faf39a95e45e7ac6e9974a90e41ad3b66f4925c9070a50d7f54a6fd4fb79b6`.

[intermediate_snapshot_detail_front_clutch_001.png](intermediate_snapshot_detail_front_clutch_001.png) · SHA-256 `e7cb946c0c3886fcb4f1f58e35fc35a6660c3f097de3058bc0abb8d3540c3214`.


The collar-joint stage (21 September 2026) adds the SH999A collar, SH997A ring,
SH997B bush, six drilled screws and one continuous locking wire, for 1,540
physical components in the combined transmission/pump candidate. Closer SNL
inspection required two coupling flanges and a forward end-bearing pocket;
the earlier single-flange reconstruction remains preserved for comparison.
The external spring and split clamp move 67 mm aft together. Axial stations,
bearing fits and wire diameter/routing remain explicit approximations. The
main internal clutch stack and standard integration remain unfinished.

Four new images preserve the installed joint, exposed mechanism, true axial
section and wire through all six drilled heads. The existing 72 progression
images, including the opaque and transparent standard tank 011 views, retain
their original bytes.

| Image | SHA-256 |
|---|---|
| [installed isometric](intermediate_snapshot_iso_clutch_collar_001.png) | `659651e385e4e898eb327dc3e836431f57bee744628e905d68f1cdf3bdc984b5` |
| [isolated mechanism](intermediate_snapshot_iso_clutch_collar_mechanism_001.png) | `a38a6177a6d5d308a8d1421d7609683135ef1a3561bb337dc7228a596c2ef339` |
| [axial section](intermediate_snapshot_detail_clutch_collar_001.png) | `a177378feebcca1bd071266232af3af38c04c2a66d2213808d12bb36afd75c4a` |
| [locking wire](intermediate_snapshot_detail_clutch_collar_wire_001.png) | `6278779e6fe989355d37b4d78b9ec1b2fa4ee17834cd1aab795bf2827fb4d2a5` |


**Superseded first main-clutch core:** the following 001 images retain the
initial 1,548-component candidate. Later full-plate tracing showed that its
large end-retention piece was misidentified; the corrected 002 views follow.
Passing static geometry checks did not establish correct source identity.

The main-clutch core stage (21 September 2026) adds the SH998D relieved bearing,
SH861B nested sleeve, SH869A cone support, four SH861D keys and SH861E retaining
ring. The combined candidate has1,548 physical components. SH999A now has the
receiving bore, four key beds and ring groove;1,539 parent components are unchanged.
The section follows the SNL nesting and preserves the preceding empty-bore view
for comparison. Literal handbook key thickness produces visibly thicker bands
than the catalogue drawing; identity and section-axis interpretation remain open.
Exact drive attachment, cones, thrust/ball mechanism, spring plungers and engine
engagement remain unfinished. The integrated tank remains011.

Four new images follow. All76 earlier snapshots, including transparent tank011,
remain byte-for-byte preserved.

| Image | SHA-256 |
|---|---|
| [installed isometric](intermediate_snapshot_iso_clutch_stack_001.png) | `8d6fce988dad1e9832f8181c3167887b341b8401c6adad711ccbe9bdbc1c1aa0` |
| [mechanism](intermediate_snapshot_iso_clutch_stack_mechanism_001.png) | `7fab17fbd59dfb4a366b097a3fbe08621d46a4f27f5c07d73caf5635edc4fee8` |
| [axial section](intermediate_snapshot_detail_clutch_stack_001.png) | `0680f174f47f595059b69d1b14a036909101f5b61fe618657115a38ca0729db4` |
| [exposed keys](intermediate_snapshot_detail_clutch_stack_keys_001.png) | `5b4591600295a2ecc8ca30cf3da912c6a9ec82ef9e9ec42485929b05bd3a2cc0` |


## Corrected main-clutch core — 22 September 2026

The 002 images preserve the separate SH998B thrust collar and external SH861E
snap ring after full-plate source tracing corrected the first core. This
1,549-component isolated transmission/pump candidate passed current geometry,
exchange, size-trial and visual checks. The old 001 images remain unchanged.
The radial variant also exposed a retained parent rim; the regenerated body now
responds coherently to its radius control. Standard tank 011 remains unchanged.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_clutch_stack_002.png) | `7fb570f78a5e634f1d05a54c53c451322a4e63dcd6b83376a4fdd45c57b787a3` |
| [mechanism](intermediate_snapshot_iso_clutch_stack_mechanism_002.png) | `8b76e182f690d4b6d6d0885f3c8c90dec0d6a90574c3c9b5609a5cf66c84b03c` |
| [axial section](intermediate_snapshot_detail_clutch_stack_002.png) | `d35ce242a3db5eaf300d2752a496d9a15b03949ea80f17270721071a8d387918` |
| [exposed keys](intermediate_snapshot_detail_clutch_stack_keys_002.png) | `873ca1ab582262085e0356b32e401bdf04868c966cafc64c258a537d54071a4f` |


## Clutch thrust mechanism — 22 September 2026

The 1,581-component isolated transmission/pump native now includes the SH998C
retainer, thirty quarter-inch steel balls and SH998A spring-stop ring. The
existing SH998B collar receives an estimated axial race. Source identity, native
geometry, exchange, two size trials and a fresh build were checked; seven native/
source views were inspected. These snapshots use 0.04 mm display tessellation
without changing analytic geometry. Race/cage manufacture and load behavior
remain unqualified. The six provisional holes await their spring-plunger sets.
Standard tank 011 and all earlier images remain unchanged.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_clutch_thrust_001.png) | `97c90ad8b0a4ef5a9e9d7ecd97e6946620bfbcf5fdd0fd1ed4ebdbec612b9288` |
| [exposed balls and cage](intermediate_snapshot_iso_clutch_thrust_open_001.png) | `d161b17d0a5f081ee5a18b94ad574545d8306525d4b73daa08efdaf3b9975e21` |
| [race contact section](intermediate_snapshot_detail_clutch_thrust_001.png) | `562cef9b8aa6dae9b4b9abade3a678fd06aa49b63bc6a7bd75a6a314f51dc2bf` |
| [retainer](intermediate_snapshot_detail_clutch_thrust_cage_001.png) | `864458d011f499d20ad971da5d2048f0d2bd703a13b59a20d00c7adec40de328` |


## Clutch cone and spring sets — 22 September 2026

The isolated transmission/pump assembly now has **1,652 physical components**.
It adds the pressed cone, separate lining, 49 rivets, plug, six plungers, cups
and springs, and the rear retaining ring. The existing keyed support now has
actual cone and cup interfaces. Conditional handbook dimensions constrain the
friction surface; support contours, finishing and spring details remain inferred.

All 326 material pairs, 462 independent checks, ten definition and 72 installed
STEP checks pass, as do two coupled geometry trials and a fresh build. Seven
native/source views were inspected. The plunger locking wire, outer drum and
flywheel/crankshaft engagement remain unfinished. Standard tank 011, including
its transparent-hull view, and all 88 prior images remain unchanged.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_clutch_cone_001.png) | `8b9b99d36d79a5e7e9c1578d12c191ed13c7233c47269744e02d6f5c9ed48c8f` |
| [clutch cutaway](intermediate_snapshot_iso_clutch_cone_cutaway_001.png) | `f6a5aec7d637dc7e52aa5272c0eeeaf1ea802a91668b78d26d9ee388f43c07ac` |
| [axial section](intermediate_snapshot_detail_clutch_cone_001.png) | `44b039e0860ea6c4fc25f7aeb86e70fda81ac5c21724cd64b68b850bc5a38b24` |
| [six spring sets](intermediate_snapshot_detail_clutch_springs_001.png) | `ca0c8aa3cd14191d6e38a0b77f273061e5428340f14fb7413d2ab907b421e182` |


## Clutch plunger retention — 22 September 2026

The 1,653-component isolated transmission/pump checkpoint adds one 30in SH861K
wire and six actual tangential head passages. Existing plungers remain shared
native links. Wire diameter, route and twist are explicit estimates; orange
highlights the wire for review and does not identify its material. Geometry,
exchange, two size trials and fresh rebuild pass. Standard tank011 and its
transparent-hull companion remain unchanged; all 92 previous images are preserved.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_clutch_retention_001.png) | `256604d12bd1d6885059f8905714b62750b1de72fc2fee3384861596b5380dcb` |
| [six-head wire route](intermediate_snapshot_detail_clutch_retention_001.png) | `72d9d70fe4af082fdedf3dd879192109eb2bf2d283e84dcf3d5fcd149ba5a502` |
| [head passage section](intermediate_snapshot_detail_plunger_wire_001.png) | `a782d7dcf948ce14f84ab3ca769ab50b908b8a5789f60d7833257440e6003afd` |


## Outer clutch drum and flywheel — 23 September 2026

The isolated candidate contains **1,662 physical components**. The drum, toothed
flywheel, six drilled screws and 48in locking wire are populated. The existing 30in
plunger wire turns inward to clear the flywheel. Geometry, STEP exchange, two
coupled parameter trials and fresh reproduction pass. Six images were inspected.

Flywheel dish and hub profiles, starter tooth count and wire routes remain
explicit approximations. The axial section exposes a steeper dish than the
handbook sketch; complete engine/crankshaft work must revisit it. Standard tank011
and its transparent-hull companion remain unchanged. All 95 earlier images are
preserved, bringing the progression to 99 images.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_clutch_drum_001.png) | `4badcc162ed9b104a28f6c1981220b5b7920d14898b70573e9bf601362b20a1a` |
| [axial section](intermediate_snapshot_section_clutch_drum_001.png) | `fd2f38afdaed6ab6c528459b7622167f536505b47c2083e11a8370e1e28edfd4` |
| [flywheel detail](intermediate_snapshot_detail_flywheel_001.png) | `a20f624175a25fc30a85da6a99af3c78481d20261ab2ef3823b3f0a6f6dabc1f` |
| [two wire routes](intermediate_snapshot_detail_clutch_wires_001.png) | `8cdb75ff84a36d10cf17e97dbcb3d0cf52cb6705a72ac250fbeb9ab93918cfc0` |


## Clutch-stop band development — 23 September 2026

The isolated development candidate has **1,681 physical components**. It adds
M4158 band, M4159 lining, fourteen copper lining rivets and three button rivets
at an inferred returned pin eye. The source-sized stop drum, belt and pump mounts
update together. This is an unfinished brake: anchor, six anchor rivets and the
operating linkage remain required. The clutch axial envelope and throwout-shaft
placement are under source review before mounting those parts.

Five native views were inspected. All 99 earlier images remain unchanged; these
three additions bring the progression to 102. Standard tank011 and its
transparent-hull companion remain unchanged.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_clutch_stop_band_001.png) | `dadf0b8a5ae68a35c66992c05cb9e813a6e3f22a863b900b2783275e0115c40d` |
| [band and lining detail](intermediate_snapshot_detail_clutch_stop_band_001.png) | `a0c7856264fc934f1bccc58af538ebea2b5ef0b39b7529ede2f65111742ee710` |
| [returned-eye section](intermediate_snapshot_section_clutch_stop_band_001.png) | `efc30fe72de5ea86c1e7bd332b7d559f6049c2639467e8f1d0f34ad79cfe9e5e` |


## Clutch release bearings, forks and shaft — 23 September 2026

The isolated development assembly has **1,758 physical components**. Two release
bearings, their pins and retaining hardware, forks, main shaft, operating lever
and three keys are populated. The two catalogue bearings contain54 estimated
internal pieces; these counts do not establish a historical manufacturing BOM.
Brackets, shaft retention, auxiliary controls and full brake linkage remain pending.

Five native views were inspected. Geometry,332 interference pairs,93 STEP
comparisons and a coupled parameter trial pass. All102 previous images are
preserved; these three additions bring the progression to105. Standard tank011
and its transparent-hull companion remain unchanged. Source registration and
overall clutch-length interpretation remain open.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_clutch_throwout_001.png) | `e1909e937fd459f1cabd623b47d7096585b36a3f64f676cb699443791e23fbe2` |
| [coupling receiver](intermediate_snapshot_detail_clutch_throwout_001.png) | `9f93302087baea0b800fb55d55769bc092325bb10b0d6a5fa4c949a92aeef302` |
| [two-row bearing section](intermediate_snapshot_section_clutch_throwout_bearing_001.png) | `4b990ad5e3f5b964633231eeccb2f01c9e4e38b583c27bf24b1ebae5a8b7e2b9` |


## Clutch supports and auxiliary controls — 23 September 2026

The isolated development assembly contains **1,786 physical components**: 27 new
mechanism pieces, one replacement floor context, two revised parent parts and
1,756 unchanged inherited occurrences. Brackets, mounting hardware, auxiliary
shaft/levers and the rear control rod are populated. Floor mounting and casting
contours remain hypotheses; full-source review corrected the longitudinal control
direction. The complete brake and forward controls remain unfinished.

All 117 independent checks, 88 affected material pairs and 46 STEP comparisons
pass, along with one coupled local parameter trial. Five native views were inspected.
All 105 earlier images remain unchanged; these additions bring the progression to
108. Standard tank011 and its transparent-hull companion remain unchanged. Source
registration, complete clutch length and historical mounting remain open.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_clutch_supports_001.png) | `3d8db4d1f797e815821f31d0fb5620262c0ed506e177699c245600236b0c3edf` |
| [support detail](intermediate_snapshot_detail_clutch_supports_001.png) | `c62de91a3c25027f3e5e63120ffee2203a5a83976b243f84c35eba16ae7636ad` |
| [auxiliary controls](intermediate_snapshot_detail_clutch_auxiliary_001.png) | `8918fa3e6518783c5cdfe4056fe804c5ce980bc017c34a1c7715081fa92aafd8` |


## Clutch-stop anchor and operating linkage — 23 September 2026

The isolated development assembly contains **1,821 physical components**, adding
35 brake pieces and revising four receiving parts. The band now owns its complete
26-child catalogue inventory, with mounting hardware separately allocated.
The mounting, carrier profile and crank arrangement remain inferred.

All 112 independent checks, 273 affected material pairs and 64 STEP comparisons
pass, together with a coupled local dimensional trial. Six native views were
inspected. These three snapshots bring the progression to 111; all 108 earlier
images are preserved. Standard tank011 and its transparent-hull companion remain
unchanged while combined drivetrain qualification and integration are pending.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_clutch_brake_001.png) | `8e7cf425882d7de080b009d3de41a8835e65acdd116e24ca4a18b8fa4828dd86` |
| [mechanism detail](intermediate_snapshot_detail_clutch_brake_001.png) | `c007d2d4b742858b0a9eb4b518b6494c751c3b87f24ece39ab5cb15842399776` |
| [end view](intermediate_snapshot_end_clutch_brake_001.png) | `561213dd04eac69b5ac731214bceff65c660552d59b52fd27c32ff63c62ef57f` |


## Engine transverse supports and floor joints — 23 September 2026

The development assembly now contains **1,848 physical components**, adding the
11 nested channel parts and 14 direct floor rivets. Two additional replacement
floor contexts and one revised floor preserve the original combined floor outline
and clutch holes. Profiles, transverse stations and floor seams remain estimates;
engine suspension brackets, rails and associated joints remain to be built.

All 151 independent checks, 93 material pairs including standard context and 40 STEP
comparisons pass. A coupled station/span/depth trial also passes 151/93 including
standard context. Six native views and a fixed-calibration SNL2 projection were
inspected. These three images bring the progression to 114, preserving all 111 prior
images. Standard tank011 and its transparent-hull companion remain unchanged.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_engine_crossmembers_001.png) | `2fd84d603879efc4f599a807f9d7e58972578ae0b0a9dfc2c2953db32711ddd5` |
| [exposed crossmembers](intermediate_snapshot_detail_engine_crossmembers_001.png) | `517031b9b9700b2ee6411631aa825fd1db955c216e71ebe6dc767df932cdb5d6` |
| [rear gusset joint](intermediate_snapshot_detail_engine_gusset_001.png) | `0d82a74f23a018be8c381e0f811b49af4dc5a13ada7ca92e193817b7b4a24ad8` |


## Engine suspension and longitudinal supports — 23 September 2026

The development candidate contains **1,909 physical components**:61 new support
pieces and two receiving revisions, preserving1,846 inherited occurrences.
All72 SNL242 engine-support children plus14 direct floor rivets are populated.
Cast profiles and joint allocation remain estimated; the17in mounting-row spacing
and flange datum are conditional aviation transfers. Engine casing/receivers,
sump fit and the six-versus-seven mounting count remain unresolved.

Nominal202 independent checks,159 material pairs including standard context and
83 STEP comparisons pass. A coupled parameter trial passes202/159, including
standard context. Seven native views and a fixed SNL2 source projection were
inspected. These three images bring the progression to117, preserving all114
prior images. Standard tank011 and its transparent-hull companion are unchanged.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_engine_suspension_001.png) | `0c8b69e9dceab23865fc0f054dd172e81c9608e1fde2df42c8b8dc7a2dab3cc0` |
| [exposed engine supports](intermediate_snapshot_detail_engine_suspension_001.png) | `3a4cf97bf47e22ccea98154dfbabbe9387457d544b19260d039c2d348b362d68` |
| [front suspension mount](intermediate_snapshot_detail_engine_front_mount_001.png) | `3f2d9f19e1a0cf48e4ca2d0d2c5edc5ece7f455f16d48ee627836b6028176b3a` |


## Hollow engine crankcase castings — 23 September 2026

The development candidate contains **1,911 physical components**: two new
castings, seven support revisions and1,902 preserved inherited occurrences.
Upper V-bank receivers, integral webs and main-bearing seats, a dry gear chamber,
lower oil trough/wells and estimated pump receivers are now represented. The
front yoke's estimated arms drop around the sump, with4.392248mm nominal clearance.
Engine internals, hardware, registration and mounting identity conflicts remain open.

Nominal191 independent checks,71 affected material pairs including standard
context and15 STEP comparisons pass. A coupled parameter trial passes191/71.
Eight native views and the fixed source projection were visually inspected.
Three images bring the progression to120; all117 earlier images and20 standard
native files are unchanged. Standard tank011 and its transparent view await
combined drivetrain integration. Profiles remain documented approximations.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_engine_case_001.png) | `d548711903b8f5a36a0b7acad9137fac29807ef5020060e9716057689fcea26c` |
| [upper crankcase casting](intermediate_snapshot_detail_engine_case_upper_001.png) | `e14f18669fbafe1cf05c0651d2b926c2932251037cd403cbdede1d3386341b1f` |
| [lower crankcase casting](intermediate_snapshot_detail_engine_case_lower_001.png) | `22666b21812d60610dbeda4d1a95f36268a51e431fc8db69c0417bd312a7ce36` |


## Engine crankshaft and bearing interiors — 23 September 2026

The development candidate contains **1,992 physical components**: 81 new shaft,
bearing and retention constituents; two revised receiving cases; 1,909 preserved
parent pieces. Nominal 437 independent checks, 517 affected material pairs
including standard context and 101 STEP comparisons pass. The coupled trial passes
437/517. Eight native views were compared with manual figures.
Unprinted profiles, thrust internals and registration remain estimates; shaft
plugs/gear and the remaining engine systems are pending.

The upper case is hidden in the review isometric to expose the internals. Both
cases remain installed in the native model. Three snapshots bring the progression
to 123, preserving 120 earlier images. Standard tank011 and its transparent-hull
companion remain unchanged pending combined drivetrain integration.

| View | SHA-256 |
| --- | --- |
| [installed isometric with upper case hidden](intermediate_snapshot_iso_engine_crankshaft_001.png) | `54b04b0acf60c0554a4f0917f573ade6a909ceedc76eb5906cd11f403fa9966d` |
| [bare crankshaft](intermediate_snapshot_detail_engine_crankshaft_001.png) | `ac88e9a41001ad05b4a72fe8ac7884f53e43db0edf51a153e771bfa4852395cf` |
| [thrust bearing section](intermediate_snapshot_detail_engine_thrust_001.png) | `12402f7333a87506b09448eb3a27f2510857a2fec392940f405b45c18385f87a` |


## Engine shaft closures — 23 September 2026

The development assembly contains 2,131 physical occurrences: 139 new closure and
retaining constituents, one revised forging and 1,991 preserved parent pieces.
Nominal 268 independent checks, 738 affected material pairs including standard
context and 157 STEP comparisons pass. Coupled parameter trial:
268/738 pass; trial STEP unchecked. Seven views inspected against source
context; unprinted cap profiles and recesses remain estimates.

The upper case is hidden only for review. Three new images bring progression to
126; all 123 prior images are preserved. Standard tank011 and its transparent-hull
companion remain unchanged pending combined drivetrain integration.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_engine_shaft_fittings_001.png) | `91e4acb00dba69cbcaa6a7507c923bf58d2dfec0532d0dc95d8f6149a96f8776` |
| [shaft and closures](intermediate_snapshot_detail_engine_shaft_fittings_001.png) | `4fc5fe28c54835a65c3003efb3cbf9d625b6e2023ee930327fd92b9d7dff8329` |
| [crankpin closure section](intermediate_snapshot_detail_engine_shaft_closures_001.png) | `e0bdd3d4f0cbd288af8d454ab16cf325840823f497d2847a321f491d4eab5b03` |


## Engine driving bevel and thrust lock — 23 September 2026

The development assembly contains 2,153 physical occurrences: 22 new, two locally
revised and 2,129 preserved. Nominal 93 independent / 428 material-pair/33 STEP checks
pass. The module/face/web trial passes 93/428/33, including standard
context and STEP. Six views were inspected against source context; bolt-grip
conflict, claw/spline counts and wire route remain documented uncertainties.

Three new images bring progression to 129; all 126prior images are preserved.
Upper case hidden only for review. Standard tank011 and its transparent-hull
companion remain unchanged pending combined drivetrain integration.

| View | SHA-256 |
| --- | --- |
| [installed isometric](intermediate_snapshot_iso_engine_gear_001.png) | `8d182cae50df7a0c101581aecaa1abc536f7c84003acbcf2b37d75bdef86e405` |
| [driving bevel joint](intermediate_snapshot_detail_engine_gear_001.png) | `6c2ff3e8ffa5c8faa128b0e0e3228e2a8ec8073604e7e887815bea52123c4ab9` |
| [thrust-nut lock](intermediate_snapshot_detail_engine_thrust_lock_001.png) | `1e766788500faac4d8c45654e2d6a3ef9556458276b83ee72af8d919d0e6eb32` |


## Lower distribution component study — 23 September 2026

Seventeen new pieces represent the lower driver and its split bearing/housing
assembly. Component and STEP checks pass; casing contacts, pump-axis position,
receiving lug and service withdrawal remain unresolved. These are development
views, not a newly qualified standard tank. Two images bring the progression to
131, preserving all 129 previous images. Standard tank011 and its transparent-hull
companion remain unchanged.

| View | SHA-256 |
| --- | --- |
| [mating gears and lower unit](intermediate_snapshot_iso_engine_lower_drive_study_001.png) | `1d47ca76c43876af9c5b5ef491c3d0ecba91257321452f319a7a31fa434a581b` |
| [exploded component study](intermediate_snapshot_detail_engine_lower_drive_study_001.png) | `b1c1bed84d71be655100c5e3af4869dab3cd7379eaa7b8cd4a21f2cf4a11292b` |


## Lower-drive receiving casting — 23 September 2026

One revised integral crankcase now supports the lower driver and retaining screw,
with explicit oil access, rear water-pump opening and offset bottom oil-pump rim.
Native fit, continuous case withdrawal, STEP, actual gear mesh, a coupled trial
and fresh reproduction pass. Casting dimensions remain estimated and pump
assemblies/standard integration remain pending. Two images bring the progression
to 133; all 131 previous images and standard tank 011 are preserved.

| View | SHA-256 |
| --- | --- |
| [receiver isometric section](intermediate_snapshot_iso_engine_lower_drive_receivers_001.png) | `b6249b604b5a42ef61b5bc62fef9943bfbe3d0e8778e490641de899fb39add53` |
| [offset oil-pump opening from below](intermediate_snapshot_detail_engine_lower_drive_receivers_001.png) | `d66af08dc2057f424e86260b668147d82da493f88bdc87d2509b16f85e6bb106` |


## Water-pump development — 23 September 2026

The development assembly now includes 60 water-pump constituents: geared shaft,
bearing internals, packing/glands/spring, open impeller, pump body, inlet cover,
sealing layers and cover fasteners. Native geometry, fit, rotation and preservation
checks pass. The pump body's STEP tolerance repair remains in progress; case
attachment, exact cast profiles and source identity conflicts remain open.
Two images bring the progression to 135; all 133 previous images are preserved.

| View | SHA-256 |
| --- | --- |
| [intermediate_snapshot_iso_engine_water_pump_study_001](intermediate_snapshot_iso_engine_water_pump_study_001.png) | `b63c5f7ee305d1e7fe79c5996e9ac6d5539867bdc4735bdf67af0b74c9210929` |
| [intermediate_snapshot_detail_engine_water_pump_study_001](intermediate_snapshot_detail_engine_water_pump_study_001.png) | `2dde934794363f710bd29fc86e4978f1495827384f91d9f8d301c0bc075fa1bc` |


## Water-pump mounting revision — 23 September 2026

Four complete source-length mounting stud sets, integral case pads, tangential
outlets and a revised flat drain seat extend the development assembly to 2,246
occurrences. All 38 native checks and 472 material comparisons pass, including
standard context. STEP, parameter-trial and reproduction qualification are still
in progress at this snapshot stage. These are development views; standard tank
011 remains unchanged. Two new images bring the progression to 137, preserving
all 135 previous images. The case section deliberately removes some receiving
material for visibility while retaining complete fasteners.

| View | SHA-256 |
| --- | --- |
| [isometric.png](intermediate_snapshot_iso_engine_water_pump_mounting_001.png) | `b01a8ccf74b95c0e2e40e0c95a3533b5e6c453800fdd1ffd302af86a9ec4dac9` |
| [installed.png](intermediate_snapshot_detail_engine_water_pump_mounting_001.png) | `b19c224c84444fc534254980d929986f3fc0afe94334ccdb718dd2cafe085b16` |


## Water-pump connections and drain wire — 23 September 2026

Printed hose-end stock and the source-length formed wire extend the pump
development checkpoint. Nominal and coupled-trial native/STEP checks and fresh
reproduction pass. Exact cast profiles and wire route remain documented estimates;
standard tank011 is unchanged. Two images bring the total to 139, preserving all 137
earlier images.

| View | SHA-256 |
| --- | --- |
| [isometric.png](intermediate_snapshot_iso_engine_water_pump_connections_001.png) | `48e6140b0f43cbb0da3fe0aa963244b4c77d895496f8889d6f06bb6b1daccd8b` |
| [drain_lock.png](intermediate_snapshot_detail_engine_water_pump_drain_lock_001.png) | `f78629194802926e1241bf5745829f90010d06af69c03570520a85ca55124ead` |
