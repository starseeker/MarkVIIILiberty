"""Inferred lower angle runs, source-controlled lengths and owned mount datums."""
import math


def values(data):
    wanted={'hull_frame_clear','hull_skirt_thickness','hull_side_thickness','track_centers',
            'roller_pin_flat_height','roller_clamp_seat','roller_pin_diameter',
            'roller_ubolt_clearance','roller_ubolt_diameter','roller_clamp_gap','roller_fastener_bore'}
    return {k:q.value for k,q in data['values'].items() if k in wanted or k.startswith('lower_support_')}


def station_angle(data, index):
    if index >= 6:return 0
    from .roller_geometry import stations
    a,b=stations(data)[2*(index//2):2*(index//2)+2]
    return math.degrees(math.atan2(a['z']-b['z'],a['x']-b['x']))


def path_z(points, half, x):
    if x<=points[0][0]+half:return points[0][1]
    for (x0,z0),(x1,z1) in zip(points,points[1:]):
        if x<=x1-half:
            q=(x-x0-half)/(x1-x0-2*half)
            return z0+(z1-z0)*(3*q*q-2*q*q*q)
        if x<=x1+half:return z1
    return points[-1][1]


def attachment_positions(points, ends, count, v):
    """Move inferred holes clear of pins/clamps without changing source counts."""
    import numpy as np
    edge=v['lower_support_mount_edge'];exclusion=v['lower_support_mount_exclusion']
    wanted=np.array([ends[0]+(ends[1]-ends[0])*(i+.5)/count for i in range(count)])
    candidate=np.linspace(ends[0]+edge,ends[1]-edge,
                          math.ceil((ends[1]-ends[0])/v['lower_support_mount_resolution'])+1)
    # Keep exact symmetry where the nominal position is available.
    candidate=np.unique(np.concatenate((candidate,wanted)))
    candidate=candidate[np.min(np.abs(candidate[:,None]-np.array([p[0] for p in points])[None,:]),axis=1)>=exclusion]
    costs=(candidate-wanted[0])**2;back=[]
    for k in range(1,count):
        best=np.minimum.accumulate(costs);best_index=np.zeros(len(costs),dtype=int)
        for q in range(1,len(costs)):
            best_index[q]=q if costs[q]<costs[best_index[q-1]] else best_index[q-1]
        previous=np.searchsorted(candidate,candidate-v['lower_support_mount_pitch'],side='right')-1
        cost=np.full(len(candidate),np.inf);valid=previous>=0
        cost[valid]=(candidate[valid]-wanted[k])**2+best[previous[valid]]
        index=np.full(len(candidate),-1,dtype=int);index[valid]=best_index[previous[valid]]
        back.append(index);costs=cost
    if not len(costs) or not np.isfinite(costs.min()):raise ValueError('No valid lower-support bolt arrangement')
    chosen=[int(np.argmin(costs))]
    for step in reversed(back):chosen.append(int(step[chosen[-1]]))
    height=(v['roller_pin_flat_height']+v['roller_clamp_seat']-v['lower_support_thickness'])/2
    return [[float(candidate[q]),path_z(points,v['lower_support_seat_half_length'],float(candidate[q]))+height]
            for q in reversed(chosen)]


def run(data, key):
    from .roller_geometry import stations
    v=values(data);all_stations=stations(data);spec=data['lower_support_runs'][key]
    indices=spec['stations'];selected=[all_stations[i] for i in indices]
    cache_key=(key,tuple((s['x'],s['z']) for s in all_stations[:29]),tuple(sorted(v.items())))
    cache=data.setdefault('_lower_support_cache',{})
    if cache_key in cache:return cache[cache_key]
    cx=sum(s['x'] for s in selected)/len(selected);cz=sum(s['z'] for s in selected)/len(selected)
    angle=station_angle(data,indices[0]) if spec.get('inclined') else 0
    c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    points=sorted([[c*(r['x']-cx)+s*(r['z']-cz),0 if spec.get('inclined') else r['z']-cz] for r in selected])
    extension=v['lower_support_end_extension']
    ends=[points[0][0]-extension,points[-1][0]+extension]
    if key=='05short':ends=[-v['lower_support_short_length']/2,v['lower_support_short_length']/2]
    elif key=='05long':
        front=all_stations[12]['x']-v['lower_support_short_length']/2-v['lower_support_split_gap']-cx
        ends=[front-v['lower_support_long_length'],front]
    half=v['lower_support_seat_half_length']
    if any(x-half<ends[0]-1e-6 or x+half>ends[1]+1e-6 for x,z in points):
        raise ValueError('A lower support cannot contain its required pin seat: '+key)
    if any(b[0]-a[0]<=2*half for a,b in zip(points,points[1:])):
        raise ValueError('Lower support flat seats overlap: '+key)
    result=dict(run=key,stations=indices,center=[cx,cz],angle_deg=angle,points=points,ends=ends,
                bolts=attachment_positions(points,ends,spec['bolts'],v))
    cache[cache_key]=result
    return result


def arguments(definition,data):
    spec=definition['arguments'];result={**values(data),**spec}
    if spec['role']=='angle':result.update(run(data,spec['run']))
    return result


def datum(spec,data):
    key=spec['lower_support_run'];r=run(data,key);v=values(data);end=spec['support_end']
    canonical=data['lower_support_runs'][key].get('inclined',False)
    if spec.get('support_bolt') is not None:
        local_end=1 if canonical else end;x,z=r['bolts'][spec['support_bolt']]
        return dict(translation=[x,local_end*v['lower_support_thickness'],z],
                    rotation_deg=[0,0,0] if local_end==1 else [0,0,180],parent=spec['parent'])
    angle=r['angle_deg'];x,z=r['center']
    return dict(translation=[x,end*(v['hull_frame_clear']/2+v['hull_skirt_thickness']),z],
                rotation_deg=[180,angle,0] if canonical and end==-1 else [0,-angle,0],parent=spec['parent'])


def installations(data):
    for hand,sign in [('Port',1),('Starboard',-1)]:
        for end in [-1,1]:
            inside=end!=sign;bank='Inner' if inside else 'Outer'
            for key,spec in data['lower_support_runs'].items():
                if spec['scope']=='inner' and not inside or spec['scope']=='outer' and inside:continue
                yield dict(id=f'{hand}LowerSupports_{bank}_Run{key}',hand=hand,hand_sign=sign,
                           end=end,run=key,mark=spec['positive_mark'] if end==1 else spec['negative_mark'])


def hull_holes(data):
    v=values(data);holes=[]
    for item in installations(data):
        r=run(data,item['run']);a=math.radians(r['angle_deg']);c,s=math.cos(a),math.sin(a)
        flip=-1 if data['lower_support_runs'][item['run']].get('inclined') and item['end']==-1 else 1
        for x,z in r['bolts']:
            holes.append(dict(position=[r['center'][0]+c*flip*x-s*z,
                item['hand_sign']*v['track_centers']/2+item['end']*(v['hull_frame_clear']/2+v['hull_skirt_thickness']+v['lower_support_thickness']),
                r['center'][1]+s*flip*x+c*z],direction=[0,-item['end'],0],
                radius=v['lower_support_bolt_diameter']/2,length=v['lower_support_bolt_length']))
    return holes
