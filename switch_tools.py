from qgis.core import *
from qgis.gui import *
import importlib.util

approot = QgsProject.instance().homePath()

class switchPanTool(QgsMapToolPan):
    def __init__(self, canvas, iface, caller_tool):
        self.canvas = canvas
        self.iface = iface
        self.caller_tool = caller_tool
        QgsMapToolEmitPoint.__init__(self, self.canvas)
            
    def keyReleaseEvent(self, e):
        circle_spec = importlib.util.spec_from_file_location("draw_circle", approot+"/query-places/draw_circle.py")
        draw_circle_file = importlib.util.module_from_spec(circle_spec)
        circle_spec.loader.exec_module(draw_circle_file)

        draw_tool = draw_circle_file.DrawSectorCircle(self.canvas, self.iface)

        path_spec = importlib.util.spec_from_file_location("find_path", approot+"/shortest-path/find_path.py")
        find_path_file = importlib.util.module_from_spec(path_spec)
        path_spec.loader.exec_module(find_path_file)
        
        path_tool = find_path_file.FindPath(self.canvas, self.iface)

        if(chr(e.key()) == 'D' and self.caller_tool == 'draw'):
            self.canvas.setMapTool(draw_tool)
        elif(chr(e.key()) == 'S' and self.caller_tool == 'path'):
            self.canvas.setMapTool(path_tool)
        elif(chr(e.key()) == 'P'):
            if (self.caller_tool == 'draw'):
                self.canvas.setMapTool(draw_tool.toolPan)
            else:
                self.canvas.setMapTool(path_tool.toolPan)
        elif(chr(e.key()) == 'I'):
            if (self.caller_tool == 'draw'):
                self.canvas.setMapTool(draw_tool.toolZoomIn)
            else:
                self.canvas.setMapTool(path_tool.toolZoomIn)
        elif(chr(e.key()) == 'O'):
            if (self.caller_tool == 'draw'):
                self.canvas.setMapTool(draw_tool.toolZoomOut)
            else:
                self.canvas.setMapTool(path_tool.toolZoomOut)
        elif(chr(e.key()) == 'Q'):
            self.canvas.unsetMapTool(self)

class switchZoomTool(QgsMapToolZoom):
    def __init__(self, canvas, iface, inOut, caller_tool):
        self.canvas = canvas
        self.iface = iface
        self.caller_tool = caller_tool
        QgsMapToolEmitPoint.__init__(self, self.canvas, inOut)
    
    def keyReleaseEvent(self, e):
        circle_spec = importlib.util.spec_from_file_location("draw_circle", approot+"/query-places/draw_circle.py")
        draw_circle_file = importlib.util.module_from_spec(circle_spec)
        circle_spec.loader.exec_module(draw_circle_file)
        
        draw_tool = draw_circle_file.DrawSectorCircle(self.canvas, self.iface)

        path_spec = importlib.util.spec_from_file_location("find_path", approot+"/shortest-path/find_path.py")
        find_path_file = importlib.util.module_from_spec(path_spec)
        path_spec.loader.exec_module(find_path_file)
        
        path_tool = find_path_file.FindPath(self.canvas, self.iface)

        if(chr(e.key()) == 'D' and self.caller_tool == 'draw'):
            self.canvas.setMapTool(draw_tool)
        elif(chr(e.key()) == 'S' and self.caller_tool == 'path'):
            self.canvas.setMapTool(path_tool)
        elif(chr(e.key()) == 'P'):
            if (self.caller_tool == 'draw'):
                self.canvas.setMapTool(draw_tool.toolPan)
            else:
                self.canvas.setMapTool(path_tool.toolPan)
        elif(chr(e.key()) == 'I'):
            if (self.caller_tool == 'draw'):
                self.canvas.setMapTool(draw_tool.toolZoomIn)
            else:
                self.canvas.setMapTool(path_tool.toolZoomIn)
        elif(chr(e.key()) == 'O'):
            if (self.caller_tool == 'draw'):
                self.canvas.setMapTool(draw_tool.toolZoomOut)
            else:
                self.canvas.setMapTool(path_tool.toolZoomOut)
        elif(chr(e.key()) == 'Q'):
            self.canvas.unsetMapTool(self)