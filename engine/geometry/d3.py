__author__ = 'whiord'

from math import *
from rotators import *
import d2

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
        if isinstance(other, Point3D):
            b = other.to_cartesian()
            return a.x * b.x + a.y * b.y + a.z * b.z
        elif isinstance(other, float) or isinstance(other, int):
            return Point3D(a.x*other, a.y*other, a.z*other)

    def __str__(self):
        if self.cs == COORD_SYSTEM_CARTESIAN:
            return "point(x:{0:0.2f}, y:{1:0.2f}, z:{2:0.2f})".format(self.x, self.y, self.z)
        elif self.cs == COORD_SYSTEM_SPHERICAL:
            return "point(a:{0:0.2f}, b:{1:0.2f}, r:{2:0.2f})".format(self.alpha, self.beta, self.rho)

    def length(self):
        if self.cs == COORD_SYSTEM_SPHERICAL:
            return self.rho
        else:
            return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def normalized(self):
        buf = self.to_spherical()
        buf.rho = 1.0
        return buf if self.cs == COORD_SYSTEM_SPHERICAL else buf.to_cartesian()

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


class DeepPoint(d2.Circle):
    def __init__(self, x, y, depth=0):
        d2.Circle.__init__(self, x, y, 1)
        self.depth = depth


class Scene3D:
    def __init__(self):
        self.objects = {}
        self.links = set()
        self.center = Point3D(0, 0, 0)

    def move_center(self, vector):
        self.center += vector
        for id, obj in self.objects.items():
            if obj.cs == COORD_SYSTEM_CARTESIAN:
                self.objects[id] = obj + vector

    def add_object(self, id, object):
        if object.cs == COORD_SYSTEM_CARTESIAN:
            self.objects[id] = object + self.center
        else:
            self.objects[id] = object

    def add_link(self, id1, id2):
        if id1 not in self.objects or id2 not in self.objects:
            return

        self.links.add((id1, id2))

    def rotate(self, projection_vector, dx, dy, rotator=BaseRotator()):
        return rotator.rotate(self, projection_vector, dx, dy)

    def project(self, screen_plane, view_distance):
        """ project(screen_plane, view_distance) -> Scene2D
            Projects 3D scene to screen plane (as orthogonal vector) according
             to view distance. Screen plane vector points to center of new coordinate
             system, and view point is behind it for distance.
            Sets in result DeepPoint instances with depth equal to distance
             from objects to view point.
        """
        scene = d2.Scene2D()
        scene.links = self.links

        norm_prj = screen_plane.normalized()
        view_point = norm_prj * view_distance + screen_plane
        #print "Screen:", screen_plane
        #print "View point:", view_point
        prj_len = screen_plane.length()
        #print "Projection length:", prj_len

        sph_prj = norm_prj.to_spherical()
        #naY.beta = -naY.beta
        naY = Point3D(sph_prj.alpha, sph_prj.beta - pi/2.0, 1, COORD_SYSTEM_SPHERICAL)

        naX = Point3D(sph_prj.alpha - pi/2.0, sph_prj.beta, 1, COORD_SYSTEM_SPHERICAL)
        #naX.alpha += naY.alpha
        #naX.beta += naY.beta

        #naY.alpha += pi
        #naY.beta = pi/2.0 - naY.beta
        #naY.beta *= -1

        #print "naX:", naX.to_cartesian()
        #print "naY:", naY.to_cartesian()

        for id, object in self.objects.items():
            #print "#{}".format(id)
            obj_prj_len = object * norm_prj
            #obj_prj = norm_prj * obj_prj_len
            len_ortho_to_plane = prj_len - obj_prj_len
            to_view = view_point - object
            norm_to_view = to_view.normalized()
            #print "Norm to view:", norm_to_view
            #print "View:", to_view, ", dist to view:", to_view.length()
            len_to_plane = to_view.length() * (1.0 - view_distance/(view_distance + len_ortho_to_plane))
            #print "Dist to plane:{0:0.2f}".format(len_to_plane)
            obj_on_plane = object + norm_to_view * len_to_plane
            #print "Object on plane:", obj_on_plane
            new_coord_object = obj_on_plane - screen_plane
            #print "New coord:", new_coord_object
            nx = new_coord_object * naX
            ny = new_coord_object * naY
            #print "nx: {0:0.2f}".format(nx)
            #print "ny: {0:0.2f}".format(ny)

            scene.add_object(id, DeepPoint(nx, ny, len_to_plane))

        return scene


import unittest


class Scene3DTests(unittest.TestCase):
    EPSILON = 0.001

    def test_projection_1(self):
        screen_vector = Point3D(0, 2, 0)
        view_distance = 5

        s3d = Scene3D()
        s3d.add_object(0, Point3D(0, 0, 0))
        s3d.add_object(1, Point3D(1, 0, 0))
        s3d.add_object(2, Point3D(0, 1, 0))
        s3d.add_object(3, Point3D(0, 0, 1))
        s3d.add_object(4, Point3D(1, 1, 0))
        s3d.add_object(5, Point3D(0, 1, 1))
        s3d.add_object(6, Point3D(1, 0, 1))
        s3d.add_object(7, Point3D(1, 1, 1))


        s2d = s3d.project(screen_vector, view_distance)
        self.assertEquals(s2d.objects.__len__(), s3d.objects.__len__())
        #print "#0", s2d.objects[0]

        self.assertLessEqual(abs(s2d.objects[0].x - 0.0), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[0].y - 0.0), self.EPSILON)

        self.assertLessEqual(abs(s2d.objects[1].x - 5/7.0), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[1].y - 0.0), self.EPSILON)

        self.assertLessEqual(abs(s2d.objects[2].x - 0.0), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[2].y - 0.0), self.EPSILON)

        self.assertLessEqual(abs(s2d.objects[3].x - 0.0), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[3].y + 5/7.0), self.EPSILON)

        self.assertLessEqual(abs(s2d.objects[4].x - 5/6.0), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[4].y - 0.0), self.EPSILON)

        self.assertLessEqual(abs(s2d.objects[5].x - 0.0), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[5].y + 5/6.0), self.EPSILON)

        self.assertLessEqual(abs(s2d.objects[6].x - 5/7.0), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[6].y + 5/7.0), self.EPSILON)

        self.assertLessEqual(abs(s2d.objects[7].x - 5/6.0), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[7].y + 5/6.0), self.EPSILON)

    def test_projection_2(self):
        sq2 = 2 ** 0.5
        screen_vector = Point3D(2, 2, 0)
        view_distance = sq2

        s3d = Scene3D()
        s3d.add_object(0, Point3D(0, 0, 0))
        s3d.add_object(1, Point3D(3, 0, 0))
        s3d.add_object(2, Point3D(0, 3, 0))


        s2d = s3d.project(screen_vector, view_distance)
        self.assertEquals(s2d.objects.__len__(), s3d.objects.__len__())
        #print "#0", s2d.objects[0]

        self.assertLessEqual(abs(s2d.objects[0].x - 0.0), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[0].y - 0.0), self.EPSILON)

        self.assertLessEqual(abs(s2d.objects[1].x - sq2), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[1].y - 0.0), self.EPSILON)

        self.assertLessEqual(abs(s2d.objects[2].x + sq2), self.EPSILON)
        self.assertLessEqual(abs(s2d.objects[2].y - 0.0), self.EPSILON)
