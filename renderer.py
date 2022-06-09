import bpy
#import pbrt
import os
import math

from .export.geometry import GeometryExporter
from .utils import util
from .preview.prepare import preparePreview

import threading
import time
import numpy as np

# Render engine ================================================================================
class PBRTRenderEngine(bpy.types.RenderEngine):
    bl_idname = "PBRTV4" # internal name
    bl_label = "PBRTV4 Renderer" # Visible name
    bl_use_preview = True
    bl_use_material = True
    bl_use_shading_nodes = False
    bl_use_shading_nodes_custom = False
    bl_use_texture_preview = True
    bl_use_texture = True
    is_busy = False
    bl_use_eevee_viewport = True
    #bl_use_shading_nodes_custom = True
    
    def __init__(self):
        pass
    
    def __del__(self):
        pass
    
    def view_draw(self, context, depsgraph):
        region = context.region
        scene = depsgraph.scene

        # Get viewport dimensions
        dimensions = region.width, region.height

        # Bind shader that converts from scene linear to display space,
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_ONE, bgl.GL_ONE_MINUS_SRC_ALPHA)
        self.bind_display_space_shader(scene)

        if not self.draw_data or self.draw_data.dimensions != dimensions:
            self.draw_data = CustomDrawData(dimensions)

        self.draw_data.draw()

        self.unbind_display_space_shader()
        bgl.glDisable(bgl.GL_BLEND)
    
    def render(self, depsgraph):
        #self.report(type, message)
        #self.error_set("Start Render Export")
        #self.th = threading.Thread(target=self.update_frame_th)
        #self.th.start()
        if self.is_preview:
            if not self.is_busy:
                self.PreviewRender(depsgraph)
        else:
            self.FinalRender(depsgraph)
        #free
        #self.free_blender_memory()
    
    def update_frame_th(self):
        while True:
            print("\nUpdate frame...\n")
            #result = self.get_result()
            iname = 'render_{}'.format(bpy.context.scene.pbrtv4.pbrt_integrator)
            filename = util.switchpath(bpy.context.scene.pbrtv4.pbrt_project_dir)+'/'+'{}.exr'.format(iname)
            #result.layers[0].load_from_file(filename)
            self.LoadResult(filename, props["scale_x"], props["scale_y"])
            time.sleep(5)
    
    def FinalRender(self, depsgraph):
        props = {}
        self.getProps(props)
        if not props['pbrt_scene_only']:
            print("--- Export objects ---")
            start_time = time.time()
            self.exportObjects(depsgraph,props)
            t = time.time() - start_time
            m = t/60.0
            mr = round(m, 5)
            print("--- Export takes %s min ---" % mr)
        self.exportSettings(depsgraph,props)
        print("RENDER STARTTTTTTT")
        filename = util.switchpath(props['pbrt_project_dir'])+'/'+'scene.pbrt'
        
        if not props['pbrt_export_scene_only']:
            if props['pbrt_image_server'] == "TEV":
                self.RunTevRender(props, filename)
            else:
                self.RunRender(props, depsgraph, filename)
        else:
            print("Export scene file only selected", )
            print("PBRT Scene exported as: ", filename)
        #if props['pbrt_film_type'] == 'gbuffer' and props['pbrt_run_denoiser'] == True:
            #self.RunDenoiser(props)
        
        #clear exporter data
        if hasattr(self, 'geometry_exporter'):
            self.geometry_exporter.ClearExportData()
        
    # Check first-run installation
    #install.install()
    # Compute film dimensions
    #scale = scene.render.resolution_percentage / 100.0
    #sx = int(scene.render.resolution_x * scale)
    #sy = int(scene.render.resolution_y * scale)
    #result = self.begin_result(0, 0, sx, sy)
    #self.end_result(result)
        
    def PreviewRender(self, depsgraph):
        #print (bpy.context.view_layer.objects.active.active_material)
        scene = depsgraph.scene
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)
        
        if max(self.size_x,  self.size_y) >= 96:
            print("Start preview render")
            props = {}
            self.getProps(props)
            preparePreview(props["previewFolder"])
            
            bsdfs = 'bsdfs.xml'
            geometry = "geometry.xml"
            bsdfs_base = 'bsdfs_base.pbrt'
            geometry_base = 'geometry_base.pbrt'
            #settings_base = 'settings_base.xml'
            
            #-----------------------------------
            # Compute film dimensions
            filename = os.path.join(props["previewFolder"], 'preview.exr')
            filmtype = "rgb"
            #export_result ='Film "gbuffer"\n'
            #export_result ='Film "rgb"\n'
            export_result ='Film "{}"\n'.format(filmtype)
            export_result +='    "string filename" [ "{}" ]\n'.format(util.switchpath(filename))
            export_result +='    "integer yresolution" [ {} ]\n'.format(self.size_y)
            export_result +='    "integer xresolution" [ {} ]\n'.format(self.size_x)  
            
            pbrt_film_sensor = bpy.context.scene.pbrtv4.pbrt_film_sensor
            if not pbrt_film_sensor == 'None':
                export_result +='    "string sensor" "{}"\n'.format(pbrt_film_sensor)
            pbrt_film_iso = bpy.context.scene.pbrtv4.pbrt_film_iso
            export_result +='    "float iso" {}\n'.format(pbrt_film_iso)
            
            pbrt_film_whitebalance = bpy.context.scene.pbrtv4.pbrt_film_whitebalance
            export_result +='    '+'"float whitebalance" {}\n'.format(pbrt_film_whitebalance)
            
            #export camera fov
            fov = bpy.context.scene.pbrtv4.pbrt_prev_fov
            #fov = self.calcFovDEG(self.size_x, self.size_y, angle)
            export_result+='Camera "perspective"\n'
            export_result+='    "float fov" [%s]\n' % (fov)
            
            #export sampler
            samplesCount = bpy.context.scene.pbrtv4.pbrt_prev_samples
            sampler =  bpy.context.scene.pbrtv4.pbrt_sampler
            export_result +='Sampler "{}"\n'.format(sampler)
            export_result +='    "integer pixelsamples" [ {} ]\n'.format(samplesCount)
            
            #colorspace
            colorSpace = bpy.context.scene.pbrtv4.pbrt_ColorSpace
            export_result +='ColorSpace "{}"\n'.format(colorSpace)
            #-----------------------------------
            
            #test write file
            settingsFile = os.path.join(props["previewFolder"], 'settings.pbrt')
            with open(settingsFile, 'w') as f:
                f.write(export_result)
                f.close()
            
            #export bsdf
            mat_name = "preview_mat"
            mat = bpy.context.view_layer.objects.active.active_material
            materialData = ''.join(GeometryExporter.export_mat_get(mat, mat_name))
            bsdfFile = os.path.join(props["previewFolder"], "preview_bsdf.pbrt")
            
            with open(bsdfFile, 'w') as f:
                f.write(materialData)
                f.close()
            props["scale_x"] = self.size_x
            props["scale_y"] = self.size_y
            self.RunPreviewRender(props, filename)
        return None
            
    def RunPreviewRender(self, props, filename):
        #run render
        sceneFile = os.path.join(props["previewFolder"], "scene.pbrt")
        pbrtExecPath = util.switchpath(bpy.context.scene.pbrtv4.pbrt_bin_dir)+'/'+'pbrt.exe'
        #start render
        if bpy.context.scene.pbrtv4.pbrt_compute_mode == 'CPU':
            cmd = [ pbrtExecPath, sceneFile ]
        else:
            cmd = [ pbrtExecPath, "--gpu", sceneFile ]
        util.runCmd(cmd)
        #---------------
        #result = self.get_result()
        #<3.0
        #result.layers[0].load_from_file(filename)
        #result.load_from_file(filename)
        self.LoadResult(filename, props["scale_x"], props["scale_y"])
        
    def getProps(self, props):
        props['pbrt_scene_only'] = bpy.context.scene.pbrtv4.pbrt_scene_only
        props['pbrt_samples'] = bpy.context.scene.pbrtv4.pbrt_samples
        props['pbrt_max_depth'] = bpy.context.scene.pbrtv4.pbrt_max_depth
        props['pbrt_sampler'] = bpy.context.scene.pbrtv4.pbrt_sampler
        props['pbrt_integrator'] = bpy.context.scene.pbrtv4.pbrt_integrator
        props['pbrt_accelerator'] = bpy.context.scene.pbrtv4.pbrt_accelerator
        props['pbrt_bvh_maxnodeprims'] = bpy.context.scene.pbrtv4.pbrt_bvh_maxnodeprims
        props['pbrt_bvh_splitmethod'] = bpy.context.scene.pbrtv4.pbrt_bvh_splitmethod
        
        #pixel filter
        props['pbrt_pfilter_type'] = bpy.context.scene.pbrtv4.pbrt_pfilter_type
        props['pbrt_pfilter_xradius'] = bpy.context.scene.pbrtv4.pbrt_pfilter_xradius
        props['pbrt_pfilter_yradius'] = bpy.context.scene.pbrtv4.pbrt_pfilter_yradius
        #------------------
        
        props['pbrt_compute_mode'] = bpy.context.scene.pbrtv4.pbrt_compute_mode
        props['pbrt_project_dir'] = bpy.context.scene.pbrtv4.pbrt_project_dir
        props["previewFolder"] = os.path.join(props['pbrt_project_dir'], "preview")
        
        props['pbrt_compute_mode'] = bpy.context.scene.pbrtv4.pbrt_compute_mode
        props['pbrt_film_type'] = bpy.context.scene.pbrtv4.pbrt_film_type
        props['pbrt_ColorSpace'] = bpy.context.scene.pbrtv4.pbrt_ColorSpace
        props['pbrt_run_denoiser'] = bpy.context.scene.pbrtv4.pbrt_run_denoiser
        props['pbrtv4_world_rotation'] = bpy.context.scene.pbrtv4_world.pbrtv4_world_rotation
        props['pbrtv4_world_color'] = bpy.context.scene.pbrtv4_world.pbrtv4_world_color
        props['pbrt_film_sensor'] = bpy.context.scene.pbrtv4.pbrt_film_sensor
        props['pbrt_bin_dir'] = bpy.context.scene.pbrtv4.pbrt_bin_dir
        
        props['pbrt_linked_as_instance'] = bpy.context.scene.pbrtv4.pbrt_linked_as_instance
        props['pbrt_use_realDisp'] = bpy.context.scene.pbrtv4.pbrt_use_realDisp
        
        props['pbrt_denoiser_dir'] = bpy.context.scene.pbrtv4.pbrt_denoiser_dir
        props['pbrt_denoiser_type'] = bpy.context.scene.pbrtv4.pbrt_denoiser_type
        
        props['pbrt_image_server'] = bpy.context.scene.pbrtv4.pbrt_image_server
        props['pbrt_export_scene_only'] = bpy.context.scene.pbrtv4.pbrt_export_scene_only
        
        iname = 'render_{}'.format(props['pbrt_integrator'])
        filename = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.exr'.format(iname)
        props['pbrt_rendered_file'] = filename
    
    def exportSettings(self, depsgraph, props):
        print (props['pbrt_samples'], props['pbrt_max_depth'],props['pbrt_sampler'],props['pbrt_integrator'],props['pbrt_compute_mode'],props['pbrt_project_dir'])
        #print ("samples: {}",bpy.types.Scene.pbrtv4.pbrtIntegratorPathSamples)
        #print ("depth: {}",bpy.types.Scene.pbrtv4.pbrtIntegratorMaxdepth)
        
        sceneData = ""
        sceneData += "#pbrt v4.0 Scene File\n"
        sceneData += "#Exported by bpbrt Blender Exporter\n"
       
        sceneData += self.export_camera(depsgraph)
        
        sceneData += self.export_ColorSpace(depsgraph, props)
        sceneData += self.export_Film(depsgraph, props)
        sceneData += self.export_Integrator(props)
        #accelerator
        sceneData += self.export_Accelerator(props)
        #accelerator
        sceneData += self.export_Sampler(props)
        sceneData += self.export_PixelFilter(props)
        sceneData += "WorldBegin\n"
        sceneData += self.export_World(props)
        sceneData += self.exportLights()
        sceneData += 'Include "materials.pbrt"\n'
        sceneData += 'Include "geometry.pbrt"\n'
        
        sceneFolder = props['pbrt_project_dir']
        sceneFile = os.path.join(props['pbrt_project_dir'], "scene.pbrt")
        
        #test write file
        with open(sceneFile, 'w') as f:
            f.write(sceneData)
            f.close()
    
    def exportLights(self):
        if hasattr(self, 'geometry_exporter'):
            if len(self.geometry_exporter.lightsData)>0:
                res = ""
                for light in self.geometry_exporter.lightsData:
                    res += light
                return res
        return ""
            
    def exportObjects(self, depsgraph, props):
        self.geometry_exporter = GeometryExporter()
        
        geometryFolder =os.path.join(props['pbrt_project_dir'], "geometry")
        texturesFolder = os.path.join(props['pbrt_project_dir'], "textures")
        if not os.path.exists(texturesFolder):
            os.makedirs(texturesFolder)
        geometryFile =os.path.join(props['pbrt_project_dir'], "geometry.pbrt")
        materialFile = os.path.join(props['pbrt_project_dir'], "materials.pbrt")
        
        if os.path.isfile(geometryFile) or os.path.islink(geometryFile):
            print("delete geometry file: ", geometryFile)
            os.unlink(geometryFile)
        if os.path.isfile(materialFile) or os.path.islink(materialFile):
            print("delete materials file: ", materialFile)
            os.unlink(materialFile)
        # Switch to object mode before exporting stuff, so everything is defined properly
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        if not os.path.exists(geometryFolder):
            os.makedirs(geometryFolder)
        linked_as_instance = props['pbrt_linked_as_instance']
        GeometryLst=self.geometry_exporter.ExportSceneGeometry(depsgraph, geometryFolder, self, linked_as_instance)
        
        #export displacement
        if props['pbrt_use_realDisp']:
            print("Preparing displacement data and convert meshes\n")
            for dInfo in self.geometry_exporter.dispData:
                self.doDisplacement(props, dInfo)
        
        #test write file
        with open(geometryFile, 'w') as f:
            for ob in GeometryLst:
                data = ob
                f.write(data)
            f.close()
        
        #remove duplicated records
       
        mats = self.geometry_exporter.materialData
        with open(materialFile, 'w') as f:
            for ob in mats:
                f.write(ob)
            f.close()
            
    def doDisplacement(self, props, dInfo):
        print(dInfo.ToStr())
        print("Processing PLY file")
        plytoolExecPath = util.switchpath(props['pbrt_bin_dir'])+'/'+'plytool.exe'
        cmd = [ plytoolExecPath, "displace", dInfo.outfile, "--outfile", dInfo.outfile, "--image", dInfo.image, "--scale", str(dInfo.scale), "--edge-length", str(dInfo.edge_length), "--uvscale", str(dInfo.uvscale)]
        util.runCmd(cmd)
        print("Done")
    #self.geometry_exporter.materialData
    #print(materialFile)
    #print(geometryFile)
    #--------
    def measure(first, second):
        locx = second[0] - first[0]
        locy = second[1] - first[1]
        locz = second[2] - first[2]

        distance = sqrt((locx)**2 + (locy)**2 + (locz)**2)
        return distance
        
    def calcFovRAD(self, resx, resy, angle):
        if resx>=resy:
            ratio = resy / resx
        else:
            ratio = resx / resy
        angle_rad = angle
        fov = 2.0 * math.atan ( ratio * math.tan( angle_rad / 2.0 )) * 180.0 / math.pi 
        return fov
        
    def calcFovDEG(self, resx, resy, angle):
        if resx>=resy:
            ratio = resy / resx
        else:
            ratio = resx / resy
        angle_deg = angle * 180.0 / math.pi 
        fov = 2.0 * math.atan ( ratio * math.tan( angle_deg / 2.0 ))* 180.0 / math.pi 
        return fov
        
    def export_camera(self, depsgraph):
        export_result = ""
        scene = depsgraph.scene
        cam_ob = scene.camera
        if cam_ob is None:
            print("no scene camera,aborting")
        elif cam_ob.type == 'CAMERA':
            print("regular scene cam")
            print("render res: ", scene.render.resolution_x , " x ", scene.render.resolution_y)
            print("Exporting camera: ", cam_ob.name)

            export_result+="Scale -1 1 1 \n#avoid the 'flipped image' bug..\n"

            cameramatrix = cam_ob.matrix_world.copy()
            matrixTransposed = cameramatrix.transposed()
            up_point = matrixTransposed[1]

            from_point=cam_ob.matrix_world.col[3]
            at_point=cam_ob.matrix_world.col[2]
            at_point=at_point * -1
            at_point=at_point + from_point

            export_result+="LookAt\t%s %s %s\n\t%s %s %s\n\t%s %s %s\n" % \
                        (from_point.x, from_point.y, from_point.z, \
                         at_point.x, at_point.y, at_point.z, \
                         up_point[0],up_point[1],up_point[2])

            fov = self.calcFovRAD(scene.render.resolution_x, scene.render.resolution_y, cam_ob.data.angle)
            if cam_ob.data.pbrtv4_camera.pbrtv4_camera_type == "perspective":
                export_result+='Camera "perspective"\n'
                export_result+='    "float fov" [%s]\n' % (fov)
                #if cam_ob.data.clip_start>0.001:
                #    export_result+='    "float zNear" [%s]\n' % (cam_ob.data.clip_start)
                #shift camera lens
                
                shiftX = cam_ob.data.shift_x/100.0
                shiftY = cam_ob.data.shift_y/100.0
                if not shiftX==0 or not shiftY==0:
                    export_result+='    "float shiftX" [%s]\n' % (shiftX)
                    export_result+='    "float shiftY" [%s]\n' % (shiftY)
            elif cam_ob.data.pbrtv4_camera.pbrtv4_camera_type == "realistic":
                export_result+='Camera "realistic"\n'
                #get lens file
                currDir = os.path.abspath(os.path.dirname(__file__))
                #print (currDir)
                lensfile =os.path.join(currDir, "lenses", cam_ob.data.pbrtv4_camera.pbrtv4_realistic_camera_file)
                export_result+='    '+'"string lensfile" ["{}"]\n'.format(util.switchpath(lensfile))
                
                if cam_ob.data.pbrtv4_camera.pbrtv4_realistic_camera_apperture != 'none':
                    export_result+='    '+'"string aperture" "{}"\n'.format(cam_ob.data.pbrtv4_camera.pbrtv4_realistic_camera_apperture)
                
                target_dist = -1
                if cam_ob.data.pbrtv4_camera.pbrtv4_camera_focus_obj:
                    target_dist = (cam_ob.data.pbrtv4_camera.pbrtv4_camera_focus_obj.location - cam_ob.location).length
                    print("CAMERA DISTANCE >>>", target_dist)
                if target_dist>0:
                    cam_ob.data.pbrtv4_camera.pbrtv4_camera_focaldistance = target_dist
                dist = cam_ob.data.pbrtv4_camera.pbrtv4_camera_focaldistance
                f_value = cam_ob.data.pbrtv4_camera.pbrtv4_camera_lensradius
                export_result+='    "float aperturediameter" [%s]\n' % (f_value)
                export_result+='    "float focusdistance" [%s]\n' % (dist)
            elif cam_ob.data.pbrtv4_camera.pbrtv4_camera_type == "orthographic":
                export_result+='Camera "orthographic"\n'
            elif cam_ob.data.pbrtv4_camera.pbrtv4_camera_type == "spherical":
                export_result+='Camera "spherical"\n'
                export_result+='    "string mapping" ["equirectangular"]\n'
                
            #use dof
            if cam_ob.data.pbrtv4_camera.pbrtv4_camera_use_dof and cam_ob.data.pbrtv4_camera.pbrtv4_camera_type == "perspective":
                target_dist = -1
                if cam_ob.data.pbrtv4_camera.pbrtv4_camera_focus_obj:
                    target_dist = (cam_ob.data.pbrtv4_camera.pbrtv4_camera_focus_obj.location - cam_ob.location).length
                    print("CAMERA DISTANCE >>>", target_dist)
                f_value = cam_ob.data.pbrtv4_camera.pbrtv4_camera_lensradius
                #sensor_size = 1.0/(f_value*10.0)
                #https://photo.stackexchange.com/questions/79605/how-do-i-correctly-convert-from-aperture-diameter-into-f-stops
                sensor_size = ((cam_ob.data.lens / f_value)/1000.0)#/2.0 #diameter or radius?
                print("SENSOR RADIUS: ",sensor_size, "CAMERA FOCAL LENGTH: ", cam_ob.data.lens,"mm")
                if target_dist>0:
                    cam_ob.data.pbrtv4_camera.pbrtv4_camera_focaldistance = target_dist
                dist = cam_ob.data.pbrtv4_camera.pbrtv4_camera_focaldistance
                
                export_result+='    "float lensradius" [%s]\n' % (sensor_size)
                export_result+='    "float focaldistance" [%s]\n' % (dist)
                
        return export_result
        
    #Integrator "volpath" "integer maxdepth" 50
    def export_Integrator(self, props):
        export_result =""
        if props['pbrt_integrator'] == "PATH":
            export_result +="Integrator {}\n".format('"path"')
            export_result +='    "integer maxdepth" [ {} ]\n'.format(props['pbrt_max_depth'])
        elif props['pbrt_integrator'] == "VOLPATH":
            export_result +="Integrator {}\n".format('"volpath"')
            export_result +='    "integer maxdepth" [ {} ]\n'.format(props['pbrt_max_depth'])
        elif props['pbrt_integrator'] == "LIGHTPATH":
            export_result +="Integrator {}\n".format('"lightpath"')
        elif props['pbrt_integrator'] == "SIMPLEVOLPATH":
            export_result +="Integrator {}\n".format('"simplevolpath"')
            export_result +='    "integer maxdepth" [ {} ]\n'.format(props['pbrt_max_depth'])
        elif props['pbrt_integrator'] == "AO":
            export_result +="Integrator {}\n".format('"ambientocclusion"')
            export_result +='    "float maxdistance" [ {} ]\n'.format(10)
        elif props['pbrt_integrator'] == "RAY":
            export_result +="Integrator {}\n".format('"ray"')
        elif props['pbrt_integrator'] == "MLT":
            export_result +="Integrator {}\n".format('"mlt"')
        else :
            export_result +="Integrator {}\n".format('"bdpt"')
            export_result +='    "integer maxdepth" [ {} ]\n'.format(props['pbrt_max_depth'])
        
        return export_result
    #Sampler "sobol"
    #"integer pixelsamples" [ 1024 ]
    
    def export_Sampler(self, props):
        export_result =""
        
        export_result +='Sampler "{}"\n'.format(props['pbrt_sampler'])
        export_result +='    "integer pixelsamples" [ {} ]\n'.format(props['pbrt_samples'])
        return export_result
        
    def export_Accelerator(self, props):
        export_result =""
        if not props['pbrt_accelerator'] == "none":
            export_result +='Accelerator "{}"\n'.format(props['pbrt_accelerator'])
            if props['pbrt_accelerator'] == "bvh":
                export_result +='    "integer maxnodeprims" [ {} ]\n'.format(props['pbrt_bvh_maxnodeprims'])
                export_result +='    "string splitmethod" "{}"\n'.format(props['pbrt_bvh_splitmethod'])
                
        return export_result
        
    def export_PixelFilter(self, props):
        export_result =""
        pfilter = props['pbrt_pfilter_type']
        xr = props['pbrt_pfilter_xradius']
        yr = props['pbrt_pfilter_yradius']
        if not pfilter == 'none':
            export_result +='PixelFilter "{}"\n'.format(pfilter)
            export_result +='    "float xradius" [ {} ]\n'.format(xr)
            export_result +='    "float yradius" [ {} ]\n'.format(yr)
        return export_result
    #Film "rgb"
    #"string filename" [ "villa-lights-on.exr" ]
    #"float iso" [ 160 ]
    #"integer yresolution" [ 444 ]
    #"integer xresolution" [ 1000 ]
    
    def CropWindow(self,depsgraph, props):
        scene = depsgraph.scene
        render = scene.render
        use_border = render.use_border
        if use_border:
            min_x = render.border_min_x
            min_y = render.border_min_y
            max_x = render.border_max_x
            max_y = render.border_max_y
            #return '"float cropwindow" [{} {} {} {}]\n'.format(min_x, min_y, max_x, max_y)
            #x x y y
            return '"float cropwindow" [{} {} {} {}]\n'.format(min_x, max_x, 1-min_y, 1-max_y)
        else:
            return ''
        
    def export_ColorSpace(self, depsgraph, props):
        colorSpace = props['pbrt_ColorSpace']
        export_result ='ColorSpace "{}"\n'.format(colorSpace)
        return export_result
        
    def export_Film(self,depsgraph, props):
        # Compute film dimensions
        scene = depsgraph.scene
        scale = scene.render.resolution_percentage / 100.0
        sx = int(scene.render.resolution_x * scale)
        sy = int(scene.render.resolution_y * scale)
        
        props["scale_x"] = sx
        props["scale_y"] = sy
        
        filename = props['pbrt_rendered_file']
        filmtype = props['pbrt_film_type']
        #export_result ='Film "gbuffer"\n'
        #export_result ='Film "rgb"\n'
        export_result ='Film "{}"\n'.format(filmtype)
        export_result +='    "string filename" [ "{}" ]\n'.format(filename)
        export_result +='    "integer yresolution" [ {} ]\n'.format(sy)
        export_result +='    "integer xresolution" [ {} ]\n'.format(sx)
        export_result +='    '+self.CropWindow(depsgraph, props)
        pbrt_film_sensor = bpy.context.scene.pbrtv4.pbrt_film_sensor
        if not pbrt_film_sensor == 'None':
            export_result +='    "string sensor" "{}"\n'.format(pbrt_film_sensor)
        pbrt_film_iso = bpy.context.scene.pbrtv4.pbrt_film_iso
        export_result +='    "float iso" {}\n'.format(pbrt_film_iso)
        
        pbrt_film_whitebalance = bpy.context.scene.pbrtv4.pbrt_film_whitebalance
        export_result +='    '+'"float whitebalance" {}\n'.format(pbrt_film_whitebalance)
        
        pbrt_film_savefp16 = bpy.context.scene.pbrtv4.pbrt_film_savefp16
        if pbrt_film_savefp16 == 'Half':
            export_result +='    '+'"bool savefp16" true\n'
        else:
            export_result +='    '+'"bool savefp16" false\n'
            
        #"string sensor" "canon_eos_100d" "canon_eos_5d_mkiv"
        #"float iso" 150
        return export_result
        
    #AttributeBegin
    #Transform [ 0 0 -1 0 1 0 0 0 0 1 0 0 0 0 0 1  ]
    #LightSource "infinite"
        #"rgb L" [ 1 1 1 ]
        #"float scale" [1]
    #AttributeEnd
    
    def export_World(self, props):
        export_result ='AttributeBegin\n'
        props['pbrtv4_world_rotation']
        #Scale -1 1 1
        #Rotate 90 -1 0 0
        #Rotate 90 0 0 1
        r = props['pbrtv4_world_rotation']
        #export_result +='    '+'Scale {} {} {}\n'.format(1, 1, -1)
        
        export_result +='    '+'Rotate {} {} {} {}\n'.format(180.0 / math.pi*r[0], 1, 0, 0)
        export_result +='    '+'Rotate {} {} {} {}\n'.format(180.0 / math.pi*r[1], 0, 1, 0)
        export_result +='    '+'Rotate {} {} {} {}\n'.format(180.0 / math.pi*r[2], 0, 0, 1)
        
        export_result +='    LightSource "infinite"\n'
        
        if bpy.context.scene.pbrtv4_world.pbrtv4_world_mode == 'CONSTANT':
            export_result +='        "rgb L" [ {} {} {} ]\n'.format(props['pbrtv4_world_color'][0],props['pbrtv4_world_color'][1],props['pbrtv4_world_color'][2])
        elif bpy.context.scene.pbrtv4_world.pbrtv4_world_mode == 'ENVIRONMENT':
            filePath = bpy.context.scene.pbrtv4_world.pbrtv4_world_path.filepath
            file = util.switchpath(util.realpath(filePath))
            export_result +='        "string filename" [ "{}" ]\n'.format(file)
        else: #Nishita
            file = util.switchpath(props['pbrt_project_dir'])+'/'+"NishitaSky.exr"
            #create sky envmap
            nishita_albedo = bpy.context.scene.pbrtv4_world.pbrtv4_nishita_albedo;
            nishita_elevation=bpy.context.scene.pbrtv4_world.pbrtv4_nishita_elevation;
            nishita_turbidity=bpy.context.scene.pbrtv4_world.pbrtv4_nishita_turbidity;
            nishita_res=bpy.context.scene.pbrtv4_world.pbrtv4_nishita_res;
            self.CreateNishitaSky(props, nishita_albedo, nishita_elevation, nishita_turbidity, nishita_res, file)
            #add link to file
            export_result +='        "string filename" [ "{}" ]\n'.format(file)
        
        power = bpy.context.scene.pbrtv4_world.pbrtv4_world_power
        export_result +='        "float scale" [ {} ]\n'.format(power)
        
        if hasattr(self, 'geometry_exporter'):
            for portal in self.geometry_exporter.portalsData:
                export_result += '        '+portal
        
        export_result +='AttributeEnd\n'
        return export_result
    def CreateNishitaSky(self, props, albedo, elevation, turbidity, res, file):
        itoolExecPath = util.switchpath(props['pbrt_bin_dir'])+'/'+'imgtool.exe'
        cmd = [ itoolExecPath, "makesky", "--albedo", str(albedo), "--elevation", str(elevation), "--outfile", file, "--turbidity", str(turbidity), "--resolution", str(res)]
        util.runCmd(cmd)
        
    def SplitGbuffer(self, props, file, ext):
        itoolExecPath = util.switchpath(props['pbrt_bin_dir'])+'/'+'imgtool.exe'
        cmd = [ itoolExecPath, "split-gbuffer", file, "--ext", ext]
        #cmd = [ itoolExecPath, "split-gbuffer", file, "--outpath", folder]
        util.runCmd(cmd)
        
    def LoadResult(self, file, sx, sy):
        result = self.begin_result(0, 0, sx, sy)
        layer = result.layers[0]
        layer.load_from_file(file)
        self.end_result(result)
    
    def RunRender(self, props, depsgraph, sceneFile):
        #self.test_break()
        # Compute pbrt executable path
        pbrtExecPath = util.switchpath(props['pbrt_bin_dir'])+'/'+'pbrt.exe'
        file = sceneFile    
        #start render
        if props['pbrt_compute_mode'] == 'CPU':
            cmd = [ pbrtExecPath, '--write-partial-images', file ]
        else:
            cmd = [ pbrtExecPath, "--gpu", '--write-partial-images', file ]
            if props['pbrt_image_server'] == "GLFW":
                cmd = [ pbrtExecPath, "--gpu", '--interactive', file ]
        util.runCmd(cmd)
        
        if props['pbrt_film_type'] == 'gbuffer':
            #split gbuffer to passes
            outImagePath = props['pbrt_rendered_file']
            if props['pbrt_denoiser_type'] == "optix":
                ext = "exr"
            else:
                ext = "pfm"
            if props['pbrt_run_denoiser'] == True:
                if ext == "exr":
                    denoised = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.exr'.format("denoised")
                    self.DenoiseOptix(props, outImagePath, denoised)
                    #result = self.get_result()
                    #result.layers[0].load_from_file(denoised)
                    self.LoadResult(denoised, props["scale_x"], props["scale_y"])
                elif ext=="pfm": #oidn
                    #self.add_pass("Albedo", 4, "RGBA")
                    #self.add_pass("Normal", 4, "RGBA")
                    self.SplitGbuffer(props, outImagePath, ext)
                    beauty = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.{}'.format("pass_0",ext)
                    albedo = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.{}'.format("pass_1",ext)
                    normal = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.{}'.format("pass_2",ext)
                    denoised = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.exr'.format("denoisedOidn")
                    self.DenoiseExternalOIDN(props, beauty, albedo, normal, denoised)
                    
                    #result = self.get_result()
                    #result.layers[0].load_from_file(denoised)
                    self.LoadResult(denoised, props["scale_x"], props["scale_y"])
            else:
                #scene = depsgraph.scene
                active_view = self.active_view_get()
                result = self.get_result()
                self.add_pass("Albedo", 4, "RGBA")
                self.add_pass("Normal", 4, "RGBA")
                self.SplitGbuffer(props, outImagePath, ext)
                beauty = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.{}'.format("pass_0",ext)
                albedo = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.{}'.format("pass_1",ext)
                normal = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.{}'.format("pass_2",ext)
                #--------beauty---pass----
                img = bpy.data.images.load(beauty, check_existing=False)
                layerPass = result.layers[0].passes.find_by_name("Combined",active_view)
                pixel_count = img.size[0] * img.size[1]
                color = [0.0, 0.0, 0.0, 1.0]
                layerPass.rect = [color] * pixel_count
                data = np.array_split(img.pixels, len(img.pixels)/4)
                print("AOV color done")
                layerPass.rect = data
                bpy.data.images.remove(img)
                #--------beauty---pass----
                #--------albedo---pass----
                img = bpy.data.images.load(albedo, check_existing=False)
                layerPass = result.layers[0].passes.find_by_name("Albedo", active_view)
                pixel_count = img.size[0] * img.size[1]
                color = [0.0, 0.0, 0.0, 1.0]
                layerPass.rect = [color] * pixel_count
                data = np.array_split(img.pixels, len(img.pixels)/4)
                print("AOV albedo done")
                layerPass.rect = data
                bpy.data.images.remove(img)
                #--------albedo---pass----
                #--------normal---pass----
                img = bpy.data.images.load(normal, check_existing=False)
                layerPass = result.layers[0].passes.find_by_name("Normal", active_view)
                pixel_count = img.size[0] * img.size[1]
                color = [0.0, 0.0, 0.0, 1.0]
                layerPass.rect = [color] * pixel_count
                data = np.array_split(img.pixels, len(img.pixels)/4)
                print("AOV normal done")
                layerPass.rect = data
                bpy.data.images.remove(img)
                #--------normal---pass----
            
            #scene = depsgraph.scene
            #scale = scene.render.resolution_percentage / 100.0
            #self.size_x = int(scene.render.resolution_x * scale)
            #self.size_y = int(scene.render.resolution_y * scale)
            
            #self.update_render_passes(scene, renderlayer="beauty")
            #self.update_render_passes(scene, renderlayer="albedo")
            
            #result = self.begin_result(0, 0, self.size_x, self.size_y, layer="beauty")
            #result.layers[0].load_from_file(beauty)
            #self.end_result(result)
            #result = self.begin_result(0, 0, self.size_x, self.size_y, layer="albedo")
            #result.layers[0].load_from_file(albedo)
            #self.end_result(result)
            
            #self.register_pass(scene, None, "Albedo", 3, "albedo", 'COLOR')
            #self.register_pass(scene, renderlayer, "Albedo", 3, "RGB", 'COLOR')
            #self.register_pass(scene, renderlayer, "Normal", 3, "RGB", 'COLOR')
            #self.register_pass(scene, renderlayer, "Albedo", 1, "X", 'VALUE')
            #self.add_pass("beauty", 3, "RGB", layer="Albedo")
            #self.add_pass("albedo", 3, "RGB", layer="View Layer")
            #self.add_pass("normal", 3, "RGB", layer="View Layer")
            
        else:
            outImagePath = props['pbrt_rendered_file']
            #result = self.get_result()
            #result.layers[0].load_from_file(outImagePath)
            self.LoadResult(outImagePath, props["scale_x"], props["scale_y"])
         
    def DenoiseExternal(self, props, beauty, albedo, normal, result):
        denoiserExecPath = util.switchpath(props['pbrt_denoiser_dir'])+'/'+'Denoiser.exe'
        cmd = [ denoiserExecPath, "-i", beauty, "-a", albedo, "-n", normal, "-o", result]
        util.runCmd(cmd)
    def DenoiseOptix(self, props, buffer, result):
        pbrtImgtoolPath = util.switchpath(props['pbrt_bin_dir'])+'/'+'imgtool.exe'
        cmd = [ pbrtImgtoolPath, "denoise-optix", buffer, "-outfile", result]
        util.runCmd(cmd)
    def DenoiseExternalOIDN(self, props, beauty, albedo, normal, result):
        denoisedPfm = util.switchpath(props['pbrt_project_dir'])+'/'+'{}.pfm'.format("denoised")
        
        denoiserExecPath = util.switchpath(props['pbrt_denoiser_dir'])+'/'+'oidnDenoise.exe'
        cmd = [ denoiserExecPath, "-hdr", beauty, "-alb", albedo, "-nrm", normal, "-o", denoisedPfm]
        util.runCmd(cmd)
        
        itoolExecPath = util.switchpath(props['pbrt_bin_dir'])+'/'+'imgtool.exe'
        cmd = [ itoolExecPath, "convert", denoisedPfm, "--outfile", result]
        util.runCmd(cmd)
    
    def run_tev_th(self):
        pbrtTevPath = util.switchpath(bpy.context.scene.pbrtv4.pbrt_bin_dir)+'/'+'tev.exe'
        #start tev
        cmd = [ pbrtTevPath ]
        util.runCmd(cmd)
            
    def RunTevRender(self, props, sceneFile):
        self.tev_th = threading.Thread(target=self.run_tev_th)
        self.tev_th.start()
        #pbrt --display-server localhost:14158 scene.pbrt
        # Compute pbrt executable path
        outImagePath = props['pbrt_rendered_file']
        pbrtExecPath = util.switchpath(props['pbrt_bin_dir'])+'/'+'pbrt.exe'
        file = sceneFile
        #start render
        if props['pbrt_compute_mode'] == 'CPU':
            cmd = [ pbrtExecPath,'--display-server', 'localhost:14158', '--write-partial-images', file ]
        else:
            cmd = [ pbrtExecPath, "--gpu", "--display-server", "localhost:14158", '--write-partial-images', file ]
        util.runCmd(cmd)
        
        #outImagePath = os.path.join(outDir, "pbrt.exr")
        #outImagePath = util.switchpath(props['pbrt_project_dir'])+'/'+'render.exr'
        #bpy.ops.image.open(filepath=outImagePath)
        #result = self.get_result()
        #result.layers[0].load_from_file(outImagePath)
        self.LoadResult(outImagePath, props["scale_x"], props["scale_y"])
    
    def RunDenoiser(self, props):
        #imgtool denoise-optix noisy.exr --outfile denoised.exr
        # Compute pbrt executable path
        pbrtImgtoolPath = util.switchpath(props['pbrt_bin_dir'])+'/'+'imgtool.exe'
        inImagePath = util.switchpath(props['pbrt_project_dir'])+'/'+'render.exr'
        outImagePath = util.switchpath(props['pbrt_project_dir'])+'/'+'Denoised.exr'
        
        cmd = [ pbrtImgtoolPath, "denoise-optix", inImagePath, "--outfile", outImagePath]
        #util.runCmd(cmd)
        
        outConvPbrtFile = open(outImagePath, "w")
        util.runCmd(cmd, stdout=outConvPbrtFile, cwd=util.switchpath(props['pbrt_project_dir']))
        outConvPbrtFile.close()
        
        outImagePath = util.switchpath(props['pbrt_project_dir'])+'/'+'Denoised.exr'
        bpy.ops.image.open(filepath=outImagePath)
        
    def RunTestOperator(self):
        print("Operator test!!!!!!!!!!!")
        
    def update_render_passes(self, scene=None, renderlayer=None):
        if not self.is_preview:
            if bpy.context.scene.pbrtv4.pbrt_film_type == 'gbuffer':
                self.register_pass(scene, renderlayer, "Combined", 4, "RGBA", 'COLOR')
                self.register_pass(scene, renderlayer, "Albedo", 4, "RGBA", 'COLOR')
                self.register_pass(scene, renderlayer, "Normal", 4, "RGBA", 'VECTOR')
