REM Testing IGA
REM Note: I cannot start the scripts directly from Eclipse, because it will then start blender with the python of Panda (which is of the wrong version). Instead, use this!
set "classes_path=C:\Users\Michele\Documents\EclipseWorkspace\xplantform"
cd "%classes_path%\iga"
python "%classes_path%\iga\run\test_reset_and_run.py"
pause