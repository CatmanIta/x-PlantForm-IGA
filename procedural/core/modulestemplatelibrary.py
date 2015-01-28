"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
import procedural.core.generationtemplatemodule
import grammar.parametric.parametricmodule

import imp
imp.reload(procedural.core.generationtemplatemodule)
imp.reload(grammar.parametric.parametricmodule)

from procedural.core.generationtemplatemodule import GenerationTemplateModule
from grammar.parametric.parametricmodule import ParametricModule

class ModulesTemplateLibrary():
    """
    Defines what Modules can be used to build strings by the procedural generators.
    Without this, we wouldn't know what letters and parameters to use!
    """
    MAX_DEFINES = 10

    def __init__(self,
                 generator,
                 rnd,
                 parameterized = True,
                 definesProbability = 0.0,
                 constantsProbability = 1.0
                 ):
        self.generator = generator
        self.rnd = rnd
        self.parameterized = parameterized
        self.definesProbability = definesProbability
        self.constantsProbability = constantsProbability    # As parameters

        # Available Modules
        self.modules_library = []

        # Growth
        self.addTemplateModule("F",1,weight=50,scale_min=0.01,scale_max=0.1)

        # Structure (just used for advancing productions)
        self.addTemplateModule("X", 2, weight=5)
        self.addTemplateModule("Y", 2, weight=5)
        self.addTemplateModule("Z", 2, weight=5)

        # Structure (just used for advancing productions, only one parameter)
        self.addTemplateModule("A", 1, weight=5)

        # Orientations
        self.addTemplateModule("+", 1, weight=20,scale_min=0,scale_max=30)
        self.addTemplateModule("-", 1, weight=20,scale_min=0,scale_max=30)
        self.addTemplateModule("&", 1, weight=20,scale_min=0,scale_max=30)
        self.addTemplateModule("^", 1, weight=20,scale_min=0,scale_max=30)
        self.addTemplateModule("/", 1, weight=20,scale_min=0,scale_max=30)
        self.addTemplateModule("\\", 1, weight=20,scale_min=0,scale_max=30)

        # Leaves
        self.addTemplateModule("L", 1, weight=50)
        self.addTemplateModule("B", 1, weight=10)
        self.addTemplateModule("K", 1, weight=10)
        self.addTemplateModule("R", 1, weight=10)

        # Branch radius
        self.addTemplateModule("!", 1, weight=20,scale_min=0,scale_max=2)

        #print("GENERATED GENERATION MODULES: " + str(len(self.modules_library)))


    def addTemplateModule(self, letter, maxParameters, weight, scale_min = 0, scale_max=1):
        """
        Create a new template of a module that could be generated.
        """
        templateModule = GenerationTemplateModule(letter,weight=weight,scale_min=scale_min,scale_max=scale_max)

        # Parameterization
        #nParameters = self.rnd.randint(1,maxParameters)#self.minNumberOfParameters,self.maxNumberOfParameters)Parameterization
        nParameters = maxParameters # @note: we keep the number of parameters fixed and pre-determined for each symbol, or it will give problems with the mutations
        for i in range(nParameters): templateModule.appendParameter("_")  # We append a fake parameter
        """
        DEPRECATED: this is chosen when generating!!
        if self.constantsProbability > 0.0:
            if self.rnd.random() < self.constantsProbability:
                # Set a constant value as parameter
                max_scale = self.modules_library.getScale(module.letter)
                if self.constantsProbability > 0.0 and self.rnd.random() < self.constantsProbability:   module.appendParameter(self.getRandomTwoDigitFloat(max_scale))

        if self.definesProbability > 0.0:
            if self.rnd.random() < self.definesProbability:
                # Select an existing define, or add a new one
                nCurrentDefines = len(self.generator.lsystem.defines)
                if nCurrentDefines == 0 or self.rnd.random() > 0.5:
                    defname, defvalue = self.generator.generateRandomDefine()
                else:
                    defname = "d"+str(self.rnd.randint(0,len(self.lsystem.defines)-1))
                new_module.appendParameter(defname)

        """
        self.modules_library.append(templateModule)

    def getTemplateModules(self):
        return self.modules_library

    def getTemplateModuleByLetter(self, letter):
        for mod in self.modules_library:
            if mod.letter == letter: return mod
        return None

    def createActualModuleFromTemplate(self, template_module, isPredecessor = False):
        """
        Creates a normal ParametricModule out of a GenerationTemplateModule.
        If this is a predecessor module (isPredecessor is True), then the module is created with variables (e.g. x,y,z) as parameters.
        """
        module = ParametricModule(template_module.letter)

        #print("Gen module has n params: " + str(len(template_module.params)))

        if self.parameterized:
            param_index = 0
            for param in template_module.params:
                value = 1   # Default value
                if isPredecessor == True:
                    if param_index == 0: value = "x"
                    if param_index == 1: value = "y"
                    if param_index == 2: value = "z"
                elif self.constantsProbability > 0.0:
                    if self.rnd.random() < self.constantsProbability:
                        # Set a constant value as parameter
                        value = template_module.generateConstantParameterValue(self.rnd)
                elif self.definesProbability > 0.0:
                    if self.rnd.random() < self.definesProbability:
                        # Select an existing define, or add a new one
                        nCurrentDefines = len(self.generator.lsystem.globalDefines)
                        if nCurrentDefines > 0 and (self.rnd.random() > 0.5 or nCurrentDefines == ModulesTemplateLibrary.MAX_DEFINES):
                            defname = "d"+str(self.rnd.randint(0,len(self.generator.lsystem.globalDefines)-1))
                        else:
                            defname, defvalue = self.generator.generateRandomDefine()
                        value = defname
                module.appendParameter(value)
                param_index += 1
        #print("New Module: " + str(module))
        return module

if __name__ == "__main__":
    print("Start testing ModulesTemplateLibrary")

    import random
    rnd = random.Random()

    print("\nTEST - Creation")
    mtl = ModulesTemplateLibrary(None,rnd, definesProbability = 0.5, constantsProbability = 0.5)

    print("\nTEST - Get modules")
    for template in mtl.getTemplateModules(): print(template)

    print("\nTEST - Get template by letter")
    tm = mtl.getTemplateModuleByLetter("X")
    print(tm)

    print("\nTEST - Create actual module (non-predecessor)")
    print(mtl.createActualModuleFromTemplate(tm, False))

    print("\nTEST - Create actual module (predecessor)")
    print(mtl.createActualModuleFromTemplate(tm, True))

    print("\nFinish testing ModulesTemplateLibrary")