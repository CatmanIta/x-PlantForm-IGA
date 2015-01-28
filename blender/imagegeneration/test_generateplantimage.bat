REM Recreating pictures
REM I cannot start the generateplantimage script directly, because it will then start blender with the python of Panda (which is of the wrong version). Instead, use this!
set "classes_path=C:\Users\Michele\Documents\EclipseWorkspace\xplantform"
REM cd "%classes_path%\blender\imagegeneration\test_generateplantimage.py"
python "%classes_path%\blender\imagegeneration\test_generateplantimage.py"
pause