import pygame as py
from math import sin, cos, hypot, atan2, pi
from dataclasses import dataclass
from Network import NeuralNetwork
from Sensor import Sensor
from utils import to_radians, polyIntersects, Point


class Car:
    def __init__(self, p_x, p_y, W, H, car_type):
        self.x = p_x
        self.y = p_y
        self.ty = p_y
        self.w = W
        self.h = H

        self.left = False
        self.right = False
        self.forward = False
        self.reverse = False

        self.angle = 0
        self.speed = 0
        self.turn_speed = 2
        self.accleration = 0.5
        self.max_speed = 7
        self.max_speed_dummy = 3
        self.friction = 0.2

        self.type = car_type
        self.use_brain = car_type == "AI"

        self.body = py.Surface((self.w, self.h))
        self.body.fill("cyan")
        self.body.set_colorkey(0)
        self.img = self.body.copy()
        self.rect = py.Rect(self.x, self.y, self.w, self.h)

        self.damaged = False
        self.best = False

        self.polygon: list = []
        self.sensor = None

        self.setup()

    def setup(self):
        if self.type != "DUMMY":
            self.body.fill("green")
            self.sensor = Sensor(self)
            self.brain = NeuralNetwork([self.sensor.ray_count, 6, 4])
            # print(self.brain.levels[0].inputs)

    def check_state(self, running):
        if running:
            self.forward = False
            self.reverse = running
            self.max_speed = self.max_speed_dummy * 1.5
        else:
            self.max_speed = self.max_speed_dummy
            self.forward = True
            self.reverse = running

    def manage_control(self, event):
        if event.type == py.KEYDOWN:
            if event.key == py.K_LEFT:
                self.left = True
            elif event.key == py.K_RIGHT:
                self.right = True
            elif event.key == py.K_UP:
                self.forward = True
            elif event.key == py.K_DOWN:
                self.reverse = True
        if event.type == py.KEYUP:
            if event.key == py.K_LEFT:
                self.left = False
            elif event.key == py.K_RIGHT:
                self.right = False
            elif event.key == py.K_UP:
                self.forward = False
            elif event.key == py.K_DOWN:
                self.reverse = False

    def rotate(self):
        old_center = self.rect.center
        self.img = py.transform.rotate(self.body, self.angle)
        self.rect = self.img.get_rect()
        self.rect.center = old_center

    def to_radians(self, angle):
        return angle * (3.1416 / 180)

    def move(self):
        if self.speed != 0:
            flip = 1 if self.speed > 0 else -1
            if self.left:
                self.angle += self.turn_speed * flip
                self.rotate()
            if self.right:
                self.angle -= self.turn_speed * flip
                self.rotate()
        if self.forward:
            self.speed += self.accleration
        if self.reverse:
            self.speed -= self.accleration

        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed / 2:
            self.speed = -self.max_speed / 2

        if self.speed > 0:
            self.speed -= self.friction
        if self.speed < 0:
            self.speed += self.friction

        if abs(self.speed) < self.friction:
            self.speed = 0

        # self.x -= sin(self.to_radians(self.angle)) * self.speed
        # self.y -= cos(self.to_radians(self.angle)) * self.speed

        dx = sin(self.to_radians(self.angle)) * self.speed
        dy = cos(self.to_radians(-self.angle)) * self.speed

        self.rect.x -= dx  # type: ignore
        if self.type == "DUMMY":
            self.rect.y -= dy  # type: ignore

        if self.type == "AI":
            if self.speed < 0 and self.rect.y < 1000:
                self.rect.y -= dy  # type: ignore
            if self.speed == 0 and self.rect.y < 1000:
                self.rect.y += 2
        self.x, self.y = self.rect.center
        self.ty -= dy

    def creare_polygon(self):
        points = []
        rad = hypot(self.w, self.h) / 2
        alpha = atan2(self.w, self.h)
        angle = to_radians(self.angle)
        points.append(
            Point(
                self.x - sin(angle - alpha) * rad,
                self.y - cos(angle - alpha) * rad,
            )
        )
        points.append(
            Point(
                self.x - sin(angle + alpha) * rad,
                self.y - cos(angle + alpha) * rad,
            )
        )
        points.append(
            Point(
                self.x - sin(pi + angle - alpha) * rad,
                self.y - cos(pi + angle - alpha) * rad,
            )
        )
        points.append(
            Point(
                self.x - sin(pi + angle + alpha) * rad,
                self.y - cos(pi + angle + alpha) * rad,
            )
        )

        return points

    def assess_damage(self, road_borders, traffic):
        for border in road_borders:
            if polyIntersects(self.polygon, border):
                return True

        for car in traffic:
            if polyIntersects(self.polygon, car.polygon):
                return True

        return False

    def update(self, road_borders, traffic):
        if self.sensor:
            self.sensor.update(road_borders, traffic)
            offsets = list(
                map(lambda x: (1 - x.offset) if x else 0, self.sensor.readings)
            )

            # print(offsets)

            outputs = NeuralNetwork.feedforward(offsets, self.brain)

            # print(outputs)

            if self.use_brain:
                self.forward = outputs[0]
                self.left = outputs[1]
                self.right = outputs[2]
                self.reverse = outputs[3]

        if self.damaged:
            if self.y < 1000:
                self.y += self.max_speed
                self.rect.y = self.y
            return

        self.move()
        self.polygon = self.creare_polygon()

        self.damaged = self.assess_damage(road_borders, traffic)

    def draw(self, app):
        if self.damaged:
            self.body.fill("red")
            self.rotate()
            # return
        else:
            if self.type != "DUMMY":
                self.body.fill("green")
                self.rotate()

        app.blit(self.img, self.rect)

        if not self.damaged:
            for i in range(len(self.polygon)):
                i = i % len(self.polygon)
                py.draw.line(
                    app,
                    "black",
                    self.polygon[i],
                    self.polygon[(i + 1) % len(self.polygon)],
                    5,
                )

        if self.best and self.sensor:
            self.sensor.draw(app)
