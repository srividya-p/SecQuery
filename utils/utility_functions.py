from string import ascii_uppercase
from qgis.core import (QgsUnitTypes, QgsVectorLayer, QgsFillSymbol)
from qgis.PyQt.QtCore import QCoreApplication

def tr(string):
    return QCoreApplication.translate('@default', string)


UNITS_LABELS = [tr("Centimeters"), tr("Meters"), tr("Kilometers"), tr("Inches"), tr("Feet"), tr("Miles"), tr("Nautical Miles"), tr('Yards')]
DIRECTION_LIST = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

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

def getLabelDict(divisions):
    if divisions < 27:
        if divisions == 4:
            return {0: 'A (N)', 1:'B (E)', 2:'C (S)', 3:'D (W)'}
        
        if divisions == 8:
            return {0: 'A (N)', 1:'B (NE)', 2:'C (E)', 3:'D (SE)', 4: 'E (S)', 5:'F (SW)', 6:'G (W)', 7:'H (SW)'}
        
        if divisions == 16:
            dir_with_letter = [f'{l} ({d})' for l, d in zip(ascii_uppercase[0:16], DIRECTION_LIST)]
            # return {0:'A (N)', 1:'B (NNE)', 2:'C (NE)', 3:'D (ENE)', 4:'E (E)', 5:'F (ESE)', 6:'G (SE)', 7:'H (SSE)',
            #                 8:'I (S)', 9:'J (SSW)', 10:'K (SW)', 11:'L (WSW)', 12:'M (W)', 13:'N (WNW)', 14:'O (NW)', 15:'P (NNW)'}
            return {k:v for k, v in zip(range(16), dir_with_letter)}
        return {k:v for k, v in zip(range(divisions), ascii_uppercase[0:divisions])}
    else:
        return {k:v for k, v in zip(range(divisions), [str(n) for n in range(divisions)])}