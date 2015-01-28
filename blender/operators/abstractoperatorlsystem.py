import procedural.plantsincrementalgenerator
#import procedural.incrementalgenerator
import blender.utilities

import imp
imp.reload(procedural.plantsincrementalgenerator)
#imp.reload(procedural.incrementalgenerator)
imp.reload(blender.utilities)

from procedural.plantsincrementalgenerator import PlantsIncrementalGenerator
#from procedural.incrementalgenerator import IncrementalGenerator
from blender.utilities import *

import bpy

class OBJECT_OT_AbstractOperatorLSystem(bpy.types.Operator):

    def execute(self, context):
        self.tree_creator = bpy.types.Scene.tree_creator
        self.current_genetic_instance = bpy.types.Scene.current_genetic_instance
        return {'FINISHED'}

    def createGenerator(self):
        # Parameters that are not saved in the genetic instance (common for all instances)
        parameterized = getattr(self.tree_creator,'parameterized')

        #TODO: The generator could be created only ONCE for all operators, and is not used by all of them!
        #self.generator = IncrementalGenerator(
        self.generator = PlantsIncrementalGenerator(
                parameterized = parameterized,
                definesProbability = getattr(self.tree_creator,'defines_probability'),
                constantsProbability = 1#getattr(self.tree_creator,'constants_probability')
            )
        self.generator.setLSystem(self.current_genetic_instance.lsystem)
        self.generator.targetIterations = getattr(self.tree_creator,'target_iterations')
        self.generator.branchProbability = getattr(self.tree_creator,'branch_probability')
        self.generator.mutation_steps_at_once = getattr(self.tree_creator,'mutation_steps')

