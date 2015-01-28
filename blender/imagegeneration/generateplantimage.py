"""
    @note: the blend file 'generate.blend' is made so to be good for rendering, with the view screen aligned to (roughly) the camera height.

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import os
import subprocess
import sys

from blender.paths import *
from blender.options import *

def generatePlantImages(genomes):
    """
    This calls blender to generate a plant image
    """
    if PASS_ARGUMENTS_TO_BLENDER_PYTHON_USING_FILES:
        saveGenomesToFile(genomes)
        genArg = ""
    else:
        # @note: If the arguments are too many (as is the case of rendering large plants), passing them directly will crash blender
        genArg = createGenomesArgument(genomes)

    """
    I try to check whether this is Panda or Blender... but they are the same!
    print sys.version
    print sys.version_info
    print sys.executable
    print sys.platform"""

    # @note: We cannot run blender in the background, or the bpy.context is not available, hence no operators can be used
    #subprocess.call([BLENDER_PATH, "--background", "--python", GENERATE_BLENDER_SCRIPT])
    subprocess.call([BLENDER_PATH, GENERATE_BLENDER_FILE
                     ,"--python", GENERATE_BLENDER_SCRIPT
                     ,"-p","0","0","10","10"       # Window: -p <sx> <sy> <w> <h>    Open with lower left corner at <sx>, <sy>  and width and height <w>, <h>.
                     ,genArg
                     ])

def createGenomesArgument(genomes):
    s = "--"
    for genome in genomes:
        s += " " + genome
    return s

def saveGenomesToFile(genomes):
    f =  open(GENOMES_TO_RENDER_FILE, 'w')
    for genome in genomes:
        f.write(genome+"\n")
    f.close()
