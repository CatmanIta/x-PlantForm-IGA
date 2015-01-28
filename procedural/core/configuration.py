""""
    Configuration global variables for procedural generation.

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

# General
MAX_N_PRODUCTIONS = 4

MIN_TOTAL_STRING_LENGTH = 1
MAX_TOTAL_STRING_LENGTH = 24  #16 was before

MIN_GENERATED_STRING_LENGTH = 1
MAX_GENERATED_STRING_LENGTH = 1

MIN_AXIOM_LENGTH = 1
MAX_AXIOM_LENGTH = 5

MIN_DEFINE_VALUE = 0
MAX_DEFINE_VALUE = 2

# Randomization
MIN_RANDOM_ITERATIONS = 3
MAX_RANDOM_ITERATIONS = 3

MIN_RANDOM_DEFINES = 1
MAX_RANDOM_DEFINES = 4

MIN_RANDOM_PRODUCTIONS = 1
MAX_RANDOM_PRODUCTIONS = 4

# Mutation
MUTATION_STEPS_AT_ONCE = 1  # Number of mutations that are done subsequently

