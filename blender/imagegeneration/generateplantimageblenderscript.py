"""
Blender script to generate and save images of the plants using the genomes read from a file
"""

# START INTEGRATION CODE
# This code needs to be called by any script loaded with blender that uses x-plantform
import sys
classesPath = "C:\\Users\\Michele\\Documents\\EclipseWorkspace\\xplantform\\"
if not classesPath in sys.path: sys.path.append(classesPath)
import blender.scriptsharedcode
import imp
imp.reload(blender.scriptsharedcode)
from blender.scriptsharedcode import *
# END INTEGRATION CODE

import blender.options
imp.reload(blender.options)
from blender.options import *

from bpy.app.handlers import persistent     # I am using app.handlers to make sure the context is correctly loaded before performing my script
import base64

VERBOSE = False

@persistent
def do_generate_image(scene, context):
    if VERBOSE: print ("STARTING DO_GENERATE_IMAGE")

    # We need to override the context's area to make sure it is the VIEW_3D
    # To do so, I must obtain the correct context from the screen
    # For operators to work correctly: http://www.blender.org/documentation/blender_python_api_2_63_7/bpy.ops.html#overriding-context
    screen = context.screen
    overridenContext = context.copy()
    overridenContext['scene'] = scene
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            overridenContext['area'] = area
            for region in area.regions:
                if region.type == 'WINDOW':
                    overridenContext['region'] = region
                    break
            break

    # Read the genomes
    if PASS_ARGUMENTS_TO_BLENDER_PYTHON_USING_FILES:    genomes = readGenomesFromFile()
    else: genomes = readGenomesFromArguments()

    # Initialise the plant generation
    turtle = Turtle()
    turtleRenderer = TurtleRenderer()
    renderManager = PlantRenderManager()

    # Shared Turtle and TurtleRenderer parameters (not depending on genomes)
    turtle.lengthNoise = 0.2
    turtle.angleNoise = 0.2
    turtleRenderer.limitDrawing = False
    turtleRenderer.showSkin = True
    turtleRenderer.showLeaves = True
    turtleRenderer.randomize_details = False    # No randomization, the details will be chosen by the genome

    # Draw the plants from the genomes
    if VERBOSE: print("Starting plant rendering...")
    i = 0
    for genome in genomes:
        if VERBOSE: print("\n START RENDERING INSTANCE " + str(i))
        if VERBOSE: print("\nRendering genome " + str(genome))
        genetic_instance = GeneticInstance(ParametricLSystem())
        genetic_instance.fromGenomeRepresentation(genome)

        if VERBOSE: print("Rendering instance: " + str(genetic_instance))
        filename = GeneticInstance.genomeToFilename(genome)
        renderManager.renderGeneticInstances(overridenContext,turtle,turtleRenderer,[genetic_instance],overridenContext)
        exportToPng(overridenContext,scene,PNG_OUTPUT_PATH,filename,overridenContext)
        i+=1
    if VERBOSE: print("Finished plant rendering.")

    if QUIT_BLENDER_AT_END_OF_GENERATION: bpy.ops.wm.quit_blender()

def readGenomesFromFile():
    genomes = []
    f = open(GENOMES_TO_RENDER_FILE,'r')
    for line in f:
        genomes.append(line)
    f.close()
    return genomes

def readGenomesFromArguments():
    args = sys.argv  # this grab all params passed to blender
    genomes =  args[-1].split(" ")
    del genomes[0] # The '--'
    return genomes

# This makes the load handlers work in command line mode. We need the post_load handler to make sure the context is ready before using it.
# http://blenderartists.org/forum/showthread.php?233979-how-to-run-bpy-app-handlers-load_post-every-time-after-file-loaded&p=2332342#post2332342
def call_load_handlers(dummy):
    if VERBOSE: print ("Calling load handlers")
    context = bpy.context
    scene = context.scene
    bpy.app.handlers.scene_update_pre.remove(call_load_handlers)
    for func in bpy.app.handlers.load_pre:
        func(scene, context)
    for func in bpy.app.handlers.load_post:
        func(scene, context)
bpy.app.handlers.load_post.append(do_generate_image)
bpy.app.handlers.scene_update_pre.append(call_load_handlers)
if VERBOSE: print ("Handlers initialised")
