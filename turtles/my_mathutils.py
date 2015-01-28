"""
    Math utilities inspired by mathutils.c of blender, so I do not have to import blender every time

    @author: Michele Pirovano
    @copyright: 2013-2015
"""

from math import sin,cos,atan2,asin,sqrt,pi

class Vector:
    """
    Defines a 3D Vector.
    Inspired by mathutils.c of Blender3D.
    """

    def __init__(self,v):
        """
        @param v: initial values
        @type v: tuple of 3 floats
        """
        self.x = v[0]
        self.y = v[1]
        self.z = v[2]


    def copy(self):
        """
        @return: A new Vector that is a copy of this one.
        """
        return Vector((self.x,self.y,self.z))

    def rotateEul(self, eul):
        """
        Rotates the Vector in place.

        @param eul: Euler angles rotation to apply
        @type eul: tuple of 3 floats
        """
        rx = eul.x
        ry = eul.y
        rz = eul.z
        x = self.x
        y = self.y
        z = self.z

        x_new = x
        y_new = y * cos(rx) - z*sin(rx)
        z_new = y * sin(rx) + z*cos(rx)

        x = x_new
        y = y_new
        z = z_new

        x_new = x * cos(ry) - z * sin(ry)
        y_new = y
        z_new = x * sin(ry) + z * cos(ry)

        x = x_new
        y = y_new
        z = z_new

        x_new = x * cos(rz) + y*sin(rz)
        y_new = -x * sin(rz) + y*cos(rz)
        z_new = z

        self.x = x_new
        self.y = y_new
        self.z = z_new

    def rotateQuat(self,quat):
        """
        Rotates the Vector in place.
        From http://www.mathworks.it/it/help/aeroblks/quaternionrotation.html

        @param quat: Quaternion representing the rotation to apply
        @type quat: tuple of 4 floats
        """
        x = self.x
        y = self.y
        z = self.z

        qx = quat.x
        qy = quat.y
        qz = quat.z
        qw = quat.w

        qxsq = qx*qx
        qysq = qy*qy
        qzsq = qz*qz

        x_new = x*(1-2*qysq-2*qzsq)+y*(2*(qx*qy-qw*qz))+z*(2*(qx*qz+qw*qy))
        y_new = x*(2*(qx*qy+qw*qz))+y*(1-2*qxsq-2*qzsq)+z*(2*(qy*qz-qw*qx))
        z_new = x*(2*(qx*qz-qw*qy))+y*(2*(qy*qz+qw*qx))+z*(1-2*qxsq-2*qysq)

        self.x = x_new
        self.y = y_new
        self.z = z_new

    def cross(self, other):
        """
        Perform the cross product vector operation between this vector and another.

        @param other: The other Vector
        @type other: Vector

        @return: A new Vector representing the cross product.
        """
        x = self.y*other.z - self.z*other.y
        y = self.z*other.x - self.x*other.z
        z = self.x*other.y - self.y*other.x
        return Vector((x,y,z))

    def dot(self, other):
        """
        Perform the dot product vector operation between this vector and another.

        @param other: The other Vector
        @type other: Vector

        @return: A float representing the dot product.
        """
        return  self.x*other.x + self.y*other.y + self.z*other.z

    def __mul__(self, other):
        return Vector((self.x*other,self.y*other,self.z*other))

    def __add__(self, other):
        return Vector((self.x+other.x,self.y+other.y,self.z+other.z))

    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.z)+")"

    def __iter__(self):
        """
        Iterates over the three values of the Vector.
        """
        yield self.x
        yield self.y
        yield self.z

class Euler:
    def __init__(self,v):
        self.x = v[0]   # Heading
        self.y = v[1]   # Pitch
        self.z = v[2]   # Roll

    def copy(self):
        return Euler((self.x,self.y,self.z))

    def rotate(self,other):
        return Euler((self.x+other.x, self.y + other.y, self.z+other.z))

    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.z)+")"

    def __mul__(self, other):
        return Euler((self.x*other,self.y*other,self.z*other))

    def __add__(self, other):
        return Euler((self.x+other.x,self.y+other.y,self.z+other.z))

class Quaternion:
    def __init__(self,v):
        self.w = v[0]
        self.x = v[1]
        self.y = v[2]
        self.z = v[3]

    def normalized(self):
        mag = sqrt(self.w*self.w + self.x*self.x + self.y*self.y + self.z*self.z)
        if mag == 0: return Quaternion((0,0,0,0))
        w = self.w/mag
        x = self.x/mag
        y = self.y/mag
        z = self.z/mag
        return Quaternion((w,x,y,z))

    def to_euler(self,eul):
        """
        Transforms this quaternion into an Euler representation.

        @note: This assumes the quaternion to be normalized!
        """
        w = self.w
        x = self.x
        y = self.y
        z = self.z

        if x == 0 and y == 0 and z == 0:
            #print("Zero rotation! We left the last eul unchanged!")
            return eul

        sqw = w*w
        sqx = x*x
        sqy = y*y
        sqz = z*z

        test = x*y*z*w;

        # We need to use this test to avoid singularities. Note that it can be extended for non-normalized quaternions: http://stackoverflow.com/questions/11492299/quaternion-to-euler-angles-algorithm-how-to-convert-to-y-up-and-between-ha
        if test > 0.4999:                            # 0.4999f OR 0.5 - EPSILON
            #print("NORTH POLE SINGULARITY")
            # Singularity at north pole
            eulx = pi * 0.5
            euly = 2*atan2(x,w)
            eulz = 0
        elif test < -0.4999:                         # -0.4999 OR -0.5 + EPSILON
            #print("SOUTH POLE SINGULARITY")
            # Singularity at south pole
            eulx = -pi * 0.5
            euly = 2*atan2(x,w)
            eulz = 0
        else:
            #print("NO SINGULARITY")
            eulx = (atan2(2.0 * (y*z + x*w),(-sqx - sqy + sqz + sqw)))# * (180.0/pi))
            euly = (asin(2.0*(x*z - y*w)))# * (180.0/pi))
            eulz = (atan2(-2.0 * (x*y + z*w),(sqx - sqy - sqz + sqw)))# * (180.0/pi))

        return  Euler((eulx,euly,eulz))

    def __str__(self):
        return "("+str(self.w)+","+str(self.x)+","+str(self.y)+","+str(self.z)+")"