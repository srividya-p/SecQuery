from geographiclib.geodesic import Geodesic
from qgis.core import QgsCoordinateReferenceSystem

epsg4326 = QgsCoordinateReferenceSystem("EPSG:4326")
geodesic = Geodesic.WGS84