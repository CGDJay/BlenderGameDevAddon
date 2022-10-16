import bpy


drawInfo = {
    "handler": None,
}

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




def register():
    bpy.app.handlers.load_post.append(load_handler)
    
    subscribe_mode_change()

def unregister():
    
    bpy.app.handlers.load_post.remove(load_handler)

    unsubscribe_mode_change()