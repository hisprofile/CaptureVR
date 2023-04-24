bl_info = {
    "name": "CaptureVR",
    "description": "Capture's VR headset location and rotation.",
    "author": "hisanimations",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "View3D > ",
    "warning": "", # used for warning icon and text in addons panel
    "doc_url": "tba",
    "support": "COMMUNITY",
    "category": "View3D",
}

import bpy
from bpy.props import *
#caminfo = bpy.context.screen.areas[3].spaces[0].region_3d.view_matrix.inverted()

#print(caminfo.to_translation())
#print(caminfo.to_euler())

handle = bpy.app.handlers.frame_change_post

def captureVR(dummy = None):
    try:
        bpy.context.scene.capturespace
        if bpy.context.scene.capturespace.type == 'EMPTY': raise
    except:
        return None

    props = bpy.context.scene.captureVRprops
    caminfo = bpy.context.scene.capturespace.region_3d.view_matrix.inverted()
    cam = bpy.context.scene.camera
    if props.followVR and bpy.context.screen.is_animation_playing:
        cam.location = caminfo.to_translation()
        cam.rotation_euler = caminfo.to_euler()
        cam.keyframe_insert(data_path='location')
        cam.keyframe_insert(data_path='rotation_euler')

def removehandle():
    for i in handle:
        if i.__name__ == 'captureVR':
            handle.remove(i)
            break

class captureVRgroup(bpy.types.PropertyGroup):
    keybind: StringProperty(name='', default='')
    followVR: BoolProperty(name='Follow VR', default=False)
    #space3d: PointerProperty(type=bpy.types.PropertyGroup)

class CAPT_OT_setspace(bpy.types.Operator):
    bl_idname = 'capturevr.setspace'
    bl_label = 'Set Active Space'
    bl_description = 'Click to set the current viewport as the source for camera data'

    def execute(self, context):
        bpy.types.Scene.capturespace = bpy.context.space_data
        return {'FINISHED'}

class CAPT_OT_stop(bpy.types.Operator):
    bl_idname = 'capturevr.stop'
    bl_label = 'Stop Capture'
    bl_description = 'Stop capture'

    def execute(self, context):
        props = bpy.context.scene.captureVRprops
        props.followVR = False
        bpy.ops.screen.animation_play()
        return {'FINISHED'}
        pass

class CAPT_PT_panel(bpy.types.Panel):
    bl_label = 'Capture VR'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Capture VR'
    
    def draw(self, context):
        layout = self.layout
        props = bpy.context.scene.captureVRprops
        layout.row().prop(props, 'keybind')
        row = layout.row()
        row.prop(props, 'followVR')
        enabled = True
        try:
            #bpy.types.SpaceView
            bpy.context.scene.capturespace
            if bpy.context.scene.capturespace.type == 'EMPTY':
                raise
        except:
            enabled = False
        row.enabled = enabled
        layout.row().operator('capturevr.setspace')
        pass

classes = [
    captureVRgroup,
    CAPT_PT_panel,
    CAPT_OT_setspace
]

addon_keymaps = []

def register():
    removehandle()
    for i in classes:
        bpy.utils.register_class(i)
    handle.append(captureVR)
    bpy.types.Scene.captureVRprops = bpy.props.PointerProperty(type=captureVRgroup)

    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='CaptureVR', space_type='VIEW_3D')
    kmi = km.keymap_items.new('capturevr.stop', '', '', shift=False)
    addon_keymaps.append((km, kmi))


def unregister():
    for i in reversed(classes):
        bpy.utils.unregister_class(i)
    removehandle()
    del bpy.types.Scene.captureVRprops