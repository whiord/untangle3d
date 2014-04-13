__author__ = 'whiord'

from math import *

COORD_SYSTEM_CARTESIAN = 0
COORD_SYSTEM_SPHERICAL = 1


class Point3D:
    def __init__(self, p1, p2, p3, cs=COORD_SYSTEM_CARTESIAN):
        self.cs = cs
        if cs == COORD_SYSTEM_SPHERICAL:
            self.alpha = p1
            self.beta = p2
            self.rho = p3
        elif cs == COORD_SYSTEM_CARTESIAN:
            self.x = p1
            self.y = p2
            self.z = p3
        else:
            raise ValueError("Unknown coordinate system")

    def __sub__(self, other):
        a = self.to_cartesian()
        b = other.to_cartesian()
        res = Point3D(a.x - b.x, a.y - b.y, a.z - b.z, COORD_SYSTEM_CARTESIAN)
        return res if self.cs == COORD_SYSTEM_CARTESIAN else res.to_spherical()

    def __add__(self, other):
        a = self.to_cartesian()
        b = other.to_cartesian()
        res = Point3D(a.x + b.x, a.y + b.y, a.z + b.z, COORD_SYSTEM_CARTESIAN)
        return res if self.cs == COORD_SYSTEM_CARTESIAN else res.to_spherical()

    def __mul__(self, other):
        a = self.to_cartesian()
        b = other.to_cartesian()
        return a.x * b.x + a.y * b.y + a.z * b.z

    def __str__(self):
        if self.cs == COORD_SYSTEM_CARTESIAN:
            return "point(x:{}, y:{}, z:{})".format(self.x, self.y, self.z)
        elif self.cs == COORD_SYSTEM_SPHERICAL:
            return "point(a:{}, b:{}, r:{})".format(self.alpha, self.beta, self.rho)

    def to_cartesian(self):
        if self.cs == COORD_SYSTEM_SPHERICAL:
            x = self.rho * cos(self.alpha) * cos(self.beta)
            y = self.rho * sin(self.alpha) * cos(self.beta)
            z = self.rho * sin(self.beta)
            return Point3D(x, y, z, COORD_SYSTEM_CARTESIAN)
        else:
            return Point3D(self.x, self.y, self.z, COORD_SYSTEM_CARTESIAN)

    def to_spherical(self):
        if self.cs == COORD_SYSTEM_CARTESIAN:
            rho = (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
            beta = asin(self.z / rho)
            alpha = atan2(self.y, self.x)
            return Point3D(alpha, beta, rho, COORD_SYSTEM_SPHERICAL)
        else:
            return Point3D(self.alpha, self.beta, self.rho, COORD_SYSTEM_SPHERICAL)