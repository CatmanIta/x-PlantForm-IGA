x-PlantForm-IGA
===============

This projects allows the procedural generation of plant-like meshes, either manually, automatically, or using interactive genetic algorithms.


- open_blender_xplantform.bat
Opens the .blend file that allows manual generation of plantforms

Modules are as follows:

- blender
Holds scripts and .blend files to run the rendering parts of the system.

	- imagegeneration
	Helper classes and .blend files to generate good PNG images of the results

	- operators
	A collection of Blender operators to perform different tasks

	- output
	The output folder where rendered meshes and images are placed

	- render
	Classes that use blender to render a pString to screen

	- textures
	The input folder from which textures are loaded

- grammar
Holds classes to create pL-systems

- iga
Holds classes to run an Interactive Genetic Algorithm and communicate with HTTP servers

- procedural
Holds classes that allow the procedural generation of pL-systems

- turtles
Holds classes that render a pL-string to a Turtle representation
