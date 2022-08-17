# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QueryTool 
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
                        QgsStyle, QgsProject)
from qgis.gui import (QgsMapTool, QgsMapToolEmitPoint)
from PyQt5.QtWidgets import (QMessageBox)

import processing

from secquery.utils.geodesic_pie_wedge import getGeodesicPieWedgeFeature
from secquery.utils.geodesic_line import getAngleWithVertical
from secquery.utils.utility_functions import getMemoryLayerFromFeatures, styleLayer, getLabelDict

class QueryTool(QgsMapTool):
    def __init__(self, iface, center_point, radius, units, segments, divisions, 
                division_length, merged_diameters_id, sector_angles, circle_id, label_id, points_layer):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.center_x = center_point[0]
        self.center_y = center_point[1]
        self.radius = radius
        self.units = units
        self.segments = segments
        self.divisions = divisions
        self.division_length = division_length
        self.circle_id = circle_id
        self.merged_diameters_id = merged_diameters_id
        self.sector_angles = sector_angles
        self.label_id = label_id

        self.sector_layer = QgsVectorLayer()
        self.points_layer = points_layer
        self.prev_id = None
        self.memory_layers = []
        
        self.label_dict = getLabelDict(self.divisions)
        
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def clearCanvas(self):
        QgsProject.instance().removeMapLayer(self.circle_id)
        QgsProject.instance().removeMapLayer(self.merged_diameters_id)
        if self.label_id:
            QgsProject.instance().removeMapLayer(self.label_id)
        for layer_id in self.memory_layers:
            QgsProject.instance().removeMapLayer(layer_id)

    def clearSector(self):
        if self.sector_layer.id():
            QgsProject.instance().removeMapLayer(self.sector_layer.id())
            self.sector_layer = QgsVectorLayer()

    def hidePrevQueriedPointLayer(self):
        if self.prev_id != None:
            prevLayer = QgsProject.instance().layerTreeRoot().findLayer(self.prev_id)
            prevLayer.setItemVisibilityChecked(False)

    def getAzimuthRangeFromSectorNumber(self, n):
        startAzimuth = n * self.division_length - self.division_length / 2
        endAzimuth = n * self.division_length + self.division_length / 2

        if startAzimuth < 0: startAzimuth += 360.0
        if endAzimuth < 0: endAzimuth += 360.0

        return startAzimuth, endAzimuth

    def drawSector(self, n, sector_name):
        center_feature = QgsFeature()
        center_feature.setGeometry(QgsGeometry.fromPointXY(
            QgsPointXY(self.center_x, self.center_y)))
        startAzimuth, endAzimuth = self.getAzimuthRangeFromSectorNumber(n)
        geodesic_center_feature = getGeodesicPieWedgeFeature(center_feature, self.radius, 
                    self.units, self.segments, startAzimuth, endAzimuth)

        sector = getMemoryLayerFromFeatures(geodesic_center_feature, 
            layerType='Polygon', layerName=f'Sector {sector_name}')
        
        style = {'style': 'no', 'outline_style': 'solid', 'outline_width': '0.7', 'outline_color': 'blue'}
        styled_sector = styleLayer(sector, style)
        QgsProject.instance().addMapLayer(styled_sector)
        self.sector_layer = styled_sector

    def identifySector(self, x, y):
        angle = getAngleWithVertical(self.center_x, self.center_y, x, y)
        
        if ((angle >= 0 and angle < self.sector_angles[0]) or 
            (angle >= self.sector_angles[-1] and angle <= 360)):
            return 0
        
        for i in range(self.divisions - 1):
            if angle >= self.sector_angles[i] and angle < self.sector_angles[i + 1]:
                return i + 1

    def generateQueriedPointsLayer(self, sector_name):
        layer_name = f'Sector {sector_name} Center ({self.center_x:.3f}, {self.center_y:.3f}) Points'
        existing_layers = QgsProject.instance().mapLayersByName(layer_name)

        if len(existing_layers) > 0:
            self.prev_id = existing_layers[0].id()
            prevLayer = QgsProject.instance().layerTreeRoot().findLayer(self.prev_id)
            prevLayer.setItemVisibilityChecked(True)
            self.iface.showAttributeTable(existing_layers[0])
            return

        sector_points = QgsVectorLayer('Point', layer_name, 'memory')
        join_features = []
        feature_count = 0

        for a in self.sector_layer.getFeatures():
            for b in self.points_layer.getFeatures():
                if a.geometry().contains(b.geometry()):
                    join_features.append(b)
                    feature_count += 1

        if feature_count == 0:
            QMessageBox().information(None, "SecQuery", f"<h3>Sector {sector_name}</h3> <p>No Location Points found!</p>")
            return

        sector_points_provider = sector_points.dataProvider()
        attributes = self.points_layer.dataProvider().fields().toList()
        sector_points_provider.addAttributes(attributes)
        sector_points.updateFields()
        sector_points_provider.addFeatures(join_features)

        selected_symbol = QgsStyle.defaultStyle().symbol('honeycomb faux 3d')
        selected_symbol.setSize(2.8)
        sector_points.renderer().setSymbol(selected_symbol)
        sector_points.triggerRepaint()
                
        self.prev_id = sector_points.id()
        QgsProject.instance().addMapLayer(sector_points)
        self.memory_layers.append(sector_points.id())
        self.iface.showAttributeTable(sector_points)        
        
    def canvasPressEvent(self, e):
        self.clearSector()
        self.hidePrevQueriedPointLayer()

        click_point = self.toMapCoordinates(self.canvas.mouseLastXY())
        x, y = click_point[0], click_point[1]

        n = self.identifySector(x, y)
        sector_name = self.label_dict[n]
        self.drawSector(n, sector_name)
        self.generateQueriedPointsLayer(sector_name)

    def keyReleaseEvent(self, e):
        try:
            if(chr(e.key()) == 'Q'):
                ret = QMessageBox.question(None, '', "Do you want to clear all Scratch Layers before quitting?", 
                        QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    warning_ret = QMessageBox.warning(None, '', "The following operation will permanently remove all Scratch Layers. Do you wish to Proceed?",
                        QMessageBox.Yes | QMessageBox.No)
                    if warning_ret == QMessageBox.Yes:
                        self.clearSector()
                        self.clearCanvas()
                self.canvas.unsetMapTool(self)
        except ValueError:
            pass