import blender.operators.abstractoperatorlsystem
import blender.utilities

import imp
imp.reload(blender.operators.abstractoperatorlsystem)
imp.reload(blender.utilities)

from blender.operators.abstractoperatorlsystem import *
from blender.utilities import showOnlyThePlantForm,showPlantAndBackground,selectAllPlantforms,exportToPng

class OBJECT_OT_ExportToPng(OBJECT_OT_AbstractOperatorLSystem):
    bl_idname = "object.export_to_png"
    bl_label = "Export PlantForm To Png"
    bl_description = "Export PlantForm To Png"

    #OUTPUT_PATH = "C:/Users/user/Desktop/RewardSystems/PCG/InteractiveEvolutionServer/xplantform/output/png/"

    def execute(self, context):
        OBJECT_OT_AbstractOperatorLSystem.execute(self,context)
        filePath = os.path.dirname(os.path.realpath(__file__))
        fileName = os.path.basename(filePath)
        folderPath = filePath.replace("\\"+fileName, '')
        outputPath = folderPath + "/../output/png/"

        exportToPng(context,context.scene,outputPath)
        return {'FINISHED'}
