__author__ = "whiord"

import pygame
import pygame.locals as pl
import pygame.time as pt
import Tkinter, tkFileDialog

import engine.gc
import engine.readconf as readconf


class AppController:
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.config = readconf.open_json(AppController.CONFIG_FILE)

        self.ended = False
        self.gc = None
        self.clock = None

        pygame.init()

    def __open_map(self):
        Tkinter.Tk().withdraw()
        file_name = tkFileDialog.askopenfilename()
        map_config = readconf.open_json(file_name)

        self.gc = engine.gc.BaseController.choose_controller(map_config.type)
        self.gc.open(map_config)

    def run(self):

        pygame.display.set_caption(self.config.caption)

        self.__open_map()
        self.clock = pt.Clock()

        while not self.ended:
            for event in pygame.event.get():
                if event.type == pl.QUIT or (event.type == pl.KEYDOWN and event.key == pl.K_q):
                    self.ended = True
                    break
                elif event.type == pl.KEYDOWN:
                    if event.key == pl.K_o:
                        self.__open_map()
                else:
                    self.gc.dispatch(event)

            self.gc.update(self.clock.get_fps(), self.clock.get_time())
            self.clock.tick(self.config.fps)

        pygame.quit()

app = AppController()
app.run()