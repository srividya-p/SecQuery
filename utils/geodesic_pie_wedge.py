# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Utility Method - Get Geodesic Pie Wedge 
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

import os
from geographiclib.geodesic import Geodesic

from qgis.core import (
    QgsPointXY, QgsGeometry, QgsProject)

from .crs_vars import epsg4326, geodesic
from .utility_functions import conversionFactorToMeters, makeIntDateLineCrossingsPositive

def getGeodesicPieWedgeFeature(centerFeature, radius, units, segments, startAzimuth, endAzimuth):
    """
    Method to get a geodesic pie wedge feature from center, radius, start and end azimuth
    """
    radius_meters = radius * conversionFactorToMeters(units)
    point_spacing = 360.0 / segments

    s_angle = startAzimuth % 360
    e_angle = 360 if endAzimuth == 360 else endAzimuth % 360
    if s_angle > e_angle:
        s_angle -= 360.0

    points = []
    point = centerFeature.geometry().asPoint()
    
    if e_angle != 360.0:
        points.append(point)

    while s_angle < e_angle:
        g = geodesic.Direct(point.y(), point.x(), s_angle, radius_meters, Geodesic.LATITUDE | Geodesic.LONGITUDE)
        points.append(QgsPointXY(g['lon2'], g['lat2']))
        s_angle += point_spacing

    g = geodesic.Direct(point.y(), point.x(), e_angle, radius_meters, Geodesic.LATITUDE | Geodesic.LONGITUDE)
    points.append(QgsPointXY(g['lon2'], g['lat2']))
    
    if e_angle != 360.0:
        points.append(point)

    makeIntDateLineCrossingsPositive(points)
    centerFeature.setGeometry(QgsGeometry.fromPolygonXY([points]))

    return centerFeature

