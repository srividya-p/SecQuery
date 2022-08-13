import os
from geographiclib.geodesic import Geodesic

from qgis.core import (
    QgsPointXY, QgsGeometry, QgsProject)

from .crs_vars import epsg4326, geodesic
from .utility_functions import conversionFactorToMeters, makeIntDateLineCrossingsPositive, DISTANCE_LABELS

def getGeodesicPieWedgeFeature(centerFeature, radius, units, segments, startAzimuth, endAzimuth):
    radius_meters = radius * conversionFactorToMeters(units)
    point_spacing = 360.0 / segments

    s_angle = startAzimuth % 360
    e_angle = 360 if endAzimuth == 360 else endAzimuth % 360
    if s_angle > e_angle:
        s_angle -= 360.0

    points = []
    point = centerFeature.geometry().asPoint()
    point_orig_x, point_orig_y = point.x(), point.y()
    
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

