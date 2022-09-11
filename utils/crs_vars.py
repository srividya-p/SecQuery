# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Declare CRS Variables 
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

from geographiclib.geodesic import Geodesic
from qgis.core import QgsCoordinateReferenceSystem

epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")
geodesic = Geodesic.WGS84