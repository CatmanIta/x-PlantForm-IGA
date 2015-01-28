"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
import math

class Utilities:

    @staticmethod
    def getRandomTwoDigitFloat(rnd, min_v, max_v):
        return math.floor((min_v+rnd.random()*(max_v-min_v))*100)/100.0
