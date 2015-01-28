"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

class DetailsHandler:
    """
    Handles details (leaves, flowers, etc.)
    """

    LEAF_NAMES = ["Leaf_Texture"] # ["Leaf_Small","Leaf_Fern","Leaf_Round","Leaf_Jagged","Leaf_Heart","Leaf_Base","Leaf_Palm","Leaf_Texture"]
    BULB_NAMES = ["Leaf_Texture"] # ["Leaf_Fern","Leaf_Round","Leaf_Jagged","Leaf_Heart","Leaf_Base"]
    FLOWER_NAMES = ["Flower_Ball","Flower_Pretty","Flower_Tulip","Flower_Gerbera"]
    FRUIT_NAMES = ["Fruit_Apple","Fruit_Lemon","Fruit_Banana"]
    MATERIAL_NAMES = ["Material.Leaf","Material.Trunk"]


    @staticmethod
    def indexOfMaterial(name):
        for i in range(len(DetailsHandler.MATERIAL_NAMES)):
            if name == DetailsHandler.MATERIAL_NAMES[i]: return i
        print("WARNING: no material of name " + name + " found! Using the first one available.")
        return 0

    @staticmethod
    def indexOfLeafModel(name):
        for i in range(len(DetailsHandler.LEAF_NAMES)):
            if name == DetailsHandler.LEAF_NAMES[i]: return i
        print("WARNING: no leaf of name " + name + " found! Using the first one available.")
        return 0

    @staticmethod
    def indexOfBulbModel(name):
        for i in range(len(DetailsHandler.BULB_NAMES)):
            if name == DetailsHandler.BULB_NAMES[i]: return i
        print("WARNING: no bulb of name " + name + " found! Using the first one available.")
        return 0

    @staticmethod
    def indexOfFlowerModel(name):
        for i in range(len(DetailsHandler.FLOWER_NAMES)):
            if name == DetailsHandler.FLOWER_NAMES[i]: return i
        print("WARNING: no flower of name " + name + " found! Using the first one available.")
        return 0

    @staticmethod
    def indexOfFruitModel(name):
        for i in range(len(DetailsHandler.FRUIT_NAMES)):
            if name == DetailsHandler.FRUIT_NAMES[i]: return i
        print("WARNING: no fruit of name " + name + " found! Using the first one available.")
        return 0

    @staticmethod
    def nameOfMaterial(i):
        return DetailsHandler.MATERIAL_NAMES[i]

    @staticmethod
    def nameOfLeafModel(i):
        return DetailsHandler.LEAF_NAMES[i]

    @staticmethod
    def nameOfBulbModel(i):
        return DetailsHandler.BULB_NAMES[i]

    @staticmethod
    def nameOfFlowerModel(i):
        return DetailsHandler.FLOWER_NAMES[i]

    @staticmethod
    def nameOfFruitModel(i):
        return DetailsHandler.FRUIT_NAMES[i]


