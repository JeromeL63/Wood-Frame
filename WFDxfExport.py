# -*- coding: utf-8 -*-
# FreeCAD init script of the Wood Frame module
# (c) 2019 Jerome Laverroux

#***************************************************************************
#*   (c) Jerome Laverroux (jerome.laverroux@free.fr) 2019                  *
#*                                                                         *
#*   This file is part of the FreeCAD CAx development system.              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   FreeCAD is distributed in the hope that it will be useful,            *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#*   Jerome Laverroux 2019                                                 *
#***************************************************************************/


__title__="FreeCAD Wood Frame Container API"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"

import ezdxf
from ezdxf.tools.standards import linetypes
import FreeCADGui, DraftLayer
import FreeCAD
from FreeCAD import Base
import WFContainer
import Draft
import os

__dir__ = os.path.dirname(FreeCAD.ActiveDocument.FileName)

import TechDraw



##fonctions vue temporaires
def removeView():
    if hasattr(FreeCAD.ActiveDocument, "View"):
        FreeCAD.ActiveDocument.removeObject("View")
    print("view removed")

def removePage():
    if hasattr(FreeCAD.ActiveDocument, "Page"):
        FreeCAD.ActiveDocument.removeObject("Page")
    print("page removed")

def addView():
    if not hasattr(FreeCAD.ActiveDocument, "Page"):
        FreeCADGui.runCommand("TechDraw_NewPageDef")
    FreeCADGui.runCommand("TechDraw_NewView")
    print("page and view added")

class DxfExport:
    def __init__(self,selection):
        self.layers = []
        self.shapesInLayers = {}
        self.obj = selection
        self.doc = ezdxf.new(dxfversion='R2010')
        self.hiddenLayerName = "Hidden lines"
        self.activeDocument= FreeCAD.ActiveDocument
        ### dxf modelspace's
        self.msp = self.doc.modelspace()
        self.container = None
        ###TODO: try to load appropriate modules and not workbenchs
        FreeCADGui.activateWorkbench("TechDrawWorkbench")
        FreeCADGui.activateWorkbench("WFrame")


    def extractLayers(self):
        #extract Draft Layers present in selection and create them in dxf
        for i in self.obj:
            if hasattr(i, 'Proxy'):
                if type(i.Proxy) == DraftLayer.Layer:
                    self.layers.append(i)

        ####Create layers in the DXF
        for i in self.layers:
            # Create new table entries (layers, linetypes, text styles, ...).
            self.doc.layers.new(i.Label, dxfattribs={'color': 2})
            l = self.doc.layers.get(i.Label)
            col = i.ViewObject.LineColor
            # Conversion from float to RGB
            r = col[0] * 255
            g = col[1] * 255
            b = col[2] * 255
            l.rgb = (r, g, b)

        ##add hidden lines Layer
        # add hidden line style
        self.doc.linetypes.new('HIDDEN', dxfattribs={'description': "Hidden _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ ",
                                                'pattern': 'A,6.35,-3.175'})

        self.doc.layers.new(self.hiddenLayerName, dxfattribs={'color': 3})
        l = self.doc.layers.get(self.hiddenLayerName)
        l.dxf.linetype = 'HIDDEN'
        ###END of layers creation

    def extractModel(self):

        # create a container which contains all parts to be exported
        self.container = WFContainer.Container("Mur_B")
        self.shapeContainer = self.container.create(self.obj)
        '''
        self.ptmin = Draft.makePoint(self.container.getPoints()[0])
        self.ptmax = Draft.makePoint(self.container.getPoints()[1])
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Selection.addSelection(self.ptmin)
        FreeCADGui.Selection.addSelection(self.ptmax)
        '''
        self.bBoxLines=[]
        for edge in self.shapeContainer.Shape.Edges:
            line= Draft.makeLine(edge.Vertexes[0].Point,edge.Vertexes[1].Point)
            self.bBoxLines.append(line)
        FreeCAD.ActiveDocument.recompute()
        # add  container's lines to the selection
        for i in self.bBoxLines:
            FreeCADGui.Selection.addSelection(i)

        for i in self.obj:
            FreeCADGui.Selection.addSelection(i)


        ### Extract all lines and hidden lines(thanks wandererfan)
        removeView()
        addView()

        dvp = FreeCAD.ActiveDocument.View
        dvp.HardHidden = True
        dvp.recompute()
        vizEdgeList = dvp.getVisibleEdges()  # result is list of Part::TopoShapeEdge
        hidEdgeList = dvp.getHiddenEdges()

        #render only boundingbox to delete it easily
        FreeCADGui.Selection.clearSelection()
        for i in self.bBoxLines:
            FreeCADGui.Selection.addSelection(i)
        removeView()
        addView()
        dvp = FreeCAD.ActiveDocument.View
        self.bBoxEdges= dvp.getVisibleEdges()




        ### Now try to extract lines
        # select shapes in layer
        self.doc.layers.new("TEMP", dxfattribs={'color': 13})

        for lay in self.layers:
            print("Select shapes in layer:", lay.Label, "\n")
            group = lay.Group
            FreeCADGui.Selection.clearSelection()
            shapes = []
            # select all shapes in layer
            for part in group:
                shapes.append(part)
                FreeCADGui.Selection.addSelection(part)
            print("Try to add view\n")
            #add container to the selection
            #FreeCADGui.Selection.addSelection(self.ptmin)
            #FreeCADGui.Selection.addSelection(self.ptmax)


            for i in self.bBoxLines:
                FreeCADGui.Selection.addSelection(i)

            # now retrieve edges of this layer
            removeView()
            addView()
            print("view added\n")
            dvp = FreeCAD.ActiveDocument.View
            #dvp.HardHidden = True
            #dvp.recompute()
            #all edges are hidden because of container
            #lst = dvp.getHiddenEdges()
            lst = dvp.getVisibleEdges()
            # create a dictionnary of shapes by layers
            print("create a dictionnary of shapes by layers:", lay.Label, "\n")
            self.shapesInLayers[lay.Label] = lst

        # now we have to compare generated Lines and remove lines which are totally
        for layerName, edgelist in self.shapesInLayers.items():
            print(layerName)
            lst = self.detectDoubles(edgelist, hidEdgeList)
            #self.shapesInLayers[layerName] = lst
            # remove bounding box in layers
            bboxrem = self.detectDoubles(lst, self.bBoxEdges)
            #replace edgelist by filtered list
            self.shapesInLayers[layerName] = lst
            # we also remove doubles in Temp layer
            lst=self.detectDoubles(vizEdgeList,edgelist)
            #and boundingbox
            self.detectDoubles(lst,self.bBoxEdges)
            vizEdgeList=lst

        # now draw lines in DXF


        for layerName, edgelist in self.shapesInLayers.items():
            for edge in edgelist:
                start = edge.Vertexes[0]
                end = edge.Vertexes[1]
                self.msp.add_line((start.X, start.Y, start.Z), (end.X, end.Y, end.Z), dxfattribs={'layer': layerName})

        for edge in vizEdgeList:
            start = edge.Vertexes[0]
            end = edge.Vertexes[1]
            self.msp.add_line((start.X, start.Y, start.Z), (end.X, end.Y, end.Z), dxfattribs={'layer': 'TEMP'})

        for edge in hidEdgeList:
            start = edge.Vertexes[0]
            end = edge.Vertexes[1]
            self.msp.add_line((start.X, start.Y, start.Z), (end.X, end.Y, end.Z), dxfattribs={'layer': self.hiddenLayerName})

        # remove temp objects
        removePage()
        for i in self.bBoxLines :
            i.Document.removeObject(i.Name)

        FreeCADGui.Selection.clearSelection()

    def detectDoubles(self,edgeList,edgeListToCompare):
        out=[]
        lst1=edgeList
        lst2=edgeListToCompare

        for edge in lst1:
            # pour toutes les lignes dans le layer
            # remove if hidden
            for h in lst2:
                #round(self.vecInLocalCoords[0], 2)

                if round(h.Vertexes[0].X,2) == round(edge.Vertexes[0].X,2):
                    if round(h.Vertexes[0].Y,2) == round(edge.Vertexes[0].Y,2):
                        if round(h.Vertexes[1].X, 2) == round(edge.Vertexes[1].X, 2):
                            if round(h.Vertexes[1].Y, 2) == round(edge.Vertexes[1].Y, 2):
                                out.append(edge)
                                print("removed :",edge)
                                #out.append(edge)
        for edge in out :
            if edge in lst1:
                lst1.remove(edge)
        print("original",edgeList,"casted",lst1)
        return lst1


    def save(self):
        # Save DXF document.
        self.doc.saveas(__dir__+'/test.dxf')

