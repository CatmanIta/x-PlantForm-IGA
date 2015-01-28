import blender.operators.abstractoperatorlsystem

import imp
imp.reload(blender.operators.abstractoperatorlsystem)

from blender.operators.abstractoperatorlsystem import *

class OBJECT_OT_RandomizeLogicallyLSystem(OBJECT_OT_AbstractOperatorLSystem):
    """ Randomize a LSystem logically """
    bl_idname = "object.randomize_l_system_logically"
    bl_label = "Randomize L-System logically"
    bl_description = "Randomize a L-System logically"

    def execute(self, context):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()
        self.generator.logicallyRandomize()
        fromGeneticInstanceToBlender(self.tree_creator,context,self.current_genetic_instance)
        return {'FINISHED'}
