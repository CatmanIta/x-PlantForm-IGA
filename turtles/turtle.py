"""
    Classes for drawing L-system structures.
    The Turtle defines the points corresponding to the turtle representation of an L-system structure.

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import turtles.my_mathutils

import imp
imp.reload(turtles.my_mathutils)

from turtles.my_mathutils import *

from math import cos,sin,pi
import random


class Quad:
    """
    This represents an oriented Quad.
    """
    def __init__(self,pos,eul):
        """
        @param pos: The position of the Quad
        @param eul: The orientation of the Quad in euler angles
        """
        self.pos = pos
        self.eul = eul

class TurtleResult:
    """
    A container for the results of drawing with a turtle.
    """
    ID = 0

    def __init__(self, instance_index, verts, edges, radii, leaves, bulbs, flowers, fruits):
        self.idd = self.ID
        self.ID += 1

        self.instance_index = instance_index
        self.verts = verts
        self.edges = edges
        self.radii = radii

        self.leaves = leaves
        self.bulbs = bulbs
        self.flowers = flowers
        self.fruits = fruits

    def __str__(self):
        s = "\nTurtle Result " + str(self.idd) + ":"
        s += "\nVerts: " + str(len(self.verts))
        s += "\nEdges: " + str(len(self.edges))
        return s

class Turtle:
    """
    A class that is used to convert a pL-String into a graphical structure.
    """

    def __init__(self, verbose = False):
        """
        Noise should be in the [0,1] range, with 0 meaning no noise and 1 meaning noise equal to the initial value.
        """
        self.verbose = verbose

        # Parameters that can be modified before drawing
        self.angle = 30
        self.step = 1
        self.lengthNoise = 0
        self.angleNoise = 0
        self.randomSeed = None
        self.defaultRadius = 0.1

        self.tropism = (0,0,-1)
        self.tropism_susceptibility = 0.4
        self.elasticityDependsOnBranchRadius = False
        self.heuristic_details_orientations = True  # If True, the details will be oriented according to some heuristics, for better visual results
        #TODO: self.force_radius_to_zero_on_ends = True

    def loadParameters(self,turtleParameters):
        """
        Loads parameters from a container.
        """
        self.defaultRadius = turtleParameters.branch_radius
        self.tropism_susceptibility = turtleParameters.tropism_susceptibility

    def draw(self, structure, instance_index = 0, statisticsContainer = None):
        """
        Draws from a pL-string

        @note: the parameter structure must be a string, not a pString!

        @param structure: The structure to convert into a graphical representation.
        @param instance_index: Index of this instance in a set of randomized instances.
        @param statisticsContainer: A container for statistics of this turtle, populated and then used externally.
        """
        assert isinstance(structure,str), "The structure parameter must be a string"

        # Statistics
        saveStatistics = statisticsContainer is not None
        if saveStatistics:
            trunkWeightStatistic = 0            # Will be higher, the longer the trunk is
            maxBranchWeightStatistic = 0        # Will be higher, the longer branches are (gets the maximum branch length)
            undergroundWeightStatistic = 0      # Will be higher, the more the branch has vertices with y < 0
            endLeavesCount = 0                  # Will be higher, the more the leaves are towards the end-depth branches (ratio on the total number of leaves)
            endBulbsCount = 0                   # Will be higher, the more the bulbs are towards the end-depth branches (ratio on the total number of bulbs)
            endFlowersCount = 0                 # Will be higher, the more the leaves are flowers the end-depth branches (ratio on the total number of flowers)
            fruitsCount = 0                     # Will be higher, the more fruits are there (ratio on the total number of details)
            detailsCount = 0                    # Will be higher, the more generic details are there

        if self.verbose: print("\nGot structure: " + structure)

        # Each instance has a different seed (for randomization)
        self.rnd = random.Random()
        if self.randomSeed: self.rnd.seed(self.randomSeed+instance_index)

        # Initializing the drawing
        last_i = 0
        tot_i = 0
        index_stack = []

        eul = Euler((0,0,0))
        eul_stack = []
        last_branch_euler = Euler((0,0,0))

        pos = Vector((0,0,0))
        pos_stack = []

        leaves  = [] # Array of leaves positions
        bulbs   = []
        flowers = []
        fruits  = []

        current_radius = self.defaultRadius
        self.randoms = []    # Array of extracted random values

        branch_depth = 0
        branch_sizes = [self.defaultRadius]     # Array of radii of each branch depth level, can be used for weight computation
        branch_lengths = [0]                    # Array of lengths for each branch depth level, can be used for weight computation

        radii_stack = []
        radii = []
        verts = []
        edges = []

        firstPointAdded  = False
        i = 0    # We'll iterate over all the characters
        while i <  len(structure):
            c = structure[i]
            if self.verbose: print("\nChecking character " + c + " at " + str(i))

            if c == '!':
                # Change branch radius
                value, i = self.extractParameter(structure,i,self.defaultRadius)
                value = max(1,value)
                if self.verbose: print("CURRENT RADIUS: " + str(current_radius))

            if c == 'F':
                # Go forward, drawing an edge
                value, i = self.extractParameter(structure,i,self.step)
                # Randomize
                rndValue = self.getRandom(last_i)
                value = value + value*rndValue*self.lengthNoise

                # Apply
                up = Vector((0,0,1))
                direction = Vector((0,0,1))
                #print("Dir up rot: " + str(direction))
                #print("Current rotation eulers: " + str(eul))
                direction.rotateEul(eul) # Segment's heading
                #print("Dir after rotation: " + str(direction))

                # Add tropism: bend towards the tropism vector
                # Vector tropism model (see "The Algorithmic Beauty of Plant" and "L-systems, Twining Plants, Lisp")
                #branch_length = value
                if self.elasticityDependsOnBranchRadius:    elasticity = 1/current_radius
                else:   elasticity = 1

                if self.tropism_susceptibility > 0:
                    tropism_vector = Vector(self.tropism)
                    #print("DIR: " + str(direction))
                    #print("tropism: " + str(tropism_vector*self.tropism_susceptibility*elasticity))
                    bending_quaternion = self.getQuaternionBetween(direction,tropism_vector*self.tropism_susceptibility*elasticity)
                    direction.rotateQuat(bending_quaternion)
                    #print("Bending quaternion: " + str(bending_quaternion))
                    #print("Dir after bending: " + str(direction))

                # Save the new euler values
                quaternion = self.getQuaternionBetween(up,direction)
                #print("Quaternion from up to new dir: " + str(quaternion))
                eul = quaternion.to_euler(eul) # Argument is the compatible euler

                #print("New eul from quaternion: " + str(eul))

                # Add the first point now, if needed
                if firstPointAdded is False:
                    self.addPos(pos,verts,current_radius,radii)
                    firstPointAdded = True

                # Add the new point
                pos = pos+direction*value
                self.addPos(pos,verts,current_radius,radii)

                if self.verbose: print("Moving to " + str(pos) + "  at direction " + str(direction) + " | index: " +str(last_i) + " to " + str(tot_i+1) + " with step " + str(value))

                tot_i += 1
                edges.append([last_i,tot_i])
                last_i = tot_i

                #print("CHECKING STACK: ")
                #for p in pos_stack: print(p)

                last_branch_euler = eul.copy()

                if saveStatistics:
                    branch_lengths[branch_depth] += 1           # We sum the length of the branch for this depth level    TODO: maybe add the 'value'? actual length?
                    branch_sizes[branch_depth] += current_radius    # We sum the radius for each advancement of the branch for this depth level, we'll then average it


            elif c == '+':
                eul_delta, i = self.changeOrientation(structure,i,(1,0,0))
                eul += eul_delta
            elif c == '-':
                eul_delta, i = self.changeOrientation(structure,i,(-1,0,0))
                eul += eul_delta
            elif c == '|':
                eul.x += pi
            elif c == '&':
                eul_delta, i = self.changeOrientation(structure,i,(0,1,0))
                eul += eul_delta
            elif c == '^':
                eul_delta, i = self.changeOrientation(structure,i,(0,-1,0))
                eul += eul_delta
            elif c == '\\':
                eul_delta, i = self.changeOrientation(structure,i,(0,0,1))
                eul += eul_delta
            elif c == '/':
                eul_delta, i = self.changeOrientation(structure,i,(0,0,-1))
                eul += eul_delta

            elif c == '[':
                # Open a new branch
                pos_stack.append(pos.copy())
                eul_stack.append(eul.copy())
                index_stack.append(last_i)
                radii_stack.append(current_radius)

                branch_depth+=1
                if len(branch_lengths) <= branch_depth:
                    branch_lengths.append(0)
                    branch_sizes.append(current_radius)
                else:
                    branch_lengths[branch_depth] = 0
                    branch_sizes[branch_depth] = current_radius

                #print("Branching at " + str(pos) + " with index " + str(last_i))

                #print("Pos stack has: ")
                #for p in pos_stack:
                #    print(p)

                #print("Orientation stack has: ")
                #for p in orientation_stack:
                #    print(p)


            elif c == ']':
                # Close the latest open branch

                #print("Pos stack had: ")
                #for p in pos_stack:
                #    print(p)

                if saveStatistics:
                    if branch_lengths[branch_depth] > maxBranchWeightStatistic:
                        maxBranchWeightStatistic = branch_lengths[branch_depth]
                        #print("Updated max branch weight to " + str(maxBranchWeightStatistic))
                branch_depth-=1

                last_pos = pos_stack[-1]
                pos = last_pos.copy()
                pos_stack = pos_stack[0:len(pos_stack)-1]#.remove(-1)

                last_index = index_stack[-1]
                last_i = last_index
                index_stack = index_stack[0:len(index_stack)-1] #.remove(-1)

                last_eul = eul_stack[-1]
                eul = last_eul
                eul_stack = eul_stack[0:len(eul_stack)-1]

                last_radius = radii_stack[-1]
                current_radius = last_radius
                radii_stack = radii_stack[0:len(radii_stack)-1]

                #print("Resuming from " + str(pos) + " with index " + str(last_i))
                #print("Orientation stack has: ")
                #for p in orientation_stack:
                #    print(p)


            elif c == "L":
                # This is a LEAF node, save its position and orientation
                isEndPoint = self.checkIsEndPoint(i,structure)
                tmp_eul = self.orientWithBranch(eul,last_branch_euler,isEndPoint)
                q = Quad(pos.copy(),tmp_eul)
                leaves.append(q)

                if saveStatistics:
                    if isEndPoint:  endLeavesCount += 1
                    detailsCount += 1


            elif c == "B":
                # This is a BULB node, save its position and orientation
                isEndPoint = self.checkIsEndPoint(i,structure)
                tmp_eul = self.orientWithBranch(eul,last_branch_euler,isEndPoint)
                q = Quad(pos.copy(),tmp_eul)
                bulbs.append(q)

                if saveStatistics:
                    if isEndPoint:  endBulbsCount += 1
                    detailsCount += 1

            elif c == "K":
                # This is a FLOWER node, save its position and orientation
                isEndPoint = self.checkIsEndPoint(i,structure)
                tmp_eul = self.orientWithBranch(eul,last_branch_euler,isEndPoint)
                q = Quad(pos.copy(),tmp_eul)
                flowers.append(q)

                if saveStatistics:
                    if isEndPoint: endFlowersCount += 1
                    detailsCount += 1

            elif c == "R":
                # This is a FRUIT node, save its position and orientation
                isEndPoint = self.checkIsEndPoint(i,structure)
                tmp_eul = self.orientWithGround(eul, last_branch_euler, isEndPoint)
                q = Quad(pos.copy(),tmp_eul)
                fruits.append(q)

                if saveStatistics:
                    if isEndPoint: fruitsCount += 1
                    detailsCount += 1
            i+=1

            #print(verts)
            #print(edges)

        result = TurtleResult(instance_index,verts,edges,radii,leaves,bulbs,flowers,fruits)

        if saveStatistics:
            trunkWeightStatistic = branch_lengths[0]
            statisticsContainer.append(trunkWeightStatistic)
            statisticsContainer.append(maxBranchWeightStatistic)

            undergroundWeightStatistic = 0
            for v in verts:
                if v.z < 0: undergroundWeightStatistic += (-v.z)
            statisticsContainer.append(undergroundWeightStatistic)

            #print("Leaves: " + str(len(leaves)) + " of which ending: " + str(endLeavesCount))
            #print("Flowers: " + str(len(flowers)) + " of which ending: " + str(endFlowersCount))
            tot_details = len(leaves)+len(bulbs)+len(flowers)
            if tot_details > 0: endDetails = (endLeavesCount + endBulbsCount + endFlowersCount)/tot_details
            else: endDetails = 0
            statisticsContainer.append(endDetails)

            if detailsCount > 0:    fruitsRatio = fruitsCount/detailsCount
            else:                   fruitsRatio = 0
            statisticsContainer.append(fruitsRatio)

            # Branch size ratio is: 0 if the trunk and branches have similar radii, 1 if the branches have smaller radii and -1 if the trunk has smaller radius
            for i in range(len(branch_sizes)):
                #print("Brach size sum: " + str(branch_sizes[i]))
                branch_sizes[i] = branch_sizes[i]/ max(1,branch_lengths[i])
                #print("Brach size avg: " + str(branch_sizes[i]))

            branch_deltas = [ (branch_sizes[i] - branch_sizes[i+1]) for i in range(len(branch_sizes)-1) ]
            #print(branch_deltas)
            if len(branch_deltas) > 0:
                branch_size_ratio = sum(branch_deltas)/len(branch_deltas)
            else:
                branch_size_ratio = 0
            branch_size_ratio = max(-1,min(1,branch_size_ratio))
            statisticsContainer.append(branch_size_ratio)

            """
            print("Branches statistics: ")
            i = 0
            for i in range(len(branch_sizes)):
            s = "Depth " + str(i) + " size " + str(branch_sizes[i]) + " length " + str(branch_lengths[i])
            if i < len(branch_sizes)-1:
                s += " delta: " + str(branch_deltas[i])
            print(s)"""

        return result

    def changeOrientation(self,structure,i,axisVector):
        """
        Changes the orientation of the branch according to the chosen rotation

        @param structure: The structure of the system
        @param i: The current character's index
        @param axisVector: The vector representing the axis of rotation
        """
        value, i = self.extractParameter(structure,i,self.angle)
        rnd_value = self.getRandom(i)
        delta_value = self.angleNoise*rnd_value
        value = value + delta_value*value
        value = value/180*pi
        eulOffset = Euler(axisVector)
        #print("Orientation stack has: ")
        #for p in orientation_stack:
        #    print(p)
        if self.verbose: print("Rotating on " + str(eulOffset) + ": " + str(value) + " | (" + str(value*180/pi) + " deg)" + " results in " + str(eulOffset*value))
        return eulOffset*value, i

    def orientWithBranch(self,eul,last_branch_euler,isEndPoint):
        """
        Returns a rotation oriented with a branch
        """
        tmp_eul = eul.copy()
        if self.heuristic_details_orientations:  # Oriented according to the branch
            if isEndPoint:
                tmp_eul = last_branch_euler.copy()  # Aligned to the last branch
            else:
                tmp_eul = last_branch_euler.copy()  # Normal to the last branch
                tmp_eul.rotate(Euler((90,0,0)))
        return tmp_eul

    def orientWithGround(self,eul,last_branch_euler,isEndPoint):
        """
        Returns a rotation oriented towards the ground
        """
        tmp_eul = eul.copy()
        if self.heuristic_details_orientations: # Always oriented towards the ground
            tmp_eul = Euler((0,0,0))
        return tmp_eul

    def checkIsEndPoint(self,i,structure):
        """
        Check whether this is an end point (leaf node)

        We need to make sure there is no F after this, before the branch closes!
        Also, no branch must be opened!
        """
        #print("Checking end point for node " + structure[i] + " at " + str(i))
        tmp_i = i
        #isEndPoint = True
        while(tmp_i <  len(structure)):
            tmp_c = structure[tmp_i]
            if tmp_c == "F" or tmp_c == "[":
                #print("NO! Found another branch!")
                return False
            if tmp_c == "]":
                #print("YES! Found end of branch!")
                return True
            tmp_i += 1
        #print("YES! Found end of tree!")
        return True

    def getQuaternionBetween(self,u,v):
        """
        Given two vectors, returns the quaternion representing the rotation between them.
        From: http://lolengine.net/blog/2013/09/18/beautiful-maths-quaternion-from-vectors
        """
        #print("U: " + str(u))
        #print("V: " + str(v))
        w = u.cross(v)
        #print("CROSS: " + str(w))
        d = u.dot(v)
        #print("DOT: " + str(d))
        q = Quaternion((1.0 + d, w.x, w.y, w.z));
        #print("Q: " + str(q))
        return q.normalized()


    def getRandom(self,index):
        """ Get a random value for the current 'branch depth' """
        if index >= len(self.randoms):
            rndValue = self.rnd.uniform(-1,+1)
            self.randoms.append(rndValue)
        else:
            rndValue = self.randoms[index]    # Re-use previously created random value
        return float(rndValue)

    def extractParameter(self,structure,i,default_value):
        """ Extracts a parameter out of a piece of structure """
        if i < len(structure)-1 and structure[i+1] == '(':
            # Get the parameter value after this
            param_value_string = ''
            j=i+2
            while True:
                c2 = structure[j]
                if c2 == ')':
                    break
                else:
                    param_value_string += c2
                    j+=1
            i = j # We place the index after the parameter
            param_value = float(param_value_string)
            if self.verbose: print("Found parameter: " + str(param_value))
            return param_value, i
        else:
            return default_value, i

    def addPos(self,v,verts,radius,radii):
        """ Saves the current position of the turtle as a vertex """
        verts.append(v.copy())
        radii.append(radius)

    def __str__(self):
        s = ""
        s += "\nTurtle:"
        s += "\nAngle: " + str(self.angle)
        s += "\nStep: " + str(self.step)
        return s

if __name__ == "__main__":
    print("Test turtle")

    print("\nTEST - Creation")
    t = Turtle(verbose = True)
    print(t)

    #s = "FFFL[LLF][++F]F(2)F(2)"
    s = "!!+(39)F(2.2)!F(2)"
    print("\nTEST - Drawing system " + s)
    result = t.draw(s)
    print(result)

    print("\nEND TESTS")

    #if renderResult: self.drawMesh(context,instance_index,verts,edges,radii,leaves,bulbs,flowers,fruits,suffix)

