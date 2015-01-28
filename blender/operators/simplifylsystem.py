import blender.operators.abstractoperatorlsystem

import imp
imp.reload(blender.operators.abstractoperatorlsystem)

from blender.operators.abstractoperatorlsystem import *

class OBJECT_OT_SimplifyLSystem(OBJECT_OT_AbstractOperatorLSystem):
    """ Simplify a LSystem """
    bl_idname = "object.simplify_l_system"
    bl_label = "Simplify L-System"
    bl_description = "Simplify a L-System"

    def execute(self, context):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()
        self.generator.mutationSimplify()
        fromGeneticInstanceToBlender(self.tree_creator,context,self.current_genetic_instance)
        return {'FINISHED'}

