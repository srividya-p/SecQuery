# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DrawSectorCircle 
 SecQuery - A QGIS plugin
 This plugin is used to render a circle with 16 wind-rose sectors and query 
 the data in them.
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

from qgis.core import *
from qgis.gui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import processing
import math
pi = math.pi

from .query_sector import QuerySectorPlaces
from secquery.ui.input_dialog import InputDialog 

class DrawSectorCircle():
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.inpDialog = InputDialog(self.canvas)
        self.inpDialog.inputDataSignal.connect(self.processInputDataSignal)
        self.progress = 0
    
    def increaseProgress(self):
        self.progress += 10
        self.inpDialog.progressBar.setValue(self.progress)

    def getCircleLayer(self, radius, centerX, centerY):
        circle = QgsVectorLayer("Polygon", "Circle", "memory")
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(
            QgsPointXY(centerX, centerY)).buffer(radius, 20))
        provider = circle.dataProvider()
        circle.startEditing()
        provider.addFeatures([feature])
        circle.commitChanges()

        symbol = QgsFillSymbol.createSimple(
            {'style': 'no', 'outline_style': 'solid', 'outline_width': '0.5', 'outline_color': 'black'})
        circle.renderer().setSymbol(symbol)
        circle.triggerRepaint()

        return circle

    def getSectorLineLayers(self, radius, centerX, centerY):
        line_layers = []
        for n in range(8):
            line_start = QgsPointXY(centerX-(radius*math.cos((2*n*pi + pi)/16)),
                                    centerY-(radius*math.sin((2*n*pi + pi)/16)))
            line_end = QgsPointXY(centerX+(radius*math.cos((2*n*pi + pi)/16)),
                                  centerY+(radius*math.sin((2*n*pi + pi)/16)))

            line = QgsVectorLayer("LineString", "Diameter "+str(n+1), "memory")
            seg = QgsFeature()
            seg.setGeometry(QgsGeometry.fromPolylineXY([line_start, line_end]))
            provider = line.dataProvider()
            line.startEditing()
            provider.addFeatures([seg])
            line.commitChanges()

            line.renderer().symbol().setColor(QColor("black"))
            line.triggerRepaint()

            line_layers.append(line)
            self.increaseProgress()
        
        return line_layers
            
    def getMergedDiameters(self, line_layers):
        parameters = {
            'LAYERS': line_layers, 
            'OUTPUT': "memory:Diameters"
        }

        merged_diameters = processing.run("qgis:mergevectorlayers", parameters)["OUTPUT"]
        merged_diameters.renderer().symbol().setColor(QColor("black"))
        merged_diameters.triggerRepaint()

        return merged_diameters

    def setLayerCrs(self, pointsLayer, pointCrs):
        if not pointCrs.isValid():
            defaultCrs = QgsCoordinateReferenceSystem('EPSG:4326')
            pointsLayer.setCrs(defaultCrs, True)
        pointsLayer.setCrs(pointCrs, True)

    def processInputDataSignal(self, radius, pointsLayer, pointCrs, centerX, centerY):
        circle = self.getCircleLayer(radius, centerX, centerY)
        QgsProject.instance().addMapLayer(circle)
        self.increaseProgress()
        
        line_layers = self.getSectorLineLayers(radius, centerX, centerY)
        merged_diameters = self.getMergedDiameters(line_layers)
        QgsProject.instance().addMapLayer(merged_diameters)
        self.increaseProgress()

        self.setLayerCrs(pointsLayer, pointCrs)
        self.inpDialog.hide()
        self.iface.messageBar().pushMessage("Sectors Drawn",
                                           "Click on the sector for which you want to query places.\nPress 'Q' to Quit.", level=Qgis.Success, duration=3)

        query_places = QuerySectorPlaces(self.iface, [centerX, centerY], 
                radius, merged_diameters.id(), circle.id(), pointsLayer)
        
        self.iface.mapCanvas().setMapTool(query_places)

    def run(self):
        self.inpDialog.exec_()

