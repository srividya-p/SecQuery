# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Utility Method - Get Geodesic Line 
 SecQuery - A QGIS plugin
 This plugin is used to render a geodesic buffers with a specified number of 
 sectors and query the point data in them.
        begin                : 2022-07-31
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Srividya Subramanian
        email                : srividya.ssa@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import math
from geographiclib.geodesic import Geodesic

from qgis.core import (QgsPointXY, QgsGeometry)

from .crs_vars import epsg4326, geodesic
from .utility_functions import conversionFactorToMeters, makeIntDateLineCrossingsPositive

maxSegments = 1000
maxSegmentLength = 20 * 1000.0

def getAngleWithVertical(x1, y1, x2, y2):
    """
    Method to get the angle a point makes with the Y Axis
    """
    dy = y2 - y1
    dx = x2 - x1
    angle = math.atan2(dx, dy)

    if angle < 0:
        angle += 2*math.pi

    return math.degrees(angle)

def getGeodesicLineFeature(lineStartFeature, length, units, azimuth, getCoords=False):
    """
    Method to get a geodesic line feature from line start, length and azimuth
    """
    length_meters = length * conversionFactorToMeters(units)
    point = lineStartFeature.geometry().asPoint()

    g = geodesic.Direct(point.y(), point.x(), azimuth, length_meters)
    angle = getAngleWithVertical(point.x(), point.y(), g['lon2'], g['lat2'])

    geodesic_line = geodesic.Line(point.y(), point.x(), azimuth)
    n = int(math.ceil(length_meters / maxSegmentLength))

    if n > maxSegments:
        n = self.maxSegments
    segmentLength = length_meters / n

    points = [point]
    for i in range(1, n + 1):
        s = segmentLength * i
        g = geodesic_line.Position(s, Geodesic.LATITUDE | Geodesic.LONGITUDE | Geodesic.LONG_UNROLL)
        points.append(QgsPointXY(g['lon2'], g['lat2']))

    makeIntDateLineCrossingsPositive(points)

    if getCoords:
        return points

    lineStartFeature.setGeometry(QgsGeometry.fromPolylineXY(points))

    return lineStartFeature, angle
