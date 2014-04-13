__author__ = 'whiord'

from gc2d import GameController2D
from geometry.d3 import *
import geometry.d2 as gd2
import geometry.utils as gutils

import pygame
import pygame.display as pdis
import pygame.locals as pl
import pygame.draw as pd

class GameController3D(GameController2D):
    TYPE_SIGNATURE = "3D"

    def __init__(self):
        GameController2D.__init__(self)
        self.objects3d = None
        self.moving = False
        self.center = 0
        self.beta = 0

    def _project(self):
        self.objects = {}
        maxy = max([point.to_cartesian().y for point in self.objects3d.values()])

        for id, point in self.objects3d.items():
            cart = point.to_cartesian()
            #print "PROJECT:", cart.x, cart.y, cart.z
            #c2 = cart.to_spherical().to_cartesian()
            #print "2: ", c2.x, c2.y, c2.z
            self.objects[id] = gd2.Circle(cart.x, -cart.z,
                                          max(self.config.circle.radius *
                                              self.map_config.scale/(maxy-cart.y+self.map_config.scale),
                                          self.config.circle.min_radius))

    def _move_system(self):
        max_rho = max([point.rho for point in self.objects3d.values()])
        trans = max_rho + self.config.borders
        for point in self.objects.values():
            point.x += trans
            point.y += trans
        self.center = int(round(trans))

    def _adjust(self):
        maxx = int(round(max([point.x for point in self.objects.values()])))
        maxy = int(round(max([point.y for point in self.objects.values()])))
        self.display = pdis.set_mode((maxx + self.config.borders, maxy + self.config.borders), pygame.RESIZABLE)

    def _resize(self, size):
        old_size = self.display.get_size()
        scale_x = float(size[0])/float(old_size[0])
        scale_y = float(size[1])/float(old_size[1])
        for id, point in self.objects3d.items():
            cart = point.to_cartesian()
            cart.x *= scale_x
            cart.y *= scale_y
            self.objects3d[id] = cart.to_spherical()
        self.display = pdis.set_mode(size, pygame.RESIZABLE)

    def open(self, map_config):
        self.map_config = map_config
        self.objects = None
        self.objects3d = {}

        if map_config.system == "spherical":
            for point in map_config.objects:
                if map_config.unit == "degree":
                    point.alpha = gutils.deg_to_rad(point.alpha)
                    point.beta = gutils.deg_to_rad(point.beta)

                self.objects3d[point.id] = Point3D(point.alpha,
                                                   point.beta,
                                                   point.rho * map_config.scale, COORD_SYSTEM_SPHERICAL)
                print(self.objects3d[point.id])
        elif map_config.system == "cartesian":
            for point in map_config.objects:
                self.objects3d[point.id] = Point3D(point.x * map_config.scale,
                                                   point.y * map_config.scale,
                                                   point.z * map_config.scale, COORD_SYSTEM_CARTESIAN).to_spherical()
                print(self.objects3d[point.id])

        self.edges = map_config.edges
        self._project()
        self._move_system()
        self._adjust()
        print("GC:", "objects created: ", len(self.objects))

    def _rotate(self, dx, dy):
        rx = gutils.deg_to_rad(dx)
        ry = gutils.deg_to_rad(dy)
        if self.beta + ry > pi/2.0:
            ry = pi/2.0 - self.beta
            self.beta = pi/2.0
        elif self.beta + ry < -pi/2.0:
            ry = -pi/2.0 - self.beta
            self.beta = -pi/2.0
        else:
            self.beta += ry

        for point in self.objects3d.values():
            point.beta += ry
            point.alpha += rx


    def _move(self, dx, dy):
        cart = self.objects3d[self.grub_id].to_cartesian()
        cart.x += dx
        cart.z -= dy
        self.objects3d[self.grub_id] = cart.to_spherical()

    def dispatch(self, event):
        if event.type == pl.MOUSEBUTTONDOWN:
            if event.button == 1:
                id = self._find_point(event.pos)
                if id is not None:
                    self.grub_id = id
                else:
                    self.moving = True
        elif event.type == pl.MOUSEMOTION:
            if self.grub_id is not None:
                dx = event.pos[0] - self.objects[self.grub_id].x
                dy = event.pos[1] - self.objects[self.grub_id].y
                self.objects[self.grub_id].x = event.pos[0]
                self.objects[self.grub_id].y = event.pos[1]
                self._move(dx, dy)
            elif self.moving:
                self._rotate(*event.rel)
                self._project()
                self._move_system()
        elif event.type == pl.MOUSEBUTTONUP:
            if event.button == 1:
                self.grub_id = None
                self.moving = False
        elif event.type == pl.VIDEORESIZE:
            self._resize(event.size)
            self._project()
            self._move_system()

    def update(self, fps, time):
        self.display.fill(self.config.background.color)
        self.info_y = 10

        pd.circle(self.display, self.config.central_point.color, (self.center, self.center),
                  self.config.central_point.radius, self.config.central_point.width)

        GameController2D._draw(self)

        self._render_info("fps: {}".format(fps))
        pdis.update()
