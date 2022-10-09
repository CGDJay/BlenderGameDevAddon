import bpy

import addon_utils
import rna_keymap_ui 
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


classes = ( 

Panel_Preferences,


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


def register():
    for cls in classes :
        bpy.utils.register_class(cls)

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
    

def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)

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
