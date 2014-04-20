__author__ = 'whiord'

import utils


class BaseRotator:
    def __init__(self):
        pass

    def rotate(self, scene, projection_vector, dx, dy):
        """ rotate(scene, projection_vector, dx, dy) -> Point3D
            Rotates scene anywise, dx and dy - are relative offset in plane orthogonal to projection vector.
            Returns new projection vector.
        """
        pass


class MeridianRotator(BaseRotator):
    def __init__(self):
        BaseRotator.__init__(self)

    def rotate(self, scene, projection_vector, dx, dy):
        for id, object in scene.objects.items():
            buf = object.to_spherical()
            buf.beta += utils.deg_to_rad(dy)
            scene.objects[id] = buf
        return projection_vector


class AxisRotator(BaseRotator):
    def __init__(self):
        BaseRotator.__init__(self)

    def rotate(self, scene, projection_vector, dx, dy):
        buf = projection_vector.to_spherical()
        buf.alpha += utils.deg_to_rad(dx)
        buf.beta += utils.deg_to_rad(dy)
        print "@@@ Screen vector:", buf
        return buf
