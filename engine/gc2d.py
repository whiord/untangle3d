__author__ = 'whiord'

from gc import BaseController
import geometry.d2 as gd2

import pygame
import pygame.display as pdis
import pygame.draw as pd
import pygame.locals as pl
import pygame.font as pf


class GameController2D(BaseController):
    TYPE_SIGNATURE = "2D"

    def __init__(self):
        BaseController.__init__(self)

    def _find_point(self, pos):
        for id, point in self.objects.items():
            if point.dist_to(*pos) < self.config.circle.radius * self.config.circle.grub_coef:
                return id
        return None

    def _adjust(self):
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

        maxx = int(round(maxx))
        maxy = int(round(maxy))
        self.display = pdis.set_mode((maxx + self.config.borders, maxy + self.config.borders), pygame.RESIZABLE)

    def _resize(self, size):
        old_size = self.display.get_size()
        scale_x = float(size[0])/float(old_size[0])
        scale_y = float(size[1])/float(old_size[1])
        for point in self.objects.values():
            point.x *= scale_x
            point.y *= scale_y
        self.display = pdis.set_mode(size, pygame.RESIZABLE)

    def open(self, map_config):
        BaseController.open(self, map_config)
        self.objects = {}

        for point in map_config.objects:
            self.objects[point.id] = gd2.Circle(point.x, point.y, self.config.circle.radius)

        self.edges = map_config.edges
        self._adjust()
        print("GC:", "objects created: ", len(self.objects))

    def dispatch(self, event):
        if event.type == pl.MOUSEBUTTONDOWN:
            if event.button == 1:
                id = self._find_point(event.pos)
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
            self._resize(event.size)

    def _draw(self):
        intersected = set()
        objs = self.objects
        for e1 in self.edges:
            for e2 in self.edges:
                if e1 != e2 and e1 not in intersected:
                    s1 = gd2.Segment(objs[e1[0]], objs[e1[1]])
                    s2 = gd2.Segment(objs[e2[0]], objs[e2[1]])
                    if gd2.intersect_seg(s1, s2, self.config.accuracy):
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
            #pd.aaline(self.display, color, (p1.x, p1.y), (p2.x, p2.y), True)

        for id, point in self.objects.items():
            color = self.config.circle.color
            if id == self.grub_id:
                color = self.config.circle.active_color
            pd.circle(self.display, color, (int(round(point.x)), int(round(point.y))), int(round(point.radius)))
            #pgfx.aacircle(self.display, int(round(point.x)), int(round(point.y)), int(round(point.radius)), color)

        self._render_info("tangled: {}/{}".format(len(intersected), len(self.edges)))

    def update(self, fps, time):
        #print("GC:", "update called")
        self.display.fill(self.config.background.color)
        self.info_y = 10

        self._draw()

        self._render_info("fps: {}".format(fps))
        pdis.update()

    def _render_info(self, text):
        font = pf.Font(None, 20)
        info = font.render(text, True, self.config.line.color)
        self.display.blit(info, (10, self.info_y))
        self.info_y += info.get_size()[1] + 5