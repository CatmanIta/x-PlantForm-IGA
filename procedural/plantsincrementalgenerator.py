"""
    Class for generating L-System structures incrementally that represent plants.

    Specific operators are created for mutations and crossover so that the structure of the tree is not broken at each step.
    We thus use operators such as:
        - add a branch
        - split a branch into two
        - add leaves
        - convert a leaf to a branch
        - etc...

    We also have constraints:
        - the initial structure has 3 productions:
            - A -> F
            - F -> F
            - ! -> !
        - The last (!) cannot be modified
        - At least an F must remain in the other two successors

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import procedural.incrementalgenerator
import grammar.parametric.parametriclsystem

import imp
imp.reload(procedural.incrementalgenerator)
imp.reload(grammar.parametric.parametriclsystem)

from procedural.incrementalgenerator import *
from grammar.parametric.parametriclsystem import *

# TODO: make some cleanups:
#        - if we have repeated branches, remove them (such as [[+!F]] <-- two branches

# TODO: add defines (they are useful to have consistence and self-similarity!)

# TODO: add 'copies': allow sub-pStrings in productions to be copied and repeated (I saw many plants having repetitions!)

class PlantsIncrementalGenerator(IncrementalGenerator):

    ##################
    # Extensions
    ##################

    def createSimpleLSystem(self):
        """
        The simplest LSystem is an already defined plant-like structure.
        """
        self.lsystem.setIterations(self.targetIterations)
        self.lsystem.setAxiomFromString("")
        self.lsystem.axiom.appendModule(self.generateModuleOfLetter("A"))

        # Advanced stub used as a starting plant

        # Growth
        production = self.addProductionFromElements(self.generatePredecessorOfLetter("A"),"*",self.generateEmptyParametricString())

        pString = self.generateEmptyParametricString()
        pString.appendModule(self.generateModuleOfLetter("!"))
        pString.appendModule(self.generateModuleOfLetter("F"))
        pString.appendOpenBranch()
        pString.appendModule(self.generateModuleOfLetter("-"))
        pString.appendModule(self.generateModuleOfLetter("A"))
        pString.appendCloseBranch()
        pString.appendOpenBranch()
        pString.appendModule(self.generateModuleOfLetter("+"))
        pString.appendModule(self.generateModuleOfLetter("A"))
        pString.appendCloseBranch()

        production.successor = pString

        # Length
        production = self.addProductionFromElements(self.generatePredecessorOfLetter("F"),"*",self.generateEmptyParametricString())
        production.successor = self.appendModuleOfLetterFromPredecessor("F",production.successor,production.predecessor)

        # Size
        production = self.addProductionFromElements(self.generatePredecessorOfLetter("!"),"*",self.generateEmptyParametricString())
        production.successor = self.appendModuleOfLetterFromPredecessor("!",production.successor,production.predecessor, forcedParameter = "x*1.2")


        """
        # Simple plant for starters

        # Growth
        production = self.addProductionFromElements(self.generatePredecessorOfLetter("A"),"*",self.generateEmptyParametricString())
        production.successor = self.appendModuleOfLetterFromPredecessor("A",production.successor,production.predecessor)
        production.successor = self.appendModuleOfLetterFromPredecessor("F",production.successor,production.predecessor)

        # Length
        production = self.addProductionFromElements(self.generatePredecessorOfLetter("F"),"*",self.generateEmptyParametricString())
        production.successor = self.appendModuleOfLetterFromPredecessor("F",production.successor,production.predecessor)

        # Size
        production = self.addProductionFromElements(self.generatePredecessorOfLetter("!"),"*",self.generateEmptyParametricString())
        production.successor = self.appendModuleOfLetterFromPredecessor("!",production.successor,production.predecessor)
        """


    def loadMutationsLibrary(self):

        # @note: we do not use 'append' anymore because we prefer 'insert'
        #self.mutations_library["append_branch"] = Mutation(self.appendBranchToRandomProduction,"added a branch to a random production",3)
        #self.mutations_library["append_self"] = Mutation(self.appendSelfToRandomProduction,"added a self-copy to a random production",3)
        self.mutations_library["append_leaf"] = Mutation(self.appendLeafToRandomProduction,"added a leaf to a random production (after a branch)",6)

        # @note: no flowers or fruits, because they do not look good visually
        #self.mutations_library["append_flower"] = Mutation(self.appendFlowerToRandomProduction,"added a flower to a random production (after a branch)",8)
        #self.mutations_library["append_fruit"] = Mutation(self.appendFruitToRandomProduction,"added a fruit to a random production (after a branch)",8)

        self.mutations_library["insert_line"] = Mutation(self.insertLineIntoRandomProduction,"inserted a line into a random production",6)
        self.mutations_library["insert_self"] = Mutation(self.insertSelfIntoRandomProduction,"inserted a self-copy into a random production",6)
        self.mutations_library["insert_branch"] = Mutation(self.insertRandomBranchInRandomProduction,"inserted a branch into a random production",6)
        self.mutations_library["insert_size"] = Mutation(self.changeSizeOfRandomLine,"change the size of a random line",6)
        self.mutations_library["split_line"] = Mutation(self.splitRandomLineInRandomProduction,"split a random line in a random production into two branches",6)
        self.mutations_library["rotate_line"] = Mutation(self.rotateRandomLineInRandomProduction,"add a random rotation to a line in a random production",6)

        #self.mutations_library["change_branch_to_leaf"] = Mutation(self.changeBranchToLeaf,"change a branch to a leaf",3)
        self.mutations_library["change_parameter"] = Mutation(self.changeRandomParameterInRandomProduction,"change a random parameter value",15)
        #TODO FIX: self.mutations_library["change_axiom_parameter"] = Mutation(self.changeRandomParameterInAxiom,"change a random parameter value",15)

        self.mutations_library["remove_leaf"] = Mutation(self.removeLeafFromRandomProduction,"removed a leaf from an existing production",5)
        #self.mutations_library["remove_flower"] = Mutation(self.removeFlowerFromRandomProduction,"removed a flower from an existing production",5)
        #self.mutations_library["remove_fruit"] = Mutation(self.removeFruitFromRandomProduction,"removed a fruit from an existing production",5)
        self.mutations_library["remove_branch"] = Mutation(self.removeBranchFromRandomProduction,"removed a branch from an existing production",5)
        self.mutations_library["remove_line"] = Mutation(self.removeLineFromRandomProduction,"removed a line from an existing production",5)
        self.mutations_library["remove_orientation"] = Mutation(self.removeOrientationFromRandomProduction,"removed an orientation from an existing production",5)
        self.mutations_library["remove_size"] = Mutation(self.removeSizeFromRandomProduction,"remove a size from an existing production",5)
        self.mutations_library["remove_self"] = Mutation(self.removeSelfFromRandomProduction,"remove a self-copy from an existing production",5)

    def loadComplexifyMutationChoices(self,availableMutations,weights):
        #self.addMutationChoice("append_branch", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH), availableMutations, weights)
        #self.addMutationChoice("append_self", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH), availableMutations, weights)

        self.addMutationChoice("append_leaf", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH, doNotConsiderProductionWithPredecessor="!"), availableMutations, weights)
        #self.addMutationChoice("append_flower", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH, doNotConsiderProductionWithPredecessor="!"), availableMutations, weights)
        #self.addMutationChoice("append_fruit", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH, doNotConsiderProductionWithPredecessor="!"), availableMutations, weights)
        self.addMutationChoice("split_line", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH, doNotConsiderProductionWithPredecessor="!"), availableMutations, weights)
        self.addMutationChoice("rotate_line", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH, doNotConsiderProductionWithPredecessor="!"), availableMutations, weights)
        self.addMutationChoice("insert_self", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH, doNotConsiderProductionWithPredecessor="!"), availableMutations, weights)
        self.addMutationChoice("insert_line", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH, doNotConsiderProductionWithPredecessor="!"), availableMutations, weights)
        self.addMutationChoice("insert_branch", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH, doNotConsiderProductionWithPredecessor="!", containedLetters=["F"]), availableMutations, weights)
        self.addMutationChoice("insert_size", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH, doNotConsiderProductionWithPredecessor="!"), availableMutations, weights)


    def loadModifyingMutationChoices(self,availableMutations,weights):
        self.addMutationChoice("change_parameter",(len(self.lsystem.productions) > 0 and self.parameterized is True), availableMutations, weights)
        #TODO FIX: self.addMutationChoice("change_axiom_parameter",(self.parameterized is True), availableMutations, weights)

        # @note: Not used because it may break the tree!
        #self.addMutationChoice("change_branch_to_leaf", len(self.lsystem.productions)>0 and self.hasProductionsWith(maxLength=MAX_TOTAL_STRING_LENGTH), availableMutations, weights)

    def loadSimplifyingMutationChoices(self,availableMutations,weights):
        self.addMutationChoice("remove_leaf",len(self.lsystem.productions) > 0 and self.hasSuccessorWithLetter("L"), availableMutations, weights)
        #self.addMutationChoice("remove_flower",len(self.lsystem.productions) > 0 and self.hasSuccessorWithLetter("K"), availableMutations, weights)
        #self.addMutationChoice("remove_fruit",len(self.lsystem.productions) > 0 and self.hasSuccessorWithLetter("R"), availableMutations, weights)
        #self.addMutationChoice("remove_size",len(self.lsystem.productions) > 0 and self.hasSuccessorWithLetter("!"), availableMutations, weights)
        self.addMutationChoice("remove_self",len(self.lsystem.productions) > 0 and self.hasSuccessorWithLetter("A"), availableMutations, weights)
        self.addMutationChoice("remove_orientation",len(self.lsystem.productions) > 0 and self.hasSuccessorWithAnyLetter(self.getAllOrientationLetters()), availableMutations, weights)
        self.addMutationChoice("remove_line",len(self.lsystem.productions) > 0 and self.hasSuccessorWithAtLeastCountOfLetter("F",2), availableMutations, weights)
        self.addMutationChoice("remove_branch",len(self.lsystem.productions) > 0 and self.hasSuccessorWithBranch(), availableMutations, weights)

    ######################
    # Mutation operators
    ######################

    # Append
    def appendLineToRandomProduction(self):
        production, index = self.getRandomUsableProduction(maxLength = MAX_TOTAL_STRING_LENGTH)
        production.successor = self.appendModuleOfLetter("F", production.successor)

    def appendSelfToRandomProduction(self):
        production, index = self.getRandomUsableProduction(maxLength = MAX_TOTAL_STRING_LENGTH)
        production.successor = self.appendModuleOfLetter("A", production.successor)

    def appendLeafToRandomProduction(self):
        """ Appends a leaf at the end of a branch """
        production, index = self.getRandomUsableProductionWithLetter("F", maxLength = MAX_TOTAL_STRING_LENGTH)

        pString = self.generateEmptyParametricString()
        pString.appendModule(self.generateModuleOfLetter("F"))
        pString.appendModule(self.generateModuleOfLetter("L"))

        production.successor = self.changeModuleFromLetterToPString(production.successor,"F",pString)

        # We remove the leaf duplicates that could have been formed @note: this approach is a little slower! I should instead add only where there isn't already a leaf!
        self.removeDuplicatesOf("L")

    def appendFlowerToRandomProduction(self):
        """
        Appends a flower at the end of a branch
        F -> FK
        """
        production, index = self.getRandomUsableProductionWithLetter("F", maxLength = MAX_TOTAL_STRING_LENGTH)

        pString = self.generateEmptyParametricString()
        pString.appendModule(self.generateModuleOfLetter("F"))
        pString.appendModule(self.generateModuleOfLetter("K"))

        production.successor = self.changeModuleFromLetterToPString(production.successor,"F",pString)

        self.removeDuplicatesOf("K")

    def appendFruitToRandomProduction(self):
        """
        Appends a fruit at the end of a branch
        F -> FR
        """
        production, index = self.getRandomUsableProductionWithLetter("F", maxLength = MAX_TOTAL_STRING_LENGTH)

        pString = self.generateEmptyParametricString()
        pString.appendModule(self.generateModuleOfLetter("F"))
        pString.appendModule(self.generateModuleOfLetter("R"))

        production.successor = self.changeModuleFromLetterToPString(production.successor,"F",pString)

        self.removeDuplicatesOf("R")


    # Insert
    def insertSelfIntoRandomProduction(self):
        """ Inserts an A """
        production, index = self.getRandomUsableProduction(maxLength = MAX_TOTAL_STRING_LENGTH)
        production.successor = self.insertModuleOfLetterRandomly("A", production.successor)

    def insertLineIntoRandomProduction(self):
        """ Inserts an F """
        production, index = self.getRandomUsableProduction(maxLength = MAX_TOTAL_STRING_LENGTH)
        production.successor = self.insertModuleOfLetterRandomly("F", production.successor)

    def insertRandomBranchInRandomProduction(self):
        """
         F -> [+F]F
        """
        production, index = self.getRandomUsableProductionWithLetter("F", maxLength = MAX_TOTAL_STRING_LENGTH)

        orientation_letter = self.getRandomOrientationLetter()

        pString = self.generateEmptyParametricString()
        pString.appendOpenBranch()
        pString.appendModule(self.generateModuleOfLetter(orientation_letter))
        pString.appendModule(self.generateModuleOfLetter("F"))
        pString.appendCloseBranch()
        pString.appendModule(self.generateModuleOfLetter("F"))

        production.successor = self.changeModuleFromLetterToPString(production.successor,"F",pString)

    # Split
    def splitRandomLineInRandomProduction(self):
        """
        F -> [+F][-F]
        """
        production, index = self.getRandomUsableProductionWithLetter("F", maxLength = MAX_TOTAL_STRING_LENGTH)

        first_orientation_letter = self.getRandomOrientationLetter()
        second_orientation_letter = self.getRandomOrientationLetter()

        pString = self.generateEmptyParametricString()
        pString.appendOpenBranch()
        pString.appendModule(self.generateModuleOfLetter(first_orientation_letter))
        pString.appendModule(self.generateModuleOfLetter("F"))
        pString.appendCloseBranch()
        pString.appendOpenBranch()
        pString.appendModule(self.generateModuleOfLetter(second_orientation_letter))
        pString.appendModule(self.generateModuleOfLetter("F"))
        pString.appendCloseBranch()

        production.successor = self.changeModuleFromLetterToPString(production.successor,"F",pString)

    # Rotate
    def rotateRandomLineInRandomProduction(self):
        """
        Adds an orientation in front of an F
        F -> +F
        """
        production, index = self.getRandomUsableProductionWithLetter("F", maxLength = MAX_TOTAL_STRING_LENGTH)
        chosen_orientation_letter = self.getRandomOrientationLetter()

        pString = self.generateEmptyParametricString()
        pString.appendModule(self.generateModuleOfLetter(chosen_orientation_letter))
        pString.appendModule(self.generateModuleOfLetter("F"))

        production.successor = self.changeModuleFromLetterToPString(production.successor,"F",pString)

        self.removeDuplicatesOf(chosen_orientation_letter)

    # Change
    def changeSizeOfRandomLine(self):
        """
        F -> !F
        """
        production, index = self.getRandomUsableProductionWithLetter("F", maxLength = MAX_TOTAL_STRING_LENGTH)

        pString = self.generateEmptyParametricString()
        pString.appendModule(self.generateModuleOfLetter("!"))
        pString.appendModule(self.generateModuleOfLetter("F"))

        production.successor = self.changeModuleFromLetterToPString(production.successor,"F",pString)

        self.removeDuplicatesOf("!")

    # Removal
    def removeLeafFromRandomProduction(self):
        production, index = self.getRandomUsableProductionWithLetter("L")
        production.successor = self.removeModuleOfLetter("L",production.successor)

    def removeFlowerFromRandomProduction(self):
        production, index = self.getRandomUsableProductionWithLetter("K")
        production.successor = self.removeModuleOfLetter("K",production.successor)

    def removeFruitFromRandomProduction(self):
        production, index = self.getRandomUsableProductionWithLetter("R")
        production.successor = self.removeModuleOfLetter("R",production.successor)

    def removeOrientationFromRandomProduction(self):
        letters = self.getAllOrientationLetters()
        while len(letters) > 0:
            orientation_letter = self.getRandomItemFromList(letters)
            production, index = self.getRandomUsableProductionWithLetter(orientation_letter)
            if production is None: letters.remove(orientation_letter)
            else: break
        #print"REMOVE ORI " + str(orientation_letter)
        #print production
        #print letters
        production.successor = self.removeModuleOfLetter(orientation_letter,production.successor)

    def removeSizeFromRandomProduction(self):
        production, index = self.getRandomUsableProductionWithLetter("!")
        production.successor = self.removeModuleOfLetter("!",production.successor)

    def removeSelfFromRandomProduction(self):
        production, index = self.getRandomUsableProductionWithLetter("A")
        production.successor = self.removeModuleOfLetter("A",production.successor)

    def removeLineFromRandomProduction(self):
        """ Makes sure that at least one F remains! """
        production, index = self.getRandomUsableProductionWithLetter("F", count = 2)
        production.successor = self.removeModuleOfLetter("F",production.successor)

    def removeBranchFromRandomProduction(self):
        """ Remove the first branch from a random production """
        production, index = self.getRandomUsableProduction(hasBranches = True)
        #print production
        production.successor = self.removeFirstBranch(production.successor)

    ##################
    # Utilities
    ##################

    def removeFirstBranch(self,input_pstring):
        """ Given a pString, removes the first branch we find """
        output_pstring = ParametricString.copyFrom(input_pstring)
        i = 0
        start_index = None
        for m in input_pstring.modulesList:
            if m.isOpenBracket():   # Will take the innermost open bracket
                start_index = i
            elif m.isClosedBracket():
                end_index = i+1
                break
            i += 1
        if start_index is None:
            print("Remove first branch failed: there are no branches here!")
            return output_pstring
        if start_index == 0 and end_index == len(input_pstring.modulesList):
            print("Remove first branch failed: the whole production is a branch!")
            return output_pstring
        output_pstring.removeModulesFromTo(start_index,end_index)
        return output_pstring

    def removeDuplicatesOf(self,chosen_letter):
        for production in self.lsystem.productions:
            modules = production.successor.getActualModules()
            for i in range(len(modules)-1,0,-1):
                if modules[i].letter == chosen_letter and modules[i].letter == modules[i-1].letter:
                    production.successor.modulesList.remove(modules[i])

    def changeModuleFromLetterToPString(self,input_pstring,from_letter,to_pstring):
        """ Changes a module into the given pString """
        module_to_change = self.getRandomModuleOfLetterFromPString(from_letter,input_pstring)
        output_pstring = self.changeModuleFromToPstring(input_pstring,module_to_change,to_pstring)
        return output_pstring

    def changeModuleFromToPstring(self,input_pstring,from_module,to_pstring):
        """ Given a module in a pstring, we change it to the given pString """
        output_pstring = ParametricString.copyFrom(input_pstring)

        # If parameterized, we make sure that the parameter value remains the same for the same letters, if possible
        if self.parameterized:
            to_modules = to_pstring.getActualModules()
            for j in range(len(to_modules)):
                if to_modules[j].letter == from_module.letter:
                    for i in range(len(from_module.params)):
                        if i < len(to_modules[j].params):
                            to_modules[j].params[i] = from_module.params[i]

        change_index = input_pstring.modulesList.index(from_module)
        del output_pstring.modulesList[change_index]
        for to_module in to_pstring:
            output_pstring.modulesList.insert(change_index,to_module)
            change_index+=1
        return output_pstring


    # Miscellaneous Checks
    def hasSuccessorWithBranch(self):
        for production in self.lsystem.productions:
            if production.successor.hasBranches():
                return True
        return False

    def hasSuccessorWithLetter(self,letter):
        for production in self.lsystem.productions:
            if production.successor.containsLetter(letter):
                return True
        return False

    def hasSuccessorWithAnyLetter(self,letters):
        for letter in letters:
            for production in self.lsystem.productions:
                if production.successor.containsLetter(letter):
                    return True
        return False

    def hasSuccessorWithAtLeastCountOfLetter(self,letter,count):
        for production in self.lsystem.productions:
            if production.successor.containsLetterAtLeastCount(letter,count):
                return True
        return False

    # Getters
    def getRandomOrientationLetter(self):
        return self.getRandomItemFromList(self.getAllOrientationLetters())

    def getAllOrientationLetters(self):
        return ["+","-","&","^","/","\\"]

    def getRandomUsableProduction(self, maxLength = None, hasBranches = None):
        """
        Gets a random production from the existing ones for further addition.
        Avoids getting too long productions.
        DEPRECATED NO!! Avoids getting productions that change size (!)
        """
        return self.getRandomExistingProduction(maxLength = maxLength,
                                                doNotConsiderProductionWithPredecessor="!",
                                                containsBranches = hasBranches)

    def getRandomUsableProductionWithLetter(self, letter, maxLength = None, count = 1):
        """
        Gets a random production from the existing ones.
        Makes sure it has the chosen letter in a module.
        """
        containedLetters = [letter]
        return self.getRandomExistingProduction(maxLength = maxLength,
                                                doNotConsiderProductionWithPredecessor = "!",
                                                atLeastCountLetters = count,
                                                containedLetters = containedLetters)



    def getRandomModuleOfLetterFromPString(self,from_letter,pstring):
        """ Gets a random module with the given letter """
        modules = pstring.getActualModules()
        modules = list(filter(lambda m: m.letter is from_letter,modules))
        index = self.rnd.randint(0,len(modules)-1)
        module_to_change = modules[index]
        return module_to_change


if __name__ == "__main__":
    print("Start testing PlantsIncrementalGenerator")

    generator = PlantsIncrementalGenerator(parameterized = True,
                                           constantsProbability = 0.5,
                                           definesProbability = 0.5)
    generator.setLSystem(ParametricLSystem())
    generator.verbose = True

    print("\n------- Testing reset -------")
    generator.resetToSimple()
    print("Initial L-system is: " + str(generator.lsystem))

    print("\n------- Testing mutations -------")

    print("\nTEST 1 - Appending a line to random production")
    generator.appendLineToRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nTEST 2 - Split random line in random production")
    generator.splitRandomLineInRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nTEST 3 - Inserting a line into a random production")
    generator.insertLineIntoRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nTEST 4 - Rotate a line randomly")
    generator.rotateRandomLineInRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nTEST 5 - Adding a leaf")
    generator.appendLeafToRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nTEST 6 - Removing a leaf")
    generator.removeLeafFromRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nTEST 7 - Inserting a branch")
    generator.insertRandomBranchInRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nTEST 8  - Removing a line")
    generator.removeLineFromRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nTEST 9  - Removing an orientation")
    generator.removeOrientationFromRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nTEST 10  - Removing a branch")
    generator.removeBranchFromRandomProduction()
    print("L-system is: " + str(generator.lsystem))

    print("\nFinish testing PlantsIncrementalGenerator")
