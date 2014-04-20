__author__ = 'whiord'

import readconf


class BaseController:
    CONFIG_FILE = "engine/config.json"
    REGISTERED_CONTROLLERS = {}

    @staticmethod
    def register_controller(type_signature, class_name):
        BaseController.REGISTERED_CONTROLLERS[type_signature] = class_name

    @staticmethod
    def choose_controller(type):
        if BaseController.REGISTERED_CONTROLLERS.has_key(type):
            return BaseController.REGISTERED_CONTROLLERS[type]()
        else:
            return None

    def __init__(self):
        self.config = readconf.open_json(BaseController.CONFIG_FILE)
        self.display = None
        self.map_config = None
        self.scene = None
        self.grub_id = None
        self.info_y = None

    def open(self, map_config):
        self.map_config = map_config

    def dispatch(self, event):
        raise NotImplementedError()

    def update(self, fps, time):
        raise NotImplementedError()



