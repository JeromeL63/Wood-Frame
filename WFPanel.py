#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2019                                                    *
#*   Jerome LAVERROUX <jerome.laverroux@free.fr                            *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************


import FreeCAD, Arch, Draft,ArchComponent, DraftVecUtils,ArchCommands, ArchStructure,math,FreeCADGui,WorkingPlane
from FreeCAD import Base, Vector,Rotation
from math import *

import DraftTrackers
import WFAttributes,WFUtils,WFDialogs


if FreeCAD.GuiUp:
    import FreeCADGui
    import DraftTools
    from DraftTools import translate,Line
else:
    def translate(ctxt,txt):
        return txt
# waiting for WFrame_rc and eventual FreeCAD integration
import os
__dir__ = os.path.dirname(__file__)

__title__="FreeCAD WoodFrame Panel"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"


from PySide import QtGui,QtCore
from pivy import coin


class WF_Panel():
    """WFramePanel"""

    def __init__(self):
        self.view = None
        self.units = None
        self.points = []



    def GetResources(self):
        return {'Pixmap'  :  __dir__ + '/Resources/icons/WF_Panel.svg',
                'Accel' : "W,P",
                'MenuText': "Add Panel",
                'ToolTip' : "Create an advanced panel with better positionning method"}

    def Activated(self):
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.units = FreeCAD.Units.Quantity(1.0, FreeCAD.Units.Length)
        ###TODO Prepare File
        # 1 : create Timber group
        # 2 : Create Layers
        FreeCADGui.Snapper.show()
        panel=Ui_Definition()
        FreeCADGui.Control.showDialog(panel)
        return

    def IsActive(self):
        if FreeCADGui.ActiveDocument:

            return True
        else:
            return False


FreeCADGui.addCommand('WF_Panel',WF_Panel())


class Ui_Definition:
    def __init__(self):

        self.panel = Panel()
        self.points=[]
        self.pt=None
        self.lastpoint=None
        self.isLength=False
        self.l=self.panel.length
        self.w=self.panel.width
        self.wmax=self.panel.maxWidth
        self.t=self.panel.thickness

        self.form = QtGui.QWidget()
        grid = QtGui.QGridLayout(self.form)

        ### COORDINATES CONTAINER ###
        self.coords = WFDialogs.CoordinatesWidget()
        grid.addWidget(self.coords, 0, 0, 1, 1)
        QtCore.QObject.connect(self.coords.oX, QtCore.SIGNAL("valueChanged(double)"), self.setoX)
        QtCore.QObject.connect(self.coords.oY, QtCore.SIGNAL("valueChanged(double)"), self.setoY)
        QtCore.QObject.connect(self.coords.oZ, QtCore.SIGNAL("valueChanged(double)"), self.setoZ)
        QtCore.QObject.connect(self.coords.eX, QtCore.SIGNAL("valueChanged(double)"), self.seteX)
        QtCore.QObject.connect(self.coords.eY, QtCore.SIGNAL("valueChanged(double)"), self.seteY)

        ### DIMENSION CONTAINER ###
        self.dim = WFDialogs.DimensionsWidget(panelMode=True)
        self.dim.width.setText(FreeCAD.Units.Quantity(self.w, FreeCAD.Units.Length).UserString)
        self.dim.maxWidth.setText(FreeCAD.Units.Quantity(self.wmax, FreeCAD.Units.Length).UserString)
        self.dim.height.setText(FreeCAD.Units.Quantity(self.t, FreeCAD.Units.Length).UserString)
        self.dim.length.setText(FreeCAD.Units.Quantity(self.l, FreeCAD.Units.Length).UserString)
        grid.addWidget(self.dim, 1, 0, 1, 1)
        QtCore.QObject.connect(self.dim.maxWidth, QtCore.SIGNAL("valueChanged(double)"), self.setMaxWidth)
        QtCore.QObject.connect(self.dim.width, QtCore.SIGNAL("valueChanged(double)"), self.setWidth)
        QtCore.QObject.connect(self.dim.height, QtCore.SIGNAL("valueChanged(double)"), self.setThickness)
        QtCore.QObject.connect(self.dim.length, QtCore.SIGNAL("valueChanged(double)"), self.setLength)

        ### DESCRIPTION CONTAINER ###
        self.desc = WFDialogs.DescriptionWidget(orientations=self.panel.orientationTypes)
        grid.addWidget(self.desc, 2, 0, 1, 1)
        QtCore.QObject.connect(self.desc.cb_Orientation, QtCore.SIGNAL("currentIndexChanged(int)"), self.sectionChanged)
        QtCore.QObject.connect(self.desc.cb_Name, QtCore.SIGNAL("currentIndexChanged(int)"), self.redraw)

        ### INSERTION POINT CONTAINER ###
        self.inspoint = WFDialogs.InsertionPointWidget()
        grid.addWidget(self.inspoint, 4, 0, 1, 1)
        QtCore.QObject.connect(self.inspoint.rb_1, QtCore.SIGNAL("clicked()"), self.offset)
        QtCore.QObject.connect(self.inspoint.rb_2, QtCore.SIGNAL("clicked()"), self.offset)
        QtCore.QObject.connect(self.inspoint.rb_3, QtCore.SIGNAL("clicked()"), self.offset)
        QtCore.QObject.connect(self.inspoint.rb_4, QtCore.SIGNAL("clicked()"), self.offset)
        QtCore.QObject.connect(self.inspoint.rb_5, QtCore.SIGNAL("clicked()"), self.offset)
        QtCore.QObject.connect(self.inspoint.rb_6, QtCore.SIGNAL("clicked()"), self.offset)
        QtCore.QObject.connect(self.inspoint.rb_7, QtCore.SIGNAL("clicked()"), self.offset)
        QtCore.QObject.connect(self.inspoint.rb_8, QtCore.SIGNAL("clicked()"), self.offset)
        QtCore.QObject.connect(self.inspoint.rb_9, QtCore.SIGNAL("clicked()"), self.offset)

        #reimplement getPoint from draft, without Dialog taskbox

        #start events
        self.curview=FreeCADGui.activeDocument().activeView()
        self.callbackClick = self.curview.addEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.mouseClick)
        self.callbackMove = self.curview.addEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.mouseMove)
        self.callbackKeys =None
        self.enterkeyCode= 65293# don't know how to to use c++ enum SoKeyboardEvent::Key::ENTER
        self.returnKeyCode=65421# don't know how to to use c++ enum SoKeyboardEvent::Key::RETURN

    def setoX(self, val):
        if len(self.points) > 0:
            if not val == self.points[0][0]:
                self.points[0][0] = val
            self.redraw()

    def setoY(self, val):
        if len(self.points) > 0:
            if not val == self.points[0][1]:
                self.points[0][1] = val
            self.redraw()

    def setoZ(self, val):
        if len(self.points) > 0:
            if not val == self.points[0][2]:
                self.points[0][2] = val
            self.redraw()

    def seteX(self, val):
        if len(self.points) > 1:
            if not val == self.vecInLocalCoords[0]:
                self.vecInLocalCoords[0] = val
                # convert local vector in global point
                origInLocalCoords = FreeCAD.DraftWorkingPlane.getLocalCoords(self.points[0])
                vecToGlobalCoords = self.vecInLocalCoords + origInLocalCoords
                vecToGlobalCoords = FreeCAD.DraftWorkingPlane.getGlobalCoords(vecToGlobalCoords)
                self.points[1] = vecToGlobalCoords
                self.redraw()

    def seteY(self, val):
        if len(self.points) > 1:
            if not val == self.vecInLocalCoords[1]:
                self.vecInLocalCoords[1] = val
                # convert local vector in global point
                origInLocalCoords = FreeCAD.DraftWorkingPlane.getLocalCoords(self.points[0])
                vecToGlobalCoords = self.vecInLocalCoords + origInLocalCoords
                vecToGlobalCoords = FreeCAD.DraftWorkingPlane.getGlobalCoords(vecToGlobalCoords)
                self.points[1] = vecToGlobalCoords
                self.redraw()


    def closeEvents(self):
        #remove all events
        if self.callbackClick:
            self.curview.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.callbackClick)
        if self.callbackMove:
            self.curview.removeEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.callbackMove)
        if self.callbackKeys:
            self.curview.removeEventCallbackPivy(coin.SoKeyboardEvent.getClassTypeId(), self.callbackKeys)

        self.callbackClick = None
        self.callbackMove = None

    def keys(self,event_cb):
        event=event_cb.getEvent()
        if event.getState() == coin.SoKeyboardEvent.DOWN:
            if (event.getKey() == self.returnKeyCode) or (event.getKey() == self.enterkeyCode):
                self.accept()
                return

            if event.getPrintableCharacter() == "1": self.inspoint.rb_1.setChecked(True)
            if event.getPrintableCharacter() == "2": self.inspoint.rb_2.setChecked(True)
            if event.getPrintableCharacter() == "3": self.inspoint.rb_3.setChecked(True)
            if event.getPrintableCharacter() == "4": self.inspoint.rb_4.setChecked(True)
            if event.getPrintableCharacter() == "5": self.inspoint.rb_5.setChecked(True)
            if event.getPrintableCharacter() == "6": self.inspoint.rb_6.setChecked(True)
            if event.getPrintableCharacter() == "7": self.inspoint.rb_7.setChecked(True)
            if event.getPrintableCharacter() == "8": self.inspoint.rb_8.setChecked(True)
            if event.getPrintableCharacter() == "9": self.inspoint.rb_9.setChecked(True)
            self.offset()

    #retreive point clicked with snap
    def mouseClick(self,event_cb):
        event = event_cb.getEvent()
        if event.getButton() == 1:
            if event.getState() == coin.SoMouseButtonEvent.DOWN:
                #start point
                if len(self.points) == 0 :
                    self.points.append(self.pt)
                    self.coords.oX.setText(str(round(self.pt[0], 2)))
                    self.coords.oY.setText(str(round(self.pt[1], 2)))
                    self.coords.oZ.setText(str(round(self.pt[2], 2)))
                    self.lastpoint=self.pt
                #end point
                elif len(self.points) == 1:
                    # calculate the local vector
                    origInLocalCoords = FreeCAD.DraftWorkingPlane.getLocalCoords(self.points[0])
                    self.vecInLocalCoords = FreeCAD.DraftWorkingPlane.getLocalCoords(self.pt)
                    self.vecInLocalCoords = self.vecInLocalCoords - origInLocalCoords
                    self.coords.eX.setText(str(round(self.vecInLocalCoords[0], 2)))
                    self.coords.eY.setText(str(round(self.vecInLocalCoords[1], 2)))

                    self.closeEvents()
                    self.points.append(self.pt)
                    FreeCADGui.Snapper.off()
                    #start keyboard events
                    self.callbackKeys = self.curview.addEventCallbackPivy(coin.SoKeyboardEvent.getClassTypeId(),self.keys)
                    self.setWidth(DraftVecUtils.dist(self.points[0], self.points[1]))
                    self.inspoint.rb_1.setChecked(True)
                    self.redraw()


    #mouse move to show sanp points
    def mouseMove(self,event_cb):
        event=event_cb.getEvent()
        mousepos=event.getPosition()
        ctrl=event.wasCtrlDown()
        shift=event.wasShiftDown()

        self.pt = FreeCADGui.Snapper.snap(mousepos, lastpoint=self.lastpoint,active=ctrl,constrain=shift)
        if hasattr(FreeCAD, "DraftWorkingPlane"):
            FreeCADGui.draftToolBar.displayPoint(self.pt, None, plane=FreeCAD.DraftWorkingPlane,mask=FreeCADGui.Snapper.affinity)

    def setMaxWidth(self,val):
        self.panel.maxWidth =val
        self.sectionChanged()

    def setWidth(self,val):
        # limit length to max panel length
        if float(val) > float(self.panel.maxWidth):
            self.width = self.panel.maxWidth
        else:
            self.panel.width=val
        self.sectionChanged()

    def setLength(self,val):
        self.panel.length=val
        self.sectionChanged()

    def setThickness(self,val):
        self.panel.thickness=val
        self.sectionChanged()

    def sectionChanged(self):
        self.l = float(self.panel.length)
        self.w = float(self.panel.width)

        self.inspoint.rb_1.setChecked(True)
        self.redraw()


    def accept(self):
        self.panel.shadowToObject()
        self.close()

    def reject(self):
        if self.panel:
            self.panel.delete()
        self.close()

    def close(self,rejected=False):
        self.closeEvents()
        FreeCADGui.Control.closeDialog()
        if rejected:
            if self.panel:
                self.panel.delete()



    def offset(self):
        #TODO dashed and dashdot line style doesn't work properly
        #on orientation =1, z is the offset to draw panel above the WP
        z=-self.l /2

        if self.inspoint.rb_1.isChecked():
            if self.panel.orientation==1:
                self.panel.setOffset(Base.Vector(-self.w / 2, 0 ,z))
            else:
                self.panel.setOffset(Base.Vector(-self.w / 2, -self.l / 2, 0))

        elif self.inspoint.rb_2.isChecked():
            if self.panel.orientation==1:
                self.panel.setOffset(Base.Vector(0, 0, z))
            else:
                self.panel.setOffset(Base.Vector(0, -self.l / 2, 0))

        elif self.inspoint.rb_3.isChecked():
            if self.panel.orientation==1:
                self.panel.setOffset(Base.Vector(self.w / 2, 0 ,z))
            else:
                self.panel.setOffset(Base.Vector(self.w / 2, -self.l / 2, 0))

        elif self.inspoint.rb_4.isChecked():
            if self.panel.orientation==1:
                self.panel.setOffset(Base.Vector(-self.w / 2,self.t/2,z))
            else:
                self.panel.setOffset(Base.Vector(-self.w / 2, 0, 0))

        elif self.inspoint.rb_5.isChecked():
            if self.panel.orientation==1:
                self.panel.setOffset(Base.Vector(0, self.t/2,z))
            else:
                self.panel.setOffset(Base.Vector(0,0,0))

        elif self.inspoint.rb_6.isChecked():
            if self.panel.orientation==1:
                self.panel.setOffset(Base.Vector(self.w / 2, self.t/2,z))
            else:
                self.panel.setOffset(Base.Vector(self.w / 2, 0, 0))

        elif self.inspoint.rb_7.isChecked():
            if self.panel.orientation==1:
                self.panel.setOffset(Base.Vector(-self.w / 2,self.t,z))
            else:
                self.panel.setOffset(Base.Vector(-self.w / 2, self.l / 2, 0))

        elif self.inspoint.rb_8.isChecked():
            if self.panel.orientation==1:
                self.panel.setOffset(Base.Vector(0, self.t, z))
            else:
                self.panel.setOffset(Base.Vector(0, self.l / 2, 0))


        elif self.inspoint.rb_9.isChecked():
            if self.panel.orientation==1:
                self.panel.setOffset(Base.Vector(self.w / 2, self.t, z))
            else:
                self.panel.setOffset(Base.Vector(self.w / 2, self.l / 2, 0))

        FreeCADGui.Selection.clearSelection()

    def redraw(self):
        if len(self.points) == 2 :
            self.panel.orientation = self.desc.cb_Orientation.currentIndex()
            self.panel.name = self.desc.cb_Name.currentText()
            self.panel.delete()
            self.panel.create(start=self.points[0], end=self.points[1], isShadow=True)
            self.offset()



class Panel():
    def __init__(self):
        print("##Panel##\r\n")
        self.name=WFAttributes.getNames()[0]
        self.type=WFAttributes.getTypes()[0]
        self.width=1200
        self.maxWidth = 1200
        self.thickness=12
        self.length = 2800
        self.orientation=0
        self.orientationTypes=["face","top"]
        self.points = [Base.Vector(0, 0, 0), Base.Vector(0, 0, 0)]
        self.angle = 0
        self.structure = None
    def delete(self):
        if self.structure:
            self.structure.Document.removeObject(self.structure.Name)
            self.structure=None


    def create(self,structure=None,start=Base.Vector(0,0,0),end=Base.Vector(0,0,0),isShadow=False):


        self.points = [start, end]
        self.isShadow=isShadow
        self.currentInsPoint=self.points[0]


        # Panel creation
        if self.structure:
            self.structure = structure
        else:
            self.structure = Arch.makePanel(None,length=self.length,width=self.width,thickness=self.thickness)


        self.setAttributes()
        self.setOrientation()
        self.setRotations()
        return self


    def shadowToObject(self):
        if self.structure:
            self.structure.ViewObject.Transparency = 10
            self.structure.ViewObject.DrawStyle = "Solid"

    def objectToShadow(self):
        self.structure.ViewObject.Transparency = 85

    def setSolid(self):
        self.structure.ViewObject.DrawStyle = "Solid"

    def setDashDot(self):
        self.structure.ViewObject.DrawStyle = "Dashdot"

    def setDashed(self):
        self.structure.ViewObject.DrawStyle = "Dashed"



    def setAttributes(self):
        self.structure.IfcType = "Plate"
        self.structure.Tag = "Wood-Frame"
        self.structure.Label = self.name

        # set specific Attributes for WFrame
        WFAttributes.insertAttr(self.structure)
        self.structure.WFName = self.name
        self.structure.Type = self.type

        # set view properties
        r = (1 / 255) * 229
        g = (1 / 255) * 181
        b = (1 / 255) * 122
        self.structure.ViewObject.ShapeColor = (r, g, b)
        if self.isShadow:
            self.objectToShadow()



    def setOffset(self,off=Base.Vector(0,0,0)):
        #function used by setoffsetnumpad
        orig=self.points[0]
        orig=FreeCAD.DraftWorkingPlane.getLocalCoords(orig)
        vector=FreeCAD.Vector(orig[0]-off[0],orig[1]-off[1],orig[2]-off[2])
        vector= FreeCAD.DraftWorkingPlane.getGlobalCoords(vector)
        self.currentInsPoint=vector
        self.setOrientation()
        self.setRotations()


    def setOrientation(self):

        # get rotations between zplan and current plan YESSSS
        self.wplan = FreeCAD.DraftWorkingPlane
        self.rotPlan = self.wplan.getRotation().Rotation

        # Initialize placement
        # set the origin point
        self.initialPlacement = FreeCAD.Base.Placement(self.currentInsPoint, FreeCAD.Rotation(0, 0, 0),FreeCAD.Vector(0, 0, 0))
        # set workingplane rotations
        self.initialPlacement = self.initialPlacement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0), self.rotPlan)
        self.structure.Placement = self.initialPlacement

        # set rotation given by orientation
        # panel defaultview is from face
        self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),FreeCAD.Rotation(90, 0, 0))
        # panel up view
        if self.orientation == 1:
            self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),FreeCAD.Rotation(90, 90, 90))

        FreeCAD.ActiveDocument.recompute()

    def setRotations(self):
        #rotate with the given vector
        self.structure=WFUtils.setRotations(self.structure, points=self.points, wplan=self.wplan)
        FreeCAD.ActiveDocument.recompute()

