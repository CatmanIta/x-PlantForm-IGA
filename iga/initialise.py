"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

from iga.core.igaservice import IgaService
from iga.communication.communicationhandler import CommunicationHandler

from grammar.parametric.parametriclsystem import ParametricLSystem

class Initialise:
    """
    Handles initialization of the interactive steady-state genetic algorithm.
    This is called once, when we want to start the IGA.
    """

    def __init__(self, verbose = False):

        # Start the communication
        communication = CommunicationHandler()

        # Resume the IGA service
        self.igaService = IgaService(verbose)

        # Generate the initial population
        population = self.igaService.generateInitialPopulation()
        databaseInstances = self.igaService.createDatabaseInstances(population)

        # Upload the initial population
        if communication.uploadPopulation(databaseInstances):
            print("Upload complete!")
        else:
            print("Cannot upload!")

if __name__ == "__main__":
    print("Start testing Initialise")
    igaInit = Initialise(verbose=False)
    print("Finish testing Initialise")