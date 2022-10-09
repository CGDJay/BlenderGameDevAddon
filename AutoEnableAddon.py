import bpy
import addon_utils

def enable_addon(addon_module_name):

    loaded_default, loaded_state = addon_utils.check(addon_module_name)

    if not loaded_state:
        addon_utils.enable(addon_module_name, default_set=True)
        print ('enabled'+addon_module_name)

def disable_addon(addon_module_name):

    loaded_default, loaded_state = addon_utils.check(addon_module_name)

    if loaded_state:
        addon_utils.disable(addon_module_name, default_set=False)


def register():
        
    enable_addon(addon_module_name="add_curve_extra_objects")
    enable_addon(addon_module_name="add_mesh_extra_objects")
    enable_addon(addon_module_name="add_mesh_BoltFactory")
    enable_addon(addon_module_name="io_import_images_as_planes")
    enable_addon(addon_module_name="mesh_looptools")
    enable_addon(addon_module_name="object_boolean_tools")

def unregister():

    disable_addon(addon_module_name="add_curve_extra_objects")
    disable_addon(addon_module_name="add_mesh_extra_objects")
    disable_addon(addon_module_name="add_mesh_BoltFactory")
    disable_addon(addon_module_name="io_import_images_as_planes")
    disable_addon(addon_module_name="mesh_looptools")
    disable_addon(addon_module_name="object_boolean_tools")