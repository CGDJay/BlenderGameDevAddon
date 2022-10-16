import bpy
from pathlib import Path
from bpy.props import PointerProperty,StringProperty,EnumProperty
from bpy.types import PropertyGroup, Panel, Operator,Menu

from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel



AddonName = __package__

AddonName=AddonName.replace('.LoadPBRMat','')

class GameDev_LoadPBRMat_Prop(PropertyGroup):
    ImportDir: StringProperty(name="ImportDir",subtype='DIR_PATH')
    MatName: StringProperty(name="MatName",default='Mat1')
    BaseColorSuffix: StringProperty(name="BaseColorSuffix",default='_D')
    NormalSuffix: StringProperty(name="NormalSuffix",default='_N')
    MaskSuffix: StringProperty(name="MaskSuffix",default='_M')

    FileType: EnumProperty(name="FileType",description='File Format for the auto saves.',
    items={
    ('.png', 'png', 'Save as png'),
    ('.jpg', 'jpg', 'Save as jpg'),
    ('.tga', 'tga', 'Save as tga'),
    },default='.png')

    AOChannel:EnumProperty(name="AOChannel",description='File Format for the auto saves.',
    items={
    ('Red', 'Red', 'Red channel'),
    ('Green', 'Green', 'Green channel'),
    ('Blue', 'Blue', 'Blue channel'),
    },default='Red')

    RougnessChannel: EnumProperty(name="RougnessChannel",description='File Format for the auto saves.',
    items={
    ('Red', 'Red', 'Red channel'),
    ('Green', 'Green', 'Green channel'),
    ('Blue', 'Blue', 'Blue channel'),
    },default='Green')

    MetallicChannel: EnumProperty(name="MetallicChannel",description='File Format for the auto saves.',
    items={
    ('Red', 'Red', 'Red channel'),
    ('Green', 'Green', 'Green channel'),
    ('Blue', 'Blue', 'Blue channel'),
    },default='Blue')


class LoadPBRMat_MT_presets(Menu):
    bl_label = "LoadPBRMat Presets"
    preset_subdir = "loadpbrmat_prop"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class LoadPBRMat_PT_presets(PresetPanel, Panel):
    bl_label = 'LoadPBRMat Presets'
    preset_subdir = 'loadpbrmat_prop_save'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'loadpbrmat.preset_add'


class LoadPBRMat_OT_add_preset(AddPresetBase, Operator):
    bl_idname = "loadpbrmat.preset_add"
    bl_label = "Add a new preset"
    preset_menu = "QuickSuffix_MT_presets"

    # Variable used for all preset values
    preset_defines = ["loadpbrmat_Prop = bpy.context.scene.loadpbrmat_Prop"]

    # Properties to store in the preset
    preset_values = [
        "loadpbrmat_Prop.BaseColorSuffix",
        "loadpbrmat_Prop.NormalSuffix",
        "loadpbrmat_Prop.MaskSuffix",
        "loadpbrmat_Prop.FileType",
        "loadpbrmat_Prop.AOChannel",
        "loadpbrmat_Prop.RougnessChannel",
        "loadpbrmat_Prop.MetallicChannel",
        
    ]

    # Where to store the preset
    preset_subdir = "loadpbrmat_prop_save"



class GameDev_LoadPBRMatPanel(Panel):
    bl_label = "LoadPBRMat"
    bl_idname = "_PT_LoadPBRMat"
    bl_space_type= 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GameDev'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "objectmode"
    def draw_header_preset(self, _context):
        LoadPBRMat_PT_presets.draw_panel_header(self.layout)
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        Prop = scene.loadpbrmat_Prop

        
        row = layout.row()
        layout.label(text="File Suffixes")
        row = layout.row()
        row.prop(Prop, "BaseColorSuffix")
        row.prop(Prop, "MaskSuffix")
        row.prop(Prop, "NormalSuffix")
        row = layout.row()
        row.prop(Prop, "ImportDir")
        row = layout.row()
        row.prop(Prop, "MatName")
        row = layout.row()
        row.prop(Prop, "FileType")
        row = layout.row()
        layout.label(text="Mask Channels")
        row = layout.row()
        row.prop(Prop, "AOChannel")
        row.prop(Prop, "RougnessChannel")
        row.prop(Prop, "MetallicChannel")
        row = layout.row()
        row.operator ("gamedev.load_pbrmat", icon = "IMPORT", text="ImportMat")


class GameDev_LoadPBRMat (Operator):
    bl_idname = "gamedev.load_pbrmat"
    bl_label = "LoadPBRMat"

    def execute(self, context):

        scene = context.scene
        Prop = scene.loadpbrmat_Prop
        BaseColorSuffix=Prop.BaseColorSuffix
        MaskSuffix=Prop.MaskSuffix
        NormalSuffix=Prop.NormalSuffix

        MatName=Prop.MatName

        FileType= str(Prop.FileType)

        print (Prop.FileType)

        myDir = Path(Prop.ImportDir)


        BaseColorPath = [file for file in myDir.iterdir() if file.name.endswith((BaseColorSuffix)+(FileType))]

        if  len(BaseColorPath) == 0 :
            print ("check settings")
            
            raise Exception ('No textures found , check settings and try again')




        mat = bpy.data.materials.new(name=MatName)
        mat.blend_method= 'CLIP'

        mat.use_nodes = True

        bsdf = mat.node_tree.nodes["Principled BSDF"]





        BaseColor = mat.node_tree.nodes.new('ShaderNodeTexImage')

        BaseColor.image = bpy.data.images.load(str(BaseColorPath[0]))
        mat.node_tree.links.new(bsdf.inputs['Alpha'], BaseColor.outputs['Alpha'])



        Mix=mat.node_tree.nodes.new('ShaderNodeMixRGB')
        
        Mix.blend_type = 'DARKEN'

        mat.node_tree.links.new(Mix.inputs['Color1'], BaseColor.outputs['Color'])

        mat.node_tree.links.new(bsdf.inputs['Base Color'], Mix.outputs['Color'])



        Mask = mat.node_tree.nodes.new('ShaderNodeTexImage')

        MaskPath = [file for file in myDir.iterdir() if file.name.endswith((MaskSuffix)+(FileType))]

        Mask.image = bpy.data.images.load(str(MaskPath[0]))

        Mask.image.colorspace_settings.name = 'Raw'

        Sep = mat.node_tree.nodes.new('ShaderNodeSeparateColor')

        mat.node_tree.links.new(Sep.inputs['Color'], Mask.outputs['Color'])

        mat.node_tree.links.new(Mix.inputs['Color2'], Sep.outputs[Prop.AOChannel])

        mat.node_tree.links.new(bsdf.inputs['Roughness'], Sep.outputs[Prop.RougnessChannel])

        mat.node_tree.links.new(bsdf.inputs['Metallic'], Sep.outputs[Prop.MetallicChannel])




        Normal = mat.node_tree.nodes.new('ShaderNodeTexImage')

        NormalPath = [file for file in myDir.iterdir() if file.name.endswith((NormalSuffix)+(FileType))]

        Normal.image = bpy.data.images.load(str(NormalPath[0]))

        Normal.image.colorspace_settings.name = 'Raw'

        NormalS=mat.node_tree.nodes.new('ShaderNodeNormalMap')

        mat.node_tree.links.new(NormalS.inputs['Color'], Normal.outputs['Color'])
        mat.node_tree.links.new(bsdf.inputs['Normal'], NormalS.outputs['Normal'])

        return {'FINISHED'}



classes = ( 


GameDev_LoadPBRMat_Prop,
GameDev_LoadPBRMat,
GameDev_LoadPBRMatPanel,
LoadPBRMat_OT_add_preset,
LoadPBRMat_MT_presets,
LoadPBRMat_PT_presets,


)


def register():
    for cls in classes :
        bpy.utils.register_class(cls)

    bpy.types.Scene.loadpbrmat_Prop = bpy.props.PointerProperty(type=GameDev_LoadPBRMat_Prop)

def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.loadpbrmat_Prop