"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""

class Mutation():
    """
    Defines a single L-system mutation.
    We define a mutation as an incremental change in the L-system structure.
    """

    def __init__(self, callback, description ="", weight=1):
        self.callback = callback    # This performs the actual mutation
        self.description = description
        self.weight = weight        # Must be [1,100]. The higher, the more likely this will appear

    def execute(self):
        self.callback()
