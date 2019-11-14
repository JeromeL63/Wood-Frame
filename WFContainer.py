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


import FreeCAD
from FreeCAD import Base


# function to draw container export bounding box

class Container:
    def __init__(self, name="Container"):
        self.lst = []
        self.min = Base.Vector(0, 0, 0)
        self.max = Base.Vector(0, 0, 0)
        self.name = name
        self.bbox = None

    def create(self, objlist):
        self.lst = objlist
        # calculate min point and max point
        for obj in self.lst:
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

        self.bbox = FreeCAD.ActiveDocument.addObject("Part::Box", self.name)
        self.bbox.Length = self.max.x - self.min.x
        self.bbox.Width = self.max.y - self.min.y
        self.bbox.Height = self.max.z - self.min.z
        self.bbox.Placement = FreeCAD.Placement(self.min, FreeCAD.Rotation(0, 0, 0))
        self.bbox.ViewObject.Transparency = 85
        # self.bbox.ViewObject.DrawStyle = "Dashed"
        FreeCAD.ActiveDocument.recompute()
        return self.bbox

    def getPoints(self):
        return [self.min,self.max]
