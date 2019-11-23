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
if FreeCAD.GuiUp:
    import FreeCADGui
    import Arch, Draft, Part
    from PySide import QtCore, QtGui
    from DraftTools import translate
    from FreeCAD import Base, Console, Vector, Rotation
    import math, DraftGeomUtils, DraftVecUtils

else:
    def translate(ctxt,txt):
        return txt
# waiting for WFrame_rc and eventual FreeCAD integration
import os
__dir__ = os.path.dirname(__file__)

__title__="FreeCAD WoodFrame List"
# Original Python Script author : Jonathan Wiedemann
__author__ = "Jerome Laverroux"
__url__ = "http://www.freecadweb.org"


class WFrameList():
    """WFrameList"""

    def GetResources(self):
        return {'Pixmap'  :  __dir__ + '/Resources/icons/WFrame_Listing.svg',
                'Accel' : "W,L",
                'MenuText': "WFrameList",
                'ToolTip' : "Create wood beams listing"}

    def Activated(self):

        """Do something here"""
        panel = _ListingTaskPanel()
        FreeCADGui.Control.showDialog(panel)

        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCADGui.ActiveDocument:
            return True
        else:
            return False
FreeCADGui.addCommand('WF_List',WFrameList())



def makeTimberListing(objs, export):
    tb = Listing(objs, export)
    tb.makeTimberList()
    #if display:
    tb.printTimberList()
    #return tb.getTimberList()



def getTagList():
    taglist = []
    for obj in FreeCAD.ActiveDocument.Objects :
        try :
            if obj.Tag:
                if taglist.count(str(obj.Tag)) == 0:
                    taglist.append(str(obj.Tag))
        except AttributeError:
            pass
    return taglist

def listingfilter(items):
    doc = FreeCAD.ActiveDocument
    objs = doc.Objects
    objlist = []
    for item in items :
        if item == "Selection":
            for obj in FreeCADGui.Selection.getSelection() :
                objlist.append(obj)
        taglist = getTagList()
        for tag in taglist :
            if item == tag :
                for obj in objs:
                    #a = obj.Name
                    #print("Objet : " + str(a))
                    #b = obj.Label
                    if hasattr(obj,"Proxy"):
                        #print(" - hasattr Proxy : ok")
                        if hasattr(obj.Proxy,"Type"):
                            #print(" - hasattr Type : ok")
                            if FreeCADGui.ActiveDocument.getObject(obj.Name).Visibility :
                                #print(" - Visibility : True")
                                try:
                                    if obj.Tag == item :
                                        objlist.append(obj)
                                except AttributeError:

                                    pass
                                #Listing()
                                #objectAnalyse(obj)
                            else:
                                #print(" - Visibility : False")
                                pass
                        else:
                            #print(" - hasattr Type : no")
                            pass
                    else:
                        #print(" - hasattr Proxy : no")
                        pass
    s = []
    for i in objlist:
        if i not in s:
            s.append(i)
    return s

class _CommandListing:
        "the Timber Listing command definition"
        def GetResources(self):
           return {'Pixmap'  : __dir__ + '/icons/Timber_Listing.svg',
                    'MenuText': QtCore.QT_TRANSLATE_NOOP("Timber_Listing","Make listing"),
                    'ToolTip': QtCore.QT_TRANSLATE_NOOP("Timber_Listing","List objects")}

        def IsActive(self):
            return True

        def Activated(self):
            pass

class _ListingTaskPanel:
    def __init__(self):
        self.form = QtGui.QWidget()
        self.form.setObjectName("TaskPanel")
        self.grid = QtGui.QGridLayout(self.form)
        self.grid.setObjectName("grid")
        self.title = QtGui.QLabel(self.form)
        self.grid.addWidget(self.title, 1, 0)
        self.textobjlist = QtGui.QLabel(self.form)
        self.grid.addWidget(self.textobjlist, 1, 1)

        self.taglistwidget = QtGui.QListWidget(self.form)
        self.taglistwidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        #QtGui.QAbstractItemView([parent=self.taglistwidget])
        self.grid.addWidget(self.taglistwidget, 2, 0)
        self.taglistwidget.addItem("Selection")
        for tag in getTagList():
            self.taglistwidget.addItem(tag)
        self.filteredlistwidget = QtGui.QListWidget(self.form)
        self.grid.addWidget(self.filteredlistwidget, 2, 1)
        self.infoText =  QtGui.QLabel(self.form)
        self.grid.addWidget(self.infoText, 3, 0)
        self.checkSpreadsheet = QtGui.QCheckBox(self.form)
        self.checkShape = QtGui.QCheckBox(self.form)
        self.grid.addWidget(self.checkSpreadsheet, 4, 0)
        self.grid.addWidget(self.checkShape, 4, 1)

        QtCore.QObject.connect(self.taglistwidget,QtCore.SIGNAL("itemSelectionChanged()"),self.makeFiltered)

        self.retranslateUi(self.form)

    def makeFiltered(self):
        items = []
        for item in self.taglistwidget.selectedItems():
            items.append(item.text())
        #print items
        objlist = listingfilter(items)
        self.filteredlistwidget.clear()
        for obj in objlist:
            self.filteredlistwidget.addItem(obj.Label)

    def accept(self):
        items = []
        export = []
        for item in self.taglistwidget.selectedItems():
            items.append(item.text())
        print(items)
        objlist = listingfilter(items)
        if self.checkSpreadsheet.isChecked() :
            export.append("Spreadsheet")
        if self.checkShape.isChecked() :
            export.append("Shape")
        makeTimberListing(objlist,export)
        return True

    def reject(self):
        FreeCAD.Console.PrintMessage("Cancel Timber Listing\n")
        return True

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)

    def retranslateUi(self, TaskPanel):
        TaskPanel.setWindowTitle("Timber Listing")
        self.title.setText("Press Ctrl to multiple selection")
        self.textobjlist.setText("Objects to be listed")
        self.infoText.setText("Export")
        self.checkSpreadsheet.setText("Make Spreadsheet")
        self.checkShape.setText("Make aligned shapes")

class Listing():
    def __init__(self, objs, export):
        self.objlist=objs
        self.export = export
        parms = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units")
        # tag list = timberlist[0]
        # section list timberlist[0][0]
        # debit list timberlist[0][0][0]
        # [ [ Tag , [ [ base , hauteur ] , [ [ debit , quantite ], ], ] ] , ]
        self.timberlist=[]

    def makeTimberList(self):
        #for tag in getTagList():
        timberlistbytag = []

        self.Label=""

        #for each object in objlist
        for obj in self.objlist:
            # if tag object match a tag in taglist

            if hasattr(obj,"Tag"):
                if obj.Tag in getTagList():
                    tag = obj.Tag
                else :
                    tag = "NoTag"

            else :
                tag = "NoTag"
                #for solids in object
            for solid in obj.Shape.Solids:
                # set a name for shape analyse
                name = str("Aligned_"+str(obj.Name))
                # make shape analyse boundbox aligned
                timber_part = self.shapeAnalyse(name,solid,)
                # add analyse to list
                timberlistbytag = self.addListe(tag, timber_part[0], timber_part[1], timber_part[2])
        #self.timberlist.append([tag,timberlistbytag])
        return self.timberlist

    def getTimberList():
        makeTimberList()
        return self.timberlist

    def printTimberList(self):
        for listbytag in self.timberlist:
            print("Tag : " + str(listbytag[0]))
            for section in listbytag[1]:
                print("Section : " + str(section[0])+"x"+str(section[1]))
                print("Qte    Longueur")
                for debit in section[2]:
                    print(str(debit[1])+"      "+str(debit[0]))
            print("")
        #if hasattr(FreeCAD.ActiveDocument,"TimberSpreadsheet"):
        #    mySheet = FreeCAD.ActiveDocument.TimberSpreadsheet
        #else :
        if "Spreadsheet" in self.export:
            self.makeSpreadsheet()

    def makeSpreadsheet(self):
        mySheet = FreeCAD.ActiveDocument.addObject('Spreadsheet::Sheet','TimberSpreadsheet')
        #mySheet.clearAll()
        FreeCAD.ActiveDocument.recompute()
        mySheet.set('A1', 'Liste')
        mySheet.set('A2', 'Date')
        mySheet.set('B2', 'Projet')
        mySheet.set('A3','Tag')
        mySheet.set('B3','largeur')
        mySheet.set('C3','Hauteur')
        mySheet.set('D3','Longueur')
        mySheet.set('E3','Quantite')
        mySheet.set('F3','Volume')
        voltotal = 0
        n=3
        for listbytag in self.timberlist:
            #n += 1
            mySheet.set('A'+str(n+1), str(listbytag[0]))
            mergestart = str(n+1)
            volsection = 0
            for section in listbytag[1]:
                voltag = 0
                #partBase = section[0]
                self.partWidth = section[0]
                self.partHeight = section[1]
                for debit in section[2]:
                    n += 1
                    #cellBase = 'B'+str(n)
                    cellWidth = 'B'+str(n)
                    cellHeigth = 'C'+str(n)
                    cellLength = 'D'+str(n)
                    cellQte = 'E'+str(n)
                    cellVol = 'F'+str(n)
                    mySheet.set(cellWidth , str(self.partWidth))
                    mySheet.set(cellHeigth , str(self.partHeight))
                    mySheet.set(cellLength , str(debit[0]))
                    mySheet.set(cellQte , str(debit[1]))
                    Console.PrintMessage("width" +str(self.partWidth)+"\r\n")
                    Console.PrintMessage("height "+str(self.partHeight)+"\r\n")
                    Console.PrintMessage("debit0 "+str(debit[0])+"\r\n")
                    Console.PrintMessage("debit1 "+str(debit[1])+"\r\n")
                    voldebit = (float(self.partWidth) * float(self.partHeight) * float(debit[0]) * float(debit[1]))/1000000000.
                    Console.PrintMessage("voldebit "+str(voldebit)+"\r\n")

                    mySheet.set(cellVol , str(voldebit))
                    voltag += voldebit
                volsection += voltag
            n += 1
            mergestop = str(n)
            mySheet.mergeCells('A' + mergestart + ':' + 'A' + mergestop)

            mySheet.set('F'+str(n),str(volsection))
            voltotal += volsection
            #print("")
        n += 1
        mySheet.set('F'+str(n),str(voltotal))
        FreeCAD.ActiveDocument.recompute()
    #def getTaginList(self):

    def addListe(self, tag, base, hauteur, longueur):
        #precision = parms.GetInt('Decimals')
        precision = 0
        base = round(base,precision)
        hauteur = round(hauteur,precision)
        longueur = round(longueur,precision)
        base = int(base)
        hauteur = int(hauteur)
        longueur = int(longueur)
        liste =  sorted([base, hauteur, longueur])
        base = liste[0]
        hauteur = liste[1]
        longueur = liste[2]
        #print "self.timberlist : ,",self.timberlist
        # By default object is not added
        added = False
        # Init taglist : list of tags present in self.timberlist
        taglist=[]
        # If current object tag is present add analyse in this taglist
        # else create a tag list with analyse
        idx = -1
        n = 0
        if len(self.timberlist) > 0:
            for tagslist in self.timberlist :
                #print tag,tagslist[0]
                if tagslist[0] == tag :
                    listbytag = tagslist[1]
                    idx = n
                n += 1
            if idx == -1 :
                self.timberlist.append([tag,[]])
                idx = -1
        else :
            self.timberlist.append([tag,[]])
            idx = -1
        #print(self.timberlist)
        if len(self.timberlist[idx][1]) > 0 :
            #print "self.timberlist est > 0"
            for x in self.timberlist[idx][1] :
                if x[0]==base and x[1]==hauteur :
                    #print "la section existe"
                    for qte in x[2]:
                        if qte[0] == longueur :
                            #print "la longueur existe"
                            #print "ajout une unite a longueur"
                            qte[1] += 1
                            added = True
                    if not added:
                        #print "ajout une longueur et une unite"
                        x[2].append([longueur,1])
                        added = True
            if not added:    #else:
                #print "la section existe pas"
                #print "ajout section , longueur, qte"
                self.timberlist[idx][1].append([base, hauteur,[[longueur,1],],])
        else:
            #print "la liste est vide"
            #print "ajout section , longueur, qte"
            self.timberlist[idx][1].append([base, hauteur,[[longueur,1],],])
        return self.timberlist
        #print "self.timberlist : ,",self.timberlist

    def getArea(self, face):
        return face.Area

    def getFacesMax(self, faces):
        faces = sorted(faces,key=self.getArea, reverse = True)
        facesMax = faces[0:4]
        return facesMax

    def getCoupleFacesEquerre(self, faces):
        listeCouple = []
        lenfaces = len(faces)
        faces.append(faces[0])
        for n in range(lenfaces):
            norm2 = faces[n+1].normalAt(0,0)
            norm1 = faces[n].normalAt(0,0)
            norm0 = faces[n-1].normalAt(0,0)
            if abs(round(math.degrees(DraftVecUtils.angle(norm1,norm0)))) == 90.:
                listeCouple.append([faces[n],faces[n-1]])
            if abs(round(math.degrees(DraftVecUtils.angle(norm1,norm2)))) == 90.:
                listeCouple.append([faces[n],faces[n+1]])
        return listeCouple

    def shapeAnalyse(self, name, shape):
        ## Create a new object with the shape of the current arch object
        ## His placment is set to 0,0,0
        obj = FreeCAD.ActiveDocument.addObject('Part::Feature',name)
        obj.Shape=shape
        obj.Placement.Base = FreeCAD.Vector(0.0,0.0,0.0)
        obj.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0.0,0.0,1.0),0.0)
        FreeCAD.ActiveDocument.recompute()
        ## Get the face to align with XY plane
        faces = obj.Shape.Faces
        facesMax = self.getFacesMax(faces)
        coupleEquerre = self.getCoupleFacesEquerre(facesMax)
        ## Get the normal of this face
        nv1 = coupleEquerre[0][0].normalAt(0,0)
        ## Get the goal normal vector
        zv = Vector(0,0,1)
        ## Find and apply a rotation to the object to align face
        pla = obj.Placement
        rot = pla.Rotation
        rot1 = Rotation(nv1, zv)
        newrot = rot.multiply(rot1)
        pla.Rotation = newrot
        ## Get the face to align with XY plane
        faces = obj.Shape.Faces
        facesMax = self.getFacesMax(faces)
        coupleEquerre = self.getCoupleFacesEquerre(facesMax)
        ## Get the longest edge from aligned face
        maxLength = 0.
        for e in coupleEquerre[0][0].Edges:
            if e.Length > maxLength:
                maxLength = e.Length
                edgeMax = e
        ## Get the angle between edge and X axis and rotate object
        vec = DraftGeomUtils.vec(edgeMax)
        vecZ = FreeCAD.Vector(vec[0],vec[1],0.0)
        pos2 = obj.Placement.Base
        rotZ = math.degrees(DraftVecUtils.angle(vecZ,FreeCAD.Vector(1.0,0.0,0.0),zv))
        Draft.rotate([obj],rotZ,pos2,axis=zv,copy=False)
        bb = obj.Shape.BoundBox
        movex = bb.XMin*-1
        movey = bb.YMin*-1
        movez = bb.ZMin*-1
        Draft.move([obj], FreeCAD.Vector(movex, movey, movez))
        FreeCAD.ActiveDocument.recompute()
        ## Get the boundbox
        analyse = [obj.Shape.BoundBox.YLength, obj.Shape.BoundBox.ZLength, obj.Shape.BoundBox.XLength]
        if not "Shape" in self.export :
            FreeCAD.ActiveDocument.removeObject(name)
        return analyse
