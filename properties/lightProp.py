import bpy
from ..utils import util

class PBRTV4LightSettings(bpy.types.PropertyGroup):
    bpy.types.Light.pbrtv4_light_power = bpy.props.FloatProperty(name="pbrtv4_light_power",
                                               description="Power",
                                               min=0.0,
                                               default=1.0)
    bpy.types.Light.pbrtv4_light_temperature = bpy.props.FloatProperty(name="pbrtv4_light_temperature",
                                               description="Blackbody temperature",
                                               min=0.0,
                                               default=6500.0)
    bpy.types.Light.pbrtv4_light_color = bpy.props.FloatVectorProperty(name="pbrtv4_light_color", 
                                                description="Light color",
                                                default=(0.8, 0.8, 0.8, 1.0), 
                                                min=0, 
                                                max=1, 
                                                subtype='COLOR', 
                                                size=4)
    bpy.types.Light.pbrtv4_light_preset = bpy.props.EnumProperty(name="pbrtv4_light_preset",
                                          description="Light spectrum",
                                          items=[("color", "color", "Color"),
                                                 ("temperature", "temperature", "Temperature"),
                                                 ("stdillum-A", "stdillum-A", "stdillum-A"),
                                                 ("stdillum-D50", "stdillum-D50", "stdillum-D50"),
                                                 ("stdillum-D65", "stdillum-D65", "stdillum-D65"),
                                                 ("stdillum-F1", "stdillum-F1", "stdillum-F1"),
                                                 ("stdillum-F2", "stdillum-F2", "stdillum-F2"),
                                                 ("stdillum-F3", "stdillum-F3", "stdillum-F3"),
                                                 ("stdillum-F4", "stdillum-F4", "stdillum-F4"),
                                                 ("stdillum-F5", "stdillum-F5", "stdillum-F5"),
                                                 ("stdillum-F6", "stdillum-F6", "stdillum-F6"),
                                                 ("stdillum-F7", "stdillum-F7", "stdillum-F7"),
                                                 ("stdillum-F8", "stdillum-F8", "stdillum-F8"),
                                                 ("stdillum-F9", "stdillum-F9", "stdillum-F9"),
                                                 ("stdillum-F10", "stdillum-F10", "stdillum-F10"),
                                                 ("stdillum-F11", "stdillum-F11", "stdillum-F11"),
                                                 ("stdillum-F12", "stdillum-F12", "stdillum-F12"),
                                                 ("illum-acesD60", "illum-acesD60", "illum-acesD60")],
                                          default='stdillum-D65')
    
def register():
    util.safe_register_class(PBRTV4LightSettings)
    bpy.types.Light.pbrtv4_light = bpy.props.PointerProperty(type=PBRTV4LightSettings)

def unregister():
    del bpy.types.Light.pbrtv4_light
    util.safe_unregister_class(PBRTV4LightSettings)
