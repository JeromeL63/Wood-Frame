# FreeCAD Wood Workbench

A collection of tools to use FreeCAD to design wood frames.  
**Note:** this a fork of the [FreeCAD-Timber Workbench][Timber-Workbench].  
It uses the FreeCAD Draft and Arch workbenches.

[Timber-Workbench]: https://github.com/j-wiedemann/FreeCAD-Timber/

## Usage
- Create beams with advanced positioning
- Create panels with advanced positioning
- Attributes, used to select and filter objects (name, groups, sub-group, material, type ....) easily
- Select and show by attributes
- Listing for invoices and production list

### Toolbar

#### Add a Wood Beam

![WFrameBeam](Resources/icons/WF_Beam.svg) Add a wood beam. To move insertion point, use the Numpad.

[![Wood-Frame-Add-Beam](http://img.youtube.com/vi/la1BvfgFgLQ/maxresdefault.jpg)](http://www.youtube.com/watch?v=la1BvfgFgLQ "Wood-Frame: Add Beam function demonstrated")  
(Click the clip above to see the Add Panel tool in action)

 
#### Add a Wood Panel

![WFramePanel](Resources/icons/WF_Panel.svg) Add a wood panel. This tool operates simliarly to Add beam, but with panel size restriction. To move insertion point, use the Numpad.

[![Wood-Frame-Add-Panel](http://img.youtube.com/vi/_G4gYu-Vkkg/maxresdefault.jpg)](http://www.youtube.com/watch?v=_G4gYu-Vkkg "Wood-Frame: Add Panel function demonstrated")  
(Click the clip above to see the Add Panel tool in action)

#### Edit Attributes

![WFAttrEdit](Resources/icons/WFEditAttr.svg) Edit the attributes of existing oobjects (name, groups, sub-group, material, type ....)

[![Wood-Frame-Edit-Attributes](http://img.youtube.com/vi/g7brtsF-MAc/maxresdefault.jpg)](http://www.youtube.com/watch?v=g7brtsF-MAc "Wood-Frame: Edit Attributes tool demonstrated")  
(Click the clip above to see the Edit Attributes tool in action)

#### Select/Hide by Attributes

![WFSelectAttr](Resources/icons/WFSelectAttr.svg) Select or hide elements in the [3D view](https://wiki/reecadweb.org/3D_view) by their specific attributes.

#### Generate Listing

![WFrame_Listing](Resources/icons/WFrame_Listing.svg) Generate a [Spreadsheet](https://wiki.freecadweb.org/Spreadsheet_Workbench) listing of the different materials selected in the [3D view](https://wiki.freecadweb.org/3D_view)

[![Wood-Frame-Generate-Listing](http://img.youtube.com/vi/RZgyhkf-bjA/maxresdefault.jpg)](http://www.youtube.com/watch?v=RZgyhkf-bjA "Wood-Frame: Listing tool demonstrated")  
(Click the clip above to see the Generate Listing tool in action)


#### Copy element

![WFCopy](Resources/icons/WFCopy.svg) Duplicates an element.

#### Align View from Current Workplane

![AlignViewWPlane](Resources/icons/AlignViewWPlane.svg) Align view from current workplane,


#### Stretch tool

[![Wood-Frame-Stretch-Tool](http://img.youtube.com/vi/6zNmxR6LGXA/maxresdefault.jpg)](http://www.youtube.com/watch?v=6zNmxR6LGXA "Wood-Frame: Stretch tool demonstrated")  
(Click the clip above to see the Stretch tool in action)

### Prerequisites
- [x] FreeCAD >= v0.19

### Installation

#### Automatic Install
<details>
  <summary>Expand this section to learn how to install and auto-update Wood Workbench</summary>
  
Use FreeCAD's built-in Addon-Manager. It requires a one-time setup and then updates seamlessly afterwards.
1. Start FreeCAD
2. Go to **Tools > Addon Manager**  
3. Click on the _Configure_ button in the top right corner
4. Select the checkbox to _Automatically check for updates at start_
5. Add the Wood Workbench Github repo address in to the _Custom repositories (one per line)_ text box:  
`https://github.com/JeromeL63/Wood-Frame`
6. Press **OK**
7. Restart FreeCAD  
Result: You should see the Wood Workbench available in the Workbench drop-down menu.
</details>

#### Manual installation
<details>
  <summary>Expand this section to learn how to manually install Wood Workbench</summary>

```bash
cd ~/.FreeCAD/Mod
git clone https://github.com/JeromeL63/Wood-Frame
```

**Note:** To stay up-to-date with FreeCAD Wood Workench:  
```bash
cd ~/.FreeCAD/Mod
git fetch
```

**Note:** Make sure to restart FreeCAD after you install or update the Wood Workbench.
</details>

## Notes
Numpad viewstyle shortcuts are modified to:  
CTRL + 1  
CTRL + 2  
....  

### Beam positioning from origin beam point


Column 1 | Column 2 | Column 3 
--------------------------|--------------------------|---------------------------
7:above plan left corner | 8:axis  plan left corner | 9:behind plan left corner
4:above plan beam axis  | 5:axis plan beam axis | 6:behind plan beam axis
1:above plan right corner | 2:axis plan right corner | 3: behind plan right corner

Now Positioning is integrated in dialog taskbox

# License
GNU General Public License V3.0
