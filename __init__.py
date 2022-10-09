# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "BlenderGameDevAddon",
    "author" : "CGDJay",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "CGDJay"
}


#-------------------------------------------------------


from msilib.schema import Icon
from multiprocessing import context
import bpy
import os
import subprocess
import sys
import rna_keymap_ui 
import addon_utils

from bpy.app.handlers import persistent

from bpy.types import  AddonPreferences, PropertyGroup, Panel, Menu
from bpy.props import (
	StringProperty,
	BoolProperty,
	IntProperty,
	FloatProperty,
	FloatVectorProperty,
	EnumProperty,
	PointerProperty,
)

#-------------------------------------------------------

# install pip and pyperclip to copy shader text

drawInfo = {
    "handler": None,
}
# path to python.exe
python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
 
# upgrade pip
subprocess.call([python_exe, "-m", "ensurepip"])
subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
 
# install required packages
subprocess.call([python_exe, "-m", "pip", "install", "pyperclip"])
subprocess.call([python_exe, "-m", "pip", "install", "opencv-python"])
subprocess.call([python_exe, "-m", "pip", "install", "triangle"])



#-------------------------------------------------------

# module registrastion method


import importlib

module_names = (
    "QuickSuffix",

    "PivotPainter",

    "QuickOps.QuickOps_pnl",
    "QuickOps.QuickOps_op",

    "CustomUV.CustomUVTools_op",
    "CustomUV.CustomUVTools_pnl",


    "BatchImporter.BatchImportFBX",

    "MossCap.MossCap",

    "TTP",

    "CustomExport",

    "LoadPBRTexture",

    "CollisionTools",

    "vertex_animation",

    "VCM.vcm_prop",
    "VCM.vcm_menus",
    "VCM.vcm_Ops",

    

)

modules = []

for module_name in module_names:
    if module_name in locals():
        modules.append(importlib.reload(locals()[module_name]))
    else:
        modules.append(importlib.import_module("." + module_name, package=__package__))


#-------------------------------------------------------

# mode change defenitions
def callback_mode_change(object, data):
    if bpy.context.active_object.mode == "SCULPT":
        bpy.context.preferences.inputs.use_mouse_emulate_3_button=True
    else:
        bpy.context.preferences.inputs.use_mouse_emulate_3_button=False

owner = object()

def subscribe_mode_change():
    subscribe_to = (bpy.types.Object, "mode")

    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=owner,
        args=(owner,"mode",),
        notify=callback_mode_change,
    )

def unsubscribe_mode_change():
    bpy.msgbus.clear_by_owner(owner)

@persistent
def load_handler(dummy):
    subscribe_mode_change()


def enable_addon(addon_module_name):

    loaded_default, loaded_state = addon_utils.check(addon_module_name)

    if not loaded_state:
        addon_utils.enable(addon_module_name, default_set=True)




#-------------------------------------------------------
#PROPERTYGROUP

class Settings(PropertyGroup):
#-------------------------------------------------------
#BATCHLIBRARYPROPERTYGROUP

    DirectoryPath:StringProperty(
    name="filepath",
    description="Choose a directory to import StaticMesh(s)",
    maxlen=512,
    default=os.path.join("//"),
    subtype='DIR_PATH')

#-------------------------------------------------------
#PALLATATLASPROPERTYGROUP
    AtlasSpace: FloatVectorProperty(
        name="Atlas Space",
        description="Distance between atlas chunks (/UdimTiles)",
        size=2,
        precision=4,
        soft_min=-1.0,
        soft_max=1.0,
        step=1,
        default=(1 , 1 ),
        
        )
    TextureType = (('0','16X16grid',''),('1','16X16gridColor',''),('2','16X16gridGreyScale',''),)
    Texture_Type: EnumProperty(name="", items = TextureType)
    


#-------------------------------------------------------
#TEXELTOOLPROPERTYGROUP

    uv_space: StringProperty(
        name="",
        description="wasting of uv space",
        default="0")
    
    density: StringProperty(
        name="",
        description="Texel Density",
        default="0")
    
    density_set: StringProperty(
        name="",
        description="Texel Density",
        default="0")
    
    tex_size = (('0','512px',''),('1','1024px',''),('2','2048px',''),('3','4096px',''))
    texture_size: EnumProperty(name="", items = tex_size)

    padding : IntProperty(
        description="padding size in pixels",
        default = 4,
        min = 0,
        max = 256
        )
        
    
    set_method_list = (('0','Each',''),('1','Average',''))
    set_method: EnumProperty(name="", items = set_method_list)


#-------------------------------------------------------
#TEXELTOOLPROPERTYGROUP

class Panel_Preferences(AddonPreferences):
    bl_idname = __package__
    #properties menu
    bool_Enable_Quick_Suiffix : BoolProperty(name="Enable quick suffix panel", default=True)
    bool_Enable_UVAtlas : BoolProperty(name="Enable UV atlas", default=True)
    bool_Enable_UVTools : BoolProperty(name="Enable UV tools", default=True)
    bool_Enable_VPM : BoolProperty(name="Enable Vertex paint master", default=True)
    bool_Enable_BatchLibrary : BoolProperty(name="Enable BatchLibrary", default=True)
    bool_Enable_MossCap : BoolProperty(name="Enable MossCap", default=True)
    bool_Enable_PivotPainter : BoolProperty(name="Enable PivotPainter", default=True)
    bool_Enable_VAT : BoolProperty(name="Enable Vertex Animation Texture", default=True)



    
    
    def draw (self, context):
        layout = self.layout
     
        box = layout.box()
        col = box.column()
        col.label(text="Keymap List:",icon="KEYINGSET")


        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        old_km_name = ""
        get_kmi_l = []
        for km_add, kmi_add in addon_keymaps:
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname:
                    if kmi_add.name == kmi_con.name:
                        get_kmi_l.append((km,kmi_con))

        get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

        for km, kmi in get_kmi_l:
            if not km.name == old_km_name:
                col.label(text=str(km.name),icon="DOT")
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
            col.separator()
            old_km_name = km.name


       
        box= layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(text="Properties:",icon="TOOL_SETTINGS")

        box= layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(icon="DOT")
        box.prop(self, "bool_Enable_Quick_Suiffix")

        box= layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(icon="DOT")
        box.prop(self, "bool_Enable_UVTools")

        box= layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(icon="DOT")
        box.prop(self, "bool_Enable_UVAtlas")
       
        box= layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(icon="DOT")
        box.prop(self, "bool_Enable_VPM")
        
        box= layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(icon="DOT")
        box.prop(self, "bool_Enable_BatchLibrary")

        box= layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(icon="DOT")
        box.prop(self, "bool_Enable_MossCap")

        box= layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(icon="DOT")
        box.prop(self, "bool_Enable_PivotPainter")

        box= layout.box()
        box.scale_y = 2
        box.scale_x = 2
        box.label(icon="DOT")
        box.prop(self, "bool_Enable_VAT")

#-------------------------------------------------------
#CLASSES

classes = ( 

Panel_Preferences,
Settings ,

 )


#-------------------------------------------------------
#KeyMaps
disabled_kmis = []

# Find a keymap item by traits.
# Returns None if the keymap item doesn't exist.


def get_active_kmi(space: str, **kwargs) -> bpy.types.KeyMapItem:
    kc = bpy.context.window_manager.keyconfigs.user
    km = kc.keymaps.get(space)
    if km:
        for kmi in km.keymap_items:
            for key, val in kwargs.items():
                if getattr(kmi, key) != val and val is not None:
                    break
            else:
                return kmi

def disable_Used_kmi():
    # Be explicit with modifiers shift/ctrl/alt so we don't
    # accidentally disable a different keymap with same traits.
    kmi = get_active_kmi("Mesh",
                         idname="mesh.split",
                         type='Y',
                         shift=False,
                         ctrl=False,
                         alt=False)

    kmi2 = get_active_kmi("Mesh",
                        idname="wm.call_menu",
                        type='U',
                        shift=False,
                        ctrl=False,
                        alt=False)
    kmi1 = get_active_kmi("Screen",
                        idname="render.render",
                        type='F12',
                        shift=False,
                        ctrl=False,
                        alt=False)

    if kmi is not None:
        kmi.active = False
        kmi1.active = False
        kmi2.active = False
        disabled_kmis.append(kmi)
        disabled_kmis.append(kmi1)
        disabled_kmis.append(kmi2)


addon_keymaps = []


#-------------------------------------------------------
#REGISTER

def register():
    
    for mod in modules:
        mod.register()


    if bpy.app.version >= (2, 81, 0):
        default_brush_name = 'Add'

    bpy.app.handlers.load_post.append(load_handler)

    subscribe_mode_change()
    enable_addon(addon_module_name="add_curve_extra_objects")
    enable_addon(addon_module_name="add_mesh_extra_objects")
    enable_addon(addon_module_name="add_mesh_BoltFactory")
    enable_addon(addon_module_name="io_import_images_as_planes")
    enable_addon(addon_module_name="mesh_looptools")
    enable_addon(addon_module_name="object_boolean_tools")

    for cls in classes :
        bpy.utils.register_class(cls)

    bpy.types.Scene.ToolSettings = PointerProperty(type=Settings)


#-------------------------------------------------------
#KeyMaps

    disable_Used_kmi()
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        
        kmi = km.keymap_items.new('wm.call_menu_pie', type = 'Y', value = 'PRESS', ctrl = False, shift = False)
        kmi.properties.name = "_MT_Quick.Operations"

        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('wm.call_menu_pie', type = 'F12', value = 'PRESS', ctrl = False, shift = False)
        kmi.properties.name = "_MT_Suffix.Selection_MT_"

        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('wm.call_menu_pie', type = 'U', value = 'PRESS', ctrl = False, shift = False)
        kmi.properties.name = "_MT_uv.customtools"

        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Vertex Paint')
        # pie menu

        kmi = km.keymap_items.new('wm.call_menu_pie', 'V', 'PRESS')
        kmi.properties.name = "VERTEXCOLORMASTER_MT_PieMain"
        kmi.active = True
        addon_keymaps.append((km, kmi))


        # override 'x' to use VCM flip brush colors
        kmi = km.keymap_items.new('vertexcolormaster.brush_colors_flip', 'X', 'PRESS')
        kmi.active = True
        addon_keymaps.append((km, kmi))
    
#-------------------------------------------------------
#UNREGISTER   
       
    ...

def unregister():

    for mod in modules:
        mod.unregister()

    bpy.app.handlers.load_post.remove(load_handler)

    unsubscribe_mode_change()

    for cls in classes :
        bpy.utils.unregister_class(cls)


    del bpy.types.Scene.ToolSettings
    
    
    
    
#-------------------------------------------------------
#KeyMaps

    # unregister shortcuts
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps['3D View']
    
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
            wm.keyconfigs.addon.keymaps.remove(km)
        except ReferenceError as e:
            e
            
    addon_keymaps.clear()


     
if __name__ == '__main__':
    register()
    disable_Used_kmi()
        
        
