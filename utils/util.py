import datetime
import os
import sys

import mathutils

import bpy
import bpy_extras
from bpy.app.handlers import persistent

import pathlib
import subprocess
from pathlib import Path
import numpy as np

#stop process
import signal
from subprocess import check_output

is_postProcess = False

#store completed objects parts by materials
class MatInfo(object):
    def __init__(self, _name):
        self.name = _name # dict containing entries like mesh_name : [exported materials]
        self.preset = "" #preset name
        self.isEmissive = False #dict name, isEm, color
        self.emColor = []
        self.scale = 1.0;
        self.insideMediumName = ""
        self.outsideMediumName = ""
        self.temperature = 6500
        self.alpha = None
        
    def getEmissionStr(self):
        if self.isEmissive:
            result = '    '+'AreaLightSource "diffuse"\n'
            if self.preset == 'color':
                result += '    '+'    '+'"rgb L" [ {} {} {} ]\n'.format(self.emColor[0], self.emColor[1], self.emColor[2])
            elif self.preset == 'blackbody':
                result += "    "+"    "+'"blackbody L" [{}]\n'.format(self.temperature)
            else:
                result += '    '+'    '+'"spectrum L" "{}"\n'.format(self.preset)
            result += "    "+"    "+'"float scale" [{}]\n'.format(self.scale)
            return result
        return ""
    @staticmethod
    def CreateInfo(_name, _isEm = False, _color = [0,0,0], _power = 0, _preset = "", _temp = 6500):
        matInfo = MatInfo(_name)
        matInfo.isEmissive = _isEm
        matInfo.preset = _preset
        matInfo.scale = _power
        matInfo.emColor.append(_color[0]);
        matInfo.emColor.append(_color[1]);
        matInfo.emColor.append(_color[2]);
        matInfo.temperature = _temp
        return matInfo

class DispInfo(object): #displacement information parameters
    def __init__(self, _name):
        self.name = "displacement"
        self.edge_length = 1.0
        self.scale = 1.0
        self.uvscale = 1.0
        self.outfile = ""
        self.image = ""
    def ToStr(self):
        res = self.name+"\n"
        res += "edge_length: "+str(self.edge_length)+"\n"
        res += "scale: "+str(self.scale)+"\n"
        res += "uvscale: "+str(self.uvscale)+"\n"
        res += "outfile: "+self.outfile+"\n"
        res += "image: "+self.image+"\n"
        return res
    @staticmethod
    def CreateInfo(name, outfile, image, edge_length, scale, uvscale):
        dInfo = DispInfo(name)
        dInfo.edge_length = edge_length
        dInfo.scale = scale
        dInfo.uvscale = uvscale
        dInfo.outfile = outfile
        dInfo.image = image
        return dInfo
    @staticmethod
    def CreateCopy(diBase):
        dInfo = DispInfo(diBase.name)
        dInfo.edge_length = diBase.edge_length
        dInfo.scale = diBase.scale
        dInfo.uvscale = diBase.uvscale
        dInfo.outfile = diBase.outfile
        dInfo.image = diBase.image
        return dInfo
        
def safe_register_class(cls):
    try:
        bpy.utils.register_class(cls)
    except Exception as e:
        print ("ERROR: Failed to register class {0}: {1}".format(cls, e))

def deleteAllInFolder(folder):
    pass
    #comment this for now
    #for filename in os.listdir(folder):
    #    file_path = os.path.join(folder, filename)
    #    try:
    #        if os.path.isfile(file_path) or os.path.islink(file_path):
    #            print("delete file: ", file_path)
    #            os.unlink(file_path)
    #        elif os.path.isdir(file_path):
    #            shutil.rmtree(file_path)
    #    except Exception as e:
    #        print('Failed to delete %s. Reason: %s' % (file_path, e))

def getCamVector():
    obj_camera = bpy.context.scene.camera
    mat= obj_camera.matrix_world
    dir= mathutils.Vector((0,0,1,1))@mat.transposed()
    dir.resize_3d()
    dir.normalize()
    return dir
        
def getFileName(path):
    head, tail = os.path.split(path)
    return tail
def replaceExtension(name, ext):
    res = os.path.splitext(name)[0]+'.'+ext
    return res
def withoutExtension(name):
    res = os.path.splitext(name)[0]
    return res
def getExtension(name):
    res = os.path.splitext(name)[1]
    res = res.split('.')
    return res[-1]
def gammaCorrect(value, gamma):
    return pow(value, 1.0 / gamma);
    
def sRgbToLinear(s):
    if s>=0 and s <= 0.04045:
        return s/12.92
    if s>0.04045 and s<=1.0:
        p = (s+0.055)/1.055
        return pow(p, 2.4)
    return 1.0

def linearToSRgb(s):
    if s>=0 and s <= 0.0031308:
        return s*12.92
    if s>0.0031308 and s<=1.0:
        p = 1.055 * pow(s, (1/2.4))-0.055
        return p
    return 1.0

def safe_unregister_class(cls):
    try:
        bpy.utils.unregister_class(cls)
    except Exception as e:
        print ("ERROR: Failed to unregister class {0}: {1}".format(cls, e))

#generate array string for medium grid
def createGrid(nx, ny, nz, value, random = False):
    total = nx*ny*nz
    arr=np.empty(total)
    #random
    if random:
        arr.fill(-1)
        arr = np.where(arr < 0, np.random.uniform(0, value, size=arr.shape), arr)
    else:
        arr.fill(value)
    #random
    np.set_printoptions(threshold=sys.maxsize)
    res_str = np.array2string(arr)
    np.set_printoptions(threshold = False)
    return res_str
    
def spectral_color(r, g, b, l): # RGB <0,1> <- lambda l <400,700> [nm]
    t = 0
    r=0.0
    g=0.0
    b=0.0
    if (l>=400.0) and (l<410.0):
        t=(l-400.0)/(410.0-400.0)
        r=+(0.33*t)-(0.20*t*t)
    elif (l>=410.0)and(l<475.0):
        t=(l-410.0)/(475.0-410.0)
        r=0.14-(0.13*t*t)
    elif (l>=545.0)and(l<595.0):
        t=(l-545.0)/(595.0-545.0)
        r=+(1.98*t)-(t*t)
    elif (l>=595.0)and(l<650.0):
        t=(l-595.0)/(650.0-595.0)
        r=0.98+(0.06*t)-(0.40*t*t)
    elif (l>=650.0)and(l<700.0):
        t=(l-650.0)/(700.0-650.0)
        r=0.65-(0.84*t)+(0.20*t*t)
    
    if (l>=415.0)and(l<475.0):
        t=(l-415.0)/(475.0-415.0)
        g=+(0.80*t*t)
    elif (l>=475.0)and(l<590.0):
        t=(l-475.0)/(590.0-475.0)
        g=0.8 +(0.76*t)-(0.80*t*t)
    elif (l>=585.0)and(l<639.0):
        t=(l-585.0)/(639.0-585.0)
        g=0.84-(0.84*t)
    
    if (l>=400.0)and(l<475.0):
        t=(l-400.0)/(475.0-400.0)
        b=+(2.20*t)-(1.50*t*t)
    elif (l>=475.0)and(l<560.0):
        t=(l-475.0)/(560.0-475.0)
        b=0.7-(t)+(0.30*t*t)
        
def ShowMessageBox(message, title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text = message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def runCmd(cmd, stdout=None, cwd=None, env=None):
    stdoutInfo = ""
    if stdout is not None:
        stdoutInfo = " > {}".format(stdout.name)
    print(">>> {}{}".format(cmd, stdoutInfo))
    subprocess.call(cmd, shell=False, stdout=stdout, cwd=cwd, env=env)

def filter_params(params):
    filter_list = list()
    for p in params:
        if p not in filter_list:
            filter_list.append(p)
    
    return filter_list

def realpath(path):
    if path.startswith('//'):
        path = bpy.path.abspath(path)
    else:
        path = os.path.realpath(path)
    path = path.replace('\\', '/')
    path = os.path.realpath(path)

    return path
    
def switchpath(path):
    p = pathlib.PureWindowsPath(path)
    return p.as_posix()

def getFileName(file):
    #base = os.path.basename(file)
    #name = os.path.splitext(base)
    #return name[0]
    return Path(file).stem

def Lerp(a, b, t):
    return a-(a*t)+(b*t)

def InvLerp(a, b, t):
    return (t-a)/(b-a)

def matrixtostr(matrix):
    return ' %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f '%(matrix[0][0],matrix[0][1],matrix[0][2],matrix[0][3],matrix[1][0],matrix[1][1],matrix[1][2],matrix[1][3],matrix[2][0],matrix[2][1],matrix[2][2],matrix[2][3],matrix[3][0],matrix[3][1],matrix[3][2],matrix[3][3])

def get_render_resolution(scene):
    scale = scene.render.resolution_percentage / 100.0
    width = int(scene.render.resolution_x * scale)
    height = int(scene.render.resolution_y * scale)
    return width, height

def calc_film_aspect_ratio(scene):
    render = scene.render
    scale = render.resolution_percentage / 100.0
    width = int(render.resolution_x * scale)
    height = int(render.resolution_y * scale)
    xratio = width * render.pixel_aspect_x
    yratio = height * render.pixel_aspect_y
    return xratio / yratio

def get_focal_distance(camera):
    if camera.data.dof.focus_object is not None:
        cam_location = camera.matrix_world.to_translation()
        cam_target_location = bpy.data.objects[camera.data.dof.focus_object.name].matrix_world.to_translation()
        focal_distance = (cam_target_location - cam_location).magnitude
    else:
        focal_distance = camera.data.dof.focus_distance

    return focal_distance

def createFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder
    
def get_pid(name):
    return check_output(["pidof",name])

def stop_process(name):
    pid = get_pid(name)
    os.kill(pid, signal.SIGSTOP)

def restart_process(name):
    pid = get_pid(name)
    os.kill(pid, signal.SIGCONT)
    
def stopPbrt():
    name = "pbrt.exe"
    stop_process(name)

#from BlendLuxCore
def get_theme(context):
    current_theme_name = context.preferences.themes.items()[0][0]
    return context.preferences.themes[current_theme_name]

def get_output_nodes(node_tree, ID):
    """ Return a list with all output nodes in a node tree """
    #print("NODE ID: "+ID)
    output_type = ID
    nodes = []

    for node in node_tree.nodes:
        node_type = getattr(node, "bl_idname", None)
        if node_type == output_type:
            nodes.append(node)
    return nodes
    
def register():
    pass

def unregister():
    pass
