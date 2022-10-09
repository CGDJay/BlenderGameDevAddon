

import math
import os
import random
import time

from ..common import*
import bpy
import bmesh
from bpy.props import BoolProperty, IntProperty
from bpy.types import Operator, Panel, PropertyGroup
from mathutils import Vector
import pyperclip
from bpy.props import PointerProperty
AddonName = __package__



# Properties
class GameDev_MossCapSettings(PropertyGroup):
    coverage : IntProperty(
        name = "Coverage",
        description = "Percentage of the object to be covered with moss",
        default = 100,
        min = 0,
        max = 100,
        subtype = 'PERCENTAGE'
        )


    vertices : BoolProperty(
        name = "Selected Faces",
        description = "Add moss only on selected faces",
        default = False
        )



# Panel
class GameDev_MossCap_PT_(Panel):
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    bl_region_type = "UI"
    bl_label = "GenerateMossCap"
    bl_category = "GameDev"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
    

        if bpy.context.preferences.addons[AddonName].preferences.bool_Enable_MossCap == True:
            return True
        else:
            return False

    def draw(self, context):
        scn = context.scene
        settings = scn.MossSettings
        layout = self.layout

        col = layout.column(align=True)
        col.prop(settings, 'coverage', slider=True)
        

        layout.use_property_split = True
        layout.use_property_decorate = False
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=False, even_rows=False, align=True)
        col = flow.column()
        col.prop(settings, 'vertices')

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("gamedev.mosscap_create", text="Add Moss", icon="SHADING_RENDERED")
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator( "gamedev.clipboardsmosshader" , text="CopyShader", icon ="SCRIPTPLUGINS")

# reads the shader.txt file and copies contents to clipboard



class GameDev_ClipboardMossShader(Operator):
        
	bl_idname = "gamedev.clipboardsmosshader"
	bl_label = "ClipboardShader"
	bl_description = "UE5ShaderCode"

	def execute (self, context):
                script_file = os.path.realpath(__file__)
                directory = os.path.dirname(script_file)
                with open((str(directory) + "\MossCapShader.txt"),"r") as f:
                        shadercode = str(f.read())
                        pyperclip.copy(shadercode)
                        return {'FINISHED'} 
           

def area(obj: bpy.types.Object) -> float:

    
    bm_obj = bmesh.new()
    bm_obj.from_mesh(obj.data)
    bm_obj.transform(obj.matrix_world)
    area = sum(face.calc_area() for face in bm_obj.faces)
    bm_obj.free
    return area


def delete_faces(vertices, bm_copy, MossCap: bpy.types.Object):
    # Find upper faces
    if vertices:
        selected_faces = set(face.index for face in bm_copy.faces if face.select)
    # Based on a certain angle, find all faces not pointing up
    down_faces = set(face.index for face in bm_copy.faces if Vector((0, 0, -1.0)).angle(face.normal, 4.0) < (math.pi / 2.0 + 0.5))
    bm_copy.free()
    bpy.ops.mesh.select_all(action='DESELECT')
    # Select upper faces
    mesh = bmesh.from_edit_mesh(MossCap.data)
    for face in mesh.faces:
        if vertices:
            if face.index not in selected_faces:
                face.select = True
        if face.index in down_faces:
            face.select = True
    # Delete unnecessary faces
    faces_select = [face for face in mesh.faces if face.select]
    bmesh.ops.delete(mesh, geom=faces_select, context='FACES_KEEP_BOUNDARY')
    mesh.free()
    bpy.ops.object.mode_set(mode = 'OBJECT')


def add_particles(context, surface_area: float, height: float, coverage: float, MossCap: bpy.types.Object, ballobj: bpy.types.Object):
    # Approximate the number of particles to be emitted
    number = int(surface_area * bpy.context.scene.unit_settings.scale_length * (height ** -2) * ((coverage / 100) ** 2))
    bpy.ops.object.particle_system_add()
    particles = MossCap.particle_systems[0]
    psettings = particles.settings
    psettings.type = 'HAIR'
    psettings.render_type = 'OBJECT'
    # Generate random number for seed
    random_seed = random.randint(0, 1000)
    particles.seed = random_seed
    # Set particles object
    psettings.particle_size = height
    psettings.instance_object = ballobj
    psettings.count = number
    # Convert particles to mesh
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = ballobj
    ballobj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    moss = bpy.context.active_object
    moss.scale = [0.09/ bpy.context.scene.unit_settings.scale_length, 0.09/ bpy.context.scene.unit_settings.scale_length, 0.09/ bpy.context.scene.unit_settings.scale_length]
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    bpy.ops.object.select_all(action='DESELECT')
    MossCap.select_set(True)
    bpy.ops.object.delete()
    moss.select_set(True)
    return moss


def add_metaballs(context, height: float, MossCap: bpy.types.Object) -> bpy.types.Object:
    ball_name = "MossCap"
    ball = bpy.data.metaballs.new(ball_name)
    ballobj = bpy.data.objects.new(ball_name, ball)
    bpy.context.scene.collection.objects.link(ballobj)
    # These settings have proven to work on a large amount of scenarios
    ball.resolution = 0.7 * height + 0.3
    ball.threshold = 1.3
    element = ball.elements.new()
    element.radius = 1.5
    element.stiffness = 0.75
    ballobj.scale = [0.09/ bpy.context.scene.unit_settings.scale_length, 0.09/ bpy.context.scene.unit_settings.scale_length, 0.09/ bpy.context.scene.unit_settings.scale_length]
    return ballobj


#Delete down facing faces packages

def NormalInDirection( normal, direction, limit = 0.5 ):
    return direction.dot( normal ) > limit


def GoingDown( normal, limit = 0.5):


   return NormalInDirection( normal, Vector( (0, 0, -1 ) ), limit )


def DeleteDownFaces(context , Object):
    obj = Object

    prevMode = obj.mode

    # Will need to be in object mode
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # Create a bmesh access
    bm = bmesh.new()
    bm.from_mesh( obj.data )

    # Get faces access
    bm.faces.ensure_lookup_table()

    # Identify the wanted faces
    faces = [f for f in bm.faces if GoingDown( f.normal )]

    # Delete them
    bmesh.ops.delete( bm, geom = faces, context = 'FACES' )

    # Push the geometry back to the mesh
    bm.to_mesh( obj.data )

    # Back to the initial mode
    bpy.ops.object.mode_set(mode=prevMode, toggle=False)




class GameDev_MossCap_OP_Create(Operator):
    bl_idname = "gamedev.mosscap_create"
    bl_label = "Create MossCap"
    bl_description = "Create MossCap (Note: This operation is extremly perfomance demanding)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context) -> bool:
        return bool(context.selected_objects)

    def execute(self, context):
        window = bpy.context.area
        window.type = 'VIEW_3D'
        coverage = context.scene.MossSettings.coverage
        height = 0.1
        vertices = context.scene.MossSettings.vertices

        # Get a list of selected objects, except non-mesh objects
        input_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        snow_list = []


        # Start UI progress bar
        length = len(input_objects)
        context.window_manager.progress_begin(0, 10)
        timer = 0


        for obj in input_objects:
            # Timer
            context.window_manager.progress_update(timer)



            # Duplicate mesh
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            object_eval = obj.evaluated_get(context.view_layer.depsgraph)
            mesh_eval = bpy.data.meshes.new_from_object(object_eval)
            MossCap = bpy.data.objects.new("moss", mesh_eval)
            MossCap.matrix_world = obj.matrix_world
            context.collection.objects.link(MossCap)
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = MossCap
            MossCap.select_set(True)
            bpy.ops.object.mode_set(mode = 'EDIT')
            bm_orig = bmesh.from_edit_mesh(MossCap.data)
            bm_copy = bm_orig.copy()
            bm_copy.transform(obj.matrix_world)
            bm_copy.normal_update()


            # Get faces data
            delete_faces(vertices, bm_copy, MossCap)
            ballobj = add_metaballs(context, height, MossCap)
            context.view_layer.objects.active = MossCap
            surface_area = area(MossCap)
            print (surface_area)
            moss = add_particles(context, surface_area, height, coverage, MossCap, ballobj)
            # Place inside collection
            context.view_layer.active_layer_collection = context.view_layer.layer_collection
            if "moss" not in context.scene.collection.children:
                coll = bpy.data.collections.new("moss")
                context.scene.collection.children.link(coll)
            else:
                coll = bpy.data.collections["moss"]
            coll.objects.link(moss)
            context.view_layer.layer_collection.collection.objects.unlink(moss)

            

            # Parent with object
            moss.parent = obj
            moss.matrix_parent_inverse = obj.matrix_world.inverted()


            # Add moss to list
            snow_list.append(moss)



            # Update progress bar
            timer += 0.1 / length



        # Select created moss meshes
        for s in snow_list:
            s.select_set(True)
        
        


        bpy.ops.object.voxel_remesh()

        bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=False, use_preserve_sharp=False, use_preserve_boundary=False, preserve_paint_mask=False, smooth_normals=False, mode='FACES', target_ratio=1.0, target_edge_length=0.1, target_faces=int(surface_area/10), mesh_area=- 1, seed=0)
        
        DeleteDownFaces(context, moss)

        

        for face in moss.data.polygons:
            face.select = True

        bpy.ops.object.mode_set(mode = 'EDIT')

        bpy.ops.uv.reset()  

        # End progress bar
        context.window_manager.progress_end()
        return {'FINISHED'}


classes = ( 



GameDev_MossCapSettings,
GameDev_MossCap_PT_,
GameDev_MossCap_OP_Create,
GameDev_ClipboardMossShader,




)


def register():
    for cls in classes :
        bpy.utils.register_class(cls)

    bpy.types.Scene.MossSettings = PointerProperty(type=GameDev_MossCapSettings)

def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.MossSettings