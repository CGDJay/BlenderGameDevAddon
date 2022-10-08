
import code
from fileinput import close
from math import atan2, tan, sin, cos
import math
import pip
from bpy.types import Operator
import bmesh
import bpy, bmesh
from bpy.props import (
        EnumProperty,
        BoolProperty,
        FloatProperty,
        FloatVectorProperty,
        StringProperty,
        EnumProperty,
        BoolProperty,
        IntVectorProperty,
        IntProperty
)
     
import os.path
from mathutils import Vector

from . . common import *
import numpy as np
import pyperclip

from math import hypot
from collections import defaultdict
from . import utilities_uv

import math
from math import copysign
from mathutils import Vector
from collections import defaultdict
from itertools import chain
import mathutils


# reads the shader.txt file and copies contents to clipboard

class ClipboardShader(Operator):
        
	bl_idname = "meshuv.clipboardshader"
	bl_label = "ClipboardShader"
	bl_description = "UE5ShaderCode"

	def execute (self, context):
                script_file = os.path.realpath(__file__)
                directory = os.path.dirname(script_file)
                with open((str(directory) + "\Shader.txt"),"r") as f:
                        shadercode = str(f.read())
                        pyperclip.copy(shadercode)
                        return {'FINISHED'} 
           

class SetIsland_Op(Operator):

        bl_idname = "meshuv.set_island"
        bl_label = "setupisland"
        bl_description = "setup island for use"



        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):

                #scene = context.scene
                #my_settings = scene.my_settings

                

                obj = bpy.context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()

                for f in bm.faces:
                
                        for l in f.loops:
                                if f.select:
                                
                                        l[uv_layer].uv[0]= 0.03
                                        l[uv_layer].uv[1]= 0.97
                                        

                bmesh.update_edit_mesh(obj.data)
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


class LoadTexture(Operator):
        bl_idname = "meshuv.atlas_texture"
        bl_label = "LoadTexture"
        bl_description = "open atlas texture"

         

        def execute (self, context):
                td = bpy.context.scene.ToolSettings

                name=('16X16grid')

                if td.Texture_Type == '0':

                        name = ('16X16grid')
                
                if td.Texture_Type == '1':

                        name = ('16X16gridColor')
                
                if td.Texture_Type == '2':
                        
                        name = ('16X16gridGreyScale')
                        


                pathTexture = os.path.join(os.path.dirname(__file__), "{}.jpg".format(name))
           
                bpy.ops.image.open(filepath=pathTexture, relative_path=False)
                
                bpy.ops.ed.undo_push()
                
                return {'FINISHED'} 


class MaterialSetup(Operator):
        bl_idname = "meshuv.material_setup"
        bl_label = "MaterialSetup"
        bl_description = "SetupAtlasMaterial"

        def execute (self,context):
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace
        
                #Making new material and assigning to active objec
                material_basic = bpy.data.materials.new(name= 'AtlasMaterial')
                material_basic.use_nodes = True
                bpy.context.object.active_material = material_basic

                
                #Adding principle node
                principled_node = material_basic.node_tree.nodes.get ('Principled BSDF')
                
                
                
                #Adding new nodes
                Hue_node = material_basic.node_tree.nodes.new ('ShaderNodeHueSaturation')
                Snap_node = material_basic.node_tree.nodes.new ('ShaderNodeMath')
                Mul_node = material_basic.node_tree.nodes.new ('ShaderNodeMath')
                Sep_node = material_basic.node_tree.nodes.new ('ShaderNodeSeparateXYZ')
                Coord_node = material_basic.node_tree.nodes.new ('ShaderNodeTexCoord')

                principled_node.inputs[0].default_value = (0,0,1,1)
                principled_node.inputs[7].default_value = 0.8
                
                
                #changingnode param
                
                Hue_node.location = (-250,0)
                Hue_node.inputs[4].default_value = (1,0,0,1)
                
                Snap_node.operation = 'SNAP'
                Snap_node.location = (-500,0)
                Snap_node.inputs[1].default_value = (AtlasSpace[1]*0.1)
                
                Mul_node.operation = 'MULTIPLY'
                Mul_node.location = (-750,0)
                Mul_node.inputs[1].default_value = (0.1)
                
                Sep_node.location = (-1000,0)
                
                Coord_node.location = (-1250,0)
                
                
                #linking nodes
                link = material_basic.node_tree.links.new
                
                link(Hue_node.outputs[0],principled_node.inputs[0])
                
                link(Snap_node.outputs[0],Hue_node.inputs[0])
                
                link(Mul_node.outputs[0],Snap_node.inputs[0])
                
                link(Sep_node.outputs[0],Mul_node.inputs[0])
                
                link(Coord_node.outputs[2],Sep_node.inputs[0])


                return {'FINISHED'}


class AtlasShiftNext_Op(Operator):
        bl_idname = "meshuv.altas_shift_next"
        bl_label = "NextColor"
        bl_description = "Next color in atlas"

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):


                obj = context.active_object               
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()
                
                
                
                for f in bm.faces:
                
                        for l in f.loops:
                                        if l[uv_layer].uv[0] > 0.93:
                                                l[uv_layer].uv = (l[uv_layer].uv[0]- 0.9375, (l[uv_layer].uv[1]))
                                                
                                                
                                        else:
                                                if f.select:
                                                        l[uv_layer].uv = (l[uv_layer].uv[0]+ 0.0625, (l[uv_layer].uv[1]))
                bmesh.update_edit_mesh(obj.data)
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


class AtlasShiftBack_Op(Operator):
        bl_idname = "meshuv.altas_shift_back"
        bl_label = "BackColor"
        bl_description = "go backwards in color atlas"

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):

                obj = bpy.context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()

                for f in bm.faces:
                
                        for l in f.loops:
                                if f.select:
                                        if l[uv_layer].uv[0] < 0.07:
                                               l[uv_layer].uv = (l[uv_layer].uv[0]+ 0.9375, (l[uv_layer].uv[1]))
                                                
                                                
                                        else:
                                                l[uv_layer].uv = (l[uv_layer].uv[0]- 0.0625, (l[uv_layer].uv[1]))
                bmesh.update_edit_mesh(obj.data)
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


class AtlasShiftDown_Op(Operator):
        bl_idname = "meshuv.altas_shift_down"
        bl_label = "DownAtlas"
        bl_description = "go down in color atlas"

        @classmethod
        def poll (cls, context):
                
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):

                obj = bpy.context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()

                for f in bm.faces:
                
                        for l in f.loops:
                                if f.select:
                                        if l[uv_layer].uv[1] < 0.07:
                                               l[uv_layer].uv = (l[uv_layer].uv[0], (l[uv_layer].uv[1])+ 0.9375)
                                                
                                                
                                        else:
                                                l[uv_layer].uv = (l[uv_layer].uv[0], (l[uv_layer].uv[1]- 0.0625))
                bmesh.update_edit_mesh(obj.data)
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


class AtlasShiftUp_Op(Operator):
        bl_idname = "meshuv.altas_shift_up"
        bl_label = "UpAtlas"
        bl_description = "go up in color atlas"

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):

                obj = bpy.context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()

                for f in bm.faces:
                
                        for l in f.loops:
                                if f.select:
                                        if l[uv_layer].uv[1] > 0.93:
                                                l[uv_layer].uv = (l[uv_layer].uv[0], (l[uv_layer].uv[1])- 0.9375)
                                                
                                                
                                        else:
                                                l[uv_layer].uv = (l[uv_layer].uv[0], (l[uv_layer].uv[1]+ 0.0625))
                bmesh.update_edit_mesh(obj.data)
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


class UdimAtlasShiftNext_Op(Operator):
        bl_idname = "meshuv.udim_altas_shift_next"
        bl_label = "NextColor"
        bl_description = "Next color in atlas"

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 



                obj = context.active_object               
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()
                
                
                
                for f in bm.faces:
                
                        for l in f.loops:
                                        if l[uv_layer].uv[0] > 7*(AtlasSpace[0]):
                                                l[uv_layer].uv = (l[uv_layer].uv[0]-15*(AtlasSpace[0]), (l[uv_layer].uv[1]))
                                                
                                                
                                        else:
                                                if f.select:
                                                        l[uv_layer].uv = (l[uv_layer].uv[0]+ (AtlasSpace[0]), (l[uv_layer].uv[1]))
                bmesh.update_edit_mesh(obj.data)
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


class UdimAtlasShiftBack_Op(Operator):
        bl_idname = "meshuv.udim_altas_shift_back"
        bl_label = "BackColor"
        bl_description = "go backwards in color atlas"

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 

                obj = bpy.context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()

                for f in bm.faces:
                
                        for l in f.loops:
                                if f.select:
                                        if l[uv_layer].uv[0] < -7*(AtlasSpace[0]):
                                               l[uv_layer].uv = (l[uv_layer].uv[0]+ 15*(AtlasSpace[0]), (l[uv_layer].uv[1]))
                                                
                                                
                                        else:
                                                l[uv_layer].uv = (l[uv_layer].uv[0]-  (AtlasSpace[0]), (l[uv_layer].uv[1]))
                bmesh.update_edit_mesh(obj.data)
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


class UdimAtlasShiftDown_Op(Operator):
        bl_idname = "meshuv.udim_altas_shift_down"
        bl_label = "DownAtlas"
        bl_description = "go down in color atlas"

        @classmethod
        def poll (cls, context):
                
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 

                obj = bpy.context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()

                for f in bm.faces:
                
                        for l in f.loops:
                                if f.select:
                                        if l[uv_layer].uv[1] < -7:
                                               l[uv_layer].uv = (l[uv_layer].uv[0], (l[uv_layer].uv[1])+ 15*(AtlasSpace[1]))
                                                
                                                
                                        else:
                                                l[uv_layer].uv = (l[uv_layer].uv[0], (l[uv_layer].uv[1])- (AtlasSpace[1]))
                bmesh.update_edit_mesh(obj.data)        
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


class UdimAtlasShiftUp_Op(Operator):
        bl_idname = "meshuv.udim_altas_shift_up"
        bl_label = "UpAtlas"
        bl_description = "go up in color atlas"

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 

                obj = bpy.context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()

                for f in bm.faces:
                
                        for l in f.loops:
                                if f.select:
                                        if l[uv_layer].uv[1] > 7:
                                                l[uv_layer].uv = (l[uv_layer].uv[0], (l[uv_layer].uv[1])- 15*(AtlasSpace[1]))
                                                
                                                
                                        else:
                                                l[uv_layer].uv = (l[uv_layer].uv[0], (l[uv_layer].uv[1])+ (AtlasSpace[1]))
                bmesh.update_edit_mesh(obj.data)
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


class UdimAtlasShiftReset_Op(Operator):
        bl_idname = "meshuv.udim_altas_shift_reset"
        bl_label = "UpAtlas"
        bl_description = "go up in color atlas"

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute (self, context):

                obj = bpy.context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                uv_layer = bm.loops.layers.uv.verify()
                coords = []
                
                
                for face in [f for f in bm.faces if f.select]:
                        for loop in face.loops:
                                coords.append(loop[uv_layer].uv)

                                for n, item in enumerate(coords):

                                        subtractX=(n,item.x)
                                        subtractY=(n,item.y)


                
                
                for face in [f for f in bm.faces if f.select]:     
                        for l in face.loops:
                                l[uv_layer].uv = (l[uv_layer].uv[0]-subtractX, (l[uv_layer].uv[1]- subtractY))
                                       
                                                
                                                
                                       
                bmesh.update_edit_mesh(obj.data)
                bpy.ops.ed.undo_push()
                return {'FINISHED'}  


def _get_snap_target_islands(context, bm, uv_layer):
        target_islands = []

        islands = get_island_info_from_bmesh(bm, only_selected=True)

        for isl in islands:
                some_verts_not_selected = False
                for face in isl["faces"]:
                        for l in face["face"].loops:
                                if not context.tool_settings.use_uv_select_sync and \
                                                not l[uv_layer].select:
                                        some_verts_not_selected = True
                                        break
                if not some_verts_not_selected:
                        target_islands.append(isl)

        return target_islands


class UdimAtlasShiftSnapToPoint_Op1(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point1"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(0.5 , 0.5 ),
        )
        

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

    

        

        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 

                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)

              
                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_Op2(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point2"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(1.5,0.5),
        )
        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

    




        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_Op3(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point3"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(2.5, 0.5),
        )
        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False




        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_Op4(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point4"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(3.5, 0.5),
        )

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False
    

        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_Op5(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point5"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(4.5, 0.5),
        )


        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False    




        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_Op6(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point6"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(5.5, 0.5),
        )

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False
    
        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_Op7(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point7"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(6.5, 0.5),
        )


        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False 

        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_Op8(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point8"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(7.5, 0.5),
        )

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False

        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}

class UdimAtlasShiftSnapToPoint_OpMinus1(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point_minus1"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(-0.5, 0.5),
        )


        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False    



        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_OpMinus2(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point_minus2"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(-1.5, 0.5),
        )
        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False
    


        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_OpMinus3(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point_minus3"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(-2.5, 0.5),
        )


        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False    



        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_OpMinus4(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point_minus4"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(-3.5, 0.5),
        )

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False
    


        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_OpMinus5(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point_minus5"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(-4.5, 0.5),
        )

        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False
    


        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_OpMinus6(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point_minus6"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(-5.5, 0.5),
        )


        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False    



        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_OpMinus7(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point_minus7"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(-6.5, 0.5),
        )


        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False    

        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}
class UdimAtlasShiftSnapToPoint_OpMinus8(bpy.types.Operator):


        bl_idname = "meshuv.udim_altas_shift_snap_to_point_minus8"
        bl_label = "Align UV (Snap to Point)"
        bl_description = "Align UV to the target point"
        bl_options = {'REGISTER', 'UNDO'}

        target : FloatVectorProperty(
        name="Snap Target",
        description="Target where UV vertices snap to",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(-7.5, 0.5),
        )


        @classmethod
        def poll (cls, context):
                obj = context.object
                
                
                if obj is not None:
                        if obj.mode == "EDIT":
                                return True
        
                return False
        def execute(self, context):
                objs = get_uv_editable_objects(context)
                AtlasSpace = bpy.context.scene.ToolSettings.AtlasSpace 
                target = Vector (self.target)* Vector(AtlasSpace)


                for obj in objs:
                        bm = bmesh.from_edit_mesh(obj.data)
                        if check_version(2, 73, 0) >= 0:
                                bm.faces.ensure_lookup_table()
                        uv_layer = bm.loops.layers.uv.verify()

 
                target_islands = \
                        _get_snap_target_islands(context, bm, uv_layer)

                for isl in target_islands:
                        ave_uv = Vector((0.0, 0.0))
                        count = 0
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        ave_uv += l[uv_layer].uv
                                        count += 1
                        if count != 0:
                                ave_uv /= count
                        diff = Vector(target) - ave_uv 

                        # Process snap operation.
                        for face in isl["faces"]:
                                for l in face["face"].loops:
                                        l[uv_layer].uv += diff


                bmesh.update_edit_mesh(obj.data)
                return {'FINISHED'}



def Calculate_TD_To_List():
    td = bpy.context.scene.ToolSettings
    calculated_obj_td = []

    #save current mode and active object
    start_active_obj = bpy.context.active_object
    start_mode = bpy.context.object.mode

    #set default values
    Area=0
    gmArea = 0
    textureSizeCurX = 1024
    textureSizeCurY = 1024
    
    #Get texture size from panel
    if td.texture_size == '0':
        textureSizeCurX = 512
        textureSizeCurY = 512
    if td.texture_size == '1':
        textureSizeCurX = 1024
        textureSizeCurY = 1024
    if td.texture_size == '2':
        textureSizeCurX = 2048
        textureSizeCurY = 2048
    if td.texture_size == '3':
        textureSizeCurX = 4096
        textureSizeCurY = 4096


    if textureSizeCurX < 1 or textureSizeCurY < 1:
        textureSizeCurX = 1024
        textureSizeCurY = 1024

    bpy.ops.object.mode_set(mode='OBJECT')

    face_count = len(bpy.context.active_object.data.polygons)

    #Duplicate and Triangulate Object
    bpy.ops.object.duplicate()
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    aspectRatio = textureSizeCurX / textureSizeCurY;
    if aspectRatio < 1:
        aspectRatio = 1 / aspectRatio
    largestSide = textureSizeCurX if textureSizeCurX > textureSizeCurY else textureSizeCurY;

    #get bmesh from active object		
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
    bm.faces.ensure_lookup_table()
    
    for x in range(0, face_count):
        Area = 0
        #UV Area calculating
        #get uv-coordinates of verteces of current triangle
        for trisIndex in range(0, len(bm.faces[x].loops) - 2):
            loopA = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
            loopB = bm.faces[x].loops[trisIndex + 1][bm.loops.layers.uv.active].uv
            loopC = bm.faces[x].loops[trisIndex + 2][bm.loops.layers.uv.active].uv
            #get multiplication of vectors of current triangle
            multiVector = Vector2dMultiple(loopA, loopB, loopC)
            #Increment area of current tri to total uv area
            Area += 0.5 * multiVector

        gmArea = bpy.context.active_object.data.polygons[x].area

        #TexelDensity calculating from selected in panel texture size
        if gmArea > 0 and Area > 0:
            texelDensity = ((largestSide / math.sqrt(aspectRatio)) * math.sqrt(Area))/(math.sqrt(gmArea)*100) / bpy.context.scene.unit_settings.scale_length
        else:
            texelDensity = 0.001

        #show calculated values on panel
        if td.units == '0':
            texelDensity = '%.3f' % round(texelDensity, 3)
        if td.units == '1':
            texelDensity = '%.3f' % round(texelDensity*100, 3)
        if td.units == '2':
            texelDensity = '%.3f' % round(texelDensity*2.54, 3)
        if td.units == '3':
            texelDensity = '%.3f' % round(texelDensity*30.48, 3)

        calculated_obj_td.append(float(texelDensity))

    #delete duplicated object
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.delete()
    bpy.context.view_layer.objects.active = start_active_obj
    
    bpy.ops.object.mode_set(mode=start_mode)

    return calculated_obj_td



def Vector2dMultiple(A, B, C):
    return abs((B[0]- A[0])*(C[1]- A[1])-(B[1]- A[1])*(C[0]- A[0]))



def SyncUVSelection():
    mesh = bpy.context.active_object.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.active
    uv_selected_faces = []
    face_count = len(bm.faces)

    
    #mark selected faces as face_is_selected True
    for faceid in range (face_count):
        face_is_selected = True
        for loop in bm.faces[faceid].loops:
            if not(loop[uv_layer].select):
                face_is_selected = False
    
        if face_is_selected and bm.faces[faceid].select:
            uv_selected_faces.append(faceid)
    
    #deselect all faces
    for faceid in range (face_count):
        for loop in bm.faces[faceid].loops:
            loop[uv_layer].select = False


    #select all faces with face_is_selected True
    for faceid in uv_selected_faces:
        for loop in bm.faces[faceid].loops:
            loop[uv_layer].select = True



        
    for id in uv_selected_faces:
        bm.faces[id].select_set(True)

    bmesh.update_edit_mesh(mesh)



#-------------------------------------------------------
class Texel_Density_Check(Operator):
    """Check Density"""
    bl_idname = "tex.texel_density_check"
    bl_label = "Check Texel Density"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        td = context.scene.ToolSettings
        
        #save current mode and active object
        start_active_obj = bpy.context.active_object
        start_selected_obj = bpy.context.selected_objects
        start_mode = bpy.context.object.mode

        #set default values
        Area=0
        gmArea = 0
        textureSizeCurX = 1024
        textureSizeCurY = 1024
        
        #Get texture size from panel
        if td.texture_size == '0':
            textureSizeCurX = 512
            textureSizeCurY = 512
        if td.texture_size == '1':
            textureSizeCurX = 1024
            textureSizeCurY = 1024
        if td.texture_size == '2':
            textureSizeCurX = 2048
            textureSizeCurY = 2048
        if td.texture_size == '3':
            textureSizeCurX = 4096
            textureSizeCurY = 4096


        if textureSizeCurX < 1 or textureSizeCurY < 1:
            textureSizeCurX = 1024
            textureSizeCurY = 1024

        aspectRatio = textureSizeCurX / textureSizeCurY;
        if aspectRatio < 1:
            aspectRatio = 1 / aspectRatio
        largestSide = textureSizeCurX if textureSizeCurX > textureSizeCurY else textureSizeCurY;

        bpy.ops.object.mode_set(mode='OBJECT')

        for o in start_selected_obj:
            bpy.ops.object.select_all(action='DESELECT')
            if o.type == 'MESH' and len(o.data.uv_layers) > 0:
                o.select_set(True)
                bpy.context.view_layer.objects.active = o
                #Duplicate and Triangulate Object
                bpy.ops.object.duplicate()
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

                bpy.ops.object.mode_set(mode='EDIT')
                
                #Select All Polygons if Calculate TD per Object
                if start_mode == 'OBJECT':
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.reveal()
                    bpy.ops.mesh.select_all(action='SELECT')

                if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and bpy.context.scene.tool_settings.use_uv_select_sync == False:
                    SyncUVSelection()

                #Get selected list of selected polygons
                bpy.ops.object.mode_set(mode='OBJECT')
                face_count = len(bpy.context.active_object.data.polygons)
                selected_faces = []
                for faceid in range (0, face_count):
                    if bpy.context.active_object.data.polygons[faceid].select == True:
                        selected_faces.append(faceid)
                
                #get bmesh from active object		
                bpy.ops.object.mode_set(mode='EDIT')
                bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
                bm.faces.ensure_lookup_table()
                for x in selected_faces:
                    #set default values for multiplication of vectors (uv and physical area of object)
                    localArea = 0
                    #UV Area calculating
                    #get uv-coordinates of verteces of current triangle
                    for trisIndex in range(0, len(bm.faces[x].loops) - 2):
                        loopA = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
                        loopB = bm.faces[x].loops[trisIndex + 1][bm.loops.layers.uv.active].uv
                        loopC = bm.faces[x].loops[trisIndex + 2][bm.loops.layers.uv.active].uv
                        #get multiplication of vectors of current triangle
                        multiVector = Vector2dMultiple(loopA, loopB, loopC)
                        #Increment area of current tri to total uv area
                        localArea += 0.5 * multiVector

                    gmArea += bpy.context.active_object.data.polygons[x].area
                    Area += localArea

                #delete duplicated object
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.delete()

        #Calculate TD and Display Value
        if Area > 0:
            #UV Area in percents
            UVspace = Area * 100
            
            #TexelDensity calculating from selected in panel texture size
            if gmArea > 0:
                TexelDensity = ((largestSide / math.sqrt(aspectRatio)) * math.sqrt(Area))/(math.sqrt(gmArea)*100) / bpy.context.scene.unit_settings.scale_length
            else:
                TexelDensity = 0.001
                

        

            #show calculated values on panel
            td.uv_space = '%.0f' % round(UVspace, ) + ' %'
            td.density = '%.0f' % round(TexelDensity*100, )

 
                

            self.report({'INFO'}, "TD is Calculated")

        else:
            self.report({'INFO'}, "No faces selected")

        #Select Objects Again
        for x in start_selected_obj:
                x.select_set(True)
                bpy.context.view_layer.objects.active = start_active_obj
                bpy.ops.object.mode_set(mode=start_mode)
        print (TexelDensity)
        td.density_set = (td.density)

        return {'FINISHED'}


#-------------------------------------------------------
class Texel_Density_Set(Operator):
    """Set Density"""
    bl_idname = "tex.texel_density_set"
    bl_label = "Set Texel Density"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        td = context.scene.ToolSettings

        #save current mode and active object
        start_active_obj = bpy.context.active_object
        start_selected_obj = bpy.context.selected_objects
        start_mode = bpy.context.object.mode

        #Get Value for TD Set
        destiny_set_filtered = td.density_set.replace(',', '.')
        try:
            densityNewValue = float(destiny_set_filtered)
            if densityNewValue < 0.0001:
                densityNewValue = 0.0001
        except:
            self.report({'INFO'}, "Density value is wrong")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='OBJECT')

        for o in start_selected_obj:
            bpy.ops.object.select_all(action='DESELECT')
            if o.type == 'MESH' and len(o.data.uv_layers) > 0:
                o.select_set(True)
                bpy.context.view_layer.objects.active = o

                #save start selected in 3d view faces
                start_selected_faces = []
                for faceid in range (0, len(o.data.polygons)):
                    if bpy.context.active_object.data.polygons[faceid].select == True:
                        start_selected_faces.append(faceid)

                bpy.ops.object.mode_set(mode='EDIT')

                #If Set TD from UV Editor sync selection
                if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and bpy.context.scene.tool_settings.use_uv_select_sync == False:
                    SyncUVSelection()

                #Select All Polygons if Calculate TD per Object
                if start_mode == 'OBJECT':
                    bpy.ops.mesh.reveal()
                    bpy.ops.mesh.select_all(action='SELECT')

                #Get current TD Value from object or faces
                bpy.ops.tex.texel_density_check()
                densityCurrentValue = float(td.density)
                if densityCurrentValue < 0.0001:
                    densityCurrentValue = 0.0001

                scaleFac = densityNewValue/densityCurrentValue
                #check opened image editor window
                IE_area = 0
                flag_exist_area = False
                for area in range(len(bpy.context.screen.areas)):
                    if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR':
                        IE_area = area
                        flag_exist_area = True
                        bpy.context.screen.areas[area].type = 'CONSOLE'
                
                bpy.context.area.type = 'IMAGE_EDITOR'
                
                if bpy.context.area.spaces[0].image != None:
                    if bpy.context.area.spaces[0].image.name == 'Render Result':
                        bpy.context.area.spaces[0].image = None
                
                if bpy.context.space_data.mode != 'UV':
                    bpy.context.space_data.mode = 'UV'
                
                if bpy.context.scene.tool_settings.use_uv_select_sync == False:
                    bpy.ops.uv.select_all(action = 'SELECT')
                
                bpy.ops.transform.resize(value=(scaleFac, scaleFac, 1))
                if td.set_method == '0':
                    bpy.ops.uv.average_islands_scale()
                bpy.context.area.type = 'VIEW_3D'
                
                if flag_exist_area == True:
                    bpy.context.screen.areas[IE_area].type = 'IMAGE_EDITOR'

                bpy.ops.mesh.select_all(action='DESELECT')

                bpy.ops.object.mode_set(mode='OBJECT')
                for faceid in start_selected_faces:
                    bpy.context.active_object.data.polygons[faceid].select = True

        #Select Objects Again
        for x in start_selected_obj:
            x.select_set(True)
        bpy.context.view_layer.objects.active = start_active_obj
        bpy.ops.object.mode_set(mode=start_mode)

        bpy.ops.tex.texel_density_check()

        return {'FINISHED'}
        

#-------------------------------------------------------
class Calculated_To_Set(Operator):
    """Copy Calc to Set"""
    bl_idname = "tex.calculate_to_set"
    bl_label = "Set Texel Density"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        td = context.scene.ToolSettings
        
        td.density_set = td.density
        
        return {'FINISHED'}
 
        
#-------------------------------------------------------
class Preset_Set(Operator):
    """Preset Set Density"""
    bl_idname = "tex.preset_set"
    bl_label = "Set Texel Density"
    bl_options = {'REGISTER', 'UNDO'}
    TDValue: StringProperty()
    
    def execute(self, context):
        td = context.scene.ToolSettings
        
        td.density_set = self.TDValue
        bpy.ops.tex.texel_density_set()
                
        return {'FINISHED'}
        






precision = 3



class Rectify(bpy.types.Operator):
	bl_idname = "uv.customuv_rectify"
	bl_label = "Rectify"
	bl_description = "Align selected faces or verts to rectangular distribution."
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False
		if bpy.context.active_object.mode != 'EDIT':
			return False
		if bpy.context.active_object.type != 'MESH':
			return False
		if not bpy.context.active_object.data.uv_layers:
			return False
		return True


	def execute(self, context):
                
                if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and bpy.context.scene.tool_settings.use_uv_select_sync == False:
                        SyncUVSelection()
                        utilities_uv.multi_object_loop(rectify, self, context)
                        bpy.context.scene.tool_settings.use_uv_select_sync = True

                        return {'FINISHED'}
                else:
                        
                        utilities_uv.multi_object_loop(rectify, self, context)
                        bpy.context.scene.tool_settings.use_uv_select_sync = True

                        return {'FINISHED'}



def rectify(self, context, me=None, bm=None, uv_layers=None):
        if me is None:
                me = bpy.context.active_object.data
                bm = bmesh.from_edit_mesh(me)
                uv_layers = bm.loops.layers.uv.verify()

        # Store selection
        faces_loops = utilities_uv.selection_store(bm, uv_layers, return_selected_faces_loops=True)

        # Find selection islands
        islands = utilities_uv.splittedSelectionByIsland( bm, uv_layers, set(faces_loops.keys()) )

        for island in islands:
                bpy.ops.uv.select_all(action='DESELECT')
                utilities_uv.set_selected_faces(island, bm, uv_layers)
                rectmain(me, bm, uv_layers, island, faces_loops)

        # Restore selection
        utilities_uv.selection_restore(bm, uv_layers)
        



def rectmain(me, bm, uv_layers, selFacesMix, faces_loops, return_discarded_faces=False):

	filteredVerts, selFaces, vertsDict, discarded_faces = ListsOfVerts(bm, uv_layers, selFacesMix, faces_loops)   

	if len(filteredVerts) < 2:
		if return_discarded_faces:
			return set()
		return

	if not selFaces:
		if discarded_faces:
			if return_discarded_faces:
				return discarded_faces
		else:
			# Line is selected -> align on axis
			for luv in filteredVerts:
				x = round(luv.uv.x, precision)
				y = round(luv.uv.y, precision)
				if luv not in vertsDict[(x, y)]:
					vertsDict[(x, y)].append(luv)

			areLinedX = True
			areLinedY = True
			allowedError = 0.00001
			valX = filteredVerts[0].uv.x
			valY = filteredVerts[0].uv.y
			for v in filteredVerts:
				if abs(valX - v.uv.x) > allowedError:
					areLinedX = False
				if abs(valY - v.uv.y) > allowedError:
					areLinedY = False
			
			if not (areLinedX or areLinedY):
				verts = filteredVerts
				verts.sort(key=lambda x: x.uv[0])	#sort by .x
				first = verts[0]
				last = verts[len(verts)-1]

				horizontal = True
				if ((last.uv.x - first.uv.x) > 0.0009):
					slope = (last.uv.y - first.uv.y)/(last.uv.x - first.uv.x)
					if (slope > 1) or (slope <-1):
						horizontal = False 
				else:
					horizontal = False
				
				if horizontal == True:
					#scale to 0 on Y
					for v in verts:
						x = round(v.uv.x, precision)
						y = round(v.uv.y, precision)
						for luv in vertsDict[(x, y)]:
							luv.uv.y = first.uv.y
				else:
					#scale to 0 on X
					verts.sort(key=lambda x: x.uv[1])	#sort by .y
					verts.reverse()	#reverse because y values drop from up to down
					first = verts[0]
					last = verts[len(verts)-1]

					for v in verts:
						x = round(v.uv.x, precision)
						y = round(v.uv.y, precision)
						for luv in vertsDict[(x, y)]:
							luv.uv.x = first.uv.x

	else:
		# At least one face is selected -> rectify
		targetFace = bm.faces.active
		# Active face checks
		if targetFace is None or len({loop for loop in targetFace.loops}.intersection(filteredVerts)) != len(targetFace.verts) or targetFace.select == False or len(targetFace.verts) != 4:
			targetFace = selFaces[0]
		
		ShapeFace(uv_layers, targetFace, vertsDict)
		
		FollowActiveUV(me, targetFace, selFaces)

		bmesh.update_edit_mesh(me, loop_triangles=False)

		if return_discarded_faces:
			return discarded_faces



def ListsOfVerts(bm, uv_layers, selFacesMix, faces_loops):
	allEdgeVerts = []
	filteredVerts = []
	selFaces = []
	discarded_faces = set()
	vertsDict = defaultdict(list)
	
	for f in selFacesMix:
		isFaceSel = True
		facesEdgeVerts = [l[uv_layers] for l in faces_loops[f]]
		if len(faces_loops[f]) < len(f.loops):
			isFaceSel = False
		
		allEdgeVerts.extend(facesEdgeVerts)
		if isFaceSel:
			if len(f.verts) != 4:
				filteredVerts.extend(facesEdgeVerts)
				discarded_faces.add(f)
			else: 
				selFaces.append(f)
				for luv in facesEdgeVerts:
					x = round(luv.uv.x, precision)
					y = round(luv.uv.y, precision)
					vertsDict[(x, y)].append(luv)
		else:
			filteredVerts.extend(facesEdgeVerts)

	if len(filteredVerts) == 0:
		filteredVerts.extend(allEdgeVerts)

	return filteredVerts, selFaces, vertsDict, discarded_faces



def ShapeFace(uv_layers, targetFace, vertsDict):
	corners = []
	for l in targetFace.loops:
		luv = l[uv_layers]
		corners.append(luv)
	
	if len(corners) != 4:
		return
	
	firstHighest = corners[0]
	for c in corners:
		if c.uv.y > firstHighest.uv.y:
			firstHighest = c    
	corners.remove(firstHighest)
	
	secondHighest = corners[0]
	for c in corners:
		if (c.uv.y > secondHighest.uv.y):
			secondHighest = c
	
	if firstHighest.uv.x < secondHighest.uv.x:
		leftUp = firstHighest
		rightUp = secondHighest
	else:
		leftUp = secondHighest
		rightUp = firstHighest
	corners.remove(secondHighest)
	
	firstLowest = corners[0]
	secondLowest = corners[1]
	
	if firstLowest.uv.x < secondLowest.uv.x:
		leftDown = firstLowest
		rightDown = secondLowest
	else:
		leftDown = secondLowest
		rightDown = firstLowest
	

	verts = [leftUp, leftDown, rightDown, rightUp]

	ratioX, ratioY = ImageRatio()
	min = float('inf')
	minV = verts[0]
	for v in verts:
		if v is None:
			continue
		for area in bpy.context.screen.areas:
			if area.type == 'IMAGE_EDITOR':
				loc = area.spaces[0].cursor_location
				hyp = hypot(loc.x/ratioX -v.uv.x, loc.y/ratioY -v.uv.y)
				if (hyp < min):
					min = hyp
					minV = v

	MakeUvFaceEqualRectangle(vertsDict, leftUp, rightUp, rightDown, leftDown, minV)



def MakeUvFaceEqualRectangle(vertsDict, leftUp, rightUp, rightDown, leftDown, startv):
	ratioX, ratioY = ImageRatio()
	ratio = ratioX/ratioY
	
	if startv is None: startv = leftUp.uv
	elif AreVertsQuasiEqual(startv, rightUp): startv = rightUp.uv
	elif AreVertsQuasiEqual(startv, rightDown): startv = rightDown.uv
	elif AreVertsQuasiEqual(startv, leftDown): startv = leftDown.uv
	else: startv = leftUp.uv
	
	leftUp = leftUp.uv
	rightUp = rightUp.uv
	rightDown = rightDown.uv
	leftDown = leftDown.uv    
   
	if (startv == leftUp): 
		finalScaleX = hypotVert(leftUp, rightUp)
		finalScaleY = hypotVert(leftUp, leftDown)
		currRowX = leftUp.x
		currRowY = leftUp.y
	
	elif (startv == rightUp):
		finalScaleX = hypotVert(rightUp, leftUp)
		finalScaleY = hypotVert(rightUp, rightDown)
		currRowX = rightUp.x - finalScaleX
		currRowY = rightUp.y
	   
	elif (startv == rightDown):
		finalScaleX = hypotVert(rightDown, leftDown)
		finalScaleY = hypotVert(rightDown, rightUp)
		currRowX = rightDown.x - finalScaleX
		currRowY = rightDown.y + finalScaleY
		
	else:
		finalScaleX = hypotVert(leftDown, rightDown)
		finalScaleY = hypotVert(leftDown, leftUp)
		currRowX = leftDown.x
		currRowY = leftDown.y +finalScaleY
	
	#leftUp, rightUp
	x = round(leftUp.x, precision)
	y = round(leftUp.y, precision)
	for v in vertsDict[(x,y)]:
		v.uv.x = currRowX
		v.uv.y = currRowY
  
	x = round(rightUp.x, precision)
	y = round(rightUp.y, precision)
	for v in vertsDict[(x,y)]:
		v.uv.x = currRowX + finalScaleX
		v.uv.y = currRowY
	
	#rightDown, leftDown
	x = round(rightDown.x, precision)
	y = round(rightDown.y, precision)    
	for v in vertsDict[(x,y)]:
		v.uv.x = currRowX + finalScaleX
		v.uv.y = currRowY - finalScaleY
		
	x = round(leftDown.x, precision)
	y = round(leftDown.y, precision)    
	for v in vertsDict[(x,y)]:
		v.uv.x = currRowX
		v.uv.y = currRowY - finalScaleY



def FollowActiveUV(me, f_act, faces):
	bm = bmesh.from_edit_mesh(me)
	uv_act = bm.loops.layers.uv.active
	
	# our own local walker
	def walk_face_init(faces, f_act):
		# first tag all faces True (so we dont uvmap them)
		for f in bm.faces:
			f.tag = True
		# then tag faces arg False
		for f in faces:
			f.tag = False
		# tag the active face True since we begin there
		f_act.tag = True

	def walk_face(f):
		# all faces in this list must be tagged
		f.tag = True
		faces_a = [f]
		faces_b = []

		while faces_a:
			for f in faces_a:
				for l in f.loops:
					l_edge = l.edge
					if l_edge.is_manifold == True and l_edge.seam == False:
						l_other = l.link_loop_radial_next
						f_other = l_other.face
						if not f_other.tag:
							yield (f, l, f_other)
							f_other.tag = True
							faces_b.append(f_other)
			# swap
			faces_a, faces_b = faces_b, faces_a
			faces_b.clear()

	def walk_edgeloop(l):
		"""
		Could make this a generic function
		"""
		e_first = l.edge
		e = None
		while True:
			e = l.edge
			yield e

			# don't step past non-manifold edges
			if e.is_manifold:
				# walk around the quad and then onto the next face
				l = l.link_loop_radial_next
				if len(l.face.verts) == 4:
					l = l.link_loop_next.link_loop_next
					if l.edge is e_first:
						break
				else:
					break
			else:
				break

	def extrapolate_uv(fac,
					   l_a_outer, l_a_inner,
					   l_b_outer, l_b_inner):
		l_b_inner[:] = l_a_inner
		l_b_outer[:] = l_a_inner + ((l_a_inner - l_a_outer) * fac)

	def apply_uv(f_prev, l_prev, f_next):
		l_a = [None, None, None, None]
		l_b = [None, None, None, None]

		l_a[0] = l_prev
		l_a[1] = l_a[0].link_loop_next
		l_a[2] = l_a[1].link_loop_next
		l_a[3] = l_a[2].link_loop_next

		#  l_b
		#  +-----------+
		#  |(3)        |(2)
		#  |           |
		#  |l_next(0)  |(1)
		#  +-----------+
		#        ^
		#  l_a   |
		#  +-----------+
		#  |l_prev(0)  |(1)
		#  |    (f)    |
		#  |(3)        |(2)
		#  +-----------+
		#  copy from this face to the one above.

		# get the other loops
		l_next = l_prev.link_loop_radial_next
		if l_next.vert != l_prev.vert:
			l_b[1] = l_next
			l_b[0] = l_b[1].link_loop_next
			l_b[3] = l_b[0].link_loop_next
			l_b[2] = l_b[3].link_loop_next
		else:
			l_b[0] = l_next
			l_b[1] = l_b[0].link_loop_next
			l_b[2] = l_b[1].link_loop_next
			l_b[3] = l_b[2].link_loop_next

		l_a_uv = [l[uv_act].uv for l in l_a]
		l_b_uv = [l[uv_act].uv for l in l_b]

		try:
			fac = edge_lengths[l_b[2].edge.index][0] / edge_lengths[l_a[1].edge.index][0]
		except ZeroDivisionError:
			fac = 1.0

		extrapolate_uv(fac,
					   l_a_uv[3], l_a_uv[0],
					   l_b_uv[3], l_b_uv[0])

		extrapolate_uv(fac,
					   l_a_uv[2], l_a_uv[1],
					   l_b_uv[2], l_b_uv[1])


	# Calculate average length per loop if needed
	bm.edges.index_update()
	edge_lengths = [None]*len(bm.edges)
	
	for f in faces:
		# we know its a quad
		l_quad = f.loops[:] 
		l_pair_a = (l_quad[0], l_quad[2])
		l_pair_b = (l_quad[1], l_quad[3])

		for l_pair in (l_pair_a, l_pair_b):
			if edge_lengths[l_pair[0].edge.index] is None:

				edge_length_store = [-1.0]
				edge_length_accum = 0.0
				edge_length_total = 0

				for l in l_pair:
					if edge_lengths[l.edge.index] is None:
						for e in walk_edgeloop(l):
							if edge_lengths[e.index] is None:
								edge_lengths[e.index] = edge_length_store
								edge_length_accum += e.calc_length()
								edge_length_total += 1

				edge_length_store[0] = edge_length_accum / edge_length_total


	walk_face_init(faces, f_act)
	for f_triple in walk_face(f_act):
		apply_uv(*f_triple)



def ImageRatio():
	ratioX, ratioY = 256,256
	for a in bpy.context.screen.areas:
		if a.type == 'IMAGE_EDITOR':
			img = a.spaces[0].image
			if img and img.size[0] != 0:
				ratioX, ratioY = img.size[0], img.size[1]
			break
	return ratioX, ratioY



def AreVertsQuasiEqual(v1, v2, allowedError = 0.00001):
	if abs(v1.uv.x -v2.uv.x) < allowedError and abs(v1.uv.y -v2.uv.y) < allowedError:
		return True
	return False



def hypotVert(v1, v2):
	hyp = hypot(v1.x - v2.x, v1.y - v2.y)
	return hyp








class unwrap(bpy.types.Operator):
    bl_idname = "uv.customtools_uv_unwrap"
    bl_label = "Unwrap"
    bl_description = "Unwrap selected uv's"
    bl_options = {'UNDO'}
    

    axis: bpy.props.StringProperty(name="axis", default="xy")

    @classmethod
    def poll(cls, context):
        

        if not bpy.context.active_object:
            return False
        if bpy.context.active_object.mode != 'EDIT':
            return False
        if bpy.context.active_object.type != 'MESH':
            return False

        if not bpy.context.object.data.uv_layers:
            return False

        return True

    def execute(self, context):
        

        if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and bpy.context.scene.tool_settings.use_uv_select_sync == False:
                SyncUVSelection()
                
                utilities_uv.multi_object_loop(unwrapmain, context, self.axis)
                bpy.context.scene.tool_settings.use_uv_select_sync = True
                bpy.ops.uv.pack_islands(margin=0.00390625)

        else:
                bpy.context.scene.tool_settings.use_uv_select_sync = False
                bpy.ops.uv.select_all(action='SELECT')
                utilities_uv.multi_object_loop(unwrapmain, context, self.axis)
                bpy.context.scene.tool_settings.use_uv_select_sync = True
                bpy.ops.uv.pack_islands(margin=0.00390625)


        return {'FINISHED'}


def get_padding(td):

    return td.padding / 1024



def unwrapmain(context, axis):
    td = context.scene.ToolSettings



    # print("operator_uv_unwrap()")

    bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
    uv_layer = bm.loops.layers.uv.verify()



    selected_faces = utilities_uv.selection_store(return_selected_UV_faces=True)

    # analyze if a full uv-island has been selected
    full_islands = utilities_uv.getSelectionIslands(bm, uv_layer, selected_faces)
    islands = utilities_uv.splittedSelectionByIsland(bm, uv_layer, selected_faces)

    selected_uv_islands = []
    for island in islands:
        for full_island in full_islands:
            if island == full_island:
                selected_uv_islands.append(list(island))

    utilities_uv.selection_restore()

    # store pins and edge seams
    edge_seam = []
    for edge in bm.edges:
        edge_seam.append(edge.seam)
        edge.seam = False

    # Pin the inverse of the current selection, and cache the uv coords
    pin_state = []
    uv_coords = []
    for face in bm.faces:
        for loop in face.loops:
            uv = loop[uv_layer]
            pin_state.append(uv.pin_uv)
            uv.pin_uv = not uv.select

            uv_coords.append(uv.uv.copy())

    # pin one vert to keep the island somewhat in place, otherwise it can get moved away quite randomly by the uv unwrap method
    # also store some uvs data to reconstruction orientation
    orient_uvs = []
    if len(selected_uv_islands) > 0:
        for island in selected_uv_islands:
            
            x_min = x_max = y_min = y_max = island[0].loops[0][uv_layer]
            x_min.pin_uv = True

            for face in island:
                for loop in face.loops:
                    uv = loop[uv_layer]
                    if uv.uv.x > x_max.uv.x:
                        x_max = uv
                    if uv.uv.x < x_min.uv.x:
                        x_min = uv
                    if uv.uv.y > y_max.uv.y:
                        y_max = uv
                    if uv.uv.y < y_min.uv.y:
                        y_min = uv
            
            orient_uvs.append((x_min, x_max, y_min, y_max, x_min.uv.copy(), x_max.uv.copy(), y_min.uv.copy(), y_max.uv.copy()))

    # apply unwrap
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.seams_from_islands()

    padding = get_padding(td)
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=padding)

    # try to reconstruct the original orientation of the uvisland
    up = mathutils.Vector((0, 1.0))
    for index, island in enumerate(selected_uv_islands):
        island_bbox = utilities_uv.get_BBOX(island, bm, uv_layer)

        x_min, x_max, y_min, y_max, x_min_coord, x_max_coord, y_min_coord, y_max_coord = orient_uvs[index]
    
        intial_x_axis = x_min_coord - x_max_coord       
        intial_x_angle = up.angle_signed(intial_x_axis)

        axis_x_current = x_min.uv - x_max.uv
        current_x_angle = up.angle_signed(axis_x_current)

        intial_y_axis = y_min_coord - y_max_coord       
        intial_y_angle = up.angle_signed(intial_y_axis)

        axis_y_current = y_min.uv - y_max.uv
        current_y_angle = up.angle_signed(axis_y_current)

        angle_x = current_x_angle - intial_x_angle
        angle_y = current_y_angle - intial_y_angle
        angle = min(angle_x, angle_y)

        center = island_bbox['center']
        utilities_uv.rotate_island(island, uv_layer, angle, center.x, center.y)

        #keep it the same size
        scale_x = intial_x_axis.length / axis_x_current.length 
        scale_y = intial_y_axis.length / axis_y_current.length 
        scale  = min([scale_x, scale_y], key=lambda x:abs(x-1.0)) #pick scale closer to 1.0
        utilities_uv.scale_island(island, uv_layer, scale, scale, center)

        #move back into place
        delta = x_min_coord - x_min.uv
        utilities_uv.move_island(island, delta.x, delta.y)

    # restore selections, pins & edge seams
    index = 0
    for face in bm.faces:
        for loop in face.loops:
            uv = loop[uv_layer]
            uv.pin_uv = pin_state[index]

            #apply axis constraint
            if axis == "x":
                uv.uv.y = uv_coords[index].y
            elif axis == "y":
                uv.uv.x = uv_coords[index].x

            index += 1

    for index, edge in enumerate(bm.edges):
        edge.seam = edge_seam[index]

    utilities_uv.selection_restore()








precision = 5



class Straighten(bpy.types.Operator):
        bl_idname = "uv.customtools_uv_straighten"
        bl_label = "Straight edges chain"
        bl_description = "Straighten selected edges chain and relax rest of the UV Island"
        bl_options = {'REGISTER', 'UNDO'}
	
        @classmethod
        def poll(cls, context):
                if not bpy.context.active_object:
                        return False
                if bpy.context.active_object.mode != 'EDIT':
                        return False
                if bpy.context.active_object.type != 'MESH':
                        return False
                if not bpy.context.object.data.uv_layers:
                        return False
                if bpy.context.scene.tool_settings.uv_select_mode != 'EDGE':
                        return False
                return True


        def execute(self, context):
                if bpy.context.area.spaces.active.type == "IMAGE_EDITOR" and bpy.context.scene.tool_settings.use_uv_select_sync == False:
                        SyncUVSelection()
                        utilities_uv.multi_object_loop(Straightenmain, self, context)
                else:
                        
                        utilities_uv.multi_object_loop(Straightenmain, self, context)

                return {'FINISHED'}



def Straightenmain(self, context):
	bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
	uv_layers = bm.loops.layers.uv.verify()

	selected_faces_loops = utilities_uv.selection_store(bm, uv_layers, return_selected_faces_loops=True)

	for face in selected_faces_loops.keys():
		if len(selected_faces_loops[face]) == len(face.loops):
			self.report({'ERROR_INVALID_INPUT'}, "No face should be selected." )
			return

	islands = utilities_uv.getSelectionIslands(bm, uv_layers, selected_faces_loops.keys())

	for island in islands:
		selected_loops_island = {loop for face in island.intersection(selected_faces_loops.keys()) for loop in selected_faces_loops[face]}

		openSegment = get_loops_segments(self, bm, uv_layers, selected_loops_island)
		if not openSegment:
			continue

		straighten(bm, uv_layers, island, openSegment)

	utilities_uv.selection_restore(bm, uv_layers, restore_seams=True)



def straighten(bm, uv_layers, island, segment_loops):
	bpy.ops.uv.select_all(action='DESELECT')
	bpy.ops.mesh.select_all(action='DESELECT')
	for face in island:
		face.select_set(True)
		for loop in face.loops:
			loop[uv_layers].select = True

	# Make edges of the island bounds seams temporarily for a more predictable result
	bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)

	bbox = segment_loops[-1][uv_layers].uv - segment_loops[0][uv_layers].uv
	straighten_in_x = True
	sign = copysign(1, bbox.x)
	if abs(bbox.y) >= abs(bbox.x):
		straighten_in_x = False
		sign = copysign(1, bbox.y)

	origin = segment_loops[0][uv_layers].uv
	edge_lengths = []
	length = 0
	newly_pinned = set()

	for i, loop in enumerate(segment_loops):
		if i > 0:
			vect = loop[uv_layers].uv - segment_loops[i-1][uv_layers].uv
			edge_lengths.append(vect.length)

	for i, loop in enumerate(segment_loops):
		if i == 0:
			if not loop[uv_layers].pin_uv:
				loop[uv_layers].pin_uv = True
				newly_pinned.add(loop)
		else:
			length += edge_lengths[i-1]
			for nodeLoop in loop.vert.link_loops:
				if nodeLoop[uv_layers].uv.to_tuple(precision) == loop[uv_layers].uv.to_tuple(precision):
					if straighten_in_x:
						nodeLoop[uv_layers].uv = origin + Vector((sign*length, 0))
					else:
						nodeLoop[uv_layers].uv = origin + Vector((0, sign*length))
					if not nodeLoop[uv_layers].pin_uv:
						nodeLoop[uv_layers].pin_uv = True
						newly_pinned.add(nodeLoop)

	try:	# Unwrapping may fail on certain mesh topologies
		bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True, use_subsurf_data=False, margin=0)
	except:
		pass

	for nodeLoop in newly_pinned:
		nodeLoop[uv_layers].pin_uv = False



def get_loops_segments(self, bm, uv_layers, island_loops_dirty):
	island_loops = set()
	island_loops_nexts = set()
	processed_edges = set()
	processed_coords = defaultdict(list)
	start_loops = []
	boundary_splitted_edges = {loop.edge for loop in island_loops_dirty if (not loop.edge.is_boundary) and loop[uv_layers].uv.to_tuple(precision) != loop.link_loop_radial_next.link_loop_next[uv_layers].uv.to_tuple(precision)}

	for loop in island_loops_dirty:
		if loop.link_loop_next in island_loops_dirty and (loop.edge in boundary_splitted_edges or loop.edge not in processed_edges):
			island_loops.add(loop)
			island_loops_nexts.add(loop.link_loop_next)
			processed_edges.add(loop.edge)

	if not processed_edges:
		self.report({'ERROR_INVALID_INPUT'}, "Invalid selection in an island: no edges selected." )
		return None

	for loop in chain(island_loops, island_loops_nexts):
		processed_coords[loop[uv_layers].uv.to_tuple(precision)].append(loop)

	for node_loops in processed_coords.values():
		if len(node_loops) > 2:
			self.report({'ERROR_INVALID_INPUT'}, "No forked edge loops should be selected." )
			return None
		elif len(node_loops) == 1:
			start_loops.extend(node_loops)

	if not start_loops:
		self.report({'ERROR_INVALID_INPUT'}, "Invalid selection in an island: closed UV edge loops." )
		return None
	elif len(start_loops) < 2:
		self.report({'ERROR_INVALID_INPUT'}, "Invalid selection in an island: self-intersecting edge loop." )
		return None
	elif len(start_loops) > 2:
		self.report({'ERROR_INVALID_INPUT'}, "Invalid selection in an island: multiple edge loops." )
		return None


	if len(processed_coords.keys()) < 2:
		self.report({'ERROR_INVALID_INPUT'}, "Invalid selection in an island: zero length edges." )
		return None

	elif len(processed_coords.keys()) == 2:
		single_edge_loops = list(chain.from_iterable(processed_coords.values()))
		if len(single_edge_loops) == 2:
			return single_edge_loops
		else:
			self.report({'ERROR_INVALID_INPUT'}, "Invalid selection in an island: zero length or overlapping edges." )
			return None

	else:

		island_nodal_loops = list(chain.from_iterable(processed_coords.values()))

		if start_loops[0] in island_nodal_loops:
			island_nodal_loops.remove(start_loops[0])
		island_nodal_loops.insert(0, start_loops[0])
		if start_loops[1] in island_nodal_loops:
			island_nodal_loops.remove(start_loops[1])
		island_nodal_loops.append(start_loops[1])


		def find_next_loop(loop):

			def get_prev(found_prev):
				if found_prev:
					for foundLoop in found_prev:
						if foundLoop[uv_layers].uv.to_tuple(precision) == loop.link_loop_prev[uv_layers].uv.to_tuple(precision):
							segment.append(foundLoop)
							for anyLoop in found_prev:
								if anyLoop[uv_layers].uv.to_tuple(precision) == loop.link_loop_prev[uv_layers].uv.to_tuple(precision):
									island_nodal_loops.remove(anyLoop)
							return foundLoop, False
				return None, True

			def get_next(found_next):
				for foundLoop in found_next:
					if foundLoop[uv_layers].uv.to_tuple(precision) == loop.link_loop_next[uv_layers].uv.to_tuple(precision):
						segment.append(foundLoop)
						for anyLoop in found_next:
							if anyLoop[uv_layers].uv.to_tuple(precision) == loop.link_loop_next[uv_layers].uv.to_tuple(precision):
								island_nodal_loops.remove(anyLoop)
						return foundLoop, False
				get_prev(set(island_nodal_loops).intersection(loop.link_loop_prev.vert.link_loops))


			found_next = set(island_nodal_loops).intersection(loop.link_loop_next.vert.link_loops)
			if found_next:
				loopNext, end = get_next(found_next)
			else:
				loopNext, end = get_prev(set(island_nodal_loops).intersection(loop.link_loop_prev.vert.link_loops))

			if end:
				openSegments.append(segment)

			return loopNext, end


		openSegments = []


		while len(island_nodal_loops) > 0:

			loop = island_nodal_loops[0]
			segment = [loop]
			end = False
			
			island_nodal_loops.pop(0)
			if loop in island_loops:
				if loop.link_loop_next in island_nodal_loops and loop.link_loop_next not in start_loops:
					island_nodal_loops.remove(loop.link_loop_next)
			elif loop.link_loop_prev in island_nodal_loops and loop.link_loop_prev not in start_loops:
				island_nodal_loops.remove(loop.link_loop_prev)
			
			while not end:
				loop, end = find_next_loop(loop)

				if not end:
					if loop.link_loop_next in island_nodal_loops and loop.link_loop_next not in start_loops:
						island_nodal_loops.remove(loop.link_loop_next)
					if loop.link_loop_prev in island_nodal_loops and loop.link_loop_prev not in start_loops:
						island_nodal_loops.remove(loop.link_loop_prev)

				if not island_nodal_loops:
					end = True
					openSegments.append(segment)
					break


		if len(openSegments) > 1:
			self.report({'ERROR_INVALID_INPUT'}, "Invalid selection in an island: multiple edge loops. Working in the longest one." )
			openSegments.sort(key=len, reverse=True)

	return openSegments[0]



class Mark(bpy.types.Operator):
        bl_idname = "uv.customuv_markseam"
        bl_label = "MarkSeam"
        bl_description = "Mark UV seam"
        bl_options = {'REGISTER', 'UNDO'}

        def execute(self, context):

                if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
                        bpy.ops.mesh.mark_seam(clear=True)
                        bpy.ops.mesh.region_to_loop()
                        bpy.ops.mesh.mark_seam()

                if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False):
                        bpy.ops.mesh.mark_seam()

                return {'FINISHED'}




   
    
        