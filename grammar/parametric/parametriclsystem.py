"""
    @author: Michele Pirovano
    @copyright: 2013-2015

    # TODO: finish refactoring the globalDefines handling!
    OK - it should be standardized for all parametric classes
    TODO: - when set to the above class, it should propagate to the lesser ones
    OK - when a new lesser class is added, it should inherit the globals as well
"""

# This code needed for blender to load correctly updated source files
import grammar.parametric.parametricproduction
import grammar.parametric.parametricstring

import imp
imp.reload(grammar.parametric.parametricproduction)
imp.reload(grammar.parametric.parametricstring)

from grammar.parametric.parametricproduction import ParametricProduction
from grammar.parametric.parametricstring import ParametricString

import random
#import os
#import multiprocessing

class ParametricLSystem:
    """
    Defines a complete P-Lsystem.
    See "The Algorithmic Beauty of Plants"
    """
    OUTPUT_PATH = "C:\\Users\\Michele\\Desktop\\"

    def __init__(self, randomSeed = 0, verbose = False):
        """
        @param randomSeed: The seed with which to initialise the random distribution
        @type randomSeed: int

        @param verbose: Optional. If True, the system will print data to the console.
        @type verbose: bool
        """
        self.verbose = verbose

        # Empty LSystem
        self.clear()

        # Initialise the randomizer
        self.randomSeed = randomSeed
        self.rnd = random.Random()
        self.rnd.seed(randomSeed)

    def clear(self):
        """
        Clears the L-System, leaving it in an empty state.
        """
        self.globalDefines = {}
        self.axiom = self.setAxiomFromString("")
        self.clearProductions()
        self.niterations = 1
        self.resultPString = None

    def clearProductions(self):
        self.productions = []

    def setIterations(self,niterations):
        """
        Defines the number of iterations for this L-System.
        @warning: Do not put a high number here, or the system will take AGES to iterate

        @param niterations: The number of iterations to perform
        @type niterations: int
        """
        self.niterations = niterations

    #################
    # Globals
    #################

    def addGlobalDefine(self,name,value):
        """
        Defines a new global parameter.
        Global defines are part of a LSystem definition.

        @param name: The name of the global define
        @type name: str

        @param value: The value of the global define
        @type value: float
        """
        self.globalDefines[name] = value
        self.refreshGlobals()
        return name,value

    def overrideGlobalDefine(self,name,value):
        """
        Overrides an existing global parameter.
        """
        if name in self.globalDefines:
            self.globalDefines[name] = value
            self.refreshGlobals()
        else:
            raise Exception("Trying to override inexistent define!")

    def refreshGlobals(self):
        if self.axiom is not None: self.axiom.setGlobals(self.globalDefines)
        for prod in self.productions: prod.setGlobals(self.globalDefines)


    #################
    # Axiom
    #################

    def setAxiomFromString(self,textString):
        """
        @param textString: Initial string to parse
        @type textString: str
        """
        newPString = ParametricString.fromTextString(textString)
        newPString.setGlobals(self.globalDefines)
        self.axiom = newPString

    def setAxiomFromPstring(self,pstring):
        """
        @param string: Initial pString
        @type string: ParametricString
        """
        pstring.setGlobals(self.globalDefines)
        self.axiom = pstring

    def addNewProduction(self):
        """
        Adds a new empty production.
        """
        newProduction = ParametricProduction()
        newProduction.setGlobals(self.globalDefines)
        self.productions.append(newProduction)
        return newProduction

    def addProductionFromString(self,string):
        """
        @param string: String to parse
        @type string: str
        """
        newProduction = self.addNewProduction()
        newProduction.parseString(string)
        return newProduction

    def addProductionFromGenomeRepresentation(self,genome):
        newProduction = self.addNewProduction()
        newProduction.parseGenome(genome)

    def addProductionFromPstrings(self,pre,cond,sub):
        newProduction = self.addNewProduction()
        newProduction.setElements(pre,cond,sub)

    def addExistingProduction(self,prod):
        prod.setGlobals(self.globalDefines)
        self.productions.append(prod)

    def overrideProduction(self,i,pre,cond,sub):
        self.productions[i].setElements(pre,cond,sub)

    def getProduction(self,i):
        return self.productions[i]

    def getProductionWithPredecessorLetter(self, letter):
        for prod in self.productions:
            if prod.predecessor.letter == letter:
                return prod
        return None

    def copyProductionFromExisting(self,old_prod):
        new_prod = self.addProductionFromString(str(old_prod)) # This will copy the production, since we convert to string and back!

        # We also make sure that the defines are consistent
        new_prod.extendGlobalDefines(old_prod.globalDefines)

    def iterate_loop(self, N):
        if N is None: N = self.niterations
        currentParametricString = ParametricString.copyFrom(self.axiom) # We create a copy so to not modify the axiom
        #self.axiom.evaluateDefines()
        #print(self)
        #print(self.globalDefines)
        for i in range(N):
            if self.verbose: print("\nStep " + str(i+1))
            currentParametricString.resetConversions()
            # All productions are applied in parallel
            for prod in self.productions:
                if self.verbose: print("Rule: " + str(prod))
                result = prod.check(currentParametricString,self.rnd)
                #print("Rule evaluates: " +  str(result))
                if result:  currentParametricString = prod.convert(currentParametricString)
            if self.verbose: print("String at step " + str(i+1) + " is " + str(currentParametricString))
            ParametricProduction.resetStochasticState()
        currentParametricString.evaluateDefines()
        return currentParametricString


    def iterate_wrapper(self, queue, N):
        result = self.iterate_loop(N)
        queue.put(result)
        queue.close()

    def iterate(self,N = None):
        """
        Perform a set of iterations of the L-System

        @param N: Number of iterations
        @type N: int

        @return: A pstring representing the resulting L-System output
        @rtype: ParametricString
        """
        result = self.iterate_loop(N)
        #self.writeToFile()

        #TODO: We need a timeout for really long executions, but it won't work because it opens another blender instance! Fix this!
        """
        queue = multiprocessing.Queue(1) # Maximum size is 1
        proc = multiprocessing.Process(target=self.iterate_wrapper, args=(self, queue, N))
        proc.start()

        # Wait for TIMEOUT seconds
        try:
            result = queue.get(True, TIMEOUT)
        except Queue.Empty:
            # Deal with lack of data somehow
            result = None
            print("TIMEOUT reached! The pString is too long!")
        finally:
            proc.terminate()
            """
        return result

    def __str__(self):
        s = ""
        s += "\nw " + str(self.axiom)
        for prod in self.productions:
            s += "\n" + str(prod)
        if len(self.globalDefines.keys()) > 0: s += "\n"
        for k in self.globalDefines.keys():
            s += "(" + k + " = " + str(self.globalDefines[k]) +") "
        return s

    def writeToFile(self):
        #filepath = os.path.abspath("exported_lsystem.txt")
        filepath = OUTOUT_PATH + "exported_lsystem.txt"
        file = open(filepath, 'w')
        file.write(str(self))
        file.close()


    def toGenomeRepresentation(self):
        """ Defines compactly a complete lsystem """
        s = ""
        s += str(self.axiom)
        s += "||"+str(self.niterations) # The iterations must be shown as well
        for prod in self.productions:
            s += "||"
            s += prod.toGenomeRepresentation()
        return s

    def fromGenomeRepresentation(self,genome):
        """ Defines compactly a complete lsystem """
        self.clear()
        #print(genome)
        tokens = genome.split("||")
        self.setAxiomFromString(tokens[0])
        self.setIterations(int(tokens[1]))
        for i in range(2,len(tokens)):  self.addProductionFromGenomeRepresentation(tokens[i])

    @staticmethod
    def copyFrom(other_pSystem):
        new_pSystem = ParametricLSystem(other_pSystem.randomSeed)
        new_pSystem.setIterations(other_pSystem.niterations)

        for def_name in list(other_pSystem.globalDefines.keys()):
            new_pSystem.addGlobalDefine(def_name,other_pSystem.globalDefines[def_name])
        for prod in list(other_pSystem.productions):
            new_pSystem.copyProductionFromExisting(prod)

        new_pSystem.setAxiomFromString(str(other_pSystem.axiom))
        return new_pSystem

    def getResultPString(self):
        """ Returns the pString that results from iterating this lsystem. Computes it, if needed. """
        # TODO: WARNING!!! Make sure the resultPstring is emptied if we do some modification to the lsystem!! OR THIS WILL BEHAVE INCORRECTLY!
        if self.resultPString == None:  self.resultPString = self.iterate()
        return self.resultPString

    def clearResultPString(self):
        self.resultPString = None

    def printGlobalDefinesStatus(self):
        print("Global defines status:")
        print("System defines: " + str(self.globalDefines))
        print("Axiom defines: " + str(self.axiom.globalDefines))
        for pp in self.productions:
            print("Production defines: " + str(pp.globalDefines))
            print("Predecessor defines:" + str(pp.predecessor.globalDefines))
            print("Successor defines:" + str(pp.successor.globalDefines))

if __name__ == "__main__":
    print("Start testing ParametricLSystem")


    def test():
        print("\nCreation")
        pl = ParametricLSystem(verbose=True)
        pl.setAxiomFromString("FA")
        pl.addProductionFromString("F:*->FB")
        pl.addProductionFromString("A:*->AF")
        pl.addProductionFromString("B:*->FAF")
        pl.niterations = 6
        print("Result lSystem: " + str(pl))

        print("\nIteration")
        ps = pl.iterate()
        print("\nResult lSystem: "+str(pl))
        print("\nResult pString: "+str(ps))
        print("With " + str(len(ps)) + " modules")


    import timeit

    numberOfTests = 1
    time = timeit.timeit("test()", setup="from __main__ import test", number=numberOfTests)/numberOfTests
    print("Average time for " + str(numberOfTests) + " test iterations: " + str(time))

    ######################
    # Specific tests

    print("\nCreation")
    pl = ParametricLSystem(verbose=True)

    print("\nAdd define")
    pl.addGlobalDefine("a",1)
    print(pl.globalDefines)

    print("\nOverride define")
    pl.overrideGlobalDefine("a",2)
    print(pl.globalDefines)

    print("\nSet axiom")
    pl.setAxiomFromString("A")
    print(pl)

    print("\nAdd production: from string")
    pl.addProductionFromString("F:*->FA")
    print(pl)

    print("\nAdd production: from existing")
    pp = ParametricProduction()
    pp.parseString('F:*->FF')
    pl.addExistingProduction(pp)
    print(pl)

    print("\nCheck all global defines")
    pl.printGlobalDefinesStatus()

    print("\nFinish testing  ParametricLSystem")
