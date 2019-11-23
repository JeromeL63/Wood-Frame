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
from PySide import QtGui, QtCore
import FreeCADGui, DraftLayer
import FreeCAD
from FreeCAD import Base
import WFContainer,WFUtils
import Draft
import Part
import os
import TechDraw


__dir__ = os.path.dirname(__file__)
class WFExport:
    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/WFDxf.svg',
                'Accel': "E,X",
                'MenuText': "Export views to DXF",
                'ToolTip': "Export container views in a DXF file"}

    def Activated(self):
        panel = Ui_Exporter()
        FreeCADGui.Control.showDialog(panel)
        return


    def IsActive(self):
        bool = False
        # test if the selected object is a container

        if FreeCAD.GuiUp:
            if len(FreeCADGui.Selection.getSelection()) == 1:
                obj = FreeCADGui.Selection.getSelection()[0]
                if hasattr(obj, "Proxy"):
                    obj = obj.Proxy
                    if hasattr(obj, "__getstate__"):
                        if obj.__getstate__() == "Container":
                            bool = True
        return bool

FreeCADGui.addCommand('WF_Export', WFExport())

class Ui_Exporter():
    def __init__(self,obj=None):
        self.views = []
        self.container=None
        if obj :
            self.container=obj
        else:
            self.container = FreeCADGui.Selection.getSelection()[0]

        FreeCADGui.Selection.clearSelection()
        self.xOffsetValue=200

        loader = FreeCADGui.UiLoader()
        self.form = QtGui.QWidget()
        self.form.setWindowTitle("Export container views into DXF")
        grid = QtGui.QGridLayout(self.form)
        self.lbl=QtGui.QLabel("Selected container: "+self.container.Label)
        self.lbl2 = QtGui.QLabel("Views to export")

        self.listviews = QtGui.QListWidget()
        self.listviews.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        for i in self.container.Views:
            self.listviews.addItem(i.Label)
            FreeCADGui.Selection.addSelection(i)

        self.remove= QtGui.QPushButton("Remove selected views")
        self.currview = QtGui.QCheckBox("Only export displayed view")
        self.lbl3= QtGui.QLabel("X Offset between views")
        self.xOffset = loader.createWidget("Gui::InputField")
        self.xOffset.setText(str(self.xOffsetValue))

        grid.addWidget(self.lbl,0,0,1,1)
        grid.addWidget(self.lbl2,1,0,1,1)
        grid.addWidget(self.listviews,2,0,1,2)
        grid.addWidget(self.remove, 3, 0, 1, 1)
        grid.addWidget(self.currview,4,0,1,1)
        grid.addWidget(self.lbl3,5,0,1,1)
        grid.addWidget(self.xOffset,5,1,1)

        QtCore.QObject.connect(self.listviews, QtCore.SIGNAL("itemSelectionChanged()"), self.highlight)
        QtCore.QObject.connect(self.remove, QtCore.SIGNAL("clicked()"), self.removeViews)
        QtCore.QObject.connect(self.currview, QtCore.SIGNAL("clicked()"), self.setOnlyCurrView)
        QtCore.QObject.connect(self.xOffset, QtCore.SIGNAL("valueChanged(double)"), self.setXOffset)


    def setXOffset(self,val):
        self.xOffsetValue=val

    def setOnlyCurrView(self):
        bool = True
        if self.currview.isChecked() : bool = False
        self.remove.setEnabled(bool)
        self.listviews.setEnabled(bool)
        self.xOffset.setEnabled(bool)

    def accept(self):
        dxf = DxfExport(self.container)
        dxf.extractLayers()

        if self.currview.isChecked():
            dxf.extractModel()
            dxf.save("currentView")
        else :
            self.listviews.selectAll()
            #TODO: add offset between views in dialog
            xoffset = 0
            yoffset = 0
            for item in self.listviews.selectedItems():
                for view in self.container.Views:
                    if view.Label in item.text():
                        FreeCAD.DraftWorkingPlane.alignToFace(view.Shape)
                        WFUtils.alignView()
                        size=dxf.getSizes()
                        #origin in techedraw is on center
                        # so we have to add width /2 to have origin on left
                        xoffset= xoffset + size[0]/2.0
                        print("view size",size)
                        dxf.extractModel(viewXOffset= xoffset)
                        print("offset",xoffset)

                        xoffset = xoffset +(size[0]/2.0) + self.xOffsetValue


            dxf.save(self.container.Label)
            dxf.removeTempObjects()



        FreeCADGui.Control.closeDialog()

    def highlight(self):
        FreeCADGui.Selection.clearSelection()
        for item in self.listviews.selectedItems():
            for i in self.container.Views:
                if i.Label in item.text():
                    FreeCADGui.Selection.addSelection(i)

    def removeViews(self):
        for item in self.listviews.selectedItems():
            row = self.listviews.row(item)
            self.listviews.takeItem(row)





##fonctions vue temporaires
def removeView():
    if hasattr(FreeCAD.ActiveDocument, "View"):
        FreeCAD.ActiveDocument.removeObject("View")

def removePage():
    if hasattr(FreeCAD.ActiveDocument, "Page"):
        FreeCAD.ActiveDocument.removeObject("Page")

def addView():

    if not hasattr(FreeCAD.ActiveDocument, "Page"):
        #FreeCADGui.runCommand("TechDraw_PageDefault")
        FreeCAD.ActiveDocument.addObject('TechDraw::DrawPage', 'Page')
        FreeCAD.ActiveDocument.addObject('TechDraw::DrawSVGTemplate', 'Template')
        FreeCAD.ActiveDocument.Template.Template = '/home/jerome/Applications/build-FreeCAD_dev/share/Mod/TechDraw/Templates/A4_LandscapeTD.svg'
        FreeCAD.ActiveDocument.Page.Template = FreeCAD.activeDocument().Template

    #FreeCAD.activeDocument().addObject('TechDraw::DrawViewPart', 'View')
    FreeCADGui.runCommand("TechDraw_View")

class DxfExport:
    '''
    this tool is used to extract a model to dxf.
    It retreive layers defined in Draft module and redo the same in dxf
    For more convenience the container tool can be used to export multi views

    Container : the container object used to export
    currentview: Optionnal. If currentview is selected, only the view displayed will be exported using
    the container content
    '''

    def __init__(self,container):
        #min and max are coordinates [x,y] of
        #left down point and right up
        #used to determine view size
        # provided by width and height
        self.min=[0,0]
        self.max=[0,0]
        self.width=0
        self.height=0

        self.layers = []
        self.shapesInLayers = {}
        self.container=WFContainer.Container(container)
        self.sel = self.container.objlist
        self.bBoxLines=None
        self.doc = ezdxf.new(dxfversion='R2010')
        self.hiddenLayerName = "Hidden lines"
        self.activeDocument= FreeCAD.ActiveDocument
        ### dxf modelspace's
        self.msp = self.doc.modelspace()
        ###TODO: try to load appropriate modules and not workbenchs
        FreeCADGui.activateWorkbench("TechDrawWorkbench")
        FreeCADGui.activateWorkbench("WFrame")


    def extractLayers(self):

        #extract layers in file :
        if hasattr(FreeCAD.ActiveDocument,"LayerContainer"):
            self.layers=FreeCAD.ActiveDocument.LayerContainer.Group
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

        # create a layer where unsorted lines are stored
        self.doc.layers.new("Unsorted", dxfattribs={'color': 13})
        ###END of layers creation

    def getSizes(self):
        self.min=[0,0]
        self.max=[0,0]

        self.bBoxLines=self.container.drawCorners()
        FreeCADGui.Selection.clearSelection()
        # render only boundingbox to delete it easily
        FreeCADGui.Selection.clearSelection()
        self.addCornersLines()
        removeView()
        addView()
        dvp = FreeCAD.ActiveDocument.View
        self.bBoxEdges = dvp.getVisibleEdges()

        # determine view size
        for edge in self.bBoxEdges:
            for vert in edge.Vertexes:
                # for X
                if vert.X < self.min[0]:
                    self.min[0] = vert.X
                elif vert.X > self.max[0]:
                    self.max[0] = vert.X
                # for Y
                if vert.Y < self.min[1]:
                    self.min[1] = vert.Y
                elif vert.Y > self.max[1]:
                    self.max[1] = vert.Y
        self.width = self.max[0] - self.min[0]
        self.height = self.max[1] - self.min[1]
        return [self.width,self.height]



    def extractModel(self,viewXOffset=0,viewYOffset=0):

        #draw container if not to have view sizes and lines
        if not self.bBoxLines:
            self.getSizes()

        #add container's objects to the selection
        for i in self.sel:
            FreeCADGui.Selection.addSelection(i)

        ### Extract all lines and hidden lines
        removeView()
        addView()

        dvp = FreeCAD.ActiveDocument.View
        dvp.HardHidden = True
        dvp.recompute()
        vizEdgeList = dvp.getVisibleEdges()  # result is list of Part::TopoShapeEdge
        hidEdgeList = dvp.getHiddenEdges()

        #remove hidden lines in front of visibles
        hidEdgeList = self.detectDoubles(hidEdgeList,vizEdgeList)
        hidEdgeList = self.detectDoubles(hidEdgeList, vizEdgeList)



        ### Now try to extract lines



        # select shapes in layer
        for lay in self.layers:
            #print(lay.Label)
            FreeCADGui.Selection.clearSelection()
            shapes = []
            for part in lay.Group:
                shapes.append(part)
                FreeCADGui.Selection.addSelection(part)

            #add corner lines to have same view position
            self.addCornersLines()

            #retrieve edges of this layer
            removeView()
            addView()
            dvp = FreeCAD.ActiveDocument.View
            lst = dvp.getVisibleEdges()
            # create a dictionnary of shapes by layers
            self.shapesInLayers[lay.Label] = lst
            #print("content :",lst)

        # now we have to compare generated Lines and remove lines which are totally drawn
        for layerName, edgelist in self.shapesInLayers.items():

            lst = self.detectDoubles(edgelist, hidEdgeList)
            # remove bounding box in layers
            bboxrem = self.detectDoubles(lst, self.bBoxEdges)
            #replace edgelist by filtered list
            self.shapesInLayers[layerName] = lst
            # we also remove doubles in Temp layer
            lst=self.detectDoubles(vizEdgeList,edgelist)
            #and boundingbox
            self.detectDoubles(lst,self.bBoxEdges)
            vizEdgeList=lst

        # and finally color visible lines splited by testing if line is on another layer's line
        for layerName in self.shapesInLayers.keys():
            corresplst = []
            notsplittedlst = []
            edgelist=self.shapesInLayers[layerName]
            for ledge in edgelist :
                for vedge in vizEdgeList :
                    if self.isOnEdge(vedge,ledge):
                        if not vedge in corresplst:
                            corresplst.append(vedge)
                            if not ledge in notsplittedlst:
                                notsplittedlst.append(ledge)

            for i in corresplst :
                vizEdgeList.remove(i)
                edgelist.append(i)
            for i in notsplittedlst:
                edgelist.remove(i)
            self.shapesInLayers[layerName] = edgelist



        # now draw lines in DXF
        # note : we have to apply symmetry  so I use -Y value
        xoff=viewXOffset
        yoff=viewYOffset
        print("x offset= ",xoff)
        for layerName, edgelist in self.shapesInLayers.items():
            for edge in edgelist:
                start = edge.Vertexes[0]
                end = edge.Vertexes[1]
                self.msp.add_line((start.X + xoff, -start.Y + yoff, start.Z), (end.X +xoff,- end.Y + yoff, end.Z), dxfattribs={'layer': layerName})

        for edge in vizEdgeList:
            start = edge.Vertexes[0]
            end = edge.Vertexes[1]
            self.msp.add_line((start.X + xoff, -start.Y + yoff, start.Z), (end.X +xoff,- end.Y + yoff, end.Z), dxfattribs={'layer': 'Unsorted'})

        for edge in hidEdgeList:
            start = edge.Vertexes[0]
            end = edge.Vertexes[1]
            self.msp.add_line((start.X + xoff, -start.Y + yoff, start.Z), (end.X +xoff,- end.Y + yoff, end.Z), dxfattribs={'layer': self.hiddenLayerName})


    def removeTempObjects(self):
        # remove temp objects in freeCAD treeview
        removePage()
        for i in self.bBoxLines:
            i.Document.removeObject(i.Name)
        FreeCADGui.Selection.clearSelection()


    def addCornersLines(self):
        # add container's corners lines
        for i in self.bBoxLines:
            FreeCADGui.Selection.addSelection(i)


    def detectDoubles(self,edgeList,edgeListToCompare):

        #function to detect if edges in edgeList are in edgeListToCompare
        # remove them and return edgList

        # it use Vertexes coordinates

        out=[]
        lst1=edgeList
        lst2=edgeListToCompare

        for edge in lst1:
            # for every lines in edgelist
            # remove if in edgelisttocompare
            for h in lst2:
                if round(h.Vertexes[0].X,2) == round(edge.Vertexes[0].X,2):
                    if round(h.Vertexes[0].Y,2) == round(edge.Vertexes[0].Y,2):
                        if round(h.Vertexes[1].X, 2) == round(edge.Vertexes[1].X, 2):
                            if round(h.Vertexes[1].Y, 2) == round(edge.Vertexes[1].Y, 2):
                                out.append(edge)

        for edge in out :
            if edge in lst1:
                lst1.remove(edge)
        return lst1

    def isOnEdge(self,edge1,edge2):
        # function that return true if edge 1 is on egde 2
        out = False
        vec1 = Base.Vector(edge1.Vertexes[1].X - edge1.Vertexes[0].X , edge1.Vertexes[1].Y-edge1.Vertexes[0].Y , 0)
        vec2 = Base.Vector(edge2.Vertexes[1].X - edge2.Vertexes[0].X, edge2.Vertexes[1].Y - edge2.Vertexes[0].Y, 0)
        vec3 = Base.Vector(edge2.Vertexes[1].X - edge1.Vertexes[0].X, edge2.Vertexes[1].Y - edge1.Vertexes[0].Y, 0)

        #now round values
        vec1.x = round(vec1.x, 2)
        vec1.y = round(vec1.y, 2)
        vec2.x = round(vec2.x, 2)
        vec2.y = round(vec2.y, 2)
        vec3.x = round(vec3.x, 2)
        vec3.y = round(vec3.y, 2)

        #check if  vectors are collinear
        if (vec1.x * vec2.y) == (vec1.y * vec2.x):
            # now check if 3 points are aligned by using vec 3
            if (vec1.x * vec3.y) == (vec1.y * vec3.x):
                out = True
        return out




    def save(self, filename, dir=None):
        # Save  generated DXF document.
        if not dir :
            dir= os.path.dirname(FreeCAD.ActiveDocument.FileName)
        self.doc.saveas(dir+'/'+filename+'.dxf')

