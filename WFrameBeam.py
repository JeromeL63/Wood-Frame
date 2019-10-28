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

__title__="FreeCAD WoodFrame Beam"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"

addBeamUI = __dir__ + "/Resources/Ui/AddBeam.ui"

from PySide import QtGui,QtCore
from pivy import coin


class WFrameBeam():
    """WFrameBeam"""

    def __init__(self):
        self.view = None
        self.units = None
        self.points = []



    def GetResources(self):
        return {'Pixmap'  :  __dir__ + '/Resources/icons/WFrameBeam.svg',
                'Accel' : "W,B",
                'MenuText': "WFrameBeam",
                'ToolTip' : "Create an advanced beam with better positionning method"}

    def Activated(self):
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.units = FreeCAD.Units.Quantity(1.0, FreeCAD.Units.Length)

        FreeCADGui.Snapper.show()

        panel=Ui_Definition()
        FreeCADGui.Control.showDialog(panel)
        return

    def IsActive(self):
        if FreeCADGui.ActiveDocument:

            return True
        else:
            return False

    def beamVector(self):
        self.tracker = DraftTrackers.lineTracker()
        self.tracker.on()
        #FreeCADGui.Snapper.getPoint(callback=self.point1,extradlg=self.definition, title="Select the origin of the beam")
        FreeCADGui.Snapper.show()
        #self.pt=FreeCADGui.Snapper.snap(FreeCAD.Vector(0,0,0))
        print(self.pt)


    def point1(self,point,obj=None):
        if point == None:
            self.tracker.finalize()
            return
        self.points.append(point)
        # ask for a second point
        FreeCADGui.Snapper.getPoint(last=point, callback=self.point2,movecallback=self.update, title="Select the end of the beam")

    def point2(self,point,obj=None):
        self.points.append(point)
        self.points[0] = FreeCAD.DraftWorkingPlane.projectPoint(self.points[0])
        self.points[1] = FreeCAD.DraftWorkingPlane.projectPoint(self.points[1])

        self.tracker.finalize()
        self.definition()

    def accept(self):
        print("accepté")

    def update(self,point,info):
        dep = point

    def definition(self):
        print("definition")
        w=QtGui.QWidget()
        ui=FreeCADGui.UiLoader()
        w.setWindowTitle("blabla")
        grid = QtGui.QGridLayout(w)
        FreeCADGui.Control.showDialog(w)
        return w





FreeCADGui.addCommand('WFrameBeam',WFrameBeam())


class Ui_Definition:
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(addBeamUI)
        self.beam = Beam(BeamDef())
        self.beamdef = self.beam.beamdef

        self.points=[]
        self.pt=None
        self.lastpoint=None
        self.isLength=False
        self.h=220
        self.w=100

        self.form.cb_Orientation.addItems(self.beamdef.getOrientationTypes())
        self.form.cb_Name.addItems(WFrameAttributes.getNames())
        self.form.led_Length.setVisible(False)
        self.form.lbl_Length.setVisible(False)

        #init default values
        self.form.led_Height.setText("220")
        self.form.led_Width.setText("100")
        self.form.cb_Name.setCurrentIndex(1)

        ##Wrong decimal point with french keyboard !
        ## QLocale doesn't solve problem
        validator= QtGui.QDoubleValidator(0,99999,1)
        self.form.led_Length.setValidator(validator)
        self.form.led_Height.setValidator(validator)
        self.form.led_Width.setValidator(validator)

        #connections
        self.form.cb_Orientation.currentIndexChanged.connect(self.sectionChanged)
        self.form.cb_Name.currentIndexChanged.connect(self.redraw)
        self.form.led_Width.textChanged.connect(self.sectionChanged)
        self.form.led_Height.textChanged.connect(self.sectionChanged)
        self.form.led_Length.textChanged.connect(self.redraw)
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
        self.curview=FreeCADGui.activeDocument().activeView()
        self.callbackClick = self.curview.addEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.mouseClick)
        self.callbackMove = self.curview.addEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.mouseMove)

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
                    if self.callbackClick:
                        self.curview.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(),self.callbackClick)
                    if self.callbackMove:
                        self.curview.removeEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.callbackMove)
                    self.callbackClick = None
                    self.callbackMove = None
                    self.points.append(self.pt)
                    print("len =1",self.points)
                    FreeCADGui.Snapper.off()
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


    def sectionChanged(self):
        self.h = float(self.beamdef.height)
        self.w = float(self.beamdef.width)

        #if cut view
        print("showLength",self.form.cb_Orientation.currentIndex())
        if self.form.cb_Orientation.currentIndex() == 2:
            self.form.led_Length.setVisible(True)
            self.form.lbl_Length.setVisible(True)
            self.form.led_Length.setText("1000")
            self.isLength=True

        else:
            if self.form.cb_Orientation.currentIndex() == 1:
                self.w = float(self.beamdef.height)
                self.h = float(self.beamdef.width)

            self.form.led_Length.setVisible(False)
            self.form.lbl_Length.setVisible(False)
            self.beam.length = ""
            self.isLength=False
        self.form.rb_5.setChecked(True)
        self.redraw()


    def accept(self):
        self.beam.shadowToObject()
        self.close()

    def reject(self):
        if self.beam:
            self.beam.delete()
        self.close()

    def close(self):
        if self.callbackClick:
            self.curview.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.callbackClick)
        if self.callbackMove:
            self.curview.removeEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.callbackMove)
        self.callbackClick = None
        self.callbackMove = None
        FreeCADGui.Control.closeDialog()


    def offset(self):
        #TODO dashed and dashdot line style doesn't work properly

        if self.form.rb_1.isChecked():
            if self.form.cb_Orientation.currentIndex() == 2:
                self.beam.setOffset(Base.Vector(-self.w / 2, -self.h / 2, 0))
            else:
                self.beam.setOffset(Base.Vector(0, -self.h / 2, -self.w / 2))
            self.beam.setSolid()

        elif self.form.rb_2.isChecked():
            if self.form.cb_Orientation.currentIndex() == 2:
                self.beam.setOffset(Base.Vector(0, -self.h / 2, 0))
                self.beam.setSolid()
            else:
                self.beam.setOffset(Base.Vector(0, -self.h / 2, 0))
                #self.beam.setDashDot()

        elif self.form.rb_3.isChecked():
            if self.form.cb_Orientation.currentIndex() == 2:
                self.beam.setOffset(Base.Vector(self.w / 2, -self.h / 2, 0))
                self.beam.setSolid()
            else:
                self.beam.setOffset(Base.Vector(0, -self.h / 2, self.w / 2))
                #self.beam.setDashed()

        elif self.form.rb_4.isChecked():
            if self.form.cb_Orientation.currentIndex() == 2:
                self.beam.setOffset(Base.Vector(-self.w / 2, 0, 0))
                self.beam.setSolid()
            else:
                self.beam.setOffset(Base.Vector(0, 0, -self.w / 2))
                self.beam.setSolid()

        elif self.form.rb_5.isChecked():
            if self.form.cb_Orientation.currentIndex() == 2:
                self.beam.setOffset(Base.Vector(0, 0, 0))
                self.beam.setSolid()
            else:
                self.beam.setOffset(Base.Vector(0, 0, 0))
                #self.beam.setDashDot()

        elif self.form.rb_6.isChecked():
            if self.form.cb_Orientation.currentIndex() == 2:
                self.beam.setOffset(Base.Vector(self.w / 2, 0, 0))
                self.beam.setSolid()
            else:
                self.beam.setOffset(Base.Vector(0, 0, self.w / 2))
                #self.beam.setDashed()

        elif self.form.rb_7.isChecked():
            if self.form.cb_Orientation.currentIndex() == 2:
                self.beam.setOffset(Base.Vector(-self.w / 2, self.h / 2, 0))
                self.beam.setSolid()
            else:
                self.beam.setOffset(Base.Vector(0, self.h / 2, -self.w / 2))
                self.beam.setSolid()

        elif self.form.rb_8.isChecked():
            if self.form.cb_Orientation.currentIndex() == 2:
                self.beam.setOffset(Base.Vector(0, self.h / 2, 0))
                self.beam.setSolid()
            else:
                self.beam.setOffset(Base.Vector(0, self.h / 2, 0))
                #self.beam.setDashDot()

        elif self.form.rb_9.isChecked():
            if self.form.cb_Orientation.currentIndex() == 2:
                self.beam.setOffset(Base.Vector(self.w / 2, self.h / 2, 0))
            else:
                self.beam.setOffset(Base.Vector(0, self.h / 2, self.w / 2))
                #self.beam.setDashed()
        FreeCADGui.Selection.clearSelection()

    def redraw(self):
        print("redraw")

        if len(self.points) == 2 :
            self.beamdef.orientation = self.form.cb_Orientation.currentText()
            self.beamdef.name = self.form.cb_Name.currentText()
            self.beamdef.width = self.form.led_Width.text()
            self.beamdef.height = self.form.led_Height.text()
            if self.isLength:
                self.beamdef.length = self.form.led_Length.text()
            self.beam.delete()
            self.beam.beamdef=self.beamdef
            self.beam.create(startPoint=self.points[0], endPoint=self.points[1], isShadow=True)

            self.offset()






class BeamDef:
    '''
    Class for defining beam object
    orientation : how the beam is viewed in a 2D plan
    '''

    def __init__(self):
        self.name=WFrameAttributes.getNames()[0]
        self.type=WFrameAttributes.getTypes()[0]
        self.width=45
        self.height=145
        self.length=1000
        self.orientation=""
        self.viewTypes=["face","up","cut"]
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

    def height(self,h):
        if h:self.height=h
        return  self.height

    def width(self,w):
        if w:self.w=w
        return self.width

    def orientation(self,o):
        if o:self.orientation=o
        return self.orientation

    def getOrientationTypes(self):
        return self.viewTypes

    def length(self, l):
        if l:self.length=l
        return self.length



class Beam():
    def __init__(self,beamdef):
        print("##Beam##\r\n")
        self.beamdef=beamdef
        self.angle = 0
        self.evalrot = self.beamdef.getOrientationTypes()
        self.structure = None
    def delete(self):
        if self.structure:
            self.structure.Document.removeObject(self.structure.Name)
            self.structure=None


    def create(self,structure=None,startPoint=Base.Vector(0,0,0),endPoint=Base.Vector(0,0,0),isShadow=False):
        self.points = [startPoint, endPoint]
        self.isShadow=isShadow
        self.currentInsPoint=self.points[0]

        #set length of the beam
        if not self.evalrot[2] in self.beamdef.orientation:
            self.beamdef.length= DraftVecUtils.dist(self.points[0],self.points[1])

        # Beam creation
        if self.structure:
            self.structure = structure
        else:
            self.structure = Arch.makeStructure(None, self.beamdef.length, self.beamdef.width, self.beamdef.height)


        self.setAttributes()
        self.setOrientation()
        self.setRotations()
        return self


    def shadowToObject(self):
        if self.structure:
            self.structure.ViewObject.Transparency = 0
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
        self.structure.IfcType = "Beam"
        self.structure.Tag = "Wood-Frame"
        self.structure.Label = self.beamdef.name

        # set specific Attributes for WFrame
        WFrameAttributes.insertAttr(self.structure)
        self.structure.WFName = self.beamdef.name
        self.structure.Type = self.beamdef.type

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
        # Rotate beam on workingplane

        self.initialPlacement = self.initialPlacement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0), self.rotPlan)
        self.structure.Placement = self.initialPlacement

        # beam defaultview is from face
        self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),FreeCAD.Rotation(0, 0, -90))
        # beam up view
        if self.evalrot[1] in self.beamdef.orientation:
            self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),FreeCAD.Rotation(0, 0, 90))
        # beam cut view
        elif self.evalrot[2] in self.beamdef.orientation:
            self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),FreeCAD.Rotation(90, 0, 0))

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


class BeamVector():
    """this class retreive 2 points selected by user"""
    def __init__(self):


        self.doc=FreeCAD.ActiveDocument
        if self.doc == None:
            FreeCAD.newDocument("Sans_Nom")
            
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.units=FreeCAD.Units.Quantity(1.0,FreeCAD.Units.Length)
        self.points = []

    def start(self):
#snapper starting
        self.tracker = DraftTrackers.lineTracker()
        self.tracker.on()
        FreeCADGui.Snapper.getPoint(callback=self.getPoint1,title="Select the origin of the beam")

    def getPoint1(self,point,obj=None):
#retreive snapped point
        if point == None:
            self.tracker.finalize()
            return        
        self.points.append(point)


#ask for a second point
        self.pt=FreeCADGui.Snapper.getPoint(last=point, callback=self.getPoint2,extradlg=Ui_Definition, movecallback=self.update, title="Select the end of the beam")


    def getPoint2(self,point,obj=None):
        self.points.append(point)
        self.points[0]=FreeCAD.DraftWorkingPlane.projectPoint(self.points[0])
        self.points[1] = FreeCAD.DraftWorkingPlane.projectPoint(self.points[1])

        print(self.points)

        self.tracker.finalize()
        self.launchUI()

    def update(self,point,info):
        dep = point

    def launchUI(self):
        start(self.points)



class start():
    def __init__(self,points):
        panel = Ui_Definition(points)
        FreeCADGui.Control.showDialog(panel)





class BeamOffsetNumPad():
    def __init__(self,beam):
        print("##BeamTracker## Beam Shadow \r\n")
        #used to prevent first click
        self.beam=beam
        self.clickCount=0
        self.boundingBoxExist= False
        #self.beam=beam        
        self.points = self.beam.points
        self.angle=0
        self.evalrot = self.beam.beamdef.getOrientationTypes()
        self.structure = None

        ###TODO numpad Positionning disabled at the moment

        # try to retreive keyboard numpad to place beam with points
        self.curview= Draft.get3DView()
        print("##BeamTracker##: please use numpad or double click/press enter to terminate")
        #self.call= self.curview.addEventCallback("SoEvent",self.action)
        self.status="PAD_5"
        self.opoint=FreeCAD.Vector(0,0,0)




####ACTION

    def action(self, arg):

        h=float(self.beam.beamdef.height)
        w=float(self.beam.beamdef.width)
        if self.evalrot[1] in self.beam.beamdef.orientation:
            w=float(self.beam.beamdef.height)
            h=float(self.beam.beamdef.width)



        if (arg["Type"] == "SoMouseButtonEvent") and (arg["Button"] == "BUTTON1") and  (arg["State"] == "UP"):
            self.clickCount+=1
            print("##BeamTracker## Mouse BUTTON1 pressed\r\n")
            if self.clickCount == 2:
                self.finish()
            elif self.clickCount >2:
                self.clickCount=1


        elif (arg["Type"] == "SoKeyboardEvent") and (arg["State"] == "UP") :

            if arg["Key"] == "ESCAPE":
                self.finish()
            # numpad assignement for beam positionning
            if arg["Key"] == "PAD_1":
                if self.evalrot[2] in self.beam.beamdef.orientation:
                    self.beam.setOffset(Base.Vector(-w / 2, -h / 2, 0))
                else:
                    self.beam.setOffset(Base.Vector(0,-h/2, -w/2))
                self.beam.setSolid()

            if arg["Key"] == "PAD_2":
                if self.evalrot[2] in self.beam.beamdef.orientation:
                    self.beam.setOffset(Base.Vector(0,-h/2, 0))
                    self.beam.setSolid()

                else:
                    self.beam.setOffset(Base.Vector(0,-h/2, 0))
                    self.beam.setDashDot()

            if arg["Key"] == "PAD_3":
                if self.evalrot[2] in self.beam.beamdef.orientation:
                    self.beam.setOffset(Base.Vector(w/2, -h/2, 0))
                    self.beam.setSolid()

                else:
                    self.beam.setOffset(Base.Vector(0,-h/2, w/2))
                    self.beam.setDashed()

            if arg["Key"] == "PAD_4":
                if self.evalrot[2] in self.beam.beamdef.orientation:
                    self.beam.setOffset(Base.Vector(-w / 2, 0, 0))
                    self.opoint[0]=w/2.0
                    self.beam.setSolid()
                else:
                    self.beam.setOffset(Base.Vector(0, 0, -w / 2))
                    self.opoint[2]=w/2.0
                    self.beam.setSolid()

            if arg["Key"] == "PAD_5":
                if self.evalrot[2] in self.beam.beamdef.orientation:
                    self.beam.setOffset(Base.Vector(0, 0, 0))
                    self.beam.setSolid()

                else:
                    self.beam.setOffset(Base.Vector(0,0,0))
                    self.beam.setDashDot()


            if arg["Key"] == "PAD_6":
                if self.evalrot[2] in self.beam.beamdef.orientation:
                    self.beam.setOffset(Base.Vector(w/2, 0, 0))
                    self.beam.setSolid()
                else:
                    self.beam.setOffset(Base.Vector(0, 0, w / 2))
                    self.beam.setDashed()

            if arg["Key"] == "PAD_7":
                if self.evalrot[2] in self.beam.beamdef.orientation:
                    self.beam.setOffset(Base.Vector(-w / 2, h / 2, 0))
                    self.beam.setSolid()
                else:
                    self.beam.setOffset(Base.Vector(0, h / 2, -w / 2))
                    self.beam.setSolid()

            if arg["Key"] == "PAD_8":
                if self.evalrot[2] in self.beam.beamdef.orientation:
                    self.beam.setOffset(Base.Vector(0, h / 2, 0))
                    self.beam.setSolid()
                    self.opoint[0]=0.0
                else:
                    self.beam.setOffset(Base.Vector(0, h / 2, 0))
                    self.opoint[2]=0.0
                    self.beam.setDashDot()

            if arg["Key"] == "PAD_9":
                if self.evalrot[2] in self.beam.beamdef.orientation:
                    self.beam.setOffset(Base.Vector(w / 2, h / 2, 0))
                    self.opoint[0]=-w/2.0
                else:
                    self.beam.setOffset(Base.Vector(0, h / 2, w / 2))
                    self.beam.setDashed()

            if arg["Key"] == "PAD_ENTER" or arg["Key"] == "RETURN":

                self.finish()

    def finish(self,closed=False):
       if self.call:
            try:
                self.curview.removeEventCallback("SoEvent",self.call)
                self.beam.shadowToObject()

            #except RuntimeError:
            except :
                pass
            self.call=None

