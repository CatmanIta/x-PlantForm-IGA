"""
    Script to test the image generation.
    @note: Call this from a .bat script!

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

import sys
classesPath = "C:\\Users\\Michele\\Documents\\EclipseWorkspace\\xplantform\\"
if not classesPath in sys.path: sys.path.append(classesPath)

from blender.imagegeneration.generateplantimage import generatePlantImages

print("Start testing Generate Plant Image")
genomes = []

genomes.append("FFF||6||||1.45981651194|0.0747723827113|3.24517983793|0|0|0|0|0|0|0")



#genomes.append("[+--F-]||F.*.F+LF||!.*.&+F[+]||!.*.&F[+]||!.*.&F[+]")

# TEST: These plants appear strange in their pictures!
#genomes.append("F+||3||F.*.[ZF]+F")                         # Was too low: fixed with enlarging the blender screen
#genomes.append("+RF--||3||!.*.F\||-.*.B-||+.*.YB/&+-+")      # Did not appear: it is underground! I'll just ignore this.
#genomes.append("-Z!||3||R.*.+K//||!.*.FX")                  # Cannot see it: the problem was that the camera had a track enabled! I removed it and now it works!

# This was invisible! (fixed now)
#genomes.append("Y(0.22,0.44)F(0.66)K(0.53)F(1.88)Z(0.1,0.38)||3||Y(x,y);*;F(0.35)Y(0.13,0.89)[F(0.86)F(y)F(1.98)F(1.63)+(45.45)]||Z(x,y);*;[-(y)]||+(x);*;[F(x)]||F(x);*;[F(x)]Z(0.94,0.97)")
#genomes.append("/(84.01)&(3.51)Z(0.65,0.09)-(16.17)B(0.14)||3||-(x);*;+(51.33)+(77.21)[-(70.68)F(1.76)F(x)]-(10.92)||/(x);*;/(x)||+(x);*;[F(x)]L(0.1)+(41.62)||Z(x,y);*;[-(y)]")


#genomes.append("&(45.02)+(24.65)F(0.38)Y(0.69,0.66)+(3.97)||6||F(x);*;\(45.73)-(x)F(0.01)||F(x);*;F(0.44)[-(x)L(0.33)]||Y(x,y);*;[F(y)]||L(x);*;[^(53.11)/(63.28)^(x)]||||5.44601489823|0.129042773597|1.84773315863|0|0|0|0|0|0|0")

#genomes.append("A(0.51)||6||A(x);*;!(0.36)F(0.0)[-(29.56)A(0.78)][+(x)A(0.55)]||F(x);*;!(x*1.95)F(x)||!(x);*;!(x)||||1.45981651194|0.0747723827113|3.24517983793|0|0|0|0|0|0|0")
generatePlantImages(genomes)

print("Finish testing Generate Plant Image")
