import blender.operators.abstractoperatorlsystem
import procedural.geneticevolver

import imp
imp.reload(blender.operators.abstractoperatorlsystem)
imp.reload(procedural.geneticevolver)

from blender.operators.abstractoperatorlsystem import *
from procedural.geneticevolver import *

class OBJECT_OT_EvolveLSystem(OBJECT_OT_AbstractOperatorLSystem):
    """
    Evolve a LSystem using automatic evolution with a pre-made fitness function.
    """
    bl_idname = "object.evolve_l_system"
    bl_label = "Evolve L-System"
    bl_description = "Evolve a L-System"

    def execute(self, context):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()

        evolver = GeneticEvolver(self.tree_creator.turtle)
        evolver.discardEmptyEvolutions = False
        evolver.setGenerator(self.generator)

        if self.tree_creator.evo_startFromCurrentInstance: evolver.setStartingInstance(self.current_genetic_instance)
        else: evolver.removeStartingInstance()

        evolver.evolve(self.tree_creator.evo_population_size,
            nIterations = self.tree_creator.evo_iterations,
            targetFitness = self.tree_creator.evo_target_fitness)

        self.current_genetic_instance = evolver.getBestInstance()

        fromGeneticInstanceToBlender(self.tree_creator,context,self.current_genetic_instance)

        return {'FINISHED'}
