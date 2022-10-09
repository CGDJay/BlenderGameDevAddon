import bpy

from bpy.props import (
        EnumProperty,
        BoolProperty,
        FloatProperty,
        FloatVectorProperty,
        StringProperty,
        EnumProperty,
        BoolProperty,
        IntVectorProperty,
        IntProperty
)

from bpy.types import PropertyGroup
from bpy.props import PointerProperty

#-------------------------------------------------------
#PROPERTYGROUP

class CustomUV_Prop(PropertyGroup):

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
#Registration

classes = ( 

CustomUV_Prop ,

 )
def register():

    for cls in classes :
        bpy.utils.register_class(cls)

    bpy.types.Scene.CustomUVProps = PointerProperty(type=CustomUV_Prop)

def unregister():

    for cls in classes :
        bpy.utils.unregister_class(cls)


    del bpy.types.Scene.CustomUVProps
