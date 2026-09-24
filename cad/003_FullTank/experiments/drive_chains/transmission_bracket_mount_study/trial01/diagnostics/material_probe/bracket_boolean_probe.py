"""Compare material outside declared revisions without sequential remainder cuts."""
exec(compile(open('/home/cyapp/MarkVIIILiberty/.work/resume-2026-09-24/bracket_material_probe.py').read().split('records={}')[0], 'probe_setup', 'exec'))
support=json.loads((H/'transmission_frame_clearance_build/inputs/transmission_support_controls.json').read_text())['controls']
records={}
for role in ['inner','outer']:
 name='Def_FixedBearing_'+role+'_bracket'
 before=load(old['definitions'][name]['brep_path']);after=load(new['definitions'][name]['brep_path'])
 radius=support[role+'_cast_radius']['value'];half=support['bracket_height']['value']/2
 length=r['bracket_dimensions'][role]['length_mm']
 witness=Part.makeCylinder(radius,length,App.Vector(0,-length/2,0),App.Vector(0,1,0)).fuse(
     box(-radius-8,-radius+12,-length/2,length/2,-half,half))
 data={'saddle_missing':details(before.common(witness).cut(after)),
       'saddle_added':details(after.common(witness).cut(before))}
 additions=[];removals=[]
 if role=='inner':
  original=load(B/'baseline_shapes/inner_original_base.brep');revised=load(B/'baseline_shapes/inner_revised_base.brep')
  additions=list(revised.cut(original).Solids);removals=list(original.cut(revised).Solids)
 tools=[]
 for j in [j for j in r['details']['joints'] if j['role']==role]:
  y,z=j['y_local_mm'],j['z_local_mm']
  tools.extend([cylinder_x(18.5,r['details']['head_seat_x_mm'],0,y,z),
                cylinder_x(9.675,r['mount_controls']['frame_front_x']-1,r['details']['head_seat_x_mm']+1,y,z)])
 allowed=removals+tools
 tool=allowed[0].multiFuse(allowed[1:])
 data['tool_union']=details(tool)
 for method in ['whole_union','solid_remainder']:
  try:
   if method=='whole_union':missing=before.cut(after.fuse(tool))
   else:
    remainder=Part.makeCompound(list(before.cut(after).Solids))
    missing=remainder.cut(tool)
   data[method]=details(missing)
  except Exception as e:data[method]={'error':str(e)}
 retained=before.multiFuse(additions) if additions else before
 data['added_outside']=details(after.cut(retained))
 # Demonstrate detection of an unapproved cut through the bearing annulus.
 bad=after.cut(Part.makeBox(8,8,8,App.Vector(-30,-20,75)))
 data['negative_control']=details(before.cut(bad.fuse(tool)))
 records[role]=data
(OUT/'boolean_results.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2),flush=True)
