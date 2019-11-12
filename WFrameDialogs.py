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


from PySide import QtGui,QtCore
import FreeCADGui
import WFrameAttributes

'''WFrameDialogs is a collection of Widgets used in WFrame'''


class CoordinatesWidget(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        gridCoords = QtGui.QGridLayout(self)
        loader = FreeCADGui.UiLoader()

        lbl01 = QtGui.QLabel("Global coords")
        lbl02 = QtGui.QLabel("Local Vector")

        lbl1 = QtGui.QLabel("Origin X")
        self.oX = loader.createWidget("Gui::InputField")
        lbl2 = QtGui.QLabel("Origin Y")
        self.oY = loader.createWidget("Gui::InputField")
        lbl3 = QtGui.QLabel("Origin Z")
        self.oZ = loader.createWidget("Gui::InputField")
        lbl4 = QtGui.QLabel("End X")
        self.eX = loader.createWidget("Gui::InputField")
        lbl5 = QtGui.QLabel("End Y")
        self.eY = loader.createWidget("Gui::InputField")
        self.retry=QtGui.QPushButton("redo")

        gridCoords.addWidget(lbl01, 0, 0, 1, 1)
        gridCoords.addWidget(lbl02, 0, 2, 1, 1)
        gridCoords.addWidget(lbl1, 1, 0, 1, 1)
        gridCoords.addWidget(self.oX, 1, 1, 1, 1)
        gridCoords.addWidget(lbl2, 2, 0, 1, 1)
        gridCoords.addWidget(self.oY, 2, 1, 1, 1)
        gridCoords.addWidget(lbl3, 3, 0, 1, 1)
        gridCoords.addWidget(self.oZ, 3, 1, 1, 1)
        gridCoords.addWidget(lbl4, 1, 2, 1, 1)
        gridCoords.addWidget(self.eX, 1, 3, 1, 1)
        gridCoords.addWidget(lbl5, 2, 2, 1, 1)
        gridCoords.addWidget(self.eY, 2, 3, 1, 1)
        gridCoords.addWidget(self.retry,1,4,1,1)




class DimensionsWidget(QtGui.QWidget):
    '''
    This is the dimension widget
    used to get height width and length
    of a beam or a panel
    '''

    def __init__(self,panelMode=False):
        QtGui.QWidget.__init__(self)
        gridDim=QtGui.QGridLayout(self)
        loader = FreeCADGui.UiLoader()
        order=2
        if not panelMode :
            b="Width"
            h="Height"
            l="Length"

        else:
            order=4
            b="Width"

            h="Thickness"
            l="Length"

        lbl1=QtGui.QLabel(b)
        self.width=loader.createWidget("Gui::InputField")
        gridDim.addWidget(lbl1, 0, 0, 1, 1)
        gridDim.addWidget(self.width, 0, 1, 1, 1)

        if panelMode :
            lblmax=QtGui.QLabel("MaxWidth")
            self.maxWidth=loader.createWidget("Gui::InputField")
            gridDim.addWidget(lblmax, 1, 0, 1, 1)
            gridDim.addWidget(self.maxWidth, 1, 1, 1, 1)

        #height or thickness
        lbl2 = QtGui.QLabel(h)
        self.height = loader.createWidget("Gui::InputField")
        gridDim.addWidget(lbl2, order, 0, 1, 1)
        gridDim.addWidget(self.height, order, 1, 1, 1)

        self.lbl_length = QtGui.QLabel(l)
        self.length = loader.createWidget("Gui::InputField")
        gridDim.addWidget(self.lbl_length, 3, 0, 1, 1)
        gridDim.addWidget(self.length, 3, 1, 1, 1)



### DESCRIPTION CONTAINER ###
class DescriptionWidget(QtGui.QWidget):
    '''
    This is the description widget
    used to select attributes
    and orientations
    '''

    def __init__(self,orientations=["face","top"]):
        QtGui.QWidget.__init__(self)
        gridDesc=QtGui.QGridLayout(self)

        lbl_Orientation=QtGui.QLabel("Orientation")
        self.cb_Orientation=QtGui.QComboBox()
        self.cb_Orientation.addItems(orientations)

        lbl_Name = QtGui.QLabel("Name")
        self.cb_Name = QtGui.QComboBox()
        self.cb_Name.addItems(WFrameAttributes.getNames())

        gridDesc.addWidget(lbl_Orientation,0,0,1,1)
        gridDesc.addWidget(self.cb_Orientation,0,1,1,1)
        gridDesc.addWidget(lbl_Name, 1, 0, 1, 1)
        gridDesc.addWidget(self.cb_Name, 1, 1, 1, 1)


class InsertionPointWidget(QtGui.QGroupBox):
    '''
    This is the insertion point widget used to
    determine an offset on Beam/Panel
    '''
    def __init__(self):
        QtGui.QGroupBox.__init__(self,"Insertion point")
        gridDesc = QtGui.QGridLayout(self)

        self.rb_1 = QtGui.QRadioButton('1')
        self.rb_2 = QtGui.QRadioButton('2')
        self.rb_3 = QtGui.QRadioButton('3')
        self.rb_4 = QtGui.QRadioButton('4')
        self.rb_5 = QtGui.QRadioButton('5 (origin)')
        self.rb_6 = QtGui.QRadioButton('6')
        self.rb_7 = QtGui.QRadioButton('7')
        self.rb_8 = QtGui.QRadioButton('8')
        self.rb_9 = QtGui.QRadioButton('9')

        gridDesc.addWidget(self.rb_1, 2, 0, 1, 1)
        gridDesc.addWidget(self.rb_2, 2, 1, 1, 1)
        gridDesc.addWidget(self.rb_3, 2, 3, 1, 1)
        gridDesc.addWidget(self.rb_4, 1, 0, 1, 1)
        gridDesc.addWidget(self.rb_5, 1, 1, 1, 1)
        gridDesc.addWidget(self.rb_6, 1, 3, 1, 1)
        gridDesc.addWidget(self.rb_7, 0, 0, 1, 1)
        gridDesc.addWidget(self.rb_8, 0, 1, 1, 1)
        gridDesc.addWidget(self.rb_9, 0, 3, 1, 1)

        self.rb_5.setChecked(True)

