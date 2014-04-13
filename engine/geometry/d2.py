__author__ = 'whiord'


class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dist_to(self, x, y):
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5

    def __sub__(self, other):
        return Point2D(self.x-other.x, self.y - other.y)

    def __mul__(self, other):
        return self.x*other.x + self.y*other.y

    def length(self):
        return (self.x**2 + self.y**2) ** 0.5


class Circle(Point2D):
    def __init__(self, x, y, radius):
        Point2D.__init__(self, x, y)
        self.radius = radius


class Line(object):
    def __init__(self, p1, p2):
        self.A = p1.y - p2.y
        self.B = p2.x - p1.x
        self.C = p1.x*p2.y - p2.x*p1.y


class Segment(Line):
    def __init__(self, p1, p2):
        super(Segment, self).__init__(p1, p2)
        self.p1 = p1
        self.p2 = p2


def intersect_line(l1, l2):
    den = l1.A*l2.B - l2.A*l1.B
    if den == 0:
        return None

    x = (l2.C*l1.B - l1.C*l2.B) / den
    y = (l2.A*l1.C - l2.C*l1.A) / den
    return Point2D(x, y)


def intersect_seg(s1, s2, acc):
    p = intersect_line(s1, s2)
    if p is None:
        return False

    t1 = s1.p2 - s1.p1
    t2 = s2.p2 - s2.p1

    u1 = p - s1.p1
    u2 = p - s2.p1

    cos1 = t1*u1
    cos2 = t2*u2

    if cos1 < 0 or cos2 < 0:
        return False

    if acc <= u1.length() <= t1.length()-acc and acc <= u2.length() <= t2.length() - acc:
        return True

    return False