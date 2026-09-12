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
| [Williams-Ellis, *The Tank Corps*](https://archive.org/details/tankcorps00clou) | 1919 near-contemporary British Tank Corps history | Mark VIII/Allied Tank program context, terminology, and provenance |

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

## Additional period and near-contemporary sources

The four sources above are the core technical set. The following sources add an important second layer: evidence of how the tank was actually assembled, tested, modified, and described by participants and contemporary technical institutions.

## 5. Harry B. Jordan, “Manufacture of Mark VIII Tanks at the Rock Island Arsenal”

The July–August 1920 issue of *Ordnance* contains a contemporary account of Mark VIII production at Rock Island Arsenal by Harry B. Jordan. The [Internet Archive scan](https://archive.org/details/sim_ordnance_july-august-1920_1_1) includes the article on pp. 27–33 and photographs of the tanks, assembly work, transport, and a loading accident. A convenient [article index page](https://tankandafvnews.com/2015/05/05/from-the-vault-ordnance-article-on-mark-viii-tank/) identifies the article and its author, but the periodical scan should be treated as the primary reference.

This is the most important addition to the current source set for the American production configuration. It records, among other things:

- the order and progression of hull, engine-room, fighting-compartment, sponson, and track assembly;
- the approximate number and character of subassemblies required for each tank;
- American installation changes to the Liberty engine, transmission, carburetor, ignition, cooling, and fuel systems;
- the use of British structural and armor components alongside American-made automotive and electrical equipment;
- track construction and adjustment, including the reported number of shoes per track;
- materials, riveted construction, fasteners, brackets, doors, ammunition storage, and other details that are easy to omit from a general arrangement drawing;
- production dates and assembly throughput; and
- road-test experience, including defects and corrective changes.

Jordan's article is a production and test account, not a complete dimensioned engineering drawing. Its greatest value is that it distinguishes the American Rock Island build from the preliminary 1918 design and supplies a plausible manufacturing sequence for the CAD assembly tree. It should be cited whenever a modeled feature represents American production practice rather than merely the intended design shown in the Preliminary Handbook.

The same *Ordnance* issue also contains a short note on the authorization of intercommunicating telephones for the Mark VIII. The subject is treated in more technical detail in the 1921 article below.

## 6. Raymond E. Carlson, “Tanks with Modern Improvements”

The March–April 1921 “Ordnance Technical Staff Number” includes Raymond E. Carlson's article [“Tanks with Modern Improvements”](https://archive.org/details/sim_ordnance_march-april-1921_1_5), beginning on p. 315. It is not a Mark VIII construction manual, but it contains Mark VIII-specific observations about crew communication and discusses contemporary tank equipment developments.

The article describes the Mark VIII intercommunicating telephone arrangement, including communication between the commander, driver, gunners, and mechanic, along with headsets, throat-type transmitters, battery power, and an extension arrangement for a man walking ahead of the tank. It also discusses experimental or proposed equipment for observation, direction, gas protection, and cooling.

This source is useful for reconstructing systems and for identifying equipment that may belong to postwar experimentation rather than the original 1918 fit. It should not be used to assume that every “modern improvement” described in 1921 was installed on every Rock Island tank.

## 7. Annual Reports of the War Department, 1920

[Volume 1, Part 4 of the Annual Reports of the War Department](https://books.google.com/books?id=e-FBAQAAMAAJ), published by the U.S. Government Printing Office in 1920, includes the reports of the Chief of Ordnance and the Director of the Tank Corps. These official reports are unlikely to replace the Handbook or SNL for detailed geometry, but they can help reconcile program status, procurement, production, testing, organization, and postwar disposition.

The reports should be treated as administrative and institutional primary sources. They are especially useful when a later summary gives a simplified production total or date that may actually combine British prototypes, American assembly, planned French production, and postwar service activity.

## 8. Albert G. Stern, *Tanks, 1914–1918: The Log-book of a Pioneer*

Albert G. Stern's 1919 [*Tanks, 1914–1918: The Log-book of a Pioneer*](https://archive.org/details/tankslogbookofpi00ster) is a firsthand, near-contemporary account by a major participant in British tank development. It is not a substitute for a drawing or service handbook, but it reproduces correspondence and cable traffic that illuminate the International-tank program and early Mark VIII trials.

The Mark VIII material is useful for:

- design intent and the division of British, American, and French responsibilities;
- the proposed Neuvy-Pailloux production arrangement;
- the first American-assembled tank and Liberty-engine trials; and
- contemporary observations of speed, trench crossing, steering, and mechanical issues.

Stern's account should be used as corroborating evidence and as a provenance trail for contemporary reports. It should not be treated as the sole authority for exact dimensions, final production configuration, or the condition of every tank described.

## 9. Clough Williams-Ellis and A. Williams-Ellis, *The Tank Corps*

The 1919 [*The Tank Corps*](https://archive.org/details/tankcorps00clou), by Clough Williams-Ellis and A. Williams-Ellis, includes an introduction by Major-General H. J. Elles, who commanded the British Tank Corps. It is a near-contemporary institutional and participant account rather than an engineering manual.

Its most important contribution to this project is a passage describing meetings of the “New” Tank Committee in December 1917 and January 1918. The account identifies U.S. Tank Corps officers Majors Drain and Alden as participants, records the decision to manufacture the Mark VIII—or “Allied Tank”—for the British and American armies, and notes that the tank never saw combat.

This makes the volume useful for:

- corroborating the International-tank program's inter-Allied origin;
- documenting contemporary use of the names **Mark VIII** and **Allied Tank**;
- establishing the relationship of Drain and Alden to the program; and
- providing a British Tank Corps perspective on the program's purpose and outcome.

It contributes little direct geometry and should not be used to establish dimensions, component shape, or final American production configuration. Its retrospective institutional narrative should instead be checked against the Preliminary Handbook, SNL G-13, Jordan's Rock Island account, Stern's memoir, and official reports. It is best treated as provenance and program-context evidence supporting the technical source hierarchy.

## 10. Herbert W. Alden's tank patent

[U.S. Patent 1,366,550, “Tank,” by Herbert W. Alden](https://patents.google.com/patent/US1366550A/en) was filed on December 14, 1918, and published on January 25, 1921. The patent describes a pivoting or “disappearing” sponson that normally projects outside the tank but can swing through an opening into the tank, together with closure, securing, hinge, and shell-storage details.

The patent is valuable evidence of design intent and is particularly relevant to a parametric sponson mechanism. Its drawings should not automatically be assumed to be a complete production drawing: patent embodiments can be schematic, and the relationship between the patented design and individual Mark VIII production vehicles still needs to be checked against the Handbook, SNL, Jordan's production account, and surviving tanks.

## 11. Period motion-picture sources

Moving images provide evidence that static drawings cannot: obstacle behavior, clearances, access arrangements, crew positions, and the sequence in which a vehicle's mechanisms operate. They should nevertheless be treated as observational evidence rather than precision measurement sources.

### Imperial War Museums, IWM 1194

The Imperial War Museums record [“TANK MARK VIII [Allocated Title]”](https://film.iwmcollections.org.uk/record/4178) identifies a 1918, 17-minute silent film of Mark VIII trials. The catalog description records attempts to cross a steep ramp and bank, movement over spoil heaps and mud, crossing a shallow trench, pushing over a tree, close views of the guns and forward machine-gun mountings, and a final view of the driver's seat and controls.

The film shows a prototype in a natural-metal finish, with incomplete fittings and sponsons partly recessed for rail travel. It is therefore especially useful for dynamic behavior and prototype configuration, not as direct evidence of the fully equipped American Rock Island tanks.

### U.S. Ordnance test and demonstration footage

The surviving online copy of [“Tests and Demonstrations of Ordnance Materiel [1918–1919]”](https://www.youtube.com/watch?v=X_6qJMSy5Fo) includes Mark VIII testing at Bridgeport, Connecticut. The YouTube upload is a finding aid and viewing copy; the archival master and authoritative catalog record should be sought from the U.S. National Archives before treating it as the repository's preservation copy.

This footage is useful for motion, obstacle negotiation, exterior proportions, and the relationship between the vehicle and its crew or observers. Film speed, frame rate, camera perspective, and editing can distort impressions of speed and mechanical behavior, so measurements derived from individual frames should remain weak evidence unless independently calibrated.

## 12. National Archives research leads

The National Archives' [Record Group 156 guide](https://www.archives.gov/research/guide-fed-records/groups/156.html) identifies several groups of records that are likely to contain primary material not represented by the digitized manuals:

- decimal correspondence from 1915–1941, including inventions and patents, inspections, and production, progress, and status reports from 1918–1920;
- Technical Staff correspondence, test-firing records, blueprints and drawings of ordnance material, and Proving Ground Branch correspondence from 1918–1920;
- Ordnance Committee agendas, minutes, and technical reference files; and
- Bridgeport Ordnance District records for 1918–1920.

These holdings are the best prospect for original drawing sheets, acceptance or test reports, correspondence about design changes, and documentation of the first American trials. A separate catalog lead associated with a photographed Mark VIII technical drawing is [NARA Identifier 264171262](https://catalog.archives.gov/id/264171262). It should remain a research lead until its item-level description and parent series are verified.

## 13. Sevellon Brown, *The Story of Ordnance in the World War*

The 1920 [*Story of Ordnance in the World War*](https://archive.org/details/storyofordnancei00browrich) is a near-contemporary institutional account. Its Mark VIII material includes an interior photograph and caption around pp. 104–105, useful for crew-compartment visual context and for documenting what the Ordnance establishment believed had been achieved by late 1918.

This is lower priority for CAD than Jordan's production account and the dedicated manuals. Its photographs and captions should be retained as period visual evidence, while its broad summaries should be checked against the more specific technical and administrative records.

## How the sources fit together

The expanded source hierarchy is therefore:

1. **Preliminary Handbook** — establish the complete vehicle and its major relationships.
2. **SNL G-13** — name and organize the parts, subassemblies, quantities, and service variants.
3. **Jordan's production account and official reports** — establish American assembly practice, production reality, testing, and program status.
4. **Component handbooks and Alden's patent** — refine the Liberty engine, Hotchkiss gun/mount, and sponson design intent.
5. **Stern's account and Williams-Ellis's history** — provide participant and institutional testimony about the International-tank program, its terminology, and its intended role.
6. **Period films** — provide test observations and dynamic evidence.
7. **Modern surviving-vehicle observations** — test three-dimensional relationships and identify restoration or service-variant differences.

This is a working hierarchy, not a rule that one source always overrides another. When two official sources disagree, the repository should record the disagreement, identify the configuration and date represented by each source, and preserve both interpretations until the evidence supports a decision.

At minimum, source records should distinguish among:

- the 1918 prototype or British/International configuration;
- the American Rock Island production tanks assembled in 1919–1920;
- later service and maintenance states represented by the 1928 SNL; and
- postwar experimental equipment or modifications described in later technical articles.

The eventual CAD baseline should name the selected configuration explicitly rather than treating “Mark VIII” as one completely fixed vehicle.

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
2. Decide whether the initial CAD baseline is the 1918 prototype/International configuration or the American Rock Island production configuration.
3. Establish the major compartments, track frames, sponsons, and running gear, checking the production sequence against Jordan's account.
4. Create a source-linked assembly tree from SNL G-13.
5. Refine the Liberty engine as a separate parametric subassembly, keeping aircraft-engine evidence distinct from tank installation evidence.
6. Refine one 6-pounder and its tank mounting, then use the tank sources to place and duplicate it in the sponsons.
7. Use the patent and period films to test sponson movement, obstacle clearances, and crew access without promoting visual observations to exact dimensions.
8. Add detail only after the larger geometry and source relationships are stable.

The result should be a historically informed, parametric reconstruction—not an unsupported claim that every surface or hidden dimension is known with engineering certainty.
