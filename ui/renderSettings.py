import bpy
from bl_ui.properties_render import RenderButtonsPanel
from bl_ui.properties_world import WorldButtonsPanel
from bl_ui.properties_material import MaterialButtonsPanel
from bl_ui.properties_object import ObjectButtonsPanel
from bl_ui.properties_data_camera import CameraButtonsPanel
from bpy.types import Panel, Menu

class PBRTV4_RENDER_PT_sampling(RenderButtonsPanel, Panel):
    COMPAT_ENGINES = {"PBRTV4"}
    bl_label = "Sampling"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.pbrtv4
        layout.operator("pbrtv4.start_render", text="Start render")
        layout.operator("pbrtv4.start_render_anim", text="Start animation render")
        #layout.operator("pbrtv4.export_for_render", text="Export pbrt4 scene")
        layout.prop(asr_scene_props, "pbrt_image_server", text="Display image in")
        layout.prop(asr_scene_props, "pbrt_export_scene_only", text="Export scene only")
        layout.prop(asr_scene_props, "pbrt_scene_only", text="Export settings only, not geometry. For rerender scene from dif cams")
        layout.prop(asr_scene_props, "pbrt_compute_mode", text="Compute device")
        
        layout.prop(asr_scene_props, "pbrt_bin_dir", text="PBRTV4 bin")
        #layout.prop(asr_scene_props, "pbrt_denoiser_dir", text="External denoiser")
        layout.separator()
        layout.prop(asr_scene_props, "pbrt_project_dir", text="Project folder")
        layout.prop(asr_scene_props, "pbrt_integrator", text="Integrator")
        
        layout.prop(asr_scene_props, "pbrt_accelerator", text="Accelerator")
        if asr_scene_props.pbrt_accelerator == 'bvh':
            col = layout.column(align=True)
            #col.alignment  = 'CENTER'
            col.prop(asr_scene_props, "pbrt_bvh_maxnodeprims", text="maxnodeprims")
            col.prop(asr_scene_props, "pbrt_bvh_splitmethod", text="splitmethod")
            
        if asr_scene_props.pbrt_integrator == 'PATH':
            col = layout.column(align=True)
            col.prop(asr_scene_props, "pbrt_sampler", text="Sampler")
            col.prop(asr_scene_props, "pbrt_samples", text="Samples")
            col.prop(asr_scene_props, "pbrt_max_depth", text="Max Depth")
            #col.prop(asr_scene_props, "textures_index", text="Cryptomatte Object")
            #col.prop(asr_scene_props, "pixel_filter_size", text="Cryptomatte Object")
        elif asr_scene_props.pbrt_integrator == 'VOLPATH':
            col = layout.column(align=True)
            col.prop(asr_scene_props, "pbrt_sampler", text="Sampler")
            col.prop(asr_scene_props, "pbrt_samples", text="Samples")
            col.prop(asr_scene_props, "pbrt_max_depth", text="Max Depth")
        elif asr_scene_props.pbrt_integrator == 'BDPT':
            col = layout.column(align=True)
            col.prop(asr_scene_props, "pbrt_sampler", text="Sampler")
            col.prop(asr_scene_props, "pbrt_samples", text="Samples")
            col.prop(asr_scene_props, "pbrt_max_depth", text="Max Depth")
            col.prop(asr_scene_props, "pbrtIntegratorBdptLSS", text="Light Sample Strategy")
            col.prop(asr_scene_props, "pbrtIntegratorBdptVS", text="Visualize Strategies")
            col.prop(asr_scene_props, "pbrtIntegratorBdptVW", text="Visualize weights")
        else:
            col = layout.column(align=True)
            col.prop(asr_scene_props, "pbrt_sampler", text="Sampler")
            col.prop(asr_scene_props, "pbrt_samples", text="Samples")
            col.prop(asr_scene_props, "pbrt_max_depth", text="Max Depth")
            
        layout.prop(asr_scene_props, "pbrt_pfilter_type", text="Pixel filter type")
        if not asr_scene_props.pbrt_pfilter_type == 'none':
            col = layout.column(align=True)
            col.prop(asr_scene_props, "pbrt_pfilter_xradius", text="xradius")
            col.prop(asr_scene_props, "pbrt_pfilter_yradius", text="yradius")
            
        layout.separator()
        layout.prop(asr_scene_props, "pbrt_linked_as_instance", text="Export linked as instances")
        layout.prop(asr_scene_props, "pbrt_use_realDisp", text="Use real displacement on mesh")

class PBRTV4_RENDER_PT_Film(RenderButtonsPanel, Panel):
    COMPAT_ENGINES = {"PBRTV4"}
    bl_label = "Film"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.pbrtv4
        
        layout.prop(asr_scene_props, "pbrt_ColorSpace", text="Color Space")
        layout.prop(asr_scene_props, "pbrt_film_savefp16", text="Color depth")
        layout.prop(asr_scene_props, "pbrt_film_type", text="Film output type")
        if asr_scene_props.pbrt_film_type == 'gbuffer':
            col = layout.column(align=True)
            col.prop(asr_scene_props, "pbrt_run_denoiser", text="Run denoiser")
            col.prop(asr_scene_props, "pbrt_denoiser_type", text="Pbrt denoiser type")
            if asr_scene_props.pbrt_denoiser_type == 'oidn':
                layout.prop(asr_scene_props, "pbrt_denoiser_dir", text="External denoiser")
            
        layout.prop(asr_scene_props, "pbrt_film_sensor", text="Sensor")
        layout.prop(asr_scene_props, "pbrt_film_iso", text="ISO")
        layout.prop(asr_scene_props, "pbrt_film_whitebalance", text="Whitebalance")
        layout.separator()
        
class PBRTV4_MATERIAL_PT_slots(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_label = "Material"
    bl_region_type = 'WINDOW'
    bl_context = "material"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.material or context.object) and engine == 'PBRTV4'

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            is_sortable = len(ob.material_slots) > 1
            rows = 3
            if (is_sortable):
                rows = 5

            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ADD', text="")
            col.operator("object.material_slot_remove", icon='REMOVE', text="")

            col.separator()

            col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        row = layout.row()

        if ob:
            row.template_ID(ob, "active_material", new="material.new")

            if slot:
                icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
                row.prop(slot, "link", icon=icon_link, icon_only=True)

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        elif mat:
            row.template_ID(space, "pin_id")

class PBRTV4_MATERIAL_PT_emissions(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_label = "Material"
    bl_region_type = 'WINDOW'
    bl_context = "material"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.material or context.object) and engine == 'PBRTV4'

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data
        
        if ob:
            #print (mat.pbrtv4_emission_color[0])
            layout.prop(mat, "pbrtv4_isEmissive", text="Enable emission")
            
            if mat.pbrtv4_isEmissive == True:
                col = layout.column(align=True)
                col.prop(mat, "pbrtv4_emission_preset", text="Preset")
                if mat.pbrtv4_emission_preset == 'color':
                    col.prop(mat, "pbrtv4_emission_color", text="Color")
                elif mat.pbrtv4_emission_preset == 'blackbody':
                    col.prop(mat, "pbrtv4_emission_temp", text="Temperature")
                col.prop(mat, "pbrtv4_emission_power", text="Power")
        elif mat:
            pass
            #row.template_ID(space, "pin_id")
            
class PBRTV4_PT_MATERIAL_previev(MaterialButtonsPanel, Panel):
    COMPAT_ENGINES = {"PBRTV4"}
    bl_label = "Preview"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.material and (engine == "PBRTV4")

    def draw(self, context):
        layout = self.layout
        #image = bpy.ops.image.open(filepath="")
        #preview_mat
        layout.template_preview(context.material, show_buttons=False)
        layout.prop(context.scene.pbrtv4, "pbrt_prev_fov", text="Preview FOV")
        layout.prop(context.scene.pbrtv4, "pbrt_prev_samples", text="Preview Samples")
        
class PBRTV4_PT_OBJECT_prop(ObjectButtonsPanel, Panel):
    COMPAT_ENGINES = {"PBRTV4"}
    bl_context = "object"
    bl_label = "PBRTV4Settings"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.object and (engine == "PBRTV4")

    def draw(self, context):
        layout = self.layout
        obj = context.object
        layout.prop(obj, "pbrtv4_isPortal", text="Is Portal")
        
class PBRTV4_WORLD_PT_common(WorldButtonsPanel, Panel):
    COMPAT_ENGINES = {"PBRTV4"}
    bl_label = "World Light"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.pbrtv4_world
      
        layout.prop(asr_scene_props, "pbrtv4_world_mode", text="World")
        
        if asr_scene_props.pbrtv4_world_mode == 'CONSTANT':
            col = layout.column(align=True)
            col.prop(asr_scene_props, "pbrtv4_world_color", text="Color")
            col.prop(asr_scene_props, "pbrtv4_world_power", text="Power")
        elif asr_scene_props.pbrtv4_world_mode == 'ENVIRONMENT':
            col = layout.column(align=True)
            col.prop(asr_scene_props, "pbrtv4_world_show_preview", text="show preview")
            if asr_scene_props.pbrtv4_world_show_preview:
                col.template_ID_preview(asr_scene_props, "pbrtv4_world_path", open="image.open")
            else:
                col.template_ID(asr_scene_props, "pbrtv4_world_path", open="image.open")
                layout.operator("pbrtv4.convert_envmap", text="Convert env map")
            col.prop(asr_scene_props, "pbrtv4_world_power", text="Power")
            col.prop(asr_scene_props, "pbrtv4_world_rotation", text="Rotation")
        elif asr_scene_props.pbrtv4_world_mode == 'NISHITA':
            col = layout.column(align=True)
            col.prop(asr_scene_props, "pbrtv4_nishita_albedo", text="Albedo")
            col.prop(asr_scene_props, "pbrtv4_nishita_elevation", text="Elevation")
            col.prop(asr_scene_props, "pbrtv4_nishita_turbidity", text="Turbidity")
            col.prop(asr_scene_props, "pbrtv4_nishita_res", text="Resolution")
            col.prop(asr_scene_props, "pbrtv4_world_power", text="Power")
            col.prop(asr_scene_props, "pbrtv4_world_rotation", text="Rotation")
            
class PBRTV4_CAMERA_PT_common(CameraButtonsPanel, Panel):
    COMPAT_ENGINES = {"PBRTV4"}
    bl_label = "PBRTV4 Camera"
    #bl_context = "camera"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1
    
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.camera and (engine == 'PBRTV4')
    def update_object(self, context):
        cam_ob = context.camera
        cam_d = context.camera.pbrtv4_camera.pbrtv4_camera_focaldistance
        target_dist = (cam_ob.pbrtv4_camera.pbrtv4_camera_focus_obj.location - cam_ob.location).length
        cam_d = target_dist
    def draw(self, context):
        layout = self.layout
        cam = context.camera.pbrtv4_camera
        layout.prop(cam, "pbrtv4_camera_type", text="Camera type")
        if cam.pbrtv4_camera_type == "realistic":
            layout.prop(cam, "pbrtv4_realistic_camera_file", text="realistic camera file")
            layout.prop(cam, "pbrtv4_realistic_camera_apperture", text="realistic camera apperture type")
            layout.prop_search(cam, "pbrtv4_camera_focus_obj", bpy.data, "objects",  text="target object")
            layout.prop(cam, "pbrtv4_camera_lensradius", text="F value (lens radius=(1/F))")
            if not cam.pbrtv4_camera_focus_obj:
                layout.prop(cam, "pbrtv4_camera_focaldistance", text="camera focal distance")
        elif cam.pbrtv4_camera_type == "perspective":
            layout.prop(cam, "pbrtv4_camera_use_dof", text="Use DOF")
            if cam.pbrtv4_camera_use_dof:
                layout.prop_search(cam, "pbrtv4_camera_focus_obj", bpy.data, "objects",  text="target object")
                #if cam.pbrtv4_camera_focus_obj:
                    #cam_ob = context.object
                    #target_dist = (cam.pbrtv4_camera_focus_obj.location - cam_ob.location).length
                    #cam_ob.data.pbrtv4_camera.pbrtv4_camera_focaldistance = target_dist
                    # print(cam.pbrtv4_camera_focus_obj.location)
                layout.prop(cam, "pbrtv4_camera_lensradius", text="F value (lens radius=(1/F))")
                if not cam.pbrtv4_camera_focus_obj:
                    layout.prop(cam, "pbrtv4_camera_focaldistance", text="camera focal distance")
                
class PBRTV4_LIGHT_PT_common(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    COMPAT_ENGINES = {"PBRTV4"}
    bl_label = "PBRTV4 Light"
    bl_region_type = 'WINDOW'
    #bl_context = "light"
    #bl_options = {'DEFAULT_CLOSED'}
    #bl_order = 1
    
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.light and (engine == 'PBRTV4')
    
    def draw(self, context):
        layout = self.layout
        light = context.light
        
        if light:
            layout.prop(light, "pbrtv4_light_power", text="pbrtv4_light_power")
            col = layout.column(align=True)
            col.prop(light, "pbrtv4_light_preset", text="Preset")
            if light.pbrtv4_light_preset == 'color':
                col.prop(light, "pbrtv4_light_color", text="Color")
            elif light.pbrtv4_light_preset == 'temperature':
                col.prop(light, "pbrtv4_light_temperature", text="Blackbody temperature")

def register():
    bpy.utils.register_class(PBRTV4_RENDER_PT_sampling)
    bpy.utils.register_class(PBRTV4_MATERIAL_PT_slots)
    bpy.utils.register_class(PBRTV4_MATERIAL_PT_emissions)
    bpy.utils.register_class(PBRTV4_PT_MATERIAL_previev)
    bpy.utils.register_class(PBRTV4_RENDER_PT_Film)
    bpy.utils.register_class(PBRTV4_WORLD_PT_common)
    bpy.utils.register_class(PBRTV4_PT_OBJECT_prop)
    bpy.utils.register_class(PBRTV4_CAMERA_PT_common)
    bpy.utils.register_class(PBRTV4_LIGHT_PT_common)
    
def unregister():
    bpy.utils.unregister_class(PBRTV4_LIGHT_PT_common)
    bpy.utils.unregister_class(PBRTV4_CAMERA_PT_common)
    bpy.utils.unregister_class(PBRTV4_PT_OBJECT_prop)
    bpy.utils.unregister_class(PBRTV4_RENDER_PT_sampling)
    bpy.utils.unregister_class(PBRTV4_MATERIAL_PT_slots)
    bpy.utils.unregister_class(PBRTV4_MATERIAL_PT_emissions)
    bpy.utils.unregister_class(PBRTV4_PT_MATERIAL_previev)
    bpy.utils.unregister_class(PBRTV4_RENDER_PT_Film)
    bpy.utils.unregister_class(PBRTV4_WORLD_PT_common)