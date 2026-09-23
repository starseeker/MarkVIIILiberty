# Whole-shape tangent-distance diagnostic

On FreeCAD 1.1.1 / OCC 7.8.0, two rear-race whole-solid distance queries
returned about 0.075288 mm despite shared boundary points within 3e-14 mm.
The diagnostic records the saved native and independent point distances,
material immediately beyond contact, and positive overlap after a 0.01 mm
axial shift. This is evidence of a distance-query inconsistency for this
geometry. No geometric clearance or Boolean tolerance was relaxed.

The original failing nominal/variant checks and checker source are preserved
here. Current acceptance checks both actual surfaces at the expected contact
point and material behind the race; whole-solid distances remain diagnostic.
