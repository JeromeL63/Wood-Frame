# -*- coding: utf-8 -*-
# FreeCAD init script of the Wood Frame module
# (c) 2019 Jerome Laverroux

# ***************************************************************************
# *   (c) Jerome Laverroux (jerome.laverroux@free.fr) 2019                  *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# *   Jerome Laverroux 2019                                                 *
# ***************************************************************************/

__title__ = "FreeCAD Wood Frame API"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"

import FreeCAD
import os

if FreeCAD.GuiUp:
    import FreeCADGui,DraftTrackers,DraftVecUtils


__dir__ = os.path.dirname(__file__)

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator

class WFCopy():
    """WFrameAttributes"""

    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/WFCopy.svg',
                'Accel': "W,C",
                'MenuText': "Copy Object",
                'ToolTip': "Copy Object"}

    def Activated(self):
        self.tracker = DraftTrackers.lineTracker()
        self.tracker.on()
        FreeCADGui.Snapper.getPoint(callback=self.getBasePoint,title="Base Point")


    def getBasePoint(self,point,obj=None):
        if point == None:
            self.tracker.finalize()
        else:
            self.basePoint=point
            FreeCADGui.Snapper.getPoint(last=self.basePoint, callback=self.getPoint, movecallback=self.update,title="Translation vector")

    def getPoint(self,point,obj=None):
        if point == None:
            self.tracker.finalize()
        else:
            copySelection(basePoint=self.basePoint,endPoint=point)


    def update(self, point, info):
        pass


    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCADGui.ActiveDocument:
            return len(FreeCADGui.Selection.getSelection()) > 0
        else:
            return False


FreeCADGui.addCommand('WFCopy', WFCopy())


def copySelection(basePoint=FreeCAD.Vector(0, 0, 0), endPoint=FreeCAD.Vector(0, 0, 0), objlist=None, number=1):
    '''
    Function to copy objects

    :param basePoint: base point of displacement vector
    :param endPoint:  end point of displacement vector
    :param objlist: List of objects
    :param number: Number of copies
    '''
    for i in range(0, number):
        print(i)
        initial = []
        # save all objects present in file
        listobj = FreeCAD.ActiveDocument.Objects
        for lbl in listobj:
            initial.append(lbl.Label)

        print(initial)
        FreeCADGui.runCommand('Std_Copy', 0)
        FreeCADGui.runCommand('Std_Paste', 0)
        after = FreeCAD.ActiveDocument.Objects
        lst = []
        # search diff between before and after copy
        for lbl in after:
            if not lbl.Label in initial and not "CutVolume" in lbl.Label:
                # TODO cut volume isn't applied but is in right place :'(
                lst.append(lbl)

        FreeCADGui.Selection.clearSelection()

        for obj in lst:
            FreeCADGui.Selection.addSelection(obj)
        objlist = FreeCADGui.Selection.getSelection()

        translateSelection(basePoint, endPoint, objlist)


def translateSelection(basePoint,endPoint,objlist=None):
    if objlist :
        # now get vector between two points
        vec = FreeCAD.Vector(endPoint[0] - basePoint[0], endPoint[1] - basePoint[1], endPoint[2] - basePoint[2])
        print(vec)
        FreeCADGui.Selection.clearSelection()
        for obj in objlist:
            # and then translate Object Base point with the given vector
            origin = obj.Placement.Base
            print("origin",origin,"name",obj.Label)
            finalPoint = FreeCAD.Vector(origin[0] + vec[0], origin[1] + vec[1], origin[2] + vec[2])
            obj.Placement.Base = finalPoint
            FreeCADGui.Selection.addSelection(obj)
        FreeCAD.ActiveDocument.recompute()
