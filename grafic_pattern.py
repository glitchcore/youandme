from time import sleep, time
import random
from math import *

from grafic_emulate import draw_scene

# API

def set_ab(a, b, track_point):
    drawing_led_value = [0] * 6
    drawing_led_value[a.color] = a.value
    drawing_led_value[b.color] = b.value
    draw_scene(drawing_led_value, [(v/255 - 0.5) * 0.4 for v in track_point])

def _delay_ms(a):
    sleep(a / 1000)

PHASE_DECIMATOR = 8

TIME_BASE = 0.1
time_for_seance = 10 * 60 * TIME_BASE
time_befor_next_lighting = 5 * 60 *TIME_BASE

SEED = 0xDEADBEEF # seed is here
def lfsr_random(prev):
    # 13 ^ 7 ^ 3
    increment = ((prev >> 3) & 1) ^ ((prev >> 7) & 1) ^ ((prev >> 13) & 1)
    prev = ((prev << 1) + increment) & 0xFFFFFFFF
    return prev

SIN_TABLE = [ 127, 130, 133, 136, 139, 142, 145, 148, 151, 154, 157, 160, 163,
166, 169, 172, 175, 178, 181, 184, 186, 189, 192, 194, 197, 200, 202, 205, 207,
209, 212, 214, 216, 218, 221, 223, 225, 227, 229, 230, 232, 234, 235, 237, 239,
240, 241, 243, 244, 245, 246, 247, 248, 249, 250, 250, 251, 252, 252, 253, 253,
253, 253, 253, 254, 253, 253, 253, 253, 253, 252, 252, 251, 250, 250, 249, 248,
247, 246, 245, 244, 243, 241, 240, 239, 237, 235, 234, 232, 230, 229, 227, 225,
223, 221, 218, 216, 214, 212, 209, 207, 205, 202, 200, 197, 194, 192, 189, 186,
184, 181, 178, 175, 172, 169, 166, 163, 160, 157, 154, 151, 148, 145, 142, 139,
136, 133, 130, 127, 123, 120, 117, 114, 111, 108, 105, 102, 99, 96, 93, 90, 87,
84, 81, 78, 75, 72, 69, 67, 64, 61, 59, 56, 53, 51, 48, 46, 44, 41, 39, 37, 35,
32, 30, 28, 26, 24, 23, 21, 19, 18, 16, 14, 13, 12, 10, 9, 8, 7, 6, 5, 4, 3, 3,
2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 3, 4, 5, 6, 7, 8, 9, 10,
12, 13, 14, 16, 18, 19, 21, 23, 24, 26, 28, 30, 32, 35, 37, 39, 41, 44, 46, 48,
51, 53, 56, 59, 61, 64, 67, 69, 72, 75, 78, 81, 84, 87, 90, 93, 96, 99, 102,
105, 108, 111, 114, 117, 120, 123,] 

def fastest_sin(x):
    return SIN_TABLE[int(x) % 256] - 127

def fastest_cos(x):
    return fastest_sin(x + 64)

class TrackParam:
    def __init__(self):
        self.angle = 50
        self.a_x = 0
        self.a_y = 0
        self.x = 127
        self.y = 127
        self.phase = 60


def update_param(param):
    param.rot = [
        fastest_cos(param.angle), -fastest_sin(param.angle),
        fastest_sin(param.angle), fastest_cos(param.angle)
    ]
        
        
def get_track_point(p, param):
    x = fastest_sin(p + param.phase / PHASE_DECIMATOR)
    y = fastest_sin(p)

    res = (
        int(param.rot[0] * x / 127 + param.rot[1] * y / 127 + param.x),
        int(param.rot[2] * x / 127 + param.rot[3] * y / 127 + param.y)
    )

    # print(p, x, y, res)

    return res

def euclid(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    res = dx * dx + dy * dy
    # print(dx, dy, res)
    return res

LED_POSITIONS = [[255, 128], [191, 237], [64, 237], [1, 128], [64, 18], [191, 18]]

class Led:
    def __init__(self, color, value):
        self.color = color
        self.value = value

def find_led_pair(led_value):
    pair = [Led(0, 0), Led(0, 0)]

    for i in range(6):
        if led_value[i] > pair[0].value:
            pair[1].value = pair[0].value
            pair[1].color = pair[0].color

            pair[0].value = led_value[i]
            pair[0].color = i
        elif led_value[i] > pair[1].value:
            pair[1].value = led_value[i]
            pair[1].color = i

    return pair

INTERPOLATION_SIZE = 16

time_start = time()
def get_time():
    return int(time() - time_start)
def get_time_f():
    return time() - time_start

def blink(led_pair, timestep, track_point):
    blink_max = max(led_pair[0].value, led_pair[1].value)

    for i in range(blink_max):
        x = i
        set_ab(
            Led(led_pair[0].color, min(x, led_pair[0].value)),
            Led(led_pair[1].color, min(x, led_pair[1].value)),
            track_point
        )
        _delay_ms(timestep)
    for i in range(blink_max):
        x = blink_max - i
        set_ab(
            Led(led_pair[0].color, min(x, led_pair[0].value)),
            Led(led_pair[1].color, min(x, led_pair[1].value)),
            track_point
        )
        _delay_ms(timestep)

if __name__ == "__main__":
    global_random = SEED
    param = TrackParam()

    # print(param.rot)

    '''
    global_random = lfsr_random(global_random)
    delay_seed = global_random
    global_random = lfsr_random(global_random)
    next_delay = global_random
    '''

    

    # print([[f"{led.color} = {led.value}" for led in ancor] for ancor in ancors])

    while True:
        global_random = lfsr_random(global_random)
        param.angle = global_random & 0xFF
        global_random = lfsr_random(global_random)
        param.phase = global_random & 0xFF
        global_random = lfsr_random(global_random)
        param.x = global_random & 0xFF
        global_random = lfsr_random(global_random)
        param.y = global_random & 0xFF
        update_param(param)

        ancors = [0] * INTERPOLATION_SIZE
        for t in range(INTERPOLATION_SIZE):
            track_point = get_track_point(int(t * 255 / INTERPOLATION_SIZE), param)

            led_value = [0] * 6
            for i in range(6):
                led_value[i] = int(max(0, min(120, (10000 - euclid(track_point, LED_POSITIONS[i]))/64)))

            # print(led_value)
            ancors[t] = find_led_pair(led_value)
        

        for t in range(INTERPOLATION_SIZE):
            track_point = get_track_point(t, param)
            interpolation_step = int(t % INTERPOLATION_SIZE)
            led_pair = ancors[interpolation_step]
            blink(led_pair, 0, track_point)
        
        # print(f"{led_pair[0].color}={led_pair[0].value}, {led_pair[1].color}={led_pair[1].value}")

        # set_a, set_b
        blink(led_pair, 0, track_point)

        _delay_ms(100)

'''
if __name__ == "__main__":
    # ???? 0 ???? 120
    led_value = [120, 40, 20, 30, 70, 65]
    KEY = random.randint(0, 65536)
    time_start = time()
    delay = 0

    while time() - time_start < time_for_seance:
        led_value = get_leds(KEY, led_value)
        real_led_value = [make_format(led, 0, 127) for led in led_value]
        print(real_led_value)
        delay = get_delay(KEY, delay)
        draw_scene(real_led_value)
        real_delay = make_format(delay, min_val=1, max_val=31)
        sleep(TIME_BASE * real_delay)

    next_seance_init(KEY)
'''

'''
LED_RADIUS = 127

LED_POSITIONS = [
    [LED_RADIUS, 0],
    [cos(radians(60)) * LED_RADIUS, sin(radians(60)) * LED_RADIUS],
    [- cos(radians(60)) * LED_RADIUS, sin(radians(60)) * LED_RADIUS],
    [- LED_RADIUS, 0],
    [- cos(radians(60)) * LED_RADIUS, - sin(radians(60)) * LED_RADIUS],
    [cos(radians(60)) * LED_RADIUS, - sin(radians(60)) * LED_RADIUS],
]

LED_POSITIONS = [[int(x[0] + 128), int(x[1] + 128)] for x in LED_POSITIONS]
print(LED_POSITIONS)
'''