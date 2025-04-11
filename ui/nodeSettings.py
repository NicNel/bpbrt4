import bpy
import os
from bpy.types import NodeTree, Node, NodeSocket
from ..utils import util, presets

pbrt4_nodes = {
    "Shaders": [("pbrtv4None", "Interface", "No desc"),
                ("pbrtv4Measured", "Measured", "No desc"),
                ("pbrtv4DiffTrans", "DiffTrans", "No desc"),
                ("pbrtv4Subsurface", "Subsurface", "No desc"),
                ("pbrtv4Mix", "Mix", "No desc"),
                ("pbrtv4Diffuse", "Diffuse", "No desc"),
                ("pbrtv4Coateddiffuse", "CoatedDiffuse", "No desc"),
                ("pbrtv4Coatedconductor", "CoatedConductor", "No desc"),
                ("pbrtv4Dielectric", "Dielectric", "No desc"),
                ("pbrtv4Conductor", "Conductor", "No desc"),
                ("pbrtv4Hair", "Hair", "No desc"),
                ("pbrtv4Disney", "Disney", "No desc")],
    "Outputs": [("pbrtv4Output", "Output", "No desc")],
    "Textures":[("pbrtv4NodeConstant", "Constant", "No desc"),
                ("pbrtv4NodeMix", "Mix", "No desc"),
                ("pbrtv4NodeDMix", "DMix", "No desc"),
                ("pbrtv4NodeMarble", "Marble", "No desc"),
                ("pbrtv4NodeScale", "Scale", "No desc"),
                ("pbrtv4NodeCheckerboard", "Checkerboard", "No desc"),
                ("pbrtv4NodeImageTexture2d", "Image", "No desc")],
    "ShapeParameters": [("pbrtv4AreaEmitter", "AreaEmitter", "No desc"),
                        ("pbrtv4Displacement", "Displacement", "No desc")],
    "Mapping": [("PBRTV4Mapping2d", "Mapping2d", "No desc")],
    "Mediums": [("pbrtv4Uniformgrid", "Uniform", "No desc"),
                ("pbrtv4Homogeneous", "Homogeneous", "No desc"),
                ("pbrtv4CloudVolume", "Cloud", "No desc")]
}

class PBRTV4TreeNode(Node):
    bl_icon = 'MATERIAL'
    bl_idname = 'pbrtv4Node'
    
    isPbrtv4TreeNode = True
    
    def setId(self, name, id):
        #matName::nodeType::nodeTreeUniqueId
        #self.name ="{}::{}::{}".format(name, self.bl_idname, id)
        #old
        #self.pbrtv4NodeID ="{}::{}::{}".format(name, self.bl_idname, id)
        #change from debug id variable (label) to internal one
        self.pbrtv4NodeID ="{}::{}::{}".format(name, self.bl_idname, id)
    
    def getId(self):
        #tmp = self.pbrtv4NodeID.split("::")
        tmp = self.pbrtv4NodeID.split("::")
        id = tmp[-1]
        return int(id)
    
    def Backprop(self, List, Data, Tag = None):
        if self.pbrtv4NodeID not in List:
            List.append(self.pbrtv4NodeID)
            return self.to_string(List, Data)
        else:
            return self
            
    #List - already exported nodes Data - nodes data to write
    def BackpropOld(self, List, Data, Tag = None):
        if self.pbrtv4NodeID not in List:
            List.append(self.pbrtv4NodeID)
            return self.to_string(List, Data)
        else:
            return self
            
    def to_string(self, List, data):
        return self
    
    @classmethod
    def poll(cls, ntree):
        b = False
        # Make your node appear in different node trees by adding their bl_idname type here.
        if ntree.bl_idname == 'ShaderNodeTree': b = True
        return b
        
    #prev version
    def constructTName(self, matName, tName):
        return "{}::{}::{}".format(matName, "Texture", tName)
    def constructMName(self, matName, tName):
        return "{}::{}::{}".format(matName, "Material", tName)
    
#diffuse
#coateddiffuse
#coatedconductor
#diffusetransmission
#dielectric
#thindielectric
#hair
#conductor
#measured
#subsurface
#mix
#constant

def AddSpecTexture(input, par, list, data):
    if input is None:
        print("Node input error!")
        return ''
    if not(input.is_linked):
        c = input.default_value
        return '  "rgb {}" [ {} {} {} ]\n'.format(par, c[0], c[1], c[2])
    else:
        node_link = input.links[0]
        curNode =  node_link.from_node
        nd = curNode.Backprop(list, data)
        return '  "texture {}" [ "{}" ]\n'.format(par, nd.pbrtv4NodeID)

def AddFloatTexture(input, par, list, data):
    if input is None:
        print("Node input error!")
        return ''
    if not(input.is_linked):
        c = input.default_value
        return '  "float {}" [ {} ]\n'.format(par, c)
    else:
        node_link = input.links[0]
        curNode =  node_link.from_node
        nd = curNode.Backprop(list, data)
        return '  "texture {}" ["{}"]\n'.format(par, nd.pbrtv4NodeID)

def AddDispTexture(input, list, data):
    if input is None:
        print("Node input error!")
        return ''
    if (input.is_linked):
        node_link = input.links[0]
        curNode =  node_link.from_node
        nd = curNode.Backprop(list, data)
        return '  "texture displacement" [ "{}" ]\n'.format(nd.pbrtv4NodeID)
    return ''
    
def AddNormTexture(input):
    if input is None:
        print("Node input error!")
        return ''
    if (input.is_linked):
        node_link = input.links[0]
        curNode =  node_link.from_node
        nrm = curNode.getFileName()
        return '  "string normalmap" "{}"\n'.format(nrm)
    return ''
    
class pbrtv4NoneMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4None'
    bl_label = 'interface'
    bl_icon = 'MATERIAL'

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")

    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
    
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        
        res ='MakeNamedMaterial "{}"\n'.format(name)
        #res +='  "string type" [ "none" ]\n'
        res +='  "string type" [ "interface" ]\n'
        
        data.append(res)
        return self
        
class pbrtv4MixMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Mix'
    bl_label = 'mix'
    bl_icon = 'MATERIAL'

    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        MixAmount_node = self.inputs.new('NodeSocketFloat', "Mix amount")
        MixAmount_node.default_value = 0.5
        Mat1_node = self.inputs.new('NodeSocketShader', "Mat1")
        Mat2_node = self.inputs.new('NodeSocketShader', "Mat2")
        
    def draw_buttons(self, context, layout):
        pass
        
    def draw_label(self):
        return self.bl_label
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        amount = self.inputs[0]
        mat1 = self.inputs[1]
        mat2 = self.inputs[2]
        
        mat1FinalName=""
        mat2FinalName=""
        
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "mix" ]\n'
        
        res += AddFloatTexture(amount, "amount", list, data)
                    
        #mat1
        if not(mat1.is_linked):
            mat1FinalName = "default"
        else:
            node_link = mat1.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            mat1FinalName = nd.pbrtv4NodeID
        #mat2
        if not(mat2.is_linked):
            mat2FinalName = "default"
        else:
            node_link = mat2.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            mat2FinalName = nd.pbrtv4NodeID
            
        res+='  "string materials" [ "{}" "{}" ]\n'.format(mat1FinalName,mat2FinalName)    
        data.append(res)
        return self
        
class pbrtv4MeasuredMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Measured'
    bl_label = 'measured'
    bl_icon = 'MATERIAL'
    
    filename: bpy.props.StringProperty(name="filename",
                                             description="Texture file name",
                                             default="",
                                             subtype='FILE_PATH')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "Displacement Texture")
        DisplacementTexture_node.hide_value = True
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "filename",text = 'Texture file name')
        
    def draw_label(self):
        return self.bl_label
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        disp = self.inputs[0]
        
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='    "string type" [ "measured" ]\n'
        res +='    "string filename" [ "{}" ]\n'.format(util.switchpath(util.realpath(self.filename)))
        
        #export bump
        res += AddDispTexture(disp, list, data)
                    
        data.append(res)
        return self
        
class pbrtv4DiffuseMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Diffuse'
    bl_label = 'diffuse'
    bl_icon = 'MATERIAL'
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        ReflectanceTexture_node = self.inputs.new('NodeSocketColor', "Color Texture")
        ReflectanceTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]
        #ReflectanceTexture_node.hide_value = True
        
        SigmaTexture_node = self.inputs.new('NodeSocketFloat', "Sigma Texture")
        #SheenTexture_node = self.inputs.new('NodeSocketFloat', "Sheen")
        #SigmaTexture_node.hide_value = True
        
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "Displacement Texture")
        DisplacementTexture_node.hide_value = True
        
        NormalTexture_node = self.inputs.new('NodeSocketFloat', "Normal Texture")
        NormalTexture_node.hide_value = True
        
    def draw_label(self):
        return self.bl_label
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        
        color = self.inputs[0]
        sigma = self.inputs[1]
        disp = self.inputs[2]
        norm = self.inputs[3]
        
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "diffuse" ]\n'
        
        res += AddSpecTexture(color, "reflectance", list, data)
        
        #export bump
        res += AddDispTexture(disp, list, data)
        
        #export norm
        res += AddNormTexture(norm)
        
        data.append(res)
        return self

class pbrtv4HairMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Hair'
    bl_label = 'hair'
    bl_icon = 'MATERIAL'
    
    def updateType(self,context):
        reflectance = self.inputs.get("reflectance")
        sigma_a = self.inputs.get("sigma_a")
        eumelanin = self.inputs.get("eumelanin")
        pheomelanin = self.inputs.get("pheomelanin")
        if self.ParType == "sigma":
            sigma_a.hide = False
            reflectance.hide = True
            eumelanin.hide = True
            pheomelanin.hide = True
        elif self.ParType == "reflectance":
            sigma_a.hide = True
            reflectance.hide = False
            eumelanin.hide = True
            pheomelanin.hide = True
        elif self.ParType == "pigments":
            sigma_a.hide = True
            reflectance.hide = True
            eumelanin.hide = False
            pheomelanin.hide = False
        else:
            sigma_a.hide = True
            reflectance.hide = True
            eumelanin.hide = True
            pheomelanin.hide = True
    
    ParType: bpy.props.EnumProperty(name="ParType",
                                              description="",
                                              items=[("default", "default", "default"),
                                                     ("sigma", "sigma", "sigma"),
                                                     ("reflectance", "reflectance", "reflectance"),
                                                     ("pigments", "pigments", "pigments")],
                                              default='default', update = updateType)
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        reflectance = self.inputs.new('NodeSocketColor', "reflectance")
        reflectance.default_value = [0.5, 0.5, 0.5, 1.0]
        reflectance.hide = True
        
        sigma_a = self.inputs.new('NodeSocketColor', "sigma_a")
        sigma_a.default_value = [0.5, 0.5, 0.5, 1.0]
        sigma_a.hide = True
        
        eumelanin = self.inputs.new('NodeSocketFloat', "eumelanin")
        eumelanin.hide = True
        pheomelanin = self.inputs.new('NodeSocketFloat', "pheomelanin")
        pheomelanin.hide = True
        
        eta = self.inputs.new('NodeSocketFloat', "eta")
        eta.default_value = 1.55
        beta_m = self.inputs.new('NodeSocketFloat', "beta_m")
        beta_m.default_value = 0.3
        beta_n = self.inputs.new('NodeSocketFloat', "beta_n")
        beta_n.default_value = 0.3
        alpha = self.inputs.new('NodeSocketFloat', "alpha")
        alpha.default_value = 2.0
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "ParType", text = 'type')
        
    def draw_label(self):
        return self.bl_label
    
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        
        eta =  self.inputs.get("eta")
        beta_m =  self.inputs.get("beta_m")
        beta_n =  self.inputs.get("beta_n")
        alpha =  self.inputs.get("alpha")
        reflectance = self.inputs.get("reflectance")
        sigma_a = self.inputs.get("sigma_a")
        eumelanin = self.inputs.get("eumelanin")
        pheomelanin = self.inputs.get("pheomelanin")
        
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "hair" ]\n'
        
        if self.ParType == "sigma":
            res += AddSpecTexture(sigma_a, "sigma_a", list, data)
        elif self.ParType == "reflectance":
            res += AddSpecTexture(reflectance, "reflectance", list, data)
        elif self.ParType == "pigments":
            res += AddFloatTexture(eumelanin, "eumelanin", list, data)
            res += AddFloatTexture(pheomelanin, "pheomelanin", list, data)
        
        res += AddFloatTexture(eta, "eta", list, data)
        res += AddFloatTexture(beta_m, "beta_m", list, data)
        res += AddFloatTexture(beta_n, "beta_n", list, data)
        res += AddFloatTexture(alpha, "alpha", list, data)
        
        data.append(res)
        return self

#diffusetransmission
class pbrtv4DiffTransMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4DiffTrans'
    bl_label = 'transmission'
    bl_icon = 'MATERIAL'

    Scale : bpy.props.FloatProperty(default=1.0, min=0.0, max=10000000.0)
    #Reflectance : bpy.props.FloatVectorProperty(name="reflectance", description="color",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        ReflectanceTexture_node = self.inputs.new('NodeSocketColor', "Color Texture")
        ReflectanceTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
        TransmittanceTexture_node = self.inputs.new('NodeSocketColor', "Transmittance Texture")
        TransmittanceTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
        SigmaTexture_node = self.inputs.new('NodeSocketFloat', "Sigma Texture")
        #SigmaTexture_node.hide_value = True
        
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "Displacement Texture")
        DisplacementTexture_node.hide_value = True
        
    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "Scale", text = 'Scale')
        #layout.prop(self, "Sigma",text = 'Sigma')
        
    def draw_label(self):
        return self.bl_label
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        color = self.inputs[0]
        transmittance = self.inputs[1]
        sigma = self.inputs[2]
        disp = self.inputs[3]
        
        name = self.pbrtv4NodeID
        
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "diffusetransmission" ]\n'
        
        #reflectance
        res += AddSpecTexture(color, "reflectance", list, data)
        #transmittance
        res += AddSpecTexture(transmittance, "transmittance", list, data)
        
        #export bump
        res += AddDispTexture(disp, list, data)
                    
        res+='  "float scale" [{}]'.format(self.Scale)
        data.append(res)
        return self

class pbrtv4SubsurfaceMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Subsurface'
    bl_label = 'subsurface'
    bl_icon = 'MATERIAL'

    RemapRoughness: bpy.props.BoolProperty(default=False)
    SeparateRoughness: bpy.props.BoolProperty(default=False)
    Eta : bpy.props.FloatProperty(default=1.5, min=1.0, max=999.0)
    Scale : bpy.props.FloatProperty(default=1.0, min=0.0, max=100000.0)
    Mfp : bpy.props.FloatVectorProperty(name="mfp", description="mfp color", precision=10, default=(1.0, 1.0, 1.0, 1.0), min=0, max=1, subtype='COLOR', size=4)
    
    def updatePreset(self,context):
        SigmaS = self.inputs[0]
        SigmaA = self.inputs[1]
        Reflectance = self.inputs[2]
        if self.NamePreset == "Reflectance":
            SigmaS.hide = True
            SigmaA.hide = True
            Reflectance.hide = False
        elif self.NamePreset == "Custom":
            SigmaS.hide = False
            SigmaA.hide = False
            Reflectance.hide = True
        else:
            SigmaS.hide = True
            SigmaA.hide = True
            Reflectance.hide = True
        #print("preset changed")
        
    NamePreset: bpy.props.EnumProperty(name="NamePreset",
                                              description="",
                                              items=presets.MediumPreset + 
                                              [("Reflectance", "Reflectance", "Reflectance"),
                                                ("Custom", "Custom", "Custom")],
                                              default='Reflectance', update=updatePreset)
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        SigmaS_node = self.inputs.new('NodeSocketColor', "Sigma S")
        SigmaS_node.default_value = [0.8, 0.8, 0.8, 1.0]
        SigmaS_node.hide = True
        
        SigmaA_node = self.inputs.new('NodeSocketColor', "Sigma A")
        SigmaA_node.default_value = [0.8, 0.8, 0.8, 1.0]
        SigmaA_node.hide = True
        
        ReflectanceTexture_node = self.inputs.new('NodeSocketColor', "Color Texture")
        ReflectanceTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]
        #ReflectanceTexture_node.hide_value = True
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "Roughness Texture")
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "Displacement Texture")
        DisplacementTexture_node.hide_value = True
        gTexture_node = self.inputs.new('NodeSocketFloat', "G")
        AlbedoTexture_node = self.inputs.new('NodeSocketColor', "Albedo Texture")
        AlbedoTexture_node.default_value = [0.0, 0.0, 0.0, 1.0]
        
    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        #layout.prop(self, "Reflectance",text = 'Color')
        #layout.prop(self, "uRoughness",text = 'uRoughness')
        #layout.prop(self, "vRoughness",text = 'vRoughness')
        layout.prop(self, "NamePreset", text = 'Preset name')
        layout.prop(self, "RemapRoughness",text = 'RemapRoughness')
        layout.prop(self, "Eta",text = 'IOR')
        layout.prop(self, "Scale", text = 'Scale')
        layout.prop(self, "Mfp", text = 'Mfp')
        
    def draw_label(self):
        return self.bl_label
        
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        sigma_s = self.inputs[0]
        sigma_a = self.inputs[1]
        reflectance = self.inputs[2]
        roughness = self.inputs[3]
        disp = self.inputs[4]
        
        name = self.pbrtv4NodeID
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "subsurface" ]\n'
        
        if self.NamePreset == "Reflectance":
            #export reflectance
            res += AddSpecTexture(reflectance, "reflectance", list, data)
            res+='  "rgb mfp" [ {} {} {} ]\n'.format(self.Mfp[0], self.Mfp[1], self.Mfp[2])
        elif self.NamePreset == "Custom":
            #export sigma_s
            res += AddSpecTexture(sigma_s, "sigma_s", list, data)
            #export sigma_a
            res += AddSpecTexture(sigma_a, "sigma_a", list, data)
        else:
            res+='  '+'"string name" [ "{}" ]\n'.format(self.NamePreset)

        #export roughness
        res += AddFloatTexture(roughness, "roughness", list, data)
                
        #export bump
        res += AddDispTexture(disp, list, data)
                    
        res+='  "float eta" [{}]\n'.format(self.Eta)
        remap='false'
        if self.RemapRoughness:
            remap='true'
        res+='  "bool remaproughness" {}\n'.format(remap)
        res+='  "float scale" [{}]'.format(self.Scale)
        data.append(res)
        return self

class pbrtv4CoateddiffuseMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Coateddiffuse'
    bl_label = 'coateddiffuse'
    bl_icon = 'MATERIAL'
    
    def updateAnisotropy(self,context):
        roughness = self.inputs.get("roughness")
        uroughness = self.inputs.get("uroughness")
        vroughness = self.inputs.get("vroughness")
        if self.Anisotropy:
            roughness.hide = True
            uroughness.hide = False
            vroughness.hide = False
        else:
            roughness.hide = False
            uroughness.hide = True
            vroughness.hide = True

    def updateViewportColor(self,context):
        mat = bpy.context.active_object.active_material
        if mat is not None:
            bpy.data.materials[mat.name].diffuse_color=self.Kd
        
    #uRoughness : bpy.props.FloatProperty(default=0.05, min=0.00001, max=1.0)
    #vRoughness : bpy.props.FloatProperty(default=0.05, min=0.00001, max=1.0)
    maxdepth : bpy.props.IntProperty(default=10, min=0, max=100)
    nsamples : bpy.props.IntProperty(default=1, min=1, max=100)
    
    Thickness : bpy.props.FloatProperty(default=0.01, min=0.0000, max=1000.0)
    RemapRoughness: bpy.props.BoolProperty(default=False)
    SeparateRoughness: bpy.props.BoolProperty(default=False)
    
    TwoSided: bpy.props.BoolProperty(default=True)
    #Reflectance : bpy.props.FloatVectorProperty(name="reflectance", description="color",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    Eta : bpy.props.FloatProperty(default=1.5, min=1.0, max=999.0)
    Anisotropy: bpy.props.BoolProperty(default=False, update=updateAnisotropy)
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        ReflectanceTexture_node = self.inputs.new('NodeSocketColor', "color")
        ReflectanceTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]
        #ReflectanceTexture_node.hide_value = True
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "roughness")
        RoughnessTexture_node.default_value = 0.05
        
        URoughnessTexture_node = self.inputs.new('NodeSocketFloat', "uroughness")
        URoughnessTexture_node.default_value = 0.05
        URoughnessTexture_node.hide = True
        
        VRoughnessTexture_node = self.inputs.new('NodeSocketFloat', "vroughness")
        VRoughnessTexture_node.default_value = 0.05
        VRoughnessTexture_node.hide = True
        
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "displacement")
        DisplacementTexture_node.hide_value = True
        
        NormalTexture_node = self.inputs.new('NodeSocketFloat', "normal")
        NormalTexture_node.hide_value = True
        
        gTexture_node = self.inputs.new('NodeSocketFloat', "G")

        AlbedoTexture_node = self.inputs.new('NodeSocketColor', "albedo")
        AlbedoTexture_node.default_value = [0.0, 0.0, 0.0, 1.0]
        
    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        #layout.prop(self, "Reflectance",text = 'Color')
        #layout.prop(self, "uRoughness",text = 'uRoughness')
        #layout.prop(self, "vRoughness",text = 'vRoughness')
        layout.prop(self, "RemapRoughness",text = 'RemapRoughness')
        layout.prop(self, "Anisotropy",text = 'Anisotropy')
        layout.prop(self, "Thickness",text = 'thickness')
        layout.prop(self, "Eta",text = 'IOR')
        
        layout.prop(self, "TwoSided",text = 'two sided')
        layout.prop(self, "maxdepth",text = 'maxdepth')
        layout.prop(self, "nsamples",text = 'nsamples')
        
    def draw_label(self):
        return self.bl_label
        
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        color = self.inputs.get("color")
        roughness = self.inputs.get("roughness")
        uroughness = self.inputs.get("uroughness")
        vroughness = self.inputs.get("vroughness")
        disp = self.inputs.get("displacement")
        norm = self.inputs.get("normal")
        g = self.inputs.get("G")
        albedo = self.inputs.get("albedo")
        
        name = self.pbrtv4NodeID
        
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "coateddiffuse" ]\n'
        #export color
        res += AddSpecTexture(color, "reflectance", list, data)
        
        #export albedo
        res += AddSpecTexture(albedo, "albedo", list, data)
        
        #export g
        res += AddFloatTexture(g, "g", list, data)
            
        #export roughness
        if self.Anisotropy:
            if uroughness is not None:
                res += AddFloatTexture(uroughness, "uroughness", list, data)
            if vroughness is not None:
                res += AddFloatTexture(vroughness, "vroughness", list, data)
        else:
            res += AddFloatTexture(roughness, "roughness", list, data)
            
        #export bump
        res += AddDispTexture(disp, list, data)
        
        #export norm
        res += AddNormTexture(norm)
            
        res+='  "float eta" [{}]\n'.format(self.Eta)
        res+='  "float thickness" [{}]\n'.format(self.Thickness)
        #two sided
        #twosided='false'
        #if self.TwoSided:
        #    twosided='true'
        #res+='  "bool twosided" {}\n'.format(twosided)
        remap='false'
        if self.RemapRoughness:
            remap='true'
        res+='  "bool remaproughness" {}\n'.format(remap)
        
        res+='  "integer maxdepth" [{}]\n'.format(self.maxdepth)
        res+='  "integer nsamples" [{}]\n'.format(self.nsamples)
        data.append(res)
        return self
        
class pbrtv4PlasticMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Plastic'
    bl_label = 'plastic'
    bl_icon = 'MATERIAL'

    Eta : bpy.props.FloatProperty(default=1.5, min=1.0, max=999.0)
    Eta_Spectrum : bpy.props.FloatVectorProperty(name="Tint", description="tint color",default=(200.0, 1.0, 900.0, 1.0), min=0, max=1000, subtype='COLOR', size=4)
    RemapRoughness: bpy.props.BoolProperty(default=False)
    
    EtaPreset: bpy.props.EnumProperty(name="EtaPreset",
                                              description="",
                                              items=presets.GlassPreset+[("custom", "Value", "Custom"),
                                                                         ("color", "color", "Custom")],
                                              default='custom')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        ReflectanceTexture_node = self.inputs.new('NodeSocketColor', "Color Texture")
        ReflectanceTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "Roughness Texture")
        RoughnessTexture_node.default_value = 0.001
        
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "Displacement Texture")
        DisplacementTexture_node.hide_value = True
        
    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "EtaPreset",text = 'Eta preset')
        if self.EtaPreset == 'custom':
            layout.prop(self, "Eta",text = 'Eta')
        elif self.EtaPreset == 'color':
            layout.prop(self, "Eta_Spectrum",text = 'Eta_Spectrum')
        
        layout.prop(self, "RemapRoughness",text = 'RemapRoughness')
        
    def draw_label(self):
        return self.bl_label
        
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        color = self.inputs[0]
        roughness = self.inputs[1]
        disp = self.inputs[2]
        
        name = self.pbrtv4NodeID
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "plastic" ]\n'
        
        if not(color.is_linked):
            c = color.default_value
            res+='  "rgb reflectance" [ {} {} {} ]\n'.format(c[0], c[1], c[2])
        else:
            node_link = color.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            res+='  "texture reflectance" ["{}"]\n'.format(nd.pbrtv4NodeID)
        
        #export roughness
        if not(roughness.is_linked):
            c = roughness.default_value
            res+='  "float roughness" [ {} ]\n'.format(c)
        else:
            node_link = roughness.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            res+='  "texture roughness" ["{}"]\n'.format(nd.pbrtv4NodeID)
        
        #export bump
        if (disp.is_linked):
            node_link = disp.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            res+='  "texture displacement" ["{}"]\n'.format(nd.pbrtv4NodeID)
        remap='false'
        if self.RemapRoughness:
            remap='true'
        res+='  "bool remaproughness" {}\n'.format(remap)
        
        #eta
        if self.EtaPreset == 'color':
            res+='  "spectrum eta" [ {} {} {} {} ]\n'.format(self.Eta_Spectrum[0], self.Eta_Spectrum[1], self.Eta_Spectrum[2], self.Eta_Spectrum[3])
            #res+='  "rgb eta" [ {} {} {} ]\n'.format(self.Eta_Spectrum[0], self.Eta_Spectrum[1], self.Eta_Spectrum[2])
        elif self.EtaPreset != 'custom':
            res+='  "spectrum eta" [ "{}" ]\n'.format(self.EtaPreset)
        else:
            res+='  "float eta" [{}]\n'.format(self.Eta)
            
        data.append(res)
        return self
        
class pbrtv4DielectricMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Dielectric'
    bl_label = 'dielectric'
    bl_icon = 'MATERIAL'

    Eta : bpy.props.FloatProperty(default=1.5, min=1.0, max=999.0)
    Eta_Spectrum : bpy.props.FloatVectorProperty(name="Tint", description="tint color",default=(200.0, 1.0, 900.0, 1.0), min=0, max=1000, subtype='COLOR', size=4)
    RemapRoughness: bpy.props.BoolProperty(default=False)
    isThin:bpy.props.BoolProperty(default=False)
    UseTint: bpy.props.BoolProperty(default=False)
    Tint : bpy.props.FloatVectorProperty(name="Tint", description="tint color",default=(1.0, 1.0, 1.0, 1.0), min=0, max=1, subtype='COLOR', size=4)
    EtaPreset: bpy.props.EnumProperty(name="EtaPreset",
                                              description="",
                                              items=presets.GlassPreset+[("custom", "Value", "Custom"),
                                                                         ("color", "color", "Custom")],
                                              default='custom')
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "Roughness Texture")
        RoughnessTexture_node.default_value = 0.001
        
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "Displacement Texture")
        DisplacementTexture_node.hide_value = True
        
        #EtaTexture_node = self.inputs.new('NodeSocketColor', "Eta spectr")
        #EtaTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]

    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "isThin",text = 'Thin dielectric')
        layout.prop(self, "EtaPreset",text = 'Eta preset')
        if self.EtaPreset == 'custom':
            layout.prop(self, "Eta",text = 'Eta')
        elif self.EtaPreset == 'color':
            layout.prop(self, "Eta_Spectrum",text = 'Eta_Spectrum')
        
        if not self.isThin:
            layout.prop(self, "RemapRoughness",text = 'RemapRoughness')
            layout.prop(self, "UseTint",text = 'Use tint')
            if self.UseTint:
                layout.prop(self, "Tint",text = 'tint color')
        
        
    def draw_label(self):
        return self.bl_label
        
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        roughness = self.inputs[0]
        disp = self.inputs[1]
        
        name = self.pbrtv4NodeID
        res ='MakeNamedMaterial "{}"\n'.format(name)
        if self.isThin:
            res +='  "string type" [ "thindielectric" ]\n'
        else:    
            res +='  "string type" [ "dielectric" ]\n'
        
        #export roughness
        if not self.isThin:
            res += AddFloatTexture(roughness, "roughness", list, data)
            #export bump
            res += AddDispTexture(disp, list, data)
            remap='false'
            if self.RemapRoughness:
                remap='true'
            res+='  "bool remaproughness" {}\n'.format(remap)
            
            if self.UseTint:
                res+='  "rgb tint" [{} {} {}]\n'.format(self.Tint[0],self.Tint[1],self.Tint[2])
        #eta
        if self.EtaPreset == 'color':
            res+='  "spectrum eta" [ {} {} {} {} ]\n'.format(self.Eta_Spectrum[0], self.Eta_Spectrum[1], self.Eta_Spectrum[2], self.Eta_Spectrum[3])
            #res+='  "rgb eta" [ {} {} {} ]\n'.format(self.Eta_Spectrum[0], self.Eta_Spectrum[1], self.Eta_Spectrum[2])
        elif self.EtaPreset != 'custom':
            res+='  "spectrum eta" [ "{}" ]\n'.format(self.EtaPreset)
        else:
            res+='  "float eta" [{}]\n'.format(self.Eta)
            
        data.append(res)
        return self
        
class pbrtv4CoatedconductorMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Coatedconductor'
    bl_label = 'coatedconductor'
    bl_icon = 'MATERIAL'
    
    def updateAnisotropy(self,context):
        roughness = self.inputs.get("roughness")
        uroughness = self.inputs.get("uroughness")
        vroughness = self.inputs.get("vroughness")
        if self.Anisotropy:
            roughness.hide = True
            uroughness.hide = False
            vroughness.hide = False
        else:
            roughness.hide = False
            uroughness.hide = True
            vroughness.hide = True
            
    def updateEta(self, context):
        color = self.inputs.get("color")
        if self.EtaPreset == 'color':
            color.hide = False
        else:
            color.hide = True

    def updateViewportColor(self,context):
        mat = bpy.context.active_object.active_material
        if mat is not None:
            bpy.data.materials[mat.name].diffuse_color=self.Kd
        
    #uRoughness : bpy.props.FloatProperty(default=0.05, min=0.00001, max=1.0)
    #vRoughness : bpy.props.FloatProperty(default=0.05, min=0.00001, max=1.0)
    maxdepth : bpy.props.IntProperty(default=10, min=0, max=100)
    nsamples : bpy.props.IntProperty(default=1, min=1, max=100)
    
    Thickness : bpy.props.FloatProperty(default=0.01, min=0.0000, max=1000.0)
    RemapRoughness: bpy.props.BoolProperty(default=False)
    SeparateRoughness: bpy.props.BoolProperty(default=False)
    
    TwoSided: bpy.props.BoolProperty(default=True)
    #Reflectance : bpy.props.FloatVectorProperty(name="reflectance", description="color",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    Eta : bpy.props.FloatProperty(default=1.5, min=1.0, max=999.0)
    Anisotropy: bpy.props.BoolProperty(default=False, update=updateAnisotropy)
    
    EtaPreset: bpy.props.EnumProperty(name="EtaPreset",
                                              description="",
                                              items=presets.MetalEta + 
                                              [("color", "color", "Use color")],
                                              default='metal-Al-eta', update=updateEta)
    kPreset: bpy.props.EnumProperty(name="kPreset",
                                              description="",
                                              items=presets.MetalK,
                                              default='metal-Al-k')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        
        ReflectanceTexture_node = self.inputs.new('NodeSocketColor', "color")
        ReflectanceTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]
        ReflectanceTexture_node.hide = True
        #ReflectanceTexture_node.hide_value = True
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "roughness")
        RoughnessTexture_node.default_value = 0.05
        
        URoughnessTexture_node = self.inputs.new('NodeSocketFloat', "uroughness")
        URoughnessTexture_node.default_value = 0.05
        URoughnessTexture_node.hide = True
        
        VRoughnessTexture_node = self.inputs.new('NodeSocketFloat', "vroughness")
        VRoughnessTexture_node.default_value = 0.05
        VRoughnessTexture_node.hide = True
        
        IRoughnessTexture_node = self.inputs.new('NodeSocketFloat', "interface.roughness")
        IRoughnessTexture_node.default_value = 0.05
        
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "displacement")
        DisplacementTexture_node.hide_value = True
        
        NormalTexture_node = self.inputs.new('NodeSocketFloat', "normal")
        NormalTexture_node.hide_value = True
        
        gTexture_node = self.inputs.new('NodeSocketFloat', "G")

        AlbedoTexture_node = self.inputs.new('NodeSocketColor', "albedo")
        AlbedoTexture_node.default_value = [0.0, 0.0, 0.0, 1.0]
        
    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        #layout.prop(self, "Reflectance",text = 'Color')
        #layout.prop(self, "uRoughness",text = 'uRoughness')
        #layout.prop(self, "vRoughness",text = 'vRoughness')
        layout.prop(self, "RemapRoughness",text = 'RemapRoughness')
        layout.prop(self, "Anisotropy",text = 'Anisotropy')
        layout.prop(self, "Thickness",text = 'thickness')
        layout.prop(self, "Eta",text = 'IOR')
        
        layout.prop(self, "TwoSided",text = 'two sided')
        layout.prop(self, "maxdepth",text = 'maxdepth')
        layout.prop(self, "nsamples",text = 'nsamples')
        
        layout.prop(self, "EtaPreset",text = 'EtaPreset')
        layout.prop(self, "kPreset",text = 'kPreset')
        
        
    def draw_label(self):
        return self.bl_label
        
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        color = self.inputs.get("color")
        roughness = self.inputs.get("roughness")
        uroughness = self.inputs.get("uroughness")
        vroughness = self.inputs.get("vroughness")
        disp = self.inputs.get("displacement")
        norm = self.inputs.get("normal")
        irough = self.inputs.get("interface.roughness")
        g = self.inputs.get("G")
        albedo = self.inputs.get("albedo")
        
        name = self.pbrtv4NodeID
        
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "coatedconductor" ]\n'
        #export color
        if self.EtaPreset == 'color':
            res += AddSpecTexture(color, "reflectance", list, data)
        #export albedo
        res += AddSpecTexture(albedo, "albedo", list, data)
        #export g
        res += AddFloatTexture(g, "g", list, data)
            
        #export roughness
        if self.Anisotropy:
            if uroughness is not None:
                res += AddFloatTexture(uroughness, "conductor.uroughness", list, data)
            if vroughness is not None:
                res += AddFloatTexture(vroughness, "conductor.vroughness", list, data)
        else:
            res += AddFloatTexture(roughness, "conductor.roughness", list, data)
        
        #export interface roughness
        res += AddFloatTexture(irough, "interface.roughness", list, data)
        
        #export bump
        res += AddDispTexture(disp, list, data)
        
        #export norm
        res += AddNormTexture(norm)
            
        res+='  "float interface.eta" [{}]\n'.format(self.Eta)
        res+='  "float thickness" [{}]\n'.format(self.Thickness)
        
        if not self.EtaPreset == 'color':    
            res+='  "spectrum conductor.eta" [ "{}" ]\n'.format(self.EtaPreset)
            res+='  "spectrum conductor.k" [ "{}" ]\n'.format(self.kPreset)
        #two sided
        #twosided='false'
        #if self.TwoSided:
        #    twosided='true'
        #res+='  "bool twosided" {}\n'.format(twosided)
        remap='false'
        if self.RemapRoughness:
            remap='true'
        res+='  "bool remaproughness" {}\n'.format(remap)
        
        res+='  "integer maxdepth" [{}]\n'.format(self.maxdepth)
        res+='  "integer nsamples" [{}]\n'.format(self.nsamples)
        data.append(res)
        return self

#"string type" [ "conductor" ]
#"spectrum eta" [ "metal-Al-eta" ]
#"spectrum k" [ "metal-Al-k" ]
#"float roughness" [ 0.005 ]
    
class pbrtv4ConductorMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Conductor'
    bl_label = 'conductor'
    bl_icon = 'MATERIAL'
    
    def updateAnisotropy(self,context):
        roughness = self.inputs.get("roughness")
        uroughness = self.inputs.get("uroughness")
        vroughness = self.inputs.get("vroughness")
        if self.Anisotropy:
            roughness.hide = True
            uroughness.hide = False
            vroughness.hide = False
        else:
            roughness.hide = False
            uroughness.hide = True
            vroughness.hide = True

    EtaPreset: bpy.props.EnumProperty(name="EtaPreset",
                                              description="",
                                              items=presets.MetalEta + 
                                              [("color", "color", "Use color")],
                                              default='metal-Al-eta')
    kPreset: bpy.props.EnumProperty(name="kPreset",
                                              description="",
                                              items=presets.MetalK,
                                              default='metal-Al-k')
    Eta : bpy.props.FloatProperty(default=1.5, min=1.0, max=999.0)
    RemapRoughness: bpy.props.BoolProperty(default=False)
    Anisotropy: bpy.props.BoolProperty(default=False, update=updateAnisotropy)
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        ReflectanceTexture_node = self.inputs.new('NodeSocketColor', "color")
        ReflectanceTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "roughness")
        RoughnessTexture_node.default_value = 0.05
        
        URoughnessTexture_node = self.inputs.new('NodeSocketFloat', "uroughness")
        URoughnessTexture_node.default_value = 0.05
        URoughnessTexture_node.hide = True
        
        VRoughnessTexture_node = self.inputs.new('NodeSocketFloat', "vroughness")
        VRoughnessTexture_node.default_value = 0.05
        VRoughnessTexture_node.hide = True
        
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "displacement")
        DisplacementTexture_node.hide_value = True
             
    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "EtaPreset",text = 'EtaPreset')
        layout.prop(self, "kPreset",text = 'kPreset')
        layout.prop(self, "RemapRoughness",text = 'RemapRoughness')
        layout.prop(self, "Anisotropy",text = 'Anisotropy')
        #layout.prop(self, "Eta",text = 'IOR')
        
    def draw_label(self):
        return self.bl_label
        
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        color = self.inputs.get("color")
        roughness = self.inputs.get("roughness")
        uroughness = self.inputs.get("uroughness")
        vroughness = self.inputs.get("vroughness")
        disp = self.inputs.get("displacement")
        
        name = self.pbrtv4NodeID
        
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "conductor" ]\n'
        #export color
        if self.EtaPreset == 'color':
            res += AddSpecTexture(color, "reflectance", list, data)
            
        #export roughness
        if self.Anisotropy:
            if uroughness is not None:
                res += AddFloatTexture(uroughness, "uroughness", list, data)
            if vroughness is not None:
                res += AddFloatTexture(vroughness, "vroughness", list, data)
        else:
            res += AddFloatTexture(roughness, "roughness", list, data)
            
        #export bump
        res += AddDispTexture(disp, list, data)
        
        if not self.EtaPreset == 'color':    
            res+='  "spectrum eta" [ "{}" ]\n'.format(self.EtaPreset)
            res+='  "spectrum k" [ "{}" ]\n'.format(self.kPreset)
        remap='false'
        if self.RemapRoughness:
            remap='true'
        res+='  "bool remaproughness" {}\n'.format(remap)       
        data.append(res)
        return self

class pbrtv4NodeImageTexture2d(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4NodeImageTexture2d'
    bl_label = 'Image'
    bl_icon = 'TEXTURE'
    
    def update_image(self, context):
        pass
    def update_type(self, context):
        #util.ShowMessageBox("This is a message", "This is a custom title", 'ERROR')
        if self.TextureType == "spectrum":
            self.outputs[0].type = "RGBA"
        else:
            self.outputs[0].type = "VALUE"
    
    image: bpy.props.PointerProperty(name="Image", type=bpy.types.Image, update=update_image)
    TextureType: bpy.props.EnumProperty(name="TextureType",
                                          description="Texture type",
                                          items=[('spectrum', "spectrum", "spectrum texture"),
                                                 ('float', "float", "float texture")],
                                          default='spectrum', update=update_type)
                                          
    ScaleValue : bpy.props.FloatProperty(default=1.0)
    show_thumbnail: bpy.props.BoolProperty(name="", default=True, description="Show thumbnail")
    
    #Convert: bpy.props.BoolProperty(name="Convert", default=False, description="Convert to sRGB")
    GammaValue : bpy.props.FloatProperty(default=1.0)
    
    Invert: bpy.props.BoolProperty(name="", default=False, description="Invert")
    EncodingType: bpy.props.EnumProperty(name="EncodingType",
                                          description="Texture encoding",
                                          items=[('sRGB', "sRGB", "sRGB texture"),
                                                 ('linear', "linear", "linear texture"),
                                                 ('gamma', "gamma", "gamma")
                                                 ],
                                          default='sRGB', update=update_type)
                                          
    WrapType: bpy.props.EnumProperty(name="WrapType",
                                          description="Wrap",
                                          items=[('repeat', "repeat", "repeat"),
                                                 ('black', "black", "black"),
                                                 ('clamp', "clamp", "clamp")
                                                 ],
                                          default='repeat')
                                          
    FilterType: bpy.props.EnumProperty(name="FilterType",
                                          description="Texture filter type",
                                          items=[('ewa', "ewa", "ewa filter"),
                                                 ('trilinear', "trilinear", "trilinear filter"),
                                                 ('bilinear', "bilinear", "bilinear filter"),
                                                 ('point', "point", "point filter"),
                                                 ('none', "none", "none filter")],
                                          default='bilinear', update=update_type)

    def init(self, context):
        self.outputs.new('NodeSocketColor', "Pbrt Matte")
        Mapping_node = self.inputs.new('NodeSocketVector', "Mapping")
        Mapping_node.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "show_thumbnail", text = 'Show preview')
        
        if self.show_thumbnail:
            layout.template_ID_preview(self, "image", open="image.open")
        else:
            layout.template_ID(self, "image", open="image.open")
        layout.prop(self, "TextureType",text = 'Texture type')
        layout.prop(self, "ScaleValue",text = 'Scale')
        layout.prop(self, "Invert",text = 'Invert')
        layout.prop(self, "WrapType", text = 'Wrap')
        layout.prop(self, "EncodingType", text = 'Encoding type')
        if self.EncodingType=="gamma":
            layout.prop(self, "GammaValue", text = 'gamma')
        layout.prop(self, "FilterType", text = 'Filter type')
        
    def draw_label(self):
        return self.bl_label
    
    def getFileName(self):
        return util.switchpath(util.realpath(self.image.filepath))
    
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        
        res = 'Texture "{}" "{}" "imagemap"\n'.format(name, self.TextureType)
        res +='  "string filename" [ "{}" ]\n'.format(util.switchpath(util.realpath(self.image.filepath)))
        res +='  "float scale" [ {} ]\n'.format(self.ScaleValue)
        res +='  "string wrap" [ "{}" ]\n'.format(self.WrapType)
        
        uv = self.inputs[0]
        if not(uv.is_linked):
            #add default mapping
            res +='  "string mapping" [ "{}" ]\n'.format("uv")
            res +='  "float uscale" [ {} ]\n'.format("1")
            res +='  "float vscale" [ {} ]\n'.format("1")
            res +='  "float udelta" [ {} ]\n'.format("0")
            res +='  "float vdelta" [ {} ]\n'.format("0")
        else:
            node_link = uv.links[0]
            curNode =  node_link.from_node
            res+=curNode.to_string(list, data)
            
        res+='  "bool invert" {}\n'.format("true" if self.Invert else "false")
        res+='  "string filter" "{}"\n'.format(self.FilterType)
        
        if self.EncodingType == "gamma":
            res+='  "string encoding" "gamma {}"\n'.format(self.GammaValue)
        else:
            res+='  "string encoding" "{}"\n'.format(self.EncodingType)
                
        data.append(res)
        return self
        
class pbrtv4NodeCheckerboard(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4NodeCheckerboard'
    bl_label = 'Checkerboard'
    bl_icon = 'TEXTURE'
    def update_type(self, context):
        if self.TextureType == "spectrum":
            self.outputs[0].type = "RGBA"
            self.inputs[0].type = "RGBA"
            self.inputs[1].type = "RGBA"
        else:
            self.outputs[0].type = "VALUE"
            self.inputs[0].type = "VALUE"
            self.inputs[1].type = "VALUE"
    TextureType: bpy.props.EnumProperty(name="TextureType",
                                          description="Texture type",
                                          items=[('spectrum', "spectrum", "spectrum texture"),
                                                 ('float', "float", "float texture")],
                                          default='spectrum', update=update_type)
                                          
    def init(self, context):
        self.outputs.new('NodeSocketColor', "Pbrt Matte")
        
        Tex1_node = self.inputs.new('NodeSocketColor', "Tex1 Texture")
        Tex1_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
        Tex2_node = self.inputs.new('NodeSocketColor', "Tex2 Texture")
        Tex2_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
        Mapping_node = self.inputs.new('NodeSocketVector', "Mapping")
        Mapping_node.hide_value = True

    def draw_buttons(self, context, layout):
        layout.prop(self, "TextureType",text = 'Texture type')
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        
    def draw_label(self):
        return self.bl_label
        
    #Texture "checkers" "spectrum" "checkerboard"
    #"float uscale" [ 16 ]
    #"float vscale" [ 16 ]
    #"rgb tex2" [ 0.2 0.2 0.2 ]
    #"rgb tex1" [ 0.4 0.4 0.4 ]
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        tex1 = self.inputs[0]
        tex2 = self.inputs[1]
        uv = self.inputs[2]
        
        name = self.pbrtv4NodeID
        #file = util.getFileName(self.filename)
        #textName = self.constructTName(name, file)
        res = 'Texture "{}" "{}" "checkerboard"\n'.format(name, self.TextureType)
        
        #tex1
        if not(tex1.is_linked):
            c = tex1.default_value
            if self.TextureType == "spectrum":
                res+='  "rgb tex1" [ {} {} {} ]\n'.format(c[0], c[1], c[2])
            else:
                res+='  "float tex1" [ {} ]\n'.format(c)
        else:
            node_link = tex1.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            res+='  "texture tex1" ["{}"]'.format(nd.pbrtv4NodeID)
            
        #tex2
        if not(tex2.is_linked):
            c = tex2.default_value
            if self.TextureType == "spectrum":
                res+='  "rgb tex2" [ {} {} {} ]\n'.format(c[0], c[1], c[2])
            else:
                res+='  "float tex2" [ {} ]\n'.format(c)
        else:
            node_link = tex2.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            res+='  "texture tex2" ["{}"]'.format(nd.pbrtv4NodeID)
        
        if not(uv.is_linked):
            res+=''
        else:
            node_link = uv.links[0]
            curNode =  node_link.from_node
            res+=curNode.to_string(list, data)
        data.append(res)
        #return text name
        return self
        
class pbrtv4NodeScale(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4NodeScale'
    bl_label = 'Scale'
    bl_icon = 'TEXTURE'
    def update_type(self, context):
        if self.TextureType == "spectrum":
            self.outputs[0].type = "RGBA"
            self.inputs[0].type = "RGBA"
        else:
            self.outputs[0].type = "VALUE"
            self.inputs[0].type = "VALUE"
    
    TextureType: bpy.props.EnumProperty(name="TextureType",
                                          description="Texture type",
                                          items=[('spectrum', "spectrum", "spectrum texture"),
                                                 ('float', "float", "float texture")],
                                          default='spectrum', update=update_type)
    ScaleValue : bpy.props.FloatProperty(default=1.0)
    #Kd : bpy.props.FloatVectorProperty(name="Kd", description="Kd",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    
    def init(self, context):
        self.outputs.new('NodeSocketColor', "Pbrt Matte")
        Texture_node = self.inputs.new('NodeSocketColor', "Texture")
        Texture_node.hide_value = True

    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "TextureType",text = 'Texture type')
        layout.prop(self, "ScaleValue",text = 'Scale')
        
    def draw_label(self):
        return self.bl_label
        
    #Texture "pavet-kd-scaled" "spectrum" "scale"
    #"float scale" [ 0.7 ]
    #"texture tex" [ "pavet-kd-img" ]
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        texture = self.inputs[0]
        if (texture.is_linked):
            node_link = texture.links[0]
            curNode =  node_link.from_node
            
            nd = curNode.Backprop(list, data)
            baseName = nd.pbrtv4NodeID
            textName = name
            res = 'Texture "{}" "{}" "scale"\n'.format(textName, self.TextureType)
            res +='    "float scale" [ {} ]\n'.format(self.ScaleValue)
            res+='    "texture tex" ["{}"]\n'.format(baseName)
        
        data.append(res)
        return self  

class pbrtv4NodeConstant(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4NodeConstant'
    bl_label = 'Constant'
    bl_icon = 'TEXTURE'
    
    def update_type(self, context):
        if self.ConstantType == "color":
            self.outputs[0].type = "RGBA"
        else:
            self.outputs[0].type = "VALUE"
    
    ConstantType: bpy.props.EnumProperty(name="ConstantType",
                                          description="Texture type",
                                          items=[('color', "color", "color"),
                                                 ("blackbody", "blackbody", "Blackbody"),
                                                 ('value', "value", "value")],
                                          default='color', update=update_type)
    
    Value : bpy.props.FloatProperty(default=0.8)
    Color : bpy.props.FloatVectorProperty(name="Color", description="color",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4)
    Temperature : bpy.props.FloatProperty(default=6500.0)
    
    GammaValue : bpy.props.FloatProperty(default=1.0)
    
    ConvertType: bpy.props.EnumProperty(name="ConvertType",
                                          description="Convert color space",
                                          items=[('raw', "raw", "raw"),
                                                 ("toLinear", "toLinear", "to Linear"),
                                                 ('toSRGB', "toSRGB", "to sRGB")],
                                          default='raw')
    
    def init(self, context):
        self.outputs.new('NodeSocketColor', "Pbrt Matte")

    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "ConstantType",text = 'Type')
        if self.ConstantType == 'color':
            layout.prop(self, "Color",text = 'Color')
            layout.prop(self, "ConvertType",text = 'convert')
            layout.prop(self, "GammaValue", text = 'gamma')
        elif self.ConstantType == 'blackbody':
            layout.prop(self, "Temperature",text = 'Blackbody temperature')
        else:
            layout.prop(self, "Value",text = 'Value')
        
    def draw_label(self):
        return self.bl_label
        
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        
        textName = name
        ct = 'float'
        if self.ConstantType == 'color' or self.ConstantType == 'blackbody':
            ct = 'spectrum'
        res = 'Texture "{}" "{}" "constant"\n'.format(textName, ct)
        if self.ConstantType == 'color':
            c = self.Color
            r,g,b = c[0], c[1], c[2]
            if self.ConvertType == 'toSRGB':
                r,g,b = util.linearToSRgb(c[0]), util.linearToSRgb(c[1]), util.linearToSRgb(c[2])
            if self.ConvertType == 'toLinear':
                r,g,b = util.sRgbToLinear(c[0]), util.sRgbToLinear(c[1]), util.sRgbToLinear(c[2])
            #gamma correction
            gamma = self.GammaValue
            r,g,b = util.gammaCorrect(r, gamma), util.gammaCorrect(g, gamma), util.gammaCorrect(b, gamma)
            res+='    "rgb value" [ {} {} {} ]\n'.format(r,g,b)
        elif self.ConstantType == 'blackbody':
            res +='    "blackbody value" [ {} ]\n'.format(self.Temperature)
        else:
            res +='    "float value" [ {} ]\n'.format(self.Value)
        
        data.append(res)
        return self  
        
class pbrtv4NodeMapping2d(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'PBRTV4Mapping2d'
    bl_label = 'Pbrtv4 UV Mapping'
    bl_icon = 'TEXTURE'
    
    UValue : bpy.props.FloatProperty(default=1.0)
    VValue : bpy.props.FloatProperty(default=1.0)
    UDelta : bpy.props.FloatProperty(default=0.0)
    VDelta : bpy.props.FloatProperty(default=0.0)
    MappingType: bpy.props.EnumProperty(name="MappingType",
                                          description="Mapping type",
                                          items=[('uv', "UV", "UV mapping")],
                                          default='uv')
    #Kd : bpy.props.FloatVectorProperty(name="Kd", description="Kd",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    
    def init(self, context):
        self.outputs.new('NodeSocketVector', "Pbrt Matte")

    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "MappingType",text = 'mapping')
        #layout.separator()
        layout.prop(self, "UValue",text = 'U')
        layout.prop(self, "VValue",text = 'V')
        layout.separator()
        layout.prop(self, "UDelta",text = 'UD')
        layout.prop(self, "VDelta",text = 'VD')
        
    def draw_label(self):
        return self.bl_label
    
    #"string wrap" [ "repeat" ]
    #"string mapping" [ "uv" ]
    #"float scale" [ 1 ]
    #"float uscale" [ 1 ]
    #"float vscale" [ -1 ]
    #"float udelta" [ 0 ]
    #"float vdelta" [ 0 ]
    def to_string(self, list, data):
        res = ""
    #    res = '    "string wrap" [ "repeat" ]\n'
        res +='  "string mapping" [ "{}" ]\n'.format(self.MappingType)
        
        res +='  "float uscale" [ {} ]\n'.format(self.UValue)
        res +='  "float vscale" [ {} ]\n'.format(self.VValue)
        
        res +='  "float udelta" [ {} ]\n'.format(self.UDelta)
        res +='  "float vdelta" [ {} ]\n'.format(self.VDelta)
        return res

#pbrtv4NodeMix
class pbrtv4NodeMix(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4NodeMix'
    bl_label = 'Mix'
    bl_icon = 'TEXTURE'
    
    def update_type(self, context):
        if self.TextureType == "spectrum":
            self.outputs[0].type = "RGBA"
            self.inputs[1].type = "RGBA"
            self.inputs[2].type = "RGBA"
        else:
            self.outputs[0].type = "VALUE"
            self.inputs[1].type = "VALUE"
            self.inputs[2].type = "VALUE"
    
    TextureType: bpy.props.EnumProperty(name="TextureType",
                                          description="Texture type",
                                          items=[('spectrum', "spectrum", "spectrum texture"),
                                                 ('float', "float", "float texture")],
                                          default='spectrum', update=update_type)
    #ScaleValue : bpy.props.FloatProperty(default=0.5)
    #Kd : bpy.props.FloatVectorProperty(name="Kd", description="Kd",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    
    def init(self, context):
        self.outputs.new('NodeSocketColor', "mix")
        Amount_node = self.inputs.new('NodeSocketFloat', "Amount")
        Amount_node.default_value = 0.5
        Texture1_node = self.inputs.new('NodeSocketColor', "Texture1")
        Texture2_node = self.inputs.new('NodeSocketColor', "Texture2")

    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "TextureType",text = 'Texture type')
        #layout.prop(self, "ScaleValue",text = 'Scale')
        
    def draw_label(self):
        return self.bl_label
        
    #Texture "pavet-kd-scaled" "spectrum" "scale"
    #"float scale" [ 0.7 ]
    #"texture tex" [ "pavet-kd-img" ]
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        amount = self.inputs[0]
        tex1 = self.inputs[1]
        tex2 = self.inputs[2]
        #res
        res = 'Texture "{}" "{}" "mix"\n'.format(name, self.TextureType)
        
        res += AddFloatTexture(amount, "amount", list, data)
                
        #tex1
        if not(tex1.is_linked):
            c = tex1.default_value
            if self.TextureType == "spectrum":
                res+='  "rgb tex1" [ {} {} {} ]\n'.format(c[0], c[1], c[2])
            else:
                res+='  "float tex1" [ {} ]\n'.format(c)
        else:
            node_link = tex1.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            res+='  "texture tex1" ["{}"]'.format(nd.pbrtv4NodeID)
            
        #tex2
        if not(tex2.is_linked):
            c = tex2.default_value
            if self.TextureType == "spectrum":
                res+='  "rgb tex2" [ {} {} {} ]\n'.format(c[0], c[1], c[2])
            else:
                res+='  "float tex2" [ {} ]\n'.format(c)
        else:
            node_link = tex2.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            res+='  "texture tex2" ["{}"]'.format(nd.pbrtv4NodeID)
        
        data.append(res)
        
        return self
        
class pbrtv4NodeMarble(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4NodeMarble'
    bl_label = 'Marble'
    bl_icon = 'TEXTURE'
    
    def update_type(self, context):
        if self.TextureType == "spectrum":
            self.outputs[0].type = "RGBA"
        else:
            self.outputs[0].type = "VALUE"
    #only spectrum supported, leave it here for now
    TextureType: bpy.props.EnumProperty(name="TextureType",
                                          description="Texture type",
                                          items=[('spectrum', "spectrum", "spectrum texture"),
                                                 ('float', "float", "float texture")],
                                          default='spectrum', update=update_type)
                                          
    Octaves:bpy.props.IntProperty(default=8)
    Roughness:bpy.props.FloatProperty(default=0.5)
    Scale:bpy.props.FloatProperty(default=1.0)
    Variation:bpy.props.FloatProperty(default=0.2)
    
    def init(self, context):
        self.outputs.new('NodeSocketColor', "marble")
        
    def draw_buttons(self, context, layout):
        #layout.prop(self, "TextureType",text = 'Texture type')
        layout.prop(self, "Octaves",text = 'Octaves')
        layout.prop(self, "Roughness",text = 'Roughness')
        layout.prop(self, "Scale",text = 'Scale')
        layout.prop(self, "Variation",text = 'Variation')
        
    def draw_label(self):
        return self.bl_label
        
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        #res
        res = 'Texture "{}" "{}" "marble"\n'.format(name, self.TextureType)
        
        res+='  "integer octaves" [ {} ]\n'.format(self.Octaves)
        res+='  "float roughness" [ {} ]\n'.format(self.Roughness)
        res+='  "float scale" [ {} ]\n'.format(self.Scale)
        res+='  "float variation" [ {} ]\n'.format(self.Variation)
        data.append(res)
        
        return self
        
class pbrtv4NodeDMix(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4NodeDMix'
    bl_label = 'DirectionMix'
    bl_icon = 'TEXTURE'
    
    def update_type(self, context):
        if self.TextureType == "spectrum":
            self.outputs[0].type = "RGBA"
            self.inputs[1].type = "RGBA"
            self.inputs[2].type = "RGBA"
        else:
            self.outputs[0].type = "VALUE"
            self.inputs[1].type = "VALUE"
            self.inputs[2].type = "VALUE"
    
    TextureType: bpy.props.EnumProperty(name="TextureType",
                                          description="Texture type",
                                          items=[('spectrum', "spectrum", "spectrum texture"),
                                                 ('float', "float", "float texture")],
                                          default='spectrum', update=update_type)
    #ScaleValue : bpy.props.FloatProperty(default=0.5)
    UseCamera: bpy.props.BoolProperty(default=False)
    
    def init(self, context):
        self.outputs.new('NodeSocketColor', "mix")
        Amount_node = self.inputs.new('NodeSocketVector', "Direction")
        Amount_node.default_value = [0,1,0]
        Texture1_node = self.inputs.new('NodeSocketColor', "Texture1")
        Texture2_node = self.inputs.new('NodeSocketColor', "Texture2")

    def draw_buttons(self, context, layout):
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        layout.prop(self, "TextureType",text = 'Texture type')
        layout.prop(self, "UseCamera",text = 'use camera vector')
        
    def draw_label(self):
        return self.bl_label
        
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        dir = self.inputs[0]
        tex1 = self.inputs[1]
        tex2 = self.inputs[2]
        #res
        res = 'Texture "{}" "{}" "directionmix"\n'.format(name, self.TextureType)
        
        if self.UseCamera:
            c = util.getCamVector()
            res+='  "vector3 dir" [ {} {} {} ]\n'.format(c[0],c[1],c[2])
        else:
            c = dir.default_value
            res+='  "vector3 dir" [ {} {} {} ]\n'.format(c[0],c[1],c[2])
        
        #tex1
        if not(tex1.is_linked):
            c = tex1.default_value
            if self.TextureType == "spectrum":
                res+='  "rgb tex1" [ {} {} {} ]\n'.format(c[0], c[1], c[2])
            else:
                res+='  "float tex1" [ {} ]\n'.format(c)
        else:
            node_link = tex1.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            res+='  "texture tex1" ["{}"]'.format(nd.pbrtv4NodeID)
            
        #tex2
        if not(tex2.is_linked):
            c = tex2.default_value
            if self.TextureType == "spectrum":
                res+='  "rgb tex2" [ {} {} {} ]\n'.format(c[0], c[1], c[2])
            else:
                res+='  "float tex2" [ {} ]\n'.format(c)
        else:
            node_link = tex2.links[0]
            curNode =  node_link.from_node
            nd = curNode.Backprop(list, data)
            res+='  "texture tex2" ["{}"]'.format(nd.pbrtv4NodeID)
        
        data.append(res)
        
        return self

#mediums
#MakeNamedMedium "liquid"
#"rgb sigma_s" [ 0.00125 0.00125 0.000625 ]
#"rgb sigma_a" [ 0.0125 0.0125 0.01 ]
#"float scale" [ 0.5 ]
#"string type" [ "homogeneous" ]

class pbrtv4UniformgridVolume(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Uniformgrid'
    bl_label = 'uniformgrid'
    bl_icon = 'VOLUME_DATA'
    
    Density : bpy.props.FloatProperty(default=1.00)
    G : bpy.props.FloatProperty(default=0.00)
    Dim : bpy.props.IntVectorProperty(name="Dimensions", description="Dimension vector",default=(1,1,1), min=1, size=3)
    Bbox: bpy.props.PointerProperty(name="Bbox", type=bpy.types.Object)
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "Medium")
        SigmaS_node = self.inputs.new('NodeSocketColor', "Sigma S")
        SigmaS_node.default_value = [0.8, 0.8, 0.8, 1.0]
        SigmaA_node = self.inputs.new('NodeSocketColor', "Sigma A")
        SigmaA_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
    def draw_buttons(self, context, layout):
        #layout.prop(self, "MediumPreset",text = 'Medium Preset')
        layout.prop(self, "Bbox",text = 'Bounding box object')
        layout.prop(self, "Density",text = 'Density')
        layout.prop(self, "Dim",text = 'Dimension vector')
        #layout.prop(self, "G",text = 'g')
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        #layout.prop(self, "Reflectance",text = 'Color')
        
    def draw_label(self):
        return self.bl_label
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        sigma_s = self.inputs[0]
        sigma_a = self.inputs[1]
        res ='MakeNamedMedium "{}"\n'.format(name)
        res +='  "string type" [ "uniformgrid" ]\n'
        
        print(self.Bbox.bound_box)
        res +='  "point3 p0" [ -0.3 -0.3 0 ]\n' #test
        res +='  "point3 p1" [ 0.3 0.3 0.6 ]\n' #test
        
        nx = self.Dim[0]
        ny = self.Dim[1]
        nz = self.Dim[2]
        
        res +='  "integer nz" [ {} ]\n'.format(nz)
        res +='  "integer ny" [ {} ]\n'.format(ny)
        res +='  "integer nx" [ {} ]\n'.format(nx)
        
        density = util.createGrid(nx, ny, nz, self.Density)
        #print(density)
        res +='  "float density" {}\n'.format(density)
        #sigma_s
        res += AddSpecTexture(sigma_s, "sigma_s", list, data)
        #sigma_a        
        res += AddSpecTexture(sigma_a, "sigma_a", list, data)
        
        data.append(res)
        return self

class pbrtv4HomogeneousVolume(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Homogeneous'
    bl_label = 'homogeneous'
    bl_icon = 'VOLUME_DATA'
    
    Scale : bpy.props.FloatProperty(default=1.00)
    G : bpy.props.FloatProperty(default=0.00)
    #Reflectance : bpy.props.FloatVectorProperty(name="reflectance", description="color",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    
    MediumPreset: bpy.props.EnumProperty(name="MediumPreset",
                                              description="",
                                              items=presets.MediumPreset+[("Custom", "Custom", "Custom")],
                                              default='Custom')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "Medium")
        SigmaS_node = self.inputs.new('NodeSocketColor', "Sigma S")
        SigmaS_node.default_value = [0.8, 0.8, 0.8, 1.0]
        SigmaA_node = self.inputs.new('NodeSocketColor', "Sigma A")
        SigmaA_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "MediumPreset",text = 'Medium Preset')
        layout.prop(self, "Scale",text = 'Scale')
        layout.prop(self, "G",text = 'g')
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        #layout.prop(self, "Reflectance",text = 'Color')
        
    def draw_label(self):
        return self.bl_label
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        sigma_s = self.inputs[0]
        sigma_a = self.inputs[1]
        res ='MakeNamedMedium "{}"\n'.format(name)
        res +='  "string type" [ "homogeneous" ]\n'
        res+='  '+'"float scale" [{}]\n'.format(self.Scale)
        res+='  '+'"float g" [{}]\n'.format(self.G)
        if self.MediumPreset != 'Custom':
            res+='  "string preset" "{}"\n'.format(self.MediumPreset)
        else:
            res += AddSpecTexture(sigma_s, "sigma_s", list, data)
            #sigma_a     
            res += AddSpecTexture(sigma_a, "sigma_a", list, data)
            
        data.append(res)
        return self
        
class pbrtv4CloudVolume(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4CloudVolume'
    bl_label = 'cloud'
    bl_icon = 'VOLUME_DATA'
    
    Scale : bpy.props.FloatProperty(default=1.00)
    G : bpy.props.FloatProperty(default=0.00)
    
    Density : bpy.props.FloatProperty(default=1.00)
    Wispiness : bpy.props.FloatProperty(default=1.00)
    Frequency : bpy.props.FloatProperty(default=5.00)
    
    P0 : bpy.props.FloatVectorProperty(name="p0", description="color", default=(0.0, 0.0, 0.0), min=0, max=1, size=3)
    P1 : bpy.props.FloatVectorProperty(name="p1", description="color", default=(1.0, 1.0, 1.0), min=0, max=1, size=3)
    #Reflectance : bpy.props.FloatVectorProperty(name="reflectance", description="color",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    
    MediumPreset: bpy.props.EnumProperty(name="MediumPreset",
                                              description="",
                                              items=presets.MediumPreset+[("Custom", "Custom", "Custom")],
                                              default='Custom')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "Medium")
        SigmaS_node = self.inputs.new('NodeSocketColor', "Sigma S")
        SigmaS_node.default_value = [0.8, 0.8, 0.8, 1.0]
        SigmaA_node = self.inputs.new('NodeSocketColor', "Sigma A")
        SigmaA_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "MediumPreset",text = 'Medium Preset')
        layout.prop(self, "Scale",text = 'Scale')
        layout.prop(self, "G",text = 'g')
        #layout.label(text="ID: {}".format(self.Pbrtv4TreeNodeId))
        #layout.prop(self, "Reflectance",text = 'Color')
        layout.prop(self, "Density",text = 'Density')
        layout.prop(self, "Wispiness",text = 'Wispiness')
        layout.prop(self, "Frequency",text = 'Frequency')
        
        layout.prop(self, "P0",text = 'P0')
        layout.prop(self, "P1",text = 'P1')
        
    def draw_label(self):
        return self.bl_label
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        sigma_s = self.inputs[0]
        sigma_a = self.inputs[1]
        res ='MakeNamedMedium "{}"\n'.format(name)
        res +='  "string type" [ "cloud" ]\n'
        #cloud data
        res+='  '+'"float density" [{}]\n'.format(self.Density)
        res+='  '+'"float wispiness" [{}]\n'.format(self.Wispiness)
        res+='  '+'"float frequency" [{}]\n'.format(self.Frequency)
        #cloud data
        res+='  '+'"float scale" [{}]\n'.format(self.Scale)
        res+='  '+'"float g" [{}]\n'.format(self.G)
        if self.MediumPreset != 'Custom':
            res+='  "string preset" "{}"\n'.format(self.MediumPreset)
        else:
            res += AddSpecTexture(sigma_s, "sigma_s", list, data)
            #sigma_a     
            res += AddSpecTexture(sigma_a, "sigma_a", list, data)
            
        data.append(res)
        return self

class pbrtv4Displacement(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Displacement'
    bl_label = 'Displacement'
    bl_icon = 'MOD_DISPLACE'
    
    Scale : bpy.props.FloatProperty(default=1.00)
    Edge_length : bpy.props.FloatProperty(default=1.00)
    Uvscale : bpy.props.FloatProperty(default=1.00)
    #Reflectance : bpy.props.FloatVectorProperty(name="reflectance", description="color",default=(0.8, 0.8, 0.8, 1.0), min=0, max=1, subtype='COLOR', size=4,update=updateViewportColor)
    
    def init(self, context):
        self.outputs.new('NodeSocketVector', "Displacement")
        Image_node = self.inputs.new('NodeSocketColor', "Image")
        Image_node.hide_value = True
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "Scale",text = 'Scale')
        layout.prop(self, "Uvscale",text = 'UV scale')
        layout.prop(self, "Edge_length",text = 'Edge length')
        
    def draw_label(self):
        return self.bl_label
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        return self
    
    def getDispInfo(self):
        image = self.inputs[0]
        
        edge_length = self.Edge_length
        scale = self.Scale
        uvscale = self.Uvscale
        imagePath = ""
        #get connected image
        if (image.is_linked):
            node_link = image.links[0]
            curNode =  node_link.from_node
            imagePath = util.switchpath(util.realpath(curNode.image.filepath))
        #def CreateInfo(name, outfile, image, edge_length, scale, uvscale):
        dInfo = util.DispInfo.CreateInfo("dispParam", "", imagePath, edge_length, scale, uvscale)
        return dInfo
        
class pbrtv4AreaEmitter(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4AreaEmitter'
    bl_label = 'AreaEmitter'
    bl_icon = 'MATERIAL'
    
    Power : bpy.props.FloatProperty(default=1.00)
    Temperature : bpy.props.FloatProperty(default=6500.00)
    Twosided : bpy.props.BoolProperty(name="Twosided", default=False, description="is two sided")
    
    def updatePreset(self,context):
        Color = self.inputs[0]
        if self.Emission_Preset == "color":
            Color.hide = False
        else:
            Color.hide = True
        
    Emission_Preset: bpy.props.EnumProperty(name="Emission_Preset",
                                            description="Emission spectrum",
                                            items=presets.EmissionPreset+[("blackbody", "blackbody", "Blackbody"),
                                                                          ("color", "color", "Color")],
                                            default='stdillum-D65', update = updatePreset)
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "Emission")
        Color_node = self.inputs.new('NodeSocketColor', "Color")
        Color_node.default_value = [1,1,1,1]
        Color_node.hide = True
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "Twosided",text = 'two sided')
        layout.prop(self, "Emission_Preset",text = 'Type')
        layout.prop(self, "Power",text = 'Power')
        if self.Emission_Preset == "blackbody":
            layout.prop(self, "Temperature",text = 'Temperature')
        
    def draw_label(self):
        return self.bl_label
    
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        return self
    
    def getEmissionInfo(self, mat_name):
        image = self.inputs[0]
        
        power = self.Power
        temp = self.Temperature
        twosided = self.Twosided
        #self.Emission_Preset
        imagePath = ""
        color = [0,0,0]
        #get connected image
        if (image.is_linked):
            node_link = image.links[0]
            curNode =  node_link.from_node
            imagePath = util.switchpath(util.realpath(curNode.image.filepath))
        else:
            color = image.default_value
        #def CreateInfo(name, outfile, image, edge_length, scale, uvscale):
        eInfo = util.MatInfo.CreateInfo(mat_name, True, color, power, self.Emission_Preset, temp)
        return eInfo
        
    def getEmissionStr(self):
        color = self.inputs[0]
        result = '    '+'AreaLightSource "diffuse"\n'
        if self.Emission_Preset == 'color':
            if (image.is_linked):
                node_link = image.links[0]
                curNode =  node_link.from_node
                imagePath = util.switchpath(util.realpath(curNode.image.filepath))
                result += '    '+'    '+'"string filename" "{}"\n'.format(imagePath)
            else:
                c = color.default_value
                result += '    '+'    '+'"rgb L" [ {} {} {} ]\n'.format(c[0], c[1], c[2])
        elif self.Emission_Preset == 'blackbody':
            result += "    "+"    "+'"blackbody L" [{}]\n'.format(self.Temperature)
        else:
            result += '    '+'    '+'"spectrum L" "{}"\n'.format(self.Emission_Preset)
        result += "    "+"    "+'"float scale" [{}]\n'.format(self.Power)
        return result

class pbrtv4Output(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Output'
    bl_label = 'PBRT4 Output'
    bl_icon = 'MATERIAL'
    
    def update_active(self, context):
        #color = [0.5,0.5,0.5]
        theme = util.get_theme(bpy.context)
        color = theme.node_editor.node_backdrop[:3]
        if self.is_active_output:
            self.disable_others(self)
            self.name = 'PBRT4 Output'
            #self.color = [color[0]*0.5, color[1]*0.7, color[2] * 1.0]
            self.color = [0.169*0.5, 0.396*0.5, 0.169*0.5]
        else:
            self.name = 'UnusedOutput'
            self.color = [color[0] * 0.5, color[1]*0.5, color[2]*0.5]
            
    is_active_output: bpy.props.BoolProperty(name="is active output", default=True, description="is active output", update=update_active)
    
    def init(self, context):
        self.use_custom_color = True
        self.is_active_output = True
        #0
        BSDF_node = self.inputs.new('NodeSocketShader', "Bsdf")
        #1
        Inside_Medium_node = self.inputs.new('NodeSocketShader', "Inside medium")
        #2
        Outside_Medium_node = self.inputs.new('NodeSocketShader', "Outside medium")
        #3
        Emission_node = self.inputs.new('NodeSocketShader', "Emission")
        #4
        Disp_node = self.inputs.new('NodeSocketVector', "Displacement")
        Disp_node.hide_value = True
        #5
        Alpha_node = self.inputs.new('NodeSocketFloatUnsigned', "Alpha")
        Alpha_node.default_value = 1.0
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "is_active_output")
    
    def copy(self, orig_node):
        if self.is_active_output:
            self.is_active_output = True
    
    def free(self):
        if self.is_active_output:
            self.set_first_match()
            
    def draw_label(self):
        return self.bl_label
    
    def set_first_match(self):
        node_tree = self.id_data
        if node_tree is None:
            return
        for node in util.get_output_nodes(node_tree, self.bl_idname):
            node.is_active_output = True
            break
    
    def disable_others(self, selected):
        node_tree = self.id_data
        if node_tree is None:
            return
        for node in util.get_output_nodes(node_tree, self.bl_idname):
            if not node == selected:
                node.is_active_output = False
                
    def to_string(self, list, data):
        name = self.pbrtv4NodeID
        return self
        
class pbrtv4DisneyMaterial(PBRTV4TreeNode):
    '''A custom node'''
    bl_idname = 'pbrtv4Disney'
    bl_label = 'disney'
    bl_icon = 'MATERIAL'

    Eta : bpy.props.FloatProperty(default=1.5, min=1.0, max=999.0)
    Specular : bpy.props.FloatProperty(default=0.5, min=0.0, max=999.0)
    #Sheen : bpy.props.FloatProperty(default=0.0, min=0.0, max=999.0)
    SheenTint : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    Clearcoat : bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    Subsurface:bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    Metallic:bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    ClearcoatGloss:bpy.props.FloatProperty(default=1.0, min=0.0, max=1.0)
    Anisotropic:bpy.props.FloatProperty(default=0.0, min=-999.0, max=1.0)
    Transmission:bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    SpecularTint:bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)
    
    Ior_type: bpy.props.EnumProperty(name="Ior_type",
                                              description="IOR type",
                                              items=[
                                              ("eta", "eta", "eta"),
                                              ("specular", "specular", "specular")
                                              ],
                                              default='eta')
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "BSDF")
        ColorTexture_node = self.inputs.new('NodeSocketColor', "color")
        ColorTexture_node.default_value = [0.8, 0.8, 0.8, 1.0]
        
        RoughnessTexture_node = self.inputs.new('NodeSocketFloat', "roughness")
        RoughnessTexture_node.default_value = 0.5
        
        MetallicTexture_node = self.inputs.new('NodeSocketFloat', "metallic")
        MetallicTexture_node.default_value = 0.0
        
        SheenTexture_node = self.inputs.new('NodeSocketFloat', "sheen")
        SheenTexture_node.default_value = 0.0
        
        DisplacementTexture_node = self.inputs.new('NodeSocketFloat', "displacement")
        DisplacementTexture_node.hide_value = True
        
        NormalTexture_node = self.inputs.new('NodeSocketFloat', "normal")
        NormalTexture_node.hide_value = True
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "Ior_type",text = 'IOR type')
        if self.Ior_type == "eta":
            layout.prop(self, "Eta",text = 'Eta')
        else:
            layout.prop(self, "Specular",text = 'Specular')
        #layout.prop(self, "Sheen",text = 'Sheen')
        layout.prop(self, "SheenTint",text = 'Sheen Tint')
        layout.prop(self, "Clearcoat",text = 'Clearcoat')
        layout.prop(self, "ClearcoatGloss", text = "ClearcoatGloss")
        layout.prop(self, "Anisotropic", text = "Anisotropic")
        layout.prop(self, "Subsurface",text = 'Subsurface')
        layout.prop(self, "Transmission",text = 'Transmission')
        layout.prop(self, "SpecularTint",text = 'SpecularTint')
        #layout.prop(self, "Metallic",text = 'Metallic')
        
    def draw_label(self):
        return self.bl_label
        
    #return str to add blocks from connected nodes to current and data to write to file
    def to_string(self, list, data):
        color = self.inputs.get("color")
        roughness = self.inputs.get("roughness")
        metallic = self.inputs.get("metallic")
        disp = self.inputs.get("displacement")
        norm = self.inputs.get("normal")
        sheen = self.inputs.get("sheen")
        
        name = self.pbrtv4NodeID
        res ='MakeNamedMaterial "{}"\n'.format(name)
        res +='  "string type" [ "disney" ]\n'
        
        res += AddSpecTexture(color, "color", list, data)
            
        #export roughness
        res += AddFloatTexture(roughness, "roughness", list, data)
            
        #export sheen
        res += AddFloatTexture(sheen, "sheen", list, data)
        
        #export metallic
        res += AddFloatTexture(metallic, "metallic", list, data)
        
        #export bump
        res += AddDispTexture(disp, list, data)
        
        res += AddNormTexture(norm)
        
        #eta
        res+='  "float eta" [{}]\n'.format(self.Eta)
        #Specular
        res+='  "float specular" [{}]\n'.format(self.Specular)
        #Specular tint 
        res+='  "float specularTint" [{}]\n'.format(self.SpecularTint)
        #Sheen
        #res+='  "float sheen" [{}]\n'.format(self.Sheen)
        #SheenTint
        res+='  "float sheenTint" [{}]\n'.format(self.SheenTint)
        #Clearcoat
        res+='  "float clearcoat" [{}]\n'.format(self.Clearcoat)
        #ClearcoatGloss
        res+='  "float clearcoatGloss" [{}]\n'.format(self.ClearcoatGloss)
        #Anisotropic
        res+='  "float anisotropic" [{}]\n'.format(self.Anisotropic)
        #Transmission
        res+='  "float transmission" [{}]\n'.format(self.Transmission)
        #subsurface
        res+='  "float subsurface" [{}]\n'.format(self.Subsurface)
        #metallic
        #res+='  "float metallic" [{}]\n'.format(self.Metallic)
        
        res+='  "bool isSpecular" {}\n'.format("false" if self.Ior_type == "eta" else "true")
        
        data.append(res)
        return self
        
#https://blender.stackexchange.com/questions/299282/create-node-and-have-the-node-follow-the-mouse
def get_current_loc(context, event, ui_scale):
    x, y = context.region.view2d.region_to_view(event.mouse_region_x, event.mouse_region_y)
    return x / ui_scale, y / ui_scale
    
class AddNodeOperator(bpy.types.Operator):
    bl_idname = "mymenu.node_adder"
    bl_label = "Menu Operator"
    bl_options = {"UNDO"}
    
    NodesList: bpy.props.EnumProperty(name="NodesList",
                                              description="",
                                              items=[])
    
    def invoke(self, context, event):
        node_type = self.NodesList
        try:
            mat = context.material
            nodes = mat.node_tree.nodes
            bpy.ops.node.select_all(action='DESELECT')
            node = nodes.new(node_type)
            node.select = True
            node.location = get_current_loc(context, event, context.preferences.system.ui_scale)
        except:
            self.report({'WARNING'}, "Can't add node")
            return {'CANCELLED'}
        bpy.ops.node.translate_attach_remove_on_cancel("INVOKE_DEFAULT")
        return {"FINISHED"}
   
class ShadersOperator(AddNodeOperator):
    bl_idname = "mymenu.shaders_add"
    NodesList: bpy.props.EnumProperty(name="NodesList",
                                              description="",
                                              items=pbrt4_nodes["Shaders"])
                                              
class OutputsOperator(AddNodeOperator):
    bl_idname = "mymenu.outputs_add"
    NodesList: bpy.props.EnumProperty(name="NodesList",
                                              description="",
                                              items=pbrt4_nodes["Outputs"])

class TexturesOperator(AddNodeOperator):
    bl_idname = "mymenu.textures_add"
    NodesList: bpy.props.EnumProperty(name="NodesList",
                                              description="",
                                              items=pbrt4_nodes["Textures"])
                                              
class ShapeParsOperator(AddNodeOperator):
    bl_idname = "mymenu.shapepars_add"
    NodesList: bpy.props.EnumProperty(name="NodesList",
                                              description="",
                                              items=pbrt4_nodes["ShapeParameters"])

class MappingOperator(AddNodeOperator):
    bl_idname = "mymenu.mapping_add"
    NodesList: bpy.props.EnumProperty(name="NodesList",
                                              description="",
                                              items=pbrt4_nodes["Mapping"])

class MediumsOperator(AddNodeOperator):
    bl_idname = "mymenu.mediums_add"
    NodesList: bpy.props.EnumProperty(name="NodesList",
                                              description="",
                                              items=pbrt4_nodes["Mediums"])
                                              
class pbrtv4Menu(bpy.types.Menu):
    bl_idname = "PBRTV4_MT_MENU"
    bl_label = "pbrt4menu"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator_menu_enum(ShadersOperator.bl_idname, "NodesList", text = "Shaders")
        layout.operator_menu_enum(OutputsOperator.bl_idname, "NodesList", text = "Outputs")
        layout.operator_menu_enum(TexturesOperator.bl_idname, "NodesList", text = "Textures")
        layout.operator_menu_enum(ShapeParsOperator.bl_idname, "NodesList", text = "Shape parameters")
        layout.operator_menu_enum(MappingOperator.bl_idname, "NodesList", text = "Mapping")
        layout.operator_menu_enum(MediumsOperator.bl_idname, "NodesList", text = "Mediums")
        
    @classmethod
    def poll(cls, context):
        #Do not add the PBRT nodes category if PBRT is not selected as renderer
        engine = context.scene.render.engine
        if engine != 'PBRTV4':
            return False
        else:
            b = False
            if context.space_data.tree_type == 'ShaderNodeTree': b = True
            return b
        
def menu_draw(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(pbrtv4Menu.bl_idname, text="PBRT4 Nodes")

classes = (
    #menus
    ShadersOperator,
    OutputsOperator,
    TexturesOperator,
    ShapeParsOperator,
    MappingOperator,
    MediumsOperator,
    pbrtv4Menu,
    #nodes
    pbrtv4Output,
    pbrtv4PlasticMaterial,
    pbrtv4Displacement,
    pbrtv4AreaEmitter,
    pbrtv4SubsurfaceMaterial,
    pbrtv4NodeMix,
    pbrtv4NodeDMix,
    pbrtv4NodeMarble,
    pbrtv4HomogeneousVolume,
    pbrtv4CloudVolume,
    pbrtv4UniformgridVolume,
    pbrtv4NodeImageTexture2d,
    pbrtv4NoneMaterial,
    pbrtv4MeasuredMaterial,
    pbrtv4NodeConstant,
    pbrtv4NodeCheckerboard,
    pbrtv4NodeScale,
    pbrtv4DiffTransMaterial,
    pbrtv4MixMaterial,
    pbrtv4ConductorMaterial,
    pbrtv4DielectricMaterial,
    pbrtv4DiffuseMaterial,
    pbrtv4CoateddiffuseMaterial,
    pbrtv4NodeMapping2d,
    pbrtv4CoatedconductorMaterial,
    pbrtv4HairMaterial,
    pbrtv4DisneyMaterial
)

def register():
    bpy.types.NODE_MT_add.append(menu_draw)
    #add internal Id property for Node
    bpy.types.Node.pbrtv4NodeID = bpy.props.StringProperty(name="NodeID", default = "NodeID")
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    bpy.types.NODE_MT_add.remove(menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Node.pbrtv4NodeID