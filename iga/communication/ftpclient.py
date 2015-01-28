"""
    FTP networking.

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

from ftplib import FTP

class FtpClient:
    """
    Handles FTP communication
    """

    def __init__(self, hostName, port = 0, username = "", password = ""):
        self.ftp = FTP()
        self.hostName = hostName
        self.port = port
        self.username = username
        self.password = password
        self.connect()

    def connect(self):
        """
        Open the connection
        """
        self.ftp.connect(self.hostName, self.port, timeout = 10)
        self.ftp.login(self.username,self.password)

    def cwd(self,dirname):
        """
        Change directory
        """
        self.ftp.cwd(dirname)

    def ls(self):
        """
        Check contents
        """
        return self.ftp.retrlines('LIST')

    def upload(self, fromPath, toPath):
        """
        Upload a file in binary mode
        """
        f = open(fromPath,'rb')
        self.ftp.storbinary('STOR ' + toPath, f)
        f.close()

    def destroy(self):
        """
        Close the connection
        """
        self.ftp.quit()

    def deleteAllFiles(self):
        """
        Delete all files on the server
        """
        for filename in self.ftp.nlst():
            self.ftp.delete(filename)


if __name__ == "__main__":
    print("Start testing FtpClient")

    print ("\nTEST - connection")
    ftpClient = FtpClient('localhost', port = 0, username = "catman", password = "")
    print ("TEST - OK")

    print ("\nTEST - list directories")
    ftpClient.ls()
    print ("TEST - OK")

    print ("\nTEST - change directory")
    ftpClient.cwd(".")
    print ("TEST - OK")

    print ("\nTEST - quit")
    ftpClient.destroy()
    print ("TEST - OK")

    print("Finish testing FtpClient")