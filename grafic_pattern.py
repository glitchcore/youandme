from time import sleep, time
import random
from math import *

from grafic_emulate import draw_scene

TIME_BASE = 0.1
time_for_seance = 10 * 60 * TIME_BASE
time_befor_next_lighting = 5 * 60 *TIME_BASE


def make_format(value, min_val=1, max_val=31):
    """
    типа договорились, что макс и мин - на 1 меньше степени двойки
    ! нужно будет переделать нормально
    """
    return (value & max_val) + min_val


def me_random(number):
    # 13 ^ 7 ^ 3
    result = number
    for _ in range(4):
        increment = ((result >> 3) & 1) ^ ((result >> 7) & 1) ^ ((result >> 13) & 1)
        result = (result << 1) + increment
    return result & 32767


def get_delay(key, prev_delay):
    new_delay = me_random(key + prev_delay)
    return new_delay


def get_leds(key, prev_led_value):
    new_leds = [
        me_random(led + key) for led in prev_led_value
    ]
    return new_leds


def next_seance_init():
    """
    планирую тут написать мега-логику по рассчёту параметров следующего сеанса

    1 - номара диодов, которые будут задействованы
    2 - время до следующего мигания (time_befor_next_lighting)
    3 - ...


    возможно, нужно будет что-то вынести в глобальные переменные (delsy, e.t.c)
    """
    pass

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
    return SIN_TABLE[int(x) % 256]

MAX_DETUNE = 255

class TrackParam:
    def __init__(self):
        self.a_x = 255
        self.a_y = 255
        self.detune = MAX_DETUNE/2
        self.x = 127
        self.y = 0
        self.phase_x = 0
        self.phase_y = 64
        
def get_track_point(p, param):
    return (
        param.a_x * (fastest_sin(p * param.detune / 64 + param.phase_x)) / 255 + param.x,
        param.a_y * (fastest_sin(p * (MAX_DETUNE - param.detune) / 64 + param.phase_y)) / 255 + param.y
    )

def euclid(a, b):
    res = (a[0] - b[0])**2 + (a[1] - b[1])**2
    # print(res)
    return res

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

LED_POSITIONS = [[255, 128], [191, 237], [64, 237], [1, 128], [64, 18], [191, 18]]

'''
if __name__ == "__main__":
    # от 0 до 120
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

if __name__ == "__main__":
    while True:
        for t in range(255):
            param = TrackParam()
            param.detune = 127
            track_point = get_track_point(t, param)
            led_value = [
                max(0, min(120, (10000 - euclid(track_point, led_point))/100)) for led_point in LED_POSITIONS]
            draw_scene(led_value)
            sleep(0.05)
