# Mark VIII Liberty Tank

This repository is a research and reconstruction project devoted to the First World War–era **Mark VIII tank**, commonly called the **Liberty tank** or **International tank**. It is intended to hold historical notes, transcriptions, photographs, drawings, dimensional evidence, and—eventually—CAD models of the vehicle and its components.

The goal is not merely to produce a visually convincing model. Wherever possible, the project will record the source behind each feature, distinguish documented dimensions from estimates, and preserve uncertainty where the surviving evidence does not support a single answer.

## What the Mark VIII was

The Mark VIII was a late-World War I heavy tank designed through a joint British-American program, with France also involved in the intended manufacturing arrangement. The design was meant for the anticipated 1919 Allied offensive and represented an attempt to combine British experience with American industrial capacity. Its collaborative origin is why it is often called the **International** tank.

The American version was powered by a 300-horsepower Liberty L-12 engine, which gave rise to the name **Liberty tank**. It was a large, slow, trench-crossing vehicle with a long hull, substantial track runs, and a separate engine compartment—an important improvement over the cramped engine-and-crew arrangements of earlier British heavy tanks. Its principal armament consisted of two 6-pounder guns mounted in side sponsons, supported by multiple machine guns.

The Armistice came before the tank could enter combat. After the war, the United States assembled 100 Mark VIII tanks at Rock Island Arsenal during 1919–1920 using British-made armor and other components. They served primarily as training vehicles with the U.S. Tank Corps and later the Infantry Branch until their retirement in 1932. British production and prototype counts are reported somewhat differently depending on whether a source is counting national variants, prototypes, or completed vehicles; this repository will preserve those distinctions rather than silently collapsing them into one number.

Only three Mark VIII tanks are generally reported to survive: one British-built example at [The Tank Museum](https://tankmuseum.org/tank_collection/mark-viii?country=all&era=all&tname=&tpage=), and two American examples in U.S. Army collections, including the restored vehicle at [Rock Island Arsenal](https://www.aschq.army.mil/About/History/Tours/RIA/Ordnance/) and the example described by the U.S. Army’s [Mark VIII historical article](https://www.lineofdeparture.army.mil/Journals/Army-History/Archive/Summer-2024-Issue/MarkVIII/). Contemporary testing is also documented in the Imperial War Museums’ film record, [“Trials of the Mark VIII ‘Liberty’ tank”](https://film.iwmcollections.org.uk/record/4178).

## Research and modeling scope

The project may include:

- historical background and terminology;
- source and archive references;
- scans, photographs, and extracted technical drawings;
- transcribed dimensions and dimensional comparisons;
- notes on American and British production differences;
- FreeCAD or other open CAD source files;
- scripts for image preparation, measurement, and model generation; and
- rendered views and documentation of the completed models.

The intended modeling standard is **evidence-led reconstruction**. A part may be modeled as confirmed, probable, inferred, or purely illustrative, with the status recorded in the accompanying documentation. When multiple surviving tanks or drawings differ, the model should identify which configuration it represents instead of presenting one vehicle as universally definitive.

The current source strategy separates the intended 1918 design, later American production and service practice, component-specific documentation, and modern observation. The [primary-source index](docs/primary-sources.md) now includes the 1920 Rock Island Arsenal production account, contemporary Ordnance technical articles, official 1920 reports, a participant's account of the International-tank program, Alden's sponson patent, and period test films. The [modern-reference index](docs/modern-reference-sources.md) remains separate so that observations of surviving museum vehicles are not confused with period design evidence.

The adopted first CAD baseline is the 1919–1920 American Rock Island first-100 production tank. The 1918 prototype or British/International configuration and later service states represented by the 1928 SNL may differ in fittings, equipment, and details. Those differences should be represented as documented variants rather than silently merged.

## Possible repository layout

The structure will evolve as the project develops, but a likely arrangement is:

```text
docs/          historical notes, source summaries, and research log
references/    photographs, drawings, dimensional references, and indexes
cad/           FreeCAD documents and other native model files
exports/       selected meshes, technical illustrations, and renderings
scripts/       processing and model-generation utilities
```

Large or externally hosted source files may be represented by metadata, checksums, accession information, and links rather than committed directly. Copyright, archive terms, and provenance should be recorded whenever material is added.

## Historical references

- [Primary sources and modeling hierarchy](docs/primary-sources.md)
- [Modern observational sources](docs/modern-reference-sources.md)
- [The Mark VIII Tank — U.S. Army, *Army History*](https://www.lineofdeparture.army.mil/Journals/Army-History/Archive/Summer-2024-Issue/MarkVIII/)
- [Mark VIII Tank — Rock Island Arsenal](https://www.aschq.army.mil/About/History/Tours/RIA/Ordnance/)
- [Mark VIII — The Tank Museum](https://tankmuseum.org/tank_collection/mark-viii?country=all&era=all&tname=&tpage=)
- [Tank Mark VIII — Imperial War Museums film collection](https://film.iwmcollections.org.uk/record/4178)

## Status

The [CAD foundation and pilot](cad/002_Foundation/README.md) provides a scripted
FreeCAD build of representative track, roller, and structural-joint parts in a
hierarchical assembly, with a simplified vehicle reference blockout. It includes
source-linked parameters, calibration records, STEP exports, and validation.
The [source survey](cad/001_Survey/survey_report.md) remains the frozen research
baseline. Geometry with incomplete historical evidence is explicitly provisional;
the pilot is not a complete or manufacturing-ready tank model.

The [complete-tank workflow](docs/complete-tank-workflow.md) defines the path from
that pilot through production inventory, full-vehicle layout, exterior and
interior reconstruction, and a validated native assembly release. Its
[execution queue](cad/003_FullTank/README.md) records the work packets and
dependencies. Full-tank implementation now includes a production-triage inventory,
an initial native installation layout, seven track component definitions in two
closed 78-unit tracks, 26 individual upper enclosure plates and closed leaves,
77 main hull plates, 39 sponson plates, 82 roof-louver components, 1,228 components
in 60 lower/upper roller stacks with four upper support angles, 306 front-idler
wheel/shaft/adjustment components, 34 lower support angles with 76 attachment
bolts, 298 driving-wheel/shaft/bearing components, 196 partial roller-pinion
components, and source/model comparison views. The
upper enclosures, hull and sponsons now have hollow interiors, with separate
floors, sides, roof pieces and closed standard leaves. Remaining hull structures,
sponson shields/supports, lower support retention, upper attachment/covers,
exact drive/pinion bearing profiles, chain drive and remaining idler attachment details,
louver spacing/support hardware, fittings and interiors still need population. The
[visual progression](cad/VISUAL_PROGRESSION.md) preserves milestone isometrics,
including a transparent-hull view from milestone011 onward.
Track closure uses the
printed pin pitch; wheel engagement remains unresolved. The complete tank and
interior reconstruction remain in progress. Standard assembled geometry takes
priority; selected static poses follow after that population work.
