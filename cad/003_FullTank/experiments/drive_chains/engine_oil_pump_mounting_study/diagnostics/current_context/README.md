# Rejected initial oil-pump installation fit

This diagnostic places the saved 146-component pump in the unchanged
2,247-component water-pump/engine development document at the previously
proposed engine-local `(1243.87630083555, 0, -282)` mm. It saves no combined
native model and changes neither source document.

[The complete probe](context_probe.json) checks 54 spatially overlapping pairs
and finds **12 material collisions**: eight with floor plate M1935 and four with
the current lower crankcase. The lower pump extends through the floor; the
existing offset case opening clips the upper body and strainer. Separately,
the proposed gasket case face is 27.6 mm below the earlier receiver's mounting
plane, so absence of stud collisions would not establish a seated joint.

The [section](installation_section.png) and
[cutaway](installation_cutaway.png) show oil-pump geometry in gold, water-pump
geometry in blue and the floor in red. Display-only cuts retain engine Y>=0;
they do not remove physical material in either document.

[The upward-shift diagnostic](vertical_clearance.json) finds a minimum
**62.5164896 mm** rigid raise to put every pump component above the floor top.
Adding 1 mm clearance clears the floor envelope but produces five collisions
in nine selected drive-interface comparisons, including the upper pump body,
strainer frame and shaft coupling. A rigid raise alone is therefore rejected.

The [source constraints](source_constraints.json) retain inspected HB58/SNL14
engine sections and SNL2 whole-tank context. The printed 20.75 inch ground
clearance stays explicit. Pump scale, lower-drive spacing and engine/drivetrain
registration must be reconciled together before choosing a receiver revision.
No undocumented floor opening is introduced to make the fit pass.
