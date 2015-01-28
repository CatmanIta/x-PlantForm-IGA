"""
    A GeneticInstance holds a LSystem that defines a single instance.
    It also holds additional parameters needed for generation and evolution.

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import grammar.parametric.parametriclsystem
import procedural.miscellaneous.detailshandler
import procedural.core.geneticturtleparameters

import imp
imp.reload(grammar.parametric.parametriclsystem)
imp.reload(procedural.miscellaneous.detailshandler)
imp.reload(procedural.core.geneticturtleparameters)

from grammar.parametric.parametriclsystem import ParametricLSystem
from procedural.miscellaneous.detailshandler import DetailsHandler
from procedural.core.geneticturtleparameters import GeneticTurtleParameters

import random
import base64
import string


class GeneticInstance():
    """
    Holds a lsystem as well as additional parameters.
    """
    def __init__(self, lsystem = ParametricLSystem()):
        self.lsystem = lsystem

        # Saved fitness, so that it needs not to be recomputed if it exists already
        self.fitness = 0    # TODO: Should be None at the beginning

        # Additional parameters used by the genetic algorithm
        self.turtleParameters = GeneticTurtleParameters()

    def copyParametersFrom(self,other_instance):
        self.turtleParameters.copyFrom(other_instance.turtleParameters)

    def randomizeAdditionalParameters(self,rnd):
        self.turtleParameters.randomize(rnd)

    def mutateAdditionalParameters(self,rnd):
        self.turtleParameters.mutateAdditionalParameters(rnd)

    def __str__(self):
        s = "" #"Instance:"
        s += "F: " + str(self.fitness)
        s += ""+ str(self.lsystem)
        s += "\n " + "[" + str(self.turtleParameters) + "]"
        return s

    def toShortString(self):
        return "F: " + str(self.fitness) + "\t" + str(self.toGenomeRepresentation())

    ##########
    # Genome
    ##########

    def toGenomeRepresentation(self):
        # "||||" separates these big elements
        full_genome = self.lsystem.toGenomeRepresentation()
        full_genome += "||||" + self.turtleParameters.toGenomeRepresentation()
        return full_genome

    def fromGenomeRepresentation(self,genome):
        #print(genome)
        tokens = genome.split("||||")
        #print("TOKENS:::")
        #for t in (tokens):
        #    print(t)
        self.lsystem.fromGenomeRepresentation(tokens[0])
        self.turtleParameters.fromGenomeRepresentation(tokens[1])

    @staticmethod
    def genomeToFilename(genome):
        #return base64.urlsafe_b64encode(genome)
        valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in genome if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        filename = 'inst_' + filename
        filename = filename[:30]    # Only the first 30 chars
        return filename

    @staticmethod
    def generateRandomPlantName(genome):
        """ Generates a random plant name """
        # TODO: Should be based on the genome!
        syllabes = ["al","inus","la","ta","va","inc","cannaba","ium","frax","inus"]
        name = ""
        for i in range(random.randint(4,7)):
            name += syllabes[random.randint(0,len(syllabes)-1)]
            if random.random() < 0.2: name += " "
        return name

    @staticmethod
    def copyFrom(other_instance):
        new_instance = GeneticInstance(ParametricLSystem.copyFrom(other_instance.lsystem))
        new_instance.copyParametersFrom(other_instance)
        return new_instance

if __name__ == "__main__":
    print("Start testing GeneticInstance")

    rnd = random.Random()

    print("\nCreation")
    gi = GeneticInstance()
    print(gi)

    print("\nRandomize additional parameters")
    gi.randomizeAdditionalParameters(rnd)
    print(gi)

    print("\nMutate additional parameters")
    gi.mutateAdditionalParameters(rnd)
    print(gi)

    print("\nTo genome")
    genome = gi.toGenomeRepresentation()
    print(genome)

    print("\nTo filename")
    print(GeneticInstance.genomeToFilename(genome))

    print("\nFinish testing GeneticInstance")
