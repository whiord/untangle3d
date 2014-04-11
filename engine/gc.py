__author__ = 'whiord'

import objects.point
import readconf

import pygame.draw as pd
#import pygame.color as pc
import pygame.locals as pl
import pygame.font as pf


class BaseController(object):
    CONFIG_FILE = "engine/config.json"

    def __init__(self, display):
        self.config = readconf.open_json(BaseController.CONFIG_FILE)
        self.display = display
        self.map_config = None
        self.objects = None
        self.edges = None
        self.grub_id = None

    def open(self, map_config):
        self.map_config = map_config

    def dispatch(self, event):
        raise NotImplementedError()

    def update(self, fps, time):
        raise NotImplementedError()

    @staticmethod
    def choose_controller(type, display):
        if type == "2D":
            return GameController2D(display)
        else:
            pass
            #return "GameController3D"


class GameController2D(BaseController):
    def __init__(self, display):
        super(GameController2D, self).__init__(display)

    def __find_point(self, pos):
        for id, point in self.objects.items():
            if point.dist_to(*pos) < self.config.circle.radius * self.config.circle.grub_coef:
                return id
        return None

    def open(self, map_config):
        super(GameController2D, self).open(map_config)
        self.objects = {}

        for point in map_config.objects:
            self.objects[point.id] = objects.point.Point2D(point.x, point.y)

        self.edges = map_config.edges

        print("GC:", "objects created: ", len(self.objects))

    def dispatch(self, event):
        if event.type == pl.MOUSEBUTTONDOWN:
            if event.button == 1:
                id = self.__find_point(event.pos)
                if id is not None:
                    self.grub_id = id
        elif event.type == pl.MOUSEMOTION:
            if self.grub_id is not None:
                self.objects[self.grub_id].x = event.pos[0]
                self.objects[self.grub_id].y = event.pos[1]
        elif event.type == pl.MOUSEBUTTONUP:
            if event.button == 1:
                self.grub_id = None

    def update(self, fps, time):
        #print("GC:", "update called")
        self.display.fill(self.config.background.color)

        for edge in self.edges:
            p1 = self.objects[edge[0]]
            p2 = self.objects[edge[1]]
            pd.line(self.display, self.config.line.color, (p1.x, p1.y), (p2.x, p2.y), self.config.line.width)

        for id, point in self.objects.items():
            color = self.config.circle.color
            if id == self.grub_id:
                color = self.config.circle.active_color
            pd.circle(self.display, color, (point.x, point.y), self.config.circle.radius)

        font = pf.Font(None, 20)
        info = font.render("fps: {}".format(fps), True, self.config.line.color)
        self.display.blit(info, (10,10))