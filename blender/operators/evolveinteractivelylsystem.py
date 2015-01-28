import blender.operators.abstractoperatorlsystem
import procedural.geneticevolver

import imp
imp.reload(blender.operators.abstractoperatorlsystem)
imp.reload(procedural.geneticevolver)

from blender.operators.abstractoperatorlsystem import *
from procedural.geneticevolver import *

class OBJECT_OT_EvolveInteractivelyLSystem(OBJECT_OT_AbstractOperatorLSystem):
    """ Evolve interactively a LSystem """
    bl_idname = "object.evolve_interactively_l_system"
    bl_label = "Evolve Interactively a L-System"
    bl_description = "Evolve Interactively a L-System"

    def execute(self, context):
        """ Generate the initial population for the user to select """
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()

        self.tree_creator.startedInteractiveEvolution = True

        evolver = GeneticEvolver(self.tree_creator.turtle)
        evolver.discardEmptyEvolutions = True
        evolver.setGenerator(self.generator)

        # We remove the standard render
        self.tree_creator.renderCurrentLSystemAtExecution = False

        # Limited population size, since we show it to the user
        population_size = self.tree_creator.evoint_options_number

        if self.tree_creator.evo_startFromCurrentInstance: evolver.setStartingInstance(self.current_genetic_instance)
        else: evolver.removeStartingInstance()

        population = evolver.generatePopulation(population_size)

        # We also save the population
        self.tree_creator.evoInt_population = population

        # We render the population, passing it to the main operator
        # Note that this operator cannot draw directly, it needs the main operator!
        #bpy.types.Scene.to_draw_lsystems = []
        for p in population:
            #lsystem = p.lsystem
            #pString = lsystem.iterate()
            bpy.types.Scene.to_draw_instances.append(p)

        return {'FINISHED'}
