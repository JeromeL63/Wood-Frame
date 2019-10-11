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
from FreeCAD import Base, Console, Vector,Rotation
from math import *

import DraftTrackers
import WFrameAttributes


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

__title__="FreeCAD WoodFrame Beam"
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"



from PySide import QtGui

class WFrameBeam():
    """WFrameBeam"""

    def GetResources(self):
        return {'Pixmap'  :  __dir__ + '/Resources/icons/WFrameBeam.svg',
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
        self.type=0
        self.width=0
        self.height=0
        self.length=0
        self.orientation=""
        self.viewTypes=["face","up","cut"]
        #the default view type
        self.view=self.viewTypes[0]

#getters and setters
    def name(self,n):
        if n:
            self.name:n
        return self.name

    def preset(self,p):
        if p:
            self.preset:p
        return self.preset

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


class BeamVector():
    """this class return 2 points selected by user"""
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
        FreeCADGui.Snapper.getPoint(callback=self.getPoint1,title="Select the origin of the beam")
    def getPoint1(self,point,obj=None):
#retreive snapped point
        if point == None:
            self.tracker.finalize()
            return        
        self.points.append(point)        
#ask for a second point        
        FreeCADGui.Snapper.getPoint(last=point,callback=self.getPoint2,movecallback=self.update,title="Select the end of the beam")
    def getPoint2(self,point,obj=None):
        self.points.append(point)
        b=BeamShadow(self.points,self.beam)
        b.createShadow()

    def update(self,point,info):
        dep = point


class BeamOffset():
    '''this class return 2 points selected by user'''
    def __init__(self,beam,originPoint,structure=None):
        self.beam=beam
        self.originPoint=originPoint
        self.structure=structure
        self.doc=FreeCAD.ActiveDocument
        if self.doc == None:
            FreeCAD.newDocument("Sans_Nom")

        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.units=FreeCAD.Units.Quantity(1.0,FreeCAD.Units.Length)
        self.points = []

#snapper starting
        self.tracker = DraftTrackers.lineTracker()
        self.tracker.on()
#ask for a point
        FreeCADGui.Snapper.getPoint(last=self.originPoint,callback=self.getPoint,movecallback=self.update,title="Change the insertion Point(or Esc)")
    def getPoint(self,point,obj=None):
        if point == None:
            self.tracker.finalize()
            self.finalize(FreeCAD.Vector(0,0,0),structure=self.structure)
            return
        self.points.append(point)
        self.points.append(self.originPoint)
        b=BeamShadow(self.points,self.beam)
        vector=FreeCAD.Vector(self.points[1][0]-self.points[0][0],self.points[1][1]-self.points[0][1],self.points[1][2]-self.points[0][2])
        self.finalize(vector,self.structure)

    def update(self,point,info):
        dep = point

    def finalize(self,finalPoint,structure=None):
        structure.ViewObject.Transparency=0
        structure.ViewObject.DrawStyle="Solid"
        Draft.move(structure,finalPoint)
        FreeCAD.ActiveDocument.recompute()




class Positionning:
    def __init__(self):
        beam=BeamDef()
        beamor=beam.getOrientationTypes()        

        beam.orientation,ok= QtGui.QInputDialog.getItem(None,"Orientation","sens de la barre",beamor,0,False)
        Console.PrintMessage("Positionning:"+str(ok)+"\r\n")
        if ok :
            beam.name,ok= QtGui.QInputDialog.getText(None,"Attributes","name:",QtGui.QLineEdit.Normal,beam.name)
            if ok:
                types=WFrameAttributes.getTypes()
                beam.preset,ok= QtGui.QInputDialog.getItem(None,"Attributes","type:",types,beam.type,False)
                if ok:
                    beam.width,ok= QtGui.QInputDialog.getText(None,"Section","Largeur(mm):",QtGui.QLineEdit.Normal,"45")
                    if ok:
                        beam.width=float(beam.width)
                        beam.height,ok= QtGui.QInputDialog.getText(None,"Section","hauteur(mm):",QtGui.QLineEdit.Normal,"145")
                        if ok:
                            beam.height=float(beam.height)
                            if beam.orientation == beamor[2] :
                                beam.length = float(QtGui.QInputDialog.getText(None,"Section","longueur(mm):",QtGui.QLineEdit.Normal,"1000")[0])
                            BeamVector(beam)

class BeamShadow():
    def __init__(self,points,beam):
        Console.PrintMessage("##BeamTracker## Beam Shadow \r\n")
        #used to prevent first click
        self.beam=beam
        self.clickCount=0
        self.boundingBoxExist= False
        #self.beam=beam        
        self.points = points
        # point used to rotate beam correctly
        self.tempPoint=Base.Vector(0,0,0)
        self.angle=0
        self.evalrot = self.beam.getOrientationTypes()
        self.structure = None

        # try to retreive keyboard numpad to place beam with points
        self.curview= Draft.get3DView()
        #self.call= self.curview.addEventCallback("SoEvent",self.action)
        self.opoint=FreeCAD.Vector(0,0,0)
        #self.status="PAD_5"



    def  createShadow(self,structure=None):
        self.clickCount=0

        if not self.evalrot[2] in self.beam.orientation:
            self.beam.length= DraftVecUtils.dist(self.points[0],self.points[1])


        #Beam creation
        if self.structure:
            self.structure=structure
        else :
            #beam cut view
            if self.evalrot[2] in self.beam.orientation:
                pass
            self.structure=Arch.makeStructure(None, self.beam.length,self.beam.width,self.beam.height)

        self.vecAngle=FreeCAD.Vector(0,0,0)
        self.vecAngle[0]=self.points[1][0]-self.points[0][0]
        self.vecAngle[1]=self.points[1][1]-self.points[0][1]
        self.vecAngle[2]=self.points[1][2]-self.points[0][2]


        #get rotations between zplan and current plan   YESSSS
        self.wplan=FreeCAD.DraftWorkingPlane
        self.rotPlan=self.wplan.getRotation().Rotation

        #Initialize placement
        # set the origin point
        self.initialPlacement=FreeCAD.Base.Placement(self.points[0], FreeCAD.Rotation(0,0,0), FreeCAD.Vector(0,0,0))
        # Rotate beam on workingplane

        self.initialPlacement=self.initialPlacement * FreeCAD.Base.Placement(FreeCAD.Vector(0,0,0), self.rotPlan)
        self.structure.Placement=self.initialPlacement

        #beam defaultview is from face
        self.structure.Placement=self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(0,0,-90))
        #beam up view
        if self.evalrot[1] in self.beam.orientation:
            self.structure.Placement=self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(0,0,90))
        #beam cut view
        elif self.evalrot[2] in self.beam.orientation:
            self.structure.Placement=self.structure.Placement * FreeCAD.Base.Placement(FreeCAD.Vector(0,0,0), FreeCAD.Rotation(90,0,0))



        ''' 
        now beam is oriented
        we have to apply offset gived by Snapper (numpad is too hard to make it working)
        '''
        BeamOffset(self.beam,self.points[0],self.structure)
        FreeCAD.ActiveDocument.recompute()



        #set Angle

        #get normal of current workplane

        self.normal=FreeCAD.DraftWorkingPlane.getNormal()

        # get angle in radians between two point with the given normal plan
        self.localPoints=[]
        self.localPoints.append(FreeCAD.DraftWorkingPlane.getLocalCoords(self.points[0]))
        self.localPoints.append(FreeCAD.DraftWorkingPlane.getLocalCoords(self.points[1]))
        self.vecAngle=FreeCAD.Vector(0,0,0)
        #relative vector angle
        self.vecAngle[0]=self.localPoints[1][0]-self.localPoints[0][0]
        self.vecAngle[1]=self.localPoints[1][1]-self.localPoints[0][1]
        self.vecAngle[2]=self.localPoints[1][2]-self.localPoints[0][2]
        #along workingplane normal
        Console.PrintMessage("##BeamTracker## Workplan normal "+str(self.normal)+"\r\n")


        self.angle=DraftVecUtils.angle(self.vecAngle,normal=self.normal)
        Console.PrintMessage("##BeamTracker## Angle before "+str(self.angle)+"°\r\n")

        ####WARNING
        #angles 90 and -90 are inverted on Draft on XY plan
        if self.normal == FreeCAD.Vector(0.0,0.0,1.0):
            self.normal=FreeCAD.Vector(0,0,-1)

        self.angle=degrees(self.angle)

        Draft.rotate(self.structure,self.angle,center=self.points[0],axis=self.normal,copy=False)
        FreeCAD.ActiveDocument.recompute()


        #set Attributes
        WFrameAttributes.insertAttr(self.structure)
        self.structure.ViewObject.Transparency=50
        self.structure.IfcType="Beam"
        self.structure.Tag="Wood-Frame"
        self.structure.Label=self.beam.name
        #specific attributes for WFrame
        self.structure.Name=self.beam.name

        # then recompute
        FreeCAD.ActiveDocument.recompute()


    def askInsPoint(self):
        Console.PrintMessage("##BeamTracker## Ask ins point\r\n")
        self.tracker=DraftTrackers.lineTracker()
        FreeCADGui.Snapper.getPoint(callback=self.getSartPoint)



####ACTION

    def action(self, arg):
        #message for tests
        #Console.PrintMessage("##BeamTracker##:"+str(arg)+"\r\n")
        h=self.beam.height
        w=self.beam.width
        if self.evalrot[1] in self.beam.orientation:
            w=self.beam.height
            h=self.beam.width



        if (arg["Type"] == "SoMouseButtonEvent") and (arg["Button"] == "BUTTON1") and  (arg["State"] == "UP"):
            self.clickCount+=1
            Console.PrintMessage("##BeamTracker## Mouse BUTTON1 pressed\r\n")
            if self.clickCount == 2:
                self.finalize()
                self.finish()
            elif self.clickCount >2:
                self.clickCount=1


        elif (arg["Type"] == "SoKeyboardEvent") and (arg["State"] == "UP") :

            if arg["Key"] == "ESCAPE":
                self.finish()
            # numpad assignement for beam positionning
            if arg["Key"] == "PAD_1":
                self.opoint=self.coords[3]
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint=self.coords[4]
                    self.structure.ViewObject.DrawStyle="Solid"
                else :
                    self.opoint[2]=w/2.0
                    self.structure.ViewObject.DrawStyle="Solid"

                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_2":
                self.opoint=self.midpoint(self.coords[2],self.coords[3])
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=0.0
                    self.structure.ViewObject.DrawStyle="Solid"
                else:
                    self.opoint[2]=0.0
                    self.structure.ViewObject.DrawStyle="Dashdot"

                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_3":
                self.opoint=self.coords[2]
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=-w/2.0
                    self.structure.ViewObject.DrawStyle="Solid"
                else:
                    self.opoint[2]=-w/2.0
                    self.structure.ViewObject.DrawStyle="Dashed"

                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_4":
                self.opoint=self.midpoint(self.coords[1],self.coords[3])
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=w/2.0
                    self.structure.ViewObject.DrawStyle="Solid"
                else:
                    self.opoint[2]=w/2.0
                    self.structure.ViewObject.DrawStyle="Solid"

                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_5":
                self.opoint=self.points[0]
                if self.evalrot[2] in self.beam.orientation:
                    self.structure.ViewObject.DrawStyle="Solid"                    
                else:                    
                    self.structure.ViewObject.DrawStyle="Dashdot"

                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_6":
                self.opoint=self.midpoint(self.coords[0],self.coords[2])
                if self.evalrot[2] in self.beam.orientation:
                    self.structure.ViewObject.DrawStyle="Solid"
                    self.opoint[0]=-w/2.0
                else:
                    self.opoint[2]=-w/2.0
                    self.structure.ViewObject.DrawStyle="Dashed"

                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_7":
                self.opoint=self.coords[1]
                if self.evalrot[2] in self.beam.orientation:
                    self.structure.ViewObject.DrawStyle="Solid"
                    self.opoint[0]=w/2.0
                else:
                    self.opoint[2]=w/2.0
                    self.structure.ViewObject.DrawStyle="Solid"

                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_8":
                self.opoint=self.midpoint(self.coords[0],self.coords[1])
                if self.evalrot[2] in self.beam.orientation:
                    self.structure.ViewObject.DrawStyle="Solid"
                    self.opoint[0]=0.0
                else:
                    self.opoint[2]=0.0
                    self.structure.ViewObject.DrawStyle="Dashdot"
                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_9":
                self.opoint=self.coords[0]
                if self.evalrot[2] in self.beam.orientation:
                    self.opoint[0]=-w/2.0
                    self.structure.ViewObject.DrawStyle="Solid"
                else:
                    self.opoint[2]=-w/2.0
                    self.structure.ViewObject.DrawStyle="Dashed"

                self.createShadow(self.opoint,self.structure)

            if arg["Key"] == "PAD_ENTER" or arg["Key"] == "RETURN":
                self.finalize()
                self.finish()



    def finish(self,closed=False):
       if self.call:
            try:
                self.curview.removeEventCallback("SoEvent",self.call)
                Console.PrintMessage("##BeamTracker## event callback removed \r\n")

            #except RuntimeError:
            except :
                pass
            self.call=None

