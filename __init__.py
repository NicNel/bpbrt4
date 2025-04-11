import sys
import os

currDir = os.path.abspath(os.path.dirname(__file__))

from .pbrt import registerPbrt, unregisterPbrt

def register():
    registerPbrt()

def unregister():
    unregisterPbrt()