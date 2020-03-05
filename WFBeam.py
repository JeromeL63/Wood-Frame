# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2019                                                    *
# *   Jerome LAVERROUX <jerome.laverroux@free.fr                            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

### TODO : Add function addNewName with the ui Button


import FreeCAD, Arch, Draft, ArchComponent, DraftVecUtils, ArchCommands, ArchStructure, math, FreeCADGui, WorkingPlane
from FreeCAD import Base, Vector, Rotation
from math import *

import DraftTrackers
import WFAttributes, WFUtils, WFDialogs

if FreeCAD.GuiUp:
    import FreeCADGui
else:
    def translate(ctxt, txt):
        return txt

# waiting for WFrame_rc and eventual FreeCAD integration
import os

__dir__ = os.path.dirname(__file__)

__title__ = "FreeCAD WoodFrame Beam"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"

from PySide import QtGui, QtCore
from pivy import coin


class WF_Beam():
    """WFBeam"""

    def __init__(self):
        self.view = None
        self.units = None
        self.points = []

    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/WF_Beam.svg',
                'Accel': "W,B",
                'MenuText': "Add beam",
                'ToolTip': "Create an advanced beam with better positioning method"}

    def Activated(self):
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.units = FreeCAD.Units.Quantity(1.0, FreeCAD.Units.Length)

        ###TODO Prepare File
        # if doesn't exist :
        # 1 : create WorkFrame group
        # 2 : Create Layers
        FreeCADGui.Snapper.show()
        panel = Ui_Definition()
        FreeCADGui.Control.showDialog(panel)
        return

    def IsActive(self):
        if FreeCADGui.ActiveDocument:

            return True
        else:
            return False


FreeCADGui.addCommand('WF_Beam', WF_Beam())


class Ui_Definition():
    def __init__(self):

        self.beam = Beam()
        self.points = []
        self.vecInLocalCoords = Base.Vector(0, 0, 0)
        self.pt = None
        self.lastpoint = None
        self.isLength = False
        self.h = self.beam.height
        self.w = self.beam.width

        self.form = QtGui.QWidget()
        self.form.setWindowTitle("Add beam")
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
        self.dim = WFDialogs.DimensionsWidget()
        self.dim.width.setText(FreeCAD.Units.Quantity(self.w, FreeCAD.Units.Length).UserString)
        self.dim.height.setText(FreeCAD.Units.Quantity(self.h, FreeCAD.Units.Length).UserString)
        grid.addWidget(self.dim, 1, 0, 1, 1)

        QtCore.QObject.connect(self.dim.width, QtCore.SIGNAL("valueChanged(double)"), self.setWidth)
        QtCore.QObject.connect(self.dim.height, QtCore.SIGNAL("valueChanged(double)"), self.setHeight)
        QtCore.QObject.connect(self.dim.length, QtCore.SIGNAL("valueChanged(double)"), self.setLength)
        self.dim.lbl_length.setVisible(False)
        self.dim.length.setVisible(False)

        ### DESCRIPTION CONTAINER ###
        self.desc = WFDialogs.DescriptionWidget(orientations=self.beam.orientationTypes)
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

        # reimplement getPoint from draft, without Dialog taskbox

        # start events
        self.curview = FreeCADGui.activeDocument().activeView()
        self.callbackClick = self.curview.addEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(),
                                                               self.mouseClick)
        self.callbackMove = self.curview.addEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.mouseMove)
        self.callbackKeys = None
        self.enterkeyCode = 65293
        self.returnKeyCode = 65421

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

    def setWidth(self, val):
        self.beam.width = val
        self.sectionChanged()

    def setHeight(self, val):
        self.beam.height = val
        self.sectionChanged()

    def setLength(self, val):
        self.beam.length = val
        self.redraw()

    def closeEvents(self):
        # remove all events
        if self.callbackClick:
            self.curview.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.callbackClick)
        if self.callbackMove:
            self.curview.removeEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.callbackMove)
        if self.callbackKeys:
            self.curview.removeEventCallbackPivy(coin.SoKeyboardEvent.getClassTypeId(), self.callbackKeys)

        self.callbackClick = None
        self.callbackMove = None

    def keys(self, event_cb):
        event = event_cb.getEvent()
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

    # retrieve point clicked with snap
    def mouseClick(self, event_cb):

        event = event_cb.getEvent()
        if event.getButton() == 1:
            if event.getState() == coin.SoMouseButtonEvent.DOWN:
                # start point
                if len(self.points) == 0:
                    self.points.append(self.pt)
                    self.coords.oX.setText(str(round(self.pt[0], 2)))
                    self.coords.oY.setText(str(round(self.pt[1], 2)))
                    self.coords.oZ.setText(str(round(self.pt[2], 2)))
                    self.lastpoint = self.pt
                # end point
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
                    # start keyboard events
                    self.callbackKeys = self.curview.addEventCallbackPivy(coin.SoKeyboardEvent.getClassTypeId(),
                                                                          self.keys)
                    self.redraw()

    # mouse move to show sanp points
    def mouseMove(self, event_cb):
        event = event_cb.getEvent()
        mousepos = event.getPosition()
        ctrl = event.wasCtrlDown()
        shift = event.wasShiftDown()

        self.pt = FreeCADGui.Snapper.snap(mousepos, lastpoint=self.lastpoint, active=ctrl, constrain=shift)
        if hasattr(FreeCAD, "DraftWorkingPlane"):
            FreeCADGui.draftToolBar.displayPoint(self.pt, None, plane=FreeCAD.DraftWorkingPlane,
                                                 mask=FreeCADGui.Snapper.affinity)

    def sectionChanged(self):
        self.h = float(self.beam.height)
        self.w = float(self.beam.width)

        # if cut view
        if self.desc.cb_Orientation.currentIndex() == 2:
            self.dim.length.setVisible(True)
            self.dim.lbl_length.setVisible(True)
            self.dim.length.setText(FreeCAD.Units.Quantity(1000, FreeCAD.Units.Length).UserString)
            self.isLength = True

        else:
            if self.desc.cb_Orientation.currentIndex() == 1:
                self.w = float(self.beam.height)
                self.h = float(self.beam.width)
            self.dim.length.setVisible(False)
            self.dim.lbl_length.setVisible(False)
            self.beam.length = ""
            self.isLength = False
        self.inspoint.rb_5.setChecked(True)
        self.redraw()

    def accept(self):
        self.beam.shadowToObject()
        self.close()

    def reject(self):
        if self.beam:
            self.beam.delete()
        self.close()

    def close(self, rejected=False):
        self.closeEvents()
        FreeCADGui.Control.closeDialog()
        if rejected:
            if self.beam:
                self.beam.delete()

    def offset(self):
        if self.inspoint.rb_1.isChecked():
            pos = 1
        elif self.inspoint.rb_2.isChecked():
            pos = 2
        elif self.inspoint.rb_3.isChecked():
            pos = 3
        elif self.inspoint.rb_4.isChecked():
            pos = 4
        elif self.inspoint.rb_5.isChecked():
            pos = 5
        elif self.inspoint.rb_6.isChecked():
            pos = 6
        elif self.inspoint.rb_7.isChecked():
            pos = 7
        elif self.inspoint.rb_8.isChecked():
            pos = 8
        elif self.inspoint.rb_9.isChecked():
            pos = 9

        pt = WFUtils.offset(height=self.h, width=self.w, orientation=self.beam.orientation, position=pos)
        self.beam.setOffset(off=pt)
        FreeCADGui.Selection.clearSelection()

    def redraw(self):
        if len(self.points) == 2:
            self.beam.orientation = self.desc.cb_Orientation.currentIndex()
            self.beam.name = self.desc.cb_Name.currentText()
            self.beam.delete()
            self.beam.create(start=self.points[0], end=self.points[1], isShadow=True)
            self.offset()


class Beam():
    '''
    Create a beam object using makeStructure from Arch
    create: create the beam in shadow mode(transparence)
    delete: undo and delete the beam
    shadowtoObject: change transparence to 0
    setoffset : change the insertion point of the beam
    '''

    def __init__(self):
        print("##Beam##\r\n")
        self.name = WFAttributes.getNames()[0]
        self.type = WFAttributes.getTypes()[0]
        self.width = 45
        self.height = 145
        self.length = 1000
        self.orientationTypes = ["face", "top", "cut"]
        self.orientation = 0
        self.isShadow=True
        self.currentInsPoint=Base.Vector(0,0,0)
        self.points = [Base.Vector(0, 0, 0), Base.Vector(0, 0, 0)]
        self.angle = 0
        self.structure = None
        self.profil=None

    def delete(self):
        if self.structure:
            self.structure.Document.removeObject(self.structure.Name)
            self.structure = None
        if self.profil:
            self.profil.Document.removeObject(self.profil.Name)
            self.profil = None

    def create(self, structure=None, start=Base.Vector(0, 0, 0), end=Base.Vector(0, 0, 0), isShadow=False):
        '''create(self, structure=None, startPoint=Base.Vector(0, 0, 0), endPoint=Base.Vector(0, 0, 0), isShadow=False)
        create the beam
        structure : copy of an existent beam
        start : the origin point in global coords
        end : the end point in global coords
        isShadow: transparent mode
        '''
        self.points = [start, end]
        self.isShadow = isShadow
        self.currentInsPoint = self.points[0]

        # set length of the beam
        if not self.orientation == 2:
            self.length = DraftVecUtils.dist(self.points[0], self.points[1])

        # Beam creation
        if self.structure:
            self.structure = structure
        else:
            if not self.profil:
                profpoints=[]
                profpoints.append(FreeCAD.Vector(-self.width /2,-self.height/2,0))
                profpoints.append(FreeCAD.Vector(self.width/2, -self.height/2, 0))
                profpoints.append(FreeCAD.Vector(self.width/2,self.height/2, 0))
                profpoints.append(FreeCAD.Vector(-self.width/2,self.height/2, 0))
                self.profil = Draft.makeWire(profpoints,closed=True)
                self.profil.Label=str(self.width)+"x"+str(self.height)+"_0"

            #self.structure = Arch.makeStructure(None, self.length, self.width, self.height)
            self.structure = Arch.makeStructure(self.profil, self.length)
            self.structure.MoveBase=True
            #Nodes : nodes .... the dark face

            if not self.orientation== 2:
                self.structure.Nodes=[self.points[0],self.points[1]]
            else :
                ###TODO
                pass


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

    def setOffset(self, off=Base.Vector(0, 0, 0)):
        # function used by setoffsetnumpad
        orig = self.points[0]
        orig = FreeCAD.DraftWorkingPlane.getLocalCoords(orig)
        vector = FreeCAD.Vector(orig[0] - off[0], orig[1] - off[1], orig[2] - off[2])
        vector = FreeCAD.DraftWorkingPlane.getGlobalCoords(vector)
        self.currentInsPoint = vector
        self.setOrientation()
        self.setRotations()

    def setOrientation(self):

        # get rotations between zplan and current plan YESSSS
        self.wplan = FreeCAD.DraftWorkingPlane
        self.rotPlan = self.wplan.getRotation().Rotation

        # Initialize placement
        # set the origin point
        self.initialPlacement = FreeCAD.Base.Placement(self.currentInsPoint, FreeCAD.Rotation(0, 0, 0),
                                                       FreeCAD.Vector(0, 0, 0))
        # Rotate beam on workingplane

        self.initialPlacement = self.initialPlacement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0), self.rotPlan)
        #self.structure.Placement = self.initialPlacement
        self.profil.Placement=self.initialPlacement

        # beam defaultview is from face
        #self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),
        #                                                                             FreeCAD.Rotation(0, 0, -90))

        self.profil.Placement=self.profil.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),
                                                                                     FreeCAD.Rotation(0, 90, 0))
        # beam up view
        if self.orientation == 1:
            #self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),
            #                                                                             FreeCAD.Rotation(0, 0, 90))
            self.profil.Placement = self.profil.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),
                                                                                   FreeCAD.Rotation(90, 0, 0))
        # beam cut view
        elif self.orientation == 2:
            #self.structure.Placement = self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),
            #                                                                             FreeCAD.Rotation(90, 0, 0))
            self.profil.Placement = self.profil.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0, 0, 0),
                                                                                   FreeCAD.Rotation(0, -90, 0))

        FreeCAD.ActiveDocument.recompute()

    def setRotations(self):
        #self.structure=WFUtils.setRotations(self.structure, points=self.points, wplan=self.wplan)
        self.profil=WFUtils.setRotations(self.profil, points=self.points, wplan=self.wplan)
        FreeCAD.ActiveDocument.recompute()

