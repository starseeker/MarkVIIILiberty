exec(open('/home/cyapp/MarkVIIILiberty/.work/clutch-cone/probe_checks.py').read().split("spring=s[")[0])
cone=s['ClutchCone_cone']
rows=[]
for name in ['ClutchCone_LiningRivet07','ClutchCone_LiningRivet08','ClutchCone_LiningRivet31']:
 j=next(a for a in r['datums']['rivet_joints'] if a['name']==name);base=A.Vector(*j['base']);axis=A.Vector(*j['normal']);cross=axis.cross(A.Vector(1,0,0));cross.normalize()
 line=Part.makeLine(base-axis*4,base+axis*13);section=cone.section(line)
 faces=[]
 for f in cone.Faces:
  surface=f.Surface
  if type(surface).__name__=='Cylinder' and abs(surface.Radius-2.38125)<1e-5:
   loc=surface.Center;distance=(base-loc).cross(surface.Axis).Length
   if distance<.001:faces.append(dict(area=f.Area,radius=surface.Radius,distance=distance,center=list(f.CenterOfMass)))
 result=dict(name=name,section_vertices=[list(v.Point) for v in section.Vertexes],cyl_faces=faces,samples=[])
 for u in [-.2,-.01,-.0001,0,.0001,.01,.2]:
  p=base+axis+cross*u;result['samples'].append(dict(offset=u,inside=cone.isInside(p,1e-7,False),distance=Part.Vertex(p).distToShape(cone)[0]))
 rows.append(result);print(json.dumps(result),flush=True)
Path('classifier.json').write_text(json.dumps(rows,indent=2)+'\n')
A.closeDocument(doc.Name)
