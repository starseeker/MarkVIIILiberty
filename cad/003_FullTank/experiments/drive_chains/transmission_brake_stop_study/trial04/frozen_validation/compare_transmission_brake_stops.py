"""Compare saved occurrence axes and mounting position with retained manual picks."""
import argparse
import math
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
out=a.candidate.resolve();m=read(out/'isolated/manifest.json');r=read(out/'report.json')
assert sha(out/r['native_file'])==m['native_sha256']==r['native_sha256']
source=H/'transmission_brake_stop_study/sources.json';s=read(source)
assert sha(source)==r['input_hashes'][str(source.relative_to(H.parents[3]))]
rows={v['name']:v for v in m['occurrences']};top=rows['TransmissionFrame_TopChannel']['frame']
su=read(H/'transmission_brake_suspension_study/trial02/report.json');nut_height=read(H/'transmission_stud_controls.json')['controls']['nut_height']['value']
comparisons={}
def angle(a,b):return math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(a,b))))))
for role,label,origin,sx,sz in [('low','LowSpeed',(1136,122),su['dimensions']['scale_x_mm_px'],su['dimensions']['scale_z_mm_px']),
    ('track','Track',(1116,133),148/(1333-1116),su['dimensions']['web_span_mm']/(956-133))]:
    picks=s['source_picks'][role];vectors={}
    for key,suffix in [('M343','StopScrew'),('MX88','StopBarSetScrew')]:
        head,tip=picks[key+'_axis_head_tip_px'];delta=[-(tip[0]-head[0])*sx,-(tip[1]-head[1])*sz]
        length=math.hypot(*delta);direction=[x/length for x in delta]
        f=rows['Port'+label+'Brake'+suffix]['frame'];actual=[f[2],f[10]]
        vectors[key]=dict(source_direction_xz=direction,model_direction_xz=actual,
            axis_angle_difference_deg=angle(direction,actual),source_pick_span_mm=length)
    f=rows['PortFixedBearing_inner_Stud01_Nut']['frame']
    point=[f[3]+nut_height/2,f[11]]
    pixel=[origin[0]+(top[3]-point[0])/sx,origin[1]+(top[11]-point[1])/sz]
    picked=picks['mount_nut_px']
    comparisons[role]=dict(origin_px=origin,scale_mm_per_pixel=[sx,sz],screw_axes=vectors,
        source_axis_angle_between_screws_deg=angle(vectors['M343']['source_direction_xz'],vectors['MX88']['source_direction_xz']),
        model_mount_nut_center_px=pixel,source_mount_nut_pick_px=picked,
        model_minus_source_forward_up_mm=[-(pixel[0]-picked[0])*sx,-(pixel[1]-picked[1])*sz],
        mount_point_definition='Native estimated nut midpoint versus manual source nut-center pick; not a printed dimension.')
write(out/'source_comparison.json',dict(native_sha256=m['native_sha256'],comparator_sha256=sha(Path(__file__)),
    source_packet_sha256=sha(source),comparisons=comparisons,pick_uncertainty_px=5,
    registration='Inherited channel datum and separate X/Z scales; no refitting to the candidate.',
    limitation='Manually picked approximate axes and nut center; source distortion and bearing-frame interpretation remain unresolved. Endpoints can move independently within pixel uncertainty; small angle residuals are not manufacturing accuracy.',
    historical_geometry_qualified=False,installation_qualified=False))
print('Saved conditional source comparison')
