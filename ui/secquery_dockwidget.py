# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SecQueryDockWidget 
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

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'secquery_dockwidget_base.ui'))

class SecQueryDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """
        Init DockWidget
        """
        super(SecQueryDockWidget, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        """
        Handle close event
        """
        self.closingPlugin.emit()
        event.accept()