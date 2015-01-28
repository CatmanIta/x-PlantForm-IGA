"""
    Class for generating L-System structures incrementally.
    Extends the Random Generator with incremental operators.

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

# This code needed for blender to load correctly updated source files
import procedural.randomgenerator
import procedural.core.mutation
import procedural.miscellaneous.utilities

import imp
imp.reload(procedural.randomgenerator)
imp.reload(procedural.core.mutation)
imp.reload(procedural.miscellaneous.utilities)

from procedural.randomgenerator import *
from procedural.core.mutation import Mutation
from procedural.miscellaneous.utilities import Utilities


# TODO: I should make all pstring methods work on the same pstring, instead of copying it!

class IncrementalGenerator(RandomGenerator):
    """
    Generates a L-system following incremental steps. Allows more control.
    """

    def __init__(self,
                 randomSeed = 0,
                 parameterized = True,
                 definesProbability = 0.5,
                 constantsProbability = 0.0,
                 verbose = False,
                 verbose_super = False
                 ):
        RandomGenerator.__init__(self,randomSeed,parameterized,definesProbability,constantsProbability,verbose)

        self.mutation_steps_at_once = MUTATION_STEPS_AT_ONCE

        self.complexificationThreshold = 0.55     # [0,1] Above this, complexify
        self.simplificationThreshold = 0.25       # [0,1] Below this, simplify (between the two, modify)

        # Mutations
        self.mutations_library = {}
        self.loadMutationsLibrary()

    def loadMutationsLibrary(self):
        """ Can be extended with additional mutations. """
        self.mutations_library["add_module_production"] = Mutation(self.addRandomModuleToRandomProduction,"added a random Module to an existing production",10)
        self.mutations_library["remove_module_production"] = Mutation(self.removeRandomModuleFromRandomProduction,"removed a random Module from an existing production",5)
        self.mutations_library["change_module_production"] = Mutation(self.changeRandomModuleInRandomProduction,"changed a random Module in an existing production",12)
        self.mutations_library["add_production"] = Mutation(self.addNewProductionFromCurrentModules,"added a new production from an existing Module",4)
        self.mutations_library["remove_production"] = Mutation(self.deleteRandomProduction,"deleted an existing production",2)
        self.mutations_library["add_module_axiom"] = Mutation(self.addRandomModuleToAxiom,"added a random Module in the axiom",3)
        self.mutations_library["remove_module_axiom"] = Mutation(self.removeRandomModuleFromAxiom,"deleted a random Module from the axiom",3)
        self.mutations_library["change_module_axiom"] = Mutation(self.changeRandomModuleInAxiom,"changed a random Module in the axiom",3)

        # Stochastic
        self.mutations_library["split_production"] = Mutation(self.splitRandomProductionRandomly,"split a production into two with stochastic variations",5)
        self.mutations_library["change_stochastic_production"] = Mutation(self.changeRandomStochasticProduction,"change the weight of a stochastic production",5)

        # Parametric
        self.mutations_library["change_parameter_expression"] = Mutation(self.changeRandomParameterInRandomProduction,"change a parameter in a production into a different parameter",5)

    def logicallyRandomize(self, nComplexificationSteps = 6):
        """
        Randomize all the values of the current L-System.
        This is done in a more 'logical' way than simply randomizing, by using multiple complexifying mutations
        """
        self.resetToSimple() # We always start from a simple LSystem

        # Performs some complexifying mutations
        for i in range(nComplexificationSteps):
            if self.verbose: print("---- Complexification iteration " + str(i) + "----")
            self.mutationComplexify()
            if self.verbose: print("After complexification at "+str(i)+": " + str(self.lsystem))

    ################
    #--- Mutations
    ################

    def getMutation(self,name):
        return self.mutations_library[name]

    def addMutationChoice(self,name,condition,availableMutations,weights):
        m = self.getMutation(name)
        w = m.weight
        if condition:
            availableMutations.append(m)
            weights.append(w)
        else:
            w = 0
        if self.verbose_super: print("Choice - " + str(m.description) + " has weight " + str(w) + " tot: " + str(sum(weights)))
        return w

    def chooseAndPerformMutation(self,availableMutations,weights):
        """
        Given a set of mutations and their weights, chooses one and executes it.
        """
        tot_weight = sum(weights)
        mutation = None
        choice = self.rnd.randint(0,tot_weight)
        cumulative_weight = 0
        #if self.verbose_super: print("CHOICE: " + str(choice) + "  TOT: " + str(tot_weight))
        for i in range(len(availableMutations)):
            cumulative_weight += weights[i]
            #if self.verbose_super: print("MUT: " + availableMutations[i].description + " CHOICE: " + str(choice) + "  CUMUL: " + str(cumulative_weight))
            if choice <= cumulative_weight:
                mutation = availableMutations[i]
                break

        if mutation and tot_weight > 0:
            mutation.execute()
            if self.verbose: print("Chosen mutation: " + mutation.description)
        else:
            if self.verbose: print("Cannot perform any mutation")

        #print("Result axiom: " + str(self.lsystem.axiom))

    def mutationAnyMultipleTimes(self):
        """
        Perform mutationAny. Done mutation_steps_at_once times.
        """
        for i in range(self.mutation_steps_at_once):
            if self.verbose:
                print("Current lsystem: " + str(self.lsystem))
                print("------------------- Mutation " + str(i) + "---------------")
                #print("Current axiom: " + str(self.lsystem.axiom))
            self.mutationAny()

    def mutationAny(self):
        """
        Perform a random mutation, either simplifying, modifying, or complexifying.
        Varies according to the thresold ratios.
        """
        complexificationRatio = self.complexificationThreshold # Above this, complexify
        simplificationRatio = self.simplificationThreshold  # Below this, simplify

        if     self.rnd.random() <= simplificationRatio:        self.mutationSimplify()
        elif   self.rnd.random() <= complexificationRatio:      self.mutationModify()
        else:      self.mutationComplexify()

    def mutationComplexify(self):
        """ Augment complexity. Done once. """
        availableMutations = []
        weights = []
        self.loadComplexifyMutationChoices(availableMutations,weights)
        self.chooseAndPerformMutation(availableMutations,weights)

    def mutationModify(self):
        """ Keep complexity, but change the productions """
        availableMutations = []
        weights = []
        self.loadModifyingMutationChoices(availableMutations,weights)
        self.chooseAndPerformMutation(availableMutations,weights)

    def mutationSimplify(self):
        """ Diminish complexity """
        availableMutations = []
        weights = []
        self.loadSimplifyingMutationChoices(availableMutations,weights)
        self.chooseAndPerformMutation(availableMutations,weights)


    def loadComplexifyMutationChoices(self,availableMutations,weights):
        """
        Chooses which mutations are complexifying.
        Can be extended to achieve specific generator behaviors.
        """
        self.addMutationChoice("add_module_axiom",self.lsystem.axiom.lengthWithoutBrackets() < MAX_AXIOM_LENGTH, availableMutations, weights)
        self.addMutationChoice("add_production",len(self.lsystem.productions) < MAX_N_PRODUCTIONS and self.hasLettersNotUsedInPrecedents(), availableMutations, weights)
        self.addMutationChoice("add_module_production",len(self.lsystem.productions )> 0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH), availableMutations, weights)

        # No stochastic variations, as they are hard to control with interactive incremental generation!
        #self.addMutationChoice("split_production",len(self.lsystem.productions) > 0 and len(self.lsystem.productions) < MAX_N_PRODUCTIONS, availableMutations, weights)
        #TODO: self.addMutationChoice("change_stochastic_production",len(self.lsystem.productions) > 0 and self.getRandomExistingStochasticProduction() != None, availableMutations, weights)

    def loadModifyingMutationChoices(self,availableMutations,weights):
        """
        Chooses which mutations are modifying.
        Can be extended to achieve specific generator behaviors.
        """
        self.addMutationChoice("change_module_axiom", True, availableMutations, weights)
        self.addMutationChoice("change_module_production",len(self.lsystem.productions) > 0, availableMutations, weights)
        self.addMutationChoice("change_parameter_expression",(len(self.lsystem.productions) > 0 and self.parameterized is True), availableMutations, weights)

    def loadSimplifyingMutationChoices(self,availableMutations,weights):
        """
        Chooses which mutations are simplifying.
        Can be extended to achieve specific generator behaviors.
        """
        self.addMutationChoice("remove_module_axiom",self.lsystem.axiom.lengthWithoutBrackets() > MIN_AXIOM_LENGTH, availableMutations, weights)
        self.addMutationChoice("remove_module_production",len(self.lsystem.productions) > 0, availableMutations, weights)
        self.addMutationChoice("remove_production",len(self.lsystem.productions) > 0, availableMutations, weights)



    ######################################
    #--- Randomized operations
    ######################################
    # TODO: those should probably be part of the generic Randomizer!

    def splitRandomProductionRandomly(self):
        production, production_index = self.getRandomExistingProduction()
        self.splitProductionRandomly(production,production_index)

    def splitProductionRandomly(self,production,production_index):
        """ Splits a production into two productions, with stochastic probabilities that sum to 1 """

        # Remove the chosen production
        self.deleteProductionAt(production_index,redistribute = False)

        initialConditionValue = production.condition.value

        # Choose a split value
        split_value = Utilities.getRandomTwoDigitFloat(self.rnd,0,initialConditionValue)

        # Create two mutated productions from the original and add them
        successor = self.mutateProductionSuccessorRandomly(production.successor)
        stochastic_value = "{0:.2f}".format(split_value)
        self.addProductionFromElements(production.predecessor, stochastic_value, successor)

        #print("New production 1: " + str(production[0] + " -- " + str(stochastic_value) + " -- " + productionSubsequent))

        successor = self.mutateProductionSuccessorRandomly(production.successor)
        stochastic_value = "{0:.2f}".format(initialConditionValue-split_value)
        self.addProductionFromElements(production.predecessor, stochastic_value, successor)

        #print("New production 2: " + str(production[0] + " | " + str(stochastic_value) + " | " + productionSubsequent))

    def mutateProductionSuccessorRandomly(self,successor):
        if successor.lengthWithoutBrackets() <= MIN_TOTAL_STRING_LENGTH: choice = self.rnd.randint(0,1)
        elif successor.lengthWithoutBrackets() >= MAX_TOTAL_STRING_LENGTH: choice = self.rnd.randint(1,2)
        else: choice = self.rnd.randint(0,2)

        if choice == 0:     successor = self.addRandomModule(successor)
        elif choice == 1:   successor = self.changeRandomModule(successor)
        elif choice == 2:   successor = self.removeRandomModule(successor)
        return successor

    def changeRandomStochasticProduction(self):
        changed_production = self.getRandomExistingStochasticProduction()

        random_change = self.rnd.uniform(-0.5,0.5)
        new_value = changed_production.condition.value + random_change
        new_value = max(0.1, min(new_value, 0.9))
        delta_change = new_value-changed_production.condition.value

        changed_production.condition.value = new_value

        self.redistributeStochasticValue(changed_production.predecessor.letter,-delta_change,excludedProduction=changed_production)


    def addRandomModuleToRandomProduction(self):
        production, index = self.getRandomExistingProduction(maxLength = MAX_TOTAL_STRING_LENGTH)
        production.successor = self.addRandomModule(production.successor)

    def removeRandomModuleFromRandomProduction(self):
        production, index = self.getRandomExistingProduction()
        production.successor = self.removeRandomModule(production.successor)

        # Also delete the production if the subsequent is now empty
        if len(production.successor) == 0: self.deleteProductionAt(index)

    def changeRandomModuleInRandomProduction(self):
        production, index = self.getRandomExistingProduction()
        production.successor = self.changeRandomModule(production.successor)

    def addRandomModuleToAxiom(self):
        #print("Current axiom: " + str(self.lsystem.axiom))
        self.lsystem.axiom = self.addRandomModule(self.lsystem.axiom)

    def removeRandomModuleFromAxiom(self):
        self.lsystem.axiom = self.removeRandomModule(self.lsystem.axiom)

    def changeRandomModuleInAxiom(self):
        self.lsystem.axiom = self.changeRandomModule(self.lsystem.axiom)

    def addNewProductionFromCurrentModules(self):
        m = self.generateRandomPredecessorFromCurrentlyUsedModules()
        if m == None:
            print("Cannot add new production! No Modules are left!")
            return
        self.addProductionFromElements(m,"*",self.generateRandomSuccessorForPredecessor(m))


    # Successor

    def generateRandomSuccessorForPredecessor(self,predecessor_module):
        return self.generateRandomParametricString(predecessor_module = predecessor_module)

    def appendModuleOfLetterFromPredecessor(self,letter,input_successor,predecessor_module, forcedParameter = None):
        output_successor = self.appendModuleOfLetter(letter,input_successor)
        if forcedParameter is not None:
            output_successor.setParameterToModulesOfLetter(letter,forcedParameter)
        else:
            self.changeRandomlyParametersFromPredecessor(output_successor,predecessor_module)
        return output_successor

    def changeRandomlyParametersFromPredecessor(self,successor,predecessor_module):
        # Change some of the parameters to the predecessor module's variable parameters
        if self.parameterized:
            if predecessor_module is not None:
                #potential_changed_modules = successor.modulesList
                #potential_changed_modules = list(filter(lambda p: not p.isBracket(), successor.modulesList))
                potential_changed_modules = successor.getActualModules() # NOTE: this should do the same as above

                # Each predecessor parameter is copied once, if possible
                for param in predecessor_module.params:
                    chosen_module = self.getRandomItemFromList(potential_changed_modules)
                    #if len(chosen_module.params) > 0:
                    index = self.rnd.randint(0,len(chosen_module.params)-1)
                    chosen_module.params[index] = param

    # Parameters

    def changeRandomParameterInRandomProduction(self):
        production, index = self.getRandomExistingProduction()
        production.successor = self.changeRandomParameter(production.successor,production.predecessor)


    def changeRandomParameterInAxiom(self):
        self.lsystem.axiom = self.changeRandomParameter(self.lsystem.axiom)


    def changeRandomParameter(self, pString, predecessor_module = None):
        """
        Changes a random parameter in one of the modules of this parametric string into another parameter.
        """
        #TODO: optionally use defines too

        pString = ParametricString.copyFrom(pString)
        #print("We are changing pString: " + str(pString))

        # Choose the module
        actualModules = pString.getActualModules()
        module = self.getRandomItemFromList(actualModules)
        #print("Module " + str(module) +  " has parameters: " + str(module.params))

        # Choose what parameter to change
        choice = self.rnd.randint(0,len(module.params)-1)
        parameterToChange = module.params[choice]
        #print("We will change parameter " + str(choice) + ": " + str(parameterToChange))

        # Choose what to change it into
        usePredecessorParameter = False
        if predecessor_module is not None:
            usePredecessorParameter = self.rnd.random() <= 0.5

        #print("Using predecessor parameter? " + str(usePredecessorParameter))
        if usePredecessorParameter:
            changeTo = self.getRandomItemFromList(predecessor_module.params)  # TODO: use other parameters too
        else:
            genModule = self.template_modules_library.getTemplateModuleByLetter(module.letter)
            changeTo = genModule.generateConstantParameterValue(self.rnd)

        # Optionally, multiply by a constant
        if self.rnd.random() <= 0.5:
            changeTo = str(changeTo) + "*" + str(Utilities.getRandomTwoDigitFloat(self.rnd,0.5,2.0))

        module.params[choice] = changeTo
        #print("We changed it to: " + str(changeTo))

        #print("The resulting pString is: " + str(pString))
        return pString

    ##############
    #--- Checks
    ##############

    # TODO: This should be similar to RandomGenerator.getRandomExistingProduction PROBABLY MERGE THEM!!!
    """def hasProductionsShorterThan(self, maxLength, doNotConsiderProductionWithPredecessor=None,
                                    containedLetters = []):
        for production_index in range(self.getNumberOfExistingProductions()):
            production = self.lsystem.productions[production_index]
            if doNotConsiderProductionWithPredecessor is not None and production.predecessor.letter == doNotConsiderProductionWithPredecessor: continue
            if len(production.successor) < maxLength: return True
        return False"""


if __name__ == "__main__":
    import time
    print("Start testing IncrementalGenerator")

    print("\nTEST - Creation")
    ig = IncrementalGenerator(verbose=True, verbose_super=True)
    print(ig)

    print("\nTEST - Reset to simple")
    ig.resetToSimple()
    print(ig)

    print("\nTEST - Logically Randomize")
    ig.logicallyRandomize(nComplexificationSteps=6)
    print(ig)

    print("\nTEST - Complexify")
    ig.mutationComplexify()
    print(ig)

    print("\nTEST - Modify")
    ig.mutationModify()
    print(ig)

    print("\nTEST - Simplify")
    ig.mutationSimplify()
    print(ig)

    print("\nTEST - Mutation any (N times)")
    t0 = time.clock()
    ig.mutation_steps_at_once = 100
    ig.mutationAnyMultipleTimes()
    print(ig)
    print(time.clock()-t0)

    print("\nFinish testing IncrementalGenerator")
