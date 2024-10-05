from dataclasses import dataclass
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])


def learp(a, b, t):
    return a + (b - a) * t


def to_radians(angle):
    return angle * (3.1416 / 180)


def to_degrees(angle):
    return angle * (180 / 3.1416)


@dataclass
class Interrsation:
    x: float
    y: float
    offset: float

    def __iter__(self):
        yield self.x
        yield self.y

    def __next__(self):
        return next(self.__iter__())


def get_intersaction(a, b, c, d):
    t_top = (d.x - c.x) * (a.y - c.y) - (d.y - c.y) * (a.x - c.x)
    u_top = (c.y - a.y) * (a.x - b.x) - (c.x - a.x) * (a.y - b.y)
    bottom = (d.y - c.y) * (b.x - a.x) - (d.x - c.x) * (b.y - a.y)

    if bottom != 0:
        t = t_top / bottom
        u = u_top / bottom

        if 0 <= t <= 1 and 0 <= u <= 1:
            return Interrsation(learp(a.x, b.x, t), learp(a.y, b.y, t), t)
            # return learp(a.x, b.x, t), learp(a.y, b.y, t), t


def polyIntersects(poly1, poly2):
    for p1 in range(len(poly1)):
        for p2 in range(len(poly2)):
            touch = get_intersaction(
                poly1[p1],
                poly1[(p1 + 1) % len(poly1)],
                Point(*poly2[p2]),
                Point(*poly2[(p2 + 1) % len(poly2)]),
            )
            if touch:
                return True
    return False
