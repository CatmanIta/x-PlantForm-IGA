"""
    Uses Metaballs to render specific structures.

    Inspired by http://blender.stackexchange.com/questions/1349/scripting-metaballs-with-negative-influence/1360#1360

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import bpy

class MetaballGenerator:
    mballFamily = None

    def addMetaball(self):
        # Note that the metaballs will be  created under a metaball 'family', i.e. a parent which has the name MetaBall and no .001 or .002 after it.
        # This 'family' will determine parameters such as threshold and so on
        mballFamily = self.mballFamily
        if mballFamily is None:
            #print("CREATING NEW METABALL!")
            mballFamily = bpy.data.metaballs.new("MetaBall")
            mballFamily.resolution = 0.15  # View resolution    [0.02 - 1] (0.02 is nicer, 1 is faster)
            mballFamily.render_resolution = 0.02
            mballFamily.threshold = 1#0.02

            scene = bpy.context.scene
            obj = bpy.data.objects.new("MetaBallObject", mballFamily)
            scene.objects.link(obj)
            self.mballCurrentObject = obj

        # We add a new metaball to the family
        mball = mballFamily.elements.new()
        #mball.co = (0,0,0)         # Optional position
        #mball.radius = 0.5         # Optional radius

        return mball

if __name__ == "__main__":
    import random

    # Create a set of metaballs
    mballGen = MetaballGenerator()

    for i in range(20):
        coordinate = tuple(random.uniform(-4,4) for i in range(3))

        element = mballGen.addMetaball()
        element.co = coordinate
        element.radius = 5.0