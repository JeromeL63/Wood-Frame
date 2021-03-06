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

###TODO implement user1 2 3 4 in functions


import FreeCAD
import ArchComponent,Draft
import xml.etree.ElementTree as AT
from math import *
import WFUtils

from PySide import QtCore, QtGui

if FreeCAD.GuiUp:
    import FreeCADGui
else:
    def translate(ctxt, txt):
        return txt
# waiting for WFrame_rc and eventual FreeCAD integration
import os

__dir__ = os.path.dirname(__file__)
__title__ = "FreeCAD WoodFrame Attributes"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"


attrEditUI = __dir__ + "/Resources/Ui/AttrEdit.ui"
attrSelectUI = __dir__ + "/Resources/Ui/AttrSelect.ui"


# if some attributes are different show ***
multiNames = "***"


class WFEditAttributes():
    """WFrameAttributes"""

    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/WFEditAttr.svg',
                'Accel': "W,E",
                'MenuText': "Edit attributes",
                'ToolTip': "Edit attributes"}

    def Activated(self):
        panel = Ui_AttrEdit()
        FreeCADGui.Control.showDialog(panel)
        return

    def IsActive(self):
        bool = False
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCADGui.ActiveDocument:
            bool = True
            for i in FreeCADGui.Selection.getSelection():
                if not hasattr(i,"Tag"):
                    return False
        return bool

FreeCADGui.addCommand('WF_EditAttributes', WFEditAttributes())


class WFSelectByAttributes():
    """WFrameAttributes"""

    def GetResources(self):
        return {'Pixmap': __dir__ + '/Resources/icons/WFSelectAttr.svg',
                'Accel': "SHIFT+A",
                'MenuText': "Select by attributes",
                'ToolTip': "Select by attributes"}

    def Activated(self):
        panel = Ui_AttrSelect()
        FreeCADGui.Control.showDialog(panel)
        return

    def IsActive(self):
       return True
FreeCADGui.addCommand('WF_SelectByAttributes', WFSelectByAttributes())



'''Strings used to determine Attributes'''
txt_name = "WFName"
txt_type = "Type"
txt_wclass = "WoodClass"
txt_group = "WFGroup"
txt_sgroup = "SubGroup"
txt_prodnum = "ProdNumber"
txt_invnum = "InvNumber"
txt_mach = "MachiningType"
txt_u1 = "User1"
txt_u2 = "User2"
txt_u3 = "User3"
txt_u4 = "User4"
lstattr = [txt_name,txt_type,txt_wclass,txt_group,txt_sgroup,txt_invnum,txt_prodnum,txt_mach,txt_u1,txt_u2,txt_u3,txt_u4]

class Attributes:
    """Create a python object that contains all attributes
    All are saved in the current project with this way
    """
    def __init__(self,obj):
        obj.Proxy = self

        obj.addProperty("App::PropertyStringList",txt_name,"WFrame")
        obj.WFName=["Panne","Chevron","Poteau"]
        obj.setEditorMode(txt_name,2)

        obj.addProperty("App::PropertyStringList", txt_type, "WFrame")
        obj.Type = ["Bar", "Panel", "Axe", "Auxiliary"]
        obj.setEditorMode(txt_type, 2)

        obj.addProperty("App::PropertyStringList",txt_wclass,"WFrame")
        obj.WoodClass=["C18","C24","GL24H","Kerto S","Kerto Q","OSB3","CTBH","CTBX","BA13","Shingle","Tuiles terre cuite"]
        obj.setEditorMode(txt_wclass, 2)

        obj.addProperty("App::PropertyStringList",txt_group,"WFrame")
        obj.WFGroup=["Charpente","Couverture","Ossature","Plancher RDC","Plancher R+1"]
        obj.setEditorMode(txt_group, 2)

        obj.addProperty("App::PropertyStringList",txt_sgroup,"WFrame")
        obj.SubGroup=["Mur_A","Mur_B","Mur_C"]
        obj.setEditorMode(txt_sgroup, 2)


        obj.addProperty("App::PropertyStringList",txt_mach,"WFrame")
        obj.setEditorMode(txt_mach, 2)

        obj.addProperty("App::PropertyString", txt_invnum, "WFrame")
        obj.setEditorMode(txt_invnum, 2)

        obj.addProperty("App::PropertyString", txt_prodnum, "WFrame")
        obj.setEditorMode(txt_prodnum, 2)


        obj.addProperty("App::PropertyString","Info", "WFrame")
        obj.Info ="Don't remove this object or you'll loose all your attributes !!!"

        obj.setEditorMode("Label", 2)

    def execute(self,obj):
        pass


def check():
    # check if there's WFrame Group
    if hasattr(FreeCAD.ActiveDocument, "WFrame"):
        wfobj = FreeCAD.ActiveDocument.WFrame

    else:
        #create group
        wfobj= FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","WFrame")

        ###TODO : Create Materials
        ###TODO : Create Layers
        ###WARNING : Layers in draft are called "Layer" and not by name !!!!
        ### have to check with Layer.Label
        # example
        r = (1 / 255) * 80
        g = (1 / 255) * 255
        b = (1 / 255) * 255
        Draft.makeLayer("Principal",linecolor=(r,g,b))

        r = (1 / 255) * 180
        g = (1 / 255) * 180
        b = (1 / 255) * 180
        Draft.makeLayer("Secondaire", linecolor=(r, g, b))
        r = (1 / 255) * 80
        g = (1 / 255) * 255
        b = (1 / 255) * 50
        Draft.makeLayer("Complémentaire", linecolor=(r, g, b))
        FreeCAD.ActiveDocument.recompute()
        #FreeCAD.ActiveDocument.Principal.ViewObject.OverrideChildren = False
    #now check if there's attributes feature
    if not hasattr(FreeCAD.ActiveDocument, "Attributes"):
        createAttributesList()
        FreeCAD.ActiveDocument.WFrame.addObject(FreeCAD.ActiveDocument.Attributes)



def createAttributesList():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Attributes")
    d = Attributes(obj)
    FreeCAD.ActiveDocument.recompute()


def getAttrlist():
    # for more convenience
    return lstattr

def getNames():
    check()
    return FreeCAD.ActiveDocument.getObject("Attributes").getPropertyByName(txt_name)


def getTypes():
    check()
    return FreeCAD.ActiveDocument.getObject("Attributes").getPropertyByName(txt_type)

def getWoodClasses():
    check()
    return FreeCAD.ActiveDocument.getObject("Attributes").getPropertyByName(txt_wclass)

def getGroups():
    check()
    return FreeCAD.ActiveDocument.getObject("Attributes").getPropertyByName(txt_group)

def getSub_Groups():
    check()
    return FreeCAD.ActiveDocument.getObject("Attributes").getPropertyByName(txt_sgroup)

def getMachining_Types():
    check()
    return FreeCAD.ActiveDocument.getObject("Attributes").getPropertyByName(txt_mach)


def insertAttr(obj: ArchComponent.Component):
    '''
    Insert all attributes/properties in the object
    '''
    for i in getAttrlist():
        obj.addProperty("App::PropertyString", i, "WFrame", "", 1)


def filterByAttr(objList=None, filter=""):
    "filter all objects provided, with the filter"
    pass


class Ui_AttrEdit:
    def __init__(self):
        ##retrieve selected objects
        self.objList = FreeCADGui.Selection.getSelection()
        ### onSelectionChange could be fun

        self.form = FreeCADGui.PySideUic.loadUi(attrEditUI)
        self.form.cb_Name.addItems(getNames())
        self.form.cb_Name.setCurrentIndex(-1)
        self.form.cb_Type.addItems(getTypes())
        self.form.cb_Type.setCurrentIndex(-1)
        self.form.cb_WoodClass.addItems(getWoodClasses())
        self.form.cb_WoodClass.setCurrentIndex(-1)
        self.form.cb_Group.addItems(getGroups())
        self.form.cb_Group.setCurrentIndex(-1)
        self.form.cb_Sub_Group.addItems(getSub_Groups())
        self.form.cb_Sub_Group.setCurrentIndex(-1)
        self.form.cb_Machining.addItems(getMachining_Types())
        self.form.cb_Machining.setCurrentIndex(-1)

        self.form.addName.clicked.connect(self.addName)
        # no more propositions
        self.form.addWoodClass.clicked.connect(self.addWoodClass)
        self.form.addGroup.clicked.connect(self.addGroup)
        self.form.addSubGroup.clicked.connect(self.addSubGroup)
        self.form.addMachining.clicked.connect(self.addMachining)
        # ui setup done

        # now retrieve properties of selected objects
        for obj in self.objList:
            # test if the object have WFrame attributes
            if not hasattr(obj.PropertiesList,"WFName"):
                # if not insert them
                insertAttr(obj)

            for i in getAttrlist():

                if i == txt_name:
                    s = self.form.cb_Name.currentText()
                    if s == obj.getPropertyByName(i) or self.form.cb_Name.currentIndex() == -1:
                        ind = self.form.cb_Name.findText(obj.getPropertyByName(i))
                        self.form.cb_Name.setCurrentIndex(ind)
                    else:
                        if not self.form.cb_Name.itemText(0) == multiNames:
                            self.form.cb_Name.insertItem(0, multiNames)
                        self.form.cb_Name.setCurrentIndex(0)

                if i == txt_type:
                    s = self.form.cb_Type.currentText()
                    if s == obj.getPropertyByName(i) or self.form.cb_Type.currentIndex() == -1:
                        ind = self.form.cb_Type.findText(obj.getPropertyByName(i))
                        self.form.cb_Type.setCurrentIndex(ind)
                    else:
                        if not self.form.cb_Type.itemText(0) == multiNames:
                            self.form.cb_Type.insertItem(0, multiNames)
                        self.form.cb_Type.setCurrentIndex(0)

                if i == txt_wclass:
                    s = self.form.cb_WoodClass.currentText()
                    if s == obj.getPropertyByName(i) or self.form.cb_WoodClass.currentIndex() == -1:
                        ind = self.form.cb_WoodClass.findText(obj.getPropertyByName(i))
                        self.form.cb_WoodClass.setCurrentIndex(ind)
                    else:
                        if not self.form.cb_WoodClass.itemText(0) == multiNames:
                            self.form.cb_WoodClass.insertItem(0, multiNames)
                        self.form.cb_WoodClass.setCurrentIndex(0)

                if i == txt_group:
                    s = self.form.cb_Group.currentText()
                    if s == obj.getPropertyByName(i) or self.form.cb_Group.currentIndex() == -1:
                        ind = self.form.cb_Group.findText(obj.getPropertyByName(i))
                        self.form.cb_Group.setCurrentIndex(ind)
                    else:
                        if not self.form.cb_Group.itemText(0) == multiNames:
                            self.form.cb_Group.insertItem(0, multiNames)
                        self.form.cb_Group.setCurrentIndex(0)

                if i == txt_sgroup:
                    s = self.form.cb_Sub_Group.currentText()
                    if s == obj.getPropertyByName(i) or self.form.cb_Sub_Group.currentIndex() == -1:
                        ind = self.form.cb_Sub_Group.findText(obj.getPropertyByName(i))
                        self.form.cb_Sub_Group.setCurrentIndex(ind)
                    else:
                        if not self.form.cb_Sub_Group.itemText(0) == multiNames:
                            self.form.cb_Sub_Group.insertItem(0, multiNames)
                        self.form.cb_Sub_Group.setCurrentIndex(0)

                if i == txt_mach:
                    s = self.form.cb_Machining.currentText()
                    if s == obj.getPropertyByName(i) or self.form.cb_Machining.currentIndex() == -1:
                        ind = self.form.cb_Machining.findText(obj.getPropertyByName(i))
                        self.form.cb_Machining.setCurrentIndex(ind)
                    else:
                        if not self.form.cb_Machining.itemText(0) == multiNames:
                            self.form.cb_Machining.insertItem(0, multiNames)
                        self.form.cb_Machining.setCurrentIndex(0)

                ###continue with user 1 2 3 4

    def accept(self):
        '''on accepted dialog'''
        for obj in self.objList:
            for i in getAttrlist():
                ###Note: I think there's an easyest way to do that in python like obj.list={}
                # if property string equal *** do nothing
                if i == txt_name and not self.form.cb_Name.currentText() == multiNames:
                    obj.WFName = self.form.cb_Name.currentText()
                elif i == txt_type and not self.form.cb_Type.currentText() == multiNames:
                    obj.Type = self.form.cb_Type.currentText()
                elif i == txt_wclass and not self.form.cb_WoodClass.currentText() == multiNames:
                    obj.WoodClass = self.form.cb_WoodClass.currentText()
                elif i == txt_group and not self.form.cb_Group.currentText() == multiNames:
                    obj.WFGroup = self.form.cb_Group.currentText()
                elif i == txt_sgroup and not self.form.cb_Sub_Group.currentText() == multiNames:
                    obj.SubGroup = self.form.cb_Sub_Group.currentText()
                elif i == txt_mach and not self.form.cb_Machining.currentText() == multiNames:
                    obj.MachiningType = self.form.cb_Machining.currentText()
                ###continue with user 1 2 3 4

        FreeCADGui.Control.closeDialog()
        FreeCAD.ActiveDocument.recompute()



    def addName(self):
        value, ok = QtGui.QInputDialog.getText(None, "Add", "new "+txt_name, QtGui.QLineEdit.Normal, "")
        if ok :
            obj = FreeCAD.ActiveDocument.getObject("Attributes")
            list = obj.getPropertyByName(txt_name)
            list.append(value)
            obj.WFName=list
            self.form.cb_Name.clear()
            self.form.cb_Name.addItems(getNames())
            ind=self.form.cb_Name.count()-1
            self.form.cb_Name.setCurrentIndex(ind)

    def addWoodClass(self):
        value, ok = QtGui.QInputDialog.getText(None, "Add", "new " + txt_wclass, QtGui.QLineEdit.Normal, "")
        if ok:
            obj = FreeCAD.ActiveDocument.getObject("Attributes")
            list = obj.getPropertyByName(txt_wclass)
            list.append(value)
            obj.WoodClass = list
            self.form.cb_WoodClass.clear()
            self.form.cb_WoodClass.addItems(getWoodClasses())
            ind = self.form.cb_WoodClass.count() - 1
            self.form.cb_WoodClass.setCurrentIndex(ind)

    def addGroup(self):
        value, ok = QtGui.QInputDialog.getText(None, "Add", "new " + txt_group, QtGui.QLineEdit.Normal, "")
        if ok:
            obj = FreeCAD.ActiveDocument.getObject("Attributes")
            list = obj.getPropertyByName(txt_group)
            list.append(value)
            obj.WFGroup = list
            self.form.cb_Group.clear()
            self.form.cb_Group.addItems(getGroups())
            ind = self.form.cb_Group.count() - 1
            self.form.cb_Group.setCurrentIndex(ind)

    def addSubGroup(self):
        value, ok = QtGui.QInputDialog.getText(None, "Add", "new " + txt_sgroup, QtGui.QLineEdit.Normal, "")
        if ok:
            obj = FreeCAD.ActiveDocument.getObject("Attributes")
            list = obj.getPropertyByName(txt_sgroup)
            list.append(value)
            obj.SubGroup = list
            self.form.cb_Sub_Group.clear()
            self.form.cb_Sub_Group.addItems(getSub_Groups())
            ind = self.form.cb_Sub_Group.count() - 1
            self.form.cb_Sub_Group.setCurrentIndex(ind)

    def addMachining(self):
        value, ok = QtGui.QInputDialog.getText(None, "Add", "new " + txt_mach, QtGui.QLineEdit.Normal, "")
        if ok:
            obj = FreeCAD.ActiveDocument.getObject("Attributes")
            list = obj.getPropertyByName(txt_mach)
            list.append(value)
            obj.MachiningType = list
            self.form.cb_Machining.clear()
            self.form.cb_Machining.addItems(getMachining_Types())
            ind = self.form.cb_Machining.count() - 1
            self.form.cb_Machining.setCurrentIndex(ind)

class Ui_AttrSelect:
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(attrSelectUI)
        self.form.cb_AttrList.addItems(getAttrlist())
        self.form.cb_AttrList.setCurrentIndex(-1)
        # connect combobox events
        self.form.cb_AttrList.currentIndexChanged.connect(self.fill)
        self.form.cb_Values.currentIndexChanged.connect(self.update)
        self.form.cb_AttrList.setCurrentIndex(0)

        self.initialSelection=FreeCADGui.Selection
        self.clearingValues=False

    def fill(self):
        self.lst = []
        for obj in FreeCAD.ActiveDocument.Objects:

            # test if the object have WFrame attributes and is not the root Attributes object
            if hasattr(obj,"WFName") and not obj.Label == "Attributes":

                n = self.form.cb_AttrList.currentText()

                if n == txt_name :
                    self.lst.append(obj.WFName)
                elif n == txt_type:
                    self.lst.append(obj.Type)
                elif n == txt_wclass:
                    self.lst.append(obj.WoodClass)
                elif n == txt_group:
                    self.lst.append(obj.WFGroup)
                elif n == txt_sgroup:
                    self.lst.append(obj.SubGroup)
                elif n == txt_mach:
                    self.lst.append(obj.MachiningType)

        # remove doubles
        print(self.lst)
        self.lst =list(set(self.lst))
        self.clearingValues=True
        self.form.cb_Values.clear()
        #print(lst,getAttrlist())
        self.form.cb_Values.addItems(self.lst)
        self.clearingValues=False

    def update(self):
        if not self.clearingValues:
            if not self.form.chk_Add.isChecked() :
                 FreeCADGui.Selection.clearSelection()

            for obj in FreeCAD.ActiveDocument.Objects:
                add=False

                if hasattr(obj,"WFName") :
                    attr = self.form.cb_AttrList.currentText()
                    val = self.form.cb_Values.currentText()


                    if attr == txt_name and obj.WFName ==  val : add = True
                    elif attr == txt_wclass and obj.WoodClass == val : add = True
                    elif attr == txt_type and obj.Type ==  val : add = True
                    elif attr == txt_group and obj.WFGroup == val: add = True
                    elif attr == txt_sgroup and obj.SubGroup == val: add = True
                    elif attr == txt_mach and obj.MachiningType == val: add = True
                    #elif attr == txt_u1

                if add :
                    if obj.ViewObject.Visibility:
                        FreeCADGui.Selection.addSelection(obj)

            if self.form.chk_Hide.isChecked() :
                FreeCADGui.runCommand('Std_ToggleVisibility',0)

            FreeCAD.ActiveDocument.recompute()


    def accept(self):
        self.update()
        FreeCADGui.Control.closeDialog()



class presets:
    def __init__(self):
        pass
    def set(self,obj):
        # set default values with the object.Name
        # TODO
        pass