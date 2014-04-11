__author__ = 'whiord'

import geometry.d2
import readconf

import pygame
import pygame.display as pdis
import pygame.draw as pd
#import pygame.color as pc
import pygame.locals as pl
import pygame.font as pf


class BaseController(object):
    CONFIG_FILE = "engine/config.json"

    def __init__(self):
        self.config = readconf.open_json(BaseController.CONFIG_FILE)
        self.display = None
        self.map_config = None
        self.objects = None
        self.edges = None
        self.grub_id = None
        self.info_y = None

    def open(self, map_config):
        self.map_config = map_config

    def dispatch(self, event):
        raise NotImplementedError()

    def update(self, fps, time):
        raise NotImplementedError()

    @staticmethod
    def choose_controller(type):
        if type == "2D":
            return GameController2D()
        else:
            pass
            #return "GameController3D"


class GameController2D(BaseController):
    def __init__(self):
        super(GameController2D, self).__init__()

    def __find_point(self, pos):
        for id, point in self.objects.items():
            if point.dist_to(*pos) < self.config.circle.radius * self.config.circle.grub_coef:
                return id
        return None

    def __adjust(self):
        minx = maxx = self.objects.values()[0].x
        miny = maxy = self.objects.values()[0].y

        for point in self.objects.values():
            minx = min(minx, point.x)
            miny = min(miny, point.y)
            maxx = max(maxx, point.x)
            maxy = max(maxy, point.y)

        dx = self.config.borders - minx
        dy = self.config.borders - miny
        maxx += dx
        maxy += dy
        for point in self.objects.values():
            point.x += dx
            point.y += dy

        self.display = pdis.set_mode((maxx + self.config.borders, maxx + self.config.borders), pygame.RESIZABLE)

    def __resize(self, size):
        old_size = self.display.get_size()
        scale_x = float(size[0])/float(old_size[0])
        scale_y = float(size[1])/float(old_size[1])
        print("Old:", old_size)
        print("New:", size)
        print("Sacle:", scale_x, scale_y)
        for point in self.objects.values():
            point.x *= scale_x
            point.y *= scale_y
        self.display = pdis.set_mode(size, pygame.RESIZABLE)

    def open(self, map_config):
        super(GameController2D, self).open(map_config)
        self.objects = {}

        for point in map_config.objects:
            self.objects[point.id] = geometry.d2.Point2D(point.x, point.y)

        self.edges = map_config.edges
        self.__adjust()
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
        elif event.type == pl.VIDEORESIZE:
            self.__resize(event.size)

    def update(self, fps, time):
        #print("GC:", "update called")
        self.display.fill(self.config.background.color)

        intersected = set()
        objs = self.objects
        for e1 in self.edges:
            for e2 in self.edges:
                if e1 != e2 and e1 not in intersected:
                    s1 = geometry.d2.Segment(objs[e1[0]], objs[e1[1]])
                    s2 = geometry.d2.Segment(objs[e2[0]], objs[e2[1]])
                    if geometry.d2.intersect_seg(s1, s2, self.config.accuracy):
                        intersected.add(e1)
                        intersected.add(e2)

        for edge in self.edges:
            p1 = self.objects[edge[0]]
            p2 = self.objects[edge[1]]

            color = self.config.line.color
            if edge in intersected:
                color = self.config.line.bad_color
            if self.grub_id is not None:
                if edge[0] == self.grub_id or edge[1] == self.grub_id:
                    color = self.config.line.active_color

            pd.line(self.display, color, (p1.x, p1.y), (p2.x, p2.y), self.config.line.width)

        for id, point in self.objects.items():
            color = self.config.circle.color
            if id == self.grub_id:
                color = self.config.circle.active_color
            pd.circle(self.display, color, (int(round(point.x)), int(round(point.y))), self.config.circle.radius)

        self.info_y = 10
        self.__render_info("fps: {}".format(fps))
        self.__render_info("tangled: {}/{}".format(len(intersected), len(self.edges)))

        pdis.update()

    def __render_info(self, text):
        font = pf.Font(None, 20)
        info = font.render(text ,True, self.config.line.color)
        self.display.blit(info, (10, self.info_y))
        self.info_y += info.get_size()[1] + 5
