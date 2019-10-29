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

#### Add a Beam

![WFrameBeam](Resources/icons/WFrameBeam.svg) Short explanation on what this function does.

#### Add a Panel

![WFramePanel](Resources/icons/WFramePanel.svg) Short explanation on what this function does.

#### Edit Attributes

![WFAttrEdit](Resources/icons/WFEditAttr.svg) Short explanation on what this function does.

#### Select/Hide by Attributes

![WFSelectAttr](Resources/icons/WFSelectAttr.svg) Short explanation on what this function does.

#### Generate Listing

![WFrame_Listing](Resources/icons/WFrame_Listing.svg) Short explanation on what this function does.

#### Copy element

![WFCopy](Resources/icons/WFCopy.svg) Short explanation on what this function does.

#### Align View from Current Workplane

![AlignViewWPlane](Resources/icons/AlignViewWPlane.svg) Short explanation on what this function does.


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
