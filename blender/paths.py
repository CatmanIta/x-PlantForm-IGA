"""
    We define here the paths needed to integrate Blender and the generator.

    @author: Michele Pirovano
    @copyright: 2013-2015
"""


XPLANTFORM_PATH = "C:\\Users\\Michele\\Documents\\EclipseWorkspace\\xplantform\\"    # TODO: this should be found automatically. Can we do it, or will blender complain?

BLENDER_PATH = "C:/Program Files/Blender Foundation/Blender266a/blender.exe"
BLENDER_PYTHON_PATH = "C:\\Program Files\\Blender Foundation\\Blender266a\\2.66"

XPLANTFORM_BLENDER_PATH = XPLANTFORM_PATH +"blender\\"
GENERATE_BLENDER_FILE = XPLANTFORM_BLENDER_PATH + "imagegeneration\\generate.blend"
GENERATE_BLENDER_SCRIPT = XPLANTFORM_BLENDER_PATH + "imagegeneration\\generateplantimageblenderscript.py"
GENOMES_TO_RENDER_FILE = XPLANTFORM_BLENDER_PATH + "imagegeneration\\genomes_to_render.txt"

EGG_OUTPUT_PATH = XPLANTFORM_BLENDER_PATH+"output\\egg\\"
PNG_OUTPUT_PATH = XPLANTFORM_BLENDER_PATH+"output\\png\\"