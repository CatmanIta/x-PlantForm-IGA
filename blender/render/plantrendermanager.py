"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import bpy
from mathutils import Vector

import blender.utilities
import imp
imp.reload(blender.utilities)
from blender.utilities import *

class PlantRenderManager:
    """
    Class that helps in rendering pL-systems in Blender
    """
    def __init__(self):
        pass

    def renderGeneticInstances(self, context, turtle, turtleRenderer, instances, overridenContext = None):
        """
        Renders a set of genetic instances into 3D meshes.
        Handles scene setup and instance distribution.
        """
        # Setup Scene
        clearScene(context)
        callOperator(bpy.ops.view3d.snap_cursor_to_center, overridenContext)

        # Setup instances variables
        # TODO: Add 'name' to the lsystems/pstrings/specific structs holding the pstrings, so that I can name them in blender and for the save files
        offsets = []
        suffixes = []
        i = 0
        for inst in instances:
            offsets.append((i,i,0))
            suffixes.append("_instance_"+str(i+1))
            i+=1

        # Render all instances
        nInstances = 1 if len(instances) > 1 else turtleRenderer.nInstances # nInstances used only if we are drawing one instance
        results = []
        for i in range(len(instances)):
            new_results = self.renderGeneticInstanceNTimes(context, turtle, turtleRenderer, instances[i], nInstances = nInstances, offset=offsets[i],suffix=suffixes[i],overridenContext = overridenContext)
            results.extend(new_results)
        return results

    def renderGeneticInstanceNTimes(self, context, turtle, turtleRenderer, instance, nInstances = 1, renderResult = True, offset = (0,0,0), suffix = "", exportedStatisticsContainer = None, overridenContext = None):
        """
        Renders a single instance multiple times.
        @return: A list of TurtleResult, one for each created instance.
        """
        #print("Rendering genetic instance " + str(instance))

        # Load render parameters
        turtle.loadParameters(instance.turtleParameters)
        turtleRenderer.loadParameters(instance.turtleParameters)
        multipleInstances = nInstances > 1

        # Render
        results = []
        for instance_index in range(nInstances):
            result = self.renderGeneticInstance(context, turtle, turtleRenderer, instance, instance_index, multipleInstances, renderResult, offset, suffix, exportedStatisticsContainer, overridenContext)
            results.append(result)
        return results

    def renderGeneticInstance(self, context, turtle, turtleRenderer, instance, instance_index, multipleInstances = False, renderResult = True, offset = (0,0,0), suffix = "", exportedStatisticsContainer = None, overridenContext = None):
        """
        Renders a single genetic instance, once.
        @return: A single TurtleResult
        """
        structureString = str(instance.lsystem.getResultPString())
        #print("\n\nIT:" + str(instance.lsystem.niterations))
        result = turtle.draw(structureString,instance_index,exportedStatisticsContainer)
        if renderResult:
            turtleRenderer.drawMesh(context, result, offset,suffix, multipleInstances = multipleInstances, overridenContext = overridenContext)
        return result
