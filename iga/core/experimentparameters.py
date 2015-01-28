"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
import os

class ExperimentParameters:
    """
    Holds parameters to configure an experiment with the IGA.
    """
    def __init__(self,savePath = None):
        """
        Constant parameters are written here
        """
        if savePath is None:
            savePath = os.getcwd()+"//saved_params"
        self.savePath = savePath

        # Evolution parameters
        self.populationSize = 50 # 50 IS BETTER: A lot of initial instances for added variation
        self.randomSeed = 0
        self.selection_size = 8
        self.tournament_size = 4
        self.delete_random_instances = True    # If True, the number of instances is fixed, if False, all instances will be kept (and it will converge)

        # Generation parameters
        self.targetIterations = 4       # Higher -> more complexity, but slower
        self.mutationStepsAtOnce = 1    # Higher -> each generation is more different in confront to the parents

        # Evolution trigger parameters
        self.min_valid_views = 4
        self.min_individual_views = 0
        self.perc_new_views = 0.15      # At least this percent of the population size must be viewed min_individual_views times

        # Additional parameters are read from a file, so that they are saved between runs
        self.readParamsFromFile()

    def resetParams(self):
        self.viewCount = 0
        self.currentGeneration = 0
        self.saveParamsToFile()

    def readParamsFromFile(self):
        try:
            f =  open(self.savePath, 'r')
            self.viewCount = int(f.readline())
            self.currentGeneration =  int(f.readline())
            f.close()
        except Exception, e:
            print(e)
            print ("We create a new file.")
            self.resetParams()

    def saveParamsToFile(self):
        s = ""
        s += str(self.viewCount)+"\n";
        s += str(self.currentGeneration);
        f =  open(self.savePath, 'w')
        f.write(s)
        f.close()

    def __str__(self):
        s = ""
        s += "View count: " + str(self.viewCount)+"\n";
        s += "Current generation: " + str(self.currentGeneration);
        return s


if __name__ == "__main__":
    print("Start testing ExperimentParameters")

    params = ExperimentParameters()

    print ("TEST - save parameters")
    params.saveParamsToFile()

    print ("TEST - read parameters")
    params.readParamsFromFile()

    print("Created: " + str(params))
    print ("TEST - OK")

    print("Finish testing ExperimentParameters")

