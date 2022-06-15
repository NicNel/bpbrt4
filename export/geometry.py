from .mesh_ply import write_ply_mesh
import os
import bpy
import copy

from .lights import export_distant_light, export_point_light, export_spot_light

from ..utils import util
import mathutils
#AttributeBegin
	#Transform [ -4.36999983e-08 -1 0 0 1 -4.36999983e-08 0 0 0 0 1 0 10.3253136 3.79926968 6.5470705 1  ]
    #ObjectBegin "plan_definitif.001"
    #NamedMaterial "INOX"
    #Shape "plymesh" "string filename" [ "geometry/mesh_00003.ply" ] 
    #NamedMaterial "CAOUTCHOUC"
    #Shape "plymesh" "string filename" [ "geometry/mesh_00004.ply" ] 
    #NamedMaterial "METAL_BLANC"
    #Shape "plymesh" "string filename" [ "geometry/mesh_00005.ply" ] 
    #NamedMaterial "MATELAS"
    #Shape "plymesh" "string filename" [ "geometry/mesh_00006.ply" ] 
#ObjectEnd
#AttributeEnd

#also can contain emission like:
#AreaLightSource "diffuse"
        #"rgb L" [ 15.258819 12.083925 9.589462 ]

class ObjectInfo(object):
    def __init__(self, _name):
        self.parts = [] # dict containing entries like mesh_name : [exported materials]
        self.materials = [] #dict name, isEm, color
        self.name = _name
        self.Transform = ""
    def notEmpty(self):
        return len(self.parts)>0
    def addPart(self, _name, _mat):
        self.parts.append(_name)
        self.materials.append(_mat)
    def to_String(self):
        print ('Name {}'.format(self.name))
        print ('Meshes:')
        for part_n in self.parts:
            print ('	Mesh part: {}'.format(part_n))
        print ('Materials:')
        for part_m in self.materials:
            print ('	Material: {} isEmitter: {}'.format(part_m.name, part_m.isEmissive))
    def to_DictStr(self, folder):
        result = "AttributeBegin\n"
        result += '    Transform [{}]\n'.format(self.Transform)
        #loop parts
        for i in range(len(self.parts)):
            result += self.materials[i].getEmissionStr()
            if not self.materials[i].mediumName == "":
                result += "AttributeBegin\n"
                result += '    MediumInterface "" "{}"\n'.format(self.materials[i].mediumName)
            result += '    NamedMaterial "{}"\n'.format(self.materials[i].name)
            filename = folder+"{}.ply".format(self.parts[i])
            
            if not self.materials[i].alpha == 1.0:
                alpha = self.materials[i].alpha
                result += '    Shape "plymesh"\n'
                result += '    '+'    '+'"string filename" [ "{}" ]\n'.format(filename)
                result += '    '+'    '+'"float alpha" [{}]\n'.format(alpha)
            else:
                result += '    Shape "plymesh"\n'
                result += '    '+'    '+'"string filename" [ "{}" ]\n'.format(filename)
            if not self.materials[i].mediumName == "":
                result += "AttributeEnd\n"
        #loop parts
        result += "AttributeEnd\n"
        return result
    def to_InstanceDictStr(self, folder):
        result = "AttributeBegin\n"
        #result += '    Transform [{}]\n'.format(self.Transform)
        result += '    ObjectBegin "{}"\n'.format(self.name)
        #loop parts
        for i in range(len(self.parts)):
            result += self.materials[i].getEmissionStr()
            result += '        NamedMaterial "{}"\n'.format(self.materials[i].name)
            filename = folder+"{}.ply".format(self.parts[i])
            result += '        Shape "plymesh" "string filename" [ "{}" ]\n'.format(filename)
        #loop parts
        result += "    ObjectEnd\n"
        result += "AttributeEnd\n"
        return result

class GeometryExporter:
    need_update=False
    
    def __init__(self):
        self.exported_meshes = {} # dict containing entries like mesh_name : [exported materials]
        self.exported_materials = set() # exported materials
        self.materialData = []
        self.instancedData = []
        self.portalsData = []
        self.lightsData = []
        
        self.linkedData = []
        self.linkedName = []
        
        self.use_disp = set() # exported materials
        self.matDispData = []#actual material disp settings
        self.dispData = []#info for convertation
    
    @staticmethod
    def addDefaultMat(name, data, color):
        c=color
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='    "string type" [ "coateddiffuse" ]\n'
        res+='    "rgb reflectance" [ {} {} {} ]\n'.format(c[0], c[1], c[2])
        res+='    "float uroughness" [ 0.1 ]\n'
        res+='    "float vroughness" [ 0.1 ]\n'
        res+='    "float eta" [1.5]\n'
        res+='    "float thickness" [0.0]\n'
        res+='    "bool remaproughness" false\n'
        data.append(res)
    
    @staticmethod
    def updateMatName(mat, export_name):
        ID = 0
        OutputNode = None
        for node in mat.node_tree.nodes:
            if hasattr(node, 'isPbrtv4TreeNode'):
                node.setId(mat.name, ID)
                ID+=1
            if node.name == 'Material Output':
                OutputNode = node
        #add if
        input = OutputNode.inputs[0] #shader input
        node_link = input.links[0]
        curNode =  node_link.from_node
        if hasattr(curNode, 'isPbrtv4TreeNode'):
            #set material name instead of generated
            curNode.name = export_name
    
    @staticmethod
    def export_mat_get(mat, export_name):
        materialData = []
        outInfo = []
        shapeInfo = {"data":materialData, "medium":None, "emission":None, "alpha":None}
        
        if mat.use_nodes == False:
            GeometryExporter.addDefaultMat(export_name, materialData, [1,0,0])
            print('! WARN !', "Material: {} has no NodeTree".format(mat.name))
            return shapeInfo
            
        OutputNode = mat.node_tree.nodes.get('PBRT4 Output')
        #for n in mat.node_tree.nodes:
        #    print(n)
        
        if OutputNode == None:
            GeometryExporter.addDefaultMat(export_name, materialData, [1,0,0])
            print('! WARN !', "Material: {} has no active Output Node".format(mat.name))
            return shapeInfo

        #export medium
        volume_input = OutputNode.inputs[1] #shader volume
        if volume_input.is_linked:
            volume_node_link = volume_input.links[0]
            volume =  volume_node_link.from_node
            #volume.pbrtv4NodeID = export_name+"_volume"
            medium_id ="{}::{}".format("preview", 0)
            volume.setId(mat.name, medium_id)
            #volume.pbrtv4NodeID = "{}::{}".format(volume.pbrtv4NodeID, object_instance.object.name) #export medium for each part
            volume.Backprop(outInfo, materialData)
            #outInfo.append(volume.pbrtv4NodeID)
            #return outInfo
            shapeInfo["medium"] = outInfo
        
        #export emission
        emission_input = OutputNode.inputs[2] #shader volume
        if emission_input.is_linked:
            em_node_link = emission_input.links[0]
            em =  em_node_link.from_node
            emInfo = em.getEmissionInfo(mat.name)
            shapeInfo["emission"] = emInfo
            #print(emInfo.getEmissionStr())
            
        #export alpha
        alpha_input = OutputNode.inputs[4] #shader displacement
        if alpha_input.is_linked:
            #texture used
            pass
        else:
            alpha = alpha_input.default_value
            if not alpha == 1.0:
                shapeInfo["alpha"] = alpha
        
        input = OutputNode.inputs[0] #shader input
        if input.is_linked:
            node_link = input.links[0]
            curNode =  node_link.from_node
            ID = 0
            #OutputNode = None
            ExportedNodes = []
            for node in mat.node_tree.nodes:
                if hasattr(node, 'isPbrtv4TreeNode'):
                    node.setId(mat.name, ID)
                    ID+=1
            if hasattr(curNode, 'isPbrtv4TreeNode'):
                #set material name instead of generated
                if hasattr(curNode, 'isPbrtv4Emitter'):
                    curNode.pbrtv4NodeID = export_name
                    curNode.to_dict(ExportedNodes, materialData)
                    emData[export_name] = curNode.em_to_dict(ExportedNodes, materialData, "area_em_"+export_name)
                else:
                    curNode.pbrtv4NodeID = export_name
                    curNode.Backprop(ExportedNodes, materialData)
            else:
                print('! WARN !', "Material: ", mat.name, " not valid pbrtV4 bsdf")
                GeometryExporter.addDefaultMat(export_name, materialData, [1,0,0])
        else:
            print('! WARN !', "Material: ", mat.name, " not valid pbrtV4 bsdf")
            GeometryExporter.addDefaultMat(export_name, materialData, [1,0,0])
        return shapeInfo
            
    def export_mat(self, object_instance, matid, abs_path):
        outInfo = []
        shapeInfo = {"medium":None, "emission":None, "alpha":None}
        
        mat = object_instance.object.material_slots[matid].material
        #print ('Exporting material: ', mat.name)
        
        if mat.use_nodes == False:
            if not mat.name in self.exported_materials:
                self.addDefaultMat(mat.name, self.materialData, [1,0,0])
                self.exported_materials.add(mat.name)
                print('! WARN !', "Material: {} has no NodeTree".format(mat.name))
            return shapeInfo
        
        OutputNode = mat.node_tree.nodes.get('PBRT4 Output')
        if OutputNode == None:
            if not mat.name in self.exported_materials:
                self.addDefaultMat(mat.name, self.materialData, [1,0,0])
                self.exported_materials.add(mat.name)
                print('! WARN !', "Material: {} has no active Output Node".format(mat.name))
            return shapeInfo
            
        #export medium
        volume_input = OutputNode.inputs[1] #shader volume
        if volume_input.is_linked:
            volume_node_link = volume_input.links[0]
            volume =  volume_node_link.from_node
            #volume.pbrtv4NodeID = export_name+"_volume"
            medium_id ="{}::{}".format(object_instance.object.name, matid)
            volume.setId(mat.name, medium_id)
            #volume.pbrtv4NodeID = "{}::{}".format(volume.pbrtv4NodeID, object_instance.object.name) #export medium for each part
            volume.Backprop(outInfo, self.materialData)
            #outInfo.append(volume.pbrtv4NodeID)
            #return outInfo
            shapeInfo["medium"] = outInfo
        #export emission
        emission_input = OutputNode.inputs[2] #shader volume
        if emission_input.is_linked:
            em_node_link = emission_input.links[0]
            em =  em_node_link.from_node
            emInfo = em.getEmissionInfo(mat.name)
            shapeInfo["emission"] = emInfo
            #print(emInfo.getEmissionStr())
        #export displacement
        disp_input = OutputNode.inputs[3] #shader displacement
        if disp_input.is_linked:
            disp_node_link = disp_input.links[0]
            disp =  disp_node_link.from_node
            dInfo = disp.getDispInfo()
            dInfo.outfile = abs_path
            self.matDispData.append(dInfo)
            #self.dispData.append(util.DispInfo.CreateCopy(dInfo))
            self.dispData.append(dInfo)
            self.use_disp.add(mat.name)#add mat to list, which uses disp
        #export alpha
        alpha_input = OutputNode.inputs[4] #shader displacement
        if alpha_input.is_linked:
            #texture used
            pass
        else:
            alpha = alpha_input.default_value
            if not alpha == 1.0:
                shapeInfo["alpha"] = alpha
                
        #export material nodetree
        if not mat.name in self.exported_materials:
            ID = 0
            #OutputNode = None
            ExportedNodes = []
            for node in mat.node_tree.nodes:
                if hasattr(node, 'isPbrtv4TreeNode'):
                    node.setId(mat.name, ID)
                    ID+=1
            input = OutputNode.inputs[0] #shader input
            if input.is_linked:
                node_link = input.links[0]
                curNode =  node_link.from_node
                if hasattr(curNode, 'isPbrtv4TreeNode'):
                    #set material name instead of generated
                    curNode.pbrtv4NodeID = mat.name
                    curNode.Backprop(ExportedNodes, self.materialData)
                else:
                    #not bpbrt4 material
                    #add default instead
                    print('! WARN !', "Material: {} not valid bpbrt4 bsdf".format(mat.name))
                    self.addDefaultMat(mat.name, self.materialData, [1,0,0])
            else:
                print('! WARN !', "Material: {} has no bsdf linked".format(mat.name))
                self.addDefaultMat(mat.name, self.materialData, [1,0,0])
            self.exported_materials.add(mat.name)
        else:
            pass
            #print(mat.name, " already exported")
        return shapeInfo
                        
    def save_mesh(self, b_mesh, matrix_world, b_name, file_path, mat_nr, info):
        if b_mesh == None:
            print('! WARN !', "Object: {} has no mesh. Skipping.".format(b_name))
            return False
        
        b_mesh.calc_normals()
        b_mesh.calc_loop_triangles() # Compute the triangle tesselation
        if mat_nr == -1:
            name = b_name
        else:
            name = "%s-%s" %(b_name, b_mesh.materials[mat_nr].name)
            
        loop_tri_count = len(b_mesh.loop_triangles)
        if loop_tri_count == 0:
            print('! WARN !', "Mesh: {} has no faces. Skipping.".format(name))
            return False

		# collect faces by mat index
        mesh_faces = b_mesh.loop_triangles
        if mat_nr == -1:
            print('! WARN !', "Object: {} has no materials. Default added".format(name))
            mtInfo = util.MatInfo.CreateInfo("default")
            info.addPart(name, mtInfo)
            write_ply_mesh(file_path, b_name, b_mesh, mesh_faces) #export whole mesh
            return False
            
        cnt = 0
        ffaces_mats=[]
        for f in mesh_faces:
            mi = f.material_index
			#export only part with material id / need to be optimized
            if mi == mat_nr:
                ffaces_mats.append(f)
                cnt=cnt+1
        
        if cnt > 0: # Only save complete meshes
            #add only parts with data
            #mtInfo = util.MatInfo.CreateInfo(b_mesh.materials[mat_nr].name, b_mesh.materials[mat_nr].pbrtv4_isEmissive, b_mesh.materials[mat_nr].pbrtv4_emission_color, b_mesh.materials[mat_nr].pbrtv4_emission_power, b_mesh.materials[mat_nr].pbrtv4_emission_preset, b_mesh.materials[mat_nr].pbrtv4_emission_temp)
            mtInfo = util.MatInfo.CreateInfo(b_mesh.materials[mat_nr].name)
            info.addPart(name, mtInfo)
            write_ply_mesh(file_path, b_name, b_mesh, ffaces_mats)
            return True
        else:
            print('! WARN !', "Material ", b_mesh.materials[mat_nr].name, " has no mesh data assigned! Skipped...")
        return False

    def export_object_mat(self, object_instance, mat_nr, info, folder):
        #object export
        b_object = object_instance.object
        if b_object.is_instancer and not b_object.show_instancer_for_render:
            return#don't export hidden mesh
        if mat_nr == -1:
            name = b_object.name_full
        else:
            name = "%s-%s" %(b_object.name_full, b_object.data.materials[mat_nr].name)
        abs_path = os.path.join(folder, "%s.ply" % name)
        
        if not object_instance.is_instance:
            #save the mesh once, if it's not an instance, or if it's an instance and the original object was not exported
            b_mesh = b_object.to_mesh()
            if self.save_mesh(b_mesh, b_object.matrix_world, b_object.name_full, abs_path, mat_nr, info) and mat_nr >= 0:
                mat_info = self.export_mat(object_instance, mat_nr, abs_path)
                #print(mat_info)
                if not mat_info["emission"] == None:
                    info.materials[-1] = mat_info["emission"]
                if not mat_info["medium"] == None:
                    info.materials[-1].mediumName = mat_info["medium"][0]
                if not mat_info["alpha"] == None:
                    info.materials[-1].alpha = mat_info["alpha"]
                #export_material(export_ctx, b_object.data.materials[mat_nr])
            else:
                pass
            b_object.to_mesh_clear()

    def export_object(self, object_instance, folder):
        objectInfo = ObjectInfo(object_instance.object.name)
        objectInfo.Transform = util.matrixtostr(object_instance.matrix_world.transposed() )
        mat_count = len(object_instance.object.data.materials)
        valid_mats=0
        #export if mats exist
        for mat_nr in range(mat_count):
            if object_instance.object.data.materials[mat_nr] is not None:
                valid_mats += 1
                self.export_object_mat(object_instance, mat_nr, objectInfo, folder)
        #export with default mat
        if valid_mats == 0: #no material, or no valid material
            self.export_object_mat(object_instance, -1, objectInfo, folder)
        return objectInfo
   
    #AttributeBegin
        #ConcatTransform [ -0.13143252 -0 0.15960668 0 0.12390019 -0 0.102029026 0 0 0.2362264 0 0 -2829.432 17.751171 -3376.446 1  ]
        #ObjectInstance "meadow_v5"
    #AttributeEnd
    
    def add_instance(self, name, transform):
        #add compound object to scene geometry with ObjectBegin
        if name not in self.instancedData:
            self.instancedData.append(name)
        #add instance with base obj name
        #get particle transform
        #partSys = object_instance.particle_system
        #print (object_instance.orco)
        
        result = "AttributeBegin\n"
        result += '    ConcatTransform [{}]\n'.format(transform)
        result += '    ObjectInstance "{}"\n'.format(name)
        result += "AttributeEnd\n"
        return result

    #"point portal" [ 1 2 3 1 2 3 ...]
    #4 (float) frame points (? not sure for now)
    def ExportPortal(self, instance):
        b_object = instance.object
        b_mesh = b_object.to_mesh()
        b_mesh.calc_loop_triangles()
        cnt = len(b_mesh.vertices)
        print("count: ", cnt)
        vStr = ""
        resStr = ""
        if cnt == 4:
            v = b_mesh.vertices
            mat = b_object.matrix_world
            
            loc = mat @ v[0].co
            vStr +='{} {} {} '.format(loc[0], loc[1], loc[2])
            
            loc = mat @ v[1].co
            vStr +='{} {} {} '.format(loc[0], loc[1], loc[2])
            
            loc = mat @ v[3].co
            vStr +='{} {} {} '.format(loc[0], loc[1], loc[2])
            
            loc = mat @ v[2].co
            vStr +='{} {} {} '.format(loc[0], loc[1], loc[2])
            
            resStr ='"point3 portal" [ {}]\n'.format(vStr)
        b_object.to_mesh_clear()
        return resStr
        
    def ClearExportData(self):
        self.exported_meshes.clear()
        #del self.exported_meshes
        self.exported_materials.clear()
        #del self.exported_materials
        
        self.linkedData.clear()
        self.linkedName.clear()
        
        self.use_disp.clear()
        self.matDispData.clear()
        self.dispData.clear()
        
        #del self.materialData[:]
        #del self.materialData
        
        #del self.instancedData[:]
        #del self.instancedData
        #del self.portalsData[:]
        #del self.portalsData
        
    #Float width = parameters.GetOneFloat("width", 1.f);
    #Float width0 = parameters.GetOneFloat("width0", width);
    #Float width1 = parameters.GetOneFloat("width1", width);
    #std::string basis = parameters.GetOneString("basis", "bezier"); "bspline"
    #std::vector<Point3f> cp = parameters.GetPoint3fArray("P");
    #std::string curveType = parameters.GetOneString("type", "flat"); "cylinder" "ribbon"
    #std::vector<Normal3f> n = parameters.GetNormal3fArray("N");
    #AttributeBegin
        #Translate 34.92 55.92 -15.351
        #Shape "curve"
        #    "float width" [ 1.0 ]
        #    "float width0" [ 1.0 ]
        #    "float width1" [ 1.0 ]
        #    "string basis" [ "bspline" ]
        #    "point3 P" [1 1 1 2 2 2]
    #AttributeEnd
    def CreateHairShape2(self, width, points):
        res ='AttributeBegin\n'
        res+='    '+'NamedMaterial "default"\n'
        res+='    '+'Shape "cylinder"\n'
        res+='    '+'    '+'"float radius" [{}]\n'.format(width)
        res +='AttributeEnd\n'
        return res
    def CreateHairShape(self, width, points, mat, curveType = 'bezier'):
        res ='AttributeBegin\n'
        res+='    '+'NamedMaterial "{}"\n'.format(mat)
        res+='    '+'Shape "curve"\n'
        res+='    '+'    '+'"float width" [{}]\n'.format(width)
        res+='    '+'    '+'"string basis" ["{}"]\n'.format(curveType)
        res+='    '+'    '+'"integer degree" [{}]\n'.format(3)
        
        res+='    '+'    '+'"string type" ["cylinder"]\n'
        res+='    '+'    '+'"point3 P" [{}]\n'.format(points)
        res +='AttributeEnd\n'
        return res
    
    def Export_hairs(self, b_object, hairs, settings, matid):
        #export material
        matName = b_object.object.material_slots[matid].material.name
        #export particles
        res = ''
        for i, h in enumerate(hairs):
            #print('hair number {i}:'.format(i=i))
            mat = b_object.matrix_world
            Points = ""
            #st = mat @ h.hair_keys[-1].co
            #Points +='{} {} {} '.format(st[0], st[1], st[2])
            #Points +='{} {} {} '.format(st[0], st[1], st[2])
            #curves = h.curves[0].points
            ctype = "bezier" if ((len(h.hair_keys)-1) % 3 == 0) else "bspline"
            #print("Hair points count: ", len(h.hair_keys), "CURVE TYPE", ctype)
            
            #loc = h.location
            #Points +='{} {} {} '.format(loc[0], loc[1], loc[2])
            for j, hv in enumerate(h.hair_keys):
                loc = mat @ hv.co
                Points +='{} {} {} '.format(loc[0], loc[1], loc[2])
            #print('  vertex {i} coordinates: {co}'.format(i=i, co=hv.co))
            res += self.CreateHairShape(settings.root_radius, Points, matName, ctype)
        return res
    
    def ExportSceneGeometry(self, depsgraph, geometryFolder, engine, linked_as_instance = True, use_selection = False):
        #clear data in geometry folder 
        util.deleteAllInFolder(geometryFolder)
        #clead containers
        self.exported_meshes.clear()
        self.exported_materials = set()
        self.materialData = []
        self.instancedData = []
        self.portalsData = []
        self.lightsData = []
        
        self.linkedData = []
        self.linkedName = []
        
        self.use_disp = set() # exported materials
        self.matDispData = []#actual material disp settings
        self.dispData = []#info for convertation
        
        #add default grey mat to scene
        self.addDefaultMat("default", self.materialData, [0.5,0.5,0.5])
        #depsgraph = bpy.context.evaluated_depsgraph_get()#TODO: get RENDER evaluated depsgraph (not implemented)
        b_scene = depsgraph.scene
        #export_world(self.export_ctx, b_scene.world, self.ignore_background)
        #self.use_selection = False
        
        GeometryLst = []
        instStr = ""
        chunk_data = []
        
        infoLst = {}
        #main export loop
        #update_progress(progress)
        total_cnt = len(depsgraph.object_instances)
        counter = 0
        for object_instance in depsgraph.object_instances:
            counter = counter + 1
            engine.update_progress(counter/total_cnt)
            if use_selection:
                #skip if it's not selected or if it's an instance and the parent object is not selected
                if not object_instance.is_instance and not object_instance.object.original.select_get():
                    continue
                if object_instance.is_instance and not object_instance.object.parent.original.select_get():
                    continue
            
            evaluated_obj = object_instance.object
            object_type = evaluated_obj.type
            #print(object_type)
            #type: enum in [‘MESH’, ‘CURVE’, ‘SURFACE’, ‘META’, ‘FONT’, ‘ARMATURE’, ‘LATTICE’, ‘EMPTY’, ‘GPENCIL’, ‘CAMERA’, ‘LIGHT’, ‘SPEAKER’, ‘LIGHT_PROBE’], default ‘EMPTY’, (readonly)
            if evaluated_obj.hide_render:
                print ("Object: {} is hidden for render. Ignoring it.".format(evaluated_obj.name), 'INFO')
                continue#ignore it since we don't want it rendered (TODO: hide_viewport)
            
            if len(evaluated_obj.particle_systems)>0: #False:
                print("PARTICLE SYSTEMS ",len(evaluated_obj.particle_systems),"\n")
                
                for hair_ps in evaluated_obj.particle_systems:
                    if hair_ps.settings.type == 'HAIR' and hair_ps.settings.render_type == 'PATH':
                        matID = hair_ps.settings.material - 1 #zero based index
                        print("MATERIAL ID", matID)
                        self.export_mat(object_instance, matID, "disable displasement")
                        hairsRes ='AttributeBegin\n'
                        hairs = hair_ps.particles
                        print("RADIUS ",hair_ps.settings.root_radius)
                        hairsRes+=self.Export_hairs(object_instance, hairs, hair_ps.settings, matID)
                        hairsRes +='AttributeEnd\n'
                        GeometryLst.append(hairsRes)
                #print(hairsRes)
                
                #export objects itself
                
            if object_instance.is_instance:
                Transform = util.matrixtostr(object_instance.matrix_world.transposed())
                #print ("Object: {} Instance.".format(evaluated_obj.name), 'INFO')
                instance_data = self.add_instance(evaluated_obj.name, Transform)
                #print ("Data: {}".format(instance_data), 'INFO')
                #instStr+=instance_data
                chunk_data.append(instance_data)
                
                #GeometryLst.append(instance_data)
                #continue#ignore it since we don't want it rendered (TODO: hide_viewport)
            
            #print(evaluated_obj.data.name,"CHECK LINKED!",evaluated_obj.name)
            #if object_instance.parent and object_instance.parent.original == context.object:
                # Do whatever you want with 'ob_inst'
                #print("CHECK LINKED!")
            
            elif object_type in {'MESH', 'FONT', 'SURFACE', 'META', 'CURVE'}:
                if evaluated_obj.pbrtv4_isPortal:
                    print ("PORTAL OBJECT!!!!!!!!!!!!!!!!!!!!!!!")
                    portal = self.ExportPortal(object_instance)
                    self.portalsData.append(portal)
                else:
                    #check if object has linked mesh data:
                    #evaluated_obj.data.name //for linked data check
                    data_name = evaluated_obj.data.name
                    if linked_as_instance and data_name in self.linkedData:
                        #export as instance:
                        #print("Export Linked As Instance Object")
                        obj_data_id = self.linkedData.index(data_name)
                        obj_data_name = self.linkedName[obj_data_id]
                        Transform = util.matrixtostr(object_instance.matrix_world.transposed())
                        instance_data = self.add_instance(obj_data_name, Transform)
                        #instStr+=instance_data
                        chunk_data.append(instance_data)
                    else:
                        #add data to linked info
                        if linked_as_instance:
                            self.linkedData.append(data_name)
                            self.linkedName.append(evaluated_obj.name)
                        #print ("export object: "+evaluated_obj.name)
                        info = self.export_object(object_instance,geometryFolder)
                        
                        if info.notEmpty():
                            #info2 = copy.deepcopy(info)
                            #info2.parts = info.parts.copy()
                            #info2.materials = info.materials.copy()
                            #print ("Original: {}".format(info.to_DictStr('geometry/')), 'INFO')
                            #print ("Instance: {}".format(info2.to_InstanceDictStr('geometry/')), 'INFO')
                            infoLst[evaluated_obj.name] = info.to_InstanceDictStr('geometry/')
                            GeometryLst.append(info.to_DictStr('geometry/'))
            elif object_type == 'LIGHT':
                if evaluated_obj.data.type == 'SUN':
                    self.lightsData.append(export_distant_light(evaluated_obj))
                    print("SUN OBJECT", evaluated_obj.data.type)
                elif evaluated_obj.data.type == 'POINT':
                    self.lightsData.append(export_point_light(evaluated_obj))
                    print("POINT LIGHT OBJECT", evaluated_obj.data.type)
                elif evaluated_obj.data.type == 'SPOT':
                    self.lightsData.append(export_spot_light(evaluated_obj))
                    print("SPOT LIGHT OBJECT", evaluated_obj.data.type)
                else:
                    print("LIGHT OBJECT", evaluated_obj.data.type, "DOESN'T SUPPURTED")
            elif object_type == 'CAMERA':
                print ("export object: ", evaluated_obj.name, " skip camera")
            else:
                print ('! WARN !', "Object: %s of type '%s' is not supported!" % (evaluated_obj.name_full, object_type))
                
        instStr=''.join(chunk_data)
        for name in self.instancedData:
            #print (infoLst[name])
            GeometryLst.append(infoLst[name])
        GeometryLst.append(instStr)
        return GeometryLst