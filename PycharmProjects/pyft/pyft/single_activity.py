from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple, Callable, Optional

import gpxpy
import lxml.etree
import pandas as pd
import numpy as np

from gpxpy import gpx

namespaces = {'garmin_tpe': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}


@dataclass
class Activity:
    """ A dataclass representing a single activity.  Stores the points (as a pd.DataFrame),
    as well as some metadata about the activity.  We only separately store data about
    the activity which cannot easily and quickly be deduced from the points."""

    activity_type: str
    date_time: datetime
    points: pd.DataFrame
    distance_2d: float # Could be deduced from points, but relatively expensive
    center: Tuple[float, float]
    activity_id: Optional[int] = None
    matched_prototype_id: Optional[int] = None
    activity_name: Optional[str] = None
    data_file: Optional[str] = None

    @staticmethod
    def from_gpx_file(data_file: str, activity_name: str = None, activity_type: str = 'run') -> 'Activity':
        with open(data_file) as f:
            g = gpxpy.parse(f)
        df = gpx_to_df(g)
        _distance_2d = df['cum_distance_2d'].iloc[-1]
        total_time = df['time'].iloc[-1] - df['time'].iloc[0]
        min_elevation = df['elevation'].min()
        max_elevation = df['elevation'].max()
        center = g.tracks[0].get_center()
        return Activity(
            activity_type=activity_type,
            date_time=g.time,
            points=df,
            distance_2d=_distance_2d,
            total_time=total_time,
            min_elevation=min_elevation,
            max_elevation=max_elevation,
            center=center,
            data_file=data_file,
            activity_name=activity_name
        )


def get_try_func(func: Callable[[gpx.GPXTrackPoint, gpx.GPXTrackPoint], float]) -> Callable[
    [gpx.GPXTrackPoint, gpx.GPXTrackPoint], float]:
    def _try_func(p1: gpx.GPXTrackPoint, p2: gpx.GPXTrackPoint) -> Optional[float]:
        try:
            return func(p1, p2)
        except AttributeError:
            return np.nan

    return _try_func


distance_2d = np.vectorize(get_try_func(lambda p1, p2: p1.distance_2d(p2)))
distance_3d = np.vectorize(get_try_func(lambda p1, p2: p1.distance_3d(p2)))


def get_hr(elem: lxml.etree._Element) -> int:
    return int(elem.find('garmin_tpe:hr', namespaces).text)


def get_cad(elem: lxml.etree._Element) -> int:
    return int(elem.find('garmin_tpe:cad', namespaces).text)


def get_garmin_tpe(point: gpx.GPXTrackPoint) -> lxml.etree._Element:
    for ext in point.extensions:
        if ext.tag.startswith(f'{{{namespaces["garmin_tpe"]}}}'):
            return ext


def _iter_points(g: gpx.GPX):
    for point, track_no, segment_no, point_no in g.walk():
        ext = get_garmin_tpe(point)
        hr = get_hr(ext)
        cad = get_cad(ext)
        yield (
            point_no, track_no, segment_no,
            point.latitude, point.longitude, point.elevation,
            point.time, hr, cad, point
        )


INITIAL_COL_NAMES = (
    'point_no', 'track_no', 'segment_no',
    'latitude', 'longitude', 'elevation',
    'time', 'hr', 'cadence', 'point'
)


def gpx_to_df(g: gpx.GPX) -> pd.DataFrame:
    df = pd.DataFrame(_iter_points(g), columns=INITIAL_COL_NAMES)
    df['prev_point'] = df['point'].shift()
    df['step_length_2d'] = distance_2d(df['point'], df['prev_point'])
    df['cumul_distance_2d'] = df['step_length_2d'].fillna(0).cumsum()
    df['km'] = df['cum_distance_2d'] // 1000
    df['prev_time'] = df['time'].shift()
    df['step_time'] = df['time'] - df['prev_time']
    df['km_pace'] = (1000 / df['step_length_2d']) * (df['time'] - df['step_time'])
    return df.drop(['point', 'prev_point', 'prev_time', 'step_time'], axis=1)
