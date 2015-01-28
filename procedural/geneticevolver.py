"""
    Class for generating L-System structures using a genetic algorithm.

    @author: Michele Pirovano
    @copyright: 2013-2015
"""
import procedural.incrementalgenerator
import procedural.core.geneticinstance

import imp
imp.reload(procedural.incrementalgenerator)
imp.reload(procedural.core.geneticinstance)

from procedural.incrementalgenerator import *
from procedural.core.geneticinstance import *

import random

class InitialPopulationGenerationChoice:
    FROM_INSTANCE = 0
    RANDOMIZED = 1
    FROM_AUTOMATED_EVOLUTION = 2

class GeneticEvolver:
    """
    Generates a set of pL-systems following a genetic algorithm.
    """
    FILE_OUTPUT_PATH = "C:\\Users\\Michele\\Desktop\\"  + "evolution_output.txt"
    MAX_POSSIBLE_ITERATIONS = 1000
    GOOD_INITIAL_FITNESS = 4 # TODO: Choose how to compute this 'good fitness'!

    def __init__(self, turtle, verbose = False, mini_verbose = False, randomSeed = None):
        self.turtle = turtle

        self.verbose = verbose
        self.mini_verbose = verbose or mini_verbose  # The bare minimum
        self.recap_verbose = True    # Only a recap of the evolution

        # Variables initialization
        self.starting_genetic_instance = None
        if randomSeed is not None: self.rnd = random.Random(randomSeed)
        else: self.rnd = random.Random()
        self.currentFitnessFunction = self.defaultFitnessFunction

        # Options
        # @note: Our crossover does not really mix things up, so it's better to rise mutation a bit, at least at the start!
        self.crossoverRate = 0.80 # Recommended by http://www.obitko.com/tutorials/genetic-algorithms/recommendations.php
        #self.mutationRate = 0.01 # Recommended by http://www.obitko.com/tutorials/genetic-algorithms/recommendations.php
        self.mutationRate = 0.30    # Higher or crossover will converge too easily!

        self.initialPopulationGenerationChoice = InitialPopulationGenerationChoice.RANDOMIZED
        self.populationInitialisationComplexifySteps = 5

        self.consider_additional_parameters = True  # If False, only the structure of the LSYSTEM is evolved, and the additional parameters are ignored. If True, the additional parameters are used (such as branch width, angle of rotation, etc.)

        self.writeToFile = False     # Will write to file the evolution progress, to be later plotted with matlab

        self.discardEmptyEvolutions = False  # If True, evolutions that result in an empty tree (0 vertices) are discarded and redone
        self.discardLSystemsLargerThan = 0  # If > 0, any lsystem evolved that has length higher than this will be discarded and redone

    ######################
    #--- Setters
    ######################

    def setGenerator(self,generator):
        self.generator = generator

    def setStartingInstance(self,instance):
        self.initialPopulationGenerationChoice = InitialPopulationGenerationChoice.FROM_INSTANCE
        self.starting_genetic_instance = instance

    def removeStartingInstance(self):
        self.initialPopulationGenerationChoice = InitialPopulationGenerationChoice.RANDOMIZED
        self.starting_genetic_instance = None

    ######################
    #--- Evolution
    ######################

    def evolve(self,
                 populationSize = 20,
                 nIterations = 2,
                 targetFitness = 0
                 ):
        """
        Evolve from scratch, for 'nIterations' iterations.
        """
        if self.verbose: print("\n----------------------------------------------"
            + "\n----------------------------------------------"
            +"\n---------- Performing  Evolution -------------")

        population = self.generatePopulation(populationSize)

        if self.verbose:
            print("\nInitial population:")
            for p in population:
                pStringResult = p.lsystem.getResultPString()
                print("Fitness: " + str(p.fitness) + " pString: " + str(pStringResult))

        self.evolvePopulation(population,nIterations,targetFitness)

    def evolvePopulation(self,
                 population,
                 nIterations = 2,
                 targetFitness = 0
                 ):
        """
        Evolve a given population for 'nIterations' iterations OR until 'targetFitness' is reached.
        """
        if self.writeToFile: self.file = open(FILE_OUTPUT_PATH,"w")
        if targetFitness > 0:
            # Iterate until reaching the target fitness
            for i in range(GeneticEvolver.MAX_POSSIBLE_ITERATIONS):
                population, candidate_instance = self.iterateEvolutionOnce(i, population)
                if candidate_instance.fitness >= targetFitness:
                    if self.mini_verbose: print("We found our hero!")
                    break
        else:
            # Iterate for the given iterations
            for i in range(nIterations):
                population, candidate_instance = self.iterateEvolutionOnce(i, population)
        if self.writeToFile: self.file.close()


    def iterateEvolutionOnce(self, iteration_index, population):
        """ Perform a single evolution iteration """
        if self.mini_verbose:  print("\nIteration " + str(iteration_index))
        if self.writeToFile: self.file.write("\nIteration " + str(iteration_index))
        population = self.evolveStep(population)
        candidate_instance = self.getBestInstance()
        pStringResult = candidate_instance.lsystem.getResultPString()
        if self.verbose: print("Current Best Fitness: " + str(candidate_instance.fitness) + " pString: " + str(pStringResult))
        if self.writeToFile: self.file.write("|"+str(candidate_instance.fitness) + "|" + str(pStringResult))
        return population, candidate_instance

    def evolveStep(self, population):
        """
        Evolve step by step.
        Evolution is performed by starting from the old population, selecting parents, recombining, and mutating, until a new full population is obtained.
        """
        population_size = len(population)
        new_population = []

        if self.recap_verbose:
            recap = "\n----------------------------------\nRECAP EVOLVE STEP:"

        # Elitism
        best_instance = self.getBestInstance(population)
        new_population.append(best_instance)

        if self.recap_verbose: recap += "\n\n|||Elite: " + best_instance.toShortString()

        if self.mini_verbose:
            print("\nElitism - we keep the best instance:")
            print(best_instance.toShortString())

        # Generation of new offspring
        for i in range(int(population_size/2)):
            if self.mini_verbose: print("\nGeneration - pair " + str(i))

            parents = self.select(population,selectionSize = 2)

            if self.recap_verbose:
                recap += "\n\n|||Selection:"
                for p in parents:
                    recap += "\n"+p.toShortString()

            if self.mini_verbose:
                print("\nSelected:")
                for p in parents:
                    #print(p)
                    print(p.toShortString())
                    #p.lsystem.printGlobalDefinesStatus()

            if self.rnd.random() < self.crossoverRate:
                offspring_crossover = self.crossPair(parents)

                if self.recap_verbose:
                    recap += "\n\n    (Crossovered):"
                    for p in offspring_crossover:
                        recap += "\n"+p.toShortString()
                        recap += "\n Fitness is " + str(self.currentFitnessFunction(p.lsystem.iterate()))

                if self.mini_verbose:
                    print("\nCrossovered:")
                    for p in offspring_crossover:
                        #print(p)
                        print(p.toShortString())
                        #p.lsystem.printGlobalDefinesStatus()
            else:
                if self.recap_verbose:
                    recap += "\n\n    (Not crossovered):"
                offspring_crossover = parents

            offspring_mutated = []
            for inst in offspring_crossover:
                if self.rnd.random() < self.mutationRate:
                    #print("MUTATING: " + str(inst))
                    inst = self.mutateInstance(inst)

                    if self.recap_verbose:
                        recap += "\n\n    (Mutated):"
                        recap += "\n"+inst.toShortString()

                    if self.mini_verbose:
                        print("\nMutated:")
                        print(inst.toShortString())
                offspring_mutated.append(inst)

            if self.mini_verbose:
                print("\nInserted as new:")
                #for p in offspring_mutated: print(self.currentFitnessFunction(p.lsystem.getResultPString()))
                for p in offspring_mutated: print(p.toShortString())
            new_population.extend(offspring_mutated)

        # Re-compute fitness
        if self.mini_verbose:   print("\nRecomputing fitness:")
        for p in new_population:
            """print "\n\nRECOMPUTING: " + str(p)#.lsystem.getResultPString())
            p.lsystem.printGlobalDefinesStatus()"""
            if p.fitness == 0:
                p.lsystem.clearResultPString()    # We did some modifications and we thus need to re-compute the result pString!
                p.fitness = self.currentFitnessFunction(p.lsystem.getResultPString())

        # Re-sort according to fitness
        new_population = self.sortPopulation(new_population)

        # De-elitism: remove the last one to keep the size consistent
        del new_population[-1]


        # Update current population
        self.currentPopulation = new_population
        if self.verbose:
            print("\nNew population: " + str(len(new_population)))
            for p in new_population:
                print(p.toShortString())
                #p.lsystem.printGlobalDefinesStatus()

        if self.recap_verbose:
            recap += "\n\nNew population:"
            for p in new_population:
                recap += "\n"+p.toShortString()

            print(recap)

        # Show the best for this run? NO!
        #self.currentFitnessFunction(self.getBestInstance().lsystem.getResultPString(), verbose = self.verbose)
        return new_population

    ###########################
    #---Population Generation
    ###########################

    def generatePopulation(self, population_size):
        """
        Generate the initial population.
        Also computes all instances' fitness.
        """
        if self.verbose: print("Generating population with method: " + str(self.initialPopulationGenerationChoice))

        if self.initialPopulationGenerationChoice == InitialPopulationGenerationChoice.FROM_INSTANCE:
            population = self.initialisePopulationTo(self.starting_genetic_instance,population_size)
        elif self.initialPopulationGenerationChoice == InitialPopulationGenerationChoice.RANDOMIZED:
            population = self.generateRandomPopulation(population_size)
        elif self.initialPopulationGenerationChoice == InitialPopulationGenerationChoice.FROM_AUTOMATED_EVOLUTION:
            population = self.generateAutomatedEvolvedPopulation(population_size)

        # Sort
        population = self.sortPopulation(population)
        self.currentPopulation = population # Update current population
        return population

    def generateRandomPopulation(self, population_size):
        """
        Generate the initial random population.
        Also computes all instances' fitness.
        """
        population = []
        for i in range(population_size):
            while True:

                # This creates new lsystems, then copies them to save the instances
                # (TODO: ??? -> the one inside the generator will be overriden each time we randomize anyway)
                self.generator.logicallyRandomize(self.populationInitialisationComplexifySteps)
                new_lsystem = ParametricLSystem.copyFrom(self.generator.lsystem)
                #new_lsystem.verbose = self.verbose
                if self.shouldDiscardLSystem(new_lsystem):
                    if self.mini_verbose: print ("WARNING: we are discarding a lsystem!!")
                    continue

                # We then create a new GeneticInstance that holds the evolved lsystem and complete the generation
                new_instance = self.createNewGeneticInstanceFromLsystem(new_lsystem)
                population.append(new_instance)
                if self.verbose:  print("Added to pop: " + new_instance.toShortString())
                break
        return population

    def generateAutomatedEvolvedPopulation(self, population_size):
        """
        Generate the initial population by evolving using a given fitness function until a good enough instance is found.
        Repeats this until we fill the population size.
        Also computes all instances' fitness.
        """
        population = []
        for i in range(population_size):
            tmp_population = self.generateRandomPopulation(population_size)

            self.evolvePopulation(tmp_population,
                                  targetFitness = GeneticEvolver.GOOD_INITIAL_FITNESS)

            new_instance = self.getBestInstance(tmp_population)
            population.append(new_instance)
            if self.verbose:  print("Added to pop: " + new_instance.toShortString())
        return population

    def initialisePopulationTo(self, input_genetic_instance, population_size):
        """
        Generate the initial population by copying a single genetic instance.
        Also computes fitness (anc copies it).
        """
        fitness = self.currentFitnessFunction(input_genetic_instance.lsystem.getResultPString())
        population = []
        for i in range(population_size):
            new_instance = GeneticInstance.copyFrom(input_genetic_instance)
            new_instance.fitness = fitness
            population.append(new_instance)
            if self.verbose:  print("Added to pop: " + new_instance.toShortString())
        return population

    def createNewGeneticInstanceFromLsystem(self, new_lsystem):
        new_instance = GeneticInstance(new_lsystem)
        if self.consider_additional_parameters: new_instance.randomizeAdditionalParameters(self.rnd)
        new_instance.fitness = self.currentFitnessFunction(new_lsystem.getResultPString())
        return new_instance

    ###########################
    #---Crossover
    ###########################

    def crossover(self, population):
        """
        Apply crossover to the given instances.
        Instances count must be an even number.
        """
        assert (len(population) % 2 == 0) , 'For crossover, the number of instances should be even!'
        crossover_population = []
        for i in range(int(len(population)/2)):
            instances_pair = [population[i],population[i+1]]
            if self.rnd.random() < self.crossoverRate:
                instances_pair = self.crossPair(instances_pair)
            crossover_population.extend(instances_pair)
        return crossover_population

    def crossPair(self, instancePair):
        """
        Apply crossover to the given pair of instances.
        Will also re-compute fitness.
        """
        inst1 = instancePair[0]
        inst2 = instancePair[1]

        offspring1_lsystem = ParametricLSystem.copyFrom(inst1.lsystem)
        offspring2_lsystem = ParametricLSystem.copyFrom(inst2.lsystem)

        """if self.verbose:
            print("\nCrossover instances:")
            print("\n " +str(inst1))
            print("\n " +str(inst2))"""

        # We perform crossover by point-crossover over the axiom
        # Maybe also switch axiom parameters?? NAH, doesn't make sense!!
        if self.verbose: print("\nSwitch axiom")
        axiom1 = inst1.lsystem.axiom
        axiom2 = inst2.lsystem.axiom
        o1, o2 = self.switchPStrings(axiom1,axiom2)
        offspring1_lsystem.setAxiomFromPstring(o1)
        offspring2_lsystem.setAxiomFromPstring(o2)

        # We perform crossover by switching production rules
        nProd1 = len(offspring1_lsystem.productions)
        nProd2 = len(offspring2_lsystem.productions)
        nProdMin = min(nProd1,nProd2)
        switchPoint = self.rnd.randint(0,nProdMin) # Not length-1, so potentially it switches nothing
        if self.verbose:
            print("\nProd1: " + str(nProd1) + "  nProd2: " + str(nProd2) + "  Switch point: " + str(switchPoint))
        offspring1_lsystem.clearProductions()
        offspring2_lsystem.clearProductions()

        for i in range(0,nProd1):
            if i < switchPoint:
                offspring2_lsystem.copyProductionFromExisting(inst2.lsystem.getProduction(i))
            else:
                offspring2_lsystem.copyProductionFromExisting(inst1.lsystem.getProduction(i))

        for i in range(0,nProd2):
            if i < switchPoint:
                offspring1_lsystem.copyProductionFromExisting(inst1.lsystem.getProduction(i))
            else:
                offspring1_lsystem.copyProductionFromExisting(inst2.lsystem.getProduction(i))


        # We perform point crossover on some successors as well
        # This is done only on successors of the same production (same predecessor)
        # We avoid breaking brackets (by checking that the balance of brackets after a switching point is 0)
        # Else, we choose another switch point!
        # (TODO: but make sure at least one F remains, however!)

        # First select (from the offspring) what productions will have their successor switched
        # TODO: this works only if the lsystems share a predecessor!!
        prod1 = self.getRandomItemFromList(offspring1_lsystem.productions)
        prod2 = offspring2_lsystem.getProductionWithPredecessorLetter(prod1.predecessor.letter)
        #print(prod1)
        #print(prod2)

        crossoverSuccessors = True
        if crossoverSuccessors:
            # Then switch their successor pstrings
            if self.verbose: print("\nSwitch successors")
            p1 = prod1.successor
            p2 = prod2.successor
            while True:
                o1, o2 = self.switchPStrings(p1,p2)
                if o1.bracketsAreBalanced() and o2.bracketsAreBalanced(): 
                    break # Exit only if brackets are balanced!
            prod1.setSuccessorPstring(o1)
            prod2.setSuccessorPstring(o2)
            #TODO: we would also need to merge thir global defines in a better way! Should check whether the define globals get switched or not around!!
            prod1.extendGlobalDefines(p2.globalDefines)
            prod2.extendGlobalDefines(p1.globalDefines)

        # TODO: enable the discard also after a crossover, or the mutations may hang!
        #if self.shouldDiscardLSystem(offspring1_lsystem) or self.shouldDiscardLSystem(offspring2_lsystem):

        offspring1_instance = GeneticInstance(offspring1_lsystem)
        offspring2_instance = GeneticInstance(offspring2_lsystem)

        # We clear the result pString since the offspring are different. TODO: do this whenever we modify a lsystem!!
        offspring1_instance.lsystem.clearResultPString()
        offspring1_instance.lsystem.clearResultPString()

        # We also need to perform crossover on the additional parameters
        if self.consider_additional_parameters:
            self.crossoverAdditionalParameters(offspring1_instance,offspring2_instance,inst1,inst2)

        """if self.verbose:
            print("\nOffspring instances:")
            print("\n " +str(offspring1_instance))
            print("\n " +str(offspring2_instance))"""

        crossed_population = [offspring1_instance,offspring2_instance]
        return crossed_population

    def crossoverAdditionalParameters(self,off1,off2,inst1,inst2):
        p_off1 = off1.turtleParameters
        p_off2 = off2.turtleParameters
        p_inst1 = inst1.turtleParameters
        p_inst2 = inst2.turtleParameters

        # I use Arithmetic crossover
        # This may converge towards the mean of two values
        # Going away from the mean is obtained through mutation
        a = self.rnd.random()
        p_off1.branch_radius = math.floor((p_inst1.branch_radius*a + p_inst2.branch_radius*(1-a))*100)/100.0
        p_off2.branch_radius = math.floor((p_inst2.branch_radius*a + p_inst1.branch_radius*(1-a))*100)/100.0

        a = self.rnd.random()
        p_off1.tropism_susceptibility = math.floor((p_inst1.tropism_susceptibility*a + p_inst2.tropism_susceptibility*(1-a))*100)/100.0
        p_off2.tropism_susceptibility = math.floor((p_inst2.tropism_susceptibility*a + p_inst1.tropism_susceptibility*(1-a))*100)/100.0

        a = self.rnd.random()
        p_off1.details_scale = math.floor((p_inst1.details_scale*a + p_inst2.details_scale*(1-a))*100)/100.0
        p_off2.details_scale = math.floor((p_inst2.details_scale*a + p_inst1.details_scale*(1-a))*100)/100.0

        a = self.rnd.random()
        p_off1.trunk_material_choice = int(p_inst1.trunk_material_choice*a + p_inst2.trunk_material_choice*(1-a))
        p_off2.trunk_material_choice = int(p_inst2.trunk_material_choice*a + p_inst1.trunk_material_choice*(1-a))

        a = self.rnd.random()
        p_off1.leaf_choice = int(p_inst1.leaf_choice*a + p_inst2.leaf_choice*(1-a))
        p_off2.leaf_choice = int(p_inst2.leaf_choice*a + p_inst1.leaf_choice*(1-a))

        a = self.rnd.random()
        p_off1.bulb_choice = int(p_inst1.bulb_choice*a + p_inst2.bulb_choice*(1-a))
        p_off2.bulb_choice = int(p_inst2.bulb_choice*a + p_inst1.bulb_choice*(1-a))

        a = self.rnd.random()
        p_off1.fruit_choice = int(p_inst1.fruit_choice*a + p_inst2.fruit_choice*(1-a))
        p_off2.fruit_choice = int(p_inst2.fruit_choice*a + p_inst1.fruit_choice*(1-a))

    ###########################
    #---Mutation
    ###########################

    def mutate(self, population):
        """
        Apply a mutation to the given population.
        """
        mutated_population = []
        for instance in population:
            if self.rnd.random() < self.mutationRate:
                instance = self.mutateInstance(instance)
            mutated_population.append(instance)
            #print("We got: " + str(new_lsystem))
        return mutated_population

    def mutateInstance(self, input_instance):
        #print("Starting from: " + str(instance.lsystem))
        n_retries = 0
        while True:
            mutated_instance = GeneticInstance.copyFrom(input_instance)
            mutated_lsystem = mutated_instance.lsystem
            self.generator.lsystem = mutated_lsystem
            self.generator.mutationAnyMultipleTimes()    # TODO: The number of mutation steps should be passed here!
            if n_retries == 10:
                if self.mini_verbose: print("Too many discards. We keep it!")
                # After some retries, we use the mutated one anyway (or it will break stuff)
                pass
            elif self.shouldDiscardLSystem(mutated_lsystem):
                if self.mini_verbose: print("We discard a mutation that is BAD!")
                n_retries+=1
                continue
            break

        # We also need to perform mutation on the additional parameters!
        if self.consider_additional_parameters: mutated_instance.mutateAdditionalParameters(self.rnd)

        # We clear the result pString since the offspring are different. TODO: do this whenever we modify a lsystem!!
        mutated_instance.lsystem.clearResultPString()

        return mutated_instance

    ###########################
    #---Selection
    ###########################

    def select(self, population, selectionSize):
        """
        Perform a selection over a population.
        """
        #return self.selectBest(population, selectionSize)
        return self.selectRoulette(population, selectionSize)

    def selectBest(self, population, selectionSize):
        """
        Selects only the higher fitness systems.
        If two are tied, shuffle.
        """
        # @note: This selection method always selects the best fitness individuals and the GA is not going on correctly... instead use tournament selection!

        population = self.sortPopulation(population)

        # Shuffling the same-fitness instances
        start_i = None
        for i in range(len(population)):
            #print("Checking " + str(i))
            if start_i is None or population[i].fitness < shuffle_fitness or i == len(population)-1:

                # Shuffle the last batch
                if start_i is not None:
                    batch = population[start_i:i]
                    #print("Batch to shuffle: "); for p in batch: print (str(p.fitness) + " " + str(p.lsystem.iterate()))

                    random.shuffle(batch)
                    population[start_i:i] = batch
                    #print("Batch shuffled: ");  for p in batch: print (str(p.fitness) + " " + str(p.lsystem.iterate()))

                # Start a new one
                start_i = i
                shuffle_fitness = population[i].fitness
                #print("Starting new batch with fitness: " + str(shuffle_fitness))

        return population[0:selectionSize]

    def selectRoulette(self, population, selectionSize):
        """
        Selects using the roulette wheel selection method.
        @note: Make sure the fitness is never negative or it won't work correctly!
        """
        selected = []
        for j in range(selectionSize):
            fitness_sum = 0
            for instance in population:
                #print("Add fitness: " + str(instance.fitness))
                fitness_sum += instance.fitness

            #print("TOTAL FITNESS: " + str(fitness_sum))
            choice = self.rnd.random()*fitness_sum
            #print("Choice: " + str(choice))
            current_sum = 0
            for i in range(len(population)):
                current_sum += population[i].fitness
                if choice < current_sum:
                    selected.append(population[i])
                    #print("Selected: " + str(i))
                    break
        return selected

    ###########################
    #---Miscellaneous
    ###########################

    def getRandomItemFromList(self,list):   #TODO: this is also in incrementalGenerator, instead place this in Utilities and the RND should be passed!
        if len(list) == 0: return None
        return list[self.rnd.randint(0,len(list)-1)]

    def switchPStrings(self, p1, p2):
        l1 = len(p1)
        l2 = len(p2)
        min_length = min(l1, l2)
        max_length = max(l1, l2)
        switchPoint = self.rnd.randint(0,min_length) # Not length-1, so potentially it switches nothing
        o1 = ParametricString()
        o2 = ParametricString()
        for i in range(max_length):
            if l1 > i: m1 = ParametricModule.copyFrom(p1[i])
            if l2 > i: m2 = ParametricModule.copyFrom(p2[i])
            if i < switchPoint:
                if l1 > i: o1.appendModule(m1)
                if l2 > i: o2.appendModule(m2)
            else:
                if l1 > i: o2.appendModule(m1)
                if l2 > i: o1.appendModule(m2)
        if self.verbose:
            print(" l1: " + str(l1) + " l2: " + str(l2) + " switch at: " + str(switchPoint))
        return o1, o2

    def shouldDiscardLSystem(self,lsystem):
        """
        Sometimes, lsystems are not good enough and we discard them.
        """
        discard = False
        if self.discardEmptyEvolutions:
            pstring = lsystem.getResultPString()
            actualModules = pstring.getActualModules()
            totalLength = len(pstring)
            numberOfF = len(list(filter(lambda m: m.letter == 'F',actualModules)))
            discard = discard or numberOfF == 0

        if self.discardLSystemsLargerThan > 0:
            discard = discard or totalLength > self.discardLSystemsLargerThan

        if self.verbose and discard: print("We should discard: Total length is " + str(totalLength) + " and number of F is " + str(numberOfF))
        return discard

    def getBestInstance(self, target_population = None):
        """ Return the best instance from a population """
        if target_population is None:
            # Use the current population
            return self.currentPopulation[0]
        return target_population[0]

    def sortPopulation(self, population):
        population.sort(key = lambda instance: -instance.fitness)
        #print("Sorted pop: "); for p in population: print (str(p.fitness) + " " + str(p.lsystem.iterate()))
        return population

    def listInstances(self):
        for inst in self.currentPopulation:
            print(inst.toShortString())

    ###########################
    #---Fitness Functions
    ###########################

    def applyFitnessFunction(self, instance):
        instance.fitness = self.currentFitnessFunction(instance.lsystem.iterate())

    def defaultFitnessFunction(self, pString, verbose = False):
        """
        The fitness function we select as default.
        @note: minimum is 0, never go negative or selection will break!
        """
        return max(0,self.treeFitnessFunction(pString, verbose))

    def ochoaFitnessFunction(self, pString, verbose = False):
        """
        From "On genetic algorithms and Lindenmayer systems" 1998
        """
        fitness = 0

        turtleResult = self.turtle.draw(pString.toString())
        verts = turtleResult.verts

        s = "pString: " + str(pString) +"\n"

        # Weights
        length_weight = -0.01
        phototropism_weight = 0#0.1
        simmetry_weight = 10


        # Constraint on length of the resulting pString
        delta_fitness = len(pString)*len(pString)
        fitness += delta_fitness * length_weight
        s+= " | Length: " + str(delta_fitness)

        # Positive phototropism (tall tree)
        if len(verts) == 0:
            delta_fitness = 0
        else:
            delta_fitness = max([v.z for v in verts])
        fitness += delta_fitness*phototropism_weight
        s+= " | Tall: " + str(delta_fitness)

        # Bilateral simmetry (balanced tree)
        if len(verts) == 0:
            delta_fitness = 0
            balance_x = 0
            balance_y = 0
        else:
            span_x_pos = max([v.x for v in verts])
            span_x_neg = -min([v.x for v in verts])
            span_y_pos = max([v.y for v in verts])
            span_y_neg = -min([v.y for v in verts])

            # We want the trees to have a balanced appearance:
            if span_x_pos == 0 or span_x_neg == 0:
                balance_x = 0
            elif span_x_pos == span_x_neg:
                balance_x = 1
            else:
                balance_x = min(1,abs(1/(span_x_pos/span_x_neg -1)))  # The span ratio should be as close to 1 as possible

            if span_y_pos == 0 or span_y_neg == 0:
                balance_y = 0
            elif span_y_pos == span_y_neg:
                balance_y = 1
            else:
                balance_y = min(1,abs(1/(span_y_pos/span_y_neg -1)))   # The span ratio  should be as close to 1 as possible


            if verbose:
                print("Balance x: " + str(balance_x))
                print("Balance y: " + str(balance_y))

                #min_span = min([span_x_pos*span_x_neg , span_y_pos*span_y_neg])
                #print("Min span: " + str(min_span))
                print("Spans: " + str(span_x_pos) + " "
                    + str(span_x_neg) + " "
                    + str(span_y_pos) + " "
                    + str(span_y_neg) + " ")

            delta_fitness = balance_x+balance_y
        fitness += delta_fitness*simmetry_weight
        s+= " | Span: " + str(delta_fitness)

        # Light gathering ability (leaves at the ends)
        # TODO!

        # Structural stability
        # TODO!

        # Proportion of branching points
        # TODO!

        fitness = fitness/(phototropism_weight+simmetry_weight+length_weight)

        s += "| Tot: " + str(fitness)
        print(s)

        return fitness


    #TODO: fitness function should somewhat be normalized! we get very different behaviors now!
    #TODO: fitness function should also use additional parameters, not just the lsystem!

    def treeFitnessFunction(self, pString, verbose = False):
        """
        This fitness creates tree-like plants.
        """

        fitness = 0
        if len(pString) == 0: return -100 # Bad, nothing has been generated at all!

        s = "pString: " + str(pString) +"\n"

        # Modifiers
        branches_modifier = 0
        length_modifier = -0.000001 # even a small value is useful to avoid adding symbols that do not contribute to anything!
        f_modifier = 0
        rot_modifier = 0
        leaves_modifier = 1
        tall_modifier = 1#2
        span_modifier = 1#1
        tallspan_modifier = 0#5
        balance_modifier = 2

        target_height = 5
        target_volume_span = 3

        trunk_weight_modifier =  -0.6
        branch_weight_modifier = -0.6
        branch_size_ratio_modifier = 0    # We want the trunk to be larger than the branches
        underground_modifier =  -1
        #details_modifier = 2 # We want some details on the tree
        end_leaves_modifier = 5 # We want leaves to be at the end of the branches
        fruits_modifier = 2 # We want some of the details to be fruits


        # Notes on the modifiers:
        # - there are subtle workings in the evolution...
        # - the tallspan modifier is the most important, but it will not be triggered alone, as it requires a certain length, which is discorauged at first
        # - this means that, in order for tall&spanning trees to appear, we should give weight to the tall OR spanning trees first!
        # - the actual fitness tends to change with each iteration!!!
        # - note: to see an actual evolution, the mutation steps should be 3-5, not 1!
        # - 'tall' is not a good fitness parameter, as it cannot be normalized. Instead, I use the tall/verts ratio, that goes from 0 to 1, that is closer to 1 the more the tree is tall in respect to its number of vertices
        # - otherwise, we use 'targets', i.e. the height must be around a target height

        # Fitness based on the underlying l-system

        # Lots of branches -> High fitness
        nBranches = 0
        for module in pString:
            if str(module) == '[':
                nBranches+=1
        delta_fitness = nBranches*branches_modifier
        #fitness += delta_fitness
        s += "| BR "+str(delta_fitness)

        # Not too long resulting pstring -> High fitness
        # We do not count branching modules!
        # I tried linear and quadratic, simply.
        # Now, the first characters will count nothing, the rest will count much more!
        length_offset = 3   # We need the offset to let the evolution proceed after simply using 1 character!
        length = pString.lengthWithoutBrackets()
        if  length < length_offset:  delta_fitness = 0
        else: delta_fitness = (length-length_offset)*(length-length_offset)*length_modifier
        fitness += delta_fitness
        s += "| L: " + str(delta_fitness)

        # Lots of F!
        numberOfF = len(list(filter(lambda p: 'F' in str(p), pString)))
        delta_fitness = numberOfF*f_modifier
        fitness += delta_fitness
        s += "| NF: " + str(delta_fitness)

        # Lots of + and -!
        numberOfRot = len(list(filter(lambda p: '+' in str(p) or '-' in str(p), pString)))
        delta_fitness = numberOfRot*rot_modifier
        fitness += delta_fitness
        s += "| NRot: " + str(delta_fitness)

        # Lots of leaves!
        numberOfLeaves = len(list(filter(lambda p: 'L' in str(p), pString)))
        delta_fitness = numberOfLeaves*leaves_modifier
        delta_fitness /= len(pString) # This makes it more or less normalized
        fitness += delta_fitness
        s += "| NLeaves: " + str(delta_fitness)

        # Fitness based on the resulting tree
        statisticsContainer = []
        turtleResult = self.turtle.draw(str(pString), statisticsContainer = statisticsContainer)
        verts = turtleResult.verts

        trunkWeight = statisticsContainer[0]
        delta_fitness = trunkWeight*trunk_weight_modifier
        fitness += delta_fitness
        s +=  "| TrunkW: " + str(delta_fitness)

        branchWeight = statisticsContainer[1]
        delta_fitness = branchWeight*branch_weight_modifier
        fitness += delta_fitness
        s +=  "| BranchW: " + str(delta_fitness)

        undergroundWeight = statisticsContainer[2]
        delta_fitness = undergroundWeight*underground_modifier
        fitness += delta_fitness
        s +=  "| Under: " + str(delta_fitness)

        endLeavesWeight = statisticsContainer[3]
        delta_fitness = endLeavesWeight*end_leaves_modifier
        fitness += delta_fitness
        s +=  "| EndLeaves: " + str(delta_fitness)

        fruitsWeight = statisticsContainer[4]
        delta_fitness = fruitsWeight*fruits_modifier
        fitness += delta_fitness
        s +=  "| Fruits: " + str(delta_fitness)

        branchSizeRatio = statisticsContainer[5]
        delta_fitness = branchSizeRatio*branch_size_ratio_modifier
        fitness += delta_fitness
        s +=  "| Size Ratio: " + str(delta_fitness)


        # We want tall trees (high max z)
        if len(verts) == 0:
            delta_fitness = 0
        else:
            delta_fitness = max([v.z for v in verts])
            delta_fitness /= len(verts) # This makes it more or less normalized
        tall_fitness = delta_fitness
        delta_fitness *= tall_modifier
        fitness += delta_fitness
        s +=  "| Tall: " + str(delta_fitness)

        # We want trees high towards the value
        if len(verts) == 0:
            delta_fitness = 0
        else:
            delta_fitness = 10-abs(target_height-max([v.z for v in verts]))
        fitness += delta_fitness
        s += " | Tall target: " + str(delta_fitness)

        # We want trees that span out (high minimum span on y and x)
        if len(verts) == 0:
            delta_fitness = 0
            balance_x = 0
            balance_y = 0

        else:
            span_x_pos = max([v.x for v in verts])
            span_x_neg = -min([v.x for v in verts])
            span_y_pos = max([v.y for v in verts])
            span_y_neg = -min([v.z for v in verts])

            # We want the trees to have a balanced appearance

            # The span ratios should be as close to 1 as possible
            if abs(span_x_pos) < 0.001 or abs(span_x_neg) < 0.001:
                balance_x = 0
            elif span_x_pos == span_x_neg:
                balance_x = 1
            else:
                #print("Ratio span x:" + str(span_x_pos/span_x_neg))
                #balance_x = min(1,abs(1/((span_x_pos+1)/(span_x_neg+1) -1)))
                balance_x = min(1,1/min(abs(span_x_pos-span_x_neg),1))

            if abs(span_y_pos) < 0.001 or abs(span_y_neg) < 0.001:
                balance_y = 0
            elif span_y_pos == span_y_neg:
                balance_y = 1
            else:
                balance_y = min(1,1/min(abs(span_y_pos-span_y_neg),1))
                #print("Ratio span y:" + str(span_y_pos+1/span_y_neg))
                #balance_y = min(1,abs(1/((span_y_pos+1)/(span_y_neg+1) -1)))  # The span ratio should be as close to 1 as possible

            """
            if verbose:
                print("Balance x: " + str(balance_x))
                print("Balance y: " + str(balance_y))

                #min_span = min([span_x_pos*span_x_neg , span_y_pos*span_y_neg])
                #print("Min span: " + str(min_span))
                print("Spans: " + str(span_x_pos) + " "
                    + str(span_x_neg) + " "
                    + str(span_y_pos) + " "
                    + str(span_y_neg) + " ")
            """

            #span_x = (max([v.x for v in verts]) - min([v.x for v in verts]))
            #span_y = (max([v.y for v in verts]) - min([v.y for v in verts]))
            #delta_fitness = span_x_pos*span_x_neg*10 + span_y_pos*span_y_neg*10
            #delta_fitness = span_x_pos + span_x_neg + span_y_pos + span_y_pos + span_x_pos*span_x_neg + span_y_pos*span_y_pos
            #print("FIT: " + str(delta_fitness))

            delta_fitness = balance_x+balance_y
        span_fitness = delta_fitness
        delta_fitness *= span_modifier
        fitness += delta_fitness
        s +=  "| Span: " + str(delta_fitness)

        if len(verts) > 0:
            # We want trees spanning towards the target value, on all four directions
            delta_fitness = 10 - abs(target_volume_span-span_x_pos) -  abs(target_volume_span-span_x_neg)  -  abs(target_volume_span-span_y_pos)  -  abs(target_volume_span-span_y_neg)
            #avg_span = (span_x_pos+span_y_pos + span_x_neg + span_y_neg)/4
            #delta_fitness = 10-abs(target_volume_span-avg_span)
            fitness += delta_fitness
            s += " | Span target: " + str(delta_fitness)

        #fitness *= tall_fitness
        #fitness *= span_fitness
        delta_fitness = (tall_fitness*tall_fitness*span_fitness*span_fitness)*tallspan_modifier
        fitness += delta_fitness
        s +=  "| TallSpan: " + str(delta_fitness)

        delta_fitness = (balance_x*balance_y)*balance_modifier
        fitness += delta_fitness
        s +=  "| Balance: " + str(delta_fitness)

        s+= "\nTot fitness: " + str(fitness)
        if verbose: print(s)

        #print("Tall: " + str(tall_fitness) + "  Span: " + str(span_fitness))
        #print("Fitness: " + str(p.fitness) + " pString: " + str(pStringResult))
        return fitness

if __name__ == "__main__":
    from turtles.turtle import *
    from procedural.plantsincrementalgenerator import *

    print("Start testing GeneticEvolver")

    class Test:
        def __init__(self, seed):
            turtle = Turtle()

            evolver = GeneticEvolver(turtle, verbose = False,
                                     mini_verbose = False,
                                     randomSeed = seed)
            evolver.initialPopulationGenerationChoice = InitialPopulationGenerationChoice.FROM_AUTOMATED_EVOLUTION

            generator = PlantsIncrementalGenerator(verbose = False, parameterized = True, randomSeed = seed)
            generator.setLSystem(ParametricLSystem())
            generator.resetToSimple()
            evolver.setGenerator(generator)

            self.evolver = evolver

        def testPopulationGenerationRandom(self, populationSize):
            print("\nTEST - Population Generation (Random)")
            self.evolver.initialPopulationGenerationChoice = InitialPopulationGenerationChoice.RANDOMIZED
            population = self.evolver.generatePopulation(populationSize)

            print("\nGenerated instances are: ")
            for instance in population: print(instance.toShortString())
            print("\nBest instance is:\n" + self.evolver.getBestInstance().toShortString())


        def testPopulationGenerationAutomated(self, size):
            print("\nTEST - Population Generation (Automated)")
            self.evolver.initialPopulationGenerationChoice = InitialPopulationGenerationChoice.FROM_AUTOMATED_EVOLUTION
            population = self.evolver.generatePopulation(size)

            print("\nGenerated instances are: ")
            for instance in population: print("\n" + str(instance.toGenomeRepresentation()) + "\n With fitness: " + str(instance.fitness))
            print("\nBest instance is:\n" + str(self.evolver.getBestInstance()))

        def testCrossover(self):
            self.evolver.verbose = True
            self.evolver.mini_verbose = True
            print("\n\nTEST - Crossover")
            inst1 = GeneticInstance(ParametricLSystem())
            inst1.lsystem.setAxiomFromString("A(1)F(2)")
            inst1.lsystem.addProductionFromString("F(x):*->F(x)F(x)")
            inst1.lsystem.addProductionFromString("A(x):*->A(x)A(x)")
            #inst1.lsystem.addProductionFromString("B:*->BB")
            inst1.randomizeAdditionalParameters(self.evolver.rnd)
            self.evolver.applyFitnessFunction(inst1)

            print("\nInstance 1 is:")
            print(inst1)

            inst2 = GeneticInstance(ParametricLSystem())
            inst2.lsystem.setAxiomFromString("F(1)D(2)B(0.2)")
            inst2.lsystem.addProductionFromString("F(x):*->F(x)+(90)F(x)")
            inst2.lsystem.addProductionFromString("A(x):*->-(90)F(x)+(90)F(x)")
            inst2.randomizeAdditionalParameters(self.evolver.rnd)
            self.evolver.applyFitnessFunction(inst2)

            print("\nInstance2 is:")
            print(inst2)

            #print("\nPerforming crossover:")
            pair = [inst1,inst2]
            offspring = self.evolver.crossPair(pair)

            print("\nOffspring is:")
            for off in offspring: 
                self.evolver.applyFitnessFunction(off)
                print("\n" + str(off))

        def testMutation(self):
            print("\n\nTEST - Mutation")
            inst1 = GeneticInstance(ParametricLSystem())
            inst1.lsystem.setAxiomFromString("A(1)F(2)B(0.2)")
            inst1.lsystem.addProductionFromString("F(x):*->F(x)F(x)")
            inst1.lsystem.addProductionFromString("A(x):*->A(x)A(x)")
            #inst1.lsystem.addProductionFromString("B:*->BB")
            inst1.randomizeAdditionalParameters(self.evolver.rnd)

            mutated_instance = self.evolver.mutateInstance(inst1)

            print("\nMutated is:")
            print("\n" + mutated_instance.toShortString())


        def testEvolution(self, populationSize, nIterations, targetFitness):
            print("\n\nTEST - Evolution")
            self.evolver.verbose = False
            self.evolver.recap_verbose  = True
            #self.evolver.mini_verbose = True
            self.evolver.initialPopulationGenerationChoice = InitialPopulationGenerationChoice.RANDOMIZED
            self.evolver.evolve(populationSize=populationSize, nIterations=nIterations, targetFitness=targetFitness)

            print("\nBest instance is:")
            print(self.evolver.getBestInstance())

    popSize = 40
    mutationIterations = 5 # TODO: insert those!
    targetFitness = 15#5# 10
    nIterations = 2
    seed = 10

    t = Test(seed)
    t.evolver.generator.targetIterations = 3 # 3 for faster convergence
    #t.testPopulationGenerationRandom(populationSize = popSize)
    #t.testPopulationGenerationAutomated(10)
    t.testEvolution(populationSize = popSize, nIterations=nIterations, targetFitness = targetFitness)

    #t.testCrossover()
    #t.testMutation()


    print("\nFinish testing GeneticEvolver")
