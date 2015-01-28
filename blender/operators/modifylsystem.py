import blender.operators.abstractoperatorlsystem

import imp
imp.reload(blender.operators.abstractoperatorlsystem)

from blender.operators.abstractoperatorlsystem import *

class OBJECT_OT_ModifyLSystem(OBJECT_OT_AbstractOperatorLSystem):
    """ Modify a LSystem """
    bl_idname = "object.modify_l_system"
    bl_label = "Modify L-System"
    bl_description = "Modify a L-System"

    def execute(self, context):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        self.createGenerator()
        self.generator.mutationModify()
        fromGeneticInstanceToBlender(self.tree_creator,context,self.current_genetic_instance)
        return {'FINISHED'}