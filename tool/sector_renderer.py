# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SectorRenderer 
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

from qgis.core import (QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, 
                        QgsProject, Qgis, QgsField, QgsTextFormat, QgsPalLayerSettings,
                        QgsVectorLayerSimpleLabeling)
from PyQt5.QtCore import (QVariant)
from PyQt5.QtGui import (QColor, QFont)

import processing
import math
pi = math.pi

from .query_tool import QueryTool
from secquery.ui.input_dialog import InputDialog 
from secquery.utils.geodesic_pie_wedge import getGeodesicPieWedgeFeature
from secquery.utils.geodesic_line import getGeodesicLineFeature
from secquery.utils.utility_functions import getMemoryLayerFromFeatures, styleLayer, DIRECTION_LIST

class SectorRenderer():
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.inp_dialog = InputDialog(self.canvas)
        self.inp_dialog.inputDataSignal.connect(self.processInputDataSignal)
        self.style = {'style': 'no', 'outline_style': 'solid', 'outline_width': '0.5', 'outline_color': 'black'}
        self.progress = 0
        self.divisions = 0
        self.division_length = 0.0
    
    def increaseProgress(self):
        self.progress += 10
        self.inp_dialog.progressBar.setValue(self.progress)

    def getCircleLayer(self, radius, center_x, center_y, units = 1, segments = 30, startAzimuth = 0, endAzimuth = 360):
        center_feature = QgsFeature()
        center_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(center_x, center_y)))
        geodesic_center_feature = getGeodesicPieWedgeFeature(center_feature, radius, 
                    units, segments, startAzimuth, endAzimuth)

        circle = getMemoryLayerFromFeatures(geodesic_center_feature, 
            layerType='Polygon', layerName='Geodesic Buffer')
        
        styled_circle = styleLayer(circle, self.style)

        return styled_circle

    def getSectorLineLayers(self, radius, center_x, center_y, azimuth, units = 1):
        line_layers = []
        center_feature = QgsFeature()
        for n in range(self.divisions):
            center_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(center_x, center_y)))
            geodesic_line_feature = getGeodesicLineFeature(center_feature, 
                radius, units, azimuth)

            line = getMemoryLayerFromFeatures(geodesic_line_feature, 
                layerType='LineString', layerName=f'Radius {n + 1}')
            
            styled_line = styleLayer(line, self.style)
            line_layers.append(styled_line)
            self.increaseProgress()
            azimuth += self.division_length
        
        return line_layers
            
    def getMergedDiameters(self, line_layers):
        parameters = {
            'LAYERS': line_layers, 
            'OUTPUT': "memory:Sectors"
        }

        sectors = processing.run("qgis:mergevectorlayers", parameters)["OUTPUT"]
        sectors.renderer().symbol().setColor(QColor("black"))
        sectors.triggerRepaint()

        return sectors

    def getDirectionLabels(self, radius, center_x, center_y, units = 1, azimuth = 0):
        center_feature = QgsFeature()
        direction_layer = QgsVectorLayer('Point', 'Directions', 'memory')
        direction_provider = direction_layer.dataProvider()
        direction_provider.addAttributes([QgsField("id", QVariant.Int), 
                                          QgsField("direction", QVariant.String)])
        direction_layer.updateFields()

        for i in range(16):
            center_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(center_x, center_y)))
            coords = getGeodesicLineFeature(center_feature, 
                radius * 1.2, units, azimuth, getCoords=True)
            
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(coords[-1]))
            feature.setAttributes([i, DIRECTION_LIST[i]])
            direction_provider.addFeature(feature)
            direction_layer.updateExtents()
            
            azimuth += 22.5

        text_format = QgsTextFormat()
        text_format.setFont(QFont("Arial", 15, weight = QFont.Bold))
        text_format.setSize(15)
        
        label_settings = QgsPalLayerSettings()
        label_settings.enabled = True
        label_settings.fieldName = 'direction'
        label_settings.placement = QgsPalLayerSettings.OverPoint
        label_settings.setFormat(text_format)

        dir_layer_settings = QgsVectorLayerSimpleLabeling(label_settings)
        direction_layer.setLabelsEnabled(True)
        direction_layer.setLabeling(dir_layer_settings)
        direction_layer.triggerRepaint()

        style = {'size':'0'}
        styled_direction_layer = styleLayer(direction_layer, style)

        return direction_layer

    def setLayerCrs(self, points_layer, point_crs):
        if not point_crs.isValid():
            defaultCrs = QgsCoordinateReferenceSystem('EPSG:4326')
            points_layer.setCrs(defaultCrs, True)
        points_layer.setCrs(point_crs, True)

    def processInputDataSignal(self, radius, units, noOfSectors, segments, showLabels, points_layer, point_crs, center_x, center_y):
        self.divisions = noOfSectors
        self.division_length = 360.0 / noOfSectors
        
        circle = self.getCircleLayer(radius, center_x, center_y, units, segments)
        QgsProject.instance().addMapLayer(circle)
        self.increaseProgress()
        
        line_layers = self.getSectorLineLayers(radius, center_x, center_y, self.division_length / 2, units)
        sectors = self.getMergedDiameters(line_layers)
        QgsProject.instance().addMapLayer(sectors)
        self.increaseProgress()

        label_id = None
        if showLabels:
            label_layer = self.getDirectionLabels(radius, center_x, center_y, units)
            QgsProject.instance().addMapLayer(label_layer)
            label_id = label_layer.id()

        self.setLayerCrs(points_layer, point_crs)
        self.inp_dialog.hide()
        self.iface.messageBar().pushMessage("Sectors Drawn",
                                           "Click on the sector for which you want to query places.\nPress 'Q' to Quit.", level=Qgis.Success, duration=3)

        query_places = QueryTool(self.iface, [center_x, center_y], 
                radius, units, segments, self.divisions, self.division_length, sectors.id(), circle.id(), label_id, points_layer)
        self.canvas.setExtent(label_layer.extent() if showLabels else circle.extent())
        self.canvas.setMapTool(query_places)

    def run(self):
        self.inp_dialog.exec_()