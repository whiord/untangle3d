__author__ = 'whiord'

import gc
import gc2d
import gc3d

gc.BaseController.register_controller(gc2d.GameController2D.TYPE_SIGNATURE, gc2d.GameController2D)
gc.BaseController.register_controller(gc3d.GameController3D.TYPE_SIGNATURE, gc3d.GameController3D)
