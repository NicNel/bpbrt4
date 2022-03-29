import bpy
from ..utils import util

class PBRTV4CameraSettings(bpy.types.PropertyGroup):
    # Texture conversion
    pbrtv4_camera_use_dof: bpy.props.BoolProperty(name="pbrtv4_camera_use_dof", default=False, description="Use DOF")
    
    pbrtv4_camera_lensradius: bpy.props.FloatProperty(name="pbrtv4_camera_lensradius",
                                               description="camera lens radius",
                                               min=0.0,
                                               default=5.6)
    pbrtv4_camera_focaldistance: bpy.props.FloatProperty(name="pbrtv4_camera_focaldistance",
                                               description="camera focal distance",
                                               min=0.0,
                                               default=1)
    pbrtv4_camera_focus_obj: bpy.props.PointerProperty(name="pbrtv4_camera_focus_obj", type=bpy.types.Object)
    
    pbrtv4_camera_type: bpy.props.EnumProperty(
        name="pbrtv4_camera_type",
        description="camera type",
        items=[
            ("perspective", "perspective", "perspective camera"),
            ("orthographic", "orthographic", "orthographic camera"),
            ("realistic", "realistic", "realistic camera"),
            ("spherical", "spherical", "spherical camera"),
            ],
            default="perspective"
    )
    
    pbrtv4_realistic_camera_apperture: bpy.props.EnumProperty(
        name="pbrtv4_realistic_camera_apperture",
        description="realistic camera apperture type",
        items=[
            ("gaussian", "gaussian", "gaussian apperture"),
            ("square", "square", "square apperture"),
            ("pentagon", "pentagon", "pentagon apperture"),
            ("star", "star", "star apperture"),
            ("none", "none", "none apperture")
            ],
            default="none"
    )
    
    pbrtv4_realistic_camera_file: bpy.props.EnumProperty(
        name="pbrtv4_realistic_camera_file",
        description="realistic camera file",
        items=[
            ("dgauss.50mm.dat", "dgauss.50mm.dat", "dgauss.50mm camera"),
            ("dgauss.dat", "dgauss.dat", "dgauss camera"),
            ("fisheye.10mm.dat", "fisheye.10mm.dat", "fisheye.10mm camera"),
            ("fisheye.dat", "fisheye.dat", "fisheye camera"),
            ("telephoto.250mm.dat", "telephoto.250mm.dat", "telephoto.250mm camera"),
            ("telephoto.dat", "telephoto.dat", "telephoto camera"),
            ("wide.22mm.dat", "wide.22mm.dat", "wide.22mm camera"),
            ("wide.dat", "wide.dat", "wide camera")
            ]
    )
    
def register():
    util.safe_register_class(PBRTV4CameraSettings)
    bpy.types.Camera.pbrtv4_camera = bpy.props.PointerProperty(type=PBRTV4CameraSettings)

def unregister():
    del bpy.types.Camera.pbrtv4_camera
    util.safe_unregister_class(PBRTV4CameraSettings)
