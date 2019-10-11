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


import FreeCAD
from math import *
from PySide import QtCore,QtGui

if FreeCAD.GuiUp:
    import FreeCADGui
    from FreeCAD import Console
    from DraftTools import translate
else:
    def translate(ctxt,txt):
        return txt
# waiting for WFrame_rc and eventual FreeCAD integration
import os
__dir__ = os.path.dirname(__file__)
__title__="FreeCAD WoodFrame Attributes"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"

attrUI=__dir__+"/Resources/AttrEdit.ui"

class WFrameAttributes():
    """WFrameAttributes"""

    def GetResources(self):
        return {'Pixmap'  :  __dir__ + '/Resources/icons/WFrameLib.svg',
                'Accel' : "W,A",
                'MenuText': "WFrameAttributes",
                'ToolTip' : "Edit attributes"}

    def Activated(self):
        panel = Ui_AttrEdit()
        FreeCADGui.Control.showDialog(panel)
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCADGui.ActiveDocument:
            return len(FreeCADGui.Selection.getSelection()) > 0
        else:
            return False


FreeCADGui.addCommand('WFrameAttributes',WFrameAttributes())


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


def getAttrList():
    '''
    Get the attributes/properties list available
    Name: the attribute name is used to have some presets like material=C18, machining type = Purlin etc..
    Type: a beam,a wall, an axe or a pannel....
    Material: attribute used to group parts on command list
    Group: used for example group = roof or group= walls
    Sub-group: used for exemple sub-group= Wall_A1, sub-group=Wall_B2
    Prod. number : the production number it could not be editable, and a tool should be written to find same parts and give it the same number
    Inv. number : same as Prod number, but it's the invoice number
    '''
    lst=["Name","Type","Material","Group","Sub-Group","Prod. Number","Inv. Number","Machining Type","User1","User2","User3","User4"]
    return lst

def getTypes():
    lst=["Beam","Pannel","Axe","Wall"]
    return lst

def getMaterials():
    lst=["C18","C24","Pin Cl4","GL24H","OSB3","Kerto S","Kerto Q","CTBH","CTBX"]
    return lst

def getMachining():
    lst=[]
    return lst

def insertAttr(obj=None):
    "Insert all attributes/properties in the object"
    pass

def filterByAttr(objList=None,filter=""):
    "filter all objects provided, with the filter"
    pass

class Ui_AttrEdit:
     def __init__(self,obj=None):
        self.obj=obj

        self.form= FreeCADGui.PySideUic.loadUi(attrUI)

        self.form.cb_Type.addItems(getTypes())
        self.form.cb_Material.addItems(getMaterials())
        self.form.cb_Machining.addItems(getMachining())



     def accept(self):
        Console.PrintMessage("##WFrame Attr## Accepted \r\n")
        FreeCADGui.Control.closeDialog()


