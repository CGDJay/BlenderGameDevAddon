import bpy
import os
from bpy.props import PointerProperty,EnumProperty,StringProperty,FloatVectorProperty,BoolProperty
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from bpy.types import Panel, Menu , PropertyGroup , Operator



AddonName = __package__

AddonName=AddonName.replace('.CustomExport','')

class GameDev_Export_Prop(PropertyGroup):
    ExportDir: StringProperty(name="ExportDir",subtype='DIR_PATH')
    TransformOld: FloatVectorProperty(name="TransformOld", default=(0,0,0))
    
    ForwardAxis:EnumProperty(name="ForwardAxis",description='Export Front axis',
    items={
    ('X', 'X', 'X Forward'),
    ('Y', 'Y', 'Y Forward'),
    ('Z', 'Z', 'Z Forward'),
    },default='X')
    UpwardAxis:EnumProperty(name="UpwardAxis",description='Export Front axis',
    items={
    ('X', 'X', 'X Upward'),
    ('Y', 'Y', 'Y Upward'),
    ('Z', 'Z', 'Z Upward'),
    },default='Z')

    CustomProps:BoolProperty(name= 'UseCustomProps', default=False)
    Modifiers:BoolProperty(name= 'UseModifiers', default=True)


class Export_MT_presets(Menu):
    bl_label = "Export Presets"
    preset_subdir = "export_Prop"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class Export_PT_presets(PresetPanel, Panel):
    bl_label = 'Export Presets'
    preset_subdir = 'export_prop_save'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'gamedev_export.preset_add'


class Export_OT_add_preset(AddPresetBase, Operator):
    bl_idname = "gamedev_export.preset_add"
    bl_label = "Add a new preset"
    preset_menu = "Export_MT_presets"

    # Variable used for all preset values
    preset_defines = ["Export_Prop = bpy.context.scene.export_Prop"]

    # Properties to store in the preset
    preset_values = [
        "Export_Prop.ForwardAxis",
        "Export_Prop.UpwardAxis",
        "Export_Prop.CustomProps",
        "Export_Prop.Modifiers",
        
    ]

    # Where to store the preset
    preset_subdir = "export_prop_save"


class GameDev_CustomExportPanel(Panel):
    bl_label = "Custom Export"
    bl_idname = "_PT_CustomExport"
    bl_space_type= 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GameDev'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "objectmode"

    def draw_header_preset(self, _context):
        Export_PT_presets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        Prop = scene.export_Prop


        layout.label(text="CustomExport")

        row = layout.row()
        row.prop(Prop, "ExportDir")

        row = layout.row()
        row.prop(Prop, "ForwardAxis")
        row.prop(Prop, "UpwardAxis")
        row = layout.row()
        row.prop(Prop, "CustomProps")

        
        row = layout.row()
        row.operator ("gmaedev.custom_export", icon = "EXPORT", text="Export")



class GameDev_Export (Operator):
    bl_idname = "gmaedev.custom_export"
    bl_label = "Export"
    
    def execute(self, context):
        
        scene = context.scene
        Export_Prop = scene.export_Prop


        #select parented object

        bpy.ops.object.select_grouped(type='PARENT')


        parentobj=bpy.context.view_layer.objects.active


        #save the original transform

        Export_Prop.TransformOld= parentobj.location


        print ('Old Transform ='+ str(Export_Prop.TransformOld))
        
        
        parentobj.location = (0,0,0)


        #select all objects attached to parent

        objname= parentobj.name

            
        for obj in bpy.data.objects[objname].children:
            bpy.context.view_layer.objects.active = obj
            bpy.context.active_object.select_set(True)
            
            for obj in obj.children:
                bpy.context.view_layer.objects.active = obj
                bpy.context.active_object.select_set(True)

            print (obj.name)
    
            
        parentobj.select_set(True)
           
        print ('Old Transform ='+ str(Export_Prop.TransformOld))  

        #set final export directroy and export 

        fn = os.path.join(Export_Prop.ExportDir, 'SM_'+parentobj.name)


        
           
        bpy.ops.export_scene.fbx(filepath=fn + ".fbx", check_existing=True, filter_glob='*.fbx',
        use_selection=True,apply_unit_scale=True,use_mesh_modifiers=Export_Prop.Modifiers,
        use_mesh_modifiers_render=True, mesh_smooth_type='EDGE', use_subsurf=False,
        use_mesh_edges=False, use_tspace=True, use_triangles=False,
        use_custom_props=Export_Prop.CustomProps, add_leaf_bones=False, bake_anim=True, 
        embed_textures=False, batch_mode='OFF', use_batch_own_dir=False,
        use_metadata=False, axis_forward= Export_Prop.ForwardAxis, axis_up=Export_Prop.UpwardAxis) 


        #apply the original transform
        print ('applying old transform')
        print ('Old Transform ='+ str(Export_Prop.TransformOld))
        parentobj.location = Export_Prop.TransformOld

        return {'FINISHED'}



classes = ( 

GameDev_Export_Prop,
GameDev_CustomExportPanel,
GameDev_Export,
Export_OT_add_preset,
Export_PT_presets,
Export_MT_presets,


)


def register():
    for cls in classes :
        bpy.utils.register_class(cls)

    bpy.types.Scene.export_Prop = bpy.props.PointerProperty(type=GameDev_Export_Prop)

def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.export_Prop