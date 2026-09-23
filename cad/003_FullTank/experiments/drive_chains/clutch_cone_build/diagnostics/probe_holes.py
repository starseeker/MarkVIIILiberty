exec(open('/home/cyapp/MarkVIIILiberty/.work/clutch-cone/probe_checks.py').read().split("spring=s[")[0])
cone=s['ClutchCone_cone'];result=[]
for name in ['ClutchCone_LiningRivet08','ClutchCone_LiningRivet31']:
 j=next(a for a in r['datums']['rivet_joints'] if a['name']==name);base=A.Vector(*j['base']);axis=A.Vector(*j['normal']);p=base+axis
 for radius in [2.38125,2.43125]:
  tool=Part.makeCylinder(radius,17,base-axis*4,axis);cut=cone.cut(tool)
  sphere=Part.makeSphere(.01,p)
  row=dict(name=name,radius=radius,common=cone.common(tool).Volume,removed=cone.Volume-cut.Volume,inside_after=cut.isInside(p,1e-7,False),ball_after=cut.common(sphere).Volume,valid=cut.isValid(),solids=len(cut.Solids))
  result.append(row);print(row,flush=True)
print('GROUND FACES',[(f.CenterOfMass.x,f.Area) for f in s['ClutchCone_Spring1'].Faces if type(f.Surface).__name__=='Plane'],flush=True)
Path('holes.json').write_text(json.dumps(result,indent=2)+'\n')
A.closeDocument(doc.Name)
