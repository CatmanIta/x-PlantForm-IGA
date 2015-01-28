import blender.operators.abstractoperatorlsystem
import procedural.geneticevolver

import imp
imp.reload(blender.operators.abstractoperatorlsystem)
imp.reload(procedural.geneticevolver)

from blender.operators.abstractoperatorlsystem import *
from procedural.geneticevolver import *

class OBJECT_OT_EvolveLSystemModal(OBJECT_OT_AbstractOperatorLSystem):
    """
    Evolve a LSystem using a Modal operator.
    A Modal operator keeps running and updates the view while it runs.
    It is useful for run-time / continuous operations.
    """
    bl_idname = "object.evolve_l_system_modal"
    bl_label = "Evolve L-System Modal"
    bl_description = "Evolve a L-System Modal"

    _timer = None
    _modal_delta_time = 1.0             # Timer at which to advance the modal operator (perform one step)

    DRAW_WHOLE_GENERATION = False        # This will draw ALL the instances of this generation. Will be VERY slow!

    DRAW_WITH_GENERATION_PERIOD = True    # Do we draw every N generations, or when the fitness changes?
    GENERATION_DRAW_PERIOD = 5     # We draw every N generations

    DRAW_WITH_FITNESS_PERIOD = not DRAW_WITH_GENERATION_PERIOD
    FITNESS_DRAW_PERIOD = 5         # We draw when the fitness is at least this large

    RENDER_TO_FILE = False        # We also save the render results to a PNG file

    def __init__(self):
        print("Start evolving")

    def __del__(self):
        print("Evolution complete")

    def invoke(self, context, event):
        self.target_draw_fitness = 0
        context.scene.frame_current = 1
        self._count = 0

        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()

        self.evolver = GeneticEvolver(self.tree_creator.turtle)
        self.evolver.discardEmptyEvolutions = False
        self.evolver.setGenerator(self.generator)

        if self.tree_creator.evo_startFromCurrentInstance: self.evolver.setStartingInstance(self.current_genetic_instance)
        else: self.evolver.removeStartingInstance()

        self.population = self.evolver.generatePopulation(self.tree_creator.evo_population_size)
        print("Starting Modal Evolution with instances:")
        self.evolver.listInstances()

        self.execute(context)
        self._timer = context.window_manager.event_timer_add(self._modal_delta_time, context.window)   # Create a new timer
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        print("Executing step: " + str(self._count))
        self._count += 1
        self.population = self.evolver.evolveStep(self.population)
        self.current_genetic_instance = self.evolver.getBestInstance()
        fromGeneticInstanceToBlender(self.tree_creator,context,self.current_genetic_instance)
        self.render(context)

        self.evolver.listInstances()

    def render(self,context):
        best_fitness = self.evolver.getBestInstance().fitness
        reached_target_fitness = False
        if best_fitness > self.target_draw_fitness:
            reached_target_fitness = True
            while True:
                self.target_draw_fitness += self.FITNESS_DRAW_PERIOD
                if self.target_draw_fitness > best_fitness: break

        willRender = (self.DRAW_WITH_GENERATION_PERIOD and self._count % self.GENERATION_DRAW_PERIOD == 0) \
                or (self.DRAW_WITH_FITNESS_PERIOD and reached_target_fitness) \
                or (not self.DRAW_WITH_GENERATION_PERIOD and not self.DRAW_WITH_FITNESS_PERIOD)

        context.area.header_text_set("Generation " + str(self._count) + " fitness: " + str(self.evolver.getBestInstance().fitness) +  " best instance: " + str(self.current_genetic_instance.lsystem.getResultPString()))

        if willRender:
            context.scene.frame_current += 1
            if self.DRAW_WHOLE_GENERATION:
                for p in self.population:
                    bpy.types.Scene.to_draw_instances.append(p)
            self.tree_creator.renderManager.renderGeneticInstances(context,
                                                          self.tree_creator.turtle,
                                                          self.tree_creator.turtleRenderer,
                                                          bpy.types.Scene.to_draw_instances
                                                          )

            bpy.types.Scene.to_draw_instances = [] # Reset the to-be-drawn array
            if self.RENDER_TO_FILE: bpy.ops.object.export_to_png(context)

    def modal(self, context, event):
        # events list: http://www.blender.org/documentation/blender_python_api_2_70_0/bpy.types.Event.html?highlight=event
        #print(event.type)
        if event.type == 'ESC':
            context.window_manager.event_timer_remove(self._timer)
            context.area.header_text_set("Cancelled")
            return {'CANCELLED'}

        if event.type == "ENTER":
            context.window_manager.event_timer_remove(self._timer)
            context.area.header_text_set("Finished")
            return{'RET'}

        if event.type == 'TIMER':
            #print("TIMER! " + str(self._timer.time_delta) + " " + str(self._timer.time_duration) + " " + str(self._timer.time_step))
            self.execute(context)
            return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}