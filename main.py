import pygame as py
from Car import Car
from Road import Road
from Sensor import Sensor
import pickle
from Network import NeuralNetwork


py.display.init()

clock = py.time.Clock()


SCREEN_WIDTH = 800

SCREEN_HEIGHT = 800

app = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def generate_cars(n):
    cars = []
    for i in range(n):
        cars.append(
            Car(road.get_let_pos(2, car_width=60), SCREEN_HEIGHT - 250, 60, 80, "AI")
        )
    return cars


offset = SCREEN_WIDTH / 3.5
road = Road(offset, 0, SCREEN_WIDTH - ((offset) * 2), SCREEN_HEIGHT)  # type: ignore
# car = Car(road.get_let_pos(2, car_width=60), SCREEN_HEIGHT - 250, 60, 80, "AI")

n = 100
cars = generate_cars(n)


traffic = [
    Car(road.get_let_pos(2, car_width=60), SCREEN_HEIGHT - 450, 60, 80, "DUMMY"),
    Car(road.get_let_pos(1, car_width=60), SCREEN_HEIGHT - 450, 60, 80, "DUMMY"),
    Car(road.get_let_pos(2, car_width=60), SCREEN_HEIGHT - 850, 60, 80, "DUMMY"),
    Car(road.get_let_pos(3, car_width=60), SCREEN_HEIGHT - 850, 60, 80, "DUMMY"),
]

best_car = cars[0]
try:
    local_best_car = pickle.load(open("data", "rb"))
    if local_best_car:
        for ind, car in enumerate(cars):
            car.brain = pickle.load(open("data", "rb"))
            if ind != 0:
                NeuralNetwork.mutate(car.brain, 0.2)

except FileNotFoundError:
    pass

frame_count = 1
while True:
    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            quit()
        if event.type == py.KEYDOWN:
            if event.key == py.K_ESCAPE:
                # pickle.dump(best_car.brain, open("data", "wb"))
                py.quit()
                quit()
            if event.key == py.K_s:
                pickle.dump(best_car.brain, open("data", "wb"))

        # car.manage_control(event)

    app.fill(120)
    clock.tick(60)

    frame_count += 1
    frame_count = frame_count % 500

    if frame_count == 0:
        for ind, tra in enumerate(traffic):
            tra.rect.y = best_car.rect.y - (300 * (ind + 1))
            tra.rect.x = road.get_let_pos(ind) - 50

    best_car.best = False
    mins = list(map(lambda car: car.ty, cars))
    best_car = cars[mins.index(min(mins))]
    # print(best_car.ty)
    best_car.best = True

    state = len(
        list(filter(lambda state: state, map(lambda car: car.damaged == False, cars)))
    )

    road.update(best_car.speed > 0 and best_car.damaged == False)
    road.draw(app)

    for c in traffic:
        c.update(road.boundarys, [])
        c.check_state(best_car.speed > 0 and best_car.damaged == False)
        c.draw(app)

    for car in cars:
        if state:
            car.update(road.boundarys, traffic)
        car.draw(app)

        if car.damaged:
            cars.pop(cars.index(car))

    py.display.flip()
