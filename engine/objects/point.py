__author__ = 'whiord'


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dist_to(self, x, y):
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5