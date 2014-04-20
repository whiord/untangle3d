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
        self.scene_rect = pygame.Rect(0, 0, 0, 0)

    def _find_point(self, pos):
        for id, point in self.scene.objects.items():
            if point.dist_to(*pos) < self.config.circle.radius * self.config.circle.grub_coef:
                return id
        return None

    def _move_system(self):
        minx = maxx = self.scene.objects.values()[0].x
        miny = maxy = self.scene.objects.values()[0].y

        for point in self.scene.objects.values():
            minx = min(minx, point.x)
            miny = min(miny, point.y)
            maxx = max(maxx, point.x)
            maxy = max(maxy, point.y)

        nx, ny = minx - self.config.borders, miny - self.config.borders
        self.scene.move_center(gd2.Point2D(nx, ny))

        width = maxx-minx+2*self.config.borders
        height = maxy-miny+2*self.config.borders

        self.scene_rect = pygame.Rect((0, 0), (width, height))

    def _adjust(self):
        self.display = pdis.set_mode(self.scene_rect.size, pygame.RESIZABLE)
        print("Scene rect:", self.scene_rect, self.scene_rect.center)

    def _resize(self, size):
        old_size = self.display.get_size()
        scale_x = float(size[0])/float(old_size[0])
        scale_y = float(size[1])/float(old_size[1])
        for point in self.scene.objects.values():
            point.x *= scale_x
            point.y *= scale_y
        self.display = pdis.set_mode(size, pygame.RESIZABLE)

    def open(self, map_config):
        BaseController.open(self, map_config)
        self.scene = gd2.Scene2D()

        for point in map_config.objects:
            self.scene.add_object(point.id, gd2.Circle(point.x, point.y, self.config.circle.radius))

        for i, j in map_config.edges:
            self.scene.add_link(i, j)

        self._move_system()
        self._adjust()
        print("GC:", "objects created: ", len(map_config.objects))

    def dispatch(self, event):
        if event.type == pl.MOUSEBUTTONDOWN:
            if event.button == 1:
                id = self._find_point(event.pos)
                if id is not None:
                    self.grub_id = id
        elif event.type == pl.MOUSEMOTION:
            if self.grub_id is not None:
                self.scene.objects[self.grub_id].x = event.pos[0]
                self.scene.objects[self.grub_id].y = event.pos[1]
        elif event.type == pl.MOUSEBUTTONUP:
            if event.button == 1:
                self.grub_id = None
        elif event.type == pl.VIDEORESIZE:
            self._resize(event.size)

    def _draw(self):
        intersected = set()
        cent_x, cent_y = 0, 0
        objs = self.scene.objects
        for e1 in self.scene.links:
            for e2 in self.scene.links:
                if e1 != e2 and e1 not in intersected:
                    s1 = gd2.Segment(objs[e1[0]], objs[e1[1]])
                    s2 = gd2.Segment(objs[e2[0]], objs[e2[1]])
                    if s1.intersect_seg(s2, self.config.accuracy):
                        intersected.add(e1)
                        intersected.add(e2)

        for edge in self.scene.links:
            p1 = objs[edge[0]]
            p2 = objs[edge[1]]

            color = self.config.line.color
            if edge in intersected:
                color = self.config.line.bad_color
            if self.grub_id is not None:
                if edge[0] == self.grub_id or edge[1] == self.grub_id:
                    color = self.config.line.active_color

            pd.line(self.display, color, (p1.x + cent_x, p1.y + cent_y),
                    (p2.x + cent_x, p2.y + cent_y), self.config.line.width)

        for id, point in objs.items():
            color = self.config.circle.color
            if id == self.grub_id:
                color = self.config.circle.active_color
            pd.circle(self.display, color, (int(round(point.x + cent_x)),
                                            int(round(point.y + cent_y))), int(round(point.radius)))

        self._render_info("tangled: {}/{}".format(len(intersected), len(self.scene.links)))

    def update(self, fps, time):
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