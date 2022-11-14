from time import sleep, time
import random
from math import *
import turtle

TIME_BASE = 0.1
TIME_FOR_SEANS = 10 * 60 * TIME_BASE

GLOBAL_DELAY = 0
GLOBAL_COLORS = [0, 0, 0, 0, 0, 0]

'''
def print_colored_circle(color, position):
    t.pencolor(color)
    t.setx(position[0])
    t.sety(position[1])
    t.dot(500)


def get_colors_list(key):
    result_list = []
    for i in range(6):
        # need own implementation of random (LFSR, for example)
        random.seed((key + GLOBAL_COLORS[i])/(10 + i))
        result_list.append(random.randint(10, 250))
    return result_list


previous_delay = 0
def get_delays_list(key):
    global previous_delay
    # mod looks very predictable
    result = (key + previous_delay) % 20
    previous_delay = result
    return result


def make_current_color_type(colors):
    color_list = []

    for i in range(6):
        color_list.append(( (r * colors[i]) / 255 for r in LEDS[i] ))

    return color_list
'''

'''
if __name__ == "__main__":
    s = turtle.getscreen()
    t = turtle.Turtle()
    t.speed(0)
    t.ht()
    key_generate = random.randint(0, 65536)
    time_start = time()

    while time() - time_start < TIME_FOR_SEANS:
        GLOBAL_COLORS = get_colors_list(key_generate)
        colors = make_current_color_type(GLOBAL_COLORS)
        delay = get_delays_list(key_generate)
        print_colored_circle(colors[0], POSITIONS[0]) # R
        print_colored_circle(colors[1], POSITIONS[1]) # G
        print_colored_circle(colors[2], POSITIONS[2]) # B
        print_colored_circle(colors[3], POSITIONS[3]) # Y
        print_colored_circle(colors[4], POSITIONS[4]) # G
        print_colored_circle(colors[5], POSITIONS[5]) # B
        sleep(TIME_BASE * delay)
'''

'''
import matplotlib.pyplot as plt

from math import *

X = np.linspace(-3, 3, 100)
Y = np.linspace(-3, 3, 100)
z = []
for i, x in enumerate(X):
    z.append([])
    for j, y in enumerate(Y):    
        z[i].append(x**2 + y**2)

# generate 2 2d grids for the x & y bounds
# y, x = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))


# x and y are bounds, so z should be the value *inside* those bounds.
# Therefore, remove the last value from the z array.
# z = z[:-1, :-1]
# z_min, z_max = -np.abs(z).max(), np.abs(z).max()

fig, ax = plt.subplots()

c = ax.pcolormesh(z) # , vmin=z_min, vmax=z_max
ax.set_title('pcolormesh')
# set the limits of the plot to the limits of the data
# ax.axis([x.min(), x.max(), y.min(), y.max()])
fig.colorbar(c, ax=ax)

plt.show()
'''

import pygame

pygame.init()
WIDTH = 50
HEIGHT = 50
window = pygame.display.set_mode((500, 500))
window.fill(0)

pic = pygame.surface.Surface((WIDTH, HEIGHT))

def draw_scene(led_value):
    DOT_SIZE = 0.3
    RADIUS = 0.2

    POSITIONS = [
        [RADIUS, 0],
        [cos(radians(60)) * RADIUS, sin(radians(60)) * RADIUS],
        [- cos(radians(60)) * RADIUS, sin(radians(60)) * RADIUS],
        [- RADIUS, 0],
        [- cos(radians(60)) * RADIUS, - sin(radians(60)) * RADIUS],
        [cos(radians(60)) * RADIUS, - sin(radians(60)) * RADIUS],
    ]
    LEDS = [
        [1,0,0], # R
        [0,1,0], # G
        [0,0,1], # B
        [1,1,0], # Y
        [0,1,0], # G
        [0,0,1], # B
    ]


    def smoothstep(edge0, edge1, x):
       if x < edge0:
          return 0

       if x >= edge1:
          return 1

       # Scale/bias into [0..1] range
       x = (x - edge0) / (edge1 - edge0);

       return x * x * (3 - 2 * x)

    def circle(center, xy, r):
        x = xy[0] - center[0]
        y = xy[1] - center[1]

        out = r**2 - (x**2 + y**2)
        out *= 30
        out = smoothstep(0, 1, out)

        return out

    def normalize_out(v):
        return [min(255,max(0, i * 255)) for i in v]

    def add(a,b):
        return [x[0] + x[1] for x in zip(a,b)]
    def mult(a,b):
        return [x * b for x in a]

    # pixel_array = pic.PixelArray(window)
    pic.fill(0)

    for i in range(WIDTH):
        for j in range(HEIGHT):
            out = [0,0,0]
            RED = [1,0,0]
            GREEN = [0,1,0]

            x = i/WIDTH - 0.5
            y = j/HEIGHT - 0.5

            PLACE_R = 0.2
            R = 0.1

            for pos, color, value in zip(POSITIONS, LEDS, led_value):
                a = circle(pos, [x, y], DOT_SIZE) * min(1, max(value / 120, 0))
                out = add(out, mult(color, a))

            out = normalize_out(out)
            pic.set_at((i, j), tuple(out))
            # pixel_array[i, j] = tuple(out)
    window.blit(pygame.transform.scale(pic, window.get_rect().size), (0, 0))
    # pixel_array.close()
    pygame.display.flip()

led_value = [120, 40, 40, 40, 40, 40]

while True:
    led_value[0] = 120 * (0.5 + sin(time()) * 0.5)
    draw_scene(led_value)