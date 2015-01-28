"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
from iga.core.igaservice import IgaService
from iga.communication.communicationhandler import CommunicationHandler

class Reset:
    """
    Resets the IGA server to an initial state
    """
    def __init__(self):
        communication = CommunicationHandler()
        igaService = IgaService()

        if not communication.reset():
            print("Cannot reset!")
            return
        else:
            print("Reset complete!")

        igaService.reset()

if __name__ == "__main__":
    print("Start testing Reset")
    Reset()
    print("Finish testing Reset")