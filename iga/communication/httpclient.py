"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import urllib2
import urllib

class HttpClient:
    """
    Handles communication through http to the web server
    """
    OK = True
    KO = False

    def __init__(self, hostName):
        self.hostName = hostName

    def destroy(self):
        pass

    def performCommand(self, commandName, params = {}):
        try:
            postData = urllib.urlencode(params)
            url = self.hostName + "cmd_" + commandName + ".php"
            print("Posting URL: " + str(url) + " with data " + str(postData))
            response = urllib2.urlopen(url,postData)
            #print response.info()
            response_result = response.read()
            if response_result[0:2] != "OK": raise Exception("Wrong response: '" + str(response_result) + "'")
            response.close()
        except Exception, e:
            print("EXCEPTION: " + str(e))
            return self.KO
        return response_result

    def performCommandAndGetResponse(self, commandName, params = {}):
        try:
            response_result = self.performCommand(commandName,params)
            if response_result == self.KO: raise Exception("Wrong response: '" + str(response_result) + "'")
            tokens = self.handleResult(response_result)
            return tokens
        except Exception, e:
            print("EXCEPTION: " + str(e))
            return self.KO

    def handleResult(self,result):
        result_choice = result[0:2]
        if result_choice == self.KO: raise Exception("Bad result obtained!")
        params = result[2:len(result)]  # Remove the OK
        tokens = params.split("<br>")   # Each token is separated by this string
        del tokens[0]                   # First element is an empty string
        return tokens

if __name__ == "__main__":
    print("Start testing HttpClient")

    print ("\nTEST - connection")
    httpClient = HttpClient('http://localhost/plantforms/')
    print ("TEST - OK")

    print ("\nTEST - command")
    httpClient.performCommand("selectInstances")
    print ("TEST - OK")

    print ("\nTEST - destroy")
    httpClient.destroy()
    print ("TEST - OK")

    print("Finish testing HttpClient")
