"""
    This code is shared by all the scripts opened with blender

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import grammar.parametric.parametriclsystem
import procedural.incrementalgenerator
import procedural.geneticevolver
import turtles.turtle
import blender.render.turtlerenderer
import blender.render.plantrendermanager
import blender.utilities
import blender.operators.alloperators
import blender.paths

# For testing with blender, we need to reload modules, because the imports will not be run again if the code changes
import imp
imp.reload(grammar.parametric.parametriclsystem)
imp.reload(procedural.incrementalgenerator)
imp.reload(procedural.geneticevolver)
imp.reload(turtles.turtle)
imp.reload(blender.render.turtlerenderer)
imp.reload(blender.render.plantrendermanager)
imp.reload(blender.utilities)
imp.reload(blender.operators.alloperators)
imp.reload(blender.paths)

from grammar.parametric.parametriclsystem import ParametricLSystem
from procedural.incrementalgenerator import IncrementalGenerator
from procedural.geneticevolver import GeneticEvolver
from turtles.turtle import Turtle
from blender.utilities import *
from blender.render.turtlerenderer import TurtleRenderer
from blender.render.plantrendermanager import PlantRenderManager
from blender.operators.alloperators import *
from blender.paths import *


def unregisterBlenderClass(_class):
    try:
        bpy.utils.unregister_class(_class)
    except Exception as e:  # DO NOT FIX THIS WARNING (needed by Blender)
        print(str(e) + ": " + str(_class))

def registerBlenderClass(_class):
    try:
        bpy.utils.register_class(_class)
    except Exception as e:  # DO NOT FIX THIS WARNING (needed by Blender)
        print(str(e) + ": " + str(_class))