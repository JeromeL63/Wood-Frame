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
import WFrameAttributes


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

addPanelUI = __dir__ + "/Resources/Ui/AddPanel.ui"

from PySide import QtGui,QtCore
from pivy import coin


class WFramePanel():
    """WFramePanel"""

    def __init__(self):
        self.view = None
        self.units = None
        self.points = []



    def GetResources(self):
        return {'Pixmap'  :  __dir__ + '/Resources/icons/WFramePanel.svg',
                'Accel' : "W,B",
                'MenuText': "WFramePanel",
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


FreeCADGui.addCommand('WFramePanel',WFramePanel())


class Ui_Definition:
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(addPanelUI)
        self.panel = Panel(Paneldef())
        self.paneldef = self.panel.paneldef

        self.points=[]
        self.pt=None
        self.lastpoint=None
        self.isLength=False
        self.l=self.paneldef.length
        self.w=self.paneldef.width
        self.t=self.paneldef.thickness

        self.form.cb_Orientation.addItems(self.paneldef.getOrientationTypes())
        self.form.cb_Name.addItems(WFrameAttributes.getNames())

        #init default values
        self.form.led_MaxLength.setText(str(self.paneldef.maxLength))
        self.form.led_Width.setText(str(self.paneldef.width))
        self.form.led_Thickness.setText(str(self.paneldef.thickness))
        self.form.cb_Name.setCurrentIndex(1)

        ##Wrong decimal point with french keyboard !
        ## QLocale doesn't solve problem
        validator= QtGui.QDoubleValidator(0,99999,1)
        self.form.led_MaxLength.setValidator(validator)
        self.form.led_Width.setValidator(validator)
        self.form.led_Thickness.setValidator(validator)

        #connections
        self.form.cb_Orientation.currentIndexChanged.connect(self.sectionChanged)
        self.form.cb_Name.currentIndexChanged.connect(self.redraw)
        self.form.led_Thickness.textChanged.connect(self.sectionChanged)
        self.form.led_Width.textChanged.connect(self.sectionChanged)
        self.form.led_MaxLength.textChanged.connect(self.redraw)
        self.form.rb_1.clicked.connect(self.offset)
        self.form.rb_2.clicked.connect(self.offset)
        self.form.rb_3.clicked.connect(self.offset)
        self.form.rb_4.clicked.connect(self.offset)
        self.form.rb_5.clicked.connect(self.offset)
        self.form.rb_6.clicked.connect(self.offset)
        self.form.rb_7.clicked.connect(self.offset)
        self.form.rb_8.clicked.connect(self.offset)
        self.form.rb_9.clicked.connect(self.offset)
        #self.form.ok.clicked.connect(self.accept)
        #self.form.cancel.clicked.connect(self.reject)


        #reimplement getPoint from draft, without Dialog taskbox

        #start events
        self.curview=FreeCADGui.activeDocument().activeView()
        self.callbackClick = self.curview.addEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.mouseClick)
        self.callbackMove = self.curview.addEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.mouseMove)
        self.callbackKeys =None
        self.enterkeyCode= 65293# don't know how to to use c++ enum SoKeyboardEvent::Key::ENTER
        self.returnKeyCode=65421# don't know how to to use c++ enum SoKeyboardEvent::Key::RETURN


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

            if event.getPrintableCharacter() == "1": self.form.rb_1.setChecked(True)
            if event.getPrintableCharacter() == "2": self.form.rb_2.setChecked(True)
            if event.getPrintableCharacter() == "3": self.form.rb_3.setChecked(True)
            if event.getPrintableCharacter() == "4": self.form.rb_4.setChecked(True)
            if event.getPrintableCharacter() == "5": self.form.rb_5.setChecked(True)
            if event.getPrintableCharacter() == "6": self.form.rb_6.setChecked(True)
            if event.getPrintableCharacter() == "7": self.form.rb_7.setChecked(True)
            if event.getPrintableCharacter() == "8": self.form.rb_8.setChecked(True)
            if event.getPrintableCharacter() == "9": self.form.rb_9.setChecked(True)
            self.offset()

    #retreive point clicked with snap
    def mouseClick(self,event_cb):
        event = event_cb.getEvent()
        if event.getButton() == 1:
            if event.getState() == coin.SoMouseButtonEvent.DOWN:
                #start point
                if len(self.points) == 0 :
                    self.points.append(self.pt)
                    self.lastpoint=self.pt
                #end point
                elif len(self.points) == 1:
                    self.closeEvents()
                    self.points.append(self.pt)
                    FreeCADGui.Snapper.off()
                    #start keyboard events
                    self.callbackKeys = self.curview.addEventCallbackPivy(coin.SoKeyboardEvent.getClassTypeId(),self.keys)
                    self.setLength()
                    self.form.rb_1.setChecked(True)
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

    def setLength(self):
        l=DraftVecUtils.dist(self.points[0], self.points[1])
        # limit length to max panel length
        if float(l) > float(self.paneldef.maxLength):
            self.length = self.paneldef.maxLength
        else:
            self.paneldef.length=l

        self.l = float(self.paneldef.length)
        self.w = float(self.paneldef.width)

    def sectionChanged(self):
        self.l = float(self.paneldef.length)
        self.w = float(self.paneldef.width)

        self.form.rb_1.setChecked(True)
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


        if self.form.rb_1.isChecked():
            if self.form.cb_Orientation.currentIndex() == 1:
                self.panel.setOffset(Base.Vector(-self.l / 2, -self.t,-self.w/2))
            else:
                self.panel.setOffset(Base.Vector(-self.l / 2, -self.w / 2, 0))

        elif self.form.rb_2.isChecked():
            if self.form.cb_Orientation.currentIndex() == 1:
                self.panel.setOffset(Base.Vector(0, -self.t,-self.w/2))
            else:
                self.panel.setOffset(Base.Vector(0, -self.w / 2, 0))

        elif self.form.rb_3.isChecked():
            if self.form.cb_Orientation.currentIndex() == 1:
                self.panel.setOffset(Base.Vector(self.l / 2, -self.t,-self.w/2))
            else:
                self.panel.setOffset(Base.Vector(self.l / 2, -self.w / 2, 0))

        elif self.form.rb_4.isChecked():
            if self.form.cb_Orientation.currentIndex() == 1:
                self.panel.setOffset(Base.Vector(-self.l / 2,-self.t/2,-self.w/2))
            else:
                self.panel.setOffset(Base.Vector(-self.l / 2, 0, 0))

        elif self.form.rb_5.isChecked():
            if self.form.cb_Orientation.currentIndex() == 1:
                self.panel.setOffset(Base.Vector(0, -self.t/2, -self.w/2))
            else:
                self.panel.setOffset(Base.Vector(0,0,0))

        elif self.form.rb_6.isChecked():
            if self.form.cb_Orientation.currentIndex() == 1:
                self.panel.setOffset(Base.Vector(self.l / 2, -self.t/2,-self.w/2))
            else:
                self.panel.setOffset(Base.Vector(self.l / 2, 0, 0))

        elif self.form.rb_7.isChecked():
            if self.form.cb_Orientation.currentIndex() == 1:
                self.panel.setOffset(Base.Vector(-self.l / 2, 0,-self.w/2))
            else:
                self.panel.setOffset(Base.Vector(-self.l / 2, self.w / 2, 0))

        elif self.form.rb_8.isChecked():
            if self.form.cb_Orientation.currentIndex() == 1:
                self.panel.setOffset(Base.Vector(0, 0, -self.w/2))
            else:
                self.panel.setOffset(Base.Vector(0, self.w / 2, 0))


        elif self.form.rb_9.isChecked():
            if self.form.cb_Orientation.currentIndex() == 1:
                self.panel.setOffset(Base.Vector(self.l / 2, 0,-self.w/2))
            else:
                self.panel.setOffset(Base.Vector(self.l / 2, self.w / 2, 0))

        FreeCADGui.Selection.clearSelection()

    def redraw(self):
        #print("redraw")

        if len(self.points) == 2 :
            self.paneldef.orientation = self.form.cb_Orientation.currentText()
            self.paneldef.name = self.form.cb_Name.currentText()
            self.paneldef.width = self.form.led_Width.text()
            self.paneldef.thickness = self.form.led_Thickness.text()
            self.paneldef.maxLength = self.form.led_MaxLength.text()
            self.setLength()
            self.panel.delete()
            self.panel.paneldef=self.paneldef
            self.panel.create(startPoint=self.points[0], endPoint=self.points[1], isShadow=True)
            self.offset()






class Paneldef:
    '''
    Class for defining panel object
    orientation : how the panel is viewed in a 2D plan
    '''

    def __init__(self):
        self.name=WFrameAttributes.getNames()[0]
        self.type=WFrameAttributes.getTypes()[0]
        self.width=2800
        self.thickness=12
        self.length = 1200
        self.maxLength=1200
        self.orientation=""
        self.viewTypes=["face","top"]
        #the default view type
        self.view=self.viewTypes[0]

#getters and setters
    def name(self,n):
        if n:self.name:n
        return self.name

    def type(self,t):
        if t:self.type=t
        return self.type

    def preset(self,p):
        if p:self.preset:p
        return self.preset

    def thickness(self,t):
        if t:self.thickness=t
        return  self.thickness

    def width(self,w):
        if w:self.w=w
        return self.width

    def orientation(self,o):
        if o:self.orientation=o
        return self.orientation

    def getOrientationTypes(self):
        return self.viewTypes

    def maxLength(self, l):
        if l:self.maxLength=l
        return self.maxLength

    def length(self, l):
        if l:
            self.length=l
        return self.length



class Panel():
    def __init__(self,paneldef):
        print("##Panel##\r\n")
        self.paneldef=paneldef
        self.angle = 0
        self.evalrot = self.paneldef.getOrientationTypes()
        self.structure = None
    def delete(self):
        if self.structure:
            self.structure.Document.removeObject(self.structure.Name)
            self.structure=None


    def create(self,structure=None,startPoint=Base.Vector(0,0,0),endPoint=Base.Vector(0,0,0),isShadow=False):
        self.points = [startPoint, endPoint]
        self.isShadow=isShadow
        self.currentInsPoint=self.points[0]


        # Panel creation
        if self.structure:
            self.structure = structure
        else:
            #self.structure = Arch.makeStructure(None, self.paneldef.length, self.paneldef.width, self.paneldef.height)
            self.structure = Arch.makePanel(None,length=self.paneldef.length,width=self.paneldef.width,thickness=self.paneldef.thickness)


        self.setAttributes()
        self.setOrientation()
        self.setRotations()
        return self


    def shadowToObject(self):
        if self.structure:
            #self.structure.ViewObject.Transparency = 0
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
        self.structure.Label = self.paneldef.name

        # set specific Attributes for WFrame
        WFrameAttributes.insertAttr(self.structure)
        self.structure.WFName = self.paneldef.name
        self.structure.Type = self.paneldef.type

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
        # Rotate panel on workingplane

        self.initialPlacement = self.initialPlacement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0), self.rotPlan)
        self.structure.Placement = self.initialPlacement

        # panel defaultview is from face
        self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),FreeCAD.Rotation(0, 0, 0))
        # panel up view
        if self.evalrot[1] in self.paneldef.orientation:
            self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),FreeCAD.Rotation(0, 0, 90))

        FreeCAD.ActiveDocument.recompute()

    def setRotations(self):
        '''set Angle on the current workingplane'''

        self.vecAngle = FreeCAD.Vector(0, 0, 0)
        self.vecAngle[0] = self.points[1][0] - self.points[0][0]
        self.vecAngle[1] = self.points[1][1] - self.points[0][1]
        self.vecAngle[2] = self.points[1][2] - self.points[0][2]

        # along workingplane normal
        self.angle= DraftVecUtils.angle(self.wplan.u,self.vecAngle,self.wplan.axis)
        self.angle = degrees(self.angle)

        #rotate in the current working plane
        Draft.rotate(self.structure, self.angle, center=self.points[0], axis=self.wplan.getNormal(), copy=False)
        FreeCAD.ActiveDocument.recompute()

