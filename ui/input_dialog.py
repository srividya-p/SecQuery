# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InputDialog 
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

import os

from qgis.core import *
from qgis.gui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'input_dialog.ui'))


class InputDialog(QtWidgets.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, canvas, parent=None):
        """Constructor."""
        super(InputDialog, self).__init__(parent)
        self.setupUi(self)

        self.canvas = canvas
        self.pointTool = QgsMapToolEmitPoint(self.canvas)
        self.radius = 0
        self.pointLayer = QgsVectorLayer()
        self.center = QgsPointXY()
        
        self.radiusInput.setValidator(QDoubleValidator(bottom = 0.1, decimals = 2))
        self.radiusInput.setPlaceholderText("Enter a decimal value above 0.1")

        self.crsSelect.setOptionVisible(self.crsSelect.CrsNotSet, True)
        self.crsSelect.setNotSetText('Select a CRS')

        self.layerCombobox.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.layerCombobox.setShowCrs(True)

        self.pointTool.canvasClicked.connect(self.getPoint)
        self.mapCoordButton.clicked.connect(self.mapClick)

        generateButton = QPushButton(self.tr("&Generate Sectors"))
        generateButton.setDefault(True)

        closeButton = QPushButton(self.tr("&Close"))
        closeButton.setDefault(True)
        
        self.buttonBox.rejected.connect(lambda: self.close())
        self.buttonBox.addButton(generateButton, QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(closeButton, QDialogButtonBox.RejectRole)

        self.textShortHelp.setText("<h1>SecQuery</h1> <b>General:</b><br>"\
                "This algorithm implements the Dijkstra-Search to return the <b>shortest path between two points</b> on a given <b>network dataset</b>.<br>"\
                "It accounts for <b>points outside of the network</b> (eg. <i>non-network-elements</i>) and calculates "\
                "<b>separate entry-</b> and <b>exit-costs</b>. Distances are measured accounting for <b>ellipsoids</b>.<br><br>"\
                "<b>Parameters (required):</b><br>"\
                "Following Parameters must be set to run the algorithm:"\
                "<ul><li>Network Layer</li><li>Startpoint Coordinates</li><li>Endpoint Coordinates</li><li>Cost Strategy</li></ul><br>"\
                "<b>Parameters (optional):</b><br>"\
                "There are also a number of <i>optional parameters</i> to implement <b>direction dependent</b> shortest paths and provide information on <b>speeds</b> on the networks edges."\
                "<ul><li>Direction Field</li><li>Value for forward direction</li><li>Value for backward direction</li><li>Value for both directions</li><li>Default direction</li><li>Speed Field</li><li>Default Speed (affects entry/exit costs)</li><li>Topology tolerance</li></ul><br>"\
                "<b>Output:</b><br>"\
                "The output of the algorithm is a Layer containing a <b>single linestring</b>, the attributes showcase the"\
                "<ul><li>Name and coordinates of startpoint</li><li>Name and coordinates of endpoint</li><li>Entry-cost to enter network</li><li>Exit-cost to exit network</li><li>Cost of shortest path on graph</li><li>Total cost as sum of all cost elements</li></ul>")

    def isInputValid(self):
        self.txtLog.append('Validating input...')
        rInp = self.radiusInput.text()
        radiusKm = 0.1 if float(rInp) < 0.1 else float(rInp)
        renderContext = QgsRenderContext().fromMapSettings(self.canvas.mapSettings())
        self.radius = renderContext.convertMetersToMapUnits(radiusKm * 1000)
        self.txtLog.append(f'Radius converted from {radiusKm} km to {self.radius} map units.')


        # self.crsSelect.setCrs(QgsCoordinateReferenceSystem("EPS6:4326"))

    def emitInputData(self):
        if self.isInputValid():
            pass
    
    def mapClick(self):
        self.hide()
        self.canvas.setMapTool(self.pointTool)

    def getPoint(self, point):
        self.x, self.y = point[0], point[1]
        self.show()
        self.centerPointInput.setText(f"{self.x}, {self.y}")
        self.canvas.unsetMapTool(self.pointTool)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
