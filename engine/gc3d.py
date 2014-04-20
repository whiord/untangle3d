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
        self.scene3d = None
        self.moving = False
        self.screen_vector = Point3D(0, 5, 0)
        self.view_distance = 5.0
        self.beta = 0

    def _project(self):
        self.scene = self.scene3d.project(self.screen_vector, self.view_distance)

    def _move_system(self, vector):
        self.scene.move_center(vector)

    def _resize(self, size):
        self.scene_rect = pygame.Rect((0, 0), size)
        self.display = pdis.set_mode(size, pygame.RESIZABLE)

    def open(self, map_config):
        self.map_config = map_config
        self.scene3d = Scene3D()
        if map_config.system == "spherical":
            for point in map_config.objects:
                if map_config.unit == "degree":
                    point.alpha = gutils.deg_to_rad(point.alpha)
                    point.beta = gutils.deg_to_rad(point.beta)

                self.scene3d.add_object(point.id, Point3D(point.alpha, point.beta,
                                      point.rho * map_config.scale, COORD_SYSTEM_SPHERICAL))
                print(self.scene3d.objects[point.id])

        elif map_config.system == "cartesian":
            for point in map_config.objects:
                self.scene3d.add_object(point.id, Point3D(point.x * map_config.scale,
                                      point.y * map_config.scale,
                                      point.z * map_config.scale, COORD_SYSTEM_CARTESIAN).to_spherical())

                print(self.scene3d.objects[point.id])

        self.scene3d.links = map_config.edges
        self._project()
        GameController2D._move_system(self)
        self._adjust()
        print("GC:", "objects created: ", len(self.scene3d.objects))

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

    def _move(self, id, dx, dy):
        cart = self.scene3d.objects[id].to_cartesian()
        cart.x -= dx
        cart.z += dy
        self.scene3d.objects[id] = cart.to_spherical()

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
                dx, dy = event.rel
                self._move(self.grub_id, dx, dy)
                old_center = self.scene.center
                self._project()
                self._move_system(old_center)
            elif event.buttons != (0, 0, 0):
                dx, dy = event.rel
                if event.buttons[0] == 1:
                    self.screen_vector = self.scene3d.rotate(self.screen_vector, dx, dy,
                                                             rotator=AxisRotator())
                if event.buttons[2] == 1:
                    self.screen_vector = self.scene3d.rotate(self.screen_vector, dx, dy,
                                                             rotator=MeridianRotator())

                print("Screen vector", str(self.screen_vector))
                old_center = self.scene.center
                self._project()
                self._move_system(old_center)
        elif event.type == pl.MOUSEBUTTONUP:
            if event.button == 1:
                self.grub_id = None
                self.moving = False
        elif event.type == pl.VIDEORESIZE:
            old_size = self.display.get_size()
            old_center = self.scene.center
            size = event.size
            scale_x = size[0]/float(old_size[0])
            scale_y = size[1]/float(old_size[1])
            new_center = gd2.Point2D(old_center.x * scale_x, old_center.y * scale_y)
            self._resize(event.size)
            self._project()

            self._move_system(new_center)

    def update(self, fps, time):
        self.display.fill(self.config.background.color)
        self.info_y = 10

        GameController2D._draw(self)

        self._render_info("fps: {}".format(fps))
        pdis.update()
