"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

# This code needed for blender to load correctly updated source files
import grammar.parametric.parametricstring
import grammar.parametric.parametricmodule
import grammar.parametric.utilities

import imp
imp.reload(grammar.parametric.parametricstring)
imp.reload(grammar.parametric.parametricmodule)
imp.reload(grammar.parametric.utilities)

from grammar.parametric.parametricstring import ParametricString
from grammar.parametric.parametricmodule import ParametricModule
from grammar.parametric.utilities import Utilities

import operator
import datetime

class ParametricProductionPredecessor(ParametricModule):
    """
    A module functioning as a predecessor to a parametric production.
    """
    def __init__(self,letter,params=[]):
        ParametricModule.__init__(self, letter, params)


class ParametricProductionCondition:
    """
    Functions as a condition for a parametric production.
    """

    def parseString(self, text, defines):
        """
        @param text: Text string that is transformed into condition.
        @type text: str

        @param defines: Global defines
        @type defines: dictionary
        """
        conditionType = ''
        conditionParamChar = None
        conditionOperatorString = None
        conditionValue = None

        #print("PARSING :'" + str(text) + "'")
        if text.strip() == "*":  # '*' Stands for always
            conditionType = '*'
            conditionValue = 1

        elif Utilities.isFloat(text):
            # If the text is a float, then this condition is a probability value [0,1]
            # Example production ---  A : 0.2 -> B
            conditionType = '#'   # '#' Stands for probability
            conditionValue = float(text)

        else:
            # Otherwise, this condition is a check on a parameter
            # Example production ---  A(x) : x > 1 -> B
            # The input text is in the form: 'x>1'
            conditionType = 'P'
            conditionOperatorString = ""
            for i in range(len(text)):
                c = text[i]
                if i == 0:
                    # The first character is the parameter to be checked
                    conditionParamChar = c
                elif (c not in ('=') and c not in ParametricProduction.ops):
                    # We finished the operator, we are building the value
                    if c.isdigit():
                        # We are checking against a constant
                        conditionValue = float(text[i:len(text)])
                    else:
                        # We are checking against a global defined parameter
                        #@note: THIS WILL WORK ONLY IF THE GLOBAL DEFINES ARE CREATED BEFORE THE PRODUCTIONS!
                        definedParam = text[i:len(text)]
                        if definedParam in defines:
                            self.conditionValue = defines[definedParam]
                    break
                else:
                    # We are building the operator
                    conditionOperatorString += c

        self.type = conditionType
        self.parameter = conditionParamChar
        self.operator = conditionOperatorString
        self.value = conditionValue


    def __str__(self):
        """
        Parses the condition into a string representation.
        """
        s = ""
        if self.type == '*':
            s += '*'
        elif self.type == '#':
            s += str(self.value)
        elif self.type == 'P':
            s += str(self.parameter)
            if self.operator is not None: s += " " + str(self.operator)
            if self.value is not None: s += " " + str(self.value)
        return s

class ParametricProductionSucessor(ParametricString):
    """
    A pString functioning as the successor in a production.
    """
    def __init__(self):
        ParametricString.__init__(self)

class ParametricProduction:
    """
    Defines a single production rule for a L-system.
    Also known as rule.
    """
    GENOME_SEPARATOR = ';'  # Not '.' used for decimal. Not ',' used for lists.
    ops = None
    randomValue = None
    totalCondition = 0

    @staticmethod
    def resetStochasticState():
        ParametricProduction.randomValue = None
        ParametricProduction.totalCondition = 0

    def __init__(self,verbose = False):
        self.verbose = verbose

        self.globalDefines = None
        self.predecessor = None
        self.condition = None
        self.successor = None

        if ParametricProduction.ops is None:
            # Build the operators dictionary
            ParametricProduction.ops = {
                    "+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "%": operator.mod,
                    ">": operator.gt,
                    "<": operator.lt,
                    "=": operator.eq,
                    "!=": operator.ne,
                    ">=": operator.ge,
                    "<=": operator.le,
                    } # etc.

    def setGlobals(self,globalDefines):
        self.globalDefines = globalDefines
        if self.predecessor is not None: self.predecessor.setGlobals(globalDefines)
        #self.condition.setGlobals(globalDefines)
        if self.successor is not None: self.successor.setGlobals(globalDefines)

    def extendGlobalDefines(self, globalDefines):
        new_defines = self.globalDefines
        for k,v in globalDefines.items():
            new_defines[k] = v
        self.setGlobals(new_defines)

    ######################
    # Building
    ######################

    def setPredecessorModule(self,pred):
        self.predecessor = pred

    def setConditionFromString(self,conditionString):
        self.condition = self.parseConditionString(conditionString)

    def setSuccessorPstring(self,succ):
        succ.setGlobals(self.globalDefines)
        self.successor = succ

    ######################
    # Parse from text string
    ######################

    def parseString(self,string):
        """
        Creates this parametric string from an actual string value.
        Must be in the form "pre:cond->succ"

        @param string: String to parse
        @type string: str
        """
        predecessorString, string = string.split(":")
        conditionString, successorString = string.split("->")
        self.predecessor = self.parsePredecessorString(predecessorString)
        self.condition = self.parseConditionString(conditionString)
        self.successor = self.parseSuccessorString(successorString)
        if self.verbose: print("\nProduction: " + str(self))

    def parsePredecessorString(self,string):
        predecessorPString = ParametricString()
        predecessorPString.setGlobals(self.globalDefines)
        predecessorPString.parseString(string)    # TODO: Maybe this predecessor should be treated as a 1-module string for consistency, instead of a module?
        assert len(predecessorPString) == 1, 'The predecessor must contain only one module!'
        return predecessorPString[0]   # Only one

    def parseConditionString(self,string):
        condition = ParametricProductionCondition()
        condition.parseString(string,self.globalDefines)
        return condition

    def parseSuccessorString(self,string):
        successor = ParametricString()
        successor.setGlobals(self.globalDefines)
        successor.parseString(string)
        return successor

    ######################
    # Parse to text string
    ######################

    def __str__(self):
        """
        Parses the production into a string representation.
        """
        s = ""
        if self.predecessor is not None: s += str(self.predecessor)
        if self.condition is not None: s += " : " + str(self.condition)
        if self.successor is not None: s += " -> " + str(self.successor)
        return s

    #########################
    # Genome Representation
    ########################

    def parseGenome(self, genome_part):
        """
        Given a genome representation of the production, parses it into a production.
        @genome_part: The part of the genome representing this production.
        """
        #print(genome)
        #print (genome.split("."))
        predecessorString, conditionString, successorString = genome_part.split(self.GENOME_SEPARATOR)
        self.predecessor = self.parsePredecessorString(predecessorString)
        self.condition = self.parseConditionString(conditionString)
        self.successor = self.parseSuccessorString(successorString)
        if self.verbose: print("\nProduction: " + str(self))

    def toGenomeRepresentation(self):
        s = ""
        s += (str(self.predecessor)  if (self.successor is not None) else "")
        s += self.GENOME_SEPARATOR + (str(self.condition) if self.successor is not None else "")
        s += self.GENOME_SEPARATOR + (str(self.successor) if self.successor is not None else "")
        return s

    ######################
    # Utilities
    ######################

    def check(self,inputString,rnd):
        """
        Checks whether the condition evaluates to True or False
        """
        # Always
        if self.condition.type == "*":
            if self.verbose: print("Condition always true")
            return True

        # Stochastic
        elif self.condition.type == "#":
            if ParametricProduction.randomValue is None:
                ParametricProduction.randomValue = rnd.random()
            ParametricProduction.totalCondition += self.condition.value
            if self.verbose: print("Checking random " + str(ParametricProduction.randomValue) + " against value " + str(self.condition.value))
            if ParametricProduction.randomValue <= ParametricProduction.totalCondition:
                return True
            else:
                return False

        # Parametric
        elif self.condition.type == "P":
            predecessor = self.predecessor
            predecessorLetter = predecessor.letter
            if self.verbose: print("Checking condition for letter " + predecessorLetter + " and parameter " + str(self.condition.parameter))

            # First, we must locate that predecessor's letter in the input string
            inputModules = inputString.modulesList
            for i in range(len(inputModules)):
                inputModule = inputModules[i]
                print(inputModule)
                print(predecessorLetter)
                if inputModule.letter == predecessorLetter:
                    # TODO: also check that the number of parameters is the same
                    print("Found the predecessor: " + predecessorLetter)

                    # Check the predecessor parameter J against the condition
                    for j in range(len(predecessor.params)):
                        if predecessor.params[j] == self.condition.parameter:
                            # I-J is the correct parameter's position
                            #print([v for v in inputString.modulesList[i].params])
                            value = inputString.modulesList[i].params[j]
                            if self.verbose: print("Parameter " + self.condition.parameter + " has value " + str(value) + " to check against " + str(self.condition.value))
                            return ParametricProduction.ops[self.condition.operator](value,(self.condition.value))
        else:
            raise Exception("Wrong condition type for condition! " + str(self.condition.type))

    def convert(self,inputPString):
        """
        Converts the given string by replacing the predecessor with the successor and updating the parameter values

        @param inputPString: The ParametricString that must be converted using this production.
        @type inputPString: ParametricString
        """
        # First, we must locate the predecessor of this rule in the input string, if there is
        inputModules = inputPString.modulesList
        #outputModules = [m for m in inputModules]   # Copy NO!!! WE DON'T COPY IT, BECAUSE THEN WE'LL HAVE TO REMOVE AND THAT TAKES A LOT OF TIME!
        outputModules = []  # We start from an empty output list and will populate it as we loop over the input modules
        # @note: with this change, I can do in 2 seconds 600,000 elements instead of 1,000!

        totInserted = 0

        #print("Input is: " + str(inputPString))
        #print(self.globalDefines)

        #tot_timedict = datetime.timedelta(0)
        #tot_timesucc = datetime.timedelta(0)

        for i in range(len(inputModules)):
            inputModule = inputModules[i]

            if inputModule.isBracket():
                outputModules.append(inputModule)
                continue

            #print("CHECKING " + str(inputModule))
            #print(datetime.datetime.now())

            if inputModule.ignoreConversion:
                #print("APPEND " + str(inputModule))
                outputModules.append(inputModule)
                continue
            if inputModule.letter != self.predecessor.letter:
                outputModules.append(inputModule)
                continue
            else:
                # This is to be transformed!
                #timestart = datetime.datetime.now()

                # We located it, we now need to substitute for the successor
                #print("FOUND THE PREDECESSOR " + predecessorLetter)

                # Remove the predecessor
                predIndex = i
                #outputModules.remove(inputModule)   # TODO: this is REALLY SLOW!!!

                #timedict = datetime.datetime.now() - timestart
                #tot_timedict += timedict
                #timestart = datetime.datetime.now()


                # We get the parameters' current values too
                predParamNames = self.predecessor.params
                predParamValues = inputModule.params
                if self.verbose:
                    strnames = " ".join([str(p) for p in predParamNames])
                    strvalues =  " ".join([str(p) for p in predParamValues])
                    print("Predecessor " + self.predecessor.letter +" at index " + str(predIndex) + " has parameters (" + strnames + ") with values (" + strvalues + ")")

                # Build a dictionary with the parameter values
                paramDict = {}
                for j in range(len(predParamNames)):
                    paramDict[predParamNames[j]] = predParamValues[j]

                #print("Dict: " + str(timedict))

                #print "Successor: " + str(self.successor)

                # Add the successors
                for j in range(len(self.successor.modulesList)):
                    successorModule = self.successor.modulesList[j]

                    # Look for what parameters must be evaluated for the successor (which contains expressions)
                    if successorModule.isBracket():
                        if self.verbose: print("Module " + successorModule)
                        actualSuccessorModule = successorModule
                    else:
                        if self.verbose:
                            strexpressions = " ".join([p for p in successorModule.params])
                            print("Successor with letter " + successorModule.letter + " has expressions (" + strexpressions + ")")
                        values = []

                        for expression in successorModule.params:
                            expression = str(expression)
                            v = ""
                            op_last = None
                            op = None
                            # Check each character of the expression
                            tmp_digit_string = ""
                            tmp_letter_string = ""

                            #print(expression)
                            #print(type(expression))
                            expression += "?"   # Ending
                            for c in expression:
                                countingDigits = False
                                countingLetters = False
                                #print(c)
                                if c in ParametricProduction.ops:
                                    # Found an operator
                                    op_last = op
                                    op = ParametricProduction.ops[c]
                                    #print("FOUND OP" + str(op))
                                elif c.isdigit() or c is '.':
                                    # Found a digit
                                    if tmp_letter_string != "":
                                        # Continuing a literal parameter
                                        tmp_letter_string += c
                                    else:
                                        # Starting a number parameter
                                        tmp_digit_string += c
                                        countingDigits = True
                                    #print(tmp_digit_string) 
                                elif c == '?':
                                    # Ending, do nothing
                                    op_last = op
                                    pass
                                else:
                                    # Found a letter
                                    tmp_letter_string += c
                                    countingLetters = True

                                # Build the previous stuff
                                if not countingDigits and len(tmp_digit_string) > 0:
                                    if self.verbose: print("FOUND NUMBER: " + str(tmp_digit_string))
                                    v = self.performOperation(v,op_last,float(tmp_digit_string))
                                    tmp_digit_string = ""

                                if not countingLetters and len(tmp_letter_string) > 0:
                                    #print "CURRENT: " + str(self.globalDefines)
                                    #print("TEMP LETTER STRING: " + str(tmp_letter_string))
                                    if tmp_letter_string in self.globalDefines.keys():
                                        new_v = self.globalDefines[tmp_letter_string]
                                    else:
                                        new_v = paramDict[tmp_letter_string]
                                        #if not (new_v is float): #TODOO!!!!
                                        #    new_v = eval(str(new_v))    # WARNING: added this for when the axiom contains some functions! Instead they should be evaluated beforehand!
                                    if self.verbose:  print("FOUND PARAMETER: " + str(tmp_letter_string) + " with value " + str(new_v) + " to be added to current value: (" + str(v) +")")
                                    v = self.performOperation(v,op_last,float(new_v))
                                    tmp_letter_string = ""

                            values.append(v)
                            #print("Value: " + str(v))
                        actualSuccessorModule = successorModule.evaluate(*values)
                        actualSuccessorModule.ignoreConversion = True   # This module won't be converted again during this step

                    if self.verbose: print("Inserting output module " + str(actualSuccessorModule))
                    #outputModules.insert(predIndex+totInserted,actualSuccessorModule)
                    outputModules.append(actualSuccessorModule)
                    totInserted+=1

                    #print("CURRENT MODULES:"); for m in outputModules: print(m)
                totInserted-=1 # The removed module must not be counted

                #timesucc = datetime.datetime.now() - timestart
                #tot_timesucc += timesucc
                #print("Succ: " + str(timesucc))

                #print ("Current output: " + str(outputModules))

        #tot_time = tot_timedict + tot_timesucc
        #print("TOT time: " + str(tot_time))
        #print("TOT dict: " + str(tot_timedict))
        #print("TOT succ: " + str(tot_timesucc))

        inputPString.modulesList = outputModules
        #print("Result: " + str(inputPString))
        return inputPString

    def performOperation(self,v1,op,v2):
        """
        Uses an operator between two values to create the result.
        """
        if op is None:
            v1 = v2
        else:
            if self.verbose: print("Operation: " + str(v1) + " " + str(op) + " " + str(v2))
            v1 = op(v1,v2)
        return v1



if __name__ == "__main__":
    print("Start testing ParametricProduction")

    print("\nCreation")
    pp = ParametricProduction(verbose=True)
    pp.setGlobals({"p":1.0})    # TODO: Must this be before? Or not?
    pp.parseString('F:*->FF')    # TODO: add a ParametricProduction.fromTextString LIKE THE REST!
    #print(pp)

    print("\nChange predecessor: parametric")
    pm = ParametricModule.fromTextString("A(x)")
    pp.setPredecessorModule(pm)
    print(pp)
    print(pm.letter)

    print("\nChange condition: probability")
    pp.setConditionFromString("0.8")
    print(pp)

    print("\nChange condition: parametric")
    pp.setConditionFromString("x>0.9")
    print(pp)

    print("\nChange successor: parametric")
    ps = ParametricString.fromTextString('F(x)A(p)')
    pp.setSuccessorPstring(ps)
    print(pp)

    import random
    rnd = random.Random()
    print("\nCheck condition")
    ps = ParametricString.fromTextString("A(1)")
    print("Input: " + str(ps))
    result = pp.check(ps, rnd)
    print("Result: " + str(result))

    print("\nConvert and evaluate  (also globals)")
    print("Input: " + str(ps))
    ps = pp.convert(ps)
    print("Result: " + str(ps))


    print("\nTo genome")
    genome = pp.toGenomeRepresentation()
    print("Result: " + str(genome))


    print("\nFinish testing ParametricProduction")