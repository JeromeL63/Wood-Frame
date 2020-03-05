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

import os

__dir__ = os.path.dirname(__file__)
__title__="FreeCAD Wood Frame Container API"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"


import FreeCAD,FreeCADGui
from FreeCAD import Base
import Draft,Part
from PySide import QtGui, QtCore
from pivy import coin
import WFDialogs,WFUtils



class WFAddContainer():

    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/WFContainer.svg',
                'Accel': "A,C",
                'MenuText': "Create exporter container",
                'ToolTip': "Create volume which contains objects to export, and configure views"}

    def Activated(self):
        panel = Ui_AddContainer()
        FreeCADGui.Control.showDialog(panel)
        return

    def IsActive(self):
        return True
FreeCADGui.addCommand('WF_AddContainer', WFAddContainer())

class WFAddView():
    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/WFView.svg',
                'Accel': "A,V",
                'MenuText': "Add view to container",
                'ToolTip': "Add view to container to be exported"}

    def Activated(self):
        panel = Ui_AddView(FreeCADGui.Selection.getSelection()[0])
        FreeCADGui.Control.showDialog(panel)
        return

    def IsActive(self):
        bool = False
        #test if the selected object is a container

        if FreeCAD.GuiUp:
            if len(FreeCADGui.Selection.getSelection()) == 1:
                obj = FreeCADGui.Selection.getSelection()[0]
                if hasattr(obj,"Proxy"):
                    obj=obj.Proxy
                    if hasattr(obj,"__getstate__"):
                        if obj.__getstate__() == "Container":
                            bool = True
        return bool


FreeCADGui.addCommand('WF_AddView', WFAddView())



class Ui_AddContainer():
    def __init__(self):
        self.form = QtGui.QWidget()
        self.form.setWindowTitle("Add export container")
        grid = QtGui.QGridLayout(self.form)
        self.selectionList = WFDialogs.ListSelectionWidget()
        self.lbl = QtGui.QLabel("Container name :")
        self.ledName= QtGui.QLineEdit("Container")
        grid.addWidget(self.lbl, 0, 0, 1, 1)
        grid.addWidget(self.ledName, 0,1, 1, 1)
        grid.addWidget(self.selectionList,1,0,1,2)
        self.list=[]


    def accept(self):
        self.selectionList.removeObserver()
        c = Container(objectsList=self.selectionList.selection,name=self.ledName.text())
        c.createVolume()
        FreeCADGui.Control.closeDialog()

    def reject(self):
        self.selectionList.removeObserver()
        FreeCADGui.Control.closeDialog()



class Ui_AddView():
    def __init__(self,container):
        loader = FreeCADGui.UiLoader()
        self.view= None
        self.rotValue =0
        self.container = Container(container)
        FreeCADGui.Selection.clearSelection()

        self.showContent()


        self.workingplane = FreeCAD.DraftWorkingPlane
        self.form = QtGui.QWidget()
        self.form.setWindowTitle("Add container view")
        grid = QtGui.QGridLayout(self.form)

        self.lbl = QtGui.QLabel("Select a face on "+ self.container.name)
        self.lblName= QtGui.QLabel("View Name")
        self.ledName = QtGui.QLineEdit("")
        self.lblrot =QtGui.QLabel("Rotation :")
        self.rotAngle = loader.createWidget("Gui::InputField")
        self.flipDirection = QtGui.QCheckBox("Flip direction(not implanted)")
        self.flipDirection.setEnabled(False)



        self.remove=QtGui.QPushButton("Clear view")
        grid.addWidget(self.lbl,0,0,1,1)
        grid.addWidget(self.lblName,1,0,1,1)
        grid.addWidget(self.ledName,1,1,1,1)
        grid.addWidget(self.lblrot,2,0,1,1)
        grid.addWidget(self.rotAngle,2,1,1,1)
        grid.addWidget(self.remove, 3, 0, 1, 1)
        grid.addWidget(self.flipDirection, 4, 0, 1, 1)
        QtCore.QObject.connect(self.remove, QtCore.SIGNAL("clicked()"), self.removeview)
        QtCore.QObject.connect(self.rotAngle, QtCore.SIGNAL("valueChanged(double)"), self.setRotation)
        QtCore.QObject.connect(self.flipDirection, QtCore.SIGNAL("clicked()"), self.flip)


    #these functions are used to listen selection(Observer) !
        FreeCADGui.Selection.addObserver(self)
    def setPreselection(self,doc,obj,sub):
        # Preselection object
        o = FreeCADGui.Selection.getPreselection()
        if hasattr(o.Object,"Type"):
            if "Face" in sub:
                print("Preselected :",str(obj),str(sub))
                self.ledName.setText(str(sub))

    def addSelection(self,doc,obj,sub,pnt):
        print(str(obj),str(sub))
        self.addview()
    #end listener functions


    def setRotation(self,val):
        self.container.rotateView(self.ledName.text(), value=val)


    def addview(self):
        #check if selectionEx is a Face
        if len(FreeCADGui.Selection.getSelectionEx()) == 1:
            sel =FreeCADGui.Selection.getSelectionEx()[0]
            if len(sel.SubObjects) > 0 :
                if type(sel.SubObjects[0]) is Part.Face :
                    name = self.ledName.text()
                    if not name: self.ledName.setText(sel.SubElementNames[0])
                    #save current workingPlane
                    self.prevWP=self.workingplane.getPlacement()
                    self.workingplane.alignToFace(sel.SubObjects[0])
                    WFUtils.alignView()
                    FreeCADGui.Snapper.setGrid()
                    w=sel.SubObjects[0].Edges[0].Length
                    h=sel.SubObjects[0].Edges[1].Length
                    self.view = self.container.addView(sel.SubObjects[0], name=self.ledName.text(),width=w,height=h)
                    FreeCADGui.Selection.clearSelection()


    def removeview(self):
        if self.view:
            FreeCAD.ActiveDocument.removeObject(self.view.Name)
            FreeCAD.ActiveDocument.recompute()
        if hasattr(self,"prevWP"):
            self.workingplane.setFromPlacement(self.prevWP)
            FreeCADGui.Snapper.setGrid()
            FreeCAD.ActiveDocument.recompute()
        self.ledName.setText("")

    def flip(self):
        #TODO : write flip function
        print("flip")


    def accept(self):
        FreeCADGui.Selection.removeObserver(self)
        self.workingplane.setFromPlacement(self.prevWP)
        FreeCADGui.Snapper.setGrid()
        FreeCADGui.Control.closeDialog()
        FreeCADGui.ActiveDocument.resetEdit()
        self.showContent(False)

    def reject(self):
        self.removeview()
        FreeCADGui.Selection.removeObserver(self)
        FreeCADGui.Control.closeDialog()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        self.showContent(False)

    def showContent(self,bool=True):
        self.showBoundingBox(bool)
        self.showViews(bool)

    def showBoundingBox(self,bool=True):
        if hasattr(self.container.group,"BoundingBox"):
            self.container.group.BoundingBox.ViewObject.Visibility=bool

    def showViews(self,bool=True):
        if hasattr(self.container.group,"Views"):
            for v in self.container.group.Views:
                v.Visibility=bool





class Ui_ContainerEdit:
    def __init__(self, container):
        loader = FreeCADGui.UiLoader()
        self.obj = container
        self.container = Container(self.obj)
        self.showContent()

        FreeCADGui.Selection.clearSelection()
        self.form = QtGui.QWidget()
        self.form.setWindowTitle("Container edition")
        grid = QtGui.QGridLayout(self.form)



        self.but_RedoBBox = QtGui.QPushButton("Redraw bounding Box")
        self.but_AddView = QtGui.QPushButton("Add a new view")
        self.lst_EditView = QtGui.QListWidget()
        self.but_TodDxf = QtGui.QPushButton("Export container's views to DXF file")

        grid.addWidget(self.but_RedoBBox,0,0,1,1)
        grid.addWidget(self.but_AddView,1 , 0, 1, 1)
        grid.addWidget(self.lst_EditView,2,0,1,1)
        grid.addWidget(self.but_TodDxf,3,0,1,1)

        #enable redo box if not present
        if hasattr(self.container.group, "BoundingBox"):
            if self.container.group.BoundingBox:
                self.but_RedoBBox.setEnabled(False)

        #populate listview
        for view in self.container.group.Views :
            self.lst_EditView.addItem(view.Label)


        QtCore.QObject.connect(self.but_RedoBBox, QtCore.SIGNAL("clicked()"), self.redoBBox)
        QtCore.QObject.connect(self.but_AddView, QtCore.SIGNAL("clicked()"), self.addView)
        QtCore.QObject.connect(self.but_TodDxf, QtCore.SIGNAL("clicked()"), self.dxf)

    def accept(self):
        FreeCADGui.Control.closeDialog()
        FreeCADGui.ActiveDocument.resetEdit()
        self.showContent(False)
        FreeCAD.ActiveDocument.recompute()

    def reject(self):
        FreeCADGui.Control.closeDialog()
        FreeCADGui.ActiveDocument.resetEdit()
        self.showContent(False)
        FreeCAD.ActiveDocument.recompute()

    def redoBBox(self):
        self.container.createVolume()

    def editView(self):
        pass
    def addView(self):
        self.accept()
        panel = Ui_AddView(self.obj)
        FreeCADGui.Control.showDialog(panel)

    def dxf(self):
        self.accept()
        import WFDxfExport as export
        panel = export.Ui_Exporter(self.obj)
        FreeCADGui.Control.showDialog(panel)


    def showContent(self,bool=True):
        self.showBoundingBox(bool)
        self.showViews(bool)

    def showBoundingBox(self,bool=True):
        if hasattr(self.container.group,"BoundingBox"):
            if self.container.group.BoundingBox:
                self.container.group.BoundingBox.ViewObject.Visibility=bool

    def showViews(self,bool=True):
        if hasattr(self.container.group,"Views"):
            for v in self.container.group.Views:
                v.Visibility=bool








# container exporter class
class Container:
    def __init__(self,obj=None,objectsList=None, name="Container"):
        self.objlist = []
        self.min = Base.Vector(0, 0, 0)
        self.max = Base.Vector(0, 0, 0)
        self.name = name
        self.bbox = None
        self.lines =[]
        self.Type = "Container"

        # create container group if not exist
        if not obj :
            self.group = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", self.name)
            self.group.addProperty("App::PropertyLinkList", "Objects", "Container")
            self.group.addProperty("App::PropertyLink", "BoundingBox", "Container")
            self.group.addProperty("Part::PropertyPartShape", "Shape", "Container")
            self.group.addProperty("App::PropertyLinkList", "Views", "Container")
        else :
            self.group = obj
            self.objlist = obj.Objects
            self.bbox = obj.BoundingBox

        if objectsList:
            self.objlist = objectsList

        self.group.Proxy = self
        self.group.Objects = self.objlist

        if FreeCAD.GuiUp:
            ViewProviderContainer(self.group.ViewObject)
        # add container in containersFolder
        getContainersFolder().addObject(self.group)
        # add group to WFrame group
        if hasattr(FreeCAD.ActiveDocument, "WFrame"):
            FreeCAD.ActiveDocument.WFrame.addObject(getContainersFolder())

    def execute(self,obj):
        g = obj.Group
        g.sort(key=lambda o: o.Label)
        obj.Group = g

    def __getstate__(self):
        if hasattr(self, "Type"):
            return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def createVolume(self):
        # calculate min point and max point of selected objects
        for obj in self.objlist:
            if hasattr(obj, "Shape"):
                for verts in obj.Shape.Vertexes:
                    if verts.X > self.max.x:
                        self.max.x = verts.X
                    elif verts.X < self.min.x:
                        self.min.x = verts.X

                    if verts.Y > self.max.y:
                        self.max.y = verts.Y
                    elif verts.Y < self.min.y:
                        self.min.y = verts.Y

                    if verts.Z > self.max.z:
                        self.max.z = verts.Z
                    elif verts.Z < self.min.z:
                        self.min.z = verts.Z
        #create  bounding box volume
        self.bbox = FreeCAD.ActiveDocument.addObject("Part::FeaturePython",self.name+"_Box")
        self.bbox.addProperty("App::PropertyString", "Type", "Container")
        self.bbox.Type ="BoundingBox"
        length = self.max.x - self.min.x
        width = self.max.y - self.min.y
        height = self.max.z - self.min.z
        self.bbox.Shape = Part.makeBox(length,width,height)
        ViewProviderBoundingBox(self.bbox.ViewObject)
        self.bbox.Placement = FreeCAD.Placement(self.min, FreeCAD.Rotation(0, 0, 0))
        self.bbox.ViewObject.Transparency = 85
        # self.bbox.ViewObject.DrawStyle = "Dashed"
        self.group.addObject(self.bbox)
        self.group.BoundingBox = self.bbox
        FreeCAD.ActiveDocument.recompute()


        return self.bbox

    def addView(self,selection,name,width=0,height=0):

        #TODO : Views should have its own volume to make sections

        WP = Draft.makeWorkingPlaneProxy(FreeCAD.DraftWorkingPlane.getPlacement())
        WP.addProperty("App::PropertyPlacement","Initial_Placement")
        WP.Initial_Placement=WP.Placement
        WP.ViewObject.DisplaySize = 1000
        WP.ViewObject.ArrowSize = 50
        WP.ViewObject.LineWidth=2
        WP.Label = name
        #ViewProviderView(WP.ViewObject)
        self.group.addObject(WP)
        # append created view in list
        lst=self.group.Views
        lst.append(WP)
        self.group.Views=lst
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        return WP


    def rotateView(self,name,value):
        for WP in self.group.Views:
            if name == WP.Label:
                # test avec un rectangle
                basepoint= WP.Placement.Base
                rec=Draft.makeRectangle(length=100,height=100,placement=WP.Initial_Placement)
                FreeCAD.ActiveDocument.recompute()
                print(FreeCAD.DraftWorkingPlane.getNormal())
                normal= FreeCAD.DraftWorkingPlane.getNormal()
                Draft.rotate(rec, value, center=WP.Placement.Base, axis=normal, copy=False)
                WP.Placement=rec.Placement
                FreeCAD.ActiveDocument.removeObject(rec.Name)
                FreeCAD.DraftWorkingPlane.alignToFace(WP.Shape)
                FreeCAD.ActiveDocument.recompute()



    def drawCorners(self):
        # create bounding box lines which limit area
        units = 100
        for edge in self.bbox.Shape.Edges:
            base = edge.Vertexes[0].Point
            vec = Base.Vector(edge.Vertexes[1].X - base.x, edge.Vertexes[1].Y - base.y, edge.Vertexes[1].Z - base.z)
            vec.multiply(1 / 100)
            pt = Base.Vector(base.x + vec.x, base.y + vec.y, base.z + vec.z)
            line = Draft.makeLine(base, pt)
            self.lines.append(line)

            vec = Base.Vector(base.x - edge.Vertexes[1].X, base.y - edge.Vertexes[1].Y, base.z - edge.Vertexes[1].Z)
            vec.multiply(1 / 100)
            pt = Base.Vector(edge.Vertexes[1].X + vec.x, edge.Vertexes[1].Y + vec.y, edge.Vertexes[1].Z + vec.z)
            line = Draft.makeLine(edge.Vertexes[1].Point, pt)
            self.lines.append(line)
        FreeCAD.ActiveDocument.recompute()
        return self.lines



def getContainersFolder():
    #function to return the containers folder, if it doesn't exist -> create
    for obj in FreeCAD.ActiveDocument.Objects:
        if obj.Name == "Containers":
            return obj
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "Containers")
    obj.Label = "Containers"
    ContainersFolder(obj)
    if FreeCAD.GuiUp:
        ViewProviderContainers(obj.ViewObject)
    return obj


#functions for treelist view style

class ContainersFolder:
    def __init__(self,obj):
        self.Type ="ContainersFolder"
        obj.Proxy=self

    def execute(self,obj):
        g = obj.Group
        g.sort(key=lambda o: o.Label)
        obj.Group = g

    def __getstate__(self):
        if hasattr(self, "Type"):
            return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state




class ViewProviderContainer:
    def __init__(self,obj):
        obj.Proxy=self
    def getIcon(self):
        return __dir__ + '/Resources/icons/WFContainer.svg'

    def setEdit(self,obj,mode=0):
        panel = Ui_ContainerEdit(obj.Object)
        FreeCADGui.Control.showDialog(panel)
        return True

    def unsetEdit(self,obj,mode=0):
        FreeCADGui.Control.closeDialog()
        return True

    def doubleClicked(self,obj):
        doc= FreeCADGui.getDocument(obj.Object.Document)
        doc.setEdit(obj.Object.Name)




class ViewProviderContainers:
    def __init__(self,obj):
        obj.Proxy=self
    def getIcon(self):
        return __dir__ + '/Resources/icons/WFContainers.svg'






class ViewProviderBoundingBox:
    def __init__(self,obj):
        obj.Proxy=self
    def getIcon(self):
        return __dir__ + '/Resources/icons/WFBBox.svg'

    def setEdit(self,obj,mode=0):
        panel = Ui_AddView(FreeCADGui.Selection.getSelection()[0].InList[0])
        FreeCADGui.Control.showDialog(panel)
        return True

    def unsetEdit(self,obj,mode=0):
        FreeCADGui.Control.closeDialog()
        return True

    def doubleClicked(self,obj):
        doc= FreeCADGui.getDocument(obj.Object.Document)
        doc.setEdit(obj.Object.Name)


class ViewProviderView:
    #TODO: erf unable to override view provider of a workingplaneProxy
    def __init__(self,obj):
        obj.Proxy=self
    def getIcon(self):
        return __dir__ + '/Resources/icons/WFView.svg'