import os
import bpy
import copy
import mathutils
import math

from ..utils import util

#"L" "scale" "from" "to" ("illuminance")
#AttributeBegin
    #CoordSysTransform "camera"
    #LightSource "distant"
        #"rgb L" [ 0.2 0.2 0.2 ]
#AttributeEnd
def export_distant_light(light):
    print("Export distant light")
    fromPos = light.location
    #rot_output = evaluated_obj.rotation_euler.to_quaternion()
    #dir_v = util.get_direction_from_quat(rot_output)
    rot_output = light.rotation_euler.to_matrix()
    vec = mathutils.Vector((0.0, 0.0, 1.0))
    dir_v = rot_output@ -vec
    dir_v.normalize()
    toPos = fromPos+dir_v
    scale = light.data.pbrtv4_light_power
    res = "AttributeBegin\n"
    res += "    "+'LightSource "distant"\n'
    if light.data.pbrtv4_light_preset == 'color':
        res += "    "+"    "+'"rgb L" [{} {} {}]\n'.format(light.data.pbrtv4_light_color[0],light.data.pbrtv4_light_color[1],light.data.pbrtv4_light_color[2])
    elif light.data.pbrtv4_light_preset == 'temperature':
        temperature = light.data.pbrtv4_light_temperature
        res += "    "+"    "+'"blackbody L" [{}]\n'.format(temperature)
    else:
        res += "    "+"    "+'"spectrum L" ["{}"]\n'.format(light.data.pbrtv4_light_preset)
    res += "    "+"    "+'"float scale" [{}]\n'.format(scale)
    res += "    "+"    "+'"point3 from" [{} {} {}]\n'.format(fromPos.x, fromPos.y, fromPos.z)
    res += "    "+"    "+'"point3 to" [{} {} {}]\n'.format(toPos.x, toPos.y, toPos.z)
    res += "AttributeEnd\n"
    return res
#"I" "scale" "power" "from"
def export_point_light(light):
    fromPos = light.location
    scale = light.data.pbrtv4_light_power
    print("Export point light")
    res = "AttributeBegin\n"
    res += "    "+'LightSource "point"\n'
    if light.data.pbrtv4_light_preset == 'color':
        res += "    "+"    "+'"rgb I" [{} {} {}]\n'.format(light.data.pbrtv4_light_color[0],light.data.pbrtv4_light_color[1],light.data.pbrtv4_light_color[2])
    elif light.data.pbrtv4_light_preset == 'temperature':
        temperature = light.data.pbrtv4_light_temperature
        res += "    "+"    "+'"blackbody I" [{}]\n'.format(temperature)
    else:
        res += "    "+"    "+'"spectrum I" ["{}"]\n'.format(light.data.pbrtv4_light_preset)
    res += "    "+"    "+'"float scale" [{}]\n'.format(scale)
    res += "    "+"    "+'"point3 from" [{} {} {}]\n'.format(fromPos.x, fromPos.y, fromPos.z)
    res += "AttributeEnd\n"
    return res
def export_spot_light(light):
    scale = light.data.pbrtv4_light_power
    size = math.degrees(light.data.spot_size)/2.0
    blend = size*light.data.spot_blend
    cameramatrix = light.matrix_world.copy()
    matrixTransposed = cameramatrix.transposed()
    from_point=light.matrix_world.col[3]
    at_point=light.matrix_world.col[2]
    at_point=at_point * -1
    at_point=at_point + from_point
    print("SPOT LOCATION: ",from_point)
    print("SPOT TARGET: ",at_point)
    print("SPOT POWER: ",scale)
    print("SPOT SIZE: ",size)
    print("SPOT BLEND: ",blend)
    
    print("Export spot light")
    res = "AttributeBegin\n"
    res += "    "+'LightSource "spot"\n'
    if light.data.pbrtv4_light_preset == 'color':
        res += "    "+"    "+'"rgb I" [{} {} {}]\n'.format(light.data.pbrtv4_light_color[0],light.data.pbrtv4_light_color[1],light.data.pbrtv4_light_color[2])
    elif light.data.pbrtv4_light_preset == 'temperature':
        temperature = light.data.pbrtv4_light_temperature
        res += "    "+"    "+'"blackbody I" [{}]\n'.format(temperature)
    else:
        res += "    "+"    "+'"spectrum I" ["{}"]\n'.format(light.data.pbrtv4_light_preset)
    res += "    "+"    "+'"float scale" [{}]\n'.format(scale)
    res += "    "+"    "+'"point3 from" [{} {} {}]\n'.format(from_point.x, from_point.y, from_point.z)
    res += "    "+"    "+'"point3 to" [{} {} {}]\n'.format(at_point.x, at_point.y, at_point.z)
    res += "    "+"    "+'"float coneangle" [{}]\n'.format(size)
    res += "    "+"    "+'"float conedeltaangle" [{}]\n'.format(blend)
    res += "AttributeEnd\n"
    return res