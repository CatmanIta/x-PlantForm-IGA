"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

class Utilities:

    @staticmethod
    def isFloat(value):
        try:
            float(value)
        except ValueError:
            return False
        return True