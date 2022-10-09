from argparse import FileType
from email.policy import default
import bpy
from bpy import context, data, ops
from pathlib import Path
from bpy.props import PointerProperty

class GameDev_LoadPBRMat_Prop(bpy.types.PropertyGroup):
    ImportDir: bpy.props.StringProperty(name="ImportDir",subtype='DIR_PATH')
    MatName: bpy.props.StringProperty(name="MatName",default='Mat1')
    FileType: bpy.props.EnumProperty(name="FileType",description='File Format for the auto saves.',
    items={
    ('.png', 'png', 'Save as png'),
    ('.jpg', 'jpg', 'Save as jpg'),
    ('.tga', 'tga', 'Save as tga'),
    },default='.png')

    AOChannel: bpy.props.EnumProperty(name="AOChannel",description='File Format for the auto saves.',
    items={
    ('Red', 'Red', 'Red channel'),
    ('Green', 'Green', 'Green channel'),
    ('Blue', 'Blue', 'Blue channel'),
    },default='Red')

    RougnessChannel: bpy.props.EnumProperty(name="RougnessChannel",description='File Format for the auto saves.',
    items={
    ('Red', 'Red', 'Red channel'),
    ('Green', 'Green', 'Green channel'),
    ('Blue', 'Blue', 'Blue channel'),
    },default='Green')

    MetallicChannel: bpy.props.EnumProperty(name="MetallicChannel",description='File Format for the auto saves.',
    items={
    ('Red', 'Red', 'Red channel'),
    ('Green', 'Green', 'Green channel'),
    ('Blue', 'Blue', 'Blue channel'),
    },default='Blue')



class GameDev_LoadPBRMatPanel(bpy.types.Panel):
    bl_label = "LoadPBRMat"
    bl_idname = "_PT_LoadPBRMat"
    bl_space_type= 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GameDev'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        Prop = scene.loadpbrmat_Prop

        # Create a simple row.
        layout.label(text="LoadPBRMat")

        row = layout.row()
        row.prop(Prop, "ImportDir")
        row = layout.row()
        row.prop(Prop, "MatName")
        row = layout.row()
        row.prop(Prop, "FileType")
        row = layout.row()
        row.prop(Prop, "AOChannel")
        row.prop(Prop, "RougnessChannel")
        row.prop(Prop, "MetallicChannel")

        
        row = layout.row()
        row.operator ("gamedev.load_pbrmat", icon = "IMPORT", text="ImportMat")





class GameDev_LoadPBRMat (bpy.types.Operator):
    bl_idname = "gamedev.load_pbrmat"
    bl_label = "LoadPBRMat"

    def execute(self, context):

        scene = context.scene
        Prop = scene.loadpbrmat_Prop

        MatName=Prop.MatName

        FileType= str(Prop.FileType)

        print (Prop.FileType)

        myDir = Path(Prop.ImportDir)



        mat = bpy.data.materials.new(name=MatName)

        mat.use_nodes = True

        bsdf = mat.node_tree.nodes["Principled BSDF"]



        BaseColorPath = [file for file in myDir.iterdir() if file.name.endswith('_D'+(FileType))]

        BaseColor = mat.node_tree.nodes.new('ShaderNodeTexImage')

        BaseColor.image = bpy.data.images.load(str(BaseColorPath[0]))




        Mix=mat.node_tree.nodes.new('ShaderNodeMixRGB')

        mat.node_tree.links.new(Mix.inputs['Color1'], BaseColor.outputs['Color'])

        mat.node_tree.links.new(bsdf.inputs['Base Color'], Mix.outputs['Color'])



        Mask = mat.node_tree.nodes.new('ShaderNodeTexImage')

        MaskPath = [file for file in myDir.iterdir() if file.name.endswith('_M'+(FileType))]

        Mask.image = bpy.data.images.load(str(MaskPath[0]))

        Mask.image.colorspace_settings.name = 'Raw'

        Sep = mat.node_tree.nodes.new('ShaderNodeSeparateColor')

        mat.node_tree.links.new(Sep.inputs['Color'], Mask.outputs['Color'])

        mat.node_tree.links.new(Mix.inputs['Color2'], Sep.outputs[Prop.AOChannel])

        mat.node_tree.links.new(bsdf.inputs['Roughness'], Sep.outputs[Prop.RougnessChannel])

        mat.node_tree.links.new(bsdf.inputs['Metallic'], Sep.outputs[Prop.MetallicChannel])




        Normal = mat.node_tree.nodes.new('ShaderNodeTexImage')

        NormalPath = [file for file in myDir.iterdir() if file.name.endswith('_N'+(FileType))]

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




)


def register():
    for cls in classes :
        bpy.utils.register_class(cls)

    bpy.types.Scene.loadpbrmat_Prop = bpy.props.PointerProperty(type=GameDev_LoadPBRMat_Prop)

def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.loadpbrmat_Prop