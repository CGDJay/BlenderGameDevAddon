import bpy
from bpy.types import Menu, Operator


class VIEW3D_MT_PIE_QuickOps(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "_MT_Quick.Operations"
    bl_idname = "_MT_Quick.Operations"
    
    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        
        
#############################################################
        #type of operators
        
        pie.operator("quick.origin")
        pie.operator("remove.support")
        pie.operator("cylinder.reduce")
        pie.operator("auto.smooth")
        pie.operator("foating.geo")
        pie.operator("quick.resolve")
        pie.operator("quick.warp")
        pie.operator("quick.lattice")
        
      

