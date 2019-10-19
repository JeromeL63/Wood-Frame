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

        initial=[]
        #save all objects present in file
        listobj=FreeCAD.ActiveDocument.Objects
        for lbl in listobj:
            initial.append(lbl.Label)

        print(initial)
        FreeCADGui.runCommand('Std_Copy',0)
        FreeCADGui.runCommand('Std_Paste',0)
        after=FreeCAD.ActiveDocument.Objects
        lst=[]
        #search diff between before and after copy
        for lbl in after :
            if not lbl.Label in initial:
                lst.append(lbl)

        #lst = list of copied objects
        FreeCADGui.Selection.clearSelection()

        for obj in lst:
            FreeCADGui.Selection.addSelection(obj)
        self.selection=FreeCADGui.Selection.getSelection()
        #get base point of the first copied object
        basePoint=self.selection[0].Placement.Base
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
            # now get vector between two points
            vec=FreeCAD.Vector(point[0]-self.basePoint[0],point[1]-self.basePoint[1],point[2]-self.basePoint[2])


            for obj in self.selection:
                # and then translate base point with the given vector
                origin=obj.Placement.Base
                finalPoint =FreeCAD.Vector(origin[0]+vec[0],origin[1]+vec[1],origin[2]+vec[2])
                obj.Placement.Base=finalPoint

        FreeCAD.ActiveDocument.recompute()

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


