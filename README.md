# BlenderGameDevAddon
A Blender addon devised to assist in the production of game development

This addon consist of multiple tools developed to streamline the game developement process. 
Some of the tools are adapted/ modified versions of excisting tools from public GNU license repositories


# Mesh Tools

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

  
# original scripts 
  - collision tools : https://github.com/greisane/gret
  - Pivot painter : https://github.com/Gvgeo/Pivot-Painter-for-Blender
  - Vertex animation : https://github.com/JoshRBogart/unreal_tools
  - tex plane tesselation : https://github.com/Pullusb/Tesselate_texture_plane
