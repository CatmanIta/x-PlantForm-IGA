import blender.operators.abstractoperatorlsystem

import imp
imp.reload(blender.operators.abstractoperatorlsystem)

from blender.operators.abstractoperatorlsystem import *

class OBJECT_OT_ResetLSystem(OBJECT_OT_AbstractOperatorLSystem):
    """ Reset a LSystem """
    bl_idname = "object.reset_l_system"
    bl_label = "Reset L-System"
    bl_description = "Reset a L-System"

    def draw(self, context):
        box = self.layout.box()
        box.label(text="Interactive Evolution")

    def execute(self, context):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()
        self.tree_creator.startedInteractiveEvolution = False
        self.generator.resetToSimple()
        fromGeneticInstanceToBlender(self.tree_creator,context,self.current_genetic_instance)
        return {'FINISHED'}


