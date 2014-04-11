__author__ = 'whiord'

import objects.point
import pygame.draw as pd
#import pygame.color as pc
import pygame.locals as pl
import pygame.font as pf


class BaseController(object):
    def __init__(self, config, display):
        self.config = config
        self.display = display
        self.map_config = None
        self.objects = None
        self.edges = None
        self.grub_id = None

        self.circle_radius = config["circle"]["radius"]
        self.circle_color = config["circle"]["color"]
        self.grub_coef = config["circle"]["grub_coef"]
        self.line_color = config["line"]["color"]
        self.line_width = config["line"]["width"]
        self.background_color = config["background"]["color"]

    def open(self, map_config):
        self.map_config = map_config

    def dispatch(self, event):
        raise NotImplementedError()

    def update(self, fps, time):
        raise NotImplementedError()

    @staticmethod
    def choose_controller(map_config):
        if map_config["type"] == "2D":
            return "GameController2D"
        else:
            return "GameController3D"


class GameController2D(BaseController):
    def __init__(self, config, display):
        super(GameController2D, self).__init__(config, display)

    def __find_point(self, pos):
        for id, point in self.objects.items():
            if point.dist_to(*pos) < self.circle_radius * self.grub_coef:
                return id
        return None

    def open(self, map_config):
        super(GameController2D, self).open(map_config)
        self.objects = {}

        for point in map_config["objects"]:
            self.objects[point["id"]] = objects.point.Point2D(point["x"], point["y"])

        self.edges = map_config["edges"]

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
        self.display.fill(self.background_color)

        for edge in self.edges:
            p1 = self.objects[edge[0]]
            p2 = self.objects[edge[1]]
            pd.line(self.display, self.line_color, (p1.x, p1.y), (p2.x, p2.y), self.line_width)

        for point in self.objects.values():
            pd.circle(self.display, self.circle_color, (point.x, point.y), self.circle_radius)

        font = pf.Font(None, 20)
        info = font.render("fps: {}".format(fps), True, self.line_color)
        self.display.blit(info, (10,10))