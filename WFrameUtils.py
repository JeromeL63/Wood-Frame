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
    import FreeCADGui


def filename():
    act=FreeCADGui.ActiveDocument.Document.FileName
    return act


class WFrameUtils:
    def __init__(self):
        pass
