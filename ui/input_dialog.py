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

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'input_dialog.ui'))


class InputDialog(QtWidgets.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        self.data = "Dialog works."
        super(InputDialog, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
