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


import FreeCAD, Arch, Draft,ArchComponent, DraftVecUtils,ArchCommands, ArchStructure,math,FreeCADGui
from FreeCAD import Base, Console, Vector
from math import *
import DraftTrackers


if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
    from DraftTools import translate
else:
    def translate(ctxt,txt):
        return txt
# waiting for WFrame_rc and eventual FreeCAD integration
import os
__dir__ = os.path.dirname(__file__)

__title__="FreeCAD WoodWork Beam"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"




'''
disabling numpad shortcuts
to use for positionning and quick launch
'''
preset = [
    ("Std_ViewAxo"   , "CTRL+0"),
    ("Std_ViewFront" , "CTRL+1"),
    ("Std_ViewTop"   , "CTRL+2"),
    ("Std_ViewRight" , "CTRL+3"),
    ("Std_ViewRear"  , "CTRL+4"),
    ("Std_ViewBottom", "CTRL+5"),
    ("Std_ViewLeft"  , "CTRL+6"),
]
for (cmd, shortcut) in preset:
    FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Shortcut").SetString(cmd, shortcut)



from PySide import QtGui



class WFrameBeam():
    """WFrameBeam"""

    def GetResources(self):
        return {'Pixmap'  :  __dir__ + '/icons/WFrameBeam.svg',
                'Accel' : "W,B",
                'MenuText': "WFrameBeam",
                'ToolTip' : "Create an advanced beam with better positionning method"}

    def Activated(self):
        Positionning()
        """Do something here"""
        return

    def IsActive(self):        
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCADGui.ActiveDocument:
            return True
        else:
            return False

FreeCADGui.addCommand('WFrameBeam',WFrameBeam())

class BeamDef:
    '''
    Beam definition
    width
    height
    orientation : how th e beam is viewed in a 2D plan
    '''
    def __init__(self):
        self.name="Poutre"
        self.width=0
        self.height=0
        self.length=0
        self.orientation=""
        self.viewTypes=["face","up","cut"]
        self.view=self.viewTypes[0]

    def name(self,n):
        if n:
            self.name:n
            return self.name

    def height(self,h):
        if h:
            self.height=h
        return  self.height

    def width(self,w):
        if w:
            self.w=w
        return self.width

    def orientation(self,o):
        if o:
            self.orientation=o
        return self.orientation

    def getOrientationTypes(self):
        return self.viewTypes

    def length(self, l):
        if l:
            self.length=l
        return self.length


class TwoPoints():
    '''this class return 2 points selected by user'''
    def __init__(self,beam):
        self.beam=beam
        self.doc=FreeCAD.ActiveDocument
        if self.doc == None:
            FreeCAD.newDocument("Sans_Nom")
            
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.units=FreeCAD.Units.Quantity(1.0,FreeCAD.Units.Length)
        self.points = []

#snapper starting
        self.tracker = DraftTrackers.lineTracker()   
        self.tracker.on()
        FreeCADGui.Snapper.getPoint(callback=self.getPoint1)
    def getPoint1(self,point,obj=None):
#retreive snapped point
        if point == None:
            self.tracker.finalize()
            return        
        self.points.append(point)
        Console.PrintMessage("Origin point:"+str(self.points[0])+"\r\n")
#ask for a second point        
        FreeCADGui.Snapper.getPoint(last=point,callback=self.getPoint2,movecallback=self.update)

    def getPoint2(self,point,obj=None):
        self.points.append(point)
        Console.PrintMessage("Point 2 :"+str(self.points[1])+"\r\n")
        self.launchBeam()

    
    def update(self,point,info):
        dep = point

    def launchBeam(self):
        b =BeamShadow(self.beam)
        b.setPoints(points=self.points)
        b.createShadow(FreeCAD.Vector(0,0,0))


class Positionning:
    def __init__(self):
        beam=BeamDef()
        beamor=beam.getOrientationTypes()        

        beam.orientation,ok= QtGui.QInputDialog.getItem(None,"Orientation","sens de la barre",beamor,0,False)
        Console.PrintMessage("Positionning:"+str(ok)+"\r\n")
        if ok :
            beam.name,ok= QtGui.QInputDialog.getText(None,"Attributes","name:",QtGui.QLineEdit.Normal,beam.name)
            if ok:
                beam.width,ok= QtGui.QInputDialog.getText(None,"Section","Largeur(mm):",QtGui.QLineEdit.Normal,"45")
                if ok:
                    beam.width=float(beam.width)
                    beam.height,ok= QtGui.QInputDialog.getText(None,"Section","hauteur(mm):",QtGui.QLineEdit.Normal,"145")
                    if ok: 
                        beam.height=float(beam.height)
                        if beam.orientation == beamor[2] :
                            beam.length = float(QtGui.QInputDialog.getText(None,"Section","longueur(mm):",QtGui.QLineEdit.Normal,"1000")[0])
                        TwoPoints(beam)

class BeamShadow():
    def __init__(self,beam):
        self.beam=beam
        self.points= []
        # point used to rotate beam correctly
        self.tempPoint=Base.Vector(0,0,0)
        self.angle=0
        self.evalrot = self.beam.getOrientationTypes()
        self.structure = None

        # try to retreive keyboard numpad to place beam with points
        self.curview= Draft.get3DView()
        self.call= self.curview.addEventCallback("SoEvent",self.action)
        self.opoint=FreeCAD.Vector(0,0,0)
        self.status="PAD_5"
        QtGui.QMessageBox.information(None, "Information", "Use numpad to move beam correctly")


    def  createShadow(self,vect,structure=None):

        #Beam creation
        if structure:
            self.structure=structure
        else :
            #beam cut view
            if self.evalrot[2] in self.beam.orientation:

                pass

            self.structure=Arch.makeStructure(None, self.beam.length,self.beam.width,self.beam.height)

        # set beam rotations up cut or front
        
        self.vect = vect
        #beam face view
        if self.evalrot[0] in self.beam.orientation:
            self.structure.Placement=FreeCAD.Placement(self.vect, FreeCAD.Rotation(0,0,-90), FreeCAD.Vector(0,0,0))

        #beam up view
        elif self.evalrot[1] in self.beam.orientation:
            self.structure.Placement=FreeCAD.Placement(self.vect, FreeCAD.Rotation(0,0,0), FreeCAD.Vector(0,0,0))

        #beam cut view
        elif self.evalrot[2] in self.beam.orientation:
            self.structure.Placement=FreeCAD.Placement(self.vect, FreeCAD.Rotation(0,90,-90), FreeCAD.Vector(0,0,0))

        FreeCAD.ActiveDocument.recompute()
        #move beam to first picked point
        Draft.move(self.structure,self.points[0])
        FreeCAD.ActiveDocument.recompute()
        
        Draft.rotate(self.structure,self.angle,center=self.points[0],copy=False)

        #set Attributes
        self.structure.ViewObject.Transparency=50
        self.structure.IfcType="Beam"
        self.structure.Tag="Wood-Frame"
        self.structure.Label=self.beam.name

        # then recompute
        FreeCAD.ActiveDocument.recompute()
        Console.PrintMessage("##BeamTracker## Hit ENTER to terminate\r\n")

    def finalize(self):
        self.structure.ViewObject.Transparency=0
        self.structure.ViewObject.DrawStyle="Solid"
        FreeCAD.ActiveDocument.recompute()

    def action(self, arg):
        #message for tests
        #Console.PrintMessage("##BeamTracker##:"+str(arg)+"\r\n")

        #beam face view
        if self.evalrot[0] in self.beam.orientation:
            h=self.beam.height
            w=self.beam.width
        #beam up view
        elif self.evalrot[1] in self.beam.orientation:
            w=self.beam.height
            h=self.beam.width
        #beam up view
        elif self.evalrot[2] in self.beam.orientation:
            h=self.beam.height
            w=self.beam.width

        if (arg["Type"] == "SoMouseButtonEvent") and (arg["Button"] == "BUTTON1") and  (arg["State"] == "UP"):
            self.finalize()
            self.finish()


        if (arg["Type"] == "SoKeyboardEvent") and (arg["State"] == "UP") :
            if arg["Key"] == "ESCAPE":

                ###TODO remove component CRASH
                '''
                rm = FreeCAD.ActiveDocument
                rm.openTransaction("Remove object")
                rm.removeObject(self.structure.Name)
                rm.commitTransaction()
                rm.recompute()
                '''
                self.finish()
            # numpad assignement for beam positionning
            if arg["Key"] == "PAD_1":
                self.opoint[1]=h/2.0
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=w/2.0
                else :
                    self.opoint[2]=w/2.0
                self.structure.ViewObject.DrawStyle="Solid"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_2":
                self.opoint[1]=h/2.0
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=0.0
                else:
                    self.opoint[2]=0.0
                self.structure.ViewObject.DrawStyle="Dashdot"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_3":
                self.opoint[1]=h/2.0
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=-w/2.0
                else:
                    self.opoint[2]=-w/2.0

                self.structure.ViewObject.DrawStyle="Dashed"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_4":
                self.opoint[1]=0.0
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=w/2.0
                else:
                    self.opoint[2]=w/2.0

                self.structure.ViewObject.DrawStyle="Solid"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_5":
                self.opoint[1]=0.0
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=0.0
                else:
                    self.opoint[2]=0.0

                self.structure.ViewObject.DrawStyle="Dashdot"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_6":
                self.opoint[1]=0.0
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=-w/2.0
                else:
                    self.opoint[2]=-w/2.0

                self.structure.ViewObject.DrawStyle="Dashed"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_7":
                self.opoint[1]=-h/2.0
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=w/2.0
                else:
                    self.opoint[2]=w/2.0

                self.structure.ViewObject.DrawStyle="Solid"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_8":
                self.opoint[1]=-h/2.0
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=0.0
                else:
                    self.opoint[2]=0.0

                self.structure.ViewObject.DrawStyle="Dashdot"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_9":
                self.opoint[1]=-h/2.0
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=-w/2.0
                else:
                    self.opoint[2]=-w/2.0

                self.structure.ViewObject.DrawStyle="Dashed"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_ENTER" or arg["Key"] == "RETURN":
                self.finalize()
                self.finish()



    def setPoints(self,points):
        self.points=points
        Console.PrintMessage("##BeamTracker## points:"+str(self.points)+"\r\n")

        #beam cut view, length is alreday set previously
        eval =self.beam.getOrientationTypes()
        if not eval[2] in self.beam.orientation:
            self.beam.length= DraftVecUtils.dist(self.points[0],self.points[1])

        Console.PrintMessage("##BeamTracker## Distance between 2 vectors:"+str(self.beam.length)+"\r\n")
        #set Angle

        #0°
        if (self.points[0][0] > self.points[1][0]) and (self.points[0][1] == self.points[1][1]):
            Console.PrintMessage("##BeamTracker## 90°\r\n")
            self.angle=0

        if (self.points[0][0] < self.points[1][0]) and (self.points[0][1] < self.points[1][1]):
            Console.PrintMessage("##BeamTracker## 0 to 89°\r\n")
            self.angle=atan((self.points[1][1]-self.points[0][1])/(self.points[1][0]-self.points[0][0]))
            self.angle=degrees(self.angle)
        #90
        elif (self.points[0][0] == self.points[1][0]) and (self.points[0][1] < self.points[1][1]):
            Console.PrintMessage("##BeamTracker## 90°\r\n")
            self.angle=90
        #91 to 179
        elif (self.points[0][0] > self.points[1][0]) and (self.points[0][1] < self.points[1][1]):
            Console.PrintMessage("##BeamTracker## 91 to 179\r\n")
            self.angle=atan((self.points[1][1]-self.points[0][1])/(self.points[1][0]-self.points[0][0]))
            self.angle=degrees(self.angle+(math.pi))
        #180
        elif (self.points[0][0] > self.points[1][0]) and (self.points[0][1] == self.points[1][1]):
            Console.PrintMessage("##BeamTracker## 180\r\n")
            self.angle=180
        #181 269
        elif (self.points[0][0] > self.points[1][0]) and (self.points[0][1] > self.points[1][1]):
            self.angle=atan((self.points[1][1]-self.points[0][1])/(self.points[1][0]-self.points[0][0]))
            Console.PrintMessage("##BeamTracker## 181 to 269\r\n")
            self.angle=degrees((math.pi)+ self.angle)
        #270
        elif (self.points[0][0] == self.points[1][0]) and (self.points[0][1] > self.points[1][1]):
            Console.PrintMessage("##BeamTracker## 270\r\n")
            self.angle=270
        #271 to 359
        else :
            self.angle=atan((self.points[1][1]-self.points[0][1])/(self.points[1][0]-self.points[0][0]))
            Console.PrintMessage("##BeamTracker## 271 to 360\r\n")
            self.angle=degrees(2*(math.pi)+ self.angle)


        Console.PrintMessage("##BeamTracker## Angle DIY"+str(self.angle)+"°\r\n")

    def finish(self,closed=False):
       if self.call:
            try:
                self.curview.removeEventCallback("SoEvent",self.call)
            #except RuntimeError:
            except :
                pass
            self.call=None

