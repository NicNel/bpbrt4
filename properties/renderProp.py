import bpy
import os
import tempfile
from ..utils import util

def UpdatedFunction(self, context):
    if bpy.context.scene.pbrtv4.pbrt_pfilter_type == 'box':
        bpy.context.scene.pbrtv4.pbrt_pfilter_xradius = 0.5;
        bpy.context.scene.pbrtv4.pbrt_pfilter_yradius = 0.5;
    elif bpy.context.scene.pbrtv4.pbrt_pfilter_type == 'gaussian':
        bpy.context.scene.pbrtv4.pbrt_pfilter_xradius = 1.5;
        bpy.context.scene.pbrtv4.pbrt_pfilter_yradius = 1.5;
    elif bpy.context.scene.pbrtv4.pbrt_pfilter_type == 'mitchell':
        bpy.context.scene.pbrtv4.pbrt_pfilter_xradius = 2.0;
        bpy.context.scene.pbrtv4.pbrt_pfilter_yradius = 2.0;
    elif bpy.context.scene.pbrtv4.pbrt_pfilter_type == 'sinc':
        bpy.context.scene.pbrtv4.pbrt_pfilter_xradius = 4.0;
        bpy.context.scene.pbrtv4.pbrt_pfilter_yradius = 4.0;
    elif bpy.context.scene.pbrtv4.pbrt_pfilter_type == 'triangle':
        bpy.context.scene.pbrtv4.pbrt_pfilter_xradius = 2.0;
        bpy.context.scene.pbrtv4.pbrt_pfilter_yradius = 2.0;
    print("In update func...")
    return
    
class PBRTV4RenderSettings(bpy.types.PropertyGroup):
    # Texture conversion
    tex_output_dir: bpy.props.StringProperty(name="tex_output_dir",
                                             description="",
                                             default="",
                                             subtype='DIR_PATH')

    tex_output_use_cust_dir: bpy.props.BoolProperty(name="tex_output_use_cust_dir",
                                                    description="",
                                                    default=False)

    textures_index: bpy.props.IntProperty(name="textures_index",
                                          description="",
                                          default=0)

    # Scene render settings.
    pixel_sampler: bpy.props.EnumProperty(name="Pixel Sampler",
                                          description="Sampler",
                                          items=[('uniform', "Uniform", "Uniform"),
                                                 ('adaptive', "Adaptive", "Adaptive")],
                                          default='uniform')

    scene_export_mode: bpy.props.EnumProperty(name="scene_export_mode",
                                              description="",
                                              items=[
                                                  ('render', "Render", ""),
                                                  ('export_only', "Export Scene Files", "")],
                                              default='render')

    pixel_filter_size: bpy.props.FloatProperty(name="pixel_filter_size",
                                               description="Pixel filter size",
                                               min=0.5,
                                               max=16.0,
                                               default=1.5)
    
    #custom
    pbrt_image_server: bpy.props.EnumProperty(name="pbrt_image_server",
                                          description="Display image in",
                                          items=[('EDITOR', "Image Editor", "Image Editor"),
                                                 ('GLFW', "Interactive", "Interactive (GLFW)"),
                                                 ('TEV', "Tev", "Tev")],
                                          default='EDITOR')
    pbrt_compute_mode: bpy.props.EnumProperty(name="pbrt_compute_mode",
                                          description="compute mode",
                                          items=[('CPU', "CPU", "CPU"),
                                                 ('GPU', "GPU", "GPU")],
                                          default='CPU')
    pbrt_film_type: bpy.props.EnumProperty(name="pbrt_film_type",
                                          description="film type",
                                          items=[('rgb', "rgb", "rgb output"),
                                                 ('gbuffer', "gbuffer", "gbuffer output"),
                                                 ('spectral', "spectral", "spectral output")],
                                          default='rgb')
    pbrt_integrator: bpy.props.EnumProperty(name="pbrt_integrator",
                                          description="integrator",
                                          items=[("PATH", "path", "Path Integrator"),
                                                 ("SIMPLEVOLPATH", "simplevolpath", "Simple Volumetric Path Integrator"),
                                                 ("VOLPATH", "volpath", "Volumetric Path Integrator"),
                                                 ("LIGHTPATH", "lightpath", "Light Path Integrator"),
                                                 ("AO", "AmbientOcclusion", "Ao Integrator"),
                                                 ("RAY", "ray", "Ray Integrator"),
                                                 ("MLT", "mlt", "Mlt Integrator"),
                                                 ("BDPT", "bdpt", "BDPT Integrator")],
                                          default='PATH')
    
    #pixel filter 
    pbrt_pfilter_type: bpy.props.EnumProperty(name="pbrt_pfilter_type",
                                          description="pfilter type",
                                          items=[('box', "box", "box filter"),
                                                 ('gaussian', "gaussian", "gaussian filter"),
                                                 ('mitchell', "mitchell", "mitchell filter"),
                                                 ('sinc', "sinc", "sinc filter"),
                                                 ('triangle', "triangle", "triangle filter"),
                                                 ('none', "none", "no filter")
                                                 ],
                                          default='box', update = UpdatedFunction)
    pbrt_accelerator: bpy.props.EnumProperty(name="pbrt_accelerator",
                                          description="pbrt Accelerator",
                                          items=[('bvh', "bvh", "bvh accelerator"),
                                                 ('kdtree', "kdtree", "kdtree accelerator"),
                                                 #('uniform', "uniform", "uniform accelerator"),
                                                 #('power', "power", "power accelerator"),
                                                 #('exhaustive', "exhaustive", "exhaustive accelerator"),
                                                 ('none', "none", "no accelerator")#actually bvh by default
                                                 ],
                                          default='none')
    pbrt_bvh_maxnodeprims: bpy.props.IntProperty(name="pbrt_bvh_maxnodeprims",
                                          description="maxnodeprims",
                                          default=4)
    pbrt_bvh_splitmethod: bpy.props.EnumProperty(
        name="pbrt_bvh_splitmethod",
        description="splitmethod",
        items=[
            ("sah", "sah", "sah"),
            ("equal", "equal", "equal"),
            ("hlbvh", "hlbvh", "hlbvh"),
            ("middle", "middle", "middle")],
            default = "sah"
    )
    
    pbrt_pfilter_xradius: bpy.props.FloatProperty(name="pbrt_pfilter_xradius",
                                               description="pbrt pixel filter xradius",
                                               min=0,
                                               default=0.5)
    pbrt_pfilter_yradius: bpy.props.FloatProperty(name="pbrt_pfilter_yradius",
                                               description="pbrt pixel filter yradius",
                                               min=0,
                                               default=0.5)
    pbrt_export_scene_only: bpy.props.BoolProperty(name="pbrt_export_scene_only",
                                                    description="",
                                                    default=False)
    #-----------------
    pbrt_samples: bpy.props.IntProperty(
        name="pbrtIntegratorPathSamples",
        description="Number of samples spp",
        default=24,
        min=1
    )
    pbrt_max_depth: bpy.props.IntProperty(
        name="pbrtIntegratorMaxdepth",
        default=16,
        min=1,
        max=1024
    )
    pbrtIntegratorBdptLSS: bpy.props.EnumProperty(
        name="pbrtIntegratorBdptLSS",
        items=[
            ("POWER", "Power", "samples light sources according to their emitted power"),
            ("UNIFORM", "Uniform", "samples all light sources uniformly"),
            ("SPATIAL", "Spatial", "computes light contributions in regions of the scene and samples from a related distribution")
        ]
    )
    pbrtIntegratorBdptVS: bpy.props.BoolProperty(
        name="pbrtIntegratorBdptVS",
        default=False
    )
    pbrtIntegratorBdptVW: bpy.props.BoolProperty(
        name="pbrtIntegratorBdptVW",
        default=False
    )
    pbrt_sampler: bpy.props.EnumProperty(
        name="pbrtIntegratorPathSampler",
        description="Sampler",
        items=[
            ("pmj02bn", "Pmj02bn", "Pmj02bn Sampler"),
            ("paddedsobol", "Paddedsobol", "Padded sobol Sampler"),
            ("halton", "Halton", "Halton Sampler"),
            ("sobol", "Sobol", "Sobol Sampler"),
            ("zsobol", "Zsobol", "Zsobol Sampler"),
            ("random", "Random", "Random Sampler"),
            ("stratified", "Stratified", "Stratified Sampler")],
            default = "halton"
    )
    pbrt_denoiser_type: bpy.props.EnumProperty(
        name="pbrt_denoiser_type",
        description="type",
        items=[
            ("optix", "Optix", "Optix denoiser"),
            ("oidn", "Oidn External", "Oidn External denoiser")],
            default = "optix"
    )
    pbrt_denoiser_dir: bpy.props.StringProperty(name="pbrt_denoiser_dir",
                                             description="External denoiser",
                                             default=util.switchpath(tempfile.gettempdir())+'/',
                                             subtype='DIR_PATH')
    pbrt_project_dir: bpy.props.StringProperty(name="pbrt_project_dir",
                                             description="",
                                             default=util.switchpath(tempfile.gettempdir())+'/',
                                             subtype='DIR_PATH')
    pbrt_bin_dir: bpy.props.StringProperty(name="pbrt_bin_dir",
                                             description="",
                                             default=util.switchpath(tempfile.gettempdir())+'/',
                                             subtype='DIR_PATH')
    pbrt_run_denoiser: bpy.props.BoolProperty(
        name="pbrt_run_denoiser",
        default=False
    )
    pbrt_prev_fov: bpy.props.FloatProperty(name="pbrt_prev_fov",
                                               description="Preview camera fov",
                                               min=1,
                                               default=18)
    pbrt_prev_samples: bpy.props.IntProperty(
        name="pbrt_prev_samples",
        default=32,
        min=0
    )
    pbrt_prev_obj: bpy.props.EnumProperty(
        name="pbrt_prev_obj",
        description="pbrt prev obj type",
        items=[
            ("sphere", "sphere", "sphere"),
            ("cube", "cube", "cube"),
            ("column", "column", "column")
            ],
            default = "sphere"
    )
    
    #film properties
    pbrt_film_sensor: bpy.props.EnumProperty(name="pbrt_film_sensor",
                                          description="Camera sensor",
                                          items=[("None", "None", "None"),
                                                 ("canon_eos_100d", "canon_eos_100d", "canon_eos_100d"),
                                                 ("canon_eos_1dx_mkii", "canon_eos_1dx_mkii", "canon_eos_1dx_mkii"),
                                                 ("canon_eos_200d_mkii", "canon_eos_200d_mkii", "canon_eos_200d_mkii"),
                                                 ("canon_eos_200d", "canon_eos_200d", "canon_eos_200d"),
                                                 ("canon_eos_5d_mkii", "canon_eos_5d_mkii", "canon_eos_5d_mkii"),
                                                 ("canon_eos_5d_mkiii", "canon_eos_5d_mkiii", "canon_eos_5d_mkiii"),
                                                 ("canon_eos_5d_mkiv", "canon_eos_5d_mkiv", "canon_eos_5d_mkiv"),
                                                 ("canon_eos_5d", "canon_eos_5d", "canon_eos_5d"),
                                                 ("canon_eos_5ds", "canon_eos_5ds", "canon_eos_5ds"),
                                                 ("canon_eos_m", "canon_eos_m", "canon_eos_m"),
                                                 ("hasselblad_l1d_20c", "hasselblad_l1d_20c", "hasselblad_l1d_20c"),
                                                 ("nikon_d810", "nikon_d810", "nikon_d810"),
                                                 ("nikon_d850", "nikon_d850", "nikon_d850"),
                                                 ("sony_ilce_6400", "sony_ilce_6400", "sony_ilce_6400"),
                                                 ("sony_ilce_7m3", "sony_ilce_7m3", "sony_ilce_7m3"),
                                                 ("sony_ilce_7rm3", "sony_ilce_7rm3", "sony_ilce_7rm3"),
                                                 
                                                 ("sony_ilce_9", "sony_ilce_9", "sony_ilce_9")],
                                          default='canon_eos_100d')
    pbrt_ColorSpace: bpy.props.EnumProperty(
        name="pbrt_ColorSpace",
        description="Color Space",
        items=[
            ("srgb", "sRGB", "sRGB Color Space"),
            ("dci-p3", "DCI_P3", "DCI_P3 Color Space"),
            ("rec2020", "Rec2020", "Rec2020 Color Space"),
            ("aces2065-1", "ACES2065_1", "ACES2065_1 Color Space")],
            default = "srgb"
    )
    
    pbrt_film_iso: bpy.props.IntProperty(
        name="pbrt_film_iso",
        default=150,
        min=0
    )
    
    pbrt_film_whitebalance: bpy.props.IntProperty(
        name="pbrt_film_whitebalance",
        default=6500,
        min=0
    )
    
    pbrt_film_savefp16: bpy.props.EnumProperty(name="pbrt_film_savefp16",
                                          description="Exr color depth",
                                          items=[('Half', "Float Half(16bit)", "Uniform"),
                                                 ('Full', "Float Full(32bit)", "Adaptive")],
                                          default='Half')
    
    pbrt_scene_only: bpy.props.BoolProperty(
        name="pbrt_scene_only",
        default=False
    )
    pbrt_linked_as_instance: bpy.props.BoolProperty(
        name="pbrt_linked_as_instance",
        default=True
    )
    pbrt_use_realDisp: bpy.props.BoolProperty(
        name="pbrt_use_realDisp",
        default=True
    )
    
    #bloom
    pbrt_bloom_lvl: bpy.props.FloatProperty(name="pbrt_bloom_lvl",
                                               description="pbrt pixel filter xradius",
                                               min=0,
                                               default=1.0)
    pbrt_bloom_scale: bpy.props.FloatProperty(name="pbrt_bloom_scale",
                                               description="pbrt pixel filter xradius",
                                               min=0,
                                               default=0.3)
    pbrt_bloom_width: bpy.props.IntProperty(
        name="pbrt_bloom_width",
        default=15,
        min=0
    )
    pbrt_ACES_toFilm: bpy.props.BoolProperty(
        name="pbrt_ACES_toFilm",
        default=False
    )
    pbrt_apply_bloom: bpy.props.BoolProperty(
        name="pbrt_apply_bloom",
        default=True
    )
                                               
                                               
    #print ("properties REGISTEREDDDD!!!")

class runRenderOperator(bpy.types.Operator):
    bl_idname = 'pbrtv4.start_render'
    bl_label = 'start render'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True)
        #bpy.ops.mesh.primitive_cube_add()
        #bpy.context.scene.render.RunTestOperator()
        return {"FINISHED"}
class runPreviewOperator(bpy.types.Operator):
    bl_idname = 'pbrtv4.start_preview_render'
    bl_label = 'start preview render'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        #not the best solution, but it raises material to update preview...
        context.material.preview_render_type = context.material.preview_render_type
        #bpy.ops.render.render({'is_preview': "True"}, 'EXEC_DEFAULT', animation=False)
        return {"FINISHED"}
class runRenderAnimOperator(bpy.types.Operator):
    bl_idname = 'pbrtv4.start_render_anim'
    bl_label = 'start render animation'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True)
        return {"FINISHED"}

class postProcessOperator(bpy.types.Operator):
    bl_idname = 'pbrtv4.post_process'
    bl_label = 'post processing'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        #get renderer
        util.is_postProcess = True
        bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True)
        '''
        for renderer in bpy.types.RenderEngine.__subclasses__():
            if renderer.bl_idname == "PBRTV4":
                renderer.is_busy = True
                bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True)
                #renderer.is_PostProcess = False
        '''     
        '''
        for renderer in bpy.types.RenderEngine.__subclasses__():
            if renderer.bl_idname == "PBRTV4":
                #renderer.RunTestOperator(renderer)
                props = {}
                renderer.getProps(renderer,props)
                file = props['pbrt_rendered_file']
                outImg = os.path.join(props['pbrt_project_dir'], 'postProcess.exr')
                self.bloomImage(file, outImg, props)
                #self.copyData(outImg)
                '''
        return {"FINISHED"}
        
    def copyData(self, img):
        img = bpy.data.images.load(img, check_existing=False)
        #layerPass = result.layers[0].passes.find_by_name("Combined",active_view)
        #bpy.data.images["Render Result"].pixels[:]
        
        target = bpy.data.images.new('Render Result', 1024, 102) #bpy.data.images["Render Result"]
        
        print(target.size[0], target.size[1],"Size!!!!!!!!!")
        
        source_pixels = img.pixels[:]
        target_pixels = list(target.pixels)
        #bpy.data.images["Render Result"].pixels[:] = target_pixels
        
        for i in range(0, len(source_pixels), 4):
            target_pixels[i+3] = source_pixels[i]
        
        #bpy.data.images["Render Result"].update()
        target.pixels[:] = target_pixels
        target.update()
        
        bpy.data.images.remove(img)
    
    def bloomImage(self, img, outImg, props):
        pbrtImgtoolPath = os.path.join(props['pbrt_bin_dir'], 'imgtool.exe')
        
        iter = ["--iterations", str(5)]
        level = ["--level", str(1)]
        out = ["--outfile", outImg]
        scale = ["--scale", str(0.3)]
        width = ["--width", str(15)]
        file = [img]
        
        cmd = [ pbrtImgtoolPath, "bloom"]+iter+level+out+scale+width+file
        util.runCmd(cmd)
        #outImagePath = util.switchpath(props['pbrt_project_dir'])+'/'+'Denoised.exr'
        bpy.ops.image.open(filepath=outImg)
        
def register():
    bpy.utils.register_class(runRenderOperator)
    bpy.utils.register_class(runRenderAnimOperator)
    bpy.utils.register_class(runPreviewOperator)
    bpy.utils.register_class(postProcessOperator)
    
    bpy.types.Object.pbrtv4_isPortal = bpy.props.BoolProperty(
        name="pbrtv4_isPortal",
        default=False
    )
    '''
    bpy.types.Material.pbrtv4_isEmissive = bpy.props.BoolProperty(
        name="pbrtv4_isEmissive",
        default=False
    )
    bpy.types.Material.pbrtv4_emission_power = bpy.props.FloatProperty(name="pbrtv4_emission_power",
                                               description="POwer",
                                               min=0.0,
                                               default=1.0)
    bpy.types.Material.pbrtv4_emission_color = bpy.props.FloatVectorProperty(name="pbrtv4_emission_color", 
                                                description="color",
                                                default=(0.8, 0.8, 0.8, 1.0), 
                                                min=0, 
                                                max=1, 
                                                subtype='COLOR', 
                                                size=4)
    bpy.types.Material.pbrtv4_emission_temp = bpy.props.FloatProperty(name="pbrtv4_emission_temp",
                                               description="blackbody temperature",
                                               default=6500.0)
    bpy.types.Material.pbrtv4_emission_preset = bpy.props.EnumProperty(name="pbrtv4_emission_preset",
                                          description="Emission spectrum",
                                          items=[("blackbody", "blackbody", "Blackbody"),
                                                 ("color", "color", "Color"),
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
    '''                                      
    util.safe_register_class(PBRTV4RenderSettings)
    bpy.types.Scene.pbrtv4 = bpy.props.PointerProperty(type=PBRTV4RenderSettings)

def unregister():
    bpy.utils.unregister_class(runRenderOperator)
    bpy.utils.unregister_class(runRenderAnimOperator)
    bpy.utils.unregister_class(runPreviewOperator)
    bpy.utils.unregister_class(postProcessOperator)
    
    del bpy.types.Object.pbrtv4_isPortal
    
    #del bpy.types.Material.pbrtv4_isEmissive
    #del bpy.types.Material.pbrtv4_emission_power
    #del bpy.types.Material.pbrtv4_emission_color
    
    del bpy.types.Scene.pbrtv4
    util.safe_unregister_class(PBRTV4RenderSettings)
