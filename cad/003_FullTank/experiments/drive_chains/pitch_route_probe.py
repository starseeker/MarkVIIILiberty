"""Discrete pitch closure of a provisional external two-sprocket chain route.

This is a mathematical preflight, not component geometry or a reconciled BOM.
It keeps the inferred12/23 tooth radii and printed3-inch pitch independent of
the provisional transmission station. No source calibration is changed.
"""
from pathlib import Path
import math
import sys
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.evidence import write,sha

PITCH=76.2
LARGE_TEETH=23
SMALL_TEETH=12
BIG=PITCH/(2*math.sin(math.pi/LARGE_TEETH))
SMALL=PITCH/(2*math.sin(math.pi/SMALL_TEETH))


def route(center_distance):
    alpha=math.acos((BIG-SMALL)/center_distance)
    ca,sa=math.cos(alpha),math.sin(alpha)
    straight=math.sqrt(center_distance**2-(BIG-SMALL)**2)
    sections=[BIG*(2*math.pi-2*alpha),straight,SMALL*2*alpha,straight]
    perimeter=sum(sections)
    def point(distance):
        distance %= perimeter
        if distance<=sections[0]:
            angle=alpha+distance/BIG
            return BIG*math.cos(angle),BIG*math.sin(angle)
        distance-=sections[0]
        if distance<=straight:
            t=distance/straight
            return (1-t)*BIG*ca+t*(center_distance+SMALL*ca),-(1-t)*BIG*sa-t*SMALL*sa
        distance-=straight
        if distance<=sections[2]:
            angle=-alpha+distance/SMALL
            return center_distance+SMALL*math.cos(angle),SMALL*math.sin(angle)
        t=(distance-sections[2])/straight
        return (1-t)*(center_distance+SMALL*ca)+t*BIG*ca,(1-t)*SMALL*sa+t*BIG*sa
    return point,perimeter


def pitches(center_distance,count):
    point,perimeter=route(center_distance)
    station=0.;stations=[station];vertices=[point(station)]
    for _ in range(count):
        start=point(station)
        station=brentq(lambda distance:math.dist(start,point(distance))-PITCH,
                      station+PITCH*.99,station+PITCH*1.1,xtol=1e-10)
        stations.append(station);vertices.append(point(station))
    return station-perimeter,vertices,stations,perimeter


def solve(count):
    # Coplanar pitch circles must at least be separate in this provisional
    # external-sprocket construction. Actual tooth-tip clearance is additional.
    minimum=BIG+SMALL
    maximum=count*PITCH
    lower=pitches(minimum,count)[0];upper=pitches(maximum,count)[0]
    if lower*upper>=0:
        return dict(pitch_count=count,closed_separate_pitch_circle_solution=False,
                    minimum_center_distance_mm=minimum,minimum_distance_closure_residual_mm=lower,
                    interpretation='No solution in this external two-circle model; this does not settle catalogue supply-unit semantics.')
    distance=brentq(lambda separation:pitches(separation,count)[0],minimum,maximum,xtol=1e-9)
    residual,vertices,stations,perimeter=pitches(distance,count)
    lengths=[math.dist(a,b) for a,b in zip(vertices,vertices[1:])]
    closing=math.dist(vertices[-1],vertices[0])
    error=max(abs(length-PITCH) for length in lengths)
    assert error<1e-7 and closing<1e-7 and abs(residual)<1e-7
    return dict(pitch_count=count,closed_separate_pitch_circle_solution=True,
        center_distance_mm=distance,continuous_route_perimeter_mm=perimeter,
        chord_length_mm=PITCH,maximum_pitch_error_mm=error,closing_error_mm=closing,
        vertices_xz_mm=vertices[:-1],station_mm=stations[:-1],
        interpretation='Exact chord closure at one provisional route phase; installed tooth engagement and component fit remain untested.')


if __name__=='__main__':
    result=dict(status='mathematical_route_preflight',pitch_mm=PITCH,large_teeth=LARGE_TEETH,
        small_teeth_inferred=SMALL_TEETH,pitch_radii_mm=dict(large=BIG,small=SMALL),
        handbook_50_pitch_case=solve(50),literal_25_pin_case=solve(25),
        source_bom_reconciled=False,native_components_created=False,
        tooth_phase_and_running_engagement_qualified=False,script_sha256=sha(__file__))
    write(ROOT/'pitch_route_report.json',result)
    for key in ['handbook_50_pitch_case','literal_25_pin_case']:
        print(key,{k:v for k,v in result[key].items() if k not in ['vertices_xz_mm','station_mm']})
