"""
    This defines the operator that performs Blender integration with the generator.
    This is opened using the Blender script editor and run by it!

    @note: The Blender operator code needs to be here to function properly.
    I cannot create a separate module with the operator as a class or Blender won't see it!

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

# START INTEGRATION CODE
# This code needs to be called by -any- script loaded with blender that uses x-plantform
import sys, os
filePath = os.path.dirname(os.path.realpath(__file__))
fileName = os.path.basename(filePath)
classesPath = filePath.replace("\\blender\\"+fileName, '')
if not classesPath in sys.path: sys.path.append(classesPath)

import blender.scriptsharedcode
import imp
imp.reload(blender.scriptsharedcode)
from blender.scriptsharedcode import *
# END INTEGRATION CODE

# Loading additional utilities
import blender.plantform_blender_integration_utilities
imp.reload(blender.plantform_blender_integration_utilities)
from blender.plantform_blender_integration_utilities import *

VERBOSE = False


import bpy
from bpy.props import FloatVectorProperty, FloatProperty, BoolProperty, IntProperty, StringProperty
from bpy.types import Operator

bl_info = {
 "name": "X-PlantForm Generator",
 "author": "Michele Pirovano",
 "version": (1, 0, 0),
 "blender": (2, 6, 6),
 "location": "View3D > Tools > Add PlantForm",
 "description": "Generates 3D Toon Trees",
 "warning": "",
 "wiki_url": "",
 "tracker_url": "",
 "category": "Add Mesh"}

"""
# This code will add PlantForm to the Tool shelf
class PANEL_AddPlantForm(bpy.types.Panel):
    bl_id_name = "object.add_plant_form_operator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Add PlantForm"
    def draw(self, context):
        col = self.layout.column(align = True)
        col.operator("object.add_plantform", text = "Add PlantForm")
"""

# This code will add PlantForm as a Blender Operator
class OBJECT_OT_AddPlantForm(bpy.types.Operator):
    """
    Add a PlantForm object
    """
    bl_idname = "object.add_plantform"
    bl_label = "Add PlantForm"
    bl_description = "Create a new PlantForm Object"
    bl_options  = {'REGISTER', 'UNDO', 'PRESET'}
    # Note: with REGISTER it will work as a GUI panel
    # http://en.wikibooks.org/wiki/Blender_3D:_Noob_to_Pro/Advanced_Tutorials/Python_Scripting/Object,_Action,_Settings

    # Parametric properties
    iterations = IntProperty(name="iterations",
                            default = 1,min = 1,max = 20,
                            description="number of iterations of the LSystem")

    axiom = StringProperty(name='axiom',default="F+F-F",
                        description="Legend for the axiom:"
                         +"  F -> go forward 1 step"
                         +"  + -> Rotate around +X"
                         +"  - -> Rotate around -X"
                         +"  & -> Rotate around +Z"
                         +"  ^ -> Rotate around -Z"
                         +"  \ -> Rotate around +Y"
                         +"  / -> Rotate around -Y")

    nproductions = IntProperty(name = "productions",
       default = 0,min = 0,max = 10,
       update = updateProductionsGui,
       description="number of rules for the LSystem")

    ndefines = IntProperty(name = "defines",
       default = 0,min = 0,max = 10,
       update = updateDefinesGui,
       description="number of defined parameters" )

    angle = FloatProperty(name="angle",default=30,min=-180,max=180,description="default angle for rotations")
    angle_noise = FloatProperty(name="angle_noise",
       default=0.2,
       min=0,
       max=1,
       description="noise added to rotation angles")

    step = FloatProperty(name="step",
       default=0.5,
       min=0.1,
       max=5,
       description="default length of a forward edge")
    step_noise = FloatProperty(name="step_noise",
       default=0.2,
       min=0,
       max=1,
       description="noise added to the step length")

    seed = IntProperty(name="seed",
                       default=1987,
                       min=0,
                       description="seed to use for randomization")

    nInstances = IntProperty(name="nInstances",
                             default=1,
                             min=1,
                             max=10,
                             description="number of plant instances to create")

    tropism = FloatVectorProperty(name="tropism",default=(0,0,-1))
    tropism_susceptibility = FloatProperty(name="bending",
        default=0.22,
        min=0,
        max=1)

    elasticity_from_radius = BoolProperty(name='elasticity / radius',default=False)

    # Mesh
    skin = BoolProperty(name='skin',
                        default=True,
                        description="applies a skin to the tree body")
    fastSkin = BoolProperty(name='fast skin',
                            default=True,
                            description="the skinning is made more performant")
    defaultRadius = IntProperty(name='radius',
                                default=3,min=1,max=50,
                                description='default branch radius')
    leaves = BoolProperty(name='leaves',
                          description="renders leaves and other details",
                          default=True)
    canopy = BoolProperty(name='canopy',
                          description = "renders canopy around leaves",
                          default=False)
    simplify = BoolProperty(name='simplify',
                            default=False)
    metaBallRadius = FloatProperty(name='canopy radius',
                                   default=0.2,min=0.1,max=5)
    showGrowth = BoolProperty(name='showGrowth',
                              description = "renders the growth of the plant",
                              default=False)

    # Details and texture
    leaf_object_name = StringProperty(name="leaf",
                                      default="Leaf_Texture")
    bulb_object_name = StringProperty(name="bulb",
                                      default="Leaf_Heart")
    flower_object_name = StringProperty(name="flower",
                                        default="Flower_Gerbera")
    fruit_object_name = StringProperty(name="fruit",
                                       default="Fruit_Apple")
    details_scale = FloatProperty(name="leaves scale",
                                  default=1,min=0.1,max=2)

    trunk_material = StringProperty(name="trunk_material",
                                    default="Material.Trunk")
    leaf_material = StringProperty(name="leaf_material",
                                   default="Material.Leaf")

    # Generation Properties
    target_iterations = IntProperty(name='target_iterations',
                                    default=5,min=1,max=10)
    branch_probability = FloatProperty(name='branch_probability',
                                       default=0.4,min=0.0,max=1.0,step=10)
    parameterized = BoolProperty(name='parameterized',
                                 default=True)
    defines_probability = FloatProperty(name='defines_probability',
                                        default=0.0,min=0.0,max=1.0,step=10)
    #constants_probability = FloatProperty(name='constants_probability',default=0.0,min=0.0,max=1.0,step=10)
    mutation_steps = IntProperty(name='mutation_steps',
                                 default=5,min=1,max=10)

    # Evolution Properties
    evo_population_size = IntProperty(name='evo_population_size',
                                      default=20,min=1,max=2000)
    #evo_selection_size = IntProperty(name='evo_selection_size',
    #                                 default=6,min=1,max=200)
    evo_iterations = IntProperty(name='evo_iterations',
                                 default=5,min=1,max=50)
    evo_target_fitness = IntProperty(name='evo_target_fitness',
                                     default=10,min=0,max=1000)
    evo_startFromCurrentInstance = BoolProperty(name='evolve current',
                                                default=False)

    ############
    #---Flags
    ############

    # Flag that tells whether we will render or not at each execution of this operator
    renderAtExecution = True

    # Interactive Evolution
    startedInteractiveEvolution = False
    evoint_options_number = 3

    ############
    #---GUI
    ############

    def draw(self, context):
        # @note: Passes self to a Scene variable so that other operators can access it
        bpy.types.Scene.tree_creator = self

        self.drawEvolutionGui(context)
        self.drawInteractiveEvolutionGui(context)
        self.drawLSystemGui(context)
        self.drawGenerationGui(context)
        self.drawRenderingGui(context)

    def drawEvolutionGui(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Evolution")
        box.prop(self, 'target_iterations')
        box.prop(self, 'branch_probability')
        box.prop(self, 'parameterized')
        box.prop(self, 'defines_probability')
        #box.prop(self, 'constants_probability')
        box.prop(self, 'mutation_steps')
        box.prop(self, 'evo_population_size')
        #box.prop(self, 'evo_selection_size')
        box.prop(self, 'evo_iterations')
        box.prop(self, 'evo_target_fitness')
        box.prop(self, 'evo_startFromCurrentInstance')

        row = box.row(align=True)
        row.operator("object.simplify_l_system", text = "Simplify")
        row.operator("object.modify_l_system", text = "Modify")
        #row = box.row(align=True)
        row.operator("object.complexify_l_system", text = "Complexify")
        row = box.row(align=True);  row.operator("object.evolve_l_system", text = "Auto-Evolve")
        row = box.row(align=True);  row.operator("object.evolve_l_system_modal", text = "Evolve Modal")

    def drawInteractiveEvolutionGui(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Interactive Evolution")

        if self.startedInteractiveEvolution:
            start_text = "Restart IntEvo"
        else:
            start_text = "Start IntEvo"

        row = box.row(align=True);
        row.operator("object.evolve_interactively_l_system", text = start_text)

        row = box.row(align=True);
        row.active = self.startedInteractiveEvolution
        row.operator("object.evoint_choose_1", text = "1")
        row.operator("object.evoint_choose_2", text = "2")
        row.operator("object.evoint_choose_3", text = "3")

    def drawLSystemGui(self,context):
        layout = self.layout
        box = layout.box()
        box.label(text="L-System")

        row = box.row(align=True);  row.operator("object.reset_l_system", text = "Reset")
        row = box.row(align=True);  row.operator("object.randomize_l_system", text = "Randomize")
        row = box.row(align=True);  row.operator("object.randomize_l_system_logically", text = "Logic Randomize")

        row = box.row(align=False)
        box.prop(self,'iterations')

        row = box.row(align=False)
        row.label(text="Result: " +str(bpy.types.Scene.current_genetic_instance.lsystem.getResultPString()))

        if getattr(self,'axiom')=='':
            box.alert=True
        box.prop(self, 'axiom')

        box.prop(self, 'nproductions')
        not_complete = True
        for i in range(self.nproductions):
            namep = 'pre' + str(i+1)
            namec = 'cond' + str(i+1)
            names = 'sub' + str(i+1)
            #box = layout.box()

            not_complete = (getattr(self,namep) == '' or getattr(self,names) == '')

            split = box.split(0.15)
            split.alert = not_complete
            split.prop(self,namep,text="")
            split = split.split(0.2)
            split.alert = not_complete
            split.prop(self,namec,text="")
            split.prop(self,names,text="")

        box.prop(self, 'ndefines')
        for i in range(self.ndefines):
            def_name = 'defn' + str(i+1)
            def_value = 'defv' + str(i+1)

            row = box.row(align=True)
            if getattr(self,def_name) == '':
                row.alert=True
            row.prop(self,def_name,text="")
            row.prop(self,def_value,text="")

    def drawGenerationGui(self,context):
        layout = self.layout
        box = layout.box()
        box.label(text="Generation")
        box.prop(self, 'angle')
        box.prop(self, 'angle_noise')
        box.prop(self, 'step')
        box.prop(self, 'step_noise')
        box.prop(self, 'seed')
        box.prop(self, 'tropism')
        box.prop(self, 'tropism_susceptibility')
        box.prop(self, 'elasticity_from_radius')

    def drawRenderingGui(self,context):
        layout = self.layout
        box = layout.box()
        box.label(text="Rendering")
        box.prop(self, 'nInstances')
        row = box.row(align=True)
        row.prop(self, 'skin')
        row.prop(self, 'fastSkin')
        row.prop(self,'simplify')
        row.prop(self, 'defaultRadius')
        row = box.row(align=True)
        row.prop(self, 'leaves')
        row.prop(self,'details_scale')
        row = box.row(align=True)
        row.prop(self, 'canopy')
        row.prop(self,'metaBallRadius')
        row = box.row(align=True)
        row.prop(self,'showGrowth')

        # This lets me select objects in the scene
        # @note: Note that we cannot change the objects' names, however! This is a Blender limitation.
        row = box.row(align=True)
        row.prop_search(
          data = self,
          property = "leaf_object_name",
          search_data = context.scene,
          search_property = "objects",
          text = "Leaf")

        row = box.row(align=True)
        row.prop_search(
          data = self,
          property = "bulb_object_name",
          search_data = context.scene,
          search_property = "objects",
          text = "Bulb")

        row = box.row(align=True)
        row.prop_search(
          data = self,
          property = "flower_object_name",
          search_data = context.scene,
          search_property = "objects",
          text = "Flower")

        row = box.row(align=True)
        row.prop_search(
          data = self,
          property = "fruit_object_name",
          search_data = context.scene,
          search_property = "objects",
          text = "Fruit")

        row = box.row(align=True)
        row.prop_search(
          data = self,
          property = "trunk_material",
          search_data = bpy.data,
          search_property = "materials",
          text = "Trunk Material")

        row = box.row(align=True)
        row.prop_search(
          data = self,
          property = "leaf_material",
          search_data = bpy.data,
          search_property = "materials",
          text = "Leaf Material")

        row = box.row(align=True);  row.operator("object.export_to_egg", text = "Export to EGG")
        row = box.row(align=True);  row.operator("object.export_to_png", text = "Export to PNG")


    #####################
    #---Operator methods
    #####################

    # This is called at the first invocation of the operator
    def invoke(self,context,event):
        # Reset what needs to be drawn
        #bpy.types.Scene.to_draw_pstrings = []
        bpy.types.Scene.to_draw_instances = []

        # We define turtles and renderers at the first invocation
        self.turtle = Turtle()
        self.turtleRenderer = TurtleRenderer()
        self.renderManager = PlantRenderManager()

        # Initialization TODO!!
        #bpy.ops.object.reset_l_system()

        self.execute(context)
        return {"FINISHED"}

    # This is called at each modification of any parameter (calling the operator again)
    def execute(self,context):
        #print("EXECUTING MAIN OPERATOR")
        #listSceneObjects(context)

        #TODO: DEPRECATED!! USE THESE ONLY FOR SHARED PARAMETERS THAT DO NOT CHANGE (like skin = true or false)
        # We update the turtles and renderers with the new parameters, selected through the GUI
        self.updateTurtle(context)
        self.updateTurtleRenderer(context)

        # Create a GeneticInstance from the chosen parameters
        genetic_instance = self.createGeneticInstance(context)
        bpy.types.Scene.current_genetic_instance = genetic_instance

        instances = bpy.types.Scene.to_draw_instances
        if self.renderAtExecution:
            if self.showGrowth:
                for i in range(self.iterations):
                    genetic_instance.lsystem.targetIterations = i+1
                    instances.append(genetic_isntance)
                    #instances.append(genetic_instance.lsystem.iterate(i+1))
            else:
                genetic_instance.lsystem.iterations = self.iterations
                instances.append(genetic_instance)
                #pStrings.append(genetic_instance.lsystem.iterate(self.iterations))
        self.renderManager.renderGeneticInstances(context,self.turtle,self.turtleRenderer,instances)
        bpy.types.Scene.to_draw_instances = [] # Empty the list of drawn instances

        # Render all chosen instances # DEPRECATED!!!!!!
        """
        pStrings = bpy.types.Scene.to_draw_pstrings
        if self.renderAtExecution:
            if self.showGrowth:
                for i in range(self.iterations):
                    pStrings.append(genetic_instance.lsystem.iterate(i+1))
            else:
                pStrings.append(genetic_instance.lsystem.iterate(self.iterations))
        #TODO: The renderPStrings should become instead renderGeneticInstance!!!
        # so that it takes the pstring as well as the turtle parameters!!
        #self.renderManager.renderPStrings(context,self.turtle,self.turtleRenderer,pStrings)

        bpy.types.Scene.to_draw_pstrings = [] # Empty the list of drawn pStrings
        """
        self.renderAtExecution = True   # Reset render at execution, so the next time any execution is performed we render the current l-system too
        return {'FINISHED'}

    def createGeneticInstance(self, context):
        """
        Create a GeneticInstance from the GUI parameters
        """
        genetic_instance = GeneticInstance(ParametricLSystem(self.seed))
        fromBlenderToGeneticInstance(self,genetic_instance)
        return genetic_instance

    # TODO: this is deprecated, since the contents of the turtle should already be in the genetic instance!
    def updateTurtle(self,context):
        t = self.turtle

        t.angle = self.angle
        t.step = self.step #/self.iterations, <-- Readd this if we want sizes to be consistent
        t.lengthNoise = self.step_noise
        t.angleNoise = self.angle_noise
        t.randomSeed = self.seed
        t.defaultRadius = self.defaultRadius

        t.tropism = self.tropism
        t.tropism_susceptibility = self.tropism_susceptibility
        t.elasticityDependsOnBranchRadius = self.elasticity_from_radius

    # TODO: this is deprecated, since the contents of the renderer should already be in the genetic instance!
    def updateTurtleRenderer(self,context):
        tr = self.turtleRenderer

        tr.metaBallRadius = self.metaBallRadius
        tr.showSkin = self.skin
        tr.fastSkin = self.fastSkin
        tr.simplify = self.simplify
        tr.showLeaves = self.leaves
        tr.showCanopy = self.canopy
        tr.details_scale = self.details_scale
        tr.nInstances = self.nInstances

        #print(self.leaf_object_name)

        tr.leaf_detail_index = DetailsHandler.indexOfLeafModel(self.leaf_object_name)
        tr.bulb_detail_index = DetailsHandler.indexOfBulbModel(self.bulb_object_name)
        tr.flower_detail_index = DetailsHandler.indexOfFlowerModel(self.flower_object_name)
        tr.fruit_detail_index =  DetailsHandler.indexOfFruitModel(self.fruit_object_name)
        tr.trunk_material_index = DetailsHandler.indexOfMaterial(self.trunk_material)
        tr.leaf_material_index = DetailsHandler.indexOfMaterial(self.leaf_material)

        bpy.types.Scene.turtleRenderer = tr

        #print ("SETUP RENDERER")

    ################
    # Utilities
    ################

    @classmethod
    def poll(cls, context):
        # DEPRECATED: Will make sure that this is enabled only if there is an active object
        # TODO: WHY IS THIS DEPRECATED??
        #ob = context.active_object
        #return ob is not None and ob.mode == 'OBJECT'
        return True


def add_to_menu(self, context):
    # This adds the plantform operator to the contextual Object menu
    self.layout.operator("object.add_plantform", icon = "PLUGIN")


def register():
    # We register the needed operators, so that they can be used inside Blender

    def unregisterClass(_class):
        try:
            bpy.utils.unregister_class(_class)
        except Exception as e:  print(str(e) + ": " + str(_class))

    def registerClass(_class):
        try:
            bpy.utils.register_class(_class)
        except Exception as e:  print(str(e) + ": " + str(_class))

    """
    unregisterClass(OBJECT_OT_ResetLSystem)
    unregisterClass(OBJECT_OT_RandomizeLSystem)
    unregisterClass(OBJECT_OT_ComplexifyLSystem)
    unregisterClass(OBJECT_OT_SimplifyLSystem)
    #unregisterClass(OBJECT_OT_EvolveByStepsLSystem)
    unregisterClass(OBJECT_OT_EvolveLSystem)
    unregisterClass(OBJECT_OT_AddPlantForm)
    unregisterClass(PANEL_AddPlantForm)
    """
    registerClass(OBJECT_OT_ResetLSystem)
    registerClass(OBJECT_OT_RandomizeLSystem)
    registerClass(OBJECT_OT_RandomizeLogicallyLSystem)
    registerClass(OBJECT_OT_ComplexifyLSystem)
    registerClass(OBJECT_OT_ModifyLSystem)
    registerClass(OBJECT_OT_SimplifyLSystem)
    registerClass(OBJECT_OT_EvolveInteractivelyLSystem)
    registerClass(OBJECT_OT_EvoIntChoose1)
    registerClass(OBJECT_OT_EvoIntChoose2)
    registerClass(OBJECT_OT_EvoIntChoose3)
    registerClass(OBJECT_OT_EvolveLSystem)
    registerClass(OBJECT_OT_EvolveLSystemModal)
    #registerClass(OBJECT_OT_EvolveByStepsLSystem)
    registerClass(OBJECT_OT_AddPlantForm)
    registerClass(OBJECT_OT_ExportToEgg)
    registerClass(OBJECT_OT_ExportToPng)

    # Add to the Tools panel
    #registerClass(PANEL_AddPlantForm)

    # Add to the Add->Mesh menu
    bpy.types.INFO_MT_mesh_add.append(add_to_menu)


def unregister():
    bpy.types.INFO_MT_mesh_add.remove(add_to_menu)

if __name__ == "__main__":

    # Clear scene
    clearScene(bpy.context)

    # Register the operator
    #unregister()
    print("Registering blender extension Plant Form...")
    register()
    print("Registered successfully!")

