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
import FreeCADGui,WFUtils

__dir__ = os.path.dirname(__file__)

__title__ = "FreeCAD WoodFrame align View on workingPlane"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"


class WFrameAlignViewWPlane():
    """WFrameBeam"""

    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/AlignViewWPlane.svg',
                'Accel': "W,A",
                'MenuText': "Align camera view on workingplane",
                'ToolTip': "Align camera view on the current workingplane"}

    def Activated(self):
        WFUtils.alignView()
        return

    def IsActive(self):
        if FreeCADGui.ActiveDocument:
            return True
        else:
            return False





FreeCADGui.addCommand('WF_AlignViewWPlane', WFrameAlignViewWPlane())
