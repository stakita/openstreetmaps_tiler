#!/usr/bin/env python3
#
# GPX file wrapper (pretty unintelligent) for extracting pertinent information from GoPro GPX files.
#
# 2022-06-29
# Simon M Takita <smtakita@gmail.com>
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
#

import sys
import logging
import dateutil.parser as dup

from . import openstreetmaps as osm

try:
    from docopt import docopt
    import xmltodict
except ImportError as e:
    installs = ['docopt', 'xmltodict']
    sys.stderr.write('Error: %s\nTry:\n    pip install --user %s\n' % (e, ' '.join(installs)))
    sys.exit(1)

log = logging.getLogger(__name__)


def to_timestamp(time_string):
    dt = dup.parse(time_string)
    return dt.timestamp()


def gpx_points_to_coordinates(gpx_points):
    return map(lambda p: osm.Coordinate(p['lon'], p['lat']), gpx_points)


def gpx_points_to_coordinate_timestamp_tuples(gpx_points):
    return map(lambda p: (osm.Coordinate(p['lon'], p['lat']), p['time']), gpx_points)


class Gpx:

    def __init__(self, gpx_data):
        log.debug('Parsing gpx_data')
        self.doc = xmltodict.parse(gpx_data)
        self.points = []
        self.stream_start_time = to_timestamp(self.doc['gpx']['metadata']['time'])
        log.debug('Start time: %r' % self.stream_start_time)
        track_points = self.doc['gpx']['trk']['trkseg']['trkpt']
        for point in track_points:
            lat = float(point['@lat'])
            lon = float(point['@lon'])
            timestamp = to_timestamp(point['time'])
            ele = float(point['ele'])
            speed = float(point['extensions']['gpxtpx:TrackPointExtension']['gpxtpx:speed'])
            log.debug('%.3f - lat: %f, lon: %f, ele: %f, speed: %f' % (timestamp, lat, lon, ele, speed))
            element = {}
            element['time'] = timestamp
            element['lat'] = lat
            element['lon'] = lon
            element['ele'] = ele
            element['speed'] = speed
            self.points.append(element)


    def start_time(self):
        return self.stream_start_time


    def all_points(self):
        for point in self.points:
            yield point



if __name__ == '__main__':
    with open('temp.gpx') as fd:
        s = fd.read()
    g = Gpx(s)
    log.info(g.start_time())
    points_iter = g.all_points()
    log.info(next(points_iter))
    log.info(next(points_iter))


# TODO: consider returning points as osm.Coordinate type
