"""
    @author: Michele Pirovano
    @copyright: 2013-2015
"""
import sys
CLASSES_PATH = "C:\\Users\\Michele\\Documents\\EclipseWorkspace\\xplantform\\"
if not CLASSES_PATH in sys.path: sys.path.append(CLASSES_PATH)

from iga.miscellaneous.clear_pictures import ClearAllPictures

ClearAllPictures()