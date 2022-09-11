# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InputDialog 
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

import os

from qgis.core import *
from qgis.gui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

from secquery.utils.utility_functions import UNITS_LABELS

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'input_dialog.ui'))


class InputDialog(QtWidgets.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()
    inputDataSignal = pyqtSignal(float, int, int, int, bool, QgsVectorLayer, QgsCoordinateReferenceSystem, float, float)

    def __init__(self, canvas, parent=None):
        """
        Init InputDialog
        """
        super(InputDialog, self).__init__(parent)
        self.setupUi(self)

        self.canvas = canvas
        self.pointTool = QgsMapToolEmitPoint(self.canvas)
        self.renderContext = QgsRenderContext().fromMapSettings(self.canvas.mapSettings())
        
        self.unitsCombobox.addItems(UNITS_LABELS)
        self.unitsCombobox.setCurrentText('Meters')

        self.crsSelect.setOptionVisible(5, False)
        self.crsSelect.setOptionVisible(1, False)
        self.crsSelect.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))

        self.layerCombobox.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.layerCombobox.setShowCrs(True)

        self.pointTool.canvasClicked.connect(self.getPoint)
        self.mapCoordButton.clicked.connect(self.mapClick)

        self.centerXInput.setValidator(QDoubleValidator())
        self.centerYInput.setValidator(QDoubleValidator())

        generateButton = QPushButton(self.tr("&Generate Sectors"))
        generateButton.setDefault(True)

        closeButton = QPushButton(self.tr("&Close"))
        closeButton.setDefault(True)
        
        self.buttonBox.addButton(generateButton, QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(closeButton, QDialogButtonBox.RejectRole)
        self.buttonBox.rejected.connect(lambda: self.close())
        self.buttonBox.accepted.connect(self.emitInputData)

        self.textShortHelp.setText("<h1>SecQuery</h1> <b>General:</b><br>"\
                "This tool is used to render geodesic buffers with a specified number of sectors and query the point data in them."\
                "Buffer radius can be specified in cm, m, km, in, ft, mi, nmi or yd."\
                "The tool also provides the functionality of displaying 16 directional labels." \
                "The buffer, sectors and direction labels are added as Memory Layers.<br><br>"\
                "<b>Parameters (required):</b><br>"\
                "Following Parameters must be set to run the tool:"\
                "<ul><li>Radius</li><li>Radius Units</li><li>Number of Sectors</li><li>Center Coordinates</li><li>Point Layer</li></ul><br>"\
                "<b>Parameters (optional):</b><br>"\
                "There are also a number of <i>optional parameters which can be set:"\
                "<ul><li>Show direction label flag</li><li>Buffer Segments</li><li>Point Layer CRS</li></ul><br>"\
                "<b>Output:</b><br>"\
                "The output of the tool are two Layers - Buffer and Sectors. A map tool is also set to query the data in these sectors." \
                "The queried data is added as a Memory layer."
        )

    def isCenterValid(self, centerXText, centerYText):
        """
        Method to check if manually entered center coordinates are valid
        """
        if centerXText == '' or centerYText == '':
            self.statusLabel.setText('Please select a center point.')
            self.statusLabel.setStyleSheet('color: red')
            return False, 0, 0

        return True, float(centerXText), float(centerYText)

    def mapClick(self):
        """
        Method to set MapTool
        """
        self.statusLabel.setText('')
        self.hide()
        self.canvas.setMapTool(self.pointTool)

    def getPoint(self, point):
        """
        Method to get map click coordinates via MapTool
        """
        self.show()
        self.centerXInput.setText(str(point[0]))
        self.centerYInput.setText(str(point[1]))
        self.canvas.unsetMapTool(self.pointTool)

    def emitInputData(self):
        """
        Method to call processInputDataSignal with required input fields
        """
        radius = self.radiusInput.value()
        units = self.unitsCombobox.currentIndex()
        noOfSectors = self.noOfSectorsInput.value()
        segments = self.segmentsInput.value()
        showLabels = self.labelCheckbox.isChecked()
        pointsLayer = self.layerCombobox.currentLayer()
        pointCrs = self.crsSelect.crs()
        centerXText = self.centerXInput.text()
        centerYText = self.centerYInput.text()

        centerValid, centerX, centerY = self.isCenterValid(centerXText, centerYText)
        if not centerValid:
            return

        self.inputDataSignal.emit(radius, units, noOfSectors, segments, showLabels, pointsLayer, pointCrs, centerX, centerY)
    
    def closeEvent(self, event):
        """
        Handle close event
        """
        self.closingPlugin.emit()
        event.accept()
