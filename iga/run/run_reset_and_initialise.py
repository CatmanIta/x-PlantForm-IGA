"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
import sys
CLASSES_PATH = "C:\\Users\\Michele\\Documents\\EclipseWorkspace\\xplantform\\"
if not CLASSES_PATH in sys.path: sys.path.append(CLASSES_PATH)

from iga.reset import Reset
from iga.initialise import Initialise

Reset()
Initialise()