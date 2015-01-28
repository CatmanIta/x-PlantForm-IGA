import blender.operators.abstractoperatorlsystem

import imp
imp.reload(blender.operators.abstractoperatorlsystem)

from blender.operators.abstractoperatorlsystem import *

class OBJECT_OT_ComplexifyLSystem(OBJECT_OT_AbstractOperatorLSystem):
    """ Complexify a LSystem """
    bl_idname = "object.complexify_l_system"
    bl_label = "Complexify L-System"
    bl_description = "Complexify a L-System"

    def execute(self, context):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()
        self.generator.mutationComplexify()
        fromGeneticInstanceToBlender(self.tree_creator,context,self.current_genetic_instance)
        return {'FINISHED'}

