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


import FreeCAD
import Arch, ArchComponent
import xml.etree.ElementTree as AT
from math import *
import WFrameUtils

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


# XML resources, where attributes lists are stored
xmlpath = __dir__ + "/Resources/Attributes.xml"
xmltree = AT.parse(xmlpath)
xmlroot = xmltree.getroot()

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
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCADGui.ActiveDocument:
            return len(FreeCADGui.Selection.getSelection()) > 0
        else:
            return False
FreeCADGui.addCommand('WFEditAttributes', WFEditAttributes())


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
FreeCADGui.addCommand('WFSelectByAttributes', WFSelectByAttributes())


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


'''Strings used to determine Attributes'''
txt_name = "Name"
txt_type = "Type"
txt_wclass = "WoodClass"
txt_group = "Group"
txt_sgroup = "SubGroup"
txt_prodnum = "ProdNumber"
txt_invnum = "InvNumber"
txt_mach = "MachiningType"
txt_u1 = "User1"
txt_u2 = "User2"
txt_u3 = "User3"
txt_u4 = "User4"

def getAttrlist():
    """
        Get the attributes/properties list available
        Name: the attribute name is used to have some presets like material=C18, machining type = Purlin etc..
        Type: a beam,a wall, an axe or a panel....
        Material: attribute used to group parts on command list
        Group: ex: group = roof or group= walls
        Sub-group:  ex: sub-group= Wall_A1, sub-group=Wall_B2
        Prod. number : the production number shouldn't be editable, and a tool should be written to find same parts and give it the same number
        Inv. number : same as Prod number, but it's the invoice number
        """
    lst = []
    for child in xmlroot:
        if not child.tag in lst:
            lst.append(child.tag)
    lst.append("Prod_Number")
    lst.append("Inv_Number")
    return lst


def getNames():
    lst = []
    for child in xmlroot.findall(txt_name):
        lst.append(child.attrib['name'])
    return lst


def getTypes():
    lst = []
    for child in xmlroot.findall(txt_type):
        lst.append(child.attrib['name'])
    return lst


def getWoodClasses():
    lst = []
    for child in xmlroot.findall(txt_wclass):
        lst.append(child.attrib['name'])
    return lst


def getGroups():
    # have to search on IFC data probably better...
    # but i don't known if there's no limit to create new groups
    lst = []
    for child in xmlroot.findall(txt_group):
        lst.append(child.attrib['name'])
    return lst


def getSub_Groups():
    lst = []
    for child in xmlroot.findall(txt_sgroup):
        lst.append(child.attrib['name'])
    return lst


def getMachining_Types():
    lst = []
    for child in xmlroot.findall(txt_mach):
        lst.append(child.attrib['name'])
    return lst


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
        ##retreive selected objects
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
        self.form.addType.clicked.connect(self.addType)
        self.form.addWoodClass.clicked.connect(self.addWoodClass)
        self.form.addGroup.clicked.connect(self.addGroup)
        self.form.addSubGroup.clicked.connect(self.addSubGroup)
        self.form.addMachining.clicked.connect(self.addMachining)
        # ui setup done

        # now retreive properties of selected objects
        for obj in self.objList:
            # test if the object have WFrame attributes
            if not 'Name' in obj.PropertiesList:
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
                    obj.Name = self.form.cb_Name.currentText()
                elif i == txt_type and not self.form.cb_Type.currentText() == multiNames:
                    obj.Type = self.form.cb_Type.currentText()
                elif i == txt_wclass and not self.form.cb_WoodClass.currentText() == multiNames:
                    obj.WoodClass = self.form.cb_WoodClass.currentText()
                elif i == txt_group and not self.form.cb_Group.currentText() == multiNames:
                    obj.Group = self.form.cb_Group.currentText()
                elif i == txt_sgroup and not self.form.cb_Sub_Group.currentText() == multiNames:
                    obj.SubGroup = self.form.cb_Sub_Group.currentText()
                elif i == txt_mach and not self.form.cb_Machining.currentText() == multiNames:
                    obj.MachiningType = self.form.cb_Machining.currentText()
                ###continue with user 1 2 3 4

        FreeCADGui.Control.closeDialog()
        FreeCAD.ActiveDocument.recompute()



    def addName(self):
        value, ok = QtGui.QInputDialog.getText(None, "Section", "new "+txt_name, QtGui.QLineEdit.Normal, "")
        if ok :
            writexml(txt_name,value)
            self.form.cb_Name.clear()
            self.form.cb_Name.addItems(getNames())
            ind=self.form.cb_Name.count()-1
            self.form.cb_Name.setCurrentIndex(ind)

    def addType(self):
        value, ok = QtGui.QInputDialog.getText(None, "Section", "new " + txt_type, QtGui.QLineEdit.Normal, "")
        if ok:
            writexml(txt_type,value)
            self.form.cb_Type.clear()
            self.form.cb_Type.addItems(getNames())
            ind = self.form.cb_Type.count() - 1
            self.form.cb_Type.setCurrentIndex(ind)

    def addWoodClass(self):
        ###TODO
        print("Woodclass")

    def addGroup(self):
        ###TODO
        print("addgroup")

    def addSubGroup(self):
        ###TODO
        print("subgroup")

    def addMachining(self):
        ###TODO
        print("machining")


def writexml(tag,value):
    '''add a line in the xml file'''
    el = AT.Element(tag, attrib={'name': value})
    xmlroot.append(el)
    indent(xmlroot)
    AT.dump(xmlroot)
    xmltree.write(xmlpath, encoding="utf-8", xml_declaration=True)


def indent(elem, level=0):
    '''indent the xml file'''
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


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
        lst = []
        for obj in FreeCAD.ActiveDocument.Objects:

            # test if the object have WFrame attributes
            if 'Name' in obj.PropertiesList:
                n = self.form.cb_AttrList.currentText()

                if n == txt_name :
                    lst.append(obj.Name)
                elif n == txt_type:
                    lst.append(obj.Type)
                elif n == txt_wclass:
                    lst.append(obj.WoodClass)
                elif n == txt_group:
                    lst.append(obj.Group)
                elif n == txt_sgroup:
                    lst.append(obj.SubGroup)
                elif n == txt_mach:
                    lst.append(obj.MachiningType)

        # remove doubles
        lst =list(set(lst))
        self.clearingValues=True
        self.form.cb_Values.clear()
        print(lst,getAttrlist())
        self.form.cb_Values.addItems(lst)
        self.clearingValues=False

    def update(self):
        if not self.clearingValues:
            if not self.form.chk_Add.isChecked() :
                 FreeCADGui.Selection.clearSelection()

            for obj in FreeCAD.ActiveDocument.Objects:
                add=False

                if 'Name' in obj.PropertiesList:
                    attr = self.form.cb_AttrList.currentText()
                    val = self.form.cb_Values.currentText()


                    if attr == txt_name and obj.Name ==  val : add = True
                    elif attr == txt_type and obj.Type ==  val : add = True
                    elif attr == txt_group and obj.Group == val: add = True
                    elif attr == txt_sgroup and obj.SubGroup == val: add = True
                    elif attr == txt_mach and obj.MachiningType == val: add = True

                if add :
                    if obj.ViewObject.Visibility:
                        FreeCADGui.Selection.addSelection(obj)

            if self.form.chk_Hide.isChecked() :
                FreeCADGui.runCommand('Std_ToggleVisibility',0)

            FreeCAD.ActiveDocument.recompute()


    def accept(self):
        self.update()
        FreeCADGui.Control.closeDialog()



