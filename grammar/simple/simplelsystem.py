"""
    OLD CODE - DEPRECATED

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

def SimpleLSystem(axiom,rules,iterations):
    """
    Creates a simple 0L-system
    @param axiom: Initial string
    @param rules: Production rules (list)
    @param iterations: Number of iterations

    @return: String representing the l-system after the iterations
    """
    s = axiom
    for i in range(iterations):
        for rule in rules:
            antecedent, consequent = rule.split("->")
            s = s.replace(antecedent,consequent)
    return s


if __name__ == "__main__":
    print("Start testing SimpleLSystem")

    print ("TEST - create the system")
    result = SimpleLSystem("FLF",["F->FF"],4)
    print("Created: " + str(result))
    print ("TEST - OK")

    print("Finish testing SimpleLSystem")

