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
import Arch,ArchComponent
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
multiNames="***"

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


def getAttrlist():
    """
    Get the attributes/properties list available
    Name: the attribute name is used to have some presets like material=C18, machining type = Purlin etc..
    Type: a beam,a wall, an axe or a pannel....
    Material: attribute used to group parts on command list
    Group: used for example group = roof or group= walls
    Sub-group: used for exemple sub-group= Wall_A1, sub-group=Wall_B2
    Prod. number : the production number it could not be editable, and a tool should be written to find same parts and give it the same number
    Inv. number : same as Prod number, but it's the invoice number
    """
    lst=["Name","Type","Material","Group","Sub_Group","Prod_Number","Inv_Number","Machining_Type","User1","User2","User3","User4"]
    return lst

def getTypes():
    lst=["Purlin","Pile","Truss","Pannel","Wall","Axe"]
    return lst

def getMaterials():
    lst=["C18","C24","Pin Cl4","GL24H","OSB3","Kerto S","Kerto Q","CTBH","CTBX"]
    return lst

def getMachining():
    lst=[]
    return lst

def insertAttr(obj :ArchComponent.Component):
    for i in getAttrlist():
        #ofr tests properties aren't hidden's
        #obj.addProperty("App::PropertyString",i,"WFrame","",4)
        obj.addProperty("App::PropertyString", i, "WFrame", "", 0)


    "Insert all attributes/properties in the object"



def filterByAttr(objList=None,filter=""):
    "filter all objects provided, with the filter"
    pass

class Ui_AttrEdit:
     def __init__(self):
        ##retreive selected objects
        self.objList=FreeCADGui.Selection.getSelection()
        ### onSelectionChange could be fun

        self.form= FreeCADGui.PySideUic.loadUi(attrUI)
        self.form.cb_Type.addItems(getTypes())
        self.form.cb_Material.addItems(getMaterials())
        self.form.cb_Machining.addItems(getMachining())
        #ui setup done


        #now retreive properties of selected objects
        Console.PrintMessage("##WFrame Attr## obj name" + str(self.objList) + " \r\n")
        for obj in self.objList:
            list={}
            for i in getAttrlist():
                ###Where is switch in python ??? :'(
                ### please re writte this function in a descent python code
                list[i] = obj.getPropertyByName(i)

                if i == getAttrlist()[0]:
                    #if text equal this property or empty
                    s=self.form.led_Name.text()
                    Console.PrintMessage("##WFrame Attr## " + str(s) + " \r\n")
                    if  (s == obj.getPropertyByName(i) ) or not(s) :
                        self.form.led_Name.setText(obj.getPropertyByName(i))
                    else:
                        self.form.led_Name.setText(multiNames)

            Console.PrintMessage("##WFrame Attr## obj name list "+str(list)+" \r\n")
        #if some properties are different show ***



     def accept(self):
         '''on accepted dialog'''
         for obj in self.objList:

            for i in getAttrlist():
                ###Note: I think there's an easyest way to do that in python like obj.list={}
                #if property string equal *** do nothing
                if i == getAttrlist()[0] and not self.form.led_Name.text()==multiNames:
                    obj.Name=self.form.led_Name.text()
         FreeCADGui.Control.closeDialog()


