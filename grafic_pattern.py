from time import sleep, time
import random
from math import *
import turtle

TIME_BASE = 0.1
DOT_SIZE = 50
RADIUS = DOT_SIZE*2
POSITIONS = [
    (RADIUS, 0),
    (cos(radians(60)) * RADIUS, sin(radians(60)) * RADIUS),
    (- cos(radians(60)) * RADIUS, sin(radians(60)) * RADIUS),
    (- RADIUS, 0),
    (- cos(radians(60)) * RADIUS, - sin(radians(60)) * RADIUS),
    (cos(radians(60)) * RADIUS, - sin(radians(60)) * RADIUS),
]
LEDS = [
    (1, 0, 0), # R
    (0, 1, 0), # G
    (0, 0, 1), # B
    (1, 1, 0), # Y
    (0, 1, 0), # G
    (0, 0, 1), # B
]
TIME_FOR_SEANS = 10 * 60 * TIME_BASE

GLOBAL_DELAY = 0
GLOBAL_COLORS = [0, 0, 0, 0, 0, 0]


def print_colored_circle(color, position):
    t.pencolor(color)
    t.setx(position[0])
    t.sety(position[1])
    t.dot(500)


def get_colors_list(key):
    result_list = []
    for i in range(6):
        random.seed((key + GLOBAL_COLORS[i])/(10 + i))
        result_list.append(random.randint(10, 250))
    return result_list


def get_delays_list(key):
    previous_delay = GLOBAL_DELAY
    result = (key + previous_delay) % 20
    return result


def make_current_color_type():
    color_list = []

    for i in range(6):
        color_list.append(( (r * GLOBAL_COLORS[i]) / 255 for r in LEDS[i] ))

    return color_list


if __name__ == "__main__":
    s = turtle.getscreen()
    t = turtle.Turtle()
    t.speed(0)
    t.ht()
    key_generate = random.randint(0, 65536)
    time_start = time()

    while time() - time_start < TIME_FOR_SEANS:
        GLOBAL_COLORS = get_colors_list(key_generate)
        colors = make_current_color_type()
        GLOBAL_DELAY = get_delays_list(key_generate)
        print_colored_circle(colors[0], POSITIONS[0]) # R
        print_colored_circle(colors[1], POSITIONS[1]) # G
        print_colored_circle(colors[2], POSITIONS[2]) # B
        print_colored_circle(colors[3], POSITIONS[3]) # Y
        print_colored_circle(colors[4], POSITIONS[4]) # G
        print_colored_circle(colors[5], POSITIONS[5]) # B
        sleep(TIME_BASE * GLOBAL_DELAY)

