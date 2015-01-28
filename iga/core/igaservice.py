"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

from turtles.turtle import Turtle
from procedural.geneticevolver import GeneticEvolver,GeneticInstance,InitialPopulationGenerationChoice
from procedural.incrementalgenerator import IncrementalGenerator
from procedural.plantsincrementalgenerator import PlantsIncrementalGenerator
from grammar.parametric.parametriclsystem import ParametricLSystem
from blender.imagegeneration.generateplantimage import *
from iga.core.experimentparameters import ExperimentParameters
from iga.core.databaseinstance import DatabaseInstance
import shutil
import os

class IgaService:
    """
    Defines the running state of the IGA steady state.
    """

    def __init__(self, verbose = False):
        self.verbose = verbose

        # Read the current experiment's parameters
        params = ExperimentParameters()

        # Create a Turtle that will be used to render the trees. Its parameters will be updated when needed.
        turtle = Turtle()

        # Initialize the genetic evolver
        lsystem = ParametricLSystem(params.randomSeed)
        generator = PlantsIncrementalGenerator(params.randomSeed,   # We use a PlantsIncrementalGenerator, so that everything evolved here is plant-like
                                         parameterized=True,        # Woooo
                                         definesProbability=0,  #TODO: fix! defines are not working because they are not saved with the instances!
                                         constantsProbability=1
                                         )
        generator.setLSystem(lsystem)
        generator.targetIterations = params.targetIterations
        #generator.branchProbability = 0.7
        #generator.mutation_steps_at_once = params.mutationStepsAtOnce
        generator.verbose = False
        generator.verbose_super = False

        evolver = GeneticEvolver(turtle)
        evolver.setGenerator(generator)
        evolver.initialPopulationGenerationChoice = InitialPopulationGenerationChoice.RANDOMIZED
        #evolver.populationInitialisationComplexifySteps = 2 # A good number to obtain a randomized tree without taking too much time
        evolver.discardEmptyEvolutions = True
        evolver.discardLSystemsLargerThan = 1000
        evolver.verbose = False
        evolver.mini_verbose = False
        evolver.recap_verbose = False

        self.params = params
        self.evolver = evolver

    def reset(self):
        """
        Reset the parameters of the IGA steady state.
        """
        self.params.resetParams()

    """
    Evolution methods
    """
    def generateInitialPopulation(self):
        """
        Generate an initial population.

        @return: The generated population.
        """
        population = self.evolver.generatePopulation(self.params.populationSize)
        if self.verbose:
            for i in range(len(population)):
                print(str(i) + ": " + str(population[i]))
                #print(population[i].lsystem.printGlobalDefinesStatus())
        return population

    def mutateAndRecombine(self,instances):
        """
        Performs a recombination operation
        """
        if self.verbose:
            print("MUTATING AND RECOMBINING")
            print("Initial instances:")
            for i in instances: 
                print(i.lsystem.niterations)
                print(i)

        crossedOffspring = self.evolver.crossover(instances)
        if self.verbose:
            print("After crossover:")
            for i in crossedOffspring: print(i)
        mutatedOffspring = self.evolver.mutate(crossedOffspring)    # TODO: make sure that no fitness is used there, so that we do not perform more operations than needed
        if self.verbose:
            print("After mutation:")
            for i in mutatedOffspring: print(i)
        return mutatedOffspring

    """
    Database to genetic instances and vice versa
    """
    def createDatabaseInstances(self, geneticInstances):
        """
        Given some genetic instances, creates database instances to populate the online database.
        """
        self.createImages(geneticInstances)

        databaseInstances = []
        for instance in geneticInstances:
            genome = instance.toGenomeRepresentation()
            dbi = DatabaseInstance(idinst=None,    # This will be updated after the upload is done
                                   genome = genome,
                                   generation=self.params.currentGeneration)
            databaseInstances.append(dbi)
        return databaseInstances

    def fromDatabaseInstances(self,databaseInstances):
        """
        Extract a set of genetic instances from database instances.

        @param databaseInstances: The instances as read from the database.
        @return: The actual genetic instances.
        """
        geneticInstances = []
        for dbi in databaseInstances:
            instance = GeneticInstance(ParametricLSystem())
            #print dbi.genome
            instance.fromGenomeRepresentation(dbi.genome)
            geneticInstances.append(instance)
        return geneticInstances

    """
    Pictures generation
    """
    def createImages(self, geneticInstances):
        """
        Open blender and produce images of the genetic instances
        """
        genomes = []
        for geneticInstance in geneticInstances:
            genomes.append(geneticInstance.toGenomeRepresentation())
        generatePlantImages(genomes)
        # We now have the output pictures. We'll get to them using the database instances' filenames

    def clearAllPictures(self):
        """
        Clear all images from the picture  folders
        """
        shutil.rmtree(PNG_OUTPUT_PATH)
        os.makedirs(PNG_OUTPUT_PATH)



if __name__ == "__main__":
    print("Test IGAService")

    print("\nTEST - Creation")
    iga = IgaService(verbose = True)
    print("\nOK - Creation")

    print("\nTEST - Generation")
    pop = iga.generateInitialPopulation()
    for p in pop:
        print(p)

    print("\nOK - Generation")

    print("\nEND TESTS")

