import bpy

from . import renderer
from . import properties

from .ui import renderSettings
from .ui import nodeSettings

# RenderEngines also need to tell UI Panels that they are compatible with.
# We recommend to enable all panels marked as BLENDER_RENDER, and then
# exclude any panels that are replaced by custom panels registered by the
# render engine, or that are not supported.
def get_panels():
    exclude_panels = {
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
    }
    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)
    return panels
	
def registerPbrt():
    #print (tempfile.gettempdir()+'/')
    #register render class
    #bpy.types.RenderEngine.pbrtv4_isPostProcess = bpy.props.BoolProperty(name="pbrtv4_isPostProcess", default=True)
    bpy.utils.register_class(renderer.PBRTRenderEngine)
    properties.register()
    renderSettings.register()
    nodeSettings.register()
    for panel in get_panels():
        panel.COMPAT_ENGINES.add('PBRTV4')
    print("bpbrtV4 addon registered")
    
def unregisterPbrt():
    bpy.utils.unregister_class(renderer.PBRTRenderEngine)
    #del bpy.types.RenderEngine.pbrtv4_isPostProcess
    properties.unregister()
    renderSettings.unregister()
    nodeSettings.unregister()
    for panel in get_panels():
        if 'PBRTV4' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('PBRTV4')
    print("bpbrtV4 addon unregistered")
