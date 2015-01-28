"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

from procedural.core.geneticinstance import GeneticInstance

class DatabaseInstance:
    """
    An instance of a plantform as seen in the database
    """
    def __init__(self, idinst, genome, name = "anon", filename="anon", generation=None):
        self.idinst = idinst
        self.genome = genome
        self.name =  GeneticInstance.generateRandomPlantName(genome)
        self.filename =  GeneticInstance.genomeToFilename(genome)
        self.generation = generation
        # TODO: self.parent_idinst = None   # Id instance of the parent

    def __str__(self):
        return str(self.idinst) + ": " + self.name + " - " + self.genome

if __name__ == "__main__":
    print("Start testing DatabaseInstance")

    print ("TEST - create instance")
    inst = DatabaseInstance(0, "FFF")

    print("Created: " + str(inst))
    print ("TEST - OK")

    print("Finish testing DatabaseInstance")