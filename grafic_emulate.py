from math import *
import pygame

pygame.init()
WIDTH = 50
HEIGHT = 50
window = pygame.display.set_mode((500, 500))
window.fill(0)

pic = pygame.surface.Surface((WIDTH, HEIGHT))


def draw_scene(led_value, track_point):
    # print(track_point)
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
        [1, 0, 0],  # R
        [0, 1, 0],  # G
        [0, 0, 1],  # B
        [1, 1, 0],  # Y
        [0, 1, 0],  # G
        [0, 0, 1],  # B
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

        out = r ** 2 - (x ** 2 + y ** 2)
        out *= 30
        out = smoothstep(0, 1, out)

        return out

    def normalize_out(v):
        return [min(255, max(0, i * 255)) for i in v]

    def add(a, b):
        return [x[0] + x[1] for x in zip(a, b)]

    def mult(a, b):
        return [x * b for x in a]

    # pixel_array = pic.PixelArray(window)
    pic.fill(0)

    for i in range(WIDTH):
        for j in range(HEIGHT):
            out = [0, 0, 0]
            RED = [1, 0, 0]
            GREEN = [0, 1, 0]

            x = i / WIDTH - 0.5
            y = j / HEIGHT - 0.5

            PLACE_R = 0.2
            R = 0.1

            for pos, color, value in zip(POSITIONS, LEDS, led_value):
                a = circle(pos, [x, y], DOT_SIZE) * min(1, max(value / 120, 0))
                out = add(out, mult(color, a))

            a = circle(track_point, [x, y], 0.1) * 10
            out = add(out, mult([1,1,1], a))

            out = normalize_out(out)
            pic.set_at((i, j), tuple(out))
            # pixel_array[i, j] = tuple(out)
    window.blit(pygame.transform.scale(pic, window.get_rect().size), (0, 0))
    # pixel_array.close()
    pygame.display.flip()
