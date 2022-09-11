# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Utility Methods (Misc) 
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

from string import ascii_uppercase
from qgis.core import (QgsUnitTypes, QgsVectorLayer, QgsFillSymbol)
from qgis.PyQt.QtCore import QCoreApplication

def tr(string):
    return QCoreApplication.translate('@default', string)


UNITS_LABELS = [tr("Centimeters"), tr("Meters"), tr("Kilometers"), tr("Inches"), tr("Feet"), tr("Miles"), tr("Nautical Miles"), tr('Yards')]
DIRECTION_LIST = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

def conversionFactorToMeters(units):
    """
    Method to get conversion factor of a given units to meters
    """
    # Centimeters
    if units == 0:
        measureFactor = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceCentimeters, QgsUnitTypes.DistanceMeters)
    # Meters
    elif units == 1:
        measureFactor = 1.0
    # Kilometers
    elif units == 2:
        measureFactor = 1000.0
    # Inches
    elif units == 3:
        measureFactor = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceFeet, QgsUnitTypes.DistanceMeters) / 12.0
    # Feet
    elif units == 4:
        measureFactor = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceFeet, QgsUnitTypes.DistanceMeters)
    # Miles
    elif units == 5:
        measureFactor = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceMiles, QgsUnitTypes.DistanceMeters)
    # Nautical Miles
    elif units == 6:
        measureFactor = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceNauticalMiles, QgsUnitTypes.DistanceMeters)
    # Yards
    elif units == 7:
        measureFactor = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceYards, QgsUnitTypes.DistanceMeters)
    return measureFactor

def hasIntDateLineCrossing(points):
    """
    Method to check if a points list has points that cross the International Date Line
    """
    points_len = len(points)
    if points_len == 0:
        return False 
    x_last = points[0].x()
    for i in range(1, points_len):
        x = points[i].x()
        if x_last < 0 and x >= 0 and x - x_last > 180:
            return True 
        elif x_last >= 0 and x < 0 and x_last - x > 180:
            return True
    return False

def makeIntDateLineCrossingsPositive(points):
    """
    Method to make points crossing the International Date Line positive in a points list
    """
    if not hasIntDateLineCrossing(points):
        return
    for point in points:
        if point.x() < 0:
            point.setX(x + 360)

def getMemoryLayerFromFeatures(feature, layerType, layerName):
    """
    Utility method to get a memory layer from features
    """
    layer = QgsVectorLayer(layerType, layerName, "memory")
    provider = layer.dataProvider()
    layer.startEditing()
    provider.addFeatures([feature])
    layer.commitChanges()
    return layer

def styleLayer(layer, style):
    """
    Utility method to style a layer with the given style string
    """
    symbol = QgsFillSymbol.createSimple(style)
    layer.renderer().setSymbol(symbol)
    layer.triggerRepaint()
    return layer

def getLabelDict(divisions):
    """
    Utility method to get sector labels for the given number of sectors
    """
    if divisions < 27:
        if divisions == 4:
            dir_with_letter = [f'{l} ({d})' for l, d in zip(ascii_uppercase[0:4], 
                [DIRECTION_LIST[i] for i in range(0, 16, 4)])]
            return {k:v for k, v in zip(range(4), dir_with_letter)}
        
        if divisions == 8:
            dir_with_letter = [f'{l} ({d})' for l, d in zip(ascii_uppercase[0:8], 
                [DIRECTION_LIST[i] for i in range(0, 16, 2)])]
            return {k:v for k, v in zip(range(8), dir_with_letter)}
        
        if divisions == 16:
            dir_with_letter = [f'{l} ({d})' for l, d in zip(ascii_uppercase[0:16], DIRECTION_LIST)]
            return {k:v for k, v in zip(range(16), dir_with_letter)}
        
        return {k:v for k, v in zip(range(divisions), ascii_uppercase[0:divisions])}
    else:
        return {k:v for k, v in zip(range(divisions), [str(n) for n in range(1, divisions + 1)])}