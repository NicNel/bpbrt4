bl_info = {
    "name": "PBRTV4_Exporter",
    "author": "NicNel",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "category": "Render",
    "location": "Info header, render engine menu",
    "description": "PBRTV4 for Blender",
    "warning": "",
}

import sys
import os

currDir = os.path.abspath(os.path.dirname(__file__))
#sys.path.append(currDir)

from .pbrt import registerPbrt, unregisterPbrt

def register():
    #pbrt.register()
    registerPbrt()

def unregister():
    #pbrt.unregister()
    unregisterPbrt()