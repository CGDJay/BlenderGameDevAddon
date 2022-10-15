from cgitb import text
from msilib.schema import Icon
import bpy
from . import CustomUVTools_op
 

AddonName = __package__

AddonName=AddonName.replace('.CustomUV','')

from bpy.types import (       
        Panel,
        Menu,
        )
        
from bpy.props import (
        StringProperty,
        EnumProperty,
        BoolProperty,
        PointerProperty,
        FloatVectorProperty,
        )



class ColorAtlasTools_panel(Panel):
        bl_space_type = "IMAGE_EDITOR"
        bl_region_type = "UI"
        bl_label = "ColorAtlasTools"
        bl_category = "GameDev"

        @classmethod
        def poll(cls, context):
        

            if bpy.context.preferences.addons[AddonName].preferences.bool_Enable_UVAtlas == True:
                return True
            else:
                return False

        def draw (self, context):
                td = context.scene.CustomUVProps

                layout = self.layout
                row=layout.row()
                row.scale_y = 4
                

                layout.prop(context.scene.CustomUVProps, "AtlasSpace")

                self.layout.label(text="Color Atlas Tools")
                
                row=layout.row()
                col = row.column()
                col.prop(td, 'Texture_Type', expand=False)
                
                row.scale_x = 2
                row.scale_y = 2
                col.operator( "meshuv.atlas_texture" , text="Setup Texture", icon ="TEXTURE")
                row=layout.row()
                row.operator( "meshuv.material_setup" , text="Setup Material", icon ="MATERIAL")
                
                row.operator( "meshuv.clipboardshader" , text="CopyShader", icon ="SCRIPTPLUGINS")



              
class ColorAtlasToolsUV0_panel(Panel):
        bl_space_type = "IMAGE_EDITOR"
        bl_region_type = "UI"
        bl_label = "UV 0 to 1 Controls"
        bl_category = "GameDev"
        bl_options = {'DEFAULT_CLOSED'}

        @classmethod
        def poll(cls, context):
        

            if bpy.context.preferences.addons[AddonName].preferences.bool_Enable_UVAtlas == True:
                return True
            else:
                return False       
        def draw (self, context):

                layout = self.layout



                self.layout.label(icon = "COLLAPSEMENU" , text="UV 0 to 1 Controls")
                
                
                row=layout.row()
                col = row.column()

                row.scale_y = 2
                
                col.operator( "meshuv.set_island" , text="Setup Islands", icon ="HANDLETYPE_VECTOR_VEC")
                row=layout.row()
                row.operator( "meshuv.altas_shift_next" , text="Next Color", icon ="TRIA_RIGHT")
                row.operator( "meshuv.altas_shift_back" , text="Back Color", icon ="TRIA_LEFT")

                row=layout.row() 
                

                row.scale_y = 2
                row.operator( "meshuv.altas_shift_down" , text="Down Gradient", icon ="TRIA_DOWN")
                row.operator( "meshuv.altas_shift_up" , text="Up Gradient", icon ="TRIA_UP")




class CustomUVTools_panel(Panel):
        bl_space_type = "IMAGE_EDITOR"
        bl_region_type = "UI"
        bl_label = "Udim-8 to 7 controls"
        bl_category = "GameDev"
        bl_options = {'DEFAULT_CLOSED'}
               
        @classmethod
        def poll(cls, context):
        
   
            if bpy.context.preferences.addons[AddonName].preferences.bool_Enable_UVAtlas == True:
                return True
            else:
                return False
                           
        def draw (self, context):

                layout = self.layout

                

                row=layout.row()
                
                self.layout.label(icon = "COLLAPSEMENU" , text="Udim -8 to 8 controls")


                row=layout.row()

                row.scale_y = 2
                row.operator( "meshuv.udim_altas_shift_next" , text="Next Color", icon ="TRIA_RIGHT")
                row.operator( "meshuv.udim_altas_shift_back" , text="Back Color", icon ="TRIA_LEFT")

                row=layout.row()
                
                row=layout.row() 
        
                

                row.scale_y = 2
                row.operator( "meshuv.udim_altas_shift_down" , text="Down Gradient", icon ="TRIA_DOWN")
                row.operator( "meshuv.udim_altas_shift_up" , text="Up Gradient", icon ="TRIA_UP")
                row=layout.row()
                

                self.layout.label(icon = "COLLAPSEMENU" , text="Grid Control") 

                row=layout.row() 

                self.layout.label(icon = "COLLAPSEMENU" , text="Posative") 
                row.scale_y = 2
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="0", icon ="COLORSET_03_VEC").target = (.5,.5)

                row=layout.row() 

                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="1", icon ="COLORSET_03_VEC").target = (1.5,.5)
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="2", icon ="COLORSET_03_VEC").target = (2.5,.5)
                
                row=layout.row()
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="3", icon ="COLORSET_03_VEC").target = (3.5,.5)
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="4", icon ="COLORSET_03_VEC").target = (4.5,.5)
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="5", icon ="COLORSET_03_VEC").target = (5.5,.5)
                
                row=layout.row()
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="6", icon ="COLORSET_03_VEC").target = (6.5,.5)
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="7", icon ="COLORSET_03_VEC").target = (7.5,.5)

                row=layout.row()
                row=layout.row()
                self.layout.label(icon = "COLLAPSEMENU" , text="Negative") 
                row=layout.row()

                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="-1", icon ="COLORSET_01_VEC").target = (-1.5,.5)
           
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="-2", icon ="COLORSET_01_VEC").target = (-2.5,.5)
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="-3", icon ="COLORSET_01_VEC").target = (-3.5,.5)
                
                row=layout.row()
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="-4", icon ="COLORSET_01_VEC").target = (-4.5,.5)
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="-5", icon ="COLORSET_01_VEC").target = (-5.5,.5)
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="-6", icon ="COLORSET_01_VEC").target = (-6.5,.5)
                
                row=layout.row()
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="-7", icon ="COLORSET_01_VEC").target = (-7.5,.5)
                row.operator( "meshuv.udim_altas_shift_snap_to_point" , text="-8", icon ="COLORSET_01_VEC").target = (-8.5,.5)




class UI_PT_texel_density_checker(Panel):
    bl_label = "Texel Density"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "GameDev"


    def draw(self, context):
        td = context.scene.CustomUVProps
        
        
        layout = self.layout
        #Split row
        row = layout.row()
        c = row.column()
        row = c.row()
        split = row.split(factor=0.5, align=True)
        c = split.column()

        #----

        layout.label(text="Texture Size:")

        row = layout.row()
        row.prop(td, 'texture_size', expand=False)


        #Split row
        row = layout.row()
        c = row.column()
        row = c.row()
        split = row.split(factor=0.5, align=True)
        c = split.column()
        c.label(text="Set Method:")
        split = split.split()
        c = split.column()
        c.prop(td, 'set_method', expand=False)
        #----

        row = layout.row()
        c = row.column()
        row = c.row()
        split = row.split(factor=0.65, align=True)
        c = split.column()
        c.prop(td, "density_set")
        split = split.split()
        c = split.column()


        c.label(text="px/m")

        layout.operator("tex.texel_density_set", text="Set My TD")
        layout.operator("tex.texel_density_check", text= "Check My TD")
        
        #--Aligner Preset Buttons----
        row = layout.row()
        c = row.column()
        row = c.row()
        split = row.split(factor=0.33, align=True)
        c = split.column()

        c.operator("tex.preset_set", text="2048").TDValue="2048"

        split = split.split(factor=0.5, align=True)
        c = split.column()

        c.operator("tex.preset_set", text="1024").TDValue="1024"
  
        split = split.split()
        c = split.column()

        c.operator("tex.preset_set", text="512").TDValue="512"

        #--Aligner Preset Buttons----
        row = layout.row()
        c = row.column()
        row = c.row()
        split = row.split(factor=0.33, align=True)
        c = split.column()

        c.operator("tex.preset_set", text="256").TDValue="256"

            
        split = split.split(factor=0.5, align=True)
        c = split.column()

        c.operator("tex.preset_set", text="128").TDValue="128" 

        c = split.column()

        c.operator("tex.preset_set", text="64").TDValue="64"


class Tools_panel(Panel):
        bl_space_type = "IMAGE_EDITOR"
        bl_region_type = "UI"
        bl_label = "Tools"
        bl_category = "GameDev"
        bl_options = {'DEFAULT_CLOSED'}
               
        @classmethod
        def poll(cls, context):
        
   
            if bpy.context.preferences.addons[AddonName].preferences.bool_Enable_UVTools == True:
                return True
            else:
                return False
                           
        def draw (self, context):

                layout = self.layout
                self.layout.label(icon = "COLLAPSEMENU" , text="CusotmTools")

                row=layout.row()
                col = row.column()
                
                

                row.scale_y = 2
                row.operator( "uv.customuv_rectify" , text="Rectify UV", icon ="CHECKBOX_DEHLT")
                row=layout.row()
                row.scale_y = 2
                row.operator( "uv.customtools_uv_straighten" , text="Straighten UV", icon ="CHECKBOX_DEHLT")
                
                row=layout.row()
                col = row.column()
                split = col.split(factor=0.75, align=True)
                split.operator(CustomUVTools_op.unwrap.bl_idname, text="Unwrap", icon = ("UNDERLINE")).axis="xy"
                row = split.row(align=True)
                row.operator(CustomUVTools_op.unwrap.bl_idname, text="U").axis="x"
                row.operator(CustomUVTools_op.unwrap.bl_idname, text="V").axis="y"


class VIEW3D_MT_PIE_customUVTools(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "CustomUVtools"
    bl_idname = "_MT_uv.customtools"
    
    def draw(self, context):
        td = context.scene.CustomUVProps
        layout = self.layout

        pie = layout.menu_pie()
        
        
#############################################################
        #type of operators



        col = pie.column()


        col.label (text = "TextureSize:")
        
        
        col.scale_y = 1.5
        col.scale_x = 1

        col.emboss = 'RADIAL_MENU'

        
        row=col.row()
        
        
        row.prop(td, 'texture_size', expand=False)
        row.prop(td, 'texture_size', expand=True , text= td.texture_size)
        
        col.emboss = 'NORMAL'

        col.separator()

        

        col.label (text = "Texel Density")

        col.emboss = 'RADIAL_MENU'
        row=col.row()
        row.operator("tex.preset_set", text="512").TDValue="512"
        row.operator("tex.preset_set", text="1024").TDValue="1024"
        row.operator("tex.preset_set", text="2048").TDValue="2048"



        col = pie.column()
        row = col.row()
        
        col.label (text = "UVTools")

        col.emboss = 'RADIAL_MENU'
        col.scale_y = 2
        col.scale_x = 2

        split = col.split(factor=0.75, align=True)
        
        col.operator("uv.customtools_uv_unwrap")

        row = split.row(align=True)
        # row.operator(CustomUVTools_op.unwrap.bl_idname, text="U").axis="x"
        # row.operator(CustomUVTools_op.unwrap.bl_idname, text="V").axis="y"

        col.emboss = 'NORMAL'

        col.separator()

        col.emboss = 'RADIAL_MENU'
        col.operator("uv.customuv_rectify")

        col.emboss = 'NORMAL'

        col.separator()

        col.emboss = 'RADIAL_MENU'

        col.operator("uv.customuv_markseam")

        
classes = ( 


Tools_panel,
VIEW3D_MT_PIE_customUVTools,
UI_PT_texel_density_checker,
CustomUVTools_panel,
ColorAtlasToolsUV0_panel,
ColorAtlasTools_panel,




)


def register():
    for cls in classes :
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)