# Primary Sources for Mark VIII Reconstruction

This document records the initial technical source set for the Mark VIII Liberty tank reconstruction project. These sources are especially valuable because they are period U.S. or British government publications rather than later summaries or museum descriptions. They do not all serve the same purpose, however: some describe the tank as a complete vehicle, while others document a component or a later service state.

The second and third Archive.org links originally supplied for the Preliminary Handbook are identical. They are therefore listed once below.

## Source overview

| Source | Date and character | Primary modeling role |
| --- | --- | --- |
| [Preliminary Handbook of the Mark VIII Tank](https://archive.org/details/prelimhandbookMarkVIIItank) | Original issue dated November 15, 1918; the widely circulated scan is a 1925 reprint | Vehicle envelope, layout, systems, dimensions, and major assemblies |
| [S. N. L. No. G-13, Tank, Mk. VIII](https://archive.org/details/SNL_G13_TANK_MKVIII) | 1928 U.S. service parts catalog | Nomenclature, part numbers, assembly hierarchy, quantities, and service variants |
| [The Liberty 12-cylinder aero engine handbook](https://archive.org/details/liberty12cylinde00grea) | 1918 British Ministry of Munitions technical handbook | Base Liberty engine construction, component geometry, and mechanical relationships |
| [Handbook for the Q. F. Hotchkiss 2.244-inch, 6-pdr., 6-cwt. Mark II Gun with Tank Mounting](https://archive.org/details/HandbookForTheQ.F.Hotchkiss2.244Inch6Pdr.6Cwt.MarkIIGunWithTankMounting) | 1919 U.S. Ordnance handbook | 6-pounder gun, tank mounting, recoil system, sights, controls, and gun/mount interfaces |

## 1. Preliminary Handbook of the Mark VIII Tank

The Preliminary Handbook is the most important starting point for the vehicle as a whole. Although the Archive.org scan is associated with the 1925 reprint, the handbook identifies the original issue as November 15, 1918—close to the end of the design and test period. It describes the tank at the level needed to establish a coherent reconstruction rather than merely a collection of disconnected parts.

It is expected to be the principal source for:

- overall length, width, height, weight, and trench-crossing geometry;
- hull, superstructure, sponson, turret, and engine-compartment arrangement;
- the longitudinal section and other general arrangement plates;
- driver, commander, gunner, and crew positions;
- engine-room separation and bulkhead layout;
- cooling, ventilation, fuel, electrical, and starting systems;
- transmission, brakes, track drive, road wheels, idlers, and track links;
- ammunition stowage and internal equipment; and
- the placement and broad installation of the two 6-pounder guns.

For the CAD project, this is the best candidate for the initial coordinate system and vehicle blockout. The handbook's general arrangement drawings should establish the relationships among the hull, track frames, sponsons, fighting compartment, engine room, and running gear before detailed parts are modeled.

The handbook should not be treated as a perfect modern engineering drawing. Foldouts and perspective illustrations may require calibration, and a dimension scaled from a plate is weaker evidence than a printed dimension or a dimension corroborated by another source. The source image, any dewarped or corrected derivative, and the transform used to produce it should be retained separately.

## 2. S. N. L. No. G-13, Tank, Mk. VIII

S. N. L. No. G-13 is a 1928 parts catalog for **Tank, Mk. VIII**. It is later than the Preliminary Handbook and should not automatically be assumed to describe the exact 1918 intended configuration. Its value is different: it supplies the vocabulary and hierarchy needed to turn a general arrangement into a structured model.

The catalog is particularly useful for:

- official component names and identification numbers;
- exploded or semi-exploded views of assemblies;
- part relationships and repeated hardware;
- quantities installed on a tank or in an assembly;
- drawing and part references;
- wiring and mechanical system organization; and
- distinctions among early production tanks, later substitutions, and components that were not interchangeable.

The SNL should become the backbone of the repository's model tree and source index. A CAD assembly should be able to point from a component or subassembly to its SNL designation, while the SNL entry should point back to the relevant handbook plate, drawing, photograph, or measurement.

Its date is also important. A 1928 service catalog may capture production and maintenance reality more clearly than the preliminary 1918 handbook, but it may also include postwar changes, replacements, or differences among the first 100 American tanks. Those distinctions should be recorded as variant data rather than flattened into one supposedly universal Mark VIII.

The SNL is a parts and nomenclature source, not necessarily a complete dimensional engineering package. Where it gives an identification or assembly relationship but no reliable dimension, the missing geometry should be supplied from the Preliminary Handbook, component manuals, surviving vehicles, or clearly labeled inference.

## 3. The Liberty 12-cylinder aero engine handbook

The Liberty handbook is a 1918 British Ministry of Munitions publication from the Technical Department—Aircraft Production. Its cover title is **The 12 cylinder Liberty aero engine**. It documents the Liberty V-12 as an engine in its own right, rather than documenting the Mark VIII installation.

This makes it valuable for reconstructing the engine's recognizable base geometry and mechanical organization, including:

- cylinder banks, crankcase, cylinder heads, and valve gear;
- camshaft and timing arrangements;
- crankshaft, connecting rods, pistons, and related internal structure;
- accessory drives and external fittings;
- lubrication and cooling passages or components; and
- the terminology used for Liberty engine parts.

The tank manuals must remain authoritative for the Mark VIII installation. The tank engine was not simply an aircraft engine dropped into the rear compartment: the tank application involved installation-specific changes such as a flywheel and modifications associated with lubrication and structural durability. Mounts, exhaust, cooling-air routing, fuel delivery, controls, and interfaces with the tank transmission should therefore be modeled from tank-specific evidence wherever available.

In practical terms, the Liberty handbook can supply the engine's component-level form, while the Preliminary Handbook and SNL G-13 determine how the engine is installed, supported, driven, cooled, fueled, and serviced in the tank.

## 4. Hotchkiss 6-pounder handbook with tank mounting

The 1919 Hotchkiss handbook covers the **Q. F. Hotchkiss 2.244-inch, 6-pdr., 6-cwt. Mark II gun with tank mounting**. It is not a general Mark VIII hull manual; its importance is that the Mark VIII's main armament cannot be reconstructed accurately from an exterior photograph or a tank-level outline alone.

It should provide the detailed reference for:

- the 6-pounder ordnance and breech;
- cradle, pivot, trunnion, and mounting components;
- hydraulic recoil and counter-recoil mechanisms;
- sighting equipment and firing controls;
- the gunner's shoulder support and related fittings; and
- the geometry needed to understand the gun's relationship to the sponson opening and armor.

The Mark VIII handbook and SNL G-13 should determine where the gun and mounting sit in the vehicle, how the sponson is shaped around them, and what ammunition or access provisions surround the installation. The Hotchkiss handbook should then supply the component-level gun and mount geometry. This division prevents a generic tank mounting manual from being mistaken for a complete Mark VIII sponson drawing.

## How the sources fit together

The initial source hierarchy is therefore:

1. **Preliminary Handbook** — establish the complete vehicle and its major relationships.
2. **SNL G-13** — name and organize the parts, subassemblies, quantities, and service variants.
3. **Component handbooks** — refine the Liberty engine and Hotchkiss gun/mount using dedicated technical descriptions.
4. **Photographs, surviving tanks, and additional drawings** — test the reconstruction, identify modifications, and resolve or document discrepancies.

This is a working hierarchy, not a rule that one source always overrides another. When two official sources disagree, the repository should record the disagreement, identify the configuration and date represented by each source, and preserve both interpretations until the evidence supports a decision.

## Recommended evidence labels

Each modeled feature should eventually carry a source and an evidence status such as:

- **Direct dimension** — explicitly printed in a source;
- **Documented arrangement** — shown or described, but not fully dimensioned;
- **Scaled from plate** — measured from a calibrated scan or foldout;
- **Assembly inference** — inferred from adjoining parts or required fit;
- **Observed variant** — visible on a surviving tank or period photograph; or
- **Illustrative/provisional** — included to complete a model but not yet supported by adequate evidence.

For every important CAD part or assembly, record the source identifier, page or plate, figure or callout, units, vehicle or component variant, and any transformations applied to the source image. Unmodified source scans should remain distinct from OCR output, dewarped images, line overlays, and other working derivatives.

## Initial modeling sequence

These sources support a progressive workflow:

1. Build a vehicle-level blockout from the Preliminary Handbook.
2. Establish the major compartments, track frames, sponsons, and running gear.
3. Create a source-linked assembly tree from SNL G-13.
4. Refine the Liberty engine as a separate parametric subassembly, keeping aircraft-engine evidence distinct from tank installation evidence.
5. Refine one 6-pounder and its tank mounting, then use the tank sources to place and duplicate it in the sponsons.
6. Add detail only after the larger geometry and source relationships are stable.

The result should be a historically informed, parametric reconstruction—not an unsupported claim that every surface or hidden dimension is known with engineering certainty.

