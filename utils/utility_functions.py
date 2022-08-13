from qgis.core import (QgsUnitTypes, QgsVectorLayer, QgsFillSymbol)
from qgis.PyQt.QtCore import QCoreApplication

def tr(string):
    return QCoreApplication.translate('@default', string)


DISTANCE_LABELS = [tr("Centimeters"), tr("Meters"), tr("Kilometers"), tr("Inches"), tr("Feet"), tr("Miles"), tr("Nautical Miles"), tr('Yards')]

def conversionFactorToMeters(units):
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
    if not hasIntDateLineCrossing(points):
        return
    for point in points:
        if point.x() < 0:
            point.setX(x + 360)

def getMemoryLayerFromFeatures(feature, layerType, layerName):
    layer = QgsVectorLayer(layerType, layerName, "memory")
    provider = layer.dataProvider()
    layer.startEditing()
    provider.addFeatures([feature])
    layer.commitChanges()
    return layer

def styleLayer(layer, style):
    symbol = QgsFillSymbol.createSimple(style)
    layer.renderer().setSymbol(symbol)
    layer.triggerRepaint()
    return layer
