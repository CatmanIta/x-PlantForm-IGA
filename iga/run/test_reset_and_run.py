"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
import sys
CLASSES_PATH = "C:\\Users\\Michele\\Documents\\EclipseWorkspace\\xplantform\\"
if not CLASSES_PATH in sys.path: sys.path.append(CLASSES_PATH)

from iga.reset import Reset
from iga.initialise import Initialise
from iga.steadystate import SteadyState

steady_state_seconds_update_period = 5

print("RESETTING")
Reset()
print("INITIALISING")
Initialise(verbose=True)
print("STEADY STATE")
SteadyState(steady_state_seconds_update_period)