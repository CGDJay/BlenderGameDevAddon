# BlenderGameDevAddon
A Blender addon devised to assist in the production of game development

This addon consist of multiple tools developed to streamline the game developement process. 
Some of the tools are adapted/ modified versions of excisting tools from public GNU license repositories


# Mesh Tools
- hidden assist
  - 3 button mouse enable in sculpt mode 
  - auto enable default addons in blender for gamedev
- Quick ops
  - quickly set origin point to selection
  - quickly create floater meshes ( currently requires custom vert group for mesh bounds)
  - quickly creat lattice
  - quickly create warp (uses 3d cursor to place the warp points)
  - reduce cylinder resolution
  - quick resolve Ngon
  - remove Subdiv support loops

- Quick suffix 
  - for quickly assigning predefined suffixes to any mesh


- Generate Moss cap
  - generates a cap mesh to work with a predifined shader to create a coat of moss cards


- Pivot painter
  - record indevidual mesh pivot positions to either texture or vertex color


- vertex animation
  - convert blend shape animation to a texture to be used within engine to recreate mesh deformation at realtime 


- Tex plane tesselation 
  - cut out alpha cards for foliage or any kind of asset witha single click 

- Custom export 
  - export selected mesh and children objects at world center and apply SM_ prefix (WIP UX)



# Installation Guide

1. Click the **Code** button in the top right of the repo & click **Download ZIP** in the dropdown (Do not unpack the ZIP file)
2. Follow this video for the rest of the simple instructions


https://user-images.githubusercontent.com/105077390/194727061-cd03f3ee-c65c-46f5-bb92-868b0097ccaf.mp4


# To do
  
  # Complete
  - [x] convert multiple custom UV atlas operator into single operator (reference the unwrap operator)
  - [x] add import image as plane operator to TPT when no object is selected
  - [x] Expose orientation and additional parameters for Custom export 
  - [x] Exspose naming conventions for Load PBR Mat
  - [x] Add presets to export
  - [x] Restore selection type after context aware Mark UV seam
  
  # UV tools
  - [ ] Fix Unwrap tool for used outside of UV sync=True
  
  # Moss Cap
  - [ ] Add test for non manifold moss cap mesh (on hold as priority is low)
  
  # Quick Suffix
  - [ ] Add Collection quick suffix 
  
  # Batch Asset Librbary
  - [ ] update batch asset library to use the split fuction to get asset tags
  
  # Pivot Painter
  - [ ] reduce the amount of available options on pivot painter to streamline the process
  - [ ] Use active selection location instead of world center for pivot to vcol operation
  
  # Collision tools
  - [ ] Create Auto UCX
  - [ ] Find optimal UI for custom collision 
 
  
  
# original scripts 
  - collision tools : https://github.com/greisane/gret
  - Pivot painter : https://github.com/Gvgeo/Pivot-Painter-for-Blender
  - Vertex animation : https://github.com/JoshRBogart/unreal_tools
  - tex plane tesselation : https://github.com/Pullusb/Tesselate_texture_plane
