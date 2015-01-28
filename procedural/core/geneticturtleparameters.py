"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import procedural.miscellaneous.detailshandler
import procedural.miscellaneous.utilities

import imp
imp.reload(procedural.miscellaneous.detailshandler)
imp.reload(procedural.miscellaneous.utilities)

from procedural.miscellaneous.detailshandler import DetailsHandler
from procedural.miscellaneous.utilities import Utilities


class GeneticTurtleParameters():
    """
    Parameters that define the turtle graphics behavior inside a GeneticInstance.
    """

    def __init__(self):
        # Turtle
        self.branch_radius = 1.0
        self.tropism_susceptibility = 0.1

        # TODO: I may put all of these in classes, or a dict, so it is easier to change them... they'd be 'GeneticProperties' or 'GeneticParameters'
        # Renderer
        self.use_canopy = False
        self.details_scale = 2.0
        self.trunk_material_choice = 0
        self.leaf_material_choice = 0
        self.leaf_choice = 0
        self.bulb_choice = 0
        self.flower_choice = 0
        self.fruit_choice = 0


    def toGenomeRepresentation(self):
        g = ""
        g += "" +str(self.branch_radius)    # TODO: cut to 2 decimals!
        g += "|"+str(self.tropism_susceptibility)
        g += "|"+str(self.details_scale)
        g += "|"+ str(1 if self.use_canopy else 0)
        g += "|"+str(self.trunk_material_choice)
        g += "|"+str(self.leaf_material_choice)
        g += "|"+str(self.leaf_choice)
        g += "|"+str(self.bulb_choice)
        g += "|"+str(self.flower_choice)
        g += "|"+str(self.fruit_choice)
        return g

    def fromGenomeRepresentation(self,g):
        tokens = g.split("|")
        self.branch_radius = float(tokens[0])
        self.tropism_susceptibility = float(tokens[1])
        self.details_scale = float(tokens[2])
        self.use_canopy = True if (int(tokens[3]) == 1) else False
        self.trunk_material_choice = int(tokens[4])
        self.leaf_material_choice = int(tokens[5])
        self.leaf_choice = int(tokens[6])
        self.bulb_choice = int(tokens[7])
        self.flower_choice= int(tokens[8])
        self.fruit_choice = int(tokens[9])

    def copyFrom(self,other_parameters):
        o = other_parameters
        self.branch_radius = o.branch_radius
        self.tropism_susceptibility = o.tropism_susceptibility
        self.details_scale = o.details_scale
        self.trunk_material_choice = o.trunk_material_choice
        self.leaf_material_choice = o.leaf_material_choice
        self.use_canopy = o.use_canopy
        self.leaf_choice = o.leaf_choice
        self.bulb_choice = o.bulb_choice
        self.flower_choice = o.flower_choice
        self.fruit_choice = o.fruit_choice

    def randomize(self,rnd):
        self.branch_radius = Utilities.getRandomTwoDigitFloat(rnd,0.1,2)
        self.tropism_susceptibility = Utilities.getRandomTwoDigitFloat(rnd,0,0.2)
        self.details_scale = Utilities.getRandomTwoDigitFloat(rnd,0.1,5.0)
        self.use_canopy = 0 #rnd.random()<0.5

        self.trunk_material_choice = rnd.randint(0,1)
        self.leaf_material_choice = rnd.randint(0,1)
        self.leaf_choice = rnd.randint(0,len(DetailsHandler.LEAF_NAMES)-1)
        self.bulb_choice = rnd.randint(0,len(DetailsHandler.BULB_NAMES)-1)
        self.flower_choice = rnd.randint(0,len(DetailsHandler.FLOWER_NAMES)-1)
        self.fruit_choice =  rnd.randint(0,len(DetailsHandler.FRUIT_NAMES)-1)


    def mutateAdditionalParameters(self, rnd):
        if rnd.random() < 0.1:  self.branch_radius = Utilities.getRandomTwoDigitFloat(rnd,0.1,2)
        if rnd.random() < 0.1:  self.tropism_susceptibility = Utilities.getRandomTwoDigitFloat(rnd,0,0.2)
        if rnd.random() < 0.1:  self.details_scale = Utilities.getRandomTwoDigitFloat(rnd,0.1,5.0)
        if rnd.random() < 0.1:  self.use_canopy = 0 # rnd.random()<0.5

        if rnd.random() < 0.1: self.trunk_material_choice = rnd.randint(0,1)
        if rnd.random() < 0.1: self.leaf_material_choice = rnd.randint(0,1)
        if rnd.random() < 0.1: self.leaf_choice = rnd.randint(0,len(DetailsHandler.LEAF_NAMES)-1)
        if rnd.random() < 0.1: self.bulb_choice = rnd.randint(0,len(DetailsHandler.BULB_NAMES)-1)
        if rnd.random() < 0.1: self.flower_choice = rnd.randint(0,len(DetailsHandler.FLOWER_NAMES)-1)
        if rnd.random() < 0.1: self.fruit_choice = rnd.randint(0,len(DetailsHandler.FRUIT_NAMES)-1)

    def __str__(self):
        return self.toGenomeRepresentation()

