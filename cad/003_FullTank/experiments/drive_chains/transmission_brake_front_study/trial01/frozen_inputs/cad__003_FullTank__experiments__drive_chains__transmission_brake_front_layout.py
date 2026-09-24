"""Place the front joints in the existing brake hierarchy; dimensions in mm."""
import FreeCAD as App

V = App.Vector


def layout(details, controls, manifest):
    rows = {r['name']: r for r in manifest['occurrences']}
    fresh, revised, groups = {}, {}, {}
    reused = {'steel_rivet': 'Def_BrakeAnchor_steel_rivet',
              'long_copper_rivet': 'Def_BrakeAnchor_long_copper_rivet',
              'cotter': 'Def_BrakeLink_cotter'}
    flip = App.Rotation(V(1, 0, 0), 180)
    screw_rotation = App.Rotation(*details['screw_rotation'])
    screw_axis = screw_rotation.multVec(V(0, 0, 1))

    def group(name, parent_owners, world):
        groups[name] = dict(parent=parent_owners[-1], owners=parent_owners+[name],
                            frame=list(world.toMatrix().A))

    def add(name, role, owner, local):
        g = groups[owner]
        world = App.Placement(App.Matrix(*g['frame'])).multiply(local)
        fresh[name] = dict(role=role, definition=reused.get(role, 'Def_BrakeFront_'+role),
                           owners=g['owners'], local=list(local.toMatrix().A),
                           frame=list(world.toMatrix().A))

    for hand in ['Port', 'Starboard']:
        for role, label in [('low', 'LowSpeed'), ('track', 'Track')]:
            prefix = hand+label+'Brake'
            dr = details['brakes'][role]
            upper = App.Placement(App.Matrix(*rows[prefix+'UpperBand']['frame']))
            for half in ['Upper', 'Lower']:
                hp = prefix+half
                row = rows[hp+'Band']
                pose = App.Placement(App.Matrix(*row['frame']))
                revised[row['name']] = dict(row, role=role+'_band')
                for i in [1, 2, 3]:
                    name = hp+'Segment1Rivet'+str(i)
                    revised[name] = dict(rows[name], definition=reused['long_copper_rivet'],
                                         role='long_copper_rivet')
                owner = hp+'FrontEarJoint'
                group(owner, row['owners'], pose)
                add(hp+'FrontEar', role+'_ear', owner, App.Placement())
                for joint in dr['steel_joints']:
                    add(hp+'FrontSteelRivet'+str(joint['index']), 'steel_rivet', owner,
                        App.Placement(App.Matrix(*joint['frame'])))
            owner = prefix+'FrontMechanism'
            group(owner, rows[prefix+'UpperBand']['owners'][:-1], upper)
            # Both sides use the same upright linkage. Only the pin/cotter
            # direction changes, keeping the single split pin outboard.
            pin_rotation = flip if hand == 'Starboard' else App.Rotation()
            for half, point_key in [('Upper', 'upper_pin_mm'), ('Lower', 'lower_pin_mm')]:
                pose = App.Placement(V(*dr[point_key]), pin_rotation)
                add(prefix+half+'FrontPin', 'pin', owner, pose)
                cotter = App.Placement(V(0, details['cotter_y_mm'], 0), App.Rotation())
                add(prefix+half+'FrontCotter', 'cotter', owner, pose.multiply(cotter))
            top = V(*dr['upper_pin_mm'])
            add(prefix+'AdjustingScrew', 'screw', owner, App.Placement(top, screw_rotation))
            add(prefix+'Lever', 'lever', owner,
                App.Placement(V(*dr['lower_pin_mm']), App.Rotation()))
            add(prefix+'Swivel', 'swivel', owner,
                App.Placement(V(*dr['swivel_mm']), screw_rotation))
            add(prefix+'AdjustingNut', 'nut', owner,
                App.Placement(top+screw_axis*(details['upper_eye_to_swivel_mm']+
                              controls['swivel_flat_distance']), screw_rotation))
            add(prefix+'AdjustingSpring', 'spring', owner,
                App.Placement(top+screw_axis*controls['screw_shoulder_distance'], screw_rotation))
    assert len(fresh) == 100 and len(revised) == 32 and len(groups) == 12
    return fresh, revised, groups
