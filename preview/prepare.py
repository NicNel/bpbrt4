import os, shutil
from ..utils.util import createFolder

def preparePreview(previewFolder):
    curDir = os.path.abspath(os.path.dirname(__file__))
    sceneDir = os.path.join(curDir, 'scene')
    geometryDir = os.path.join(sceneDir, 'geometry')
    destGeometryDir = os.path.join(previewFolder, "geometry")
    destGeometryDir = createFolder(destGeometryDir)
    print(geometryDir)
    print(destGeometryDir)
    copytree(geometryDir, destGeometryDir)
    #copy base files
    bsdfs_base = os.path.join(sceneDir, 'bsdfs_base.pbrt')
    geometry_base = os.path.join(sceneDir, 'geometry_base.pbrt')
    scene_base = os.path.join(sceneDir, 'scene.pbrt')
    
    shutil.copy2(bsdfs_base, previewFolder)
    shutil.copy2(geometry_base, previewFolder)
    shutil.copy2(scene_base, previewFolder)
    
def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
