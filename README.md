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

The likely first CAD baseline is the American Rock Island production tank, but that choice should remain explicit. The 1918 prototype or British/International configuration, the 1919–1920 American production configuration, and later service states represented by the 1928 SNL may differ in fittings, equipment, and details. Those differences should be represented as documented variants rather than silently merged.

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

This repository is at the research and reference-gathering stage. CAD work will be added incrementally as source material is organized and the evidence for individual components is evaluated.
