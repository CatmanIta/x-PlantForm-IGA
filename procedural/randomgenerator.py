"""
    Class for generating L-System structures procedurally

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import grammar.parametric.parametricproduction
import grammar.parametric.parametricmodule
import grammar.parametric.parametricstring
import grammar.parametric.parametriclsystem
import procedural.core.modulestemplatelibrary
import procedural.core.configuration
import procedural.miscellaneous.utilities

import imp
imp.reload(grammar.parametric.parametricproduction)
imp.reload(grammar.parametric.parametricmodule)
imp.reload(grammar.parametric.parametricstring)
imp.reload(grammar.parametric.parametriclsystem)
imp.reload(procedural.core.modulestemplatelibrary)
imp.reload(procedural.core.configuration)
imp.reload(procedural.miscellaneous.utilities)

from grammar.parametric.parametricproduction import ParametricProduction
from grammar.parametric.parametricmodule import ParametricModule
from grammar.parametric.parametricstring import ParametricString
from grammar.parametric.parametriclsystem import ParametricLSystem
from procedural.core.modulestemplatelibrary import ModulesTemplateLibrary
from procedural.core.configuration import *
from procedural.miscellaneous.utilities import Utilities


import random, math

class RandomGenerator():
    """
    Randomly generates a L-system with a uniform distribution.
    """

    def __init__(self,
                 randomSeed = 0,
                 parameterized = True,
                 definesProbability = 0.5,
                 constantsProbability = 0.0,
                 verbose = False,
                 verbose_super = False):
        """
        Randomly changes values of the L-System.
        """
        self.verbose = verbose
        self.verbose_super = verbose

        self.lsystem = ParametricLSystem()    # Init with a empty Lsystem

        self.parameterized = parameterized
        self.rnd = random.Random()
        if randomSeed > 0: self.rnd.seed(randomSeed)

        self.template_modules_library = ModulesTemplateLibrary(self,self.rnd,parameterized,definesProbability,constantsProbability)

        # Parameters
        self.targetIterations = 3               # How many iterations for the resulting lsystem
        self.branchProbability = 0.5            # [0,1] @note: Used only when generating a random pstring
        self.branchCloseProbability = 0.2       # [0,1] If high, it will close branches soon after opening them. If low, it will let them be larger.
        #self.definesProbability =  0.5          # [0,1]
        #self.constantsProbability =  1.0        # [0,1]

    def __str__(self):
        s = "Randomizer"
        if self.lsystem is not None: s += " with lsystem " + str(self.lsystem)
        return s

    def setLSystem(self,lsystem):
        """
        Sets the L-System that will be modified

        @param lsystem: The L-System to modify.
        @type lsystem: ParametricLSystem
        """
        self.lsystem = lsystem
        self.updateCurrentlyUsedLetters()

    def clear(self):
        """
        Sets empty values
        """
        self.lsystem.clear()
        self.updateCurrentlyUsedLetters()

    def resetToSimple(self):
        """
        Resets the L-System to a simple format
        """
        self.clear()
        self.createSimpleLSystem()

    def createSimpleLSystem(self):
        """
        Creates the simplest Lsystem for this generator. Can be extended.
        """
        self.lsystem.setIterations(self.targetIterations)
        self.lsystem.setAxiomFromString("")
        self.lsystem.axiom.appendModule(self.generateModuleOfLetter("F"))
        self.updateCurrentlyUsedLetters()

    def updateCurrentlyUsedLetters(self):
        """
        Updates the list of ParametricModule letters that are already in use in the current L-System.
        """
        self.currentlyUsedLetters = []

        def checkAddToCurrentlyUsedLetters(self,s):
            if s not in self.currentlyUsedLetters:
                self.currentlyUsedLetters.append(s)

        parametricAxiom = self.lsystem.axiom
        if parametricAxiom is not None:
            available_letters = [m.letter for m in self.template_modules_library.getTemplateModules()]
            for pModule in parametricAxiom:
                if pModule.letter in available_letters: checkAddToCurrentlyUsedLetters(self,pModule.letter)

        for production in self.lsystem.productions:
            if production.predecessor.letter in available_letters: checkAddToCurrentlyUsedLetters(self,production.predecessor.letter)
            for pModule in production.successor:
                if pModule.letter in available_letters: checkAddToCurrentlyUsedLetters(self,pModule.letter)

    def randomize(self):
        """
        Randomize all the values of the current L-System.
        """
        self.lsystem.clear()
        #self.lsystem.setIterations(self.rnd.randint(MIN_RANDOM_ITERATIONS,MAX_RANDOM_ITERATIONS))
        self.lsystem.setIterations(self.targetIterations)   # The iterations are fixed

        ndefines = self.rnd.randint(MIN_RANDOM_DEFINES,MAX_RANDOM_DEFINES)
        self.generateRandomDefines(ndefines)

        self.lsystem.axiom = self.generateRandomParametricString()

        nproductions = self.rnd.randint(MIN_RANDOM_PRODUCTIONS,MAX_RANDOM_PRODUCTIONS)
        self.generateRandomProductions(nproductions)

    def generateRandomDefines(self,ndefines):
        for i in range(ndefines): self.generateRandomDefine()

    def generateRandomDefine(self):
        return self.addGlobalDefine("d"+str(len(self.lsystem.globalDefines)),
                                    Utilities.getRandomTwoDigitFloat(self.rnd,MIN_DEFINE_VALUE,MAX_DEFINE_VALUE))


    def generateRandomProductions(self,nproductions):
        for i in range(nproductions):
            self.generateAndAddRandomProduction()

    ########################
    # Utilities
    ########################


    # Modules from templates

    def generatePredecessorOfLetter(self,letter):
        """ Generates a Predecessor Module from a letter """
        templateModule = self.template_modules_library.getTemplateModuleByLetter(letter)
        module = self.template_modules_library.createActualModuleFromTemplate(templateModule, isPredecessor = True)
        return module

    def generateModuleOfLetter(self,letter):
        """ Generates a Module from a letter """
        templateModule = self.template_modules_library.getTemplateModuleByLetter(letter)
        module = self.template_modules_library.createActualModuleFromTemplate(templateModule)
        return module

    def generateRandomModule(self, notUsingModules = []):
        """ Returns a random Module """
        notUsingLetters = list(m.letter for m in notUsingModules)
        templateModules = self.template_modules_library.getTemplateModules()
        templateModules = list(filter(lambda m: m.letter not in notUsingLetters, templateModules))
        templateModules = self.getRandomItemFromList(templateModules)
        module = self.template_modules_library.createActualModuleFromTemplate(templateModules)
        return module

    # Modules from other stuff

    def generateWeightedRandomModule(self):
        """ Returns a random ParametricModule based on the supplied weights """
        templateModules = self.template_modules_library.getTemplateModules()
        templateModule = self.getRandomItemFromWeightedList([s for s in templateModules],[s.weight for s in templateModules])
        module = self.template_modules_library.createActualModuleFromTemplate(templateModule)
        return module

    def generateRandomCurrentModule(self):
        """ Returns a random ParametricModule from the currently used ones """
        module = ParametricModule(self.getRandomItemFromList(self.currentUsedModules))
        return module

    def generateRandomCurrentModuleNotUsedAsPrecedent(self):
        """
        Returns a random ParametricModule from the currently used ones, if not already used in a predecessor.
        Also makes sure the module has correct parameters.
        """
        #print(self.lsystem)
        notUsedAsPrecedentLetters = list(filter(self.letterIsNotUsedAsPrecedent,self.currentlyUsedLetters))
        #print("Not used as precedent letters: " + str(notUsedAsPrecedentLetters))
        if len(notUsedAsPrecedentLetters) == 0: return None
        letter = self.getRandomItemFromList(notUsedAsPrecedentLetters)
        #print("Chosen letter: " + str(letter))
        module = self.generatePredecessorOfLetter(letter)
        return module

    def generateRandomPredecessor(self):
        return self.generateRandomModule()

    def generateRandomPredecessorFromCurrentlyUsedModules(self):
        return self.generateRandomCurrentModuleNotUsedAsPrecedent()

    # Checks for modules

    def hasLettersNotUsedInPrecedents(self):
        notUsedAsPrecedentLetters = list(filter(self.letterIsNotUsedAsPrecedent,self.currentlyUsedLetters))
        return len(notUsedAsPrecedentLetters) > 0

    def letterIsNotUsedAsPrecedent(self,s):
        for prod in self.lsystem.productions:
            if s == prod.predecessor.letter: return False
        return True

    # Parametric Strings

    def generateRandomParametricString(self, minLength = MIN_GENERATED_STRING_LENGTH, maxLength = MAX_GENERATED_STRING_LENGTH, predecessor_module = None):
        """
        Generates a random string composed of ParametricModules.
        May also randomly open and close branches.
        May also randomly add new defines.
        Forces the string's validity.

        If a predecessor_module is passed, its parameter variables (x,y) need to appear in the generated string
        We add them to the current generated string at the end.
        """
        if self.branchProbability > 0.0: openBranches = 0
        n_modules = self.rnd.randint(minLength,maxLength)
        pstring = ParametricString()
        pstring.setGlobals(self.lsystem.globalDefines)

        for i in range(n_modules):  # We add N modules

            # Generate the module
            new_module = self.generateWeightedRandomModule()#parametric=True)

            # Randomly open branches (NOT: only if the module is a new rotation, otherwise it doesn't make sense)
            if self.branchProbability > 0.0:
                if openBranches > 0 and self.rnd.random() < self.branchCloseProbability:
                    pstring.appendCloseBranch()
                    openBranches -= 1
                if self.rnd.random() < self.branchProbability:   #new_module.isOrientation() and
                    pstring.appendOpenBranch()
                    openBranches += 1

            # Append the module
            pstring.appendModule(new_module)

        # Close the remaining branches
        if self.branchProbability > 0.0:
            for i in range(openBranches): pstring.appendCloseBranch()

        # Change some of the parameters to the predecessor module's variable parameters
        if self.parameterized:
            print("PRED: " + str(predecessor_module))
            if predecessor_module is not None:
                potential_changed_modules = pstring.modulesList
                potential_changed_modules = list(filter(lambda p: not p.isBracket(), pstring.modulesList))

                #print "Potential changed modules: "
                #for m in potential_changed_modules: print m

                # Each predecessor parameter is copied once, if possible
                for param in predecessor_module.params:
                    chosen_module = self.getRandomItemFromList(potential_changed_modules)
                    #if len(chosen_module.params) > 0:
                    index = self.rnd.randint(0,len(chosen_module.params)-1)
                    chosen_module.params[index] = param

        return pstring

    def generateEmptyParametricString(self):
        pstring = ParametricString()
        pstring.setGlobals(self.lsystem.globalDefines)
        return pstring

    # Defines

    def addGlobalDefine(self,name,value):
        return self.lsystem.addGlobalDefine(name,value)

    def overrideGlobalDefine(self,i,name,value):
        self.lsystem.overrideGlobalDefine(i,name,value)

    # Productions

    def getProduction(self,i):
        return self.lsystem.productions[i]

    def addExistingProduction(self,prod):
        self.lsystem.addExistingProduction(prod)

    def addNewProduction(self):
        return self.lsystem.addNewProduction()

    def addProductionFromElements(self,pre,cond,succ):
        prod = self.addNewProduction()
        prod.setPredecessorModule(pre)
        prod.setConditionFromString(cond)
        prod.setSuccessorPstring(succ)
        return prod

    def overrideProduction(self,i,prod):
        self.lsystem.overrideProduction(i,prod)

    def deleteProductionAt(self,index,redistribute = True):
        """
        Delete a production.

        @param redistribute: If True and the deleted production was stochastic, the remaining value is redistributed.
        @type redistribute: bool
        """
        deleted_production = self.lsystem.productions[index]
        del  self.lsystem.productions[index]

        if redistribute:
            # If this production was stochastic, we need to redistribute its weight to the other productions with the same predecessor
            condition_type = deleted_production.condition.type
            if condition_type == '#':
                predecessor_letter = deleted_production.predecessor.letter
                condition_value = deleted_production.condition.value
                self.redistributeStochasticValue(predecessor_letter,condition_value)

        return deleted_production

    def redistributeStochasticValue(self,predecessor_letter,redistributed_value,excludedProduction=None):
        remaining_value = 1-redistributed_value
        print("Redistributing weight: the weight to distribute is " + str(redistributed_value) + " and the remanining weight is " + str(remaining_value))
        for prod in self.lsystem.productions:
            if prod.predecessor.letter == predecessor_letter and prod != excludedProduction:
                print("Production has value " + str(prod.condition.value))
                prod.condition.value = round((prod.condition.value+prod.condition.value/redistributed_value*redistributed_value)*100)/100.0
                print("Production is thus given value " + str(prod.condition.value))

    def generateAndAddRandomProduction(self):
        #TODO: Add stochastic variations
        self.addProductionFromElements(self.generateRandomPredecessor(),"*",self.generateRandomParametricString())

    def getNumberOfExistingProductions(self):
        return len(self.lsystem.productions)

    def getRandomExistingProduction(self, maxLength = None, containedLetters=[],
                                    atLeastCountLetters = 1,
                                    doNotConsiderProductionWithPredecessor=None,
                                    containsBranches = None):
        """
        Returns one of the existing productions.
        Ignores productions that reached maxLength with their successor.
        Returns None if no production exists
        """
        if self.getNumberOfExistingProductions() == 0: return None, -1

        availableIndices = self.getAllProductionIndicesWith(maxLength,containedLetters,atLeastCountLetters,doNotConsiderProductionWithPredecessor,containsBranches)

        production_index = self.getRandomItemFromList(availableIndices)
        if len(availableIndices) == 0: return None, -1
        return self.lsystem.productions[production_index], production_index

    def getAllProductionIndicesWith(self, maxLength = None, containedLetters=[],
                                    atLeastCountLetters = 1,
                                    doNotConsiderProductionWithPredecessor=None,
                                    containsBranches = None):
        availableIndices = [i for i in range(self.getNumberOfExistingProductions())]
        for production_index in range(self.getNumberOfExistingProductions()):
            production = self.lsystem.productions[production_index]
            successor = production.successor
            if maxLength and len(successor) > maxLength:
                availableIndices.remove(production_index)
            elif containsBranches is not None and successor.hasBranches() != containsBranches:
                availableIndices.remove(production_index)
            elif len(containedLetters)>0 and not successor.containsAllLettersAtLeastCount(containedLetters,atLeastCountLetters):
                availableIndices.remove(production_index)
            elif doNotConsiderProductionWithPredecessor is not None and production.predecessor.letter == doNotConsiderProductionWithPredecessor:
                availableIndices.remove(production_index)
        if len(availableIndices) == 0: return []
        return availableIndices

    def hasProductionsWith(self, maxLength = None, containedLetters=[],
                                    atLeastCountLetters = 1,
                                    doNotConsiderProductionWithPredecessor=None,
                                    containsBranches = None):
        availableIndices = self.getAllProductionIndicesWith(maxLength,containedLetters,atLeastCountLetters,doNotConsiderProductionWithPredecessor,containsBranches)
        return len(availableIndices) > 0


    def getRandomExistingStochasticProduction(self):
        def isStochastic(production): return production.condition.type == '#'
        prods = list(filter(isStochastic,self.lsystem.productions))
        return self.getRandomItemFromList(prods)

    # Various
    def getRandomItemFromList(self,list):
        if len(list) == 0: return None
        return list[self.rnd.randint(0,len(list)-1)]

    def getRandomItemFromWeightedList(self,list,weights):
        if len(list) == 0: return None
        assert(len(list) == len(weights))
        tot_weight = 0
        n = range(len(list))
        tot_weight = sum(weights)

        choice = self.rnd.randint(0,tot_weight)
        cumulative_weight = 0
        for i in n:
            cumulative_weight += weights[i]
            if choice <= cumulative_weight:
                return list[i]
        assert(False)  # Should never pass here


    #####################
    # Mutations
    #####################

    def appendModuleOfLetter(self,letter,pString):
        new_module = self.generateModuleOfLetter(letter)
        return self.appendModuleToPstring(new_module,pString)

    def appendModuleToPstring(self,new_module,pString):
        pString = ParametricString.copyFrom(pString)
        pString.modulesList.append(new_module)
        if new_module.letter not in self.currentlyUsedLetters:  self.currentlyUsedLetters.append(new_module.letter)
        return pString

    def insertModuleOfLetterRandomly(self,letter,pString):
        new_module = self.generateModuleOfLetter(letter)
        return self.insertModuleIntoPstringRandomly(new_module,pString)

    def insertModuleIntoPstringRandomly(self,new_module,pString):
        pString = ParametricString.copyFrom(pString)
        index = self.rnd.randint(0,len(pString))    # Max is len(pString) so that we can also insert at the end
        pString.modulesList.insert(index,new_module)
        if new_module.letter not in self.currentlyUsedLetters:  self.currentlyUsedLetters.append(new_module.letter)
        return pString

    def addRandomModule(self,pString):
        """
        Add a random Module to a ParametricString, chosen from the available ones.
        This may select an unused Module too.
        #TODO: this is actually an "insertInRandomModule"
        """
        #print("Current pString: " + str(pString))
        pString = ParametricString.copyFrom(pString)
        new_module = self.generateWeightedRandomModule()#parametric=True)
        index = self.rnd.randint(0,len(pString))    # Max is len(pString) so that we can also insert at the end
        #print("From string " + str(pString) + " we add at index " + str(index) + " a new Module " + str(new_module))
        pString.modulesList.insert(index,new_module)
        #print("Result: " + str(pString))

        if new_module.letter not in self.currentlyUsedLetters:
            self.currentlyUsedLetters.append(new_module.letter)

        return pString

    def removeModuleOfLetter(self,letter,pString):
        module = pString.getFirstModuleOfLetter(letter)
        return self.removeModule(module, pString)

    # TODO: all these 'append', 'remove', 'insert' and so on would be better placed in the ParametricString class
    def removeModule(self,module,input_pstring):
        #print(module)
        #print(pString)
        output_pstring = ParametricString.copyFrom(input_pstring)
        if module in input_pstring.modulesList:
            index = input_pstring.index(module)
            removeBrackets = self.checkBracketsRemoval(index,output_pstring)
            del output_pstring.modulesList[index]
            if removeBrackets: self.performBracketsRemoval(index,output_pstring)
        return output_pstring

    def checkBracketsRemoval(self,index,pString):
        # We check if we need to remove the brackets: if no other module is around the chosen index
        return index > 0 and index < len(pString)-1 and pString[index-1].isOpenBracket() and pString[index+1].isClosedBracket()

        """print(index>0)
        print( len(pString)-1)
        print(index < len(pString)-1 )
        print(pString[index-1] )
        print(str(pString[index-1]) == '[')
        if index < len(pString)-1:
            print(pString[index+1] )
            print(type(pString[index+1]))
            print(str(pString[index+1]) == "]")
        print("\nWe got pString: " + str(pString))
        print("We'll remove at index " + str(index) + " the letter " + str(pString[index]))
        print("Also removing brackets? " + str(removeBrackets))"""

    def performBracketsRemoval(self,index,pString):
        removeBrackets = True
        while removeBrackets is True:
            #print("Now pString is " + str(pString))
            del pString.modulesList[index]
            #print("Now pString is " + str(pString))
            del pString.modulesList[index-1]
            #print("Now pString is " + str(pString))
            #if len(pString) > 0: print("At left we now have " + str(pString[index-2]))

            # Keep checking for brackets
            index = index-1
            if not self.checkBracketsRemoval(index,pString):
                #print("We finished removing brackets!")
                removeBrackets = False
            #else:
                #print("We still need to remove brackets!")

        #print("Final pString is " + str(pString) +"\n")
        return pString

    def removeRandomModule(self,pString):
        pString = ParametricString.copyFrom(pString)
        available_letters = [m.letter for m in self.template_modules_library.getTemplateModules()]
        while True:
            index = self.rnd.randint(0,len(pString)-1)
            if not pString[index].isBracket() and pString[index].letter in available_letters: break

        # We also remove the brackets if no other module is there
        removeBrackets = self.checkBracketsRemoval(index, pString)
        del pString.modulesList[index]
        if removeBrackets: self.performBracketsRemoval(index, pString)
        #TODO: Do something if we completely remove this production
        return pString

    def changeRandomModule(self,pString):
        pString = ParametricString.copyFrom(pString)
        available_letters = [m.letter for m in self.template_modules_library.getTemplateModules()]

        # Choose what module we want to change
        modules = pString.getActualModules()
        modules = list(filter(lambda m: m.letter in available_letters,modules))
        index = self.rnd.randint(0,len(modules)-1)
        module_to_change = modules[index]
        #print("We will change module at : " + str(index) + " " + str(module_to_change))

        # Choose what we will change it to, avoid replacing with the same letter
        new_module = self.generateRandomModule(notUsingModules = [module_to_change])
        #print("Changed to " + str(new_module))

        # If parameterized, we make sure that the parameter value remains the same, if possible
        if self.parameterized:
            for i in range(len(new_module.params)):
                if i < len(module_to_change.params):
                    new_module.params[i] = module_to_change.params[i]

        #print("From string " + str(string) + " we change module " + str(string[index]) + " at index " + str(index) + " to a new module " + new_module)
        pString.modulesList[pString.modulesList.index(module_to_change)] = new_module
        #print("Result: " + string)
        return pString

    def deleteRandomProduction(self):
        index = self.rnd.randint(0,len(self.lsystem.productions)-1)
        self.deleteProductionAt(index)


if __name__ == "__main__":
    print("Start testing RandomGenerator")

    print("\nTEST - Creation")
    rg = RandomGenerator(verbose = True, verbose_super = True)
    print(rg)

    print("\nTEST - Reset")
    rg.resetToSimple()
    print(rg)

    print("\nTEST - Clear")
    rg.clear()
    print(rg)

    print("\nTEST - Add Simple LSystem")
    rg.createSimpleLSystem()
    print(rg)

    print("\nTEST - Clear & Randomize everything")
    rg.clear()
    rg.randomize()
    print(rg)

    print("\nTEST - Clear & Add random defines")
    rg.clear()
    rg.generateRandomDefines(2)
    print(rg)

    print("\nTEST - Clear & Add random productions")
    rg.clear()
    rg.generateRandomProductions(3)
    print(rg)

    print("\nFinish testing RandomGenerator")
