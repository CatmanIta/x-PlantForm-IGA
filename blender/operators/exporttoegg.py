import blender.operators.abstractoperatorlsystem

import imp
imp.reload(blender.operators.abstractoperatorlsystem)

from blender.operators.abstractoperatorlsystem import *

import sys, os

class OBJECT_OT_ExportToEgg(OBJECT_OT_AbstractOperatorLSystem):
    bl_idname = "object.export_to_egg"
    bl_label = "Export To Egg"
    bl_description = "Export To Egg"

    #OUTPUT_PATH = "C:/Users/user/Desktop/RewardSystems/PCG/InteractiveEvolutionServer/xplantform/output/egg/"

    def execute(self, context):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)

        filePath = os.path.dirname(os.path.realpath(__file__))
        fileName = os.path.basename(filePath)
        folderPath = filePath.replace("\\"+fileName, '')
        outputPath = folderPath + "/../output/egg/"

        bpy.ops.object.select_all(action='DESELECT')
        for obj in context.scene.objects:
            if "PlantForm" in obj.name:
                obj.select = True
                bpy.ops.export.panda3d_egg(filepath=outputPath+obj.name+".egg")
                obj.select = False
        return {'FINISHED'}
