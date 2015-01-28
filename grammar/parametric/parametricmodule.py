"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

# This code needed for blender to load correctly updated source files
import grammar.parametric.utilities

import imp
imp.reload(grammar.parametric.utilities)

from grammar.parametric.utilities import Utilities

class ParametricModule:
    """
    Defines a single L-system module.
    Aka letter, aka parametric letter, aka symbol.

    Examples are: A(x), B, C(a,b,c), D(10.0), E(10+x)

    @note: Parameters may either be:
        - variables (x,y,z)
        - numbers (1,10.0,12.5)
        - expressions (10+x,x*2,x*y)
    """

    def __init__(self, letter, params = []):
        """
        @param letter: The letter assigned to this module. It determines its behavior in a L-system. For example, 'F'
        @type letter: character

        @param params: The parameters that are assigned to this module
        @type params: list
        """
        if len(letter) > 1: raise Exception("Letter must be a single character!")
        self.letter = letter
        self.ignoreConversion = False
        self.globalDefines = None

        # Copy the parameters. May be set if the symbol is parameterized. May be multiple parameters.
        # Number parameters are cast directly
        self.params = []
        for p in params:
            self.appendParameter(p)

    @staticmethod
    def fromTextString(textString):
        letter = textString[0]
        params = textString[2:-1].split(",")
        if params == [""]: params = []
        return ParametricModule(letter,params)

    def setGlobals(self,globalDefines):
        self.globalDefines = globalDefines

    def isOrientation(self):
        """
        Check whether this module defines an orientation.
        """
        return self.letter in ['+','-','&','^','/','\\']

    def isBracket(self):
        """
        Check whether this module defines an open or closed bracket
        """
        return self.isOpenBracket() or self.isClosedBracket()

    def isOpenBracket(self):
        return self.letter == '['

    def isClosedBracket(self):
        return self.letter == ']'

    def __str__(self):
        s = self.letter
        if len(self.params)>0:
            s += '('
            for j in range(len(self.params)):
                p = self.params[j]
                s += str(p)
                if j < len(self.params)-1: s += ','
            s += ')'
        return s

    def evaluate(self,*values):
        """
        Evaluates this parametric module and return the 'valued' module.
        For example, if the module is A(x,y), and we pass it the values x=2 and y=3, we get A(2,3).
        """
        evaluatedModule = ParametricModule(self.letter,self.params)
        for i in range(len(evaluatedModule.params)):
            evaluatedModule.params[i] = values[i]
        return evaluatedModule

    def appendParameter(self,p):
        """
        Appends a parameter to the list of parameters of this module.
        """
        if Utilities.isFloat(p):
            self.params.append(float(p))
        else:
            self.params.append(p)

    def hasParemeters(self):
        return len(self.params) > 0

    def changeAllParametersTo(self,v):
        """
        Changes all the parameters of this module to the given value.
        """
        for i in range(len(self.params)):
            self.params[i] = v

    @staticmethod
    def copyFrom(other_module):
        """
        Copies a Module and returns the copy.
        """
        new_module = ParametricModule(other_module.letter)
        new_module.params = [p for p in other_module.params]
        return new_module




''' TODO: We may not need this. Let's not distinguish.
class ValuedModule(Module):
    """
    A module with values instead of variables as parameters
    """

    def __init__(self,letter,params=[]):
        Module.__init__(self, letter, params)

'''

if __name__ == "__main__":
    print("Start testing ParametricModule")

    print("\nCreation")
    m = ParametricModule('A',[1,2,3])
    print(m)

    print("\nAppend parameter")
    m.appendParameter(5)
    print(m)

    print("\nVariable parameters")
    m = ParametricModule.fromTextString("B(x,y)")
    print(m)

    print("\nEvaluation")
    ev_m = m.evaluate(0,1)
    print(ev_m)

    print("\nHas parameters?")
    print(ev_m.hasParemeters())

    print("\nChanging all params to 5.0")
    ev_m.changeAllParametersTo('5.0')
    print(ev_m)

    print("\nCopy")
    copy_m = ParametricModule.copyFrom(ev_m)
    print(copy_m)

    print("\nCreate open bracket")
    m = ParametricModule.fromTextString("[")
    print(m)

    print("\nFinish testing ParametricModule")


