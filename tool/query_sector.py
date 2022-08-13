# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuerySectorPlaces 
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
from secquery.utils.geodesic_pie_wedge import getGeodesicPieWedgeFeature
from secquery.utils.utility_functions import getMemoryLayerFromFeatures, styleLayer, getLabelDict

class QuerySectorPlaces(QgsMapTool):
    def __init__(self, iface, center_point, radius, merged_diameters_id, circle_id, points_layer):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.center_x = center_point[0]
        self.center_y = center_point[1]
        self.radius = radius
        self.circle_id = circle_id
        self.merged_diameters_id = merged_diameters_id

        self.sector_layer = QgsVectorLayer()
        self.points_layer = points_layer
        self.prev_id = None
        self.memory_layers = []
        
        self.label_dict = getLabelDict(DIVISIONS)
        
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def clearCanvas(self):
        QgsProject.instance().removeMapLayer(self.circle_id)
        QgsProject.instance().removeMapLayer(self.merged_diameters_id)
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

    def drawSector(self, n):
        arc_start = [self.center_x+(self.radius*math.cos((2*n*pi + pi)/16)),
                     self.center_y+(self.radius*math.sin((2*n*pi + pi)/16))]
        arc_end = [self.center_x+(self.radius*math.cos((2*(n+1)*pi + pi)/16)),
                   self.center_y+(self.radius*math.sin((2*(n+1)*pi + pi)/16))]
        arc_mid = [self.center_x+(self.radius*math.cos((2*n*pi + 2*(n+1)*pi + pi)/32)),
                   self.center_y+(self.radius*math.sin((2*n*pi + 2*(n+1)*pi + pi)/32))]

        arc = QgsVectorLayer(
            "LineString?crs=epsg:4326&field=id:integer&field=name:string(20)&index=yes", "line", "memory")
        arc_geom = QgsCircularString()
        arc_geom.setPoints([
            QgsPoint(arc_start[0], arc_start[1]),
            QgsPoint(arc_mid[0], arc_mid[1]),
            QgsPoint(arc_end[0], arc_end[1])]
        )
        arc_feature = QgsFeature()
        arc_feature.setGeometry(QgsGeometry(arc_geom))

        line1_start = QgsPointXY(self.center_x, self.center_y)
        line1_mid = QgsPointXY(
            (self.center_x+arc_start[0])/2, (self.center_y+arc_start[1])/2)
        line1_end = QgsPointXY(arc_start[0], arc_start[1])
        line1 = QgsVectorLayer("LineString", "line", "memory")
        seg1 = QgsFeature()
        seg1.setGeometry(QgsGeometry.fromPolylineXY(
            [line1_start, line1_mid, line1_end]))

        line2_start = QgsPointXY(self.center_x, self.center_y)
        line2_mid = QgsPointXY(
            (self.center_x+arc_end[0])/2, (self.center_y+arc_end[1])/2)
        line2_end = QgsPointXY(arc_end[0], arc_end[1])
        line2 = QgsVectorLayer("LineString", "line", "memory")
        seg2 = QgsFeature()
        seg2.setGeometry(QgsGeometry.fromPolylineXY(
            [line2_start, line2_mid, line2_end]))

        merged = QgsVectorLayer("LineString", "Sector "+str(n+1), "memory")
        provider = merged.dataProvider()

        merged.startEditing()
        provider.addFeatures([seg1])
        provider.addFeatures([seg2])
        provider.addFeatures([arc_feature])
        merged.commitChanges()

        sector = processing.run("qgis:polygonize", {
                                'INPUT': merged, 'OUTPUT': 'memory:Sector '+str(n+1)})["OUTPUT"]

        QgsProject.instance().addMapLayer(sector)
        symbol = QgsFillSymbol.createSimple(
            {'style': 'no', 'outline_style': 'solid', 'outline_width': '0.7', 'outline_color': 'blue'})
        sector.renderer().setSymbol(symbol)
        sector.triggerRepaint()

        self.sector_layer = sector

    def identifySector(self, x, y):
        dy = y - self.center_y
        dx = x - self.center_x
        angle = math.atan2(dx, dy)
        angle += pi / DIVISIONS

        if angle < 0:
            angle += 2*pi

        sector_num = int(angle//((2*pi) / DIVISIONS))
        return sector_num

    def querySectorPoints(self, sector_name):
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
        print (f'Sector - ({x:.4f}, {y:.4f})')

        n = self.identifySector(x, y)
        print(n)
        # self.drawSector(n)
        # self.querySectorPoints(self.label_dict[n])

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