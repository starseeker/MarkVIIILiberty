"""Align a 50-pitch route to the existing static roller-pinion relief phase.

The documented 12-tooth transmission sprocket receives a derived phase and station.
These remain candidates; the provisional transmission datum is not edited.
"""
import math
from pathlib import Path
import sys
from scipy.optimize import brentq
from pitch_route_probe import PITCH,BIG,SMALL,LARGE_TEETH,SMALL_TEETH,route
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.model import load,datum_values
from lib.evidence import read,write,sha,fingerprint


def closed_route(center_distance,first_angle,count=50):
    point,perimeter=route(center_distance)
    alpha=math.acos((BIG-SMALL)/center_distance)
    start=BIG*(first_angle-alpha)
    station=start;vertices=[point(station)]
    for _ in range(count):
        previous=point(station)
        station=brentq(lambda t:math.dist(previous,point(t))-PITCH,
                      station+PITCH*.99,station+PITCH*1.1,xtol=1e-10)
        vertices.append(point(station))
    return station-start-perimeter,vertices


def angle_error(angle,phase,teeth):
    step=2*math.pi/teeth
    return abs((angle-phase+step/2)%step-step/2)


if __name__=='__main__':
    data=load();fit_path=STAGE/'experiments/roller_pinions/static_fit/report.json';fit=read(fit_path)
    assert fit['passed']
    driving=datum_values('port_drive',data)['translation']
    delta=fit['corrected_relative_axis_mm']
    big=(driving[0]+delta[0],driving[2]+delta[2])
    provisional=datum_values('transmission_axis',data)['translation']
    beta=math.atan2(provisional[2]-big[1],provisional[0]-big[0])
    phase=math.radians(fit['selected']['phase_deg'])
    tooth_angles=[(math.pi/2-phase-2*math.pi*n/LARGE_TEETH-beta)%(2*math.pi) for n in range(LARGE_TEETH)]
    # Choose an actual relief center near the large sprocket's upper quadrant, safely
    # inside its wrap for every center distance in the root bracket.
    first=min(a for a in tooth_angles if math.pi/2<=a<=math.pi)
    distance=brentq(lambda c:closed_route(c,first)[0],BIG+SMALL,50*PITCH,xtol=1e-9)
    residual,points=closed_route(distance,first)
    assert abs(residual)<1e-7 and math.dist(points[0],points[-1])<1e-7
    small_angles=[];large_angles=[]
    for x,z in points[:-1]:
        if abs(math.hypot(x,z)-BIG)<1e-7:large_angles.append(math.atan2(z,x))
        if abs(math.hypot(x-distance,z)-SMALL)<1e-7:small_angles.append(math.atan2(z,x-distance))
    assert len(large_angles)>3 and len(small_angles)>3
    big_error=max(angle_error(a,first,LARGE_TEETH) for a in large_angles)
    small_error=max(angle_error(a,small_angles[0],SMALL_TEETH) for a in small_angles)
    assert big_error<1e-9 and small_error<1e-9
    def world(point):
        x,z=point
        return [big[0]+x*math.cos(beta)-z*math.sin(beta),
                big[1]+x*math.sin(beta)+z*math.cos(beta)]
    candidate=world((distance,0))
    result=dict(status='phase_aligned_mathematical_candidate',pitch_count=50,pitch_mm=PITCH,
        large_teeth=LARGE_TEETH,small_teeth=SMALL_TEETH,
        tooth_count_source='HB130 original scan, outline table and prose',
        roller_pinion_phase_deg=math.degrees(phase),center_distance_mm=distance,
        roller_pinion_axis_xz_mm=big,provisional_transmission_axis_xz_mm=[provisional[0],provisional[2]],
        candidate_transmission_axis_xz_mm=candidate,
        provisional_station_difference_mm=math.dist(candidate,(provisional[0],provisional[2])),
        small_pinion_candidate_phase_deg=math.degrees(math.pi/2-small_angles[0]-beta)%(360/SMALL_TEETH),
        large_pitch_circle_vertices=len(large_angles),small_pitch_circle_vertices=len(small_angles),
        maximum_large_tooth_phase_error_rad=big_error,maximum_small_tooth_phase_error_rad=small_error,
        maximum_pitch_error_mm=max(abs(math.dist(a,b)-PITCH) for a,b in zip(points,points[1:])),
        closing_error_mm=math.dist(points[0],points[-1]),vertices_world_xz_mm=[world(p) for p in points[:-1]],
        authored_fingerprint=fingerprint(),static_fit_report_sha256=sha(fit_path),script_sha256=sha(__file__),
        transmission_datum_changed=False,native_components_created=False,physical_contacts_qualified=False,
        limitation='Retains the direction to a provisional transmission datum, but derives a new station from50 pitches. Tooth-center alignment alone is not tooth/profile clearance or historical station evidence.')
    write(ROOT/'installed_pitch_route_report.json',result)
    print({k:v for k,v in result.items() if k not in ['vertices_world_xz_mm','authored_fingerprint']})
