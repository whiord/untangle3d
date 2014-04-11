__author__ = "whiord"

import pygame
import pygame.locals as pl
import pygame.time as pt
import json
import io
import Tkinter, tkFileDialog

import engine.gc
import engine.readconf as readconf


class AppController:
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.config = readconf.open_json(AppController.CONFIG_FILE)

        self.size = (self.config.window.width, self.config.window.height)
        #self.caption = self.config["caption"]
        #self.fps = self.config["fps"]

        self.display = None
        self.ended = False
        self.gc = None
        self.clock = None

        pygame.init()

    def _open_map(self):
        Tkinter.Tk().withdraw()
        filename = tkFileDialog.askopenfilename()
        with io.open(filename) as map_file:
            map_config = json.load(map_file)
            print(map_config)

        cl = engine.gc.BaseController.choose_controller(map_config)
        self.gc = eval("engine.gc." + cl)(self.config.engine, self.display)
        self.gc.open(map_config)

    def run(self):
        self.display = pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.config.caption)

        self._open_map()
        self.clock = pt.Clock()

        while not self.ended:
            for event in pygame.event.get():
                if event.type == pl.QUIT or (event.type == pl.KEYDOWN and event.key == pl.K_q):
                    self.ended = True
                    break
                elif event.type == pl.KEYDOWN:
                    if event.key == pl.K_o:
                        self._open_map()
                else:
                    print(event)
                    self.gc.dispatch(event)

            self.gc.update(self.clock.get_fps(), self.clock.get_time())
            pygame.display.update()
            self.clock.tick(self.config.fps)

        pygame.quit()

app = AppController()
app.run()