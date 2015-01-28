"""
    Handles communication

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

from blender.paths import PNG_OUTPUT_PATH
from iga.core.databaseinstance import DatabaseInstance

from iga.communication.httpclient import HttpClient
from iga.communication.ftpclient import FtpClient

class CommunicationHandler:

    httpServerName = 'http://localhost/plantforms/'
    ftpServerName = 'localhost'

    OK = True
    KO = False

    def __init__(self):
        try:
            self.httpClient = HttpClient(self.httpServerName)
        except Exception, e:
            print("ERROR: Problem with HTTP client connection!")
            print(e)
            exit(1)

        try:
            self.ftpClient = FtpClient(self.ftpServerName,21,"catman")
        except Exception, e:
            print("ERROR: Problem with FTP client connection!")
            print(e)
            exit(1)

    def destroy(self):
        """
        Close all communication
        """
        self.httpClient.destroy()
        self.ftpClient.destroy()


    #################
    # Commands
    #################

    def uploadPopulation(self, databaseInstances):
        for i in range(len(databaseInstances)):
            newId = self.uploadInstance(databaseInstances[i])
            databaseInstances[i].idinst = newId
        self.uploadPictures(databaseInstances)
        return self.OK

    def uploadInstance(self,databaseInstance):
        params = {}
        params['genome'] = databaseInstance.genome
        params['name'] = databaseInstance.name
        params['generation'] = databaseInstance.generation
        tokens = self.httpClient.performCommandAndGetResponse('insertInstance',params)
        return tokens[0]    # Returns the generated ID

    def selectInstances(self, selection_size, min_individual_views, tournament_size):
        params = {}
        params['selection_size'] = selection_size
        params['min_individual_views'] = min_individual_views
        params['tournament_size'] = tournament_size
        tokens = self.httpClient.performCommandAndGetResponse('selectInstances',params)

        databaseInstances = []
        #print(tokens)
        for i in range(len(tokens)/2):
            idinst = tokens[i*2]
            genome = tokens[i*2+1]
            #print("INST: " + str(idinst))
            #print("GEN: " + str(genome))
            dbi = DatabaseInstance(idinst,genome)
            databaseInstances.append(dbi)
        return databaseInstances

    def selectAllInstances(self):
        """
        Select all instances
        """
        tokens = self.httpClient.performCommandAndGetResponse('selectAllInstances')

        databaseInstances = []
        for i in range(len(tokens)/2):
            idinst = tokens[i*2]
            genome = tokens[i*2+1]
            dbi = DatabaseInstance(idinst,genome)
            databaseInstances.append(dbi)
        return databaseInstances

    def deleteRandomInstances(self,number_of_instances, min_individual_views):
        params = {}
        params['number_of_instances'] = number_of_instances
        params['min_individual_views'] = min_individual_views
        return self.httpClient.performCommand('deleteRandomInstances',params)

    def canSteadyStateEvolve(self,currentViewCount,population_size,perc_new_views,min_individual_views,min_valid_views):
        params = {}
        params['currentViewCount'] = currentViewCount
        params['population_size'] = population_size
        params['perc_new_views'] = perc_new_views
        params['min_individual_views'] = min_individual_views
        params['min_valid_views'] = min_valid_views
        return self.httpClient.performCommand('canSteadyStateEvolve',params)

    def getViewsCount(self):
        tokens = self.httpClient.performCommandAndGetResponse('getViewsCount')
        return tokens[0]

    def uploadPictures(self,databaseInstances):
        retries = 0
        while True:
            try:
                imageFolderPath = PNG_OUTPUT_PATH
                for i in range(len(databaseInstances)):
                    self.ftpClient.upload(imageFolderPath+"\\"+databaseInstances[i].filename+".png", str(databaseInstances[i].idinst)+".png")
                return self.OK
            except Exception, e:
                print(e)
                if retries == 5:
                    exit()
                else:
                    print("Retrying...")
                    retries += 1
                    self.ftpClient.connect()    # We retry the connection

    def reset(self):
        """
        Reset the whole state of the server
        """
        self.clearAllPictures()
        result = self.httpClient.performCommand('reset')
        return result

    def clearAllPictures(self):
        """
        Delete all the pictures on the server
        """
        self.ftpClient.deleteAllFiles()

if __name__ == "__main__":
    print("Start testing Communication")

    print ("\nTEST - connection")
    communication = CommunicationHandler()
    print ("TEST - OK")

    print ("\nTEST - reset")
    communication.reset()
    print ("TEST - OK")

    print ("\nTEST - views count")
    viewCount = communication.getViewsCount()
    print "View count: " + str(viewCount)
    print ("TEST - OK")

    print ("\nTEST - select")
    instances = communication.selectInstances(selection_size=2, min_individual_views=0, tournament_size=2)
    for inst in instances: print inst
    print ("TEST - OK")

    print ("\nTEST - destroy")
    communication.destroy()
    print ("TEST - OK")

    print("Finish testing Communication")
