import pygame as py
from dataclasses import dataclass, field, KW_ONLY

# from Car import Car
from math import pi, sin, cos
from utils import *


# @dataclass
# class Point:
#     x: int | float
#     y: int | float

# mytype = type('Car', Car)


# @dataclass
# class Sensor:
#     car:
#     ray_count: int = 4
#     ray_length: int = 150
#     rey_spread: float = pi / 2
#     rays: list[tuple[tuple, tuple]] = field(default_factory=list)
#     readings: list = field(default_factory=list)
#     # road_boundaries: list[tuple] = field(default_factory=list)

from collections.abc import Sequence


class NamedMutableSequence(Sequence):
    __slots__ = ()

    def __init__(self, *a, **kw):
        slots = self.__slots__
        for k in slots:
            setattr(self, k, kw.get(k))

        if a:
            for k, v in zip(slots, a):
                setattr(self, k, v)

    def __str__(self):
        clsname = self.__class__.__name__
        values = ", ".join("%s=%r" % (k, getattr(self, k)) for k in self.__slots__)
        return "%s(%s)" % (clsname, values)

    __repr__ = __str__

    def __getitem__(self, item):
        return getattr(self, self.__slots__[item])

    def __setitem__(self, item, value):
        return setattr(self, self.__slots__[item], value)

    def __len__(self):
        return len(self.__slots__)


class Point(NamedMutableSequence):
    __slots__ = ("x", "y")


endd = Point(1, 1)


class Sensor:
    def __init__(self, car, ray_count=4):
        self.car = car
        self.ray_count = ray_count
        self.ray_length = 250
        self.rey_spread = pi / 2
        self.rays = []
        self.readings = []
        self.road_boundaries = []

    def cast_rays(self):
        self.rays = []

        for i in range(self.ray_count):
            ray_angle = learp(
                -self.rey_spread / 2,
                self.rey_spread / 2,
                0.5 if self.ray_count == 1 else (i / (self.ray_count - 1)),
            ) + to_radians(self.car.angle)

            self.rays.append(
                (
                    (self.car.rect.centerx, self.car.rect.centery),
                    (
                        self.car.rect.centerx - (self.ray_length * sin(ray_angle)),
                        self.car.rect.centery - (self.ray_length * cos(ray_angle)),
                    ),
                )
            )

    def get_readings(self, ray, road_boundaries, traffic):
        touches = []

        for i in range(len(road_boundaries)):
            touch = get_intersaction(
                Point(*ray[0]),
                Point(*ray[1]),
                Point(*road_boundaries[i][0]),
                Point(*road_boundaries[i][1]),
            )

            if touch:
                touches.append(touch)

        for car in traffic:
            poly = car.polygon
            for i in range(len(poly)):
                touch = get_intersaction(
                    Point(*ray[0]),
                    Point(*ray[1]),
                    poly[i],
                    poly[(i + 1) % len(poly)],
                )

                if touch:
                    touches.append(touch)

        if len(touches) == 0:
            return None
        else:
            ofsets = map(lambda r: r.offset, touches)
            min_offset = min(ofsets)
            return list(filter(lambda r: r.offset == min_offset, touches))[0]

    def update(self, boundarys, traffic):
        self.cast_rays()

        self.readings = []
        for ray in self.rays:
            self.readings.append(self.get_readings(ray, boundarys, traffic))

    def draw(self, app):
        for i in range(self.ray_count):
            end = self.rays[i][1]
            if self.readings[i]:
                end = self.readings[i]
                endd = Point(*end)
                py.draw.line(app, "red", self.rays[i][1], endd, 5)
            py.draw.line(app, "yellow", self.rays[i][0], tuple(end), 5)
