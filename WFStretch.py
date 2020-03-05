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

import os
__dir__ = os.path.dirname(__file__)

import FreeCADGui,FreeCAD,Part
from PySide import QtGui, QtCore
import WFUtils

class WFStretch():
    """WFrameStretch command"""

    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/WFStretch.svg',
                'Accel': "W,S",
                'MenuText': "Stretch Object",
                'ToolTip': "Stretch Object"}

    def Activated(self):
        panel = Ui_Stretch(FreeCADGui.Selection.getSelection())
        FreeCADGui.Control.showDialog(panel)

    def IsActive(self):
        boollst = []
        # test if the selected object is a container
        if FreeCAD.GuiUp:
            for obj in FreeCADGui.Selection.getSelection():
                if hasattr(obj, "Proxy"):
                    if hasattr(obj.Proxy, "__getstate__"):
                        if obj.Proxy.__getstate__() == "Structure":
                            boollst.append(True)
                        else : boollst.append(False)
                    else :boollst.append(False)
                else : boollst.append(False)
        out = False
        if len(FreeCADGui.Selection.getSelection())>0:
            if not False in boollst: out =True
        return out

FreeCADGui.addCommand('WF_Stretch', WFStretch())


class Ui_Stretch():
    def __init__(self,objlist):
        loader = FreeCADGui.UiLoader()

        self.objlist=objlist
        FreeCADGui.Selection.clearSelection()
        self.distValue=0
        self.form = QtGui.QWidget()
        self.form.setWindowTitle("Stretch")
        grid = QtGui.QGridLayout(self.form)
        self.lbl = QtGui.QLabel("Selection set:")
        self.distance = loader.createWidget("Gui::InputField")
        self.distance.setText(FreeCAD.Units.Quantity(self.distValue,FreeCAD.Units.Length).UserString)

        grid.addWidget(self.lbl, 0, 0, 1, 1)
        grid.addWidget(self.distance, 1, 1, 1, 1)
        self.objlist[0].Base.Visibility = True
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.runCommand('Std_BoxElementSelection', 0)

        QtCore.QObject.connect(self.distance, QtCore.SIGNAL("valueChanged(double)"), self.setDistance)

    def accept(self):
        FreeCADGui.Control.closeDialog()
        ###TODO: Séparer les faces ne fonction des objects
        sel=FreeCADGui.Selection.getSelectionEx()
        for obj in self.objlist:
            for selection in sel:
                if selection.HasSubObjects:
                    if obj.Name == selection.ObjectName:
                        for i, sub in enumerate(selection.SubObjects):
                            if faceIsOnNormalExtrusion(obj,selection.SubObjects[i]):
                                stretch(obj,selection.SubObjects[i],self.distValue)
                        FreeCAD.ActiveDocument.recompute()
                else :
                    print(selection.ObjectName + " has no sub object")

    def setDistance(self, val):
        self.distValue = val



def stretch(obj,face,distance):
    # function to create an extrusion of a face along normal with the given distance

    print("##Stretch##")
    # if placement is on selection
    pt=obj.Base.Placement.Base
    if face.isInside(pt,0,True):
        # retrieve normal extrusion
        normal= obj.Base.Shape.normalAt(0,0)
        # multiply by distance
        normal.multiply(-distance)
        # then move placement BASE
        obj.Base.Placement.Base=obj.Base.Placement.Base.add(normal)

    obj.Length = obj.Length + FreeCAD.Units.Quantity(distance, FreeCAD.Units.Length)


def lineIntersectFace(A,B,face):
    # return a vertex if vector AB cross face
    # A ,B : two points defining line
    # face : Part::Face

    lineVector = B - A
    # face's normal
    normalPlan = face.normalAt(0, 0)
    p1 = face.CenterOfMass
    d = -((normalPlan.x * p1.x) + (normalPlan.y * p1.y) + (normalPlan.z * p1.z))

    if lineVector.dot(normalPlan) == 0.0:
        # if A belongs to P : the full Line L is included in the Plane
        if (normalPlan.x * A.x) + (normalPlan.y * A.y) + (normalPlan.z * A.z) + d == 0.0:
            return A
        # if not the Plane and line are parallel without intersection
        else:
            return None
    else:
        #NOTE: due to float precision we have to cast the results
        precision= 10000
        resultcasted = (normalPlan.x * lineVector.x + normalPlan.y * lineVector.y + normalPlan.z * lineVector.z)
        resultcasted = int(resultcasted * precision)
        resultcasted = resultcasted / precision

        if resultcasted == 0.0:
            return None
        k = -1 * (normalPlan.x * A.x + normalPlan.y * A.y + normalPlan.z * A.z + d) / (normalPlan.x * lineVector.x + normalPlan.y * lineVector.y + normalPlan.z * lineVector.z)
        tx = A.x + k * lineVector.x
        ty = A.y + k * lineVector.y
        tz = A.z + k * lineVector.z
        crossVert = FreeCAD.Vector(tx, ty, tz)
        #TODO: due to float precision we have to cast the results
        return crossVert

def faceIsOnNormalExtrusion(obj,face):
    #get insertion point
    A= obj.Placement.Base
    #get normal extrusion
    B= obj.Base.Shape.normalAt(0,0)
    # multiply by length and more
    B=B.multiply(obj.Length * 10.0)
    #test if line cross face
    if lineIntersectFace(A,B,face):
        return True
    else:
        return False
