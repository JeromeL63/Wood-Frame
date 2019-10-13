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
import WFrameUtils

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

#if some properties are different show ***
multiNames="***"

class WFrameAttributes():
    """WFrameAttributes"""

    def GetResources(self):
        return {'Pixmap'  :  __dir__ + '/Resources/icons/WFrameLib.svg',
                'Accel' : "W,A",
                'MenuText': "WFrameAttributes",
                'ToolTip' : "Edit attributes"}

    def Activated(self):
        utils= WFrameUtils
        print(utils.filename())
        panel = Ui_AttrEdit()
        FreeCADGui.Control.showDialog(panel)
        #FreeCAD.getDocument()
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


txt_name="Name"
txt_type="Type"
txt_mat="Material"
txt_group="Group"
txt_sgroup="Sub_Group"
txt_prodnum="Prod_Number"
txt_invnum="Inv_Number"
txt_mach="Machining_Type"
txt_u1="User1"
txt_u2="User2"
txt_u3="User3"
txt_u4="User4"

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
    lst=[txt_name,txt_type,txt_mat,txt_group,txt_sgroup,txt_prodnum,txt_invnum,txt_mach,txt_u1,txt_u2,txt_u3,txt_u4]
    return lst

def getTypes():
    lst=["none","Purlin","Pile","Truss","Pannel","Wall","Axe"]
    return lst

def getMaterials():
    lst=["C18","C24","Pin Cl4","GL24H","OSB3","Kerto S","Kerto Q","CTBH","CTBX","BA13","Shingle","Tuile terre cuite"]
    return lst
def getGroups():
    # have to search on IFC data probably better...
    # but i don't known if there's no limit to create new groups
    lst=["none","Charpente","Couverture","Ossature","Plancher RDC","Plancher R+1"]#etc...
    return lst
def getSub_Groups():
    lst=["none","Mur_A","Mur_B","Mur_C"]#for example
    return lst
def getMachining_Types():
    lst=["Marqué","Raboté"]# I really don't know what to put there, maybe @rockn should be better
    return lst


def insertAttr(obj :ArchComponent.Component):
    for i in getAttrlist():

        #ofr tests properties aren't hidden's
        #obj.addProperty("App::PropertyString",i,"WFrame","",4)
        if i==txt_name or i==txt_u1 or i==txt_u2 or i==txt_u3 or i==txt_u4:
            obj.addProperty("App::PropertyString", i, "WFrame", "", 0)

        elif i ==txt_type:
            obj.addProperty("App::PropertyEnumeration", i, "WFrame","", 0)
            obj.Type = getTypes()

        elif i == txt_mat:
            #Material already exist in "Component" section
            pass

        elif i == txt_group:
            obj.addProperty("App::PropertyEnumeration", i, "WFrame", "", 0)
            obj.Group = getGroups()

        elif i == txt_sgroup:
            obj.addProperty("App::PropertyEnumeration", i, "WFrame", "", 0)
            obj.Sub_Group = getSub_Groups()

        elif i == txt_mach:
            obj.addProperty("App::PropertyEnumeration", i, "WFrame", "", 0)
            obj.Machining_Type = getMachining_Types()

        elif i==txt_prodnum or i==txt_invnum:
            obj.addProperty("App::PropertyString", i, "WFrame", "", 4)







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
        self.form.cb_Group.addItems(getGroups())
        self.form.cb_Sub_Group.addItems(getSub_Groups())
        self.form.cb_Machining.addItems(getMachining_Types())
        #ui setup done


        #now retreive properties of selected objects
        for obj in self.objList:
            list={}
            for i in getAttrlist():
                ###Where is switch in python ??? :'(
                ### please re writte this function in a descent python code
                list[i] = obj.getPropertyByName(i)


                if i == txt_name:
                    s=self.form.led_Name.text()
                    if  (s == obj.getPropertyByName(i) ) or not(s) :
                        self.form.led_Name.setText(obj.getPropertyByName(i))
                    else:
                        self.form.led_Name.setText(multiNames)

                elif i == txt_u1:
                    s=self.form.led_User1.text()
                    if  (s == obj.getPropertyByName(i) ) or not(s) :
                        self.form.led_User1.setText(obj.getPropertyByName(i))
                    else:
                        self.form.led_User1.setText(multiNames)

                elif i == txt_u2:
                    s=self.form.led_User2.text()
                    if  (s == obj.getPropertyByName(i) ) or not(s) :
                        self.form.led_User2.setText(obj.getPropertyByName(i))
                    else:
                        self.form.led_User2.setText(multiNames)

                elif i == txt_u3:
                    s=self.form.led_User3.text()
                    if  (s == obj.getPropertyByName(i) ) or not(s) :
                        self.form.led_User3.setText(obj.getPropertyByName(i))
                    else:
                        self.form.led_User3.setText(multiNames)

                elif i == txt_u4:
                    s=self.form.led_User4.text()
                    if  (s == obj.getPropertyByName(i) ) or not(s) :
                        self.form.led_User4.setText(obj.getPropertyByName(i))
                    else:
                        self.form.led_User4.setText(multiNames)

                elif i == txt_type:
                    s=self.form.cb_Type.currentText()

                    if  s == obj.getPropertyByName(i)  or s == "none" :
                        Console.PrintMessage(txt_type + "|" + self.form.cb_Type.currentText())
                        self.form.cb_Type.setCurrentIndex(getTypes().index(obj.getPropertyByName(i)))
                    else:
                        self.form.cb_Type.insertItem(0,multiNames)
                        self.form.cb_Type.setCurrentIndex(0)

                elif i == txt_mat:
                    s=self.form.cb_Type.currentText()
                    if  (s == obj.getPropertyByName(i) ) or s == "none" :
                        self.form.cb_Material.setCurrentIndex(getMaterials().index(obj.getPropertyByName(i)))
                    else:
                        self.form.cb_Material.insertItem(0, multiNames)
                        self.form.cb_Material.setCurrentIndex(0)

                elif i == txt_group:
                    s = self.form.cb_Group.currentText()
                    if (s == obj.getPropertyByName(i)) or s == "none" :
                        self.form.cb_Group.setCurrentIndex(getGroups().index(obj.getPropertyByName(i)))
                    else:
                        self.form.cb_Group.insertItem(0, multiNames)
                        self.form.cb_Group.setCurrentIndex(0)

                elif i == txt_sgroup:
                    s = self.form.cb_Sub_Group.currentText()
                    if (s == obj.getPropertyByName(i)) or s == "none" :
                        self.form.cb_Sub_Group.setCurrentIndex(getSub_Groups().index(obj.getPropertyByName(i)))
                    else:
                        self.form.cb_Sub_Group.insertItem(0, multiNames)
                        self.form.cb_Sub_Group.setCurrentIndex(0)

                elif i == txt_mach:
                    s = self.form.cb_Machining.currentText()
                    if (s == obj.getPropertyByName(i)) or s == "none" :
                        self.form.cb_Machining.setCurrentIndex(getMachining_Types().index(obj.getPropertyByName(i)))
                    else:
                        self.form.cb_Machining.insertItem(0, multiNames)
                        self.form.cb_Machining.setCurrentIndex(0)


     def accept(self):
         '''on accepted dialog'''
         for obj in self.objList:

            for i in getAttrlist():
                ###Note: I think there's an easyest way to do that in python like obj.list={}
                #if property string equal *** do nothing
                if i == txt_name and not self.form.led_Name.text()==multiNames:
                    obj.Name=self.form.led_Name.text()

                elif i == txt_u1 and not self.form.led_User1.text() == multiNames:
                    obj.User1 = self.form.led_User1.text()
                elif i == txt_u2 and not self.form.led_User2.text() == multiNames:
                    obj.User2 = self.form.led_User2.text()
                elif i == txt_u3 and not self.form.led_User3.text() == multiNames:
                    obj.User3 = self.form.led_User3.text()
                elif i == txt_u4 and not self.form.led_User4.text() == multiNames:
                    obj.User4 = self.form.led_User4.text()

                elif i == txt_type and not self.form.cb_Type.currentText() == multiNames:
                    obj.Type = self.form.cb_Type.currentText()

                elif i == txt_mat and not self.form.cb_Material.currentText() == multiNames:
                    #retreive Material from Component
                    obj.Material = self.form.cb_Material.currentText()

                elif i == txt_group and not self.form.cb_Group.currentText() == multiNames:
                    obj.Group = self.form.cb_Group.currentText()

                elif i == txt_sgroup and not self.form.cb_Sub_Group.currentText() == multiNames:
                    obj.Sub_Group = self.form.cb_Sub_Group.currentText()

                elif i == txt_mach and not self.form.cb_Machining.currentText() == multiNames:
                    obj.Machining_Type = self.form.cb_Machining.currentText()

         FreeCADGui.Control.closeDialog()
         FreeCAD.ActiveDocument.recompute()


