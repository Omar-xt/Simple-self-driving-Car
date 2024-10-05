import pygame as py
from dataclasses import dataclass, field


@dataclass
class Road:
    x: int
    y: int
    w: int
    h: int
    speed: int = 5
    len_count: int = 3
    moving: bool = False
    frame_count: int = 0
    boundarys: list = field(default_factory=list)

    def __post_init__(self):
        self.boundarys = [
            ((self.x + 10, self.y), (self.x, self.y + self.h)),
            ((self.x + self.w - 5, self.y), (self.x + self.w - 5, self.y + self.h)),
        ]

    def learp(self, a, b, t):
        return a + (b - a) * t

    def get_let_pos(self, index, car_width=60):
        len_width = self.w / self.len_count
        return (
            self.x
            + (len_width * max(0, min(self.len_count - 1, index - 1)))
            + len_width / 2
            - car_width / 2
        )

    def update(self, is_moving):
        self.moving = is_moving

        if self.moving:
            self.speed += 5

        if self.speed == self.h:
            self.speed = 0

    def draw(self, app):
        py.draw.rect(app, "gray", (self.x, self.y, self.w, self.h))
        py.draw.rect(app, "white", (self.x + self.w - 5, self.y, 5, self.h))
        for i in range(self.len_count):
            x = self.learp(self.x, self.x + self.w, i / self.len_count)
            if i == 0:
                py.draw.rect(app, "white", (x, self.y, 5, self.h))
            for j in range(-self.h, self.h, 40):
                py.draw.rect(app, "white", (x, j + self.speed, 5, 20))

            # py.draw.line(
            #     app,
            #     "black",
            #     (self.x + i * self.w / self.len_count, self.y),
            #     (self.x + (i + 1) * self.w / self.len_count, self.y + self.h),
            # )
