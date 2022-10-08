


import bpy
import os


class GameDev_Export_Prop(bpy.types.PropertyGroup):
    ExportDir: bpy.props.StringProperty(name="ExportDir",subtype='DIR_PATH')
    TransformOld: bpy.props.FloatVectorProperty(name="TransformOld", default=(0,0,0))
    
    
    

class GameDev_CustomExportPanel(bpy.types.Panel):
    bl_label = "Custom Export"
    bl_idname = "_PT_CustomExport"
    bl_space_type= 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GameDev'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        Prop = scene.export_Prop

        # Create a simple row.
        layout.label(text="CustomExport")

        row = layout.row()
        row.prop(Prop, "ExportDir")
        
        row = layout.row()
        row.operator ("gmaedev.custom_export", icon = "EXPORT", text="Export")










class GameDev_Export (bpy.types.Operator):
    bl_idname = "gmaedev.custom_export"
    bl_label = "Export"
    
    def execute(self, context):
        #place this in execute
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
            print (obj.name)
    
            
        parentobj.select_set(True)
           
        print ('Old Transform ='+ str(Export_Prop.TransformOld))  

        #set final export directroy and export 

        fn = os.path.join(Export_Prop.ExportDir, 'SM_'+parentobj.name)


        
           
        bpy.ops.export_scene.fbx(filepath=fn + ".fbx", check_existing=True, filter_glob='*.fbx',
        use_selection=True,apply_unit_scale=True,use_mesh_modifiers=True,
        use_mesh_modifiers_render=True, mesh_smooth_type='EDGE', use_subsurf=False,
        use_mesh_edges=False, use_tspace=True, use_triangles=False,
        use_custom_props=False, add_leaf_bones=False, bake_anim=True, 
        embed_textures=False, batch_mode='OFF', use_batch_own_dir=False,
        use_metadata=False, axis_forward='X', axis_up='-Z') 


        #apply the original transform
        print ('applying old transform')
        print ('Old Transform ='+ str(Export_Prop.TransformOld))
        parentobj.location = Export_Prop.TransformOld

        return {'FINISHED'}





