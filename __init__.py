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

# reload packages

if "bpy" in locals():
    import importlib
    importlib.reload (QuickOps.QuickOps_pnl)
    importlib.reload (QuickOps.QuickOps_op)

    importlib.reload (CustomUV.CustomUVTools_op)
    importlib.reload (CustomUV.CustomUVTools_pnl)


    importlib.reload (QuickSuffix)
    importlib.reload (MossCap.MossCap)
    importlib.reload (PivotPainter)

    importlib.reload (VCM.vcm_globals)
    importlib.reload (VCM.vcm_helpers)
    importlib.reload (VCM.vcm_prop)
    importlib.reload (VCM.vcm_menus)
    importlib.reload (VCM.vcm_Ops)



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
	IntVectorProperty,
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


from .QuickOps.QuickOps_pnl import*  

from .QuickOps.QuickOps_op import *

from . CustomUV.CustomUVTools_op import * 

from . CustomUV.CustomUVTools_pnl import *

from . CustomUV.utilities_uv import *

from . import QuickSuffix 

from .BatchImporter.BatchImportFBX import * 

from .MossCap.MossCap import *

from . import PivotPainter

from . import TTP

from . import CustomExport

from . import LoadPBRTexture

from . import CollisionTools



from .vertex_animation import *

from .VCM.vcm_prop import *
from .VCM.vcm_menus import *
from .VCM.vcm_Ops import *

# not used in this file
from .VCM.vcm_globals import *
from .VCM.vcm_helpers import *




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



#-------------------------------------------------------
#PROPERTYGROUP

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

#-------------------------------------------------------
# Quick Ops

VIEW3D_MT_PIE_QuickOps,
Quick_Origin ,
Remove_Support ,
cylinder_reduce ,
Auto_Smooth ,
Foalting_Geo ,
Quick_Resolve ,
QuickWarp ,
QuickLattice ,

#-------------------------------------------------------
# UV Tools

ColorAtlasTools_panel,
CustomUVTools_panel,
ColorAtlasToolsUV0_panel ,
VIEW3D_MT_PIE_customUVTools,



UI_PT_texel_density_checker,
Texel_Density_Check,
Texel_Density_Set,
Calculated_To_Set, 
Preset_Set, 

Tools_panel,

SetIsland_Op ,
AtlasShiftBack_Op ,
AtlasShiftNext_Op ,
AtlasShiftDown_Op ,
AtlasShiftUp_Op ,
LoadTexture,
MaterialSetup ,

UdimAtlasShiftNext_Op ,
UdimAtlasShiftBack_Op ,
UdimAtlasShiftDown_Op ,
UdimAtlasShiftUp_Op ,
UdimAtlasShiftReset_Op ,

UdimAtlasShiftSnapToPoint_Op1 ,
UdimAtlasShiftSnapToPoint_Op2 ,
UdimAtlasShiftSnapToPoint_Op3 ,
UdimAtlasShiftSnapToPoint_Op4 ,
UdimAtlasShiftSnapToPoint_Op5 ,
UdimAtlasShiftSnapToPoint_Op6 ,
UdimAtlasShiftSnapToPoint_Op8 ,

UdimAtlasShiftSnapToPoint_OpMinus1 ,
UdimAtlasShiftSnapToPoint_OpMinus2 ,
UdimAtlasShiftSnapToPoint_OpMinus3 ,
UdimAtlasShiftSnapToPoint_OpMinus4 ,
UdimAtlasShiftSnapToPoint_OpMinus5 ,
UdimAtlasShiftSnapToPoint_OpMinus6 ,
UdimAtlasShiftSnapToPoint_OpMinus7 ,
UdimAtlasShiftSnapToPoint_OpMinus8,
ClipboardShader ,
Rectify,
unwrap,
Straighten,
Mark,



#-------------------------------------------------------
# Quick suffix


QuickSuffix.QuickSuffix_Props_,
QuickSuffix._PT_QuickSuffix,
QuickSuffix.VIEW3D_MT_PIE_Suffix,
QuickSuffix.SuffixOne,
QuickSuffix.SuffixTwo,
QuickSuffix.SuffixThree,
QuickSuffix.SuffixFour,
QuickSuffix.SuffixFive,
QuickSuffix.SuffixSix,
QuickSuffix.SuffixSeven,
QuickSuffix.SuffixEight,
QuickSuffix._OT_PieMenu,


#-------------------------------------------------------
# Vertex Color Master

VertexColorMasterProperties,
vcm_MossVertexColors,
VERTEXCOLORMASTER_OT_QuickFill,
VERTEXCOLORMASTER_OT_Fill,
VERTEXCOLORMASTER_OT_Invert,
VERTEXCOLORMASTER_OT_Posterize,
VERTEXCOLORMASTER_OT_Remap,
VERTEXCOLORMASTER_OT_CopyChannel,
VERTEXCOLORMASTER_OT_EditBrushSettings,
VERTEXCOLORMASTER_OT_NormalsToColor,
VERTEXCOLORMASTER_OT_IsolateChannel,
VERTEXCOLORMASTER_OT_ApplyIsolatedChannel,
VERTEXCOLORMASTER_OT_RandomizeMeshIslandColors,
VERTEXCOLORMASTER_OT_RandomizeMeshIslandColorsPerChannel,
VERTEXCOLORMASTER_OT_FlipBrushColors,
VERTEXCOLORMASTER_OT_Gradient,
VERTEXCOLORMASTER_OT_BlurChannel,
vcm_EdgeWare,
VERTEXCOLORMASTER_PT_MainPanel,
VERTEXCOLORMASTER_MT_PieMain,


BatchAssetLibrary,
ImportButton,
ExportButton,

GameDev_MossCapSettings,
GameDev_MossCap_PT_,
GameDev_MossCap_OP_Create,
GameDev_ClipboardMossShader,


PivotPainter.UE4_PivotPainterProperties,
PivotPainter.VIEW3D_PT_pivot_painter_Object,																							
PivotPainter.PPB_OT_CreateTextures,
PivotPainter.PPB_OT_ShowHideExtraOptions,
PivotPainter.PPB_OT_ShowHideExperimentalOptions,
PivotPainter.PPB_OT_CreateSelectOrder,
PivotPainter.PivotToVcol,


VAT_Properties,
OBJECT_OT_ProcessAnimMeshes,
VIEW3D_PT_VertexAnimation,

TTP.TESS_props_group,
TTP.TESS_OT_tesselate_plane,
TTP.TESS_PT_tesselate_UI,
TTP.TESS_PT_subsettings_UI,

LoadPBRTexture.GameDev_LoadPBRMat_Prop,
LoadPBRTexture.GameDev_LoadPBRMat,
LoadPBRTexture.GameDev_LoadPBRMatPanel,


CustomExport.GameDev_Export_Prop,
CustomExport.GameDev_CustomExportPanel,
CustomExport.GameDev_Export,

CollisionTools.GameDev_OT_collision_assign,
CollisionTools.GameDev_OT_collision_copy_to_linked,
CollisionTools.GameDev_OT_collision_make,
CollisionTools._PT_CustomCol,




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

if __name__ == "main":
    disable_Used_kmi()

addon_keymaps = []




#-------------------------------------------------------
#REGISTER

def register():
    



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
    
    

    bpy.types.Scene.loadpbrmat_Prop = bpy.props.PointerProperty(type=LoadPBRTexture.GameDev_LoadPBRMat_Prop)
    
    bpy.types.Scene.export_Prop = bpy.props.PointerProperty(type=CustomExport.GameDev_Export_Prop)

    bpy.types.Scene.vat_prop = PointerProperty(type= VAT_Properties)

    bpy.types.Scene.pivot_painter = PointerProperty(type = PivotPainter.UE4_PivotPainterProperties)

    bpy.types.Scene.ToolSettings = PointerProperty(type=Settings)

    bpy.types.Scene.my_prop_grp = PointerProperty(type=QuickSuffix.QuickSuffix_Props_)

    bpy.types.Scene.vertex_color_master_settings = PointerProperty(type=VertexColorMasterProperties)
    
    bpy.types.Scene.MossSettings = PointerProperty(type=GameDev_MossCapSettings)

    bpy.types.Scene.ttp_props = PointerProperty(type=TTP.TESS_props_group)
    
    disable_Used_kmi()
    
#-------------------------------------------------------
#KeyMaps



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



    bpy.app.handlers.load_post.remove(load_handler)

    unsubscribe_mode_change()

    for cls in classes :
        bpy.utils.unregister_class(cls)

    
    del bpy.types.Scene.pivot_painter
    del bpy.types.Scene.ToolSettings
    del bpy.types.Scene.my_prop_grp
    del bpy.types.Scene.vertex_color_master_settings
    del bpy.types.Scene.MossSettings
    del bpy.types.Scene.vat_prop
    del bpy.types.Scene.ttp_props
    del bpy.types.Scene.export_Prop
    del bpy.types.Scene.loadpbrmat_Prop
    
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
        
        
