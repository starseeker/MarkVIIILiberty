"""Grader self-test implementations. Never supplied to candidate sessions."""
CONSTRUCTION = '''
def build(p, frame):
    def cyl(r, a, b):
        return Part.makeCylinder(r, b-a, App.Vector(a,0,0), App.Vector(1,0,0))
    bearing = cyl(p['outer_radius'], p['shoulder'], p['bearing_end'])
    for a,b,r in [(p['shoulder'],p['relief_start'],p['rear_bore']),
                  (p['relief_start'],p['relief_end'],p['relief_radius']),
                  (p['relief_end'],p['bearing_end'],p['front_bore'])]:
        bearing = bearing.cut(cyl(r,a,b))
    end = p['x0']+p['sleeve_length']
    sleeve = cyl(p['sleeve_radius'],p['x0'],end).fuse(cyl(p['outer_radius'],p['x0'],p['shoulder']))
    sleeve = sleeve.cut(cyl(p['sleeve_bore'],p['x0']-1,end+1))
    for k in range(p['groove_count']):
        groove = Part.makeBox(end-p['x0']+2,p['groove_root'],p['groove_width'],
                              App.Vector(p['x0']-1,0,-p['groove_width']/2))
        groove.rotate(App.Vector(),App.Vector(1,0,0),k*360/p['groove_count'])
        sleeve = sleeve.cut(groove)
    result = {'bearing':bearing.removeSplitter(),'sleeve':sleeve.removeSplitter()}
    for shape in result.values():
        shape.Placement = frame.multiply(shape.Placement)
    return result
'''

REPAIR = '''
def rebuild(parent, p):
    def cyl(r,a,b):
        return Part.makeCylinder(r,b-a,App.Vector(a,0,0),App.Vector(1,0,0))
    lip = parent.common(cyl(p['lip_radius']+1,p['joint_face']-1,p['lip_end']))
    body = cyl(p['body_radius'],p['lip_end'],p['front'])
    s = lip.fuse(body).cut(cyl(p['rear_bore'],p['joint_face']-1,p['bore_step']))
    return s.cut(cyl(p['main_bore'],p['bore_step'],p['front']+1)).removeSplitter()
'''

LEGACY_REPAIR = '''
def rebuild(parent, p):
    def cyl(r,a,b):
        return Part.makeCylinder(r,b-a,App.Vector(a,0,0),App.Vector(1,0,0))
    s = parent.fuse(cyl(p['body_radius'],p['lip_end'],p['front']))
    s = s.cut(cyl(p['rear_bore'],p['joint_face']-1,p['bore_step']))
    return s.cut(cyl(p['main_bore'],p['bore_step'],p['front']+1)).removeSplitter()
'''
