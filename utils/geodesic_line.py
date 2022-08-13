import math
from geographiclib.geodesic import Geodesic

from qgis.core import (
    QgsPointXY, QgsGeometry)

from .crs_vars import epsg4326, geodesic
from .utility_functions import conversionFactorToMeters, makeIntDateLineCrossingsPositive

maxSegments = 1000
maxSegmentLength = 20 * 1000.0

def getGeodesicLineFeature(lineStartFeature, length, units, azimuth):
    length_meters = length * conversionFactorToMeters(units)
    
    point = lineStartFeature.geometry().asPoint()
    point_orig_x, point_orig_y = point.x(), point.y()

    geodesic_line = geodesic.Line(point.y(), point.x(), azimuth)
    n = int(math.ceil(length / maxSegmentLength))

    if n > maxSegments:
        n = self.maxSegments
    segmentLength = length / n

    points = [point]
    for i in range(1, n + 1):
        s = segmentLength * i
        g = geodesic_line.Position(s, Geodesic.LATITUDE | Geodesic.LONGITUDE | Geodesic.LONG_UNROLL)
        points.append(QgsPointXY(g['lon2'], g['lat2']))

    makeIntDateLineCrossingsPositive(points)
    lineStartFeature.setGeometry(QgsGeometry.fromPolylineXY(points))

    return lineStartFeature
    