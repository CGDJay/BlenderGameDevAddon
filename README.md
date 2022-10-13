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


- Batch library importer
  - batch import meshes into the blender asset library


- Generate Moss cap
  - generates a cap mesh to work with a predifined shader to create a coat of moss cards


- Pivot painter
  - record indevidual mesh pivot positions to either texture or vertex color


- vertex animation
  - convert blend shape animation to a texture to be used within engine to recreate mesh deformation at realtime 


- Tex plane tesselation 
  - cut out alpha cards for foliage or any kind of asset witha single click 


- Load PBR Mat
  - instantly import any texture set into blender for realtime preview (WIP UX)

- Custom export 
  - export selected mesh and children objects at world center and apply SM_ prefix (WIP UX)

- Custom col
  - quickly assign custom collision meshes to selection (WIP UX)

# UV Tools

- Color Atlas Tools
  - quickly shift selection UV into apporpriate UV space on atlas texture
  - quickly move selected UV islands into the correct Udim space for Virtual texture atlases

- Texel Density
  - quickly assign correct texel density to selected mesh

- UV tools 
  - quickly modify UV shells with rectify and unrap on indevidual axis (WIP)


# Installation Guide

1. Click the **Code** button in the top right of the repo & click **Download ZIP** in the dropdown (Do not unpack the ZIP file)
2. Follow this video for the rest of the simple instructions


https://user-images.githubusercontent.com/105077390/194727061-cd03f3ee-c65c-46f5-bb92-868b0097ccaf.mp4


# To do
  - [ ] Find optimal UI for custom collision 
  - [x] Expose orientation and additional parameters for Custom export 
  - [x] Exspose naming conventions for Load PBR Mat
  - [ ] Fix Unwrap tool for used outside of UV sync=True
  - [x] Restore selection type after context aware Mark UV seam
  - [ ] Add test for non manifold moss cap mesh
  - [ ] Use active selection location instead of world center for pivot to vcol operation
  - [x] Add presets to export
  - [ ] Create Auto UCX
  - [ ] Add Collection quick suffix 
  - [x] add import image as plane operator to TPT when no object is selected
  - [ ] update batch asset library to use the split fuction to get asset tags
  - [ ] reduce the amount of available options on pivot painter to streamline the process
  - [ ] convert multiple custom UV atlas operator into single operator (reference the unwrap operator)
  
  
# original scripts 
  - collision tools : https://github.com/greisane/gret
  - Pivot painter : https://github.com/Gvgeo/Pivot-Painter-for-Blender
  - Vertex animation : https://github.com/JoshRBogart/unreal_tools
  - tex plane tesselation : https://github.com/Pullusb/Tesselate_texture_plane
