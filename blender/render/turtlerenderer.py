"""
    Renders a Turtle representation in Blender.

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import bpy
from mathutils import Vector, Euler, Matrix
import random

import blender.render.metaballs
import procedural.miscellaneous.detailshandler

import imp
imp.reload(blender.render.metaballs)
imp.reload(procedural.miscellaneous.detailshandler)

from blender.render.metaballs import MetaballGenerator
from procedural.miscellaneous.detailshandler import DetailsHandler

MAX_DRAWABLE_VERTS = 5000
MAX_SKINNABLE_VERTS = 1000

class TurtleRenderer:
    """
    Given a Turtle representation, renders the result as a 3D mesh.
    """

    def __init__(self, seed = None, verbose = False):
        self.verbose = verbose

        self.showSkin = False
        self.fastSkin = True
        self.simplify = False
        self.limitDrawing = True    # If True, the skinning and drawing will be limited based on the number of vertices, to avoid hangs.

        self.showLeaves =   False

        self.showCanopy =   False
        self.metaBallRadius = 1.5

        self.leaf_detail_index = 0
        self.bulb_detail_index = 0
        self.flower_detail_index = 0
        self.fruit_detail_index = 0

        self.leaf_material_index = 0
        self.trunk_material_index = 0

        self.details_scale = 1
        self.randomize_details = False                # Will randomly choose from the list of details

        self.rnd = random.Random()
        if seed is not None: self.rnd.seed(seed)

        self.nInstances = 1

    def loadParameters(self,turtleParameters):
        self.details_scale = turtleParameters.details_scale
        self.showCanopy = turtleParameters.use_canopy
        self.trunk_material_index = turtleParameters.trunk_material_choice
        self.leaf_material_index = turtleParameters.leaf_material_choice
        self.leaf_detail_index = turtleParameters.leaf_choice
        self.bulb_detail_index = turtleParameters.bulb_choice
        self.flower_detail_index = turtleParameters.flower_choice
        self.fruit_detail_index = turtleParameters.fruit_choice

    def drawMesh(self, context, turtleResult, origin_offset = (0,0,0), suffix = "", randomSeed = None, multipleInstances = False,
                 overridenContext = None):
        if overridenContext is None:    scene = context.scene
        else:                           scene = overridenContext['scene']

        verts = turtleResult.verts
        edges = turtleResult.edges
        radii = turtleResult.radii
        leaves = turtleResult.leaves
        bulbs = turtleResult.bulbs
        flowers = turtleResult.flowers
        fruits = turtleResult.fruits
        instance_index = turtleResult.instance_index
        idd = turtleResult.idd
        if randomSeed: self.rnd.seed(randomSeed+instance_index)

        if len(verts) == 0:
            if overridenContext is None: context.area.header_text_set("WARNING: Mesh drawing aborted due no vertices supplied.")
            else: context['area'].header_text_set("WARNING: Mesh drawing aborted due no vertices supplied.")
            print("WARNING: Mesh drawing aborted due no vertices supplied.")
            return

        if self.limitDrawing and len(verts) > MAX_DRAWABLE_VERTS:
                if overridenContext is None: context.area.header_text_set("WARNING: Mesh drawing aborted due to huge number of vertices: " + str(len(verts)))
                else: context['area'].header_text_set("WARNING: Mesh drawing aborted due to huge number of vertices: " + str(len(verts)))
                print("WARNING: Mesh drawing aborted due to huge number of vertices: " + str(len(verts)))
                return

        if suffix == "":     name = str(idd) + "_" + str(instance_index)
        else:                name = suffix

        if multipleInstances: origin_offset = (origin_offset[0]-((int)(instance_index/5))*1+self.rnd.uniform(-0.5,0.5)*1.0,
                                               origin_offset[1]+(instance_index%5)*1+self.rnd.uniform(-0.5,0.5)*1.0,
                                               origin_offset[2])

        me = bpy.data.meshes.new('PlantFormMesh' + name)
        ob = bpy.data.objects.new("PlantForm" + name, me)
        me.from_pydata(verts, edges, [])
        me.update()
        ob.location = scene.cursor_location + Vector(origin_offset)
        scene.objects.link(ob)

        # Add details
        #print("Turtle renderer: Show detaiils")
        if self.showLeaves:
            if self.randomize_details: leaf_name = DetailsHandler.LEAF_NAMES[random.randint(0,len(DetailsHandler.LEAF_NAMES)-1)]
            else: leaf_name = DetailsHandler.LEAF_NAMES[self.leaf_detail_index]
            self.addDetails("leaf",leaves,leaf_name,self.details_scale,ob)

            if self.randomize_details: bulb_name = DetailsHandler.BULB_NAMES[random.randint(0,len(DetailsHandler.BULB_NAMES)-1)]
            else: bulb_name =  DetailsHandler.BULB_NAMES[self.bulb_detail_index]
            self.addDetails("bulb",bulbs,bulb_name,self.details_scale,ob)

            if self.randomize_details: flower_name = DetailsHandler.FLOWER_NAMES[random.randint(0,len(DetailsHandler.FLOWER_NAMES)-1)]
            else: flower_name = DetailsHandler.FLOWER_NAMES[self.flower_detail_index]
            self.addDetails("flower",flowers,flower_name,self.details_scale,ob)

            if self.randomize_details: fruit_name = DetailsHandler.FRUIT_NAMES[random.randint(0,len(DetailsHandler.FRUIT_NAMES)-1)]
            else: fruit_name =  DetailsHandler.FRUIT_NAMES[self.fruit_detail_index]
            self.addDetails("fruit",fruits,fruit_name,self.details_scale,ob)

        # Metaballs around leaves to simulate canopy
        #print("Turtle renderer: Show canopy")
        if self.showCanopy:
            if len(leaves) > 0:
                mballGenerator = MetaballGenerator()
                for leafQuad in leaves:
                    pos = self.toBlenderVector(leafQuad.pos)
                    mball = mballGenerator.addMetaball()
                    mball.co = pos
                    mball.radius = self.metaBallRadius
                    mballGenerator.mballCurrentObject.parent = ob   # The current mball element's object is in this variable

                scene.objects.active = mballGenerator.mballCurrentObject     # Select the object as active
                scene.objects.active.select = True  # Must force selection
                bpy.ops.object.convert(target='MESH', keep_original=False)

                if len(bpy.context.object.data.vertices) > 0:
                    # Set the foliage material
                    foliage_material_name = ""
                    if foliage_material_name != "":
                        mat = bpy.data.materials[foliage_material_name]
                        scene.objects.active.data.materials.append(mat)

                    # We also unwrap the resulting mesh for texture mapping
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.faces_shade_flat() # Flat shaded
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.unwrap()
                    bpy.ops.object.mode_set(mode='OBJECT')

        if self.showSkin:
            if self.limitDrawing and len(verts) > MAX_SKINNABLE_VERTS:
                if overridenContext is None: context.area.header_text_set("WARNING: Mesh skinning blocked due to large number of vertices: " + str(len(verts)))
                else: context['area'].header_text_set("WARNING: Mesh skinning blocked due to large number of vertices: " + str(len(verts)))
                print("WARNING: Mesh skinning blocked due to large number of vertices: " + str(len(verts)))
                return

            else:

                if self.verbose:  print("Turtle renderer: Applying skin modifier")
                current_modifier_index = 0

                # Apply a skin modifier
                # Note that this will create A LOT of vertices (simplification will help later)
                scene.objects.active = ob     # Select the object as active
                bpy.ops.object.modifier_add(type='SKIN')
                scene.objects.active.modifiers[current_modifier_index].use_smooth_shade=True
                current_modifier_index+=1

                verts = scene.objects.active.data.vertices
                skinverts = scene.objects.active.data.skin_vertices[0].data

                # Set the radius of the branches
                if self.verbose: print("Turtle renderer: Setting radius")
                for i,v in enumerate(skinverts):
                    r = radii[i]

                    """
                    height = verts[i].co[2]
                    if height > 0: r = 1.0/height
                    else: r = 1.0
                    if (r < 0.1): r = 0.1
                    if (r > 1.0): r = 1.0
                    #print(r)
                    """

                    v.radius = [r* 0.01, r* 0.01]  # r = 1 -> small radius

                if not self.fastSkin:
                    if self.verbose: print("Turtle renderer: Making it nicer")
                    # Additional modifications to make the mesh nicer

                    # Add a SubSurf modifier to obtain a smoother mesh
                    bpy.ops.object.modifier_add(type='SUBSURF')
                    scene.objects.active.modifiers[current_modifier_index].levels = 1
                    current_modifier_index+=1

                    # Edge Split makes for a more cartoony appearance
                    bpy.ops.object.modifier_add(type='EDGE_SPLIT')
                    current_modifier_index+=1
                    #bpy.ops.object.modifier_apply(modifier="EdgeSplit"); current_modifier_index-=1

                # Simplification
                #if not self.fastSkin:
                if self.simplify:
                    if self.verbose: print("Turtle renderer: Simplification")
                    bpy.ops.object.modifier_add(type='DECIMATE')
                    scene.objects.active.modifiers[current_modifier_index].ratio=0.1
                    scene.objects.active.modifiers[current_modifier_index].decimate_type = 'DISSOLVE'  # We use planar decimation, more cartoonish
                    scene.objects.active.modifiers[current_modifier_index].angle_limit = 5.0/180.0*3.14159 # 5 degrees is enough
                    current_modifier_index+=1
                    #bpy.ops.object.modifier_apply(modifier="Decimate"); current_modifier_index-=1

                # We will apply modifier to obtain the final mesh.
                self.applyModifiers = True
                if self.applyModifiers:
                    if self.verbose: print("Turtle renderer: Apply modifiers")

                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.modifier_apply(modifier="Skin")
                    if not self.fastSkin: bpy.ops.object.modifier_apply(modifier="Subsurf")
                    if not self.fastSkin: bpy.ops.object.modifier_apply(modifier="EdgeSplit")
                    if self.simplify: bpy.ops.object.modifier_apply(modifier="Decimate")

                    if self.simplify:
                        # We can also simplify further by removing doubles
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all()
                        bpy.ops.mesh.remove_doubles() # We use the default threshold (0.0001). We can put here: threshold=0.01 if we prefer.
                        bpy.ops.mesh.normals_make_consistent(inside=False)
                        bpy.ops.object.mode_set(mode='OBJECT')


                if self.verbose: print("Turtle renderer: Trunk material")
                # Set the trunk material
                trunk_material_name = DetailsHandler.nameOfMaterial(self.trunk_material_index)
                mat = bpy.data.materials[trunk_material_name]
                scene.objects.active.data.materials.append(mat)

                scene.objects.active = scene.objects.active #mballGenerator.mballCurrentObject     # Select the object as active
                scene.objects.active.select = True  # Must force selection

                """
                if self.applyModifiers:
                    # We also unwrap the resulting mesh for texture mapping
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.faces_shade_flat() # Flat shaded
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.unwrap()
                    bpy.ops.object.mode_set(mode='OBJECT')
                """


    def addDetails(self,type_name,details_list,mesh_name,mesh_scale,parent):
        context = bpy.context

        qv = ((0.5,0,0),(0.5,1,0),(-0.5,1,0),(-0.5,0,0))
        if mesh_name is "" or (not mesh_name in bpy.data.objects):
            q = bpy.data.meshes.new('PlantForm-'+type_name)
            q.from_pydata(qv, [], [(0,1,2,3)])
            q.update()
            q.uv_textures.new()
        else:
            q = bpy.data.objects[mesh_name].data # .data will get the mesh linked to the object

        for tmpQuad in details_list:
            obj,base = self.add_obj(q, context)
            eul = self.toBlenderEuler(tmpQuad.eul)
            pos = self.toBlenderVector(tmpQuad.pos)
            r = eul.to_matrix()
            r.resize_4x4()
            obj.matrix_world = Matrix.Translation(pos)*r
            obj.parent = parent
            obj.scale = (mesh_scale,mesh_scale,mesh_scale)

    @staticmethod
    def add_obj(obdata, context):
        scene = context.scene
        obj_new = bpy.data.objects.new(obdata.name, obdata)
        base = scene.objects.link(obj_new)
        return obj_new,base

    def toBlenderVector(self, myPos):
        return Vector((myPos.x,myPos.y,myPos.z))

    def toBlenderEuler(self, myEul):
        return Euler((myEul.x,myEul.y,myEul.z))

