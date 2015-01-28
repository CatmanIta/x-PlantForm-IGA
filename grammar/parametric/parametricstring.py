"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

# This code needed for blender to load correctly updated source files
import grammar.parametric.parametricmodule

import imp
imp.reload(grammar.parametric.parametricmodule)

from grammar.parametric.parametricmodule import ParametricModule

class ParametricString:
    """
    An pL-system string, composed of multiple ParametricModule
    Examples: B(y)A(x,y)  F(x)C(y)
    """

    def __init__(self):
        self.modulesList = []
        self.globalDefines = None

    @staticmethod
    def fromTextString(textString):
        ps = ParametricString()
        ps.parseString(textString)
        return ps

    def setGlobals(self,globalDefines):
        """
        The global defines this pString uses.
        """
        self.globalDefines = globalDefines
        #self.evaluateDefines()    # TODO: should we also force the evaluation?

    def parseString(self,textString):
        """
        Creates this parametric string from an actual string value.

        @param string: String to parse
        @type string: str
        """
        self.modulesList = self.stringToModulesList(textString)

    def __str__(self):
        s = ""
        for i in range(len(self.modulesList)):
            module = self.modulesList[i]
            s += str(module)
        return s

    def resetConversions(self):
        for module in self.modulesList:
            module.ignoreConversion = False

    def containsAllLetters(self,letters):
        """ True if this pString contains all the requested letters. """
        for l in letters:
            if not self.containsLetter(l): return False
        return True

    def containsAllLettersAtLeastCount(self,letters,count):
        """ True if this pString contains all the requested letters, with each at least COUNT times. """
        for l in letters:
            if not self.containsLetterAtLeastCount(l,count): return False
        return True

    def containsLetter(self,letter):
        """ True if this pString contains the requested letter (at least once) """
        for m in self.getActualModules():
            if m.letter == letter: return True
        return False

    def containsLetterAtLeastCount(self,letter,count):
        """ True if this pString contains the requested letter at least COUNT times. """
        n = 0
        for m in self.getActualModules():
            if m.letter == letter: n+=1
        return n>=count

    def hasBranches(self):
        """ True if this pString contains at least one branch """
        for m in self.modulesList:
            if m.isBracket():
                return True
        return False

    ################
    # Building
    ################

    def appendOpenBranch(self):
        self.modulesList.append(ParametricModule.fromTextString("["))

    def appendCloseBranch(self):
        self.modulesList.append(ParametricModule.fromTextString("]"))

    def appendModule(self,m):
        if self.globalDefines is not None:
            for i in range(len(m.params)):
                if m.params[i] in self.globalDefines:    # Uses global defines, if available
                    m.params[i] = self.globalDefines[m.params[i]]
        self.modulesList.append(m)

    def removeModulesFromTo(self,start_index,end_index):
        del self.modulesList[start_index:end_index]

    def evaluateDefines(self):
        """
        Evaluates this pString according to global defines. Its modules are replaced with 'valued' modules.
        """
        for i in range(len(self.modulesList)):
            if self.modulesList[i].isBracket(): continue    # Bracket have no params
            self.modulesList[i].params = [(self.globalDefines[v]  if v in self.globalDefines else v)  for v in  self.modulesList[i].params]

    def setParameterToModulesOfLetter(self,letter,param_value):
        """
        Sets the value of all parameters of a module with the given letter to a chosen value.
        """
        for m in self.getActualModules():
            if m.letter == letter: m.changeAllParametersTo(param_value)
    ################
    # Utilities
    ################

    def __iter__(self):
        return self.modulesList.__iter__()

    def __getitem__(self, key):
        return self.modulesList[key]

    def __len__(self):
        return len(self.modulesList)

    def index(self,m):
        return self.modulesList.index(m)

    def lengthWithoutBrackets(self):
        return len(self.getActualModules())

    def bracketsAreBalanced(self):
        balance = 0
        for m in self.modulesList:
            if m.isOpenBracket(): balance += 1
            elif m.isClosedBracket(): balance -= 1
        return balance == 0

    def getActualModules(self):
        """ Returns the list of modules, without additional stuff such as brackets """
        return list(filter( lambda m: not m.isBracket(),self.modulesList))

    def getFirstModuleOfLetter(self,letter):
        for m in self.getActualModules():
            if m.letter == letter:
                return m
        return None

    @staticmethod
    def copyFrom(other_pString):
        """
        Copies a ParametricString and returns the copy.
        """
        new_pString = ParametricString()
        new_pString.setGlobals(other_pString.globalDefines)
        new_pString.modulesList = []
        for m in other_pString.modulesList:
            new_pString.modulesList.append(ParametricModule.copyFrom(m))
        return new_pString

    def stringToModulesList(self,inputTextString):
        """
        Parse a text string into a sequence of pL-System modules, o.e. a parametric string.

        @param inputTextString: The string to be parsed.
        @type inputTextString: str

        @return: A list of modules
        @rtype: list of ParametricModule
        """
        modulesList = []

        inputTextString = inputTextString.strip()

        #if verbose: print("\nParsing string " + inputTextString)

        tmp_params_string = ""
        tmp_letter_string = ""

        letter = ''
        params = []

        inputTextString += "?"      # We treat this as the ending character
        countingLetters = True      # Always starts with a letter symbol
        buildLast = False
        appendThisAfter = False

        for i in range(len(inputTextString)):
            c = inputTextString[i]

            if c == ']':
                # Next is a letter
                countingLetters = True
                # We finished the last one
                buildLast = True
                appendThisAfter = True

            elif c == '[':
                # Next is a letter
                countingLetters = True
                # We finished the last one
                buildLast = True
                appendThisAfter = True

            elif c == ')':
                # Next is a letter
                countingLetters = True
                # We finished the last one
                buildLast = True

            elif c == '(':
                # Next is a param
                countingLetters = False
                # We finished the last one
                buildLast = True

            elif c == '?':
                # Ending!
                # We finished the last one
                buildLast = True

            else:
                if countingLetters:
                    # A letter is exactly one character long
                    tmp_letter_string += c
                    buildLast = True
                else:
                    # A parameter may be longer than one character
                    tmp_params_string += c

            # Build the previous stuff
            if buildLast:
                if len(tmp_letter_string) > 0:

                    if len(letter) > 0:
                        # We already had a letter
                        modulesList.append(ParametricModule(letter,[]))

                    letter = tmp_letter_string
                    tmp_letter_string = ''

                    #if verbose: print("Found letter: " + letter)

                    if inputTextString[i] != '(' and inputTextString[i+1] != '(':
                        #if verbose: print("Adding NONPARAMETRIC")
                        # This is not a parametric module, so we just add it
                        modulesList.append(ParametricModule(letter,params))
                        letter = ''

                if len(tmp_params_string) > 0:
                    params = tmp_params_string.split(",")

                    #if verbose: print("Found params: " + tmp_params_string)
                    tmp_params_string = ''

                    # Parametric module
                    #if verbose: print("Adding PARAMETRIC")
                    modulesList.append(ParametricModule(letter,params))
                    letter = ''
                    params = []

                #if len(params) > 0:
                #    modulesList.append(Module(letter,params))
                #    letter = ''
                #    params = []

                buildLast = False


            if appendThisAfter:
                modulesList.append(ParametricModule(c,[]))
                appendThisAfter = False

        if len(letter) > 0:
            # We still had a letter
            modulesList.append(ParametricModule(letter,[]))

        """if verbose:
            print("Modules: ")
            for a in modulesList: print(a)"""

        return modulesList


''' TODO: Differentiate ParametricString from ValuedParametricString
class ValuedParametricString(ParametricString):
    """
    An L-system string with parametric values.
    Examples: B(3)A(1,2)  F(10)C(2)
    """

    def __init__(self,globalDefines):
        ParametricString.__init__(self, globalDefines)
'''


if __name__ == "__main__":
    print("Start testing ParametricString")

    print("\nCreation")
    ps = ParametricString.fromTextString("FF[F]AAEEE")
    print(ps)

    print("\nAppend module")
    ps.appendModule(ParametricModule("C"))
    print(ps)

    print("\nAppend module with global parameter")
    ps.appendModule(ParametricModule("C",["p"]))
    print(ps)

    print("\nSet global defines")
    globalDefines = {"p":2.6}
    ps.setGlobals(globalDefines)
    print(ps)

    print("\nEvaluate globals")
    ps.evaluateDefines()
    print(ps)

    print("\nAppend parametric module")
    ps.appendModule(ParametricModule("X",["x","y"]))
    print(ps)

    print("\nEvaluate parameters")
    ps.setParameterToModulesOfLetter("X",1.2)
    print(ps)

    print("\nCopy")
    ps_2 = ParametricString.copyFrom(ps)
    print(ps_2)

    print("\nCheck modules")
    print("NMods: " + str(len(ps.modulesList)))
    for m in ps.modulesList:
        print(str(m) + " (bracket? " + str(m.isBracket()) +") (has params? " + str(m.hasParemeters()) + ")")


    print("\nHas branches? " + str(ps.hasBranches()))
    print("\nIs balanced? " + str(ps.bracketsAreBalanced()))


    print("\nFinish testing ParametricString")