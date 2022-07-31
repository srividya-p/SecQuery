from qgis.core import *
from qgis.gui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import importlib.util
import math
pi = math.pi

approot = QgsProject.instance().homePath()

query_spec = importlib.util.spec_from_file_location("query_sector", approot+"/query-places/query_sector.py")
query_sector_file = importlib.util.module_from_spec(query_spec)
query_spec.loader.exec_module(query_sector_file)

tool_spec = importlib.util.spec_from_file_location("tool", approot+"/utils/switch_tools.py")
tool_file = importlib.util.module_from_spec(tool_spec)
tool_spec.loader.exec_module(tool_file)

class DrawSectorCircle(QgsMapTool):
    def __init__(self, canvas, iface):
        self.canvas = canvas
        self.iface = iface
        self.x = 0
        self.y = 0
        self.circle = QgsVectorLayer()
        self.line_layers = []
        self.toolPan = tool_file.switchPanTool(self.canvas, self.iface, 'draw')
        self.toolZoomIn = tool_file.switchZoomTool(self.canvas, self.iface, False, 'draw')
        self.toolZoomOut = tool_file.switchZoomTool(self.canvas, self.iface, True, 'draw')
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def clearCanvas(self):
        if(len(self.line_layers) > 0):
            for line in self.line_layers:
                QgsProject.instance().removeMapLayer(line.id())

            QgsProject.instance().removeMapLayer(self.circle.id())

            self.line_layers = []
            self.circle = QgsVectorLayer()

    def drawCircle(self, radius):
        circle = QgsVectorLayer("Polygon", "Circle", "memory")
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(
            QgsPointXY(self.x, self.y)).buffer(radius, 20))
        provider = circle.dataProvider()
        circle.startEditing()
        provider.addFeatures([feature])
        circle.commitChanges()

        symbol = QgsFillSymbol.createSimple(
            {'style': 'no', 'outline_style': 'solid', 'outline_width': '0.5', 'outline_color': 'black'})
        circle.renderer().setSymbol(symbol)
        circle.triggerRepaint()

        self.circle = circle
        QgsProject.instance().addMapLayer(circle)

    def drawSectorLines(self, radius):
        line_layers = []
        for n in range(8):
            line_start = QgsPointXY(self.x-(radius*math.cos((2*n*pi + pi)/16)),
                                    self.y-(radius*math.sin((2*n*pi + pi)/16)))
            line_end = QgsPointXY(self.x+(radius*math.cos((2*n*pi + pi)/16)),
                                  self.y+(radius*math.sin((2*n*pi + pi)/16)))

            line = QgsVectorLayer("LineString", "Diameter "+str(n+1), "memory")
            seg = QgsFeature()
            seg.setGeometry(QgsGeometry.fromPolylineXY([line_start, line_end]))
            provider = line.dataProvider()
            line.startEditing()
            provider.addFeatures([seg])
            line.commitChanges()

            # symbol = QgsFillSymbol.createSimple({'color': 'black'})
            line.renderer().symbol().setColor(QColor("black"))
            line.triggerRepaint()

            self.line_layers.append(line)
            QgsProject.instance().addMapLayer(line)

    
    def canvasPressEvent(self, e):
        self.clearCanvas()

        point = self.toMapCoordinates(self.canvas.mouseLastXY())
        self.x = point[0]
        self.y = point[1]
        print ('Center - ({:.4f}, {:.4f})'.format(self.x, self.y))

        radius, ok = QInputDialog.getDouble(
            self.iface.mainWindow(), 'Radius', 'Give a radius in km:', min=0.1)

        if ok:
            self.drawCircle(radius)
            self.drawSectorLines(radius)
            self.iface.messageBar().pushMessage("Sectors Drawn",
                                           "Click on the sector for which you want to query places.\nPress 'Q' to Quit.\nPress 'L' to change Location.", level=Qgis.Success, duration=3)

            query_places = query_sector_file.QuerySectorPlaces(
                self.iface.mapCanvas(), self.iface, point, radius, self.line_layers, self.circle)
            self.iface.mapCanvas().setMapTool(query_places)

    def keyReleaseEvent(self, e):
        if(chr(e.key()) == 'Q'):
            self.canvas.unsetMapTool(self)
        elif(chr(e.key()) == 'P'):
            self.canvas.setMapTool(self.toolPan)
        elif(chr(e.key()) == 'I'):
            self.canvas.setMapTool(self.toolZoomIn)
        elif(chr(e.key()) == 'O'):
            self.canvas.setMapTool(self.toolZoomOut)

