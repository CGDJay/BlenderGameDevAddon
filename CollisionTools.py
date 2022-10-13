
from multiprocessing import context
from bpy.types import SpaceView3D
from itertools import chain
from math import pi, radians, sqrt, isclose
from mathutils import Matrix, Vector
import bmesh
import bpy
from bpy import data
import re
import numpy as np
import gpu
from gpu_extras.batch import batch_for_shader

SMALL_NUMBER = 1e-8

def get_parent_name (self, object):
    if object.parent:
        name= object.name
        try:
            parent = object.parent
            name=parent.name
            print("Parent Name:")
            print(name)
        except BaseException :
            print("no parent object")
    else:
        name = object.name

    return (name)

def drawColWire():
    
    for obj in bpy.data.objects:


        if 'Collision' in obj and obj.visible_get(view_layer=bpy.context.view_layer) == True:
            loc = obj.matrix_world.to_translation()

            mesh = obj.data
            coords = [v.co + loc for v in mesh.vertices]
            indices = [(e.vertices[0], e.vertices[1]) for e in mesh.edges]

            shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
            batch = batch_for_shader(
            shader, 'LINES', {"pos": coords}, indices=indices)

            shader.bind()
            shader.uniform_float("color", (0, 1, 0, 1))

            batch.draw(shader)

        else:
            pass
    return

def get_point_dist_to_line_sq(point, direction, origin):
    """
    Calculates the square distance of a given point in world space to a given line.
    Assumes direction is normalized.
    """
    closest_point = origin + direction * (point - origin).dot(direction)


    return (closest_point - point).length_squared

def get_range_pct(min_value, max_value, value):
    """Calculates the percentage along a line from min_value to max_value."""

    divisor = max_value - min_value
    if abs(divisor) <= SMALL_NUMBER:
        return 1.0 if value >= max_value else 0.0


    return (value - min_value) / divisor

def get_dist_sq(a, b):
    """Returns the square distance between two 3D vectors."""
    x, y, z = a[0] - b[0], a[1] - b[1], a[2] - b[2]


    return x*x + y*y + z*z

def calc_best_fit_line(points):
    """
    Calculates the best fit line that minimizes distance from the line to each point.
    Returns two vectors: the direction of the line and a point it passes through.
    """
    # https://stackoverflow.com/questions/24747643/3d-linear-regression
    # https://machinelearningmastery.com/calculate-principal-component-analysis-scratch-python/

    A = np.array(points)
    M = np.mean(A.T, axis=1)  # Find mean
    C = A - M  # Center around mean
    V = np.cov(C.T)  # Calculate covariance matrix of centered matrix
    U, s, Vh = np.linalg.svd(V)  # Singular value decomposition


    return Vector(U[:,0]), Vector(M)

def get_context(active_obj=None, selected_objs=None):
    """Returns context for single object operators."""

    ctx = {}
    if active_obj and selected_objs:
        # Operate on all the objects, active object is specified. Selected should include active
        ctx['object'] = ctx['active_object'] = active_obj
        selected_objs = selected_objs if active_obj in selected_objs else list(selected_objs) + [active_obj]
        ctx['selected_objects'] = ctx['selected_editable_objects'] = selected_objs

    elif not active_obj and selected_objs:
        # Operate on all the objects, it isn't important which one is active
        ctx['object'] = ctx['active_object'] = next(iter(selected_objs))
        ctx['selected_objects'] = ctx['selected_editable_objects'] = [active_obj]

    elif active_obj and not selected_objs:
        # Operate on a single object
        ctx['object'] = ctx['active_object'] = active_obj
        ctx['selected_objects'] = ctx['selected_editable_objects'] = [active_obj]


    return ctx

def get_collection(context, name, allow_duplicate=False, clean=True):
    """Ensures that a collection with the given name exists in the scene."""

    # collection = bpy.data.collections.get(name)

    collection = None
    collections = [context.scene.collection]

    while collections:
        cl = collections.pop()
        if cl.name == name or allow_duplicate and re.match(rf"^{name}(?:\.\d\d\d)?$", cl.name):
            collection = cl
            break
        collections.extend(cl.children)
        cl = None

    if not collection:
        collection = bpy.data.collections.new(name)

    elif clean:
        for obj in collection.objects[:]:
            collection.objects.unlink(obj)

    if name not in context.scene.collection.children:
        context.scene.collection.children.link(collection)


    return collection


class TempModifier:
    """Convenient modifier wrapper to use in a `with` block to be automatically applied at the end."""

    def __init__(self, obj, type):
        self.obj = obj
        self.type = type

    def __enter__(self):
        self.saved_mode = bpy.context.mode
        if bpy.context.mode == 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()

        self.modifier = self.obj.modifiers.new(type=self.type, name="")
        # Move first to avoid the warning on applying
        ctx = get_context(self.obj)
        bpy.ops.object.modifier_move_to_index(ctx, modifier=self.modifier.name, index=0)

        return self.modifier

    def __exit__(self, exc_type, exc_value, exc_traceback):
        ctx = get_context(self.obj)

        bpy.ops.object.modifier_apply(ctx, modifier=self.modifier.name)

        if self.saved_mode == 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()


collision_prefixes = ("UCX", "UBX", "UCP", "USP")

def get_collision_objects(context, obj):

    pattern = r"^(?:%s)_%s_\d+$" % ('|'.join(collision_prefixes), obj.name)

    return [o for o in context.scene.objects if re.match(pattern, o.name)]

def find_free_col_name(prefix, name):
    n = 1
    while True:
        if n >= 10:
            col_name = f"{prefix}_{name}_{n}"
            n += 1
        else:

            col_name = f"{prefix}_{name}_0{n}"
            n += 1

        if col_name not in bpy.context.scene.objects:
            break


    return col_name

def remove_extra_data(obj):
    assert obj.type == 'MESH'

    obj.vertex_groups.clear()
    obj.shape_key_clear()

    mesh = obj.data
    mesh.use_customdata_vertex_bevel = False
    mesh.use_customdata_edge_bevel = False
    mesh.use_customdata_edge_crease = False

    # mesh.materials.clear() seems to crash
    while mesh.materials:
        mesh.materials.pop()
    while mesh.uv_layers.active:
        mesh.uv_layers.remove(mesh.uv_layers.active)
    while mesh.attributes.active:
        mesh.attributes.remove(mesh.attributes.active)

def is_box(bm):
    """Check if the mesh can be represented by a box collision shape."""

    if len(bm.verts) != 8:
        return False

    c = sum((vert.co for vert in bm.verts), Vector()) / len(bm.verts)
    avg_d_sq = sum(get_dist_sq(vert.co, c) for vert in bm.verts) / len(bm.verts)


    return all(isclose(avg_d_sq, get_dist_sq(vert.co, c), abs_tol=0.0001/bpy.context.scene.unit_settings.scale_length) for vert in bm.verts)

class GameDev_OT_collision_assign(bpy.types.Operator):
    #tooltip
    """Assign selected collision meshes to the active object"""

    bl_idname = 'gamedev.collision_assign'
    bl_label = "Assign Collision"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        return len(context.selected_objects) > 1 and context.object and context.mode == 'OBJECT'

    def execute(self, context):
        for obj in context.selected_objects[:]:
            if obj == context.active_object:
                continue

            prefix = obj.name[:3]
            if prefix in collision_prefixes:
                obj.name = find_free_col_name(prefix, context.active_object.name)

                if obj.data.users == 1:
                    obj.data.name = obj.name

        return {'FINISHED'}

class GameDev_OT_collision_copy_to_linked(bpy.types.Operator):
    #tooltip
    """Copy collision meshes from active to linked objects"""

    bl_idname = 'gamedev.collision_copy_to_linked'
    bl_label = "Copy Collision to Linked"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(context.active_object)

    def execute(self, context):
        obj = context.active_object
        col_objs = get_collision_objects(context, obj)
        if not col_objs:
            self.report({'WARNING'}, "Active object has no collision assigned.")
            return {'CANCELLED'}


        if obj.data.users == 1:
            self.report({'WARNING'}, "Active object data has no other users.")
            return {'CANCELLED'}

        num_linked = 0
        for other_obj in bpy.data.objects:
            if other_obj != obj and other_obj.data == obj.data:
                num_linked += 1

                # Clean collision
                for old_col_obj in get_collision_objects(context, other_obj):
                    bpy.data.objects.remove(old_col_obj, do_unlink=True)

                # Copy collision to other object's location
                obj_to_other = obj.matrix_world.inverted() @ other_obj.matrix_world
                for col_obj in col_objs:
                    name = find_free_col_name(col_obj.name[:3], other_obj.name)
                    new_col_obj = bpy.data.objects.new(name, col_obj.data)
                    new_col_obj.matrix_world = (other_obj.matrix_world @
                        (obj.matrix_world.inverted() @ col_obj.matrix_world))
                    new_col_obj.show_wire = col_obj.show_wire
                    new_col_obj.display_type = col_obj.display_type
                    new_col_obj.display.show_shadows = col_obj.display.show_shadows

                    for collection in col_obj.users_collection:
                        collection.objects.link(new_col_obj)

        self.report({'INFO'}, f"Copied collision to {num_linked} other objects.")


        return {'FINISHED'}


def calculate_parameters(self, context, obj):
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
        vert_cos = [vert.co for vert in bm.verts if vert.select]

    else:
        dg = context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(dg)
        vert_cos = [vert.co for vert in obj_eval.data.vertices]

    if len(vert_cos) < 3:
        raise RuntimeError("Requires at least three vertices")

    axis, _ = calc_best_fit_line(vert_cos)

    corner1 = vert_cos[0].copy()
    corner2 = vert_cos[1].copy()

    for co in vert_cos:
        corner1.x = min(corner1.x, co.x)
        corner1.y = min(corner1.y, co.y)
        corner1.z = min(corner1.z, co.z)
        corner2.x = max(corner2.x, co.x)
        corner2.y = max(corner2.y, co.y)
        corner2.z = max(corner2.z, co.z)

    # Bounding box dimensions
    self.aabb_depth = abs(corner1.x - corner2.x)
    self.aabb_width = abs(corner1.y - corner2.y)
    self.aabb_height = abs(corner1.z - corner2.z)
    self.location = center = (corner1 + corner2) * 0.5

    # Cylinder radius
    self.cyl_radius1 = self.cyl_radius2 = 0.001

    for co in vert_cos:
        dx = center.x - co.x
        dy = center.y - co.y
        d = sqrt(dx * dx + dy * dy)
        influence2 = get_range_pct(corner1.z, corner2.z, co.z)
        influence1 = 1.0 - influence2
        self.cyl_radius1 = max(self.cyl_radius1, d * influence1)
        self.cyl_radius2 = max(self.cyl_radius2, d * influence2)
    self.cyl_height = self.aabb_height

    # Capsule axis and radius
    radius_sq = 0.001
    depth_sq = 0.0

    for co in vert_cos:
        dist_to_axis_sq = get_point_dist_to_line_sq(co, axis, center)

        if dist_to_axis_sq > radius_sq:
            radius_sq = dist_to_axis_sq
        dist_along_axis_sq = (co - center).project(axis).length_squared

        if dist_along_axis_sq > depth_sq:
            depth_sq = dist_along_axis_sq
    self.cap_radius = sqrt(radius_sq)
    self.cap_rotation = axis.to_track_quat('Z', 'X').to_euler('XYZ')
    self.cap_depth = sqrt(depth_sq) * 2.0 - self.cap_radius

    # Sphere radius
    self.sph_radius = max(self.aabb_depth, self.aabb_width, self.aabb_height)

def create_col_object_from_bm(self, context, obj, bm, prefix=None):
    if not prefix:
        # Autodetect (should detect sphere too)
        prefix = "UBX" if is_box(bm) else "UCX"

    name = find_free_col_name(prefix, obj.name)
    data = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(data)
    
    col_obj = bpy.data.objects.new(name, data)
    col_obj.matrix_world = obj.matrix_world
    col_obj.show_wire = True
    col_obj.display_type = 'WIRE' if self.wire else 'SOLID'
    col_obj.display.show_shadows = False
    col_obj.location=col_obj.location - obj.location
    col_obj.parent = obj
    col_obj ['Collision'] = True

    # bmeshes created with from_mesh or from_object may have some UVs or customdata
    remove_extra_data(col_obj)

    # Link to scene
    if not self.collection:
        collection = context.scene.collection
    else:
        collection = get_collection(context, self.collection, allow_duplicate=True, clean=False)
        collection.color_tag = 'COLOR_04'
    collection.objects.link(col_obj)


    return col_obj

def create_split_col_object_from_bm(self, context, obj, bm, thickness, offset=0.0):
    # Based on https://github.com/blender/blender-addons/blob/master/mesh_tools/split_solidify.py
    # by zmj100, updated by zeffii to BMesh
    distance = thickness * (offset + 1.0) * 0.5
    src_bm = bm
    src_bm.faces.ensure_lookup_table()
    src_bm.verts.ensure_lookup_table()
    src_bm.normal_update()

    for src_f in src_bm.faces:
        bm = bmesh.new()
        # Add new vertices
        vs1 = []
        vs2 = []
        for v in src_f.verts:
            p1 = v.co + src_f.normal * distance  # Out
            p2 = v.co + src_f.normal * (distance - thickness)  # In
            vs1.append(bm.verts.new(p1))
            vs2.append(bm.verts.new(p2))

        # Add new faces
        n = len(vs1)
        bm.faces.new(vs1)


        for i in range(n):
            j = (i + 1) % n
            vseq = vs1[i], vs2[i], vs2[j], vs1[j]
            bm.faces.new(vseq)
        vs2.reverse()
        bm.faces.new(vs2)

        create_col_object_from_bm(self,context, obj, bm)
        bm.free()

class GameDev_OT_collision_AutoUBX(bpy.types.Operator):
    bl_idname = "gamedev.collision_auto_ubx"
    bl_label = "createubx"
    bl_options = {'REGISTER', 'UNDO'}

    collection: bpy.props.StringProperty(
        name="Collection",
        description="Name of the collection for the collision objects",
        default="Collision",
    )

    scaleThreshhold:bpy.props.FloatProperty(
        name="Area",
        description="Bounding box width",
        subtype='DISTANCE',
        min=0.001,
        default= 100,
    )

    def get_mesh_area(self,object,scaleThreshhold):
        isTooSmall = True
        if object.type== 'MESH':

            bm = bmesh.new()
            bm.from_mesh(object.data)
            area = sum(f.calc_area() for f in bm.faces)*bpy.context.scene.unit_settings.scale_length
            print(area)

            bm.free()
            if area > scaleThreshhold:
                isTooSmall = False


        return (isTooSmall)




    def get_BoundBox(self,object):
        obj= object

        verts   = [v.co for v in obj.data.vertices]

        points = np.asarray(verts)
        means = np.mean(points, axis=1)

        cov = np.cov(points, y = None,rowvar = 0,bias = 1)

        v, vect = np.linalg.eig(cov)

        tvect = np.transpose(vect)
        points_r = np.dot(points, np.linalg.inv(tvect))

        co_min = np.min(points_r, axis=0)
        co_max = np.max(points_r, axis=0)

        xmin, xmax = co_min[0], co_max[0]
        ymin, ymax = co_min[1], co_max[1]
        zmin, zmax = co_min[2], co_max[2]

        xdif = (xmax - xmin) * 0.5
        ydif = (ymax - ymin) * 0.5
        zdif = (zmax - zmin) * 0.5

        cx = xmin + xdif
        cy = ymin + ydif
        cz = zmin + zdif

        corners = np.array([
            [cx - xdif, cy - ydif, cz - zdif],
            [cx - xdif, cy + ydif, cz - zdif],
            [cx - xdif, cy + ydif, cz + zdif],
            [cx - xdif, cy - ydif, cz + zdif],
            [cx + xdif, cy + ydif, cz + zdif],
            [cx + xdif, cy + ydif, cz - zdif],
            [cx + xdif, cy - ydif, cz + zdif],
            [cx + xdif, cy - ydif, cz - zdif],
        ])

        object_BB = np.dot(corners, tvect)
        center = np.dot([cx, cy, cz], tvect)

        corners = [Vector((el[0], el[1], el[2])) for el in corners]

        return(object_BB)

    def create_cube(self,object_BB):

        vertices = object_BB

        #######    Top      Left     right     bottom    front      back
        faces=[(1,0,3,2),(4,6,7,5),(0,7,6,3),(7,0,1,5),(2,4,5,1),(4,2,3,6)]
        edges=[]
        # Create an empty mesh and the object.
        mesh = bpy.data.meshes.new('Basic_Cube')
        mesh.from_pydata(vertices,edges,faces)


        new_object = bpy.data.objects.new("new_object",mesh)
        bm = bmesh.new()
        me = new_object.data
        bm.from_mesh(me) # load bmesh
        for f in bm.faces:
            f.normal_flip()
        bm.normal_update() # not sure if req'd
        bm.to_mesh(me)
        me.update()
        bm.clear() #.. clear before load next


        view_layer=bpy.context.view_layer
        view_layer.active_layer_collection.collection.objects.link(new_object)
        return(new_object)
   
    def execute(self, context):

        object=bpy.context.view_layer.objects.active

        parentname=get_parent_name(self,object)
        number=(0)

        bpy.ops.object.select_grouped(type='PARENT')
        parentobj=bpy.context.view_layer.objects.active

        for obj in bpy.data.objects[parentname].children:
            bpy.context.view_layer.objects.active = obj
            bpy.context.active_object.select_set(True)
            print (obj.name)
        if parentobj.type != 'MESH':
            pass
        else:

            parentobj.select_set(True)

        for obj in bpy.context.selected_objects:

            if 'Collision' not in obj:

                object = obj

                if self.get_mesh_area(object,self.scaleThreshhold) == True:
                    pass
                    continue

                number = number+1

                print (number)


                object_BB = self.get_BoundBox(object)

                new_object=self.create_cube(object_BB)
                new_object.display_type = 'WIRE'
                new_object ['Collision'] = True

                #set this to parent name if parent is not a empty
                col_name=find_free_col_name('UBX',obj.name)


                new_object.name = col_name

                new_object.location=object.location
                
                new_object.parent = bpy.data.objects[obj.name]

                if new_object.parent != None:
                    print ("something")
                    new_object.matrix_parent_inverse = new_object.parent.matrix_world.inverted()

                if not self.collection:
                    collection = context.scene.collection
                else:
                    collection = get_collection(context, self.collection, allow_duplicate=True, clean=False)
                    collection.color_tag = 'COLOR_04'
                    collection.objects.link(new_object)





        return {'FINISHED'}

class GameDev_OT_collision_makeUBX(bpy.types.Operator):
    #tooltip
    """Generate collision for selected geometry"""

    bl_idname = 'gamedev.collision_make_ubx'
    bl_label = "Make UBX Collision"
    bl_options = {'REGISTER', 'UNDO'}

        # AABB settings
    aabb_width: bpy.props.FloatProperty(
        name="Width",
        description="Bounding box width",
        subtype='DISTANCE',
        min=0.001,
    )
    aabb_height: bpy.props.FloatProperty(
        name="Height",
        description="Bounding box height",
        subtype='DISTANCE',
        min=0.001,
    )
    aabb_depth: bpy.props.FloatProperty(
        name="Depth",
        description="Bounding box depth",
        subtype='DISTANCE',
        min=0.001,
    )
    collection: bpy.props.StringProperty(
        name="Collection",
        description="Name of the collection for the collision objects",
        default="Collision",
    )

    wire: bpy.props.BoolProperty(
        name="Wire",
        description="How to display the collision objects in viewport",
        default=True,
    )
    hollow: bpy.props.BoolProperty(
        name="Hollow",
        description="Create a hollow shape from multiple bodies",
        default=False,
    )
    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="Wall thickness",
        subtype='DISTANCE',
        default=0.2,
        min=0.001,
    )
    offset: bpy.props.FloatProperty(
        name="Offset",
        description="Offset the thickness from the center",
        subtype='DISTANCE',
        default=-1.0,
        min=-1.0,
        max=1.0,
    )
    location: bpy.props.FloatVectorProperty(
        name="Location",
        description="Shape location",
        subtype='TRANSLATION',
        size=3,
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object


        return obj and obj.type == 'MESH' and obj.mode in {'OBJECT', 'EDIT'}



    def get_BoundBox(self,object):
        obj = object

        if obj.mode == 'EDIT':
            print ('in edit mode')
            bm = bmesh.from_edit_mesh(obj.data)
            verts = [v.co for v in bm.verts if v.select]
        else:

            verts   = [v.co for v in obj.data.vertices]

        points = np.asarray(verts)
        means = np.mean(points, axis=1)

        cov = np.cov(points, y = None,rowvar = 0,bias = 1)

        v, vect = np.linalg.eig(cov)

        tvect = np.transpose(vect)
        points_r = np.dot(points, np.linalg.inv(tvect))

        co_min = np.min(points_r, axis=0)
        co_max = np.max(points_r, axis=0)

        xmin, xmax = co_min[0], co_max[0]
        ymin, ymax = co_min[1], co_max[1]
        zmin, zmax = co_min[2], co_max[2]

        xdif = (xmax - xmin) * 0.5
        ydif = (ymax - ymin) * 0.5
        zdif = (zmax - zmin) * 0.5

        cx = xmin + xdif
        cy = ymin + ydif
        cz = zmin + zdif

        corners = np.array([
            [cx - xdif, cy - ydif, cz - zdif],
            [cx - xdif, cy + ydif, cz - zdif],
            [cx - xdif, cy + ydif, cz + zdif],
            [cx - xdif, cy - ydif, cz + zdif],
            [cx + xdif, cy + ydif, cz + zdif],
            [cx + xdif, cy + ydif, cz - zdif],
            [cx + xdif, cy - ydif, cz + zdif],
            [cx + xdif, cy - ydif, cz - zdif],
        ])

        object_BB = np.dot(corners, tvect)
        center = np.dot([cx, cy, cz], tvect)

        corners = [Vector((el[0], el[1], el[2])) for el in corners]

        return(object_BB)

    def create_cube(self,object_BB):

        vertices = object_BB

        #######    Top      Left     right     bottom    front      back
        faces=[(1,0,3,2),(4,6,7,5),(0,7,6,3),(7,0,1,5),(2,4,5,1),(4,2,3,6)]
        edges=[]
        # Create an empty mesh and the object.
        mesh = bpy.data.meshes.new('Basic_Cube')
        mesh.from_pydata(vertices,edges,faces)


        new_object = bpy.data.objects.new("new_object",mesh)
        bm = bmesh.new()
        me = new_object.data
        bm.from_mesh(me) # load bmesh
        for f in bm.faces:
            f.normal_flip()
        bm.normal_update() # not sure if req'd
        bm.to_mesh(me)
        me.update()
        bm.clear() #.. clear before load next


        view_layer=bpy.context.view_layer
        view_layer.active_layer_collection.collection.objects.link(new_object)
        return(new_object)

    def execute(self, context):

        obj = context.active_object

        parentname=get_parent_name(self,obj)
        number=(0)

        if obj.mode != 'EDIT':
            # When working from object mode, it follows that there should be only one collision shape
            pattern = re.compile(rf"^U[A-Z][A-Z]_{obj.name}_\d+")
            for mesh in [mesh for mesh in bpy.data.meshes if pattern.match(mesh.name)]:
                bpy.data.meshes.remove(mesh)
        for obj in bpy.context.selected_objects:
            object_BB = self.get_BoundBox(obj)

            new_object=self.create_cube(object_BB)
            new_object.display_type = 'WIRE'
            new_object ['Collision'] = True

            new_object.location=obj.location
            new_object.parent = bpy.data.objects[obj.name]

            col_name=find_free_col_name('UBX',obj.name)
            new_object.name = col_name

            if new_object.parent != None:
                print ("something")
                new_object.matrix_parent_inverse = new_object.parent.matrix_world.inverted()

            if not self.collection:
                collection = context.scene.collection

            else:
                collection = get_collection(context, self.collection, allow_duplicate=True, clean=False)
                collection.color_tag = 'COLOR_04'

            collection.objects.link(new_object)




        return {'FINISHED'}

class GameDev_OT_collision_makeUCX(bpy.types.Operator):
    #tooltip
    """Generate collision for selected geometry"""

    bl_idname = 'gamedev.collision_make_ucx'
    bl_label = "Make UCX Collision"
    bl_options = {'REGISTER', 'UNDO'}


    # Convex settings
    planar_angle: bpy.props.FloatProperty(
        name="Max Face Angle",
        description="Use to remove decimation bias towards large, bumpy faces",
        subtype='ANGLE',
        default=radians(10.0),
        min=0.0,
        max=radians(180.0),
        soft_max=radians(90.0),
    )
    decimate_ratio: bpy.props.FloatProperty(
        name="Decimate Ratio",
        description="Percentage of edges to collapse",
        subtype='FACTOR',
        default=1.0,
        min=0.0,
        max=1.0,
    )
    use_symmetry: bpy.props.BoolProperty(
        name="Symmetry",
        description="Maintain symmetry on an axis",
        default=False,
    )
    symmetry_axis: bpy.props.EnumProperty(
        name="Symmetry Axis",
        description="Axis of symmetry",
        items=[
            ('X', "X", "X"),
            ('Y', "Y", "Y"),
            ('Z', "Z", "Z"),
        ],
    )

    wire: bpy.props.BoolProperty(
        name="Wire",
        description="How to display the collision objects in viewport",
        default=True,
    )
    hollow: bpy.props.BoolProperty(
        name="Hollow",
        description="Create a hollow shape from multiple bodies",
        default=False,
    )
    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="Wall thickness",
        subtype='DISTANCE',
        default=0.2,
        min=0.001,
    )
    offset: bpy.props.FloatProperty(
        name="Offset",
        description="Offset the thickness from the center",
        subtype='DISTANCE',
        default=-1.0,
        min=-1.0,
        max=1.0,
    )
    location: bpy.props.FloatVectorProperty(
        name="Location",
        description="Shape location",
        subtype='TRANSLATION',
        size=3,
    )
    collection: bpy.props.StringProperty(
        name="Collection",
        description="Name of the collection for the collision objects",
        default="Collision",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object


        return obj and obj.type == 'MESH' and obj.mode in {'OBJECT', 'EDIT'}


    def make_convex_collision(self, context, obj):

        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(obj.data).copy()
            bm.verts.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.select], context='VERTS')

        else:
            bm = bmesh.new()
            dg = context.evaluated_depsgraph_get()
            bm.from_object(obj, dg)

        # Clean incoming mesh
        bm.edges.ensure_lookup_table()
        for edge in bm.edges:
            edge.seam = False
            edge.smooth = True

        bm.faces.ensure_lookup_table()
        for face in bm.faces:
            face.smooth = False

        # While convex_hull works only on verts, pass all the geometry so that it gets tagged

        geom = list(chain(bm.verts, bm.edges, bm.faces))
        result = bmesh.ops.convex_hull(bm, input=geom, use_existing_faces=True)

        # geom_interior: elements that ended up inside the hull rather than part of it
        # geom_unused: elements that ended up inside the hull and are are unused by other geometry
        # The two sets may intersect, so for now just delete one of them. I haven't found a case yet
        # where this leaves out unwanted geometry

        bmesh.ops.delete(bm, geom=result['geom_interior'], context='TAGGED_ONLY')
        bm.normal_update()
        bmesh.ops.dissolve_limit(bm, angle_limit=self.planar_angle,
            verts=bm.verts, edges=bm.edges, use_dissolve_boundaries=False, delimit=set())
        bmesh.ops.triangulate(bm, faces=bm.faces)
        col_obj = create_col_object_from_bm(self,context, obj, bm, "UCX")
        bm.free()


        # Decimate (no bmesh op for this currently?)
        with TempModifier(col_obj, type='DECIMATE') as dec_mod:
            dec_mod.ratio = self.decimate_ratio
            dec_mod.use_symmetry = self.use_symmetry
            dec_mod.symmetry_axis = self.symmetry_axis

        return (col_obj)


    def execute(self, context):
        obj = context.active_object

        if obj.mode != 'EDIT':
            # When working from object mode, it follows that there should be only one collision shape
            pattern = re.compile(rf"^U[A-Z][A-Z]_{obj.name}_\d+")
            for mesh in [mesh for mesh in bpy.data.meshes if pattern.match(mesh.name)]:
                bpy.data.meshes.remove(mesh)
        for obj in bpy.context.selected_objects:
            if obj.type=='MESH':
                calculate_parameters(self,context, context.object)
                col_obj=self.make_convex_collision(context, obj)

                parentname=get_parent_name(self,obj)
                col_obj ['Collision'] = True
                col_obj.location=obj.location
                col_obj.parent = bpy.data.objects[obj.name]
                col_obj ['Collision'] = True
                if col_obj.parent != None:
                    print ("something")
                    col_obj.matrix_parent_inverse = col_obj.parent.matrix_world.inverted()


        return {'FINISHED'}

class GameDev_OT_collision_make(bpy.types.Operator):
    #tooltip
    """Generate collision for selected geometry"""

    bl_idname = 'gamedev.collision_make'
    bl_label = "Make Collision"
    bl_options = {'REGISTER', 'UNDO'}

    shape: bpy.props.EnumProperty(
        name="Shape",
        description="Selects the collision shape",
        items=[
            ('CUBE', "CUBE", "Axis-aligned box collision.", 'MESH_PLANE', 0),
            ('CYLINDER', "Cylinder", "Cylinder collision.", 'MESH_CYLINDER', 1),
            ('CAPSULE', "Capsule", "Capsule collision.", 'MESH_CAPSULE', 2),
            ('SPHERE', "Sphere", "Sphere collision.", 'MESH_UVSPHERE', 3),
            ('CONVEX', "Convex", "Convex collision.", 'MESH_ICOSPHERE', 4),
            ('WALL', "Wall", "Wall collision.", 'MOD_SOLIDIFY', 5),
        ],
    )
    collection: bpy.props.StringProperty(
        name="Collection",
        description="Name of the collection for the collision objects",
        default="Collision",
    )
    wire: bpy.props.BoolProperty(
        name="Wire",
        description="How to display the collision objects in viewport",
        default=True,
    )
    hollow: bpy.props.BoolProperty(
        name="Hollow",
        description="Create a hollow shape from multiple bodies",
        default=False,
    )
    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="Wall thickness",
        subtype='DISTANCE',
        default=0.2,
        min=0.001,
    )
    offset: bpy.props.FloatProperty(
        name="Offset",
        description="Offset the thickness from the center",
        subtype='DISTANCE',
        default=-1.0,
        min=-1.0,
        max=1.0,
    )
    location: bpy.props.FloatVectorProperty(
        name="Location",
        description="Shape location",
        subtype='TRANSLATION',
        size=3,
    )

    # AABB settings
    aabb_width: bpy.props.FloatProperty(
        name="Width",
        description="Bounding box width",
        subtype='DISTANCE',
        min=0.001,
    )
    aabb_height: bpy.props.FloatProperty(
        name="Height",
        description="Bounding box height",
        subtype='DISTANCE',
        min=0.001,
    )
    aabb_depth: bpy.props.FloatProperty(
        name="Depth",
        description="Bounding box depth",
        subtype='DISTANCE',
        min=0.001,
    )

    # Cylinder settings
    cyl_caps: bpy.props.BoolProperty(
        name="Caps",
        description="Create shapes for the top and bottom of the cylinder",
        default=False,
    )
    cyl_sides: bpy.props.IntProperty(
        name="Sides",
        description="Number of sides",
        default=8,
        min=3,
    )
    cyl_rotate: bpy.props.BoolProperty(
        name="Rotate",
        description="Rotate cylinder by half",
    )
    cyl_radius1: bpy.props.FloatProperty(
        name="Radius 1",
        description="First cylinder radius",
        subtype='DISTANCE',
        min=0.001,
    )
    cyl_radius2: bpy.props.FloatProperty(
        name="Radius 2",
        description="Second cylinder radius",
        subtype='DISTANCE',
        min=0.001,
    )
    cyl_height: bpy.props.FloatProperty(
        name="Height",
        description="Cylinder height",
        subtype='DISTANCE',
        min=0.001,
    )

    # Capsule settings
    cap_radius: bpy.props.FloatProperty(
        name="Radius",
        description="Capsule radius",
        subtype='DISTANCE',
        min=0.001,
    )
    cap_depth: bpy.props.FloatProperty(
        name="Depth",
        description="Capsule depth",
        subtype='DISTANCE',
        min=0.001,
    )
    cap_rotation: bpy.props.FloatVectorProperty(
        name="Rotation",
        description="Capsule rotation",
        subtype='EULER',
        size=3,
    )

    # Sphere settings
    sph_radius: bpy.props.FloatProperty(
        name="Radius",
        description="Sphere radius",
        subtype='DISTANCE',
        min=0.001,
    )

    # Convex settings
    planar_angle: bpy.props.FloatProperty(
        name="Max Face Angle",
        description="Use to remove decimation bias towards large, bumpy faces",
        subtype='ANGLE',
        default=radians(10.0),
        min=0.0,
        max=radians(180.0),
        soft_max=radians(90.0),
    )
    decimate_ratio: bpy.props.FloatProperty(
        name="Decimate Ratio",
        description="Percentage of edges to collapse",
        subtype='FACTOR',
        default=1.0,
        min=0.0,
        max=1.0,
    )
    use_symmetry: bpy.props.BoolProperty(
        name="Symmetry",
        description="Maintain symmetry on an axis",
        default=False,
    )
    symmetry_axis: bpy.props.EnumProperty(
        name="Symmetry Axis",
        description="Axis of symmetry",
        items=[
            ('X', "X", "X"),
            ('Y', "Y", "Y"),
            ('Z', "Z", "Z"),
        ],
    )

    # Wall settings
    wall_fill_holes: bpy.props.BoolProperty(
        name="Fill holes",
        description="Fill rectangular holes in walls",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object


        return obj and obj.type == 'MESH' and obj.mode in {'OBJECT', 'EDIT'}

    def make_aabb_collision(self, context, obj):
        v = Vector((self.aabb_depth, self.aabb_width, self.aabb_height)) * 0.5

        bm = bmesh.new()
        verts = bmesh.ops.create_cube(bm, calc_uvs=False)['verts']
        verts[0].co = self.location.x - v.x, self.location.y - v.y, self.location.z - v.z
        verts[1].co = self.location.x - v.x, self.location.y - v.y, self.location.z + v.z
        verts[2].co = self.location.x - v.x, self.location.y + v.y, self.location.z - v.z
        verts[3].co = self.location.x - v.x, self.location.y + v.y, self.location.z + v.z
        verts[4].co = self.location.x + v.x, self.location.y - v.y, self.location.z - v.z
        verts[5].co = self.location.x + v.x, self.location.y - v.y, self.location.z + v.z
        verts[6].co = self.location.x + v.x, self.location.y + v.y, self.location.z - v.z
        verts[7].co = self.location.x + v.x, self.location.y + v.y, self.location.z + v.z

        if self.hollow:
            create_split_col_object_from_bm(self,context, obj, bm, self.thickness, self.offset)

        else:
            create_col_object_from_bm(self,context, obj, bm)
        bm.free()

    def make_cylinder_collision(self, context, obj):
        mat = Matrix.Translation(self.location)

        if self.cyl_rotate:
            mat @= Matrix.Rotation(pi / self.cyl_sides, 4, 'Z')
        bm = bmesh.new()
        cap_ends = not self.hollow or self.cyl_caps
        bmesh.ops.create_cone(bm, cap_ends=cap_ends, cap_tris=False, segments=self.cyl_sides,
            radius1=self.cyl_radius1, radius2=self.cyl_radius2, depth=self.cyl_height,
            calc_uvs=False, matrix=mat)
        if self.hollow:
            create_split_col_object_from_bm(self,context, obj, bm, self.thickness, self.offset)

        else:
            create_col_object_from_bm(self,context, obj, bm)
        bm.free()

    def make_capsule_collision(self, context, obj):

        mat = Matrix.Translation(self.location) @ self.cap_rotation.to_matrix().to_4x4()
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8,
            radius1=self.cap_radius, radius2=self.cap_radius, depth=self.cap_depth,
            calc_uvs=False, matrix=mat)
        bm.faces.ensure_lookup_table()
        caps = [bm.faces[-1], bm.faces[-4]]
        bmesh.ops.poke(bm, faces=caps, offset=self.cap_radius)
        create_col_object_from_bm(self,context, obj, bm, "UCP")
        bm.free()

    def make_sphere_collision(self, context, obj):
        
        mat = Matrix.Translation(self.location)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=self.sph_radius*0.5,
            calc_uvs=False, matrix=mat)
        create_col_object_from_bm(self,context, obj, bm, "USP")
        bm.free()

    def make_convex_collision(self, context, obj):

        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(obj.data).copy()
            bm.verts.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.select], context='VERTS')

        else:
            bm = bmesh.new()
            dg = context.evaluated_depsgraph_get()
            bm.from_object(obj, dg)

        # Clean incoming mesh
        bm.edges.ensure_lookup_table()
        for edge in bm.edges:
            edge.seam = False
            edge.smooth = True

        bm.faces.ensure_lookup_table()
        for face in bm.faces:
            face.smooth = False

        # While convex_hull works only on verts, pass all the geometry so that it gets tagged

        geom = list(chain(bm.verts, bm.edges, bm.faces))
        result = bmesh.ops.convex_hull(bm, input=geom, use_existing_faces=True)

        # geom_interior: elements that ended up inside the hull rather than part of it
        # geom_unused: elements that ended up inside the hull and are are unused by other geometry
        # The two sets may intersect, so for now just delete one of them. I haven't found a case yet
        # where this leaves out unwanted geometry

        bmesh.ops.delete(bm, geom=result['geom_interior'], context='TAGGED_ONLY')
        bm.normal_update()
        bmesh.ops.dissolve_limit(bm, angle_limit=self.planar_angle,
            verts=bm.verts, edges=bm.edges, use_dissolve_boundaries=False, delimit=set())
        bmesh.ops.triangulate(bm, faces=bm.faces)
        col_obj = create_col_object_from_bm(self,context, obj, bm, "UCX")
        bm.free()

        # Decimate (no bmesh op for this currently?)
        with TempModifier(col_obj, type='DECIMATE') as dec_mod:
            dec_mod.ratio = self.decimate_ratio
            dec_mod.use_symmetry = self.use_symmetry
            dec_mod.symmetry_axis = self.symmetry_axis

    def make_wall_collision(self, context, obj):
        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(obj.data).copy()
            bm.verts.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.select], context='VERTS')
        else:
            bm = bmesh.new()
            dg = context.evaluated_depsgraph_get()
            bm.from_object(obj, dg)

        if self.wall_fill_holes:
            result = bmesh.ops.holes_fill(bm, edges=bm.edges, sides=4)
            hole_edges = list(chain.from_iterable(f.edges for f in result['faces']))
            bmesh.ops.dissolve_edges(bm, edges=hole_edges, use_verts=True)
        bmesh.ops.split_edges(bm, edges=bm.edges)
        bmesh.ops.dissolve_limit(bm, angle_limit=radians(5.0),
            verts=bm.verts, edges=bm.edges, use_dissolve_boundaries=False, delimit=set())

        create_split_col_object_from_bm(self,context, obj, bm, self.thickness, self.offset)
        bm.free()

    def execute(self, context):
        obj = context.active_object

        if obj.mode != 'EDIT':
            # When working from object mode, it follows that there should be only one collision shape
            pattern = re.compile(rf"^U[A-Z][A-Z]_{obj.name}_\d+")
            for mesh in [mesh for mesh in bpy.data.meshes if pattern.match(mesh.name)]:
                bpy.data.meshes.remove(mesh)

        if self.shape == 'CUBE':
            self.make_aabb_collision(context, obj)

        elif self.shape == 'CYLINDER':
            self.make_cylinder_collision(context, obj)

        elif self.shape == 'CAPSULE':
            self.make_capsule_collision(context, obj)

        elif self.shape == 'SPHERE':
            self.make_sphere_collision(context, obj)

        elif self.shape == 'CONVEX':
            self.make_convex_collision(context, obj)

        elif self.shape == 'WALL':
            self.make_wall_collision(context, obj)

        return {'FINISHED'}

    def invoke(self, context, event):
        # Calculate initial properties
        try:
            calculate_parameters(self,context, context.object)

        except RuntimeError as e:
            self.report({'ERROR'}, str(e))


            return {'CANCELLED'}

        # Ideally this would execute once then show the popup dialog, doesn't seem possible
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        row = col.row(align=True)
        row.prop(self, 'shape')
        row.prop(self, 'wire', icon='MOD_WIREFRAME', text="")

        if self.shape in {'CUBE', 'CYLINDER'}:
            col.separator()
            col.prop(self, 'hollow')

            if self.hollow:
                col.prop(self, 'thickness')
                col.prop(self, 'offset')

        if self.shape == 'CUBE':
            col.prop(self, 'aabb_width')
            col.prop(self, 'aabb_height')
            col.prop(self, 'aabb_depth')

        elif self.shape == 'CYLINDER':
            col.prop(self, 'cyl_rotate')
            col.prop(self, 'cyl_sides')
            col.prop(self, 'cyl_radius1')
            col.prop(self, 'cyl_radius2')
            col.prop(self, 'cyl_height')
            col.prop(self, 'cyl_caps')

        elif self.shape == 'CAPSULE':
            col.prop(self, 'cap_radius')
            col.prop(self, 'cap_depth')

        elif self.shape == 'SPHERE':
            col.prop(self, 'sph_radius')

        elif self.shape == 'CONVEX':
            col.prop(self, 'planar_angle')
            col.prop(self, 'decimate_ratio')
            row = col.row(align=True, heading="Symmetrize")
            row.prop(self, 'use_symmetry', text="")
            row.prop(self, 'symmetry_axis', expand=True)

        elif self.shape == 'WALL':
            col.prop(self, 'thickness')
            col.prop(self, 'offset')
            col.prop(self, 'wall_fill_holes')


class _PT_CustomCol(bpy.types.Panel):

    bl_label = "CustomCol"
    bl_idname = "_PT_CustomCol"
    bl_space_type= 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GameDev'
    bl_options = {'DEFAULT_CLOSED'}

    def draw (self, context):
        layout = self.layout
        
        box = layout.box()
        col = box.column(align=False)
        col.label(text="Collision", icon='MESH_CUBE')

        row = col.row(align=True)
        row.operator('gamedev.collision_make', text="Make")
        row.operator('gamedev.collision_assign', text="Assign")
        row = col.row(align=True)
        row.operator('gamedev.collision_make_ubx', text="UBX")
        row = col.row(align=True)
        row.operator('gamedev.collision_make_ucx', text="UCX")
    

        box = layout.box()
        col = box.column(align=False)
        col.label(text="Auto Collision", icon='MESH_CUBE')
        row = col.row(align=True)
        row.operator('gamedev.collision_auto_ubx', text="UBX")


classes = (

GameDev_OT_collision_AutoUBX,
GameDev_OT_collision_makeUCX,
GameDev_OT_collision_makeUBX,
GameDev_OT_collision_assign,
GameDev_OT_collision_copy_to_linked,
GameDev_OT_collision_make,
_PT_CustomCol,

)


try:
    SpaceView3D.draw_handler_remove(SpaceView3D.my_handler, 'WINDOW')
except (AttributeError, ValueError):
    pass

SpaceView3D.my_handler = SpaceView3D.draw_handler_add(drawColWire, (), 'WINDOW', 'POST_VIEW')

def register():
    for cls in classes :
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)