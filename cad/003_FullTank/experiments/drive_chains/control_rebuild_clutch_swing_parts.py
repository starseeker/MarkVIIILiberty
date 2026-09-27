"""Estimated SH944 castings, axial Woodruff keyseats and complete clamp stock.

Local shaft axis Y; both link arms point down (-Z). Woodruff disk planes
contain the shaft axis, with tangential thickness X. No original dimensions
are implied beyond the source bolt lengths and selected key-size hypothesis.
"""
import math
import FreeCAD as App
import Part
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def hexagon(af,z0,z1):
 r=af/math.sqrt(3);ps=[V(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3),z0) for i in range(6)]
 return Part.Face(Part.makePolygon(ps+ps[:1])).extrude(Z*(z1-z0))
def bolt(length):return hexagon(19.05,-8.255,0).fuse(Part.makeCylinder(6.35,length))
def parts(c):
 stock=c['base_stock'];height=c['journal_z']-c['base_z'];jr=c['shaft_radius'];keyr=c['key_radius'];kw=c['key_width'];kh=c['key_height'];top=jr+c['key_projection'];kc=top-kh+keyr
 # Key in an axial/radial plane: its circular arc runs along Y and Z,
 # while its tangential thickness runs along X.
 key=Part.makeCylinder(keyr,kw,V(-kw/2,0,kc),X).common(box(-kw,kw,-keyr-1,keyr+1,-keyr,top))
 shaft=Part.makeCylinder(jr,c['shaft_length'],V(0,-c['shaft_length']/2,0),Y)
 for lane in c['link_y_offsets']:
  tool=Part.makeCylinder(keyr+.025,kw+.05,V(-kw/2-.025,lane,kc),X)
  shaft=shaft.cut(tool)
 bracket=box(-44.45,44.45,-80,80,0,stock)
 for lane in [-35,35]:
  ps=[V(-18,lane-5,stock),V(18,lane-5,stock),V(22,lane-5,height),V(-22,lane-5,height)]
  web=Part.Face(Part.makePolygon(ps+ps[:1])).extrude(Y*10)
  bracket=bracket.fuse(web).fuse(Part.makeCylinder(22,10,V(0,lane-5,height),Y))
 bracket=bracket.cut(Part.makeCylinder(jr+.15,170,V(0,-85,height),Y))
 for x in [-20,20]:
  for y in [-65,65]:bracket=bracket.cut(Part.makeCylinder(6.5,stock+2,V(x,y,-1)))
 shapes=dict(Def_ClutchSwingBracket_Redo=bracket,Def_ClutchSwingShaft_Redo=shaft,Def_ClutchSwingKey_Redo=key,Def_ClutchSwingMountBolt_Redo=bolt(44.45),Def_ClutchSwingClampBolt_Redo=bolt(63.5))
 for kind,length in [('Short',c['short_arm']),('Long',c['long_arm'])]:
  # Hub, full clamp ears and arm are united before cutting ANY receiver.
  hub=Part.makeCylinder(22,20,V(0,-10,0),Y)
  hub=hub.fuse(box(12,42,-10,10,-20,20)).fuse(box(-6,6,-6,6,-length,0)).fuse(Part.makeCylinder(13,12,V(0,-6,-length),Y))
  hub=hub.cut(Part.makeCylinder(jr+.125,22,V(0,-11,0),Y))
  hub=hub.cut(box(0,45,-11,11,-1,1))
  hub=hub.cut(Part.makeCylinder(6.5,42,V(30,0,-21)))
  # Axial rectangular hub keyway receives the segment protruding from shaft.
  hub=hub.cut(box(-kw/2-.025,kw/2+.025,-11,11,jr-1,top+.025))
  hub=hub.cut(Part.makeCylinder(6.5,14,V(0,-7,-length),Y))
  shapes['Def_ClutchSwing'+kind+'_Redo']=hub
 for name,q in shapes.items():
  assert q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed(),name
  assert q.getTolerance(1)<=1e-4,(name,q.getTolerance(1))
 return shapes
