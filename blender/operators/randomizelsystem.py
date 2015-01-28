import blender.operators.abstractoperatorlsystem

import imp
imp.reload(blender.operators.abstractoperatorlsystem)

from blender.operators.abstractoperatorlsystem import *

class OBJECT_OT_RandomizeLSystem(OBJECT_OT_AbstractOperatorLSystem):
    """ Randomize a LSystem """
    bl_idname = "object.randomize_l_system"
    bl_label = "Randomize L-System"
    bl_description = "Randomize a L-System"

    def execute(self, context):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()
        self.generator.randomize()
        fromGeneticInstanceToBlender(self.tree_creator,context,self.current_genetic_instance)
        return {'FINISHED'}
