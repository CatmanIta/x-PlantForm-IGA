"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
from iga.core.igaservice import IgaService
from iga.communication.communicationhandler import CommunicationHandler

import time

class SteadyState:
    """
    Steady state interactive genetic algorithm.
    This runs as long as the IGA is needed.
    """

    def __init__(self,secondsBetweenUpdates = 60*15, performOnlyOnce = False, verbose=False):
        self.verbose = verbose

        # Start the communication
        self.communication = CommunicationHandler()

        # Resume the IGA service
        self.igaService = IgaService(verbose)

        if performOnlyOnce:
            self.update()
            return

        while True:
            # Sleep until the chosen time arrives
            if self.verbose: print "Waiting " + str(secondsBetweenUpdates) + "s\n"
            time.sleep(secondsBetweenUpdates)
            self.update()

    def update(self):
        """
        Perform an update step of the IGA steady state.
        """
        if self.verbose: print("START STEADY STATE UPDATE! Time: " + str(time.time()))
        if self.canSteadyStateEvolve():
            if self.verbose: print("Evolving the steady state!")
            self.updateSteadyState()
            self.evolveSteadyState()
        else:
            if self.verbose: print("Cannot evolve the steady state!")
        if self.verbose: print("End steady state update!")

    def updateSteadyState(self):
        """
        Update the steady state if an evolution occoured.
        """
        self.igaService.params.viewCount = self.communication.getViewsCount()
        if self.verbose: print("CURRENT VIEW COUNT: " + str(self.igaService.params.viewCount))
        self.igaService.params.currentGeneration += 1
        self.igaService.params.saveParamsToFile()

    def canSteadyStateEvolve(self):
        """
        Check whether we should evolve the steady state.
        """
        return self.communication.canSteadyStateEvolve(
                                                           self.igaService.params.viewCount,
                                                           self.igaService.params.populationSize,
                                                           self.igaService.params.perc_new_views,
                                                           self.igaService.params.min_individual_views,
                                                           self.igaService.params.min_valid_views
                                                           )

    def evolveSteadyState(self):
        """
        Perform the steady state evolution
        """
        databaseInstances = self.communication.selectInstances(self.igaService.params.selection_size,
                                                           self.igaService.params.min_individual_views,
                                                           self.igaService.params.tournament_size)

        instances = self.igaService.fromDatabaseInstances(databaseInstances)
        offspring = self.igaService.mutateAndRecombine(instances)

        if self.igaService.params.delete_random_instances:
            self.communication.deleteRandomInstances(len(instances), self.igaService.params.min_individual_views)

        databaseInstances = self.igaService.createDatabaseInstances(offspring)
        self.communication.uploadPopulation(databaseInstances)




if __name__ == "__main__":

    import sys
    classesPath = "C:\\Users\\user\\Desktop\\RewardSystems\\PCG\\InteractiveEvolutionServer\\xplantform\\"
    if not classesPath in sys.path: sys.path.append(classesPath)

    print("Starting SteadyState")
    seconds = 2
    steadyState = SteadyState(seconds,verbose=True)
    print("Finishing SteadyState")