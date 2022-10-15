
import bpy

from bpy.props import StringProperty, PointerProperty

from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from bpy.types import Panel, Menu , PropertyGroup , Operator
AddonName = __package__

class QuickSuffix_Props_(PropertyGroup):


    Suffix_1 : StringProperty(name= "Suffix_1")
    Suffix_2 : StringProperty(name= "Suffix_2")
    Suffix_3 : StringProperty(name= "Suffix_3")
    Suffix_4 : StringProperty(name= "Suffix_4")
    Suffix_5 : StringProperty(name= "Suffix_5")
    Suffix_6 : StringProperty(name= "Suffix_6")
    Suffix_7 : StringProperty(name= "Suffix_7")
    Suffix_8 : StringProperty(name= "Suffix_8")



class QuickSuffix_MT_presets(Menu):
    bl_label = "quicksuffix Presets"
    preset_subdir = "quicksuffix_prop"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class QuickSuffix_PT_presets(PresetPanel, Panel):
    bl_label = 'QuickSuffix Presets'
    preset_subdir = 'quicksuffix_prop_save'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'quick_suffix.preset_add'


class QuickSuffix_OT_add_preset(AddPresetBase, Operator):
    bl_idname = "quick_suffix.preset_add"
    bl_label = "Add a new preset"
    preset_menu = "QuickSuffix_MT_presets"

    # Variable used for all preset values
    preset_defines = ["quicksuffix = bpy.context.scene.quicksuffix_prop"]

    # Properties to store in the preset
    preset_values = [
        "quicksuffix.Suffix_1",
        "quicksuffix.Suffix_2",
        "quicksuffix.Suffix_3",
        "quicksuffix.Suffix_4",
        "quicksuffix.Suffix_5",
        "quicksuffix.Suffix_6",
        "quicksuffix.Suffix_7",
        "quicksuffix.Suffix_8",
        
    ]

    # Where to store the preset
    preset_subdir = "quicksuffix_prop_save"




class _PT_QuickSuffix(Panel):


    bl_label = "Quick Suffix"
    bl_idname = "_PT_QuickSuffix"
    bl_space_type= 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GameDev'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "objectmode"


    
    @classmethod
    def poll(cls, context):


        if bpy.context.preferences.addons[AddonName].preferences.bool_Enable_Quick_Suiffix == True:
            return True
        else:
            return False

            
    def draw_header_preset(self, _context):
        QuickSuffix_PT_presets.draw_panel_header(self.layout)


    def draw (self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop




        row= layout.row()
        row.label(text="QuickSuffix", icon='ARMATURE_DATA')
        row= layout.row()
        layout.prop(my_prop_grp, "Suffix_1")
        row= layout.row()
        layout.prop(my_prop_grp, "Suffix_2")
        row= layout.row()
        layout.prop(my_prop_grp, "Suffix_3")
        row= layout.row()
        layout.prop(my_prop_grp, "Suffix_4")
        row= layout.row()
        layout.prop(my_prop_grp, "Suffix_5")
        row= layout.row()
        layout.prop(my_prop_grp, "Suffix_6")
        row= layout.row()
        layout.prop(my_prop_grp, "Suffix_7")
        row= layout.row()
        layout.prop(my_prop_grp, "Suffix_8")
        row= layout.row()
        row.operator ("suffix.piemenu", icon = "EVENT_F12", text="To open menu Press:")



class VIEW3D_MT_PIE_Suffix(Menu):


    # label is displayed at the center of the pie menu.
    bl_label = "SuffixSelection"
    bl_idname = "_MT_Suffix.Selection_MT_"

    @classmethod
    def poll(cls, context):
        if context.object.mode == "OBJECT":
            return True
        return False


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop

        # SuffixOne.bl_label.replace = str(my_prop_grp.Suffix_1)



        pie = layout.menu_pie()

        if my_prop_grp.Suffix_1 == "":
            pie.operator("suffix.one",text = 'SuffixOne')
        else:
            pie.operator("suffix.one",text = my_prop_grp.Suffix_1)


        if my_prop_grp.Suffix_2 == "":
            pie.operator("suffix.two",text = 'SuffixTwo')
        else:
            pie.operator("suffix.two",text = my_prop_grp.Suffix_2)


        if my_prop_grp.Suffix_3 == "":
            pie.operator("suffix.three",text = 'SuffixThree')
        else:
            pie.operator("suffix.three",text = my_prop_grp.Suffix_3)


        if my_prop_grp.Suffix_4 == "":
            pie.operator("suffix.four",text = 'SuffixFour')
        else:
            pie.operator("suffix.four",text = my_prop_grp.Suffix_4)


        if my_prop_grp.Suffix_5 == "":
            pie.operator("suffix.five",text = 'SuffixFive')
        else:
            pie.operator("suffix.five",text = my_prop_grp.Suffix_5)


        if my_prop_grp.Suffix_6 == "":
            pie.operator("suffix.six",text = 'SuffixSix')
        else:
            pie.operator("suffix.six",text = my_prop_grp.Suffix_6)


        if my_prop_grp.Suffix_7 == "":
            pie.operator("suffix.seven",text = 'SuffixSeven')
        else:
            pie.operator("suffix.seven",text = my_prop_grp.Suffix_7)


        if my_prop_grp.Suffix_8 == "":
            pie.operator("suffix.eight",text = 'SuffixEight')
        else:
            pie.operator("suffix.eight",text = my_prop_grp.Suffix_8)





 #############################################################
        #SuffixOne

class SuffixOne(Operator):

    bl_idname = "suffix.one"
    bl_label = "SuffixOne"


    @classmethod
    def poll (cls, context):
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop




        if my_prop_grp.Suffix_1 =='':
            return False

        return True

    def execute(self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop


        objectsName =  (bpy.context.active_object.name +'_'+ my_prop_grp.Suffix_1)
        bpy.context.active_object.name = (objectsName)






        return {'FINISHED'}

 #############################################################
        #SuffixTwo

class SuffixTwo(Operator):

    bl_idname = "suffix.two"
    bl_label = "SuffixTwo"
    @classmethod
    def poll (cls, context):
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop




        if my_prop_grp.Suffix_2 =='':
            return False

        return True

    def execute(self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop



        objectsName =  (bpy.context.active_object.name +'_'+ my_prop_grp.Suffix_2)
        bpy.context.active_object.name = (objectsName)






        return {'FINISHED'}

 #############################################################
        #SuffixThree

class SuffixThree(Operator):

    bl_idname = "suffix.three"
    bl_label = "SuffixThree"

    @classmethod
    def poll (cls, context):
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop




        if my_prop_grp.Suffix_3 =='':
            return False

        return True
    def execute(self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop

        objectsName =  (bpy.context.active_object.name +'_'+ my_prop_grp.Suffix_3)
        bpy.context.active_object.name = (objectsName)






        return {'FINISHED'}

 #############################################################
        #SuffixFour

class SuffixFour(Operator):

    bl_idname = "suffix.four"
    bl_label = "SuffixFour"

    @classmethod
    def poll (cls, context):
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop




        if my_prop_grp.Suffix_4 =='':
            return False

        return True

    def execute(self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop

        objectsName =  (bpy.context.active_object.name +'_'+ my_prop_grp.Suffix_4)
        bpy.context.active_object.name = (objectsName)






        return {'FINISHED'}

 #############################################################
        #SuffixFive

class SuffixFive(Operator):

    bl_idname = "suffix.five"
    bl_label = "SuffixFive"

    @classmethod
    def poll (cls, context):
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop




        if my_prop_grp.Suffix_5 =='':
            return False

        return True

    def execute(self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop

        objectsName =  (bpy.context.active_object.name +'_'+ my_prop_grp.Suffix_5)
        bpy.context.active_object.name = (objectsName)






        return {'FINISHED'}


 #############################################################
        #SuffixSix

class SuffixSix(Operator):

    bl_idname = "suffix.six"
    bl_label = "SuffixSix"

    @classmethod
    def poll (cls, context):
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop




        if my_prop_grp.Suffix_6 =='':
            return False

        return True

    def execute(self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop

        objectsName =  (bpy.context.active_object.name +'_'+ my_prop_grp.Suffix_6)
        bpy.context.active_object.name = (objectsName)






        return {'FINISHED'}


 #############################################################
        #SuffixSeven

class SuffixSeven(Operator):

    bl_idname = "suffix.seven"
    bl_label = "SuffixSeven"

    @classmethod
    def poll (cls, context):
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop




        if my_prop_grp.Suffix_7 =='':
            return False

        return True

    def execute(self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop

        objectsName =  (bpy.context.active_object.name +'_'+ my_prop_grp.Suffix_7)
        bpy.context.active_object.name = (objectsName)






        return {'FINISHED'}



 #############################################################
        #SuffixEight

class SuffixEight(Operator):

    bl_idname = "suffix.eight"
    bl_label = "SuffixEight"

    @classmethod
    def poll (cls, context):
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop




        if my_prop_grp.Suffix_8 =='':
            return False

        return True

    def execute(self, context):
        layout = self.layout
        scene = context.scene
        my_prop_grp = scene.quicksuffix_prop

        objectsName =  (bpy.context.active_object.name +'_'+ my_prop_grp.Suffix_8)
        bpy.context.active_object.name = (objectsName)






        return {'FINISHED'}


class _OT_PieMenu(Operator):

    bl_idname = "suffix.piemenu"
    bl_label = "OP_PieMenu"


    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="_MT_Suffix.Selection_MT_")





        return {'FINISHED'}



classes = ( 



QuickSuffix_Props_,
_PT_QuickSuffix,
VIEW3D_MT_PIE_Suffix,
SuffixOne,
SuffixTwo,
SuffixThree,
SuffixFour,
SuffixFive,
SuffixSix,
SuffixSeven,
SuffixEight,
_OT_PieMenu,
QuickSuffix_MT_presets,
QuickSuffix_PT_presets,
QuickSuffix_OT_add_preset,

)


def register():
    for cls in classes :
        bpy.utils.register_class(cls)

    bpy.types.Scene.quicksuffix_prop = PointerProperty(type=QuickSuffix_Props_)


def unregister():
    for cls in classes :
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.quicksuffix_prop