"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
from iga.core.igaservice import IgaService
from iga.communication.communicationhandler import CommunicationHandler

class RecreateAllPictures:
    """
    Recreates all the pictures of the current instances and uploads them on the server.
    """

    def __init__(self):
        communication = CommunicationHandler()
        igaService = IgaService()

        db_instances = communication.selectAllInstances()
        genetic_instances = igaService.fromDatabaseInstances(db_instances)
        igaService.createImages(genetic_instances)
        communication.uploadPictures(db_instances)

if __name__ == "__main__":
    print("Start testing RecreateAllPictures")
    RecreateAllPictures()
    print("Finish testing RecreateAllPictures")