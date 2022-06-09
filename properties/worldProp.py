import bpy
from ..utils import util
import os

class PBRTV4WorldSettings(bpy.types.PropertyGroup):
    # Texture conversion
    pbrtv4_world_color : bpy.props.FloatVectorProperty(name="pbrtv4_world_color", 
                                                description="color",
                                                default=(1.0, 1.0, 1.0, 1.0), 
                                                min=0, 
                                                max=1, 
                                                subtype='COLOR', 
                                                size=4)
    
    pbrtv4_world_path: bpy.props.PointerProperty(name="pbrtv4_world_path", type=bpy.types.Image,
                                             description="")

    pbrtv4_world_mode: bpy.props.EnumProperty(name="pbrtv4_world_mode",
                                              description="",
                                              items=[("CONSTANT", "Constant", "Color env"),
                                                 ("ENVIRONMENT", "Environment", "File env"),
                                                 ("NISHITA", "Nishita Sky", "Nishita Sky")],
                                              default='CONSTANT')

    pbrtv4_world_power: bpy.props.FloatProperty(name="pbrtv4_world_power",
                                               description="Power",
                                               min=0.0,
                                               default=1.0)
    pbrtv4_world_rotation : bpy.props.FloatVectorProperty(name="pbrtv4_world_rotation", 
                                                description="rotation",
                                                default=(0.0, 0.0, 0.0), 
                                                subtype='EULER', 
                                                size=3)
    pbrtv4_world_show_preview: bpy.props.BoolProperty(name="", default=False, description="Show thumbnail")
    
    #Nishita sky prop
    pbrtv4_nishita_albedo: bpy.props.FloatProperty(name="pbrtv4_nishita_albedo",
                                               description="nishita albedo",
                                               min=0.0,
                                               max=1.0,
                                               default=0.5)
    pbrtv4_nishita_elevation: bpy.props.FloatProperty(name="pbrtv4_nishita_elevation",
                                               description="nishita elevation",
                                               min=0.0,
                                               max=90.0,
                                               default=10.0)
    pbrtv4_nishita_turbidity: bpy.props.FloatProperty(name="pbrtv4_nishita_turbidity",
                                               description="nishita turbidity",
                                               min=1.7,
                                               max=10.0,
                                               default=3.0)
    pbrtv4_nishita_res: bpy.props.IntProperty(name="pbrtv4_nishita_res",
                                               description="nishita resolution",
                                               min=16,
                                               default=512)
class convertEnvOperator(bpy.types.Operator):
    bl_idname = 'pbrtv4.convert_envmap'
    bl_label = 'convert env map'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        envmap = bpy.context.scene.pbrtv4_world.pbrtv4_world_path
        envmap_conv = self.convert_map(envmap.filepath)
        envmap.filepath = envmap_conv
        envmap.reload()
        envmap.update()
        return {"FINISHED"}
    def convert_map(self, envmap):
        baseTexture = util.switchpath(util.realpath(envmap))
        baseName = util.getFileName(baseTexture)
        print(baseName)
        ext = util.getExtension(baseTexture)
        if not ext=="exr":
            util.ShowMessageBox("File format: *."+ext+" doesn't supported! *.exr only")
            print("File format: *."+ext+" doesn't supported! *.exr only")
            return baseTexture
        else:
            if baseName.split("_")[-1]=="converted":
                print("File already converted. Path: "+baseTexture)
                util.ShowMessageBox("File already converted. Path: "+baseTexture)
                return baseTexture
            else:
                baseName = util.replaceExtension(baseName+"_converted", "exr")
                print(baseName)
                textureFolder = util.createFolder(os.path.join(bpy.context.scene.pbrtv4.pbrt_project_dir, "textures"))
                converted_file = os.path.join(textureFolder, baseName)
                converted_file = util.switchpath(converted_file)
                itoolExecPath = os.path.join(bpy.context.scene.pbrtv4.pbrt_bin_dir, "imgtool.exe")
                cmd = [ itoolExecPath, "makeequiarea", baseTexture, "--outfile", converted_file]
                #print(cmd)
                util.runCmd(cmd)
                print("Complete! Converted file: "+converted_file)
                util.ShowMessageBox("Complete! Converted file: "+converted_file)
                return converted_file
def register():
    bpy.utils.register_class(convertEnvOperator)
    util.safe_register_class(PBRTV4WorldSettings)
    bpy.types.Scene.pbrtv4_world = bpy.props.PointerProperty(type=PBRTV4WorldSettings)

def unregister():
    bpy.utils.unregister_class(convertEnvOperator)
    del bpy.types.Scene.pbrtv4_world
    util.safe_unregister_class(PBRTV4WorldSettings)
