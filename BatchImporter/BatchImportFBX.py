from ast import Num
from gettext import Catalog
import os
import re
from pickle import OBJ
from re import X
from tokenize import Number
from unicodedata import name
import bpy
from bpy.types import PropertyGroup, Panel,Operator

AddonName = __package__

from bpy.props import (
	StringProperty,
	PointerProperty,
    BoolProperty,
)

AddonName = __package__

class BatchAssetLibrary(Panel):
    bl_label = "BatchAssetLibrary"
    bl_idname = "batchassetlibrary"
    bl_space_type= 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GameDev'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
      
        
        if bpy.context.preferences.addons[AddonName].preferences.bool_Enable_BatchLibrary == True:
            return True
        else:
            return False

    def draw (self, context):
        layout = self.layout
        scene = context.scene
        Props = scene.BatchImportProps

        row= layout.row()

        row.label(text="Batch import Asset library", icon='ASSET_MANAGER')
        
        row= layout.row()
        row.prop(Props,"DirectoryPath")

        row= layout.row()

        row.scale_y = 2
        row.scale_x = 2

        row.operator ("object.import_button", icon = "IMPORT", text="Import Into Library")

        row.operator ("object.export_button", icon = "EXPORT", text="export Into Library")


class ImportButton(Operator):
    """Tooltip"""
    bl_idname = "object.import_button"
    bl_label = "ImportButton"



    def execute(self, context):
        scene = context.scene
        Props = scene.BatchImportProps

        
        # put the location to the folder where the FBXs are located here in this fashion
        
        path_to_obj_dir = os.path.join(Props.DirectoryPath)


        # get list of all files in directory
        file_list = sorted(os.listdir(path_to_obj_dir))


        # get a list of files ending in 'fbx'
        obj_list = [item for item in file_list if item.endswith('.fbx')]

        # loop through the strings in obj_list and add the files to the scene

        for item in obj_list:
            path_to_file = os.path.join(path_to_obj_dir, item)
            bpy.ops.import_scene.fbx(filepath = path_to_file,
            use_custom_props = True
            )
        
            
            # if heavy importing is expected 
            # you may want use saving to main file after every import 

            #bpy.ops.wm.save_mainfile()

        bpy.ops.object.select_by_type(type='MESH')
        objs = [obj for obj in bpy.data.objects if obj.type in ["MESH", "CURVE"]]

        Size = 'Small'

        

                
        for obj in objs:
            
            if obj.dimensions.z >= 200:
                Size = 'Large'
            else:
                Size = 'Small'
            
            obj.asset_mark()

            obj.asset_data.tags.new(Size)
                        

        Metrics = re.compile(r"(\d+)X(\d+)") # edit this string
        for obj in objs:
            
            match = Metrics.match(obj.name)
            if match == None:
                print("no match for %s"  % obj.name)
            else:
                print("matched %s" % match.group(0))
                obj.asset_data.tags.new((match.group(0))+'M')

                

            

        return {'FINISHED'}


class ExportButton(Operator):
    """Tooltip"""
    bl_idname = "object.export_button"
    bl_label = "ExportButton"



    def execute(self, context):
        scene = context.scene
        Props = scene.BatchImportProps
        # put the location to the folder where the FBXs are located here in this fashion
        # this line will only work on windows ie C:\objects
        

        PropName='Tag'
        PropNumber=0

        bpy.ops.object.select_by_type(type='MESH')
        objs = [obj for obj in bpy.data.objects if obj.type in ["MESH"]]
        for obj in objs:
           
            PropNumber=0

            for tag_name in [tag.name for tag in obj.asset_data.tags]:
                PropName = (PropName)+str(PropNumber)
                obj[PropName] = tag_name
                PropNumber= PropNumber+1
                       
            


        for obj in objs:
            obj.select_set(True)
            path_to_obj_dir = os.path.join(Props.DirectoryPath, obj.name+'.fbx')
            bpy.ops.export_scene.fbx(
            filepath=path_to_obj_dir,
            use_selection=True,
            use_custom_props = True
        )
            break


                

            

        return {'FINISHED'}


class BatchImport_Prop(PropertyGroup):
#-------------------------------------------------------
#BATCHLIBRARYPROPERTYGROUP

    DirectoryPath:StringProperty(
    name="filepath",
    description="Choose a directory to import StaticMesh(s)",
    maxlen=512,
    default=os.path.join("//"),
    subtype='DIR_PATH')


classes = ( 
BatchImport_Prop,
BatchAssetLibrary,
ImportButton,
ExportButton,

)


def register():
    for cls in classes :
        bpy.utils.register_class(cls)

    bpy.types.Scene.BatchImportProps = PointerProperty(type=BatchImport_Prop)

def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.BatchImportProps