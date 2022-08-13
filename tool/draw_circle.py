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

from qgis.core import *
from qgis.gui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import processing
import math
pi = math.pi

from .sector_config import DIVISIONS, DIVISION_LENGTH
from .query_sector import QuerySectorPlaces
from secquery.ui.input_dialog import InputDialog 
from secquery.utils.geodesic_pie_wedge import getGeodesicPieWedgeFeature
from secquery.utils.geodesic_line import getGeodesicLineFeature
from secquery.utils.utility_functions import getMemoryLayerFromFeatures, styleLayer

class SectorRenderer():
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.inp_dialog = InputDialog(self.canvas)
        self.inp_dialog.inputDataSignal.connect(self.processInputDataSignal)
        self.style = {'style': 'no', 'outline_style': 'solid', 'outline_width': '0.5', 'outline_color': 'black'}
        self.progress = 0
    
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

    def getSectorLineLayers(self, radius, center_x, center_y, units = 1, azimuth = DIVISION_LENGTH / 2):
        line_layers = []
        center_feature = QgsFeature()
        for n in range(DIVISIONS):
            center_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(center_x, center_y)))
            geodesic_line_feature = getGeodesicLineFeature(center_feature, 
                radius, units, azimuth)

            line = getMemoryLayerFromFeatures(geodesic_line_feature, 
                layerType='LineString', layerName=f'Radius {n + 1}')
            
            styled_line = styleLayer(line, self.style)
            line_layers.append(styled_line)
            self.increaseProgress()
            azimuth += DIVISION_LENGTH
        
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

    def getDirectionLabels(self):
        print('Drawing Labels...')

    def setLayerCrs(self, points_layer, point_crs):
        if not point_crs.isValid():
            defaultCrs = QgsCoordinateReferenceSystem('EPSG:4326')
            points_layer.setCrs(defaultCrs, True)
        points_layer.setCrs(point_crs, True)

    def processInputDataSignal(self, radius, units, segments, showLabels, points_layer, point_crs, center_x, center_y):
        circle = self.getCircleLayer(radius, center_x, center_y, units, segments)
        QgsProject.instance().addMapLayer(circle)
        self.increaseProgress()
        
        line_layers = self.getSectorLineLayers(radius, center_x, center_y, units)
        sectors = self.getMergedDiameters(line_layers)
        QgsProject.instance().addMapLayer(sectors)
        self.increaseProgress()

        # if showLabels:
        #     label_layer = self.getDirectionLabels()

        self.setLayerCrs(points_layer, point_crs)
        self.inp_dialog.hide()
        self.iface.messageBar().pushMessage("Sectors Drawn",
                                           "Click on the sector for which you want to query places.\nPress 'Q' to Quit.", level=Qgis.Success, duration=3)

        query_places = QuerySectorPlaces(self.iface, [center_x, center_y], 
                radius, units, segments, sectors.id(), circle.id(), points_layer)
        self.canvas.setExtent(circle.extent())
        self.canvas.setMapTool(query_places)

    def run(self):
        self.inp_dialog.exec_()