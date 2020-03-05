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
import Draft
from FreeCAD import Base
import os
from math import *


if FreeCAD.GuiUp:
    import FreeCADGui,DraftTrackers,DraftVecUtils


__dir__ = os.path.dirname(__file__)

def QT_TRANSLATE_NOOP(ctx,txt): return txt # dummy function for the QT translator

def alignView():
    #function to align view to the current WorkingPlane
    c = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()
    r = FreeCAD.DraftWorkingPlane.getRotation().Rotation.Q
    c.orientation.setValue(r)

def getTagList():
    #function to retrieve tags in document
    taglist = []
    for obj in FreeCAD.ActiveDocument.Objects :
        if hasattr(obj,"Tag"):
            if not obj.Tag in taglist:
                taglist.append(str(obj.Tag))

    return taglist


def listFilter(items):
    #Function to list selection by tag
    doc = FreeCAD.ActiveDocument
    objs = doc.Objects
    objlist = []
    for item in items :
        if item == "Selection":
            for obj in FreeCADGui.Selection.getSelection() :
                objlist.append(obj)
        taglist = getTagList()
        for tag in taglist :
            if item == tag :
                for obj in objs:
                    if FreeCADGui.ActiveDocument.getObject(obj.Name).Visibility:
                        if hasattr(obj,"Proxy"):
                            if hasattr(obj.Proxy,"Type"):
                                if hasattr(obj,"Tag"):
                                    if obj.Tag == item :
                                        objlist.append(obj)

    s = []
    for i in objlist:
        if i not in s:
            s.append(i)
    return s





class WFCopy():
    """WFrameAttributes"""

    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/WFCopy.svg',
                'Accel': "6",
                'MenuText': "Copy Object",
                'ToolTip': "Copy Object"}

    def Activated(self):
        self.tracker = DraftTrackers.lineTracker()
        self.tracker.on()
        self.objList=FreeCADGui.Selection.getSelection()
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
            copySelection(base=self.basePoint,end=point,objlist=self.objList)


    def update(self, point, info):
        pass


    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCADGui.ActiveDocument:
            return len(FreeCADGui.Selection.getSelection()) > 0
        else:
            return False






def copySelection(base=FreeCAD.Vector(0, 0, 0), end=FreeCAD.Vector(0, 0, 0), objlist=None, number=1):
    '''
    Function to copy objects

    :param base: base point of displacement vector
    :param end:  end point of displacement vector
    :param objlist: List of objects
    :param number: Number of copies
    '''
    vec = Base.Vector(0, 0, 0)
    vec.x = end.x - base.x
    vec.y = end.y - base.y
    vec.z = end.z - base.z

    if objlist:
        print ("launch copies")
        for i in range(0, number):
           objlist = Draft.move(objlist, vec, copy=True)
        FreeCAD.ActiveDocument.recompute()


FreeCADGui.addCommand('WF_Copy', WFCopy())




def offset(height,width,orientation=0,position=5):
    '''
    This function return an offset point calculated with height width and orientation
    :param height: part's height
    :param width: part's width
    :param orientation: orientation between 0 to 2
    :param position: from 1 to 9 equal numpad positions
    :return: Base.Vector of the offset
    '''
    out=Base.Vector(0,0,0)

    #TODO dashed and dashdot line style doesn't work properly

    if position == 1:
        if orientation == 2:
            out=Base.Vector(-width / 2, -height / 2, 0)
        else:
            out=Base.Vector(0, -height / 2, -width / 2)
        #self.beam.setSolid()

    elif position == 2:
        if orientation == 2:
            out=Base.Vector(0, -height / 2, 0)
            #self.beam.setSolid()
        else:
            out=Base.Vector(0, -height / 2, 0)
            #self.beam.setDashDot()

    elif position == 3:
        if orientation == 2:
            out=Base.Vector(width / 2, -height / 2, 0)
            #self.beam.setSolid()
        else:
            out=Base.Vector(0, -height / 2, width / 2)
            #self.beam.setDashed()

    elif position == 4:
        if orientation == 2:
            out=Base.Vector(-width / 2, 0, 0)
            #self.beam.setSolid()
        else:
            out=Base.Vector(0, 0, -width / 2)
            #self.beam.setSolid()

    elif position == 5:
        if orientation == 2:
            out=Base.Vector(0, 0, 0)
            #self.beam.setSolid()
        else:
            out=Base.Vector(0, 0, 0)
            #self.beam.setDashDot()

    elif position == 6:
        if orientation == 2:
            out=Base.Vector(width / 2, 0, 0)
            #self.beam.setSolid()
        else:
            out=Base.Vector(0, 0, width / 2)
            #self.beam.setDashed()

    elif position == 7:
        if orientation == 2:
            out=Base.Vector(-width / 2, height / 2, 0)
            #self.beam.setSolid()
        else:
            out=Base.Vector(0, height / 2, -width / 2)
            #self.beam.setSolid()

    elif position == 8:
        if orientation == 2:
            out=Base.Vector(0, height / 2, 0)
            #self.beam.setSolid()
        else:
            out=Base.Vector(0, height / 2, 0)
            #self.beam.setDashDot()

    elif position == 9:
        if orientation == 2:
            out=Base.Vector(width / 2, height / 2, 0)
        else:
            out=Base.Vector(0, height / 2, width / 2)
            #self.beam.setDashed()
    return out




def setRotations(structure=None,points=[Base.Vector(0,0,0),Base.Vector(0,0,0)],wplan=None):
    '''Rotate structure by the given two points on the current workingplane wplan'''
    import DraftVecUtils,Draft

    vecAngle = FreeCAD.Vector(0, 0, 0)
    vecAngle[0] = points[1][0] - points[0][0]
    vecAngle[1] = points[1][1] - points[0][1]
    vecAngle[2] = points[1][2] - points[0][2]

    # along workingplane normal
    angle = DraftVecUtils.angle(wplan.u, vecAngle, wplan.axis)
    angle = degrees(angle)

    # rotate in the current working plane
    Draft.rotate(structure, angle, center=points[0], axis=wplan.getNormal(), copy=False)

    return structure

def toNormalizedVector(vec,lg):
    return FreeCAD.Vector(vec[0] / lg,vec[1] /lg,vec[2]/lg)

def normalizedToVector(vec,lg):
    return FreeCAD.Vector(vec[0] * lg, vec[1] * lg, vec[2] * lg)




