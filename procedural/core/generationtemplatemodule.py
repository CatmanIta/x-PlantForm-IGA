"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import grammar.parametric.parametricmodule
import procedural.miscellaneous.utilities

import imp
imp.reload(grammar.parametric.parametricmodule)
imp.reload(procedural.miscellaneous.utilities)

from grammar.parametric.parametricmodule import ParametricModule
from procedural.miscellaneous.utilities import Utilities


class GenerationTemplateModule(ParametricModule):
    """
    A module used in the procedural generators.
    It functions as a 'template' for modules, so that an actual module, valued and/or parameterized, can be extracted from this.
    """
    def __init__(self,letter,params=[],weight=1,scale_min=0,scale_max=1):
        ParametricModule.__init__(self, letter, params)
        self.weight = weight                # Must be [1,100]. The higher, the more likely this will appear in the generation
        self.scale_min = scale_min          # Determines the minimum random value that this module can have as a single parameter
        self.scale_max = scale_max          # Determines the maximum random value that this module can have as a single parameter

    def __str__(self):
        s = ParametricModule.__str__(self)
        s += "(W: " + str(self.weight) + ")"
        return s

    def generateConstantParameterValue(self,rnd):
        return Utilities.getRandomTwoDigitFloat(rnd,self.scale_min,self.scale_max)


if __name__ == "__main__":
    print("Start testing GenerationTemplateModule")

    print("\nCreation")
    gm = GenerationTemplateModule("A")
    print(gm)

    print("\nFinish testing GenerationTemplateModule")
