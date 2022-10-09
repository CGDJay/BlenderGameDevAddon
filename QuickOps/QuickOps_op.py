import bpy
from bpy.types import Menu, Operator
import operator
import numpy
import mathutils
#############################################################
        #HardsurfaceRemesh     

class QuickWarp (bpy.types.Operator):
    
    bl_idname = "quick.warp"
    bl_label = "QuickWarp"

    @classmethod
    def poll (cls, context):
            obj = context.object
            
            
            if obj is not None:
                    if obj.mode == "OBJECT":
                            return True
    
            return False    

    
    
    def execute(self, context): 
        
                
        obj = context.object

        DeformObj=bpy.context.active_object

        #set up empties for To and from on the warp modifier

        emptyFrom = bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location= ((bpy.context.scene.cursor.location)+mathutils.Vector((0, 0, 100))) , scale=(1, 1, 1))

        bpy.context.object.empty_display_size = 100

        bpy.context.active_object.name = 'EmptyFrom'

        emptyFrom=bpy.context.active_object


        emptyTo=bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=((bpy.context.scene.cursor.location)-mathutils.Vector((0, 0, 100))) , scale=(1, 1, 1))


        bpy.context.object.empty_display_size = 100

        bpy.context.active_object.name = 'EmptyTo'

        emptyTo=bpy.context.active_object


        #Add warp modifier and modifiy settings to assign empties and change dalloff radius

        WARP=DeformObj.modifiers.new(name='Warp', type="WARP")
        WARP.object_from = emptyFrom
        WARP.object_to = emptyTo
        WARP.falloff_radius = 150

        return {'FINISHED'}


        







   
            
        return {'FINISHED'}         
#############################################################
        #FloatingGeo        

class Foalting_Geo (bpy.types.Operator):
    
    bl_idname = "foating.geo"
    bl_label = "FoaltingGeo" 

    @classmethod
    def poll (cls, context):
            obj = context.object
            
            
            if obj is not None:
                    if obj.mode == "OBJECT":
                            return True
    
            return False      
    
    def execute(self, context):   

        target_obj = context.active_object
        tool_objs = [o for o in context.selected_objects if o != target_obj]

        SHRINK = 'SHRINKWRAP'
        DATA = 'DATA_TRANSFER'
        
        for obj in tool_objs:
            bool_mod = target_obj.modifiers.new(name='Float_' + obj.name, type=SHRINK)
            bool_mod.wrap_method = 'PROJECT'
            bool_mod.target = obj
            
            
            
            data_mod = target_obj.modifiers.new(name='Float_' + obj.name, type=DATA)
            data_mod.object = obj
            data_mod.use_loop_data = True
            data_mod.data_types_loops = {'CUSTOM_NORMAL'}
            data_mod.loop_mapping = 'POLYINTERP_LNORPROJ'
            data_mod.vertex_group = vertex_group = "Group"
                                
            
            return {'FINISHED'}
#############################################################
        #QuickOrigin

class Quick_Origin(bpy.types.Operator):
    
    bl_idname = "quick.origin"
    bl_label = "QuickOrigin"
    
    
    def execute(self, context):     
        if context.active_object.mode == 'EDIT':
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
            bpy.ops.object.editmode_toggle()
        
        elif context.active_object.mode == 'OBJECT':
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')


            
        return {'FINISHED'}  
    
    
#############################################################
        #AutoSmooth
    
class Auto_Smooth(bpy.types.Operator):
    
    bl_idname = "auto.smooth"
    bl_label = "AutoSmooth"
    
    
    def execute(self, context):     
        
        if context.active_object.mode == 'EDIT':
            bpy.ops.mesh.faces_shade_smooth()
            bpy.context.object.data.use_auto_smooth = True
            bpy.context.object.data.auto_smooth_angle = 1.0472

            
        elif context.active_object.mode == 'OBJECT':
            bpy.ops.object.shade_smooth()
            bpy.context.object.data.use_auto_smooth = True
            bpy.context.object.data.auto_smooth_angle = 1.0472
    
            
        return {'FINISHED'} 
    
    
#############################################################
        #RemoveSupportLoops    
    
class Remove_Support(bpy.types.Operator):
    
    bl_idname = "remove.support"
    bl_label = "RemoveSupports"
    
    
    def execute(self, context):     
       
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        bpy.context.object.modifiers["Decimate"].angle_limit = 0.10472


            
        return {'FINISHED'} 
    
    
    
#############################################################
        #Cylinder Reduce      

class cylinder_reduce(bpy.types.Operator):
    
    bl_idname = "cylinder.reduce"
    bl_label = "CylinderReduce"

    @classmethod
    def poll (cls, context):
            obj = context.object
            
            
            if obj is not None:
                    if obj.mode == "EDIT":
                            return True
    
            return False    
    
    
    
    def execute(self, context):     
       
        
        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.mesh.select_nth()
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.dissolve_mode(use_verts=True)
   
            
        return {'FINISHED'} 
    
#############################################################
        #QuickResolve     

class Quick_Resolve(bpy.types.Operator):
    
    bl_idname = "quick.resolve"
    bl_label = "QuickResolve"

    @classmethod
    def poll (cls, context):
            obj = context.object
            
            
            if obj is not None:
                    if obj.mode == "EDIT":
                            return True
    
            return False  
    
    
    def execute(self, context):     
       
        
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.tris_convert_to_quads()

   
            
        return {'FINISHED'}   
    
#############################################################
        #SortModifiers     

class QuickLattice(bpy.types.Operator):
    bl_idname = "quick.lattice"
    bl_label = "QuickLattice" 


    #poll check for if the user is in object mode 
    @classmethod
    def poll (cls, context):
            obj = context.object
            
            
            if obj is not None:
                    if obj.mode == "OBJECT":
                            return True

            return False     
        
         
    
    
    def execute(self, context):
        

                
        obj = context.object



        local_bbox_center = 0.125 * sum((mathutils.Vector(b) for b in obj.bound_box), mathutils.Vector())
        
        global_bbox_center = obj.matrix_world @ local_bbox_center
        
        DeformObj=bpy.context.active_object
        
        ObjDimensions=DeformObj.dimensions
        
        print (ObjDimensions)
        
        #set up Lattice

        LatticeObj = bpy.ops.object.add(type='LATTICE', align='WORLD', location= (global_bbox_center) , scale=(1, 1, 1))

        

        bpy.context.active_object.name = 'Lattice'
        
        LatticeObj=bpy.context.active_object
        
        LatticeObj.dimensions = ObjDimensions
       
        LatticeObj.rotation_euler = DeformObj.rotation_euler
       
        LatticeObj.show_in_front= True
        
        
        
        #Add Lattice modifier and modifiy settings to assign Lattice 

        Lattice=DeformObj.modifiers.new(name='Lattice', type="LATTICE")
        Lattice.object = LatticeObj
        
        return {'FINISHED'}

      
    
classes = ( 

Quick_Origin ,
Remove_Support ,
cylinder_reduce ,
Auto_Smooth ,
Foalting_Geo ,
Quick_Resolve ,
QuickWarp ,
QuickLattice ,


)


def register():
    for cls in classes :
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)
