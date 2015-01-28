"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
from iga.core.igaservice import IgaService
from iga.communication.communicationhandler import CommunicationHandler

class ClearAllPictures:
    """
    Clears all the pictures both locally and on the server.
    """

    def __init__(self):
        communication = CommunicationHandler()
        igaService = IgaService()

        igaService.clearAllPictures()    # Local
        communication.clearAllPictures()    # Server

if __name__ == "__main__":
    print("Start testing ClearAllPictures")
    ClearAllPictures()
    print("Finish testing ClearAllPictures")