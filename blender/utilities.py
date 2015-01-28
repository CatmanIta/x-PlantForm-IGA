"""
    Utilities to use from inside blender

    @author: Michele Pirovano
    @copyright: 2013-2015
"""
import bpy
from bpy.props import FloatProperty, StringProperty

import procedural.miscellaneous.detailshandler

import imp
imp.reload(procedural.miscellaneous.detailshandler)

from procedural.miscellaneous.detailshandler import DetailsHandler


######################
# Operator utilities
######################

def callOperator(operator, overridenContext = None):
    if overridenContext is None: operator()
    else: operator(overridenContext)

def callOperatorWithAction(operator, action, overridenContext = None):
    if overridenContext is None: operator(action=action)
    else: operator(overridenContext,action=action)

def callOperatorWithAlignActive(operator, align_active, overridenContext = None):
    if overridenContext is None: operator(align_active=align_active)
    else: operator(overridenContext,align_active=align_active)

def exportToPng(context, scene, output_path, plant_name = "test", overridenContext = None):
    # We want to show the plants, ready for rendering
    showPlantAndBackground(scene)
    selectAllPlantforms(scene)

    if overridenContext is not None:        user_preferences = context['user_preferences']
    else:                                   user_preferences = context.user_preferences

    old_smooth_view_value = user_preferences.view.smooth_view
    user_preferences.view.smooth_view = 0

    callOperator(bpy.ops.view3d.view_selected,overridenContext)
    callOperator(bpy.ops.view3d.camera_to_view,overridenContext)
    #callOperatorWithAction(bpy.ops.object.select_all,'DESELECT',overridenContext)

    bpy.data.scenes["Scene"].render.filepath = output_path + plant_name + ".png" #'Plant_%d.png' % scene.frame_current
    bpy.ops.render.render(write_still=True)

    # We restore the view
    #callOperatorWithAlignActive(bpy.ops.view3d.viewnumpad,True,overridenContext)
    #showOnlyThePlantForm(scene)
    user_preferences.view.smooth_view = old_smooth_view_value

####################
# Scene handling
####################

def selectAllPlantforms(scene):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if "PlantForm" in obj.name:
            obj.select = True

def showOnlyThePlantForm(scene):
    for i in range(20): scene.layers[i] = True if i==1 else False

def showPlantAndBackground(scene):
    for i in range(20): scene.layers[i] = True if i in (1,2) else False

def clearScene(context):
    if isinstance(context, dict):
        #print(context['scene'])
        scene = context['scene']
        mode = context['mode']
    else:
        #print(context.scene)
        scene = context.scene
        mode = context.mode

    showOnlyThePlantForm(scene)

    if mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')

    for obj in bpy.data.objects:
        if obj.select:
            #print("DELETING " + str(obj))
            scene.objects.active = obj
            bpy.ops.object.delete(use_global=False)

def listSceneObjects(context):
    print("\nCurrent objects:")
    for o in context.scene.objects:
        print(o.name + " Selected? " + str(o.select))

####################
# GUI Integration
####################

def iterateOverDefines(tree_creator):
    return [('defn' + str(i+1), 'defv' + str(i+1)) for i in range(tree_creator.ndefines)]

def iterateOverProductions(tree_creator):
    return [('pre' + str(i+1), 'cond' + str(i+1), 'sub'+str(i+1)) for i in range(tree_creator.nproductions)]

def updateDefinesGui(self,context):
    """ Called when the number of defines is updated """
    for (def_name,def_value) in iterateOverDefines(self):

        try:
            getattr(self,def_name)
        except AttributeError:
            setattr(self.__class__, def_name,
                StringProperty(
                 name = def_name,
                 description = "the defined parameter name")
                )

        try:
            getattr(self,def_value)
        except AttributeError:
            setattr(self.__class__, def_value,
                FloatProperty(
                 name = def_value,
                 description = "the defined parameter value")
                )

def updateProductionsGui(self,context):
    """ Called when the number of productions is updated """
    #print(self.nproductions)
    for (namep,namec,names) in iterateOverProductions(self):

        try:
            getattr(self,namep)
        except AttributeError:
            setattr(self.__class__, namep,
                StringProperty(
                 name = namep,
                 description = "the precedent string")
                )

        try:
            getattr(self,namec)
        except AttributeError:
            setattr(self.__class__, namec,
                StringProperty(
                 name = namec,
                 default= "*",
                 description = "the condition string")
                )
        try:
            getattr(self,names)
        except AttributeError:
            setattr(self.__class__, names,
                StringProperty(
                 name = names,
                 description = "the replacement string")
                )


def fromBlenderToGeneticInstance(tree_creator, genetic_instance):
    """ Writes the current Tree Creator parameters to the GeneticInstance """

    # LSystem part
    genetic_instance.lsystem.clear()
    genetic_instance.lsystem.setIterations(tree_creator.iterations)

    # NOTE: it is important that the defines are created before the productions or the axioms, so they can be used by them
    for (def_name,def_value) in iterateOverDefines(tree_creator):
        if not getattr(tree_creator,def_name) is "":
            genetic_instance.lsystem.addGlobalDefine(getattr(tree_creator,def_name),getattr(tree_creator,def_value))

    genetic_instance.lsystem.setAxiomFromString(tree_creator.axiom)

    for (namep,namec,names) in iterateOverProductions(tree_creator):
        if not getattr(tree_creator,namep) is "" and not getattr(tree_creator,namep) is "":
            rule = getattr(tree_creator,namep)+":"+getattr(tree_creator,namec)+"->"+getattr(tree_creator,names)
            genetic_instance.lsystem.addProductionFromString(rule)

    # Turtle parameters part
    tp = genetic_instance.turtleParameters
    tp.branch_radius = tree_creator.defaultRadius
    tp.tropism_susceptibility = tree_creator.tropism_susceptibility
    tp.use_canopy = tree_creator.canopy
    tp.details_scale = tree_creator.details_scale
    tp.trunk_material_choice = DetailsHandler.indexOfMaterial(tree_creator.trunk_material)
    tp.leaf_material_choice = DetailsHandler.indexOfMaterial(tree_creator.leaf_material)
    tp.leaf_choice =  DetailsHandler.indexOfLeafModel(tree_creator.leaf_object_name)
    tp.bulb_choice =  DetailsHandler.indexOfBulbModel(tree_creator.bulb_object_name)
    tp.flower_choice =  DetailsHandler.indexOfFlowerModel(tree_creator.flower_object_name)
    tp.fruit_choice =  DetailsHandler.indexOfFruitModel(tree_creator.fruit_object_name)

    #TODO: SHOULD USE ALL THE TURTLE PARAMETERS THAT CAN BE CHANGED!!!!!


# TODO: should also consider additional Turtle parameters
def fromGeneticInstanceToBlender(tree_creator, context, genetic_instance):
    """ Reads all the current Tree Creator parameters from the LSystem instance """

    # LSystem part
    tree_creator.iterations = genetic_instance.lsystem.niterations
    tree_creator.nproductions = len(genetic_instance.lsystem.productions)
    tree_creator.ndefines = len(genetic_instance.lsystem.globalDefines)

    tree_creator.axiom = str(genetic_instance.lsystem.axiom)

    updateDefinesGui(tree_creator,context)
    updateProductionsGui(tree_creator,context)

    i = 0
    keys = list(genetic_instance.lsystem.globalDefines.keys())
    values = list(genetic_instance.lsystem.globalDefines.values())
    for (def_name,def_value) in iterateOverDefines(tree_creator):
        # TODO: CHECK THIS!!!! THEY ARE IN A DICTIONARY! NOT ORDERED!
        setattr(tree_creator,def_name,str(keys[i]))
        setattr(tree_creator,def_value,values[i])
        i+=1

    i = 0
    productions = genetic_instance.lsystem.productions
    for (namep,namec,names) in iterateOverProductions(tree_creator):
        setattr(tree_creator,namep,str(productions[i].predecessor))
        setattr(tree_creator,namec,str(productions[i].condition))
        setattr(tree_creator,names,str(productions[i].successor))
        i+=1

    # Turtle parameters part
    tp = genetic_instance.turtleParameters
    tree_creator.defaultRadius = tp.branch_radius
    tree_creator.tropism_susceptibility = tp.tropism_susceptibility
    tree_creator.canopy = tp.use_canopy
    tree_creator.details_scale = tp.details_scale
    #print(tp.trunk_material_choice)
    tree_creator.trunk_material = DetailsHandler.nameOfMaterial(tp.trunk_material_choice)
    #print(tree_creator.trunk_material)
    tree_creator.leaf_material = DetailsHandler.nameOfMaterial(tp.leaf_material_choice)
    tree_creator.leaf_object_name = DetailsHandler.nameOfLeafModel(tp.leaf_choice)
    tree_creator.bulb_object_name = DetailsHandler.nameOfBulbModel(tp.bulb_choice)
    tree_creator.flower_object_name = DetailsHandler.nameOfFlowerModel(tp.flower_choice)
    tree_creator.fruit_object_name = DetailsHandler.nameOfFruitModel(tp.fruit_choice)

