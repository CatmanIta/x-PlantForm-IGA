import blender.operators.abstractoperatorlsystem
import procedural.geneticevolver

import imp
imp.reload(blender.operators.abstractoperatorlsystem)
imp.reload(procedural.geneticevolver)

from blender.operators.abstractoperatorlsystem import *
from procedural.geneticevolver import *


class OBJECT_OT_AbstractEvoIntChooser(OBJECT_OT_AbstractOperatorLSystem):

    def execute(self, context, choice_index):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()

        evolver = GeneticEvolver(self.tree_creator.turtle)
        evolver.discardEmptyEvolutions = True
        evolver.setGenerator(self.generator)

        # We disable the standard render
        self.tree_creator.renderCurrentLSystemAtExecution = False

        options_number = self.tree_creator.evoint_options_number

        # We choose the instance
        selected_instance = self.tree_creator.evoInt_population[choice_index-1]

        # The selection size is just 1, done by the user
        to_mutate_pop = [selected_instance]

        # We mutate it N-1 times
        mutated_pops = []
        for i in range(options_number-1):
            mutated_pops.extend(evolver.mutate(to_mutate_pop))

        # We obtain N instances
        population = []
        population.extend(to_mutate_pop)
        population.extend(mutated_pops)
        print(population)

        # This will be the new population
        self.tree_creator.evoInt_population = population

        # We render the population, passing it to the main operator
        #bpy.types.Scene.to_draw_instances = []
        i = 0
        for p in population:
            i+=1
            #lsystem = p.lsystem
            #pString = lsystem.iterate()
            bpy.types.Scene.to_draw_instances.append(p)

        # We set the current L-System gui to the one we have selected
        fromGeneticInstanceToBlender(self.tree_creator,context,self.current_genetic_instance)



class OBJECT_OT_EvoIntChoose1(OBJECT_OT_AbstractEvoIntChooser):
    bl_idname = "object.evoint_choose_1"
    bl_label = "EvoInt Choose 1"
    bl_description = "EvoInt Choose 1"
    def execute(self, context):
        OBJECT_OT_AbstractEvoIntChooser.execute(self,context,1)
        return {'FINISHED'}

class OBJECT_OT_EvoIntChoose2(OBJECT_OT_AbstractEvoIntChooser):
    bl_idname = "object.evoint_choose_2"
    bl_label = "EvoInt Choose 2"
    bl_description = "EvoInt Choose 2"
    def execute(self, context):
        OBJECT_OT_AbstractEvoIntChooser.execute(self,context,2)
        return {'FINISHED'}

class OBJECT_OT_EvoIntChoose3(OBJECT_OT_AbstractEvoIntChooser):
    bl_idname = "object.evoint_choose_3"
    bl_label = "EvoInt Choose 3"
    bl_description = "EvoInt Choose 3"
    def execute(self, context):
        OBJECT_OT_AbstractEvoIntChooser.execute(self,context,3)
        return {'FINISHED'}

class OBJECT_OT_EvoIntChoose4(OBJECT_OT_AbstractEvoIntChooser):
    bl_idname = "object.evoint_choose_4"
    bl_label = "EvoInt Choose 4"
    bl_description = "EvoInt Choose 4"
    def execute(self, context):
        OBJECT_OT_AbstractEvoIntChooser.execute(self,context,4)
        return {'FINISHED'}

class OBJECT_OT_EvoIntChoose5(OBJECT_OT_AbstractEvoIntChooser):
    bl_idname = "object.evoint_choose_5"
    bl_label = "EvoInt Choose 5"
    bl_description = "EvoInt Choose 5"
    def execute(self, context):
        OBJECT_OT_AbstractEvoIntChooser.execute(self,context,5)
        return {'FINISHED'}

class OBJECT_OT_EvoIntChoose6(OBJECT_OT_AbstractEvoIntChooser):
    bl_idname = "object.evoint_choose_6"
    bl_label = "EvoInt Choose 6"
    bl_description = "EvoInt Choose 6"
    def execute(self, context):
        OBJECT_OT_AbstractEvoIntChooser.execute(self,context,6)
        return {'FINISHED'}